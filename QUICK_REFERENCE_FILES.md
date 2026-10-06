# Quick Reference - Files That Change

## 🎯 What Are You Doing?

### Adding a New Feature Page
```
✅ assets/views_[feature].py          (create new)
✅ assets/urls.py                      (add routes)
✅ assets/templates/assets/[page].html (create new)
✅ assets/templates/assets/base.html   (add nav link)
```

### Adding a Filter/Search
```
✅ assets/views_[feature].py          (modify queryset)
✅ assets/templates/assets/[page].html (add input)
```

### Changing UI/Display
```
✅ assets/templates/assets/[page].html (HTML)
✅ assets/static/assets/css/styles.css (CSS - optional)
```

### Adding a Form Field
```
✅ assets/forms/[model]_forms.py      (add to fields)
✅ assets/templates/assets/[form].html (add to template)
✅ assets/models/[model].py           (if new field)
✅ Run: python manage.py makemigrations (if model changed)
```

### Adding Business Logic
```
✅ assets/services/[service].py       (add method)
✅ assets/views.py                    (call method)
```

### Fixing a Bug
```
✅ [File with the bug]                (fix it)
✅ Search for similar bugs            (grep)
```

---

## 📂 File Location Quick Guide

### Views (Python Logic)
```
assets/views.py                    ← Main views
assets/views_server_controller.py  ← Server controller views
assets/views_[feature].py          ← Feature-specific views
```

### Templates (HTML)
```
assets/templates/assets/
├── base.html                      ← Layout/navigation
├── asset_list.html                ← Asset listing
├── asset_form.html                ← Asset edit form
├── freed_systems.html             ← Freed systems
├── free_ips.html                  ← Free IP addresses
├── server_controller_list.html    ← Server controllers
├── server_controller_form.html    ← SC edit form
└── server_controller_reassign.html ← SC reassign
```

### Forms
```
assets/forms/
├── asset_forms.py                 ← Asset forms
└── [model]_forms.py               ← Other model forms
```

### Services (Business Logic)
```
assets/services/
├── asset_service.py               ← Asset operations
├── notification_service.py        ← Email notifications
└── export_service.py              ← Excel exports
```

### CSS
```
assets/static/assets/css/
├── styles.css                     ← Main styles
└── mobile.css                     ← Mobile responsive
```

### URLs
```
assets/urls.py                     ← App URL routing
asset_tracker/urls.py              ← Root URL config
```

---

## 🔄 After Making Changes

### Always Update
```
✅ deployment_package/             ← Copy changed files here
```

### If Model Changed
```
✅ python manage.py makemigrations
✅ python manage.py migrate
```

### If Static Files Changed
```
✅ python manage.py collectstatic
```

### If Template Changed
```
✅ Hard refresh browser (Ctrl+F5)
```

---

## 🎨 Recent Changes Log

### IP Filter Feature (Sept 9, 2026)
```
Modified:
  ✅ assets/views_server_controller.py
  ✅ assets/templates/assets/server_controller_list.html
  
Updated:
  ✅ deployment_package/ (both files)
```

### Server Controller Feature (Sept 8, 2026)
```
Created:
  ✅ assets/views_server_controller.py
  ✅ assets/templates/assets/server_controller_list.html
  ✅ assets/templates/assets/server_controller_form.html
  ✅ assets/templates/assets/server_controller_reassign.html
  
Modified:
  ✅ assets/urls.py
  ✅ assets/templates/assets/base.html
  ✅ assets/templates/assets/freed_systems.html
  ✅ assets/static/assets/css/styles.css
```

### Email Toggle Feature
```
Modified:
  ✅ assets/forms/asset_forms.py
  ✅ assets/services/notification_service.py
  ✅ assets/templates/assets/asset_form.html
```

---

## 💡 Pro Tips

1. **Before editing:** Read the file first
2. **After editing:** Test immediately
3. **After testing:** Update deployment_package
4. **Document:** Add to README/docs

---

## 🚨 Common Mistakes

❌ **Forgetting to update deployment_package**
✅ Always copy changed files to deployment_package/

❌ **Not testing after changes**
✅ Test in browser immediately

❌ **Editing wrong file**
✅ Double-check file path before editing

❌ **Forgetting migrations**
✅ Run makemigrations after model changes

---

## 📞 Quick Help

### Server not reloading?
- Check terminal for errors
- Restart: Ctrl+C then `python manage.py runserver`

### Changes not visible?
- Hard refresh: Ctrl+F5
- Clear browser cache

### Template not found?
- Check file name spelling
- Check path in view

### ImportError?
- Check imports at top of file
- Check __init__.py in models/

---

**Created:** September 9, 2026  
**For:** Asset Tracker Development  
**See also:** DEVELOPMENT_GUIDE.md (detailed version)
