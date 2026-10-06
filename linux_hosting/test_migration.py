#!/usr/bin/env python
"""
Migration Testing Script for Asset Tracker
===========================================

This script verifies database migration was successful by:
- Checking record counts
- Validating data integrity
- Testing relationships
- Verifying critical fields

Usage:
    python test_migration.py

Use this AFTER importing data to PostgreSQL on Linux server.

Author: Asset Tracker Team
Date: 2024
"""

import os
import sys
import django

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from django.apps import apps


class MigrationTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = []
    
    def print_header(self, title):
        """Print section header."""
        print("\n" + "="*60)
        print(title)
        print("="*60)
    
    def print_subheader(self, title):
        """Print subsection header."""
        print("\n" + title)
        print("-"*60)
    
    def test_pass(self, message):
        """Record passed test."""
        print(f"  ✓ {message}")
        self.passed_tests += 1
    
    def test_fail(self, message):
        """Record failed test."""
        print(f"  ✗ {message}")
        self.failed_tests += 1
    
    def test_warning(self, message):
        """Record warning."""
        print(f"  ⚠ {message}")
        self.warnings.append(message)
    
    def test_database_connection(self):
        """Test 1: Database connectivity."""
        self.print_subheader("Test 1: Database Connection")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                self.test_pass(f"Connected to database")
                print(f"    Database: {version.split(',')[0]}")
            return True
        except Exception as e:
            self.test_fail(f"Database connection failed: {e}")
            return False
    
    def test_model_counts(self):
        """Test 2: Record counts for all models."""
        self.print_subheader("Test 2: Model Record Counts")
        
        counts = {}
        total_records = 0
        
        for model in apps.get_models():
            try:
                count = model.objects.count()
                counts[model._meta.label] = count
                total_records += count
                
                if count > 0:
                    self.test_pass(f"{model._meta.label}: {count} records")
                else:
                    self.test_warning(f"{model._meta.label}: 0 records (empty)")
            except Exception as e:
                self.test_fail(f"{model._meta.label}: Error - {e}")
        
        print(f"\n  Total records across all models: {total_records}")
        
        if total_records == 0:
            self.test_fail("No data found in database!")
            return False
        else:
            self.test_pass(f"Database contains {total_records} total records")
            return True
    
    def test_core_models(self):
        """Test 3: Core application models."""
        self.print_subheader("Test 3: Core Application Models")
        
        try:
            from assets.models import Asset, Employee, Accessory, AssetHistory
            
            # Test Asset model
            asset_count = Asset.objects.count()
            if asset_count > 0:
                self.test_pass(f"Assets: {asset_count} records")
                
                # Check first asset has required fields
                first_asset = Asset.objects.first()
                if first_asset.asset_tag:
                    self.test_pass(f"Sample asset tag: {first_asset.asset_tag}")
                else:
                    self.test_warning("Sample asset has no asset_tag")
            else:
                self.test_warning("No assets in database")
            
            # Test Employee model
            employee_count = Employee.objects.count()
            if employee_count > 0:
                self.test_pass(f"Employees: {employee_count} records")
                
                # Check first employee
                first_employee = Employee.objects.first()
                if first_employee.name:
                    self.test_pass(f"Sample employee: {first_employee.name}")
                else:
                    self.test_warning("Sample employee has no name")
            else:
                self.test_warning("No employees in database")
            
            # Test Accessory model
            accessory_count = Accessory.objects.count()
            if accessory_count > 0:
                self.test_pass(f"Accessories: {accessory_count} records")
            else:
                self.test_warning("No accessories in database")
            
            # Test AssetHistory model
            history_count = AssetHistory.objects.count()
            if history_count > 0:
                self.test_pass(f"Asset History: {history_count} records")
            else:
                self.test_warning("No asset history in database")
            
            return True
            
        except Exception as e:
            self.test_fail(f"Core model test failed: {e}")
            return False
    
    def test_relationships(self):
        """Test 4: Model relationships."""
        self.print_subheader("Test 4: Model Relationships")
        
        try:
            from assets.models import Asset, Employee
            
            # Test Asset -> Employee relationship
            assets_with_employees = Asset.objects.exclude(employee__isnull=True).count()
            if assets_with_employees > 0:
                self.test_pass(f"{assets_with_employees} assets linked to employees")
            else:
                self.test_warning("No assets linked to employees")
            
            # Test Employee -> Assets relationship
            employees_with_assets = Employee.objects.filter(assets__isnull=False).distinct().count()
            if employees_with_assets > 0:
                self.test_pass(f"{employees_with_assets} employees have assets")
            else:
                self.test_warning("No employees have assets")
            
            # Test Accessories -> Assets relationship
            from assets.models import Accessory
            accessories_with_assets = Accessory.objects.exclude(asset__isnull=True).count()
            if accessories_with_assets > 0:
                self.test_pass(f"{accessories_with_assets} accessories linked to assets")
            else:
                self.test_warning("No accessories linked to assets")
            
            return True
            
        except Exception as e:
            self.test_fail(f"Relationship test failed: {e}")
            return False
    
    def test_admin_users(self):
        """Test 5: Admin user accounts."""
        self.print_subheader("Test 5: Admin User Accounts")
        
        try:
            # Check for superusers
            superusers = User.objects.filter(is_superuser=True)
            if superusers.exists():
                self.test_pass(f"Found {superusers.count()} superuser(s)")
                for user in superusers:
                    print(f"    - {user.username} ({user.email})")
            else:
                self.test_fail("No superuser accounts found!")
                print("    You need to create a superuser: python manage.py createsuperuser")
            
            # Check total users
            total_users = User.objects.count()
            self.test_pass(f"Total users: {total_users}")
            
            return superusers.exists()
            
        except Exception as e:
            self.test_fail(f"Admin user test failed: {e}")
            return False
    
    def test_data_integrity(self):
        """Test 6: Data integrity checks."""
        self.print_subheader("Test 6: Data Integrity")
        
        try:
            from assets.models import Asset, Employee
            
            # Check for duplicate asset tags
            from django.db.models import Count
            duplicates = Asset.objects.values('asset_tag').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            if duplicates.exists():
                self.test_warning(f"Found {duplicates.count()} duplicate asset tags")
                for dup in duplicates[:5]:
                    print(f"    - {dup['asset_tag']}: {dup['count']} occurrences")
            else:
                self.test_pass("No duplicate asset tags")
            
            # Check for employees without codes
            employees_no_code = Employee.objects.filter(employee_code__isnull=True).count()
            if employees_no_code > 0:
                self.test_warning(f"{employees_no_code} employees without employee_code")
            else:
                self.test_pass("All employees have employee codes")
            
            # Check for assets without types
            assets_no_type = Asset.objects.filter(asset_type__isnull=True).count()
            if assets_no_type > 0:
                self.test_warning(f"{assets_no_type} assets without type")
            else:
                self.test_pass("All assets have types")
            
            return True
            
        except Exception as e:
            self.test_fail(f"Data integrity test failed: {e}")
            return False
    
    def test_database_features(self):
        """Test 7: Database-specific features."""
        self.print_subheader("Test 7: Database Features")
        
        try:
            # Check database backend
            backend = connection.settings_dict['ENGINE']
            self.test_pass(f"Database backend: {backend}")
            
            if 'postgresql' in backend:
                # PostgreSQL specific tests
                with connection.cursor() as cursor:
                    # Check encoding
                    cursor.execute("SHOW client_encoding")
                    encoding = cursor.fetchone()[0]
                    self.test_pass(f"Database encoding: {encoding}")
                    
                    # Check timezone
                    cursor.execute("SHOW timezone")
                    timezone = cursor.fetchone()[0]
                    self.test_pass(f"Database timezone: {timezone}")
            
            return True
            
        except Exception as e:
            self.test_fail(f"Database features test failed: {e}")
            return False
    
    def generate_summary(self):
        """Generate test summary."""
        self.print_header("Test Summary")
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTests Passed:  {self.passed_tests}")
        print(f"Tests Failed:  {self.failed_tests}")
        print(f"Warnings:      {len(self.warnings)}")
        print(f"Pass Rate:     {pass_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED - Migration Successful!")
            print("="*60)
            print("\nNext steps:")
            print("1. Test the web interface")
            print("2. Verify all features work correctly")
            print("3. Set up SSL certificate")
            print("4. Configure backups")
            return True
        else:
            print("\n" + "="*60)
            print("✗ SOME TESTS FAILED - Review errors above")
            print("="*60)
            print("\nRecommended actions:")
            print("1. Review failed tests")
            print("2. Check DATABASE_MIGRATION.md troubleshooting section")
            print("3. Verify data_backup.json was imported correctly")
            return False


def main():
    """Main test execution."""
    print("\n" + "="*60)
    print("Asset Tracker - Migration Testing")
    print("="*60)
    print("\nThis script will verify your database migration.\n")
    
    tester = MigrationTester()
    
    # Run all tests
    tests = [
        tester.test_database_connection,
        tester.test_model_counts,
        tester.test_core_models,
        tester.test_relationships,
        tester.test_admin_users,
        tester.test_data_integrity,
        tester.test_database_features,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            tester.test_fail(f"Test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    # Generate summary
    success = tester.generate_summary()
    
    # Show warnings if any
    if tester.warnings:
        print("\n" + "="*60)
        print("Warnings Summary")
        print("="*60)
        for i, warning in enumerate(tester.warnings, 1):
            print(f"{i}. {warning}")
    
    print()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
