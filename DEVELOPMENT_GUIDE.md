# Development Guide - Which Files Change for Features

This guide explains which files typically get modified when adding or changing features in the Asset Tracker application.

---

## 📁 Project Structure Overview

```
Asset tracker/
├── assets/                          ← Main application folder
│   ├── models/                      ← Database models
│   ├── views.py                     ← View functions/classes
│   ├── views_*.py                   ← Specialized view modules
│   ├── urls.py                      ← URL routing
│   ├── forms/                       ← Form definitions
│   ├── services/                    ← Business logic
│   ├── templates/assets/            ← HTML templates
│   └── static/assets/               ← CSS, JS, images
├── asset_tracker/                   ← Project settings
│   ├── settings.py                  ← Configuration
│   ├── urls.py                      ← Root URL config
│   └── middleware.py                ← Middleware (auth, etc.)
└── deployment_package/              ← Files ready for server
```

---

## 🎯 Common Feature Changes

### 1️⃣ Adding a New Page/Feature

**Example:** Server Controllers page

**Files that change:**
```
✅ assets/views_[feature].py         ← New view file (create)
✅ assets/urls.py                     ← Add URL routes
✅ assets/templates/assets/[page].html ← New template (create)
✅ assets/templates/assets/base.html  ← Add navigation link
✅ assets/static/assets/css/styles.css ← Add styles (optional)
```

**Steps:**
1. Create view file: `assets/views_server_controller.py`
2. Add URL patterns in `assets/urls.py`
3. Create templates in `assets/templates/assets/`
4. Update navigation in `base.html`
5. Add CSS if needed

---

### 2️⃣ Adding a Filter/Search Feature

**Example:** IP filter with VM detection

**Files that change:**
```
✅ assets/views_[feature].py         ← Update get_queryset() method
✅ assets/views_[feature].py         ← Update get_context_data()
✅ assets/templates/assets/[page].html ← Add filter input field
```

**Steps:**
1. Modify view's `get_queryset()` to handle filter parameter
2. Add context variables in `get_context_data()`
3. Add input field in template
4. Add filter logic (queries)

---

### 3️⃣ Adding a Form Field

**Example:** Email notification toggle

**Files that change:**
```
✅ assets/forms/[model]_forms.py     ← Add field to form
✅ assets/templates/assets/[form].html ← Add field to template
✅ assets/models/[model].py          ← Add field to model (if new)
✅ migrations/ (if model changed)    ← Database migration
```

**Steps:**
1. Add field to model (if needed)
2. Run `python manage.py makemigrations`
3. Add field to form class
4. Add field to template
5. Update view logic if needed

---

### 4️⃣ Modifying Display/UI

**Example:** Increase filter field height

**Files that change:**
```
✅ assets/templates/assets/[page].html ← Update inline styles or classes
✅ assets/static/assets/css/styles.css ← Add/modify CSS (better approach)
```

**Steps:**
1. Either add inline styles in template
2. Or add CSS classes in styles.css
3. Hard refresh browser (Ctrl+F5)

---

### 5️⃣ Adding Business Logic

**Example:** Skip email sending logic

**Files that change:**
```
✅ assets/services/[service].py      ← Add/modify service method
✅ assets/views.py or views_*.py     ← Call service method
```

**Steps:**
1. Add logic to appropriate service file
2. Call from view
3. Keep views thin, services thick

---

### 6️⃣ Adding Authentication/Permissions

**Example:** Login required middleware

**Files that change:**
```
✅ asset_tracker/middleware.py       ← Add middleware class
✅ asset_tracker/settings.py         ← Register middleware
✅ assets/views.py                   ← Add mixins/decorators
```

**Steps:**
1. Create middleware class
2. Add to MIDDLEWARE in settings.py
3. Use LoginRequiredMixin in views

---

### 7️⃣ Adding a New Model

**Example:** HyperVVM model

