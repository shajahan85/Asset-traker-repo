#!/usr/bin/env python
"""
Database Export Script for Asset Tracker
=========================================

This script exports all data from SQLite database to JSON format
for migration to PostgreSQL on Linux server.

Usage:
    python export_database.py
    python export_database.py --yes    (skip confirmation)

Output:
    - data_backup.json (all application data)
    - database_backup_YYYYMMDD_HHMMSS.json (timestamped copy)

Author: Asset Tracker Team
Date: 2024
"""

import os
import sys
import json
import argparse
from datetime import datetime
import django

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.core.management import call_command
from django.db import connection


def check_database_connection():
    """Verify database connection."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def get_database_stats():
    """Get statistics about the database."""
    from django.apps import apps
    
    stats = {}
    for model in apps.get_models():
        try:
            count = model.objects.count()
            if count > 0:
                stats[model._meta.label] = count
        except Exception as e:
            print(f"Warning: Could not count {model._meta.label}: {e}")
    
    return stats


def export_data(auto_confirm=False):
    """Export database to JSON file."""
    print("\n" + "="*60)
    print("Asset Tracker Database Export")
    print("="*60 + "\n")
    
    # Check database connection
    if not check_database_connection():
        return False
    
    # Get database statistics
    print("\nDatabase Statistics:")
    print("-" * 40)
    stats = get_database_stats()
    for model_label, count in sorted(stats.items()):
        print(f"  {model_label:30s} : {count:5d} records")
    print("-" * 40)
    print(f"  Total models with data     : {len(stats)}")
    print()
    
    # Confirm export
    total_records = sum(stats.values())
    print(f"Total records to export: {total_records}\n")
    
    if not auto_confirm:
        response = input("Proceed with export? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Export cancelled.")
            return False
    else:
        print("Auto-confirming export (--yes flag used)\n")
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"database_backup_{timestamp}.json"
    
    print("\nExporting data...")
    print(f"  Output files:")
    print(f"    - data_backup.json")
    print(f"    - {backup_filename}")
    print()
    
    try:
        # Export to temporary file first
        temp_file = "temp_export.json"
        
        # Exclude system tables that will be regenerated
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.permission',
            '--exclude', 'admin.logentry',
            '--exclude', 'sessions.session',
            '--output', temp_file
        )
        
        # Read and validate JSON
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Exported {len(data)} records successfully")
        
        # Save as data_backup.json
        with open('data_backup.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to: data_backup.json")
        
        # Save timestamped backup
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to: {backup_filename}")
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        # Show file sizes
        backup_size = os.path.getsize('data_backup.json') / 1024
        print(f"\nBackup file size: {backup_size:.2f} KB")
        
        print("\n" + "="*60)
        print("Export completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Copy data_backup.json to your Linux server")
        print("2. Follow the migration guide in linux_hosting/DATABASE_MIGRATION.md")
        print("3. Import data using: python manage.py loaddata data_backup.json")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Export Asset Tracker database to JSON for migration'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    try:
        success = export_data(auto_confirm=args.yes)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nExport cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
