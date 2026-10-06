# Database Migration Guide

Complete guide for migrating your Asset Tracker database from Windows SQLite to Linux PostgreSQL.

---

## Overview

This guide covers migrating your existing data from:
- **Source:** Windows development machine with SQLite database
- **Target:** Linux production server with PostgreSQL database

**Time Required:** 30-60 minutes  
**Difficulty:** Intermediate  
**Downtime:** Required during migration

---

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Step 1: Export Data from Windows](#step-1-export-data-from-windows)
3. [Step 2: Prepare Linux Server](#step-2-prepare-linux-server)
4. [Step 3: Import Data to PostgreSQL](#step-3-import-data-to-postgresql)
5. [Step 4: Verify Migration](#step-4-verify-migration)
6. [Step 5: Testing](#step-5-testing)
7. [Troubleshooting](#troubleshooting)
8. [Rollback Procedure](#rollback-procedure)

---

## Pre-Migration Checklist

Before starting, ensure you have:

- [ ] Access to Windows machine with current database
- [ ] SSH access to Linux server
- [ ] PostgreSQL installed and running on Linux server
- [ ] Database and user created in PostgreSQL
- [ ] Application deployed to Linux server
- [ ] Backup of current SQLite database (`db.sqlite3`)
- [ ] All Django migrations applied on both systems

### Verify Current Database

On **Windows**, check your database:

```powershell
cd "d:\Asset tracker"
python manage.py showmigrations
```

All migrations should show `[X]` (applied).

---

## Step 1: Export Data from Windows

### 1.1 Run Export Script

On your **Windows machine**:

```powershell
cd "d:\Asset tracker"

# Run the export script
python linux_hosting\export_database.py
```

**What this script does:**
- Connects to your SQLite database
- Shows statistics (number of records per model)
- Exports all data to JSON format
- Creates two files:
  - `data_backup.json` (main export file)
  - `database_backup_YYYYMMDD_HHMMSS.json` (timestamped backup)

**Example output:**
```
==============================================================
Asset Tracker Database Export
==============================================================

✓ Database connection successful

Database Statistics:
----------------------------------------
  assets.Asset                  :   156 records
  assets.Employee               :    45 records
  assets.Accessory              :    89 records
  assets.AssetHistory           :   234 records
  auth.User                     :     3 records
----------------------------------------
  Total models with data        :    5

Total records to export: 527

Proceed with export? (yes/no): yes

Exporting data...
  Output files:
    - data_backup.json
    - database_backup_20241205_143022.json

✓ Exported 527 records successfully
✓ Saved to: data_backup.json
✓ Saved to: database_backup_20241205_143022.json

Backup file size: 156.34 KB

==============================================================
Export completed successfully!
==============================================================
```

### 1.2 Verify Export File

Check that `data_backup.json` was created:

```powershell
# Check file exists and size
dir data_backup.json

# Optional: Preview first few lines
Get-Content data_backup.json -Head 20
```

### 1.3 Manual Export (Alternative Method)

If the script fails, use Django's built-in command:

```powershell
python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.permission --exclude admin.logentry --exclude sessions.session --indent 2 > data_backup.json
```

---

## Step 2: Prepare Linux Server

### 2.1 Upload Data File to Server

From **Windows**, upload the backup file:

**Using SCP (recommended):**
```powershell
scp data_backup.json username@your_server_ip:/tmp/
```

**Using FileZilla or WinSCP:**
- Connect to your server via SFTP
- Upload `data_backup.json` to `/tmp/` directory

### 2.2 Verify Upload

On **Linux server**, verify the file:

```bash
ls -lh /tmp/data_backup.json
```

### 2.3 Move File to Application Directory

```bash
sudo mv /tmp/data_backup.json /var/www/asset_tracker/
sudo chown www-data:www-data /var/www/asset_tracker/data_backup.json
```

---

## Step 3: Import Data to PostgreSQL

### 3.1 Ensure PostgreSQL is Ready

Verify PostgreSQL is running:

```bash
sudo systemctl status postgresql
```

Test database connection:

```bash
sudo -u postgres psql -d asset_tracker_db -c "SELECT version();"
```

### 3.2 Run Migrations First

**Important:** Run migrations BEFORE importing data to create all tables.

```bash
cd /var/www/asset_tracker
source venv/bin/activate

# Show migration status
python manage.py showmigrations

# Apply all migrations
python manage.py migrate

# Verify tables were created
python manage.py dbshell
# In PostgreSQL shell:
\dt
\q
```

You should see all Django tables created (assets_asset, assets_employee, etc.).

### 3.3 Import Data

Now import your data:

```bash
cd /var/www/asset_tracker
source venv/bin/activate

python manage.py loaddata data_backup.json
```

**Expected output:**
```
Installed 527 object(s) from 1 fixture(s)
```

### 3.4 Handle Import Errors

**Common Issue: Primary Key Conflicts**

If you get primary key errors, try flushing first (⚠️ **this deletes existing data**):

```bash
# Only if import fails and database is empty
python manage.py flush --no-input
python manage.py loaddata data_backup.json
```

**Common Issue: Foreign Key Violations**

This usually means migrations weren't run properly. Solution:

```bash
python manage.py migrate --fake-initial
python manage.py loaddata data_backup.json
```

---

## Step 4: Verify Migration

### 4.1 Check Record Counts

Verify all data was imported:

```bash
cd /var/www/asset_tracker
source venv/bin/activate

python manage.py shell
```

In Python shell:

```python
from assets.models import Asset, Employee, Accessory, AssetHistory
from django.contrib.auth.models import User

print(f"Assets: {Asset.objects.count()}")
print(f"Employees: {Employee.objects.count()}")
print(f"Accessories: {Accessory.objects.count()}")
print(f"History: {AssetHistory.objects.count()}")
print(f"Users: {User.objects.count()}")

# Exit shell
exit()
```

**Compare these numbers with your Windows export output.**

### 4.2 Check Sample Records

Verify actual data:

```bash
python manage.py shell
```

```python
from assets.models import Asset, Employee

# Check first asset
asset = Asset.objects.first()
print(f"Asset Tag: {asset.asset_tag}")
print(f"Type: {asset.asset_type}")
print(f"Employee: {asset.employee}")

# Check first employee
employee = Employee.objects.first()
print(f"Name: {employee.name}")
print(f"Employee Code: {employee.employee_code}")
print(f"Assets: {employee.assets.count()}")

exit()
```

### 4.3 Verify Admin User

Try logging in as admin:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Check admin user exists
admin = User.objects.filter(is_superuser=True).first()
print(f"Admin username: {admin.username}")
print(f"Admin email: {admin.email}")

exit()
```

**Note:** If admin password doesn't work, reset it:

```bash
python manage.py changepassword admin
```

---

## Step 5: Testing

### 5.1 Start Test Server

Start Gunicorn (if not already running):

```bash
sudo systemctl start asset_tracker
sudo systemctl status asset_tracker
```

### 5.2 Test Web Interface

Open your browser and test:

1. **Access site:** `http://your_server_ip` or `https://your_domain.com`

2. **Login:** Use your admin credentials

3. **Test Features:**
   - [ ] Dashboard loads
   - [ ] Asset list shows all assets
   - [ ] Employee list shows all employees
   - [ ] Search works
   - [ ] Filtering works
   - [ ] View asset details
   - [ ] View employee details
   - [ ] Check asset history
   - [ ] View accessories
   - [ ] Static files load (CSS, images)

### 5.3 Test CRUD Operations

⚠️ **Create a test asset first, then modify it:**

- [ ] Create new test asset
- [ ] Edit test asset
- [ ] View test asset history
- [ ] Delete test asset (soft delete if applicable)

### 5.4 Test Critical Features

Based on your application:

- [ ] Asset assignment to employee
- [ ] Asset freeing
- [ ] Freed system reassignment
- [ ] Accessories assignment
- [ ] Export functionality
- [ ] Import functionality (if any)
- [ ] Email notifications (if enabled)

---

## Troubleshooting

### Issue: "No module named 'psycopg2'"

**Solution:**
```bash
pip install psycopg2-binary
sudo systemctl restart asset_tracker
```

### Issue: "relation does not exist"

**Solution:** Migrations weren't run.
```bash
python manage.py migrate
python manage.py loaddata data_backup.json
```

### Issue: "duplicate key value violates unique constraint"

**Solution:** Database not empty or data already imported.
```bash
# Check what's in database
python manage.py dbshell
SELECT COUNT(*) FROM assets_asset;
\q

# If data exists and you want to start fresh:
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata data_backup.json
```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Can't login with admin password

**Solution:** Reset password after import.
```bash
python manage.py changepassword admin
# Or create new superuser:
python manage.py createsuperuser
```

### Issue: "Database connection failed"

**Solution:** Check `.env` file settings.
```bash
cat /var/www/asset_tracker/.env | grep DB_

# Test PostgreSQL connection manually:
psql -h localhost -U asset_tracker_user -d asset_tracker_db
```

---

## Rollback Procedure

If migration fails and you need to rollback:

### On Linux Server:

```bash
# Stop application
sudo systemctl stop asset_tracker

# Drop and recreate database
sudo -u postgres psql
DROP DATABASE asset_tracker_db;
CREATE DATABASE asset_tracker_db;
GRANT ALL PRIVILEGES ON DATABASE asset_tracker_db TO asset_tracker_user;
\q

# Run migrations again
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py migrate

# Try import again
python manage.py loaddata data_backup.json

# Restart application
sudo systemctl start asset_tracker
```

### On Windows (Continue Development):

Your SQLite database is unchanged. Continue using:

```powershell
cd "d:\Asset tracker"
python manage.py runserver
```

---

## Post-Migration Steps

Once migration is successful:

1. **Update DNS** (if using domain name)
   - Point domain to new server IP

2. **Set up SSL certificate:**
   ```bash
   sudo certbot --nginx -d your_domain.com
   ```

3. **Enable monitoring:**
   - Set up uptime monitoring
   - Configure log rotation
   - Set up backup cron jobs

4. **Schedule regular backups:**
   ```bash
   # Add to crontab
   sudo crontab -e
   
   # Daily backup at 2 AM
   0 2 * * * /var/www/asset_tracker/linux_hosting/backup.sh
   ```

5. **Document credentials** in secure location:
   - Database password
   - Admin password
   - Server SSH password
   - SSL certificate location

---

## Checklist Summary

### Pre-Migration:
- [ ] SQLite database backed up
- [ ] PostgreSQL installed and configured
- [ ] Application deployed to Linux
- [ ] All migrations applied

### Migration:
- [ ] Data exported from Windows
- [ ] Export file uploaded to Linux
- [ ] PostgreSQL migrations run
- [ ] Data imported successfully
- [ ] Record counts verified

### Post-Migration:
- [ ] Web interface tested
- [ ] Login works
- [ ] All features tested
- [ ] Admin password working
- [ ] Static files loading
- [ ] SSL certificate installed
- [ ] Backups scheduled
- [ ] DNS updated (if applicable)

---

## Support Files

- `export_database.py` - Automated export script
- `test_migration.py` - Migration verification script
- `.env.example` - Environment variables template
- `backup.sh` - Database backup script

---

**Last Updated:** December 2024  
**For:** Asset Tracker Django Application  
**Database Migration:** SQLite → PostgreSQL

