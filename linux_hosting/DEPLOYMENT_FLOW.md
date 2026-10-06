# Asset Tracker - Deployment Flow Diagram

Visual guide to understand the deployment architecture and process flow.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS (443) / HTTP (80)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      NGINX Web Server                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Reverse Proxy                                           │ │
│  │  • SSL Termination                                         │ │
│  │  • Static Files Serving (/static/)                        │ │
│  │  • Media Files Serving (/media/)                          │ │
│  │  • Security Headers                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Proxy Pass (Internal)
                         │ localhost:8000
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GUNICORN WSGI Server                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Worker Processes (CPU * 2 + 1)                         │ │
│  │  • Request Handling                                        │ │
│  │  • Process Management                                      │ │
│  │  • Managed by Systemd                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ WSGI Protocol
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DJANGO Application                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │    Views     │  │   Models     │  │  Templates   │   │ │
│  │  │              │  │              │  │              │   │ │
│  │  │  • Assets    │  │  • Asset     │  │  • HTML      │   │ │
│  │  │  • Teams     │  │  • User      │  │  • Forms     │   │ │
│  │  │  • History   │  │  • History   │  │  • Lists     │   │ │
│  │  │  • Export    │  │  • IP Addr   │  │              │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────┬──────────────────────────────────────┬────────────────┘
          │                                      │
          │                                      │
          ▼                                      ▼
┌──────────────────────────┐          ┌──────────────────────────┐
│   PostgreSQL Database    │          │   File System            │
│                          │          │                          │
│  • Asset Data            │          │  • Static Files          │
│  • User Data             │          │    /staticfiles/         │
│  • History Records       │          │                          │
│  • IP Addresses          │          │  • Media Files           │
│  • Teams & Branches      │          │    /media/               │
│                          │          │                          │
└──────────────────────────┘          └──────────────────────────┘
```

## 📊 Request Flow

```
User Request → Nginx → Gunicorn → Django → Database
                                         ↓
                                   Response
                                         ↓
User ← Nginx ← Gunicorn ← Django ← Database
```

### Detailed Request Flow

```
1. User opens browser → http://yourdomain.com/assets/
                                    ↓
2. DNS resolves domain → Server IP (e.g., 192.168.1.100)
                                    ↓
3. Request hits Nginx (Port 80/443)
                                    ↓
