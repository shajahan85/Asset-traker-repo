# Design: Branch Management Completion

## Architecture Overview

This design completes the Branch Management feature by adding the remaining templates, updating existing templates to display branch information, and integrating branch filtering into the export functionality.

### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         Views Layer                          │
│  - BranchListView (existing)                                │
│  - BranchCreateView (existing)                              │
│  - BranchUpdateView (existing)                              │
│  - BranchDeleteView (existing)                              │
│  - AssetListView (update to show branch)                    │
│  - Export views (update to filter by branch)                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                      Services Layer                          │
│  - AssetService (verify branch handling)                    │
│  - FilterService (already has branch filtering)             │
│  - ExportService (add branch filtering)                     │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                      Models Layer                            │
│  - Branch (existing)                                        │
│  - Asset (existing with branch FK)                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Template Layer

#### 1.1 Branch Form Template (`branch_form.html`)
**Purpose:** Unified template for branch creation and editing

**Structure:**
```html
{% extends "assets/base.html" %}

<form method="post">
  - CSRF token
  - Branch name field
  - Branch code field
  - Active status checkbox
  - Submit/Cancel buttons
</form>
```

**Features:**
- Form validation error display
- Conditional title (Create/Edit)
- Bootstrap styling
- Cancel button returns to branch list

#### 1.2 Branch Delete Confirmation (`branch_confirm_delete.html`)
**Purpose:** Confirm branch deletion with safety check

**Structure:**
```html
{% extends "assets/base.html" %}

<confirmation message>
  - Branch name display
  - Asset count warning (if any)
  - Confirm/Cancel buttons
</confirmation>
```

**Safety Features:**
- Shows number of assets assigned
- Warning message if branch has assets
- Server-side validation in view

#### 1.3 Asset List Template Updates (`asset_list.html`)
**Changes Required:**
1. Add Branch column to table:
   ```html
   <th>Branch</th>
   ...
   <td>{{ asset.branch.name }}</td>
   ```

2. Add branch filter to filter form:
   ```html
   <select name="branch">
     <option value="">All Branches</option>
     {% for branch in branches %}
       <option value="{{ branch.id }}">{{ branch.name }}</option>
     {% endfor %}
   </select>
   ```

3. Update view context to include branches queryset

#### 1.4 Asset Form Template Updates (`asset_form.html`)
**Changes Required:**
1. Ensure branch field is rendered:
   ```html
   <div class="form-group">
     <label>Branch *</label>
     {{ form.branch }}
     {% if form.branch.errors %}
       <div class="error">{{ form.branch.errors }}</div>
     {% endif %}
   </div>
   ```

2. Branch field styling consistent with other fields

### 2. Service Layer Updates

#### 2.1 AssetService Verification
**Methods to Check:**

```python
# create_asset - should already handle branch
def create_asset(form_data):
    asset = Asset(**form_data)
    asset.save()  # branch included in form_data
    return asset

# update_asset - should already handle branch
def update_asset(asset, form_data):
    for key, value in form_data.items():
        setattr(asset, key, value)  # includes branch
    asset.save()
    return asset

# create_scrapped_asset - verify branch is preserved
def create_scrapped_asset(asset, reason):
    scrapped = Asset(
        # ... other fields ...
        branch=asset.branch,  # VERIFY THIS EXISTS
    )
    return scrapped

# create_freed_asset - verify branch is preserved
def create_freed_asset(asset):
    freed = Asset(
        # ... other fields ...
        branch=asset.branch,  # VERIFY THIS EXISTS
    )
    return freed
```

**Action:** Read these methods and add branch field if missing.

#### 2.2 ExportService Updates
**Current State:** Has methods for exporting assets but no branch filtering

**Required Changes:**

```python
def export_active_assets(filters=None, branch_id=None):
    """Export active assets with optional branch filter."""
    queryset = Asset.objects.filter(status='active')
    
    if branch_id:
        queryset = queryset.filter(branch_id=branch_id)
        branch_name = Branch.objects.get(id=branch_id).name
    else:
        branch_name = "All Branches"
    
    # Apply other filters
    if filters:
        queryset = FilterService.apply_filters(queryset, filters)
    
    # Create Excel file
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    
    # Add branch name as header
    worksheet['A1'] = f'Active Assets - {branch_name}'
    worksheet['A1'].font = Font(bold=True, size=14)
    
    # ... rest of export logic ...
```

