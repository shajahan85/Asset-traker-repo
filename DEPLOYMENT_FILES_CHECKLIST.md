# Asset Tracker - Deployment Files Checklist

## ✅ REQUIRED FILES/FOLDERS (Copy these to test server)

### **Core Application Files:**
```
✅ manage.py                          # Django management script
✅ requirements.txt                   # Python dependencies
✅ .env.example                       # Environment template (rename to .env on server)
✅ .gitignore                         # Optional but useful
```

### **Application Folders:**
```
✅ asset_tracker/                     # Main Django project folder
   ├── settings.py
   ├── urls.py
   ├── wsgi.py
   └── __init__.py

✅ assets/                            # Assets app
   ├── models.py
   ├── views.py
   ├── forms/
   ├── templates/
   ├── static/
   ├── services/
   ├── management/
   └── all other .py files

✅ authentication/                    # Authentication app
   ├── models.py
   ├── views.py
   ├── templates/
   └── all other .py files

✅ power_monitoring/                  # Power monitoring app
   ├── models.py
   ├── views.py
   ├── templates/
   └── all other .py files
```

### **Deployment Scripts (NEW - I created these):**
```
✅ deploy_test_server.ps1            # Automated deployment script
✅ start_server.ps1                  # Server start script
✅ DEPLOYMENT.md                     # Deployment guide
✅ QUICK_START.md                    # Quick reference
✅ web.config.example                # IIS configuration template
```

### **Optional Documentation:**
```
⚠️ README.md                         # Project documentation (optional)
⚠️ ASSET_MANAGEMENT_GUIDE.md        # User guide (optional)
```

---

## ❌ NOT REQUIRED (Exclude these - Development/Testing only)

### **Development Tools:**
```
❌ .git/                             # Git version control (only for developers)
❌ .kiro/                            # Kiro IDE configuration
❌ .vscode/                          # VS Code settings
❌ .pytest_cache/                    # Test cache
❌ .hypothesis/                      # Testing framework data
❌ .snapshots/                       # Test snapshots
❌ __pycache__/                      # Python cache (auto-generated)
```

### **Database & Logs (Don't copy existing):**
```
❌ db.sqlite3                        # Your development database
❌ authentication.log                # Development logs
❌ media/                            # Your development uploaded files
❌ staticfiles/                      # Will be regenerated on server
```

### **Environment Files:**
```
❌ .env                              # Your personal environment (has secrets!)
                                     # Use .env.example instead, then configure
```

### **Test & Debug Files:**
```
❌ pytest.ini                        # Test configuration
❌ test_*.py                         # All test files (70+ files!)
❌ debug_*.py                        # All debug scripts
❌ check_*.py                        # All check scripts
❌ fix_*.py                          # All fix scripts
❌ verify_*.py                       # All verify scripts
❌ create_*.py                       # All create scripts
❌ migrate_*.py                      # All migration scripts
❌ restore_*.py                      # All restore scripts
❌ sync_*.py                         # All sync scripts
❌ update_*.py                       # All update scripts
❌ manual_*.py                       # All manual scripts
❌ run_*.py                          # All run scripts
❌ add_*.py                          # All add scripts
```

### **Test HTML Files:**
```
❌ test_*.html                       # All test HTML files
```

### **Documentation (Development-specific):**
```
❌ *_SUMMARY.md                      # All summary documents
❌ *_REPORT.md                       # All report documents
❌ *_TESTING_*.md                    # All testing documents
❌ *_CHECKLIST.md                    # All checklist documents
❌ *_INSTRUCTIONS.md/.txt            # All instruction documents
❌ *_GUIDE.md                        # Most guides (except DEPLOYMENT.md)
❌ CLEAR_CACHE_INSTRUCTIONS.txt      # Development instructions
```

### **Batch Files:**
```
❌ start_server.bat                  # Use start_server.ps1 instead
```

---

## 📦 SIMPLIFIED COPY LIST

### **Method 1: Copy Only These Folders & Files**

```
YOUR PROJECT ROOT/
│
├── manage.py                        ✅ COPY
├── requirements.txt                 ✅ COPY
├── .env.example                     ✅ COPY (rename to .env)
├── .gitignore                       ✅ COPY (optional)
│
├── deploy_test_server.ps1           ✅ COPY
├── start_server.ps1                 ✅ COPY
├── DEPLOYMENT.md                    ✅ COPY
├── QUICK_START.md                   ✅ COPY
├── web.config.example               ✅ COPY
│
├── asset_tracker/                   ✅ COPY ENTIRE FOLDER
├── assets/                          ✅ COPY ENTIRE FOLDER
├── authentication/                  ✅ COPY ENTIRE FOLDER
├── power_monitoring/                ✅ COPY ENTIRE FOLDER
│
└── [Everything else]                ❌ DON'T COPY
```

### **Method 2: Exclude These Patterns**

