═══════════════════════════════════════════════════════════════════════════════
                         DEPLOY TO LINUX - PACKAGE
            Files Modified in August-September 2026 (13 files)
═══════════════════════════════════════════════════════════════════════════════

This package contains ONLY the files that were modified recently.
All files have recent modification dates (Aug-Sep 2026).

═══════════════════════════════════════════════════════════════════════════════
📦 WHAT'S IN THIS PACKAGE
═══════════════════════════════════════════════════════════════════════════════

DEPLOY_TO_LINUX/
└── assets/
    ├── views.py                               (2026-09-04)
    ├── views_server_controller.py             (2026-09-09)
    ├── forms/
    │   └── asset_forms.py                     (2026-09-15) ⭐ Bug fix
    ├── services/
    │   ├── asset_service.py                   (2026-09-04)
    │   └── notification_service.py            (2026-09-03)
    ├── templates/assets/
    │   ├── base.html                          (2026-09-08)
    │   ├── asset_form.html                    (2026-09-03)
    │   ├── freed_systems.html                 (2026-09-08)
    │   ├── free_ips.html                      (2026-08-31)
    │   ├── server_controller_form.html        (2026-09-08)
    │   ├── server_controller_list.html        (2026-09-09)
    │   └── server_controller_reassign.html    (2026-09-08)
    └── static/assets/css/
        └── styles.css                         (2026-09-16) ⭐ TODAY!

Total: 13 files

═══════════════════════════════════════════════════════════════════════════════
🚀 DEPLOYMENT INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

1. Upload this folder to Linux server:
   scp -r DEPLOY_TO_LINUX user@server:/tmp/

2. On Linux server, run these commands:

   # Go to upload location
   cd /tmp/DEPLOY_TO_LINUX

   # Stop services
   sudo systemctl stop asset_tracker nginx

   # Copy files (overwrite existing)
   sudo cp -r assets/* /var/www/asset_tracker/assets/

   # Fix permissions
   sudo chown -R www-data:www-data /var/www/asset_tracker/assets
   sudo chmod -R 755 /var/www/asset_tracker/assets

   # Collect static files (CRITICAL!)
   cd /var/www/asset_tracker
   source venv/bin/activate
   python manage.py collectstatic --clear --noinput

   # Restart services
   sudo systemctl start asset_tracker nginx

   # Verify
   sudo systemctl status asset_tracker nginx

3. YOU (user): Clear browser cache and test!

═══════════════════════════════════════════════════════════════════════════════
✅ WHAT GETS FIXED
═══════════════════════════════════════════════════════════════════════════════

- Page freeze bug (asset_forms.py with limit=30)
- Table scrolling with fixed header (styles.css)
- Server Controllers feature (new)
- Email notification toggle
- UI improvements

═══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL COMMANDS
═══════════════════════════════════════════════════════════════════════════════

MUST run collectstatic:
  python manage.py collectstatic --clear --noinput

MUST restart services:
  sudo systemctl restart asset_tracker nginx

MUST clear browser cache:
  Ctrl + Shift + Delete → All time → Clear

═══════════════════════════════════════════════════════════════════════════════
