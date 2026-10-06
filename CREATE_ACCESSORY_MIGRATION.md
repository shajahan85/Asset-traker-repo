# Create Accessory Migration

## Step 1: Create Migration

Run this command to create the migration for the new Accessory model:

```powershell
python manage.py makemigrations assets
```

Expected output:
```
Migrations for 'assets':
  assets\migrations\00XX_accessory.py
    - Create model Accessory
```

## Step 2: Apply Migration

Run this command to apply the migration:

```powershell
python manage.py migrate assets
```

Expected output:
```
Running migrations:
  Applying assets.00XX_accessory... OK
```

## Step 3: Verify

Check that the accessory table was created:

```powershell
python manage.py dbshell
```

Then in SQLite:
```sql
.tables
.schema assets_accessory
.exit
```

Or use Django shell:
```powershell
python manage.py shell
```

```python
from assets.models import Accessory
print(Accessory._meta.db_table)
# Should print: assets_accessory
```

## Summary of Changes

### New Features Added:

1. ✅ **Employee Code Field** - Already existed in Asset model, now visible in forms
2. ✅ **Accessory Model** - New model to track accessories (mouse, keyboard, monitor, etc.)
3. ✅ **Accessory Formset** - Dynamic form to add/remove accessories when creating/editing assets
4. ✅ **Employee Search** - New page to search assets by employee code
5. ✅ **Navigation Link** - Added "Employee Search" to main navigation

### Files Modified:

- `assets/models/accessory.py` - NEW (Accessory model)
- `assets/models/__init__.py` - Updated (import Accessory)
- `assets/forms/asset_forms.py` - Updated (added employee_code field and AccessoryFormSet)
- `assets/views.py` - Updated (handle accessories in create/update, new EmployeeSearchView)
- `assets/urls.py` - Updated (added employee_search URL)
- `assets/templates/assets/asset_form.html` - Updated (added employee_code and accessories section)
- `assets/templates/assets/employee_search.html` - NEW (search page)
- `assets/templates/assets/base.html` - Updated (added navigation link)
- `assets/admin.py` - Updated (registered Accessory model)
- `assets/services/asset_service.py` - Updated (handle employee_code)

### What You Can Do Now:

1. **Add Employee Code** when creating/editing assets
2. **Add Multiple Accessories** to each asset (unlimited)
3. **Search by Employee Code** to see all assets and accessories for an employee
4. **View Full Details** including IP addresses, system info, warranty, and accessories

### Example Use Cases:

**Creating an Asset with Accessories:**
1. Go to Create Asset page
2. Fill in asset details including Employee Code
3. Scroll to "Accessories Provided" section
4. Click "+ Add Accessory" to add items (Mouse, Keyboard, Monitor, etc.)
5. Fill in details for each accessory
6. Click "Create Asset"

**Searching by Employee Code:**
1. Click "Employee Search" in navigation
2. Enter employee code
3. See all assets assigned to that employee
4. View complete details including accessories

**Viewing Asset Details:**
- Each asset card shows:
  - Employee name and code
  - Asset tag and system type
  - Serial number
  - Operating system
  - IP addresses (primary and additional)
  - Team and branch
  - Warranty information
  - All accessories provided