When copying, exclude files/folders matching these patterns:
```
.git
.kiro
.vscode
.pytest_cache
.hypothesis
.snapshots
__pycache__
*.pyc
*.pyo
*.log
db.sqlite3
.env
media/
staticfiles/
test_*.py
test_*.html
debug_*.py
check_*.py
fix_*.py
verify_*.py
create_*.py
migrate_*.py
restore_*.py
sync_*.py
update_*.py
manual_*.py
run_*.py
add_*.py
*_SUMMARY.md
*_REPORT.md
*_TESTING_*.md
*_CHECKLIST.md
*_INSTRUCTIONS.*
*.bat
pytest.ini
```

---

## 🚀 EASIEST DEPLOYMENT METHOD

### **Option A: PowerShell Script (Automated)**

Run this on your **development machine** to create a clean copy:

```powershell
# Create deployment package
$source = "d:\Asset tracker"
$destination = "d:\Asset_Tracker_Deploy"

# Create destination
New-Item -ItemType Directory -Force -Path $destination

# Copy required files
Copy-Item "$source\manage.py" $destination
Copy-Item "$source\requirements.txt" $destination
Copy-Item "$source\.env.example" $destination
Copy-Item "$source\.gitignore" $destination -ErrorAction SilentlyContinue

# Copy deployment scripts
Copy-Item "$source\deploy_test_server.ps1" $destination -ErrorAction SilentlyContinue
Copy-Item "$source\start_server.ps1" $destination -ErrorAction SilentlyContinue
Copy-Item "$source\DEPLOYMENT.md" $destination -ErrorAction SilentlyContinue
Copy-Item "$source\QUICK_START.md" $destination -ErrorAction SilentlyContinue
Copy-Item "$source\web.config.example" $destination -ErrorAction SilentlyContinue

# Copy application folders
Copy-Item "$source\asset_tracker" $destination -Recurse -Force
Copy-Item "$source\assets" $destination -Recurse -Force
Copy-Item "$source\authentication" $destination -Recurse -Force
Copy-Item "$source\power_monitoring" $destination -Recurse -Force

Write-Host "✓ Deployment package created at: $destination" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy the 'Asset_Tracker_Deploy' folder to your test server"
Write-Host "2. On test server, run: .\deploy_test_server.ps1"
```

### **Option B: Manual Copy**

1. **Create new folder:** `C:\Asset_Tracker_Clean`
2. **Copy only these folders:**
   - `asset_tracker/`
   - `assets/`
   - `authentication/`
   - `power_monitoring/`
3. **Copy these files:**
   - `manage.py`
   - `requirements.txt`
   - `.env.example`
   - `deploy_test_server.ps1`
   - `start_server.ps1`
   - `DEPLOYMENT.md`
   - `QUICK_START.md`
4. **Transfer to test server**
5. **On test server, rename** `.env.example` to `.env`

---

## 📊 SIZE COMPARISON

**Your current folder:** ~500MB+ (with all test files, database, cache)
**Clean deployment:** ~50MB (90% smaller!)

**What you're removing:**
- 70+ test files
- 30+ debug scripts
- 20+ documentation files
- Development database
- Cache folders
- Git history
- All logs

---

## ⚠️ IMPORTANT NOTES

### **About .env File:**
- ❌ **NEVER copy your .env file** (contains secrets!)
- ✅ **Copy .env.example** instead
- ✅ **Create new .env on server** with server-specific values

### **About Database:**
- ❌ **Don't copy db.sqlite3** (development data)
- ✅ **Fresh database will be created** on server
- ✅ **Import production data** after setup if needed

### **About Media Files:**
- ❌ **Don't copy media/ folder** initially
- ✅ **Will be created automatically** by deployment script
- ✅ **Copy specific files later** if you need them

### **About Static Files:**
- ❌ **Don't copy staticfiles/** folder
- ✅ **Will be generated** by `collectstatic` command

---

## 🎯 RECOMMENDED WORKFLOW

### **1. On Development Machine:**
```powershell
# Run the PowerShell script above to create clean copy
# Result: d:\Asset_Tracker_Deploy (clean folder)
```

### **2. Transfer to Test Server:**
```
- Copy entire Asset_Tracker_Deploy folder to test server
- Location: C:\TestServer\asset-tracker
```

### **3. On Test Server:**
```powershell
cd C:\TestServer\asset-tracker
.\deploy_test_server.ps1
# Script handles everything automatically!
```

---

## 💡 PRO TIP

Create a `.deployignore` file (like `.gitignore`) to remember what not to copy:
```
.git/
.kiro/
.vscode/
.pytest_cache/
.hypothesis/
__pycache__/
*.pyc
*.log
db.sqlite3
.env
media/
staticfiles/
test_*.py
debug_*.py
*_SUMMARY.md
```

---

## ✅ VERIFICATION

After copying to test server, your folder should look like:
```
asset-tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── deploy_test_server.ps1
├── start_server.ps1
├── asset_tracker/
├── assets/
├── authentication/
└── power_monitoring/
```

That's it! About 10 items instead of 150+.

---

**Questions? Check DEPLOYMENT.md or QUICK_START.md for detailed instructions.**
