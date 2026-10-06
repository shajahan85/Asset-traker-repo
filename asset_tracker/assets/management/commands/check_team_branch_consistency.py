"""
Management command to check for cross-branch team assignments.

This command validates that all assets with teams have asset.team.branch == asset.branch.
It reports any inconsistencies found and provides detailed information about affected assets.

Usage:
    python manage.py check_team_branch_consistency
"""

from django.core.management.base import BaseCommand
from django.db.models import F
from assets.models import Asset


class Command(BaseCommand):
    """Check for cross-branch team assignments in assets."""
    
    help = 'Check for assets with teams that belong to a different branch than the asset'
    
    def handle(self, *args, **options):
        """Execute the consistency check."""
        self.stdout.write(self.style.SUCCESS('Checking team-branch consistency...'))
        self.stdout.write('')
        
        # Query all assets with both team and branch assigned
        assets_with_teams = Asset.objects.filter(
            team__isnull=False,
            branch__isnull=False
        ).select_related('team', 'team__branch', 'branch')
        
        total_checked = assets_with_teams.count()
        self.stdout.write(f'Total assets with teams and branches: {total_checked}')
        self.stdout.write('')
        
        # Find inconsistencies where asset.team.branch != asset.branch
        inconsistent_assets = assets_with_teams.exclude(
            team__branch=F('branch')
        )
        
        inconsistent_count = inconsistent_assets.count()
        
        if inconsistent_count == 0:
            self.stdout.write(self.style.SUCCESS('✓ No cross-branch team assignments found!'))
            self.stdout.write(self.style.SUCCESS('All assets have teams from their own branch.'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Found {inconsistent_count} cross-branch team assignment(s):'))
            self.stdout.write('')
            
            # Display details for each inconsistent asset
            for asset in inconsistent_assets:
                self.stdout.write(self.style.WARNING(f'Asset: {asset.asset_tag}'))
                self.stdout.write(f'  Serial Number: {asset.serial_number}')
                self.stdout.write(f'  Asset Branch: {asset.branch.name} (ID: {asset.branch.id})')
                self.stdout.write(f'  Team: {asset.team.name} (ID: {asset.team.id})')
                self.stdout.write(f'  Team Branch: {asset.team.branch.name} (ID: {asset.team.branch.id})')
                self.stdout.write(f'  Assigned To: {asset.assigned_to or "N/A"}')
                self.stdout.write('')
            
            self.stdout.write(self.style.ERROR(f'Total inconsistencies: {inconsistent_count}'))
            self.stdout.write(self.style.WARNING('Please correct these assignments to maintain data integrity.'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Consistency check complete!'))
