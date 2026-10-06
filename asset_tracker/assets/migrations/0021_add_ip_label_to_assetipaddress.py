# Generated migration to add ip_label field to AssetIPAddress model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0020_migrate_legacy_ips'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetipaddress',
            name='ip_label',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text="Description label for this IP address (e.g., 'WiFi', 'Mobile', 'VPN')"
            ),
        ),
    ]
