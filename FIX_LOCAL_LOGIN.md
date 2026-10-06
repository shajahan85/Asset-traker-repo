# FIX - Cannot Login on Local Laptop

**Problem:** Your laptop uses SQLite database which is empty (no users)  
**Solution:** Create an admin user account

---

## Option 1: Use Windows PowerShell (Not the broken terminal in IDE)

1. **Open Windows PowerShell** (not the IDE terminal)
   - Press `Windows + X`
   - Click "Windows PowerShell" or "Terminal"

2. **Navigate to your project:**
   ```powershell
   cd "d:\Asset tracker"
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Create admin user:**
   ```powershell
   python manage.py createsuperuser
   ```

5. **Follow the prompts:**
   ```
   Username: admin
   Email: admin@example.com
   Password: [type your password]
   Password (again): [type same password]
   ```

6. **Now try to log in to the site** at `http://192.168.11.213:8000/`
   - Username: `admin`
   - Password: [the password you just entered]

---

## Option 2: Connect to Production MySQL Database

If you want to use the same database as production (with all the real data):

1. **Edit the .env file** at `d:\Asset tracker\.env`

2. **Change these lines:**

   **FROM:**
   ```
   DATABASE_ENGINE=django.db.backends.sqlite3
   DATABASE_NAME=db.sqlite3
   ```

   **TO:**
   ```
   DATABASE_ENGINE=django.db.backends.mysql
   DATABASE_NAME=asset_tracker
   DATABASE_USER=your_mysql_username
   DATABASE_PASSWORD=your_mysql_password
   DATABASE_HOST=192.168.11.213
   DATABASE_PORT=3306
   ```

3. **Save the file**

4. **Restart Django** (in the IDE, stop the server and start it again)

5. **Now you can log in with the same username/password as production**

---

## Which Option Should You Choose?

### Choose Option 1 (Create local admin user) if:
- ✅ You just want to test the site locally
- ✅ You don't need the production data
- ✅ Faster and simpler

### Choose Option 2 (Connect to MySQL) if:
- ✅ You need to see the real production data
- ✅ You want to test with actual assets (BIDC1326, etc.)
- ✅ You have the MySQL credentials

---

## After Fixing Login:

Once you can log in, the site should work normally EXCEPT:
- Assets BIDC1326, BIDC1544, BIDC1569 will still freeze (database corruption issue)
- This needs to be fixed with SQL commands on the MySQL database

---

**Try Option 1 first (it's easier!) and let me know if you can log in.**
