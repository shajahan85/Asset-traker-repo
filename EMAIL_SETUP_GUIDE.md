# Email Notifications Setup Guide

Email notifications have been **ENABLED** for all asset lifecycle events.

## 📧 Email Notifications Are Sent For:

1. ✅ **Asset Created** - When a new asset is added
2. ✅ **Asset Updated** - When asset information is modified
3. ✅ **Asset Freed** - When an asset is freed
4. ✅ **Asset Scrapped** - When an asset is scrapped
5. ✅ **Asset Reassigned** - When a freed asset is reassigned to active

## 👥 Current Email Recipients:

Notifications are currently sent to:
- anoop@benzyinfotech.com
- Shajahan.t@benzyinfotech.com
- desktopsupport@benzyinfotech.com
- sreeshob@benzyinfotech.com

**To change recipients:** Edit `assets/services/notification_service.py` line 18-22

---

## 🔧 Email Configuration Options

### **Option 1: Gmail SMTP (Recommended for Testing)**

Add to your `.env` file:

```env
# Email Settings - Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Gmail Setup Steps:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use the generated password (not your regular password)

---

### **Option 2: Office 365 / Outlook SMTP**

Add to your `.env` file:

```env
# Email Settings - Office 365
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@company.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@company.com
```

---

### **Option 3: Custom SMTP Server**

Add to your `.env` file:

```env
# Email Settings - Custom SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourserver.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@yourcompany.com
```

---

### **Option 4: Console Backend (Testing Only)**

For development/testing, emails are printed to console instead of sent:

```env
# Email Settings - Console (Testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@assettracker.com
```

**This is the default in the deployment script.**

---

### **Option 5: File Backend (Save to Disk)**

For testing, emails are saved as files:

```env
# Email Settings - File Backend
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=C:\temp\app-emails
DEFAULT_FROM_EMAIL=noreply@assettracker.com
```

---

## 🚀 Quick Setup for Production

### **Step 1: Choose Email Method**

For production, use Gmail or Office 365 (Option 1 or 2 above)

### **Step 2: Update .env File**

On your test/production server, edit `.env` file:

```powershell
notepad C:\TestServer\asset-tracker\.env
```

Add the email settings based on your choice above.

### **Step 3: Test Email Configuration**

Run this test:

```powershell
cd C:\TestServer\asset-tracker
.\venv\Scripts\Activate.ps1
python manage.py shell
```

Then in Python shell:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email
send_mail(
    'Asset Tracker - Email Test',
    'If you receive this, email is configured correctly!',
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@company.com'],
    fail_silently=False,
)
print("Email sent! Check your inbox.")
```

### **Step 4: Verify Settings**

```powershell
python manage.py shell
```

```python
from django.conf import settings
print("Email Backend:", settings.EMAIL_BACKEND)
print("Email Host:", settings.EMAIL_HOST)
print("Email Port:", settings.EMAIL_PORT)
print("From Email:", settings.DEFAULT_FROM_EMAIL)
```

---

## 📝 Example Email Content

### **When Asset is Created:**

```
Subject: New Asset Created: BIDC1234

New Asset Created

Asset Tag: BIDC1234
System Type: Desktop
Manufacturer: Dell
Operating System: Windows 11
IP Address: 192.168.10.100
Assigned To: John Doe
Team: IT Support
Created By: admin

Particulars: Dell OptiPlex 7090
```

### **When Asset is Freed:**

```
Subject: Asset Freed: BIDC1234

Asset Freed

Asset Tag: BIDC1234
System Type: Desktop
Manufacturer: Dell
Operating System: Windows 11
Previously Assigned To: John Doe
Freed By: admin
Freed Date: 2026-08-04 14:30

Health Status: Healthy
Issues: None
```

---

## 🔒 Security Best Practices

1. **Never commit .env file** to version control
2. **Use App Passwords** for Gmail (not your regular password)
3. **Restrict SMTP access** to your server's IP if possible
4. **Use TLS/SSL** for email transmission
5. **Store passwords securely** in environment variables

---

## 🎯 Change Email Recipients

### **Method 1: Edit notification_service.py**

Edit: `assets/services/notification_service.py`

Find line 18-22:

```python
NOTIFICATION_RECIPIENTS = [
    'anoop@benzyinfotech.com',
    'Shajahan.t@benzyinfotech.com',
    'desktopsupport@benzyinfotech.com',
    'sreeshob@benzyinfotech.com'
]
```

Change to your emails:

```python
NOTIFICATION_RECIPIENTS = [
    'admin@yourcompany.com',
    'it-team@yourcompany.com',
]
```

### **Method 2: Use Environment Variable (Advanced)**

Edit `assets/services/notification_service.py`, change line 18:

```python
NOTIFICATION_RECIPIENTS = settings.ASSET_NOTIFICATION_EMAILS.split(',')
```

Then in `.env` file:

```env
ASSET_NOTIFICATION_EMAILS=admin@company.com,it@company.com,manager@company.com
```

---

## 🐛 Troubleshooting

### **No emails received:**

1. **Check .env configuration**
   ```powershell
   cat .env | Select-String "EMAIL"
   ```

2. **Check Django logs**
   ```powershell
   cat authentication.log -Tail 50
   ```

3. **Test SMTP connection manually**
   ```powershell
   python manage.py shell
   ```
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print("Connected successfully!")
   server.quit()
   ```

### **Authentication errors:**

- For Gmail: Make sure you're using an App Password, not your regular password
- For Office 365: Check if your organization allows SMTP
- Check username format (some require full email, some just username)

### **Emails going to spam:**

1. Add your SMTP server IP to SPF records
2. Set up proper FROM address
3. Ask recipients to whitelist the sender

### **Connection timeout:**

1. Check firewall allows outbound SMTP (port 587 or 465)
2. Verify SMTP server address is correct
3. Try different ports (587 for TLS, 465 for SSL, 25 for unencrypted)

---

## 📊 Email Notification Status

**Current Status:** ✅ **ENABLED**

All email notifications in `assets/services/asset_service.py` have been activated.

To disable again (not recommended):
```python
# Comment out these lines in asset_service.py:
# NotificationService.send_asset_created_notification(asset, user)
```

---

## 🎯 Next Steps

1. **Choose email method** (Gmail, Office 365, or custom SMTP)
2. **Update .env file** with email settings
3. **Test email sending** using Python shell
4. **Create a test asset** to verify notifications work
5. **Update email recipients** if needed

---

**For more information, see:**
- Django Email Documentation: https://docs.djangoproject.com/en/4.2/topics/email/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
