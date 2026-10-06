import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets_accessory'")
result = cursor.fetchone()

if result:
    print("✓ assets_accessory table EXISTS in database")
    cursor.execute("PRAGMA table_info(assets_accessory)")
    columns = cursor.fetchall()
    print(f"  Columns: {len(columns)}")
    for col in columns:
        print(f"    - {col[1]} ({col[2]})")
else:
    print("✗ assets_accessory table DOES NOT EXIST - migration needed")
    print("\nRun: python manage.py makemigrations assets")