**Methods to Update:**
1. `export_active_assets()`
2. `export_freed_assets()`
3. `export_scrapped_assets()`

### 3. View Layer Updates

#### 3.1 AssetListView Context
**Add branches to context:**

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['branches'] = Branch.objects.filter(is_active=True).order_by('name')
    return context
```

#### 3.2 Export View Updates
**Add branch parameter handling:**

```python
def export_active_assets(request):
    branch_id = request.GET.get('branch')
    filters = {
        'status': request.GET.get('status'),
        'category': request.GET.get('category'),
        # ... other filters ...
    }
    
    response = ExportService.export_active_assets(filters, branch_id)
    return response
```

## Data Flow

### Asset List with Branch Filter
```
1. User selects branch from dropdown
2. Form submits to AssetListView
3. View passes branch filter to FilterService
4. FilterService applies branch filter to queryset
5. Template renders filtered assets with branch column
```

### Asset Creation with Branch
```
1. User fills asset form with branch selection
2. Form validation ensures branch is selected
3. AssetService.create_asset() saves asset with branch
4. Asset saved to database with branch FK
5. Redirect to asset list showing new asset with branch
```

### Branch-Filtered Export
```
1. User clicks export with branch filter applied
2. Export view extracts branch_id from request
3. ExportService filters assets by branch
4. Excel file generated with branch name in header
5. File downloaded with branch-specific data
```

## Database Schema (No Changes)

The schema is already complete:

```sql
-- Branch table (existing)
CREATE TABLE branch (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Asset table (existing with branch FK)
CREATE TABLE asset (
    id INTEGER PRIMARY KEY,
    -- ... other fields ...
    branch_id INTEGER REFERENCES branch(id) ON DELETE PROTECT
);
```

## Error Handling

### Branch Deletion
- **Error:** Cannot delete branch with assets
- **Action:** Show error message, redirect to branch list
- **Implementation:** Check in BranchDeleteView.delete()

### Asset Without Branch
- **Error:** Asset form submitted without branch
- **Action:** Show validation error "Branch is required"
- **Implementation:** Form validation in AssetForm

### Invalid Branch Filter
- **Error:** Branch ID doesn't exist
- **Action:** Ignore filter, show all assets
- **Implementation:** Try/except in FilterService

## Testing Strategy

### Unit Tests
1. AssetService methods preserve branch correctly
2. FilterService filters by branch
3. ExportService includes branch in exports

### Integration Tests
1. Create asset with branch → verify saved
2. Update asset branch → verify updated
3. Filter by branch → verify correct results
4. Export with branch filter → verify Excel content

### Manual Tests
1. Navigate to Branches page → see all branches
2. Create new branch → appears in list
3. Edit branch → changes saved
4. Try to delete branch with assets → see error
5. Filter assets by branch → see filtered results
6. Export assets by branch → Excel has branch name
7. View asset list → see branch column
8. Create asset → must select branch
9. Edit asset → can change branch

## Security Considerations

- Branch creation/edit/delete restricted to admin users (AdminRequiredMixin)
- All users can view branches and filter by branch
- Branch field required on asset creation (data integrity)
- Cannot delete branch with assets (referential integrity)

## Performance Considerations

- Use `select_related('branch')` on asset queries to avoid N+1
- Branch filter uses indexed foreign key
- Export queries should prefetch branch data
- Branch dropdown cached for filter form

## Rollback Plan

If issues occur:
1. All changes are in templates and services (no DB changes)
2. Can revert template changes without affecting data
3. Existing assets already have Kochi branch assigned
4. No migration to rollback

## File Modifications Summary

### New Files
- `assets/templates/assets/branch_form.html`
- `assets/templates/assets/branch_confirm_delete.html`

### Modified Files
- `assets/templates/assets/asset_list.html` (add branch column and filter)
- `assets/templates/assets/asset_form.html` (verify branch field shown)
- `assets/services/export_service.py` (add branch filtering)
- `assets/services/asset_service.py` (verify branch handling)
- `assets/views.py` (add branches to context, handle branch in exports)

### No Changes Required
- `assets/models.py` (already complete)
- `assets/forms/branch_form.py` (already complete)
- `assets/forms/asset_forms.py` (already includes branch)
- `assets/views_branch.py` (already complete)
- `assets/services/filter_service.py` (already has branch filtering)
