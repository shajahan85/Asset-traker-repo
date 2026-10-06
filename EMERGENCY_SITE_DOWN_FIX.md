# EMERGENCY - SITE NOT LOADING

**URGENT:** The entire site is not opening now.

---

## STEP 1: Check if Django is running

**Linux team - run this command:**

```bash
sudo systemctl status asset_tracker
```

**What to look for:**
- If it says `Active: active (running)` → Django is running, move to STEP 2
- If it says `Active: inactive (dead)` or `failed` → Django crashed, move to STEP 3

---

## STEP 2: If Django is running, check for errors in the log

```bash
sudo tail -50 /var/log/asset_tracker/error.log
```

Or if the log is elsewhere:

```bash
sudo journalctl -u asset_tracker -n 50
```

**Send us the last 50 lines** - we'll tell you what's wrong.

---

## STEP 3: If Django crashed, restart it

```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

**After restart, try to open the site.**

If it still doesn't open, run:

```bash
sudo journalctl -u asset_tracker -n 100
```

**Send us the output** - we'll see why it's crashing.

---

## STEP 4: Check if the problem is the file we uploaded

**Did you upload a new asset_forms.py file recently?**

If YES, there might be a syntax error in the file. 

**Quick fix - restore the original file:**

```bash
cd /var/www/asset_tracker/assets/forms/
sudo cp asset_forms.py asset_forms.py.broken
sudo cp asset_forms.py.backup asset_forms.py
sudo systemctl restart asset_tracker
```

Then try to open the site.

---

## STEP 5: If nothing else works - check if port is blocked

```bash
sudo netstat -tlnp | grep 8000
```

Or if using gunicorn/uwsgi:

```bash
sudo netstat -tlnp | grep python
```

This shows if Django is listening on the correct port.

---

## QUICK EMERGENCY QUESTIONS:

Please answer these so we can help faster:

1. **What error do you see in the browser?**
   - "Connection refused"?
   - "502 Bad Gateway"?
   - "500 Internal Server Error"?
   - Blank white page?
   - Or something else?

2. **When did the site stop working?**
   - Right after the SQL UPDATE commands?
   - Right after restarting Django?
   - After uploading a new file?

3. **Was the site working for other users before? Or only certain assets were freezing?**

---

**MOST LIKELY CAUSES:**

1. **Syntax error in asset_forms.py** - The file we uploaded has a Python syntax error
2. **Django crashed** - Need to restart the service
3. **Database connection lost** - MySQL might be down or connection settings wrong

---

## FASTEST FIX TO TRY RIGHT NOW:

**Linux team - run these 3 commands:**

```bash
# 1. Check Django status
sudo systemctl status asset_tracker

# 2. If it's not running, restart it
sudo systemctl restart asset_tracker

# 3. Check if it started successfully
sudo systemctl status asset_tracker
```

**Send us the output of command #3** - we'll see if Django is running or what error it shows.

---

**After you run these commands, tell us:**
- Is the site loading now?
- If not, what does `systemctl status` show?
