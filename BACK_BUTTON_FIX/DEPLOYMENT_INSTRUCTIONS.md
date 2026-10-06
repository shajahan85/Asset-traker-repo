# Back Button / Cancel Button Fix

**Issue:** After searching/filtering and then editing an asset, clicking back/cancel returns to main page instead of the filtered results page

**Fix:** Remember the filtered page URL and redirect back to it after editing

---

## PROBLEM SCENARIO

**Before fix:**
1. Go to Assets page → Apply filters (search "Sankar", team filter, branch filter, etc.)
2. Click Edit on an asset → Make changes → Click Update
3. **Problem:** Redirects to `/assets/` (main page) - loses all filters!
4. Have to apply filters again

**After fix:**
1. Go to Assets page → Apply filters
2. Click Edit → Make changes → Click Update
3. ✅ **Returns to** `/assets/?search=Sankar&team=5&branch=2` (filtered page)
4. All filters preserved!

---

## FILES TO UPLOAD

### File 1: views.py
**Upload to:** `/var/www/asset_tracker/assets/views.py`

### File 2: asset_list.html
**Upload to:** `/var/www/asset_tracker/assets/templates/assets/asset_list.html`

### File 3: asset_form.html
**Upload to:** `/var/www/asset_tracker/assets/templates/assets/asset_form.html`

---

## DEPLOYMENT STEPS

### 1. Backup Current Files

```bash
cd /var/www/asset_tracker/assets/
sudo cp views.py views.py.backup_$(date +%Y%m%d_%H%M%S)

cd /var/www/asset_tracker/assets/templates/assets/
sudo cp asset_list.html asset_list.html.backup_$(date +%Y%m%d_%H%M%S)
sudo cp asset_form.html asset_form.html.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Upload Files

**Using WinSCP/FileZilla:**
- Upload `BACK_BUTTON_FIX\views.py` → `/var/www/asset_tracker/assets/`
- Upload `BACK_BUTTON_FIX\asset_list.html` → `/var/www/asset_tracker/assets/templates/assets/`
- Upload `BACK_BUTTON_FIX\asset_form.html` → `/var/www/asset_tracker/assets/templates/assets/`

**Using scp:**
```powershell
scp "d:\Asset tracker\BACK_BUTTON_FIX\views.py" username@server:/tmp/
scp "d:\Asset tracker\BACK_BUTTON_FIX\asset_list.html" username@server:/tmp/
scp "d:\Asset tracker\BACK_BUTTON_FIX\asset_form.html" username@server:/tmp/
```

Then on server:
```bash
sudo mv /tmp/views.py /var/www/asset_tracker/assets/
sudo mv /tmp/asset_list.html /var/www/asset_tracker/assets/templates/assets/
sudo mv /tmp/asset_form.html /var/www/asset_tracker/assets/templates/assets/

sudo chown www-data:www-data /var/www/asset_tracker/assets/views.py
sudo chown www-data:www-data /var/www/asset_tracker/assets/templates/assets/asset_list.html
sudo chown www-data:www-data /var/www/asset_tracker/assets/templates/assets/asset_form.html

sudo chmod 644 /var/www/asset_tracker/assets/views.py
sudo chmod 644 /var/www/asset_tracker/assets/templates/assets/asset_list.html
sudo chmod 644 /var/www/asset_tracker/assets/templates/assets/asset_form.html
```

### 3. Restart Django

```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

---

## TESTING

### Test 1: With Search Filter
1. Go to Assets page
2. Search for "Sankar" in the search box
3. Click Edit on any asset in the results
4. Make a change → Click Update
5. ✅ **Verify:** Returns to search results for "Sankar"

### Test 2: With Team Filter
1. Go to Assets page
2. Apply Team filter (e.g., select "IT Team")
3. Click Edit on any asset
4. Make a change → Click Update
5. ✅ **Verify:** Returns to filtered page showing only IT Team assets

### Test 3: With Multiple Filters
1. Go to Assets page
2. Apply multiple filters (search + team + branch)
3. Click Edit on any asset
4. Make a change → Click Update
5. ✅ **Verify:** Returns to page with all filters applied

### Test 4: Cancel Button
1. Go to Assets page with filters applied
2. Click Edit on an asset
3. Click Cancel button (without saving)
4. ✅ **Verify:** Returns to filtered page

### Test 5: Browser Back Button
1. Apply filters on Assets page
2. Click Edit on an asset
3. Click browser Back button
4. ✅ **Verify:** Returns to filtered page

---

## CODE CHANGES

### Change 1: asset_list.html (Line 148)
**Before:**
```html
<a href="{% url 'asset_update' asset.pk %}" class="btn btn-sm btn-warning">Edit</a>
```

**After:**
```html
<a href="{% url 'asset_update' asset.pk %}?next={{ request.get_full_path|urlencode }}" class="btn btn-sm btn-warning">Edit</a>
```

**What it does:** Passes the current URL (with filters) to the edit page

---

### Change 2: asset_form.html (Line 127)
**Before:**
```html
<form method="post" enctype="multipart/form-data" novalidate>
    {% csrf_token %}
```

**After:**
```html
<form method="post" enctype="multipart/form-data" novalidate>
    {% csrf_token %}
    {% if request.GET.next %}
    <input type="hidden" name="next" value="{{ request.GET.next }}">
    {% endif %}
```

**What it does:** Adds hidden field to remember where user came from

---

### Change 3: asset_form.html (Line 546)
**Before:**
```html
<a href="{% url 'asset_list' %}" class="btn btn-secondary">Cancel</a>
```

**After:**
```html
<a href="{% if request.GET.next %}{{ request.GET.next }}{% else %}{% url 'asset_list' %}{% endif %}" class="btn btn-secondary">Cancel</a>
```

**What it does:** Cancel button goes back to filtered page

---

### Change 4: views.py (AssetUpdateView.form_valid, Line 574)
**Before:**
```python
return redirect(self.success_url)
```

**After:**
```python
# Redirect back to the page user came from (with filters intact)
next_url = self.request.GET.get('next') or self.request.POST.get('next')
if next_url:
    return redirect(next_url)
return redirect(self.success_url)
```

**What it does:** Redirects to the filtered page after successful save

---

## BENEFITS

✅ **Better UX:** Users don't lose their place when editing assets  
✅ **Saves time:** No need to re-apply filters after every edit  
✅ **Works with search:** Preserves search queries  
✅ **Works with filters:** Preserves team, branch, and other filters  
✅ **Works with Cancel:** Cancel button also goes back correctly  
✅ **Works with browser back:** Browser back button works as expected  

---

## NOTES

- This fix applies to ALL asset edit operations
- Filters are preserved in the URL as query parameters
- If no filters were applied, it goes to the main assets page (normal behavior)
- The "next" parameter is URL-encoded to handle special characters

---

## ROLLBACK

If needed, restore backups:

```bash
cd /var/www/asset_tracker/assets/
sudo cp views.py.backup_* views.py

cd /var/www/asset_tracker/assets/templates/assets/
sudo cp asset_list.html.backup_* asset_list.html
sudo cp asset_form.html.backup_* asset_form.html

sudo systemctl restart asset_tracker
```

---

## TIME REQUIRED

- Upload files: 5 minutes
- Restart Django: 1 minute
- Testing: 3 minutes

**Total: ~10 minutes**

---

**Much better user experience!** 🎯