**Files that change:**
```
✅ assets/models/[model].py          ← Create model file
✅ assets/models/__init__.py         ← Import model
✅ assets/admin.py                   ← Register in admin
✅ migrations/                       ← Create migration
```

**Steps:**
1. Create model file
2. Import in `__init__.py`
3. Run `python manage.py makemigrations`
4. Run `python manage.py migrate`
5. Register in admin (optional)

---

### 8️⃣ Adding Export Functionality

**Example:** Export to Excel

**Files that change:**
```
✅ assets/services/export_service.py ← Add export method
✅ assets/views.py or views_*.py     ← Add export view
✅ assets/urls.py                    ← Add export URL
✅ assets/templates/assets/[page].html ← Add export button
```

**Steps:**
1. Add export method in service
2. Create view to call service
3. Add URL route
4. Add button in template

---

### 9️⃣ Adding Notifications/Emails

**Example:** Email notifications with employee code

**Files that change:**
```
✅ assets/services/notification_service.py ← Email logic
✅ assets/templates/assets/emails/[type].html ← Email templates
✅ assets/views.py                   ← Trigger notification
✅ asset_tracker/settings.py         ← Email configuration
```

**Steps:**
1. Update notification service
2. Modify email templates
3. Call service from views
4. Configure SMTP settings

---

### 🔟 Fixing Bugs

**Example:** Wrong relationship name

**Files that change:**
```
✅ [File with the bug]               ← Fix the error
✅ Related files using same code     ← Check for same pattern
✅ deployment_package/               ← Update deployment files
```

**Steps:**
1. Identify bug location
2. Fix the issue
3. Search for same pattern elsewhere
4. Test thoroughly
5. Update deployment package

---

## 🎨 Template Changes

### When to modify templates:

| Change | File |
|--------|------|
| Add new page | Create new `[page].html` |
| Modify layout | `base.html` |
| Add navigation link | `base.html` |
| Change form fields | `[form].html` |
| Update table display | `[list].html` |
| Add filters | `[list].html` |
| Change button/link | Any relevant template |

---

## 🎯 View Changes

### When to modify views:

| Change | Method/Class |
|--------|--------------|
| Add new page | Create new view class/function |
| Add filtering | Modify `get_queryset()` |
| Add sorting | Modify `get_queryset()` |
| Pass data to template | Modify `get_context_data()` |
| Handle form submission | Modify `form_valid()` or `post()` |
| Add permissions | Add mixin or decorator |
| Change redirect | Modify `success_url` or return |

---

## 📊 URL Changes

### When to modify urls.py:

| Change | Action |
|--------|--------|
| Add new page | Add `path()` entry |
| Change URL pattern | Modify existing `path()` |
| Add URL parameters | Add `<type:name>` in path |
| Remove page | Remove `path()` entry |

**Example:**
```python
# assets/urls.py
urlpatterns = [
    path('server-controllers/', ServerControllerListView.as_view(), name='server_controller_list'),
    path('server-controllers/<int:pk>/edit/', ServerControllerEditView.as_view(), name='server_controller_edit'),
]
```

---

## 🎨 CSS Changes

### When to modify CSS:

| Change | File | Method |
|--------|------|--------|
| Page-specific style | Template | Inline style or `<style>` block |
| Reusable style | `styles.css` | Add CSS class |
| Component style | `styles.css` | Add to existing section |
| Mobile responsive | `mobile.css` | Add media queries |

---

## 🔧 Service Layer Changes

### When to modify services:

| Change | Service File |
|--------|-------------|
| Asset operations | `asset_service.py` |
| Email notifications | `notification_service.py` |
| Excel exports | `export_service.py` |
| API integrations | Create new service |

---

## 📝 Form Changes

### When to modify forms:

| Change | Location |
|--------|----------|
| Add field | Form class `fields = [...]` |
| Custom validation | Add `clean_[field]()` method |
| Field widget | Set `widgets = {...}` |
| Field labels | Set `labels = {...}` |

