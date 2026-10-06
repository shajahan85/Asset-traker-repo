# Database Migration Overview

## What is Database Migration?

Your Asset Tracker currently uses **SQLite** (a file-based database) on Windows. For production deployment on Linux, you'll migrate to **PostgreSQL** (a server-based database).

### Why Migrate?

| Feature | SQLite (Current) | PostgreSQL (Production) |
|---------|------------------|-------------------------|
| **Performance** | Good for single user | Excellent for multiple users |
| **Concurrent Access** | Limited | Unlimited |
| **Scalability** | Small-medium data | Large datasets |
| **Reliability** | File-based | Server-based with backups |
| **Location** | db.sqlite3 file | Database server |

---

## Migration Process Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MIGRATION WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

WINDOWS (Development)                LINUX (Production)
═════════════════════                ══════════════════

┌──────────────┐                    
│  SQLite DB   │                    
│  (db.sqlite3)│                    
└──────┬───────┘                    
       │                             
       │ 1. EXPORT                   
       │ python export_database.py   
       ↓                             
┌──────────────────┐                
│ data_backup.json │                
└─────────┬────────┘                
          │                          
          │ 2. UPLOAD                
          │ scp to server            
          ↓                          
                              ┌──────────────────┐
                              │ data_backup.json │
                              └─────────┬────────┘
                                        │
                                        │ 3. IMPORT
                                        │ loaddata command
                                        ↓
                              ┌──────────────────┐
                              │  PostgreSQL DB   │
                              │                  │
                              └──────────────────┘
                                        │
                                        │ 4. VERIFY
                                        │ test_migration.py
                                        ↓
                              ┌──────────────────┐
                              │  Ready for       │
                              │  Production!     │
                              └──────────────────┘
```

---

## Quick Start

### On Windows (Development Machine)

```powershell
# Step 1: Export your data
cd "d:\Asset tracker"
python linux_hosting\export_database.py

# Step 2: Upload to server
scp data_backup.json username@server:/tmp/
```

### On Linux Server (Production)

```bash
# Step 3: Move file and import
sudo mv /tmp/data_backup.json /var/www/asset_tracker/
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py migrate
python manage.py loaddata data_backup.json

# Step 4: Test migration
python linux_hosting/test_migration.py
```

---

## Files Included

### 1. export_database.py
**Purpose:** Export SQLite data to JSON  
**Run On:** Windows  
**Output:** data_backup.json  
**Features:**
- Shows database statistics
- Creates timestamped backup
- Validates export
- Shows file size

### 2. DATABASE_MIGRATION.md
**Purpose:** Complete migration guide  
**Contains:**
- Step-by-step instructions
- Troubleshooting section
- Rollback procedures
- Testing checklist

### 3. test_migration.py
**Purpose:** Verify migration success  
**Run On:** Linux (after import)  
**Tests:**
- Database connection
- Record counts
- Relationships
- Data integrity
- Admin users

### 4. MIGRATION_QUICK_REFERENCE.md
**Purpose:** Quick command reference  
**Contains:**
- All commands in one place
- Quick troubleshooting
- Checklist

---

## What Gets Migrated?

### ✅ Data That Migrates

- **All Assets** - System details, asset tags, types
- **All Employees** - Names, codes, branches, departments
- **All Accessories** - Keyboards, monitors, etc.
- **Asset History** - All changes and assignments
- **Admin Users** - Your admin account
- **Custom Settings** - Any configuration data

### ❌ What Doesn't Migrate

- **Migrations** - Run `python manage.py migrate` on Linux
- **Static Files** - Run `python manage.py collectstatic` on Linux
- **Media Files** - Upload separately if any
- **Virtual Environment** - Create new on Linux
- **Passwords** - May need to reset admin password

---

## Common Questions

### Q: Will my SQLite database be deleted?
**A:** No! The export only reads data. Your Windows database remains unchanged.

### Q: Can I continue development on Windows?
**A:** Yes! Keep using SQLite on Windows. The Linux server will use PostgreSQL independently.

### Q: What if migration fails?
**A:** Your Windows database is safe. On Linux, you can drop and recreate PostgreSQL database and try again.

### Q: Do I need to export again if I add new data?
**A:** If you add data on Windows after initial export, you'll need to export again or add that data manually on Linux.

### Q: Can I test migration before production?
**A:** Yes! You can set up PostgreSQL on Windows to test, or use a staging Linux server.

---

## Troubleshooting Quick Fixes

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "relation does not exist"
```bash
python manage.py migrate
python manage.py loaddata data_backup.json
```

### "duplicate key value"
```bash
# Database has old data, flush it:
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata data_backup.json
```

### "Can't login after migration"
```bash
python manage.py changepassword admin
```

---

## Time Estimates

| Task | Time Required |
|------|---------------|
| Reading documentation | 15 minutes |
| Exporting data (Windows) | 2 minutes |
| Uploading to server | 5 minutes |
| Importing data (Linux) | 5 minutes |
| Testing migration | 10 minutes |
| Troubleshooting (if needed) | 15-30 minutes |
| **Total** | **~30-60 minutes** |

---

## Support Documents

1. **DATABASE_MIGRATION.md** - Full detailed guide
2. **MIGRATION_QUICK_REFERENCE.md** - Quick commands
3. **DEPLOYMENT_GUIDE.md** - Overall deployment
4. **export_database.py** - Export script
5. **test_migration.py** - Testing script

---

## Decision Matrix: When to Migrate?

### Migrate Now If:
- ✅ Deploying to production
- ✅ Need multiple users
- ✅ Want better performance
- ✅ Need reliable backups

### Stay with SQLite If:
- ✅ Only development/testing
- ✅ Single user only
- ✅ Small dataset
- ✅ Not deploying to server

---

## Next Steps

1. **Read:** DATABASE_MIGRATION.md for complete instructions
2. **Export:** Run export_database.py on Windows
3. **Deploy:** Follow DEPLOYMENT_GUIDE.md for server setup
4. **Import:** Load data into PostgreSQL
5. **Test:** Run test_migration.py to verify

---

## Safety Notes

- ✅ Always backup before migration
- ✅ Test on staging server first (if possible)
- ✅ Keep original SQLite database
- ✅ Verify data after import
- ✅ Test all features after migration

---

**Ready to migrate?** Start with **DATABASE_MIGRATION.md**

**Need quick commands?** See **MIGRATION_QUICK_REFERENCE.md**

**Questions?** Check troubleshooting section in **DATABASE_MIGRATION.md**

