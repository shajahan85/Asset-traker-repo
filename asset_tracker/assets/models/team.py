"""Team model with hierarchical support."""
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class TeamManager(models.Manager):
    """Custom manager for efficient team hierarchy queries."""
    
    def get_hierarchy(self, branch=None):
        """
        Get all teams with parent relationships prefetched.
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.select_related('parent', 'branch').prefetch_related('sub_teams')
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_parent_teams(self, branch=None):
        """
        Get only parent teams (teams without a parent).
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.filter(parent__isnull=True)
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_sub_teams(self, branch=None):
        """
        Get only sub-teams (teams with a parent).
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.filter(parent__isnull=False)
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_teams_by_branch(self, branch):
        """
        Get all teams for a specific branch.
        
        Args:
            branch: Branch instance
            
        Returns:
            QuerySet of teams for the branch, ordered hierarchically
        """
        return self.filter(branch=branch).select_related('parent', 'branch').order_by('parent__name', 'name')
    
    def get_hierarchical_choices(self, branch=None):
        """
        Get teams formatted for dropdown display with hierarchy.
        
        Args:
            branch: Optional Branch instance to filter by
            
        Returns:
            list of tuples: (id, display_name)
        """
        choices = []
        parent_teams = self.get_parent_teams(branch=branch).order_by('name')
        
        for parent in parent_teams:
            choices.append((parent.id, parent.name))
            sub_teams = parent.sub_teams.filter(branch=parent.branch).order_by('name') if branch else parent.sub_teams.all().order_by('name')
            for sub in sub_teams:
                choices.append((sub.id, f"  └─ {sub.name}"))
        
        return choices


class Team(models.Model):
    """Model for storing organizational teams with hierarchical support."""
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.PROTECT,
        related_name='teams',
        db_index=True,
        help_text="Branch this team belongs to"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_teams',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TeamManager()

    class Meta:
        ordering = ['branch__name', 'name']
        indexes = [
            models.Index(fields=['branch', 'parent', 'name']),
            models.Index(fields=['parent', 'name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'name'],
                name='unique_team_name_per_branch'
            )
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def clean(self):
        """Validate team hierarchy constraints."""
        # Prevent self-reference
        if self.parent == self:
            raise ValidationError("A team cannot be its own parent.")

        # Prevent circular references
        if self.parent and self._creates_circular_reference():
            raise ValidationError("This parent assignment would create a circular reference.")

        # Prevent depth > 2 (only parent and sub-team levels)
        if self.parent and self.parent.parent:
            raise ValidationError("Teams can only be nested 2 levels deep (parent and sub-team).")

        # Prevent converting parent with children to sub-team
        if self.parent and self.sub_teams.exists():
            raise ValidationError("Cannot assign a parent to a team that has sub-teams.")
        
        # Validate branch consistency with parent
        if self.parent and self.branch_id != self.parent.branch_id:
            raise ValidationError(
                "Sub-team must belong to the same branch as its parent team."
            )
        
        # Prevent changing branch if team has sub-teams
        if self.pk and self.sub_teams.exists():
            old_instance = Team.objects.get(pk=self.pk)
            if old_instance.branch_id != self.branch_id:
                raise ValidationError(
                    "Cannot change branch - this parent team has sub-teams in the current branch."
                )

    def _creates_circular_reference(self):
        """Check if assigning this parent would create a circular reference."""
        current = self.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False

    @property
    def is_parent(self):
        """Check if this team has sub-teams."""
        return self.sub_teams.exists()

    @property
    def hierarchy_level(self):
        """Return hierarchy level: 0 for parent, 1 for sub-team."""
        return 1 if self.parent else 0

    def get_all_sub_teams(self):
        """Get all sub-teams for this team."""
        return self.sub_teams.all()

    def get_hierarchy_display(self):
        """Get display string with hierarchy context."""
        if self.parent:
            return f"  └─ {self.name}"
        return self.name
    
    def get_asset_count(self, include_sub_teams=True):
        """
        Get count of assets assigned to this team.
        
        Args:
            include_sub_teams: If True and this is a parent team, include assets from sub-teams
        
        Returns:
            int: Total count of assets
        """
        from django.db.models import Q
        from .asset import Asset
        
        if include_sub_teams and self.is_parent:
            # Include assets from this team and all sub-teams
            # Query from Asset model to include both direct assignments and sub-team assignments
            return Asset.objects.filter(
                Q(team=self) | Q(team__parent=self)
            ).count()
        else:
            # Only count assets directly assigned to this team
            return self.assets.count()
    
    def get_asset_statistics(self, include_sub_teams=True):
        """
        Get detailed statistics for assets assigned to this team.
        
        Args:
            include_sub_teams: If True and this is a parent team, include assets from sub-teams
        
        Returns:
            dict: Statistics including total count, by status, by system type
        """
        from django.db.models import Q, Count
        from .asset import Asset
        
        if include_sub_teams and self.is_parent:
            # Include assets from this team and all sub-teams
            # Query from Asset model to include both direct assignments and sub-team assignments
            assets = Asset.objects.filter(
                Q(team=self) | Q(team__parent=self)
            )
        else:
            # Only assets directly assigned to this team
            assets = self.assets.all()
        
        return {
            'total': assets.count(),
            'by_status': dict(assets.values('status').annotate(count=Count('status')).values_list('status', 'count')),
            'by_system_type': dict(assets.values('system_type').annotate(count=Count('system_type')).values_list('system_type', 'count')),
        }


# Signal handlers for cache invalidation
@receiver(post_save, sender=Team)
def invalidate_team_hierarchy_cache_on_save(sender, instance, **kwargs):
    """Invalidate team hierarchy cache when a team is saved."""
    cache.delete('team_hierarchy')
    cache.delete(f'team_{instance.id}_hierarchy')
    if instance.parent:
        cache.delete(f'team_{instance.parent.id}_sub_teams')


@receiver(post_delete, sender=Team)
def invalidate_team_hierarchy_cache_on_delete(sender, instance, **kwargs):
    """Invalidate team hierarchy cache when a team is deleted."""
    cache.delete('team_hierarchy')
    cache.delete(f'team_{instance.id}_hierarchy')
    # Check if parent exists before accessing it (it might be deleted via CASCADE)
    try:
        if instance.parent_id:  # Use parent_id to avoid database query
            cache.delete(f'team_{instance.parent_id}_sub_teams')
    except:
        pass  # Parent might already be deleted