---

## 🗂️ Model Changes

### When to modify models:

| Change | Action | Migration? |
|--------|--------|-----------|
| Add field | Add to model class | ✅ Yes |
| Remove field | Remove from model | ✅ Yes |
| Change field type | Modify field | ✅ Yes |
| Add method | Add to model class | ❌ No |
| Add property | Add `@property` | ❌ No |
| Change relationship | Modify FK/M2M | ✅ Yes |

**Important:** Always run migrations after model changes!
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📦 Deployment Package

### Files to copy to deployment_package:

✅ **Always copy these when changed:**
- Any file in `assets/views*.py`
- Any file in `assets/forms/`
- Any file in `assets/services/`
- Any file in `assets/templates/`
- Any file in `assets/static/`

❌ **Don't copy these:**
- `migrations/` (run on server)
- `__pycache__/`
- `.pyc` files
- Database files
- Virtual environment

---

## 🚀 Development Workflow

### Standard workflow for adding a feature:

```
1. Plan the feature
   ├─ Identify affected files
   └─ Design the approach

2. Write the code
   ├─ Models (if needed)
   ├─ Forms (if needed)
   ├─ Views/Services
   ├─ Templates
   └─ URLs

3. Test locally
   ├─ Run development server
   ├─ Test all functionality
   └─ Check for errors

4. Update deployment package
   ├─ Copy changed files
   └─ Update documentation

5. Deploy to server
   ├─ Upload files
   ├─ Run migrations (if needed)
   ├─ Collect static files
   └─ Restart service
```

---

## 🔍 Quick Reference: File Purpose

### Core Application Files

| File | Purpose |
|------|---------|
| `models/[model].py` | Database structure |
| `views.py` | Page logic |
| `views_[feature].py` | Feature-specific logic |
| `urls.py` | URL routing |
| `forms/[model]_forms.py` | Form definitions |
| `services/[service].py` | Business logic |
| `templates/assets/` | HTML pages |
| `static/assets/` | CSS, JS, images |

### Configuration Files

| File | Purpose |
|------|---------|
| `settings.py` | App configuration |
| `urls.py` (root) | Main URL config |
| `middleware.py` | Request/response processing |
| `admin.py` | Admin panel config |

---

## 💡 Tips

### 1. Keep Views Thin
Move logic to services, not in views.

### 2. DRY Principle
Don't repeat code - create reusable functions/classes.

### 3. Template Inheritance
Use `{% extends "base.html" %}` for consistency.

### 4. Naming Conventions
- Views: `[Feature]ListView`, `[Feature]EditView`
- Templates: `[feature]_list.html`, `[feature]_form.html`
- URLs: `[feature]_list`, `[feature]_edit`

### 5. Test After Every Change
Run server and test immediately.

---

## 🎯 Recent Features Example

### Server Controller IP Filter

**Files Changed:**
1. `assets/views_server_controller.py`
   - Modified `get_queryset()` - added IP filter logic
   - Modified `get_context_data()` - added filter variables

2. `assets/templates/assets/server_controller_list.html`
   - Added IP filter input field
   - Added filter notice box
   - Enhanced VM display
   - Adjusted field heights

3. `deployment_package/`
   - Copied both files above
   - Added documentation

**Result:** IP filtering with VM detection working perfectly!

---

## 📚 Summary

When adding/changing features, typically you'll modify:

**Most Common:**
1. Template (HTML) - UI changes
2. View (Python) - Logic changes
3. URL config - Routing

**Sometimes:**
4. Forms - Form fields
5. Services - Business logic
6. CSS - Styling

**Rarely:**
7. Models - Database structure
8. Settings - Configuration
9. Middleware - Request processing

**Always:**
10. Deployment package - Update for server

---

**Last Updated:** September 9, 2026  
**For:** Asset Tracker Django Application
