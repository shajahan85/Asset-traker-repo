# Server Controller Machines - FINAL SPECIFICATION

## ✅ Approved & Ready for Implementation

---

## 📋 CONFIRMED REQUIREMENTS

### 1. ✅ IP Range Identification
**IP Range:** `192.168.50.0` to `192.168.50.255` (192.168.50.x)
**Method:** Dynamic filtering - no static database field
**Checks:** Primary IP, additional IPs, and manual_ip field

### 2. ✅ Page Structure
**Type:** Tabbed interface (single page)
**URL:** `/assets/server-controllers/`
**Tabs:**
- Active Tab - Shows active server controllers
- Freed Tab - Shows freed server controllers

### 3. ✅ Visual Identification
**Method:** Yellow round badge with "SC" text
**Badge Specs:**
- Shape: Circle (border-radius: 50%)
- Color: Yellow (#ffc107)
- Text: "SC" in bold black
- Size: 24px × 24px
- Position: Before system type name

### 4. ✅ Editable Fields (Complete List)

**Basic Information:**
- Asset Tag
- System Name
- IP Address (must be 192.168.50.x)
- System Type

**Organization:**
- Team
- Branch

**System Details:**
- Operating System
- Hardware Serial ⭐ REQUIRED

**Hyper-V VMs:**
- VM Names (multiple)
- VM IP Addresses (multiple)

**Assets & Warranty:**
- Accessories ⭐ REQUIRED
- Purchase Date ⭐ REQUIRED
- Warranty ⭐ REQUIRED

**Additional:**
- Notes/Description

**NOT Editable:**
- ❌ Assigned To / User (removed)
- ❌ Employee Code (removed)

### 5. ✅ Freed Systems Display
**Special Highlighting:** YES - Yellow "SC" badge
**Additional Columns:** NO - Use standard columns
**Badge Location:** Before system type in Free Systems page

### 6. ✅ Navigation Placement
**Location:** Between "Network Devices" and "Testing Devices"
**Permissions:** Staff only (`user.is_staff`)
**Menu Section:** Staff Only area

### 7. ✅ Permissions
**Access Level:** Staff only
**Permission Required:** `user.is_staff = True`

### 8. ✅ Dynamic IP-Based Filtering
**Key Rule:** System appears in Server Controllers ONLY when IP is in 192.168.50.x range

**When IP changes TO 50.x range:**
- System automatically ADDED to Server Controllers list
- Yellow SC badge appears

**When IP changes FROM 50.x range:**
- System automatically REMOVED from Server Controllers list
- Yellow SC badge disappears
- Warning shown during edit

### 9. ✅ Reassign Workflow
**Flow:**
1. Click "Reassign" button on freed server controller
2. Form with: Assigned To, Team, Notes
3. Status changes to 'active'
4. Removed from: Free Server Controllers + Free Systems
5. Added to: Active Server Controllers (if still 50.x IP)

**Requirements:** All fields required
**Confirmation:** Yes - standard Django form confirmation
**Notifications:** No email (use existing notification system)

### 10. ✅ Scrap Workflow
**Flow:**
1. Click "Scrap" button on freed server controller
2. Confirmation dialog
3. Status changes to 'scrapped'
4. Removed from: Free Server Controllers + Free Systems
5. Added to: Scrapped Items

**Reason Required:** No - optional
**Notifications:** No email

### 11. ✅ Additional Features
**Included:**
- ✅ Export to Excel (for active list)
- ✅ Basic filters (by team, branch)
- ✅ Search functionality (by asset tag, system name)

**Not Included (future enhancement):**
- ⬜ Bulk actions
- ⬜ Power status indicator
- ⬜ Quick VM view modal

---

## 🏗️ TECHNICAL ARCHITECTURE

### Models
**No new models** - Use existing `Asset` model

**Helper Method to Add:**
```python
class Asset(models.Model):
    # ... existing fields ...
    
    def is_server_controller(self):
        """Check if this asset is a server controller (192.168.50.x)"""
        ip = self.get_primary_ip()
        if ip and ip.startswith('192.168.50.'):
            return True
        if self.manual_ip and self.manual_ip.startswith('192.168.50.'):
            return True
        return False
    
    def get_primary_ip(self):
        """Get primary IP address as string"""
        if self.ip_address:
            return self.ip_address.address
        return self.manual_ip or ''
```

### Views to Create

1. **ServerControllerListView** (`/server-controllers/`)
   - Shows both active and freed (tabbed)
   - Filter by IP range: 192.168.50.x
   - Staff only

2. **ServerControllerEditView** (`/server-controllers/<pk>/edit/`)
   - Custom form with all required fields
   - IP validation (must be 192.168.50.x or warn)
   - Hyper-V VM management

3. **ServerControllerFreeView** (`/server-controllers/<pk>/free/`)
   - Mark as freed
   - Redirect to freed tab

4. **ServerControllerReassignView** (`/server-controllers/<pk>/reassign/`)
   - Reassign freed server controller
   - Remove from both free locations

5. **ServerControllerScrapView** (`/server-controllers/<pk>/scrap/`)
   - Mark as scrapped
   - Remove from both free locations

### Forms to Create

1. **ServerControllerForm**
   - All editable fields
   - IP validation with warning
   - Hyper-V VM inline formset

2. **ServerControllerFilterForm**
   - Filter by team
   - Filter by branch
   - Search by asset tag/name

### Templates to Create

1. **server_controller_list.html**
   - Tabbed interface (Active/Freed)
   - Table with all columns
   - Export button, filters

2. **server_controller_form.html**
   - Edit form layout
   - VM management section
   - Warning for IP changes

### URL Patterns

```python
# Server Controllers
path('server-controllers/', ServerControllerListView.as_view(), name='server_controller_list'),
path('server-controllers/<int:pk>/edit/', ServerControllerEditView.as_view(), name='server_controller_edit'),
path('server-controllers/<int:pk>/free/', ServerControllerFreeView.as_view(), name='server_controller_free'),
path('server-controllers/<int:pk>/reassign/', ServerControllerReassignView.as_view(), name='server_controller_reassign'),
path('server-controllers/<int:pk>/scrap/', ServerControllerScrapView.as_view(), name='server_controller_scrap'),
path('server-controllers/export/', server_controller_export, name='server_controller_export'),
```

### Navigation Bar Update

```html
<!-- In assets/templates/assets/base.html -->
{% if user.is_staff %}
<li><a href="{% url 'hyperv_vm_list' %}">Virtual Machines</a></li>
<li><a href="{% url 'network_device_list' %}">Network Devices</a></li>
<li><a href="{% url 'server_controller_list' %}">Server Controllers</a></li>  <!-- NEW -->
<li><a href="{% url 'testing_device_list' %}">Testing Devices</a></li>
<li><a href="{% url 'operating_systems' %}">Operating Systems</a></li>
<li><a href="{% url 'asset_import' %}">Import Assets</a></li>
{% endif %}
```

### CSS Updates

```css
/* Yellow SC Badge */
.badge-sc {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background-color: #ffc107;
    color: #000;
    font-weight: bold;
    font-size: 0.7rem;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

/* IP Change Warning */
.ip-change-warning {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}
```

---

## 📊 DATA FLOW

### Freeing a Server Controller
```
Active SC (192.168.50.x, status='active')
    ↓ [Free button]
Status = 'freed'
    ↓
Appears in 2 places:
    1. Freed tab in Server Controllers page
    2. Free Systems page (with yellow SC badge)
```

### Reassigning
```
Freed SC
    ↓ [Reassign button]
Form: Assign to user/team
    ↓
Status = 'active'
    ↓
Removed from:
    - Freed Server Controllers tab
    - Free Systems page
    ↓
IF IP still 192.168.50.x:
    Added to Active Server Controllers tab
ELSE:
    Just added to regular Active Assets
```

### Scrapping
```
Freed SC
    ↓ [Scrap button]
Confirmation
    ↓
Status = 'scrapped'
    ↓
Removed from:
    - Freed Server Controllers tab
    - Free Systems page
    ↓
Added to:
    - Scrapped Items page
```

### IP Change
```
Edit Server Controller
    ↓
Change IP from 192.168.50.8 to 192.168.10.5
    ↓
Warning shown: "Will be removed from Server Controllers"
    ↓
User confirms
    ↓
Save
    ↓
No longer appears in Server Controllers
SC badge disappears everywhere
```

---

## ✅ ACCEPTANCE CRITERIA

1. ✅ "Server Controllers" link visible in navbar (staff only)
2. ✅ Server Controllers page shows all 192.168.50.x systems
3. ✅ Two tabs: Active and Freed
4. ✅ Edit button works with all required fields
5. ✅ IP validation: warns if changing outside 50.x range
6. ✅ Free button marks system as freed
7. ✅ Freed SCs appear in both freed tab AND Free Systems page
8. ✅ Yellow SC badge visible in Free Systems page
9. ✅ Reassign removes from both free locations
10. ✅ Scrap removes from both free locations
11. ✅ Export to Excel works
12. ✅ Filters work (team, branch, search)
13. ✅ Dynamic filtering: IP change auto-updates lists
14. ✅ Hyper-V VM management in edit form

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Core Structure (30 min)
- ✅ Create helper method `is_server_controller()`
- ✅ Create URL patterns
- ✅ Create basic ServerControllerListView
- ✅ Create server_controller_list.html template
- ✅ Add navigation link

### Phase 2: List Display (30 min)
- ✅ Implement tabbed interface (Active/Freed)
- ✅ Display table with all columns
- ✅ Add filters and search
- ✅ Add yellow SC badge

### Phase 3: Edit Functionality (45 min)
- ✅ Create ServerControllerForm
- ✅ Create ServerControllerEditView
- ✅ Create server_controller_form.html
- ✅ Add IP validation with warning
- ✅ Add Hyper-V VM management

### Phase 4: Free/Reassign/Scrap (30 min)
- ✅ Implement Free action
- ✅ Implement Reassign action
- ✅ Implement Scrap action
- ✅ Update freed_systems.html to show SC badge

### Phase 5: Export & Polish (30 min)
- ✅ Implement Export to Excel
- ✅ Add CSS for badge
- ✅ Test all workflows
- ✅ Add help text and tooltips

### Phase 6: Testing (30 min)
- ✅ Test IP range filtering
- ✅ Test Free → Reassign workflow
- ✅ Test Free → Scrap workflow
- ✅ Test IP change behavior
- ✅ Test dual-location display
- ✅ Test permissions (staff only)

**Total Estimated Time: 3 hours**

---

## 📁 FILES TO CREATE/MODIFY

### New Files (3):
1. `assets/views/server_controller_views.py` - All SC views
2. `assets/templates/assets/server_controller_list.html` - Main list page
3. `assets/templates/assets/server_controller_form.html` - Edit form

### Modified Files (6):
1. `assets/models.py` - Add helper method
2. `assets/urls.py` - Add URL patterns
3. `assets/templates/assets/base.html` - Add navigation link
4. `assets/templates/assets/freed_systems.html` - Add SC badge
5. `assets/static/assets/css/styles.css` - Add badge CSS
6. `assets/forms/asset_forms.py` - Create ServerControllerForm

---

## 🎯 SUCCESS METRICS

- **Visibility:** Staff can easily find and manage server controllers
- **Accuracy:** Dynamic IP filtering ensures accurate categorization
- **Efficiency:** Edit form has all needed fields
- **Workflow:** Free/Reassign/Scrap work seamlessly
- **Identification:** Yellow SC badge makes SCs instantly recognizable

---

**Status:** ✅ Specification Complete & Approved  
**Ready for:** Implementation  
**Start Date:** December 2024  
**Estimated Completion:** 3 hours  

---

## 🚦 READY TO BUILD! 🚀
