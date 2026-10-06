# Database Migration - Quick Reference Card

Quick commands for migrating Asset Tracker from SQLite to PostgreSQL.

---

## Windows (Export Phase)

### Export Database
```powershell
cd "d:\Asset tracker"
python linux_hosting\export_database.py
```

**Output:** `data_backup.json`

### Upload to Server
```powershell
scp data_backup.json username@server_ip:/tmp/
```

---

## Linux Server (Import Phase)

### Move File to App Directory
```bash
sudo mv /tmp/data_backup.json /var/www/asset_tracker/
cd /var/www/asset_tracker
source venv/bin/activate
```

### Run Migrations (Create Tables)
```bash
python manage.py migrate
```

### Import Data
```bash
python manage.py loaddata data_backup.json
```

### Test Migration
```bash
python linux_hosting/test_migration.py
```

### Verify Counts (Quick Check)
```bash
python manage.py shell
```

```python
from assets.models import Asset, Employee, Accessory, AssetHistory
from django.contrib.auth.models import User

print(f"Assets: {Asset.objects.count()}")
print(f"Employees: {Employee.objects.count()}")
print(f"Accessories: {Accessory.objects.count()}")
print(f"History: {AssetHistory.objects.count()}")
print(f"Users: {User.objects.count()}")
exit()
```

### Reset Admin Password (If Needed)
```bash
python manage.py changepassword admin
```

### Restart Application
```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

---

## Troubleshooting Quick Fixes

### Import Fails (Already Has Data)
```bash
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata data_backup.json
```

### Missing psycopg2
```bash
pip install psycopg2-binary
sudo systemctl restart asset_tracker
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database Connection Error
```bash
# Check .env file
cat .env | grep DB_

# Test PostgreSQL
psql -h localhost -U asset_tracker_user -d asset_tracker_db
```

---

## Checklist

**Export Phase:**
- [ ] Run export script on Windows
- [ ] Verify `data_backup.json` created
- [ ] Upload file to Linux server

**Import Phase:**
- [ ] Move file to `/var/www/asset_tracker/`
- [ ] Run migrations
- [ ] Import data with loaddata
- [ ] Run test script
- [ ] Verify counts match

**Testing:**
- [ ] Login works
- [ ] Assets display
- [ ] Employees display
- [ ] Search works
- [ ] Create test asset
- [ ] Edit test asset
- [ ] Delete test asset

**Post-Migration:**
- [ ] Reset admin password
- [ ] Test all features
- [ ] Set up SSL
- [ ] Configure backups

---

**Full Guide:** See `DATABASE_MIGRATION.md`  
**Support Scripts:** `export_database.py`, `test_migration.py`

