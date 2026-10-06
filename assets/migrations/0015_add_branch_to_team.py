# Generated migration for adding branch field to Team model

from django.db import migrations, models
import django.db.models.deletion


def assign_teams_to_kochi_branch(apps, schema_editor):
    """Assign all existing teams to Kochi branch."""
    Team = apps.get_model('assets', 'Team')
    Branch = apps.get_model('assets', 'Branch')
    
    # Get or create Kochi branch
    kochi_branch, created = Branch.objects.get_or_create(
        name='Kochi',
        defaults={'code': 'KCH', 'is_active': True}
    )
    
    if created:
        print(f"Created Kochi branch with code KCH")
    
    # Assign all teams to Kochi branch
    team_count = Team.objects.update(branch=kochi_branch)
    print(f"Assigned {team_count} teams to Kochi branch")
    
    # Validation: check for any cross-branch asset-team assignments
    Asset = apps.get_model('assets', 'Asset')
    inconsistent_assets = Asset.objects.filter(
        team__isnull=False,
        branch__isnull=False
    ).exclude(
        team__branch=models.F('branch')
    )
    
    inconsistent_count = inconsistent_assets.count()
    if inconsistent_count > 0:
        print(f"WARNING: Found {inconsistent_count} assets with cross-branch team assignments")
        for asset in inconsistent_assets[:10]:  # Show first 10
            print(f"  Asset {asset.asset_tag}: branch={asset.branch.name}, team.branch={asset.team.branch.name}")


def reverse_branch_assignment(apps, schema_editor):
    """Reverse migration - remove branch assignments."""
    # Branch field will be removed by schema migration
    # No data migration needed for reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0014_branch_asset_branch'),
    ]

    operations = [
        # Step 1: Add branch field as nullable first
        migrations.AddField(
            model_name='team',
            name='branch',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='teams',
                to='assets.branch',
                help_text='Branch this team belongs to'
            ),
        ),
        
        # Step 2: Assign all teams to Kochi branch
        migrations.RunPython(
            assign_teams_to_kochi_branch,
            reverse_branch_assignment
        ),
        
        # Step 3: Make branch field non-nullable
        migrations.AlterField(
            model_name='team',
            name='branch',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='teams',
                to='assets.branch',
                help_text='Branch this team belongs to',
                db_index=True
            ),
        ),
        
        # Step 4: Remove old unique constraint on name
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=100),
        ),
        
        # Step 5: Add composite index on branch, parent, name
        migrations.AddIndex(
            model_name='team',
            index=models.Index(fields=['branch', 'parent', 'name'], name='team_branch_parent_name_idx'),
        ),
        
        # Step 6: Add unique constraint for team name per branch
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(
                fields=['branch', 'name'],
                name='unique_team_name_per_branch'
            ),
        ),
        
        # Step 7: Update Meta ordering to include branch
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['branch__name', 'name']},
        ),
    ]