4. Nginx checks request type:
   ├─ /static/* → Serve from /var/www/asset_tracker/staticfiles/
   ├─ /media/*  → Serve from /var/www/asset_tracker/media/
   └─ Other     → Proxy to Gunicorn (localhost:8000)
                                    ↓
5. Gunicorn receives request
   ├─ Selects available worker process
   └─ Passes to Django via WSGI
                                    ↓
6. Django processes request:
   ├─ URL routing
   ├─ View function/class
   ├─ Database queries (PostgreSQL)
   ├─ Template rendering
   └─ Response generation
                                    ↓
7. Gunicorn sends response back to Nginx
                                    ↓
8. Nginx sends response to user's browser
                                    ↓
9. Browser renders HTML/CSS/JS
```

## 🔄 Deployment Process Flow

```
START Deployment
        │
        ▼
┌───────────────────┐
│ 1. Server Setup   │
│ • Update system   │
│ • Install packages│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 2. Database Setup │
│ • Create DB       │
│ • Create user     │
│ • Grant perms     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 3. Upload Files   │
│ • Project code    │
│ • Config files    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 4. Configure Env  │
│ • Create .env     │
│ • Set secrets     │
│ • Set DB creds    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 5. Setup Python   │
│ • Create venv     │
│ • Install deps    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 6. Django Setup   │
│ • Run migrations  │
│ • Collectstatic   │
│ • Create superuser│
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 7. Configure Nginx│
│ • Copy config     │
│ • Update domain   │
│ • Test config     │
│ • Reload Nginx    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 8. Setup Gunicorn │
│ • Copy service    │
│ • Copy socket     │
│ • Start service   │
│ • Enable service  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 9. Verify         │
│ • Check services  │
│ • Test HTTP       │
│ • Check logs      │
└─────────┬─────────┘
          │
          ▼
     SUCCESS ✓
```

## 🔐 Data Flow

### Asset Creation Flow

```
User fills form → Submit button
                       ↓
              Frontend validation
                       ↓
              POST to /assets/create/
                       ↓
                Django receives
                       ↓
           Form validation (backend)
                       ↓
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   Valid Form?                    Invalid Form?
        │                             │
        │ Yes                         │ No
        ▼                             ▼
   Save to Database         Return with errors
        │                             │
        ├─ Create Asset record        └─> Display errors
        ├─ Create History entry           to user
        ├─ Send notifications
        │  (emails disabled)
        └─ Redirect to list
                  ↓
           Success message
```

### Authentication Flow

```
User Login Request
        │
        ▼
    Check session
        │
        ├─ Has valid session? → Access granted
        │
        ├─ No session → Show login form
        │                       ↓
        │                Enter credentials
        │                       ↓
        │               Verify with database
        │                       ↓
        │          ┌────────────┴────────────┐
        │          │                         │
        │          ▼                         ▼
        │     Valid?                     Invalid?
        │          │                         │
        │          │ Yes                     │ No
        │          ▼                         ▼
        │   Create session            Show error
        │   Set cookie               Retry login
        │          │
        │          ▼
        └─> Access granted
                  │
                  ▼
         User dashboard/assets
```

## 🔄 Update Flow

```
START Update
        │
        ▼
┌───────────────────┐
│ 1. Backup         │
│ • DB backup       │
│ • Media backup    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 2. Pull Code      │
│ • Git pull        │
│ • Or upload new   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 3. Update Deps    │
│ • pip install     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 4. Run Migrations │
│ • migrate         │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 5. Collectstatic  │
│ • New CSS/JS      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 6. Restart        │
│ • systemctl       │
│   restart         │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ 7. Verify         │
│ • Check status    │
│ • Test features   │
└─────────┬─────────┘
          │
          ▼
     SUCCESS ✓
```

## 📂 Directory Structure

```
/var/www/asset_tracker/
│
├── asset_tracker/          # Django project directory
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── settings_production.py
│
├── assets/                 # Main app
│   ├── models/
│   ├── views.py
│   ├── forms/
│   ├── templates/
│   └── static/
│
├── linux_hosting/          # Deployment files
│   ├── nginx.conf
│   ├── gunicorn_config.py
│   ├── deploy.sh
│   └── *.md
│
├── venv/                   # Virtual environment
│   ├── bin/
│   ├── lib/
│   └── ...
│
├── staticfiles/            # Collected static files
│   ├── admin/
│   ├── assets/
│   └── ...
│
├── media/                  # User uploaded files
│   └── attachments/
│
├── .env                    # Environment variables
├── manage.py
└── requirements.txt

/var/log/asset_tracker/
├── gunicorn_access.log
├── gunicorn_error.log
└── django_errors.log

/etc/nginx/
└── sites-available/
    └── asset_tracker

/etc/systemd/system/
├── asset_tracker.service
└── asset_tracker.socket
```

## 🔌 Port & Process Map

```
Port 80  (HTTP)  → Nginx → Listening
Port 443 (HTTPS) → Nginx → Listening (after SSL)
Port 8000 (Internal) → Gunicorn → localhost only

Processes:
├── nginx (www-data)
├── gunicorn master (www-data)
│   ├── gunicorn worker 1
│   ├── gunicorn worker 2
│   ├── gunicorn worker 3
│   └── gunicorn worker N
└── postgresql (postgres)
```

## 🎯 Summary

**User Request Path:**
Browser → Nginx → Gunicorn → Django → PostgreSQL

**Static Files Path:**
Browser → Nginx → File System (direct serve)

**Admin Access:**
yourdomain.com/admin/ → Same path as above + Django admin

**Deployment Method:**
deploy.sh → Automates all steps in deployment flow

---

This diagram shows the complete flow of:
1. How requests are processed
2. How components interact
3. How deployment happens
4. How updates are applied

For detailed instructions, see other documentation files!
