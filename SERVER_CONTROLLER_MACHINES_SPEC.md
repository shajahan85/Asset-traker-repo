# Server Controller Machines - Feature Specification

## 📋 Overview

Create a dedicated management system for **Server Controller Machines** - systems with IP addresses in the **192.168.50.x** range.

---

## 🎯 Requirements

### 1. Server Controller Machines Page
**URL:** `/assets/server-controllers/`

**Features:**
- List all active systems with IP in **192.168.50.x** range
- Show columns:
  - Serial Number
  - Asset Tag
  - System Name
  - IP Address (192.168.50.x)
  - Assigned To
  - Hyper-V VMs (if any)
  - VM IP Addresses
  - Actions (Edit, Free)

### 2. Edit Functionality
- Edit **all** system details
- Edit IP address (must remain in 192.168.50.x range)
- Edit system name
- Edit associated Hyper-V machines
- Edit Hyper-V VM IP addresses

### 3. Free Functionality
When a server controller is freed:
- Status changes to `freed`
- System appears in **2 places:**
  1. **Free Server Controller Machines** (inside Server Controller page)
  2. **Free Systems** (existing page)
- System type labeled as: **"Server Controller Machine"**

### 4. Free Server Controller Machines Section
**Location:** Inside Server Controller Machines page (tabbed or separate section)

**Features:**
- List all freed server controllers (192.168.50.x range + status=freed)
- Same columns as active list
- Actions:
  - **Reassign** - Remove from both free pages
  - **Scrap** - Remove from both free pages
  - **View History**

### 5. Workflow Rules

#### Reassign:
1. User clicks "Reassign" on a freed server controller
2. Assign to new user/team
3. Status changes to `active`
4. **Removed from:**
   - Free Server Controller Machines list
   - Free Systems page
5. **Appears in:**
   - Active Server Controller Machines list

#### Scrap:
1. User clicks "Scrap" on a freed server controller
2. Status changes to `scrapped`
3. **Removed from:**
   - Free Server Controller Machines list
   - Free Systems page
4. **Appears in:**
   - Scrapped Items page

---

## 🏗️ Technical Implementation

### Database Changes
**No new models needed** - use existing `Asset` model

**Identification:**
- Filter by IP address range: `192.168.50.0` to `192.168.50.255`
- OR by manual_ip starting with `192.168.50.`

### New System Type
Add to choices or use existing: `"Server Controller"`

### Views to Create

1. **ServerControllerListView**
   - URL: `/assets/server-controllers/`
   - Shows active server controllers (status='active')

2. **ServerControllerEditView**
   - URL: `/assets/server-controllers/<pk>/edit/`
   - Custom form for server controller editing

3. **ServerControllerFreeView**
   - URL: `/assets/server-controllers/<pk>/free/`
   - Mark as freed

4. **FreedServerControllerListView**
   - URL: `/assets/server-controllers/freed/`
   - Shows freed server controllers (status='freed')
   - OR as section in main page

5. **ServerControllerReassignView**
   - URL: `/assets/server-controllers/<pk>/reassign/`
   - Reassign freed server controller

### Templates to Create

1. `server_controller_list.html`
   - Active server controllers list
   - Tab/section for freed server controllers

2. `server_controller_form.html`
   - Edit form with all fields
   - Hyper-V VM management

3. `freed_server_controllers.html`
   - OR section in main template
   - List of freed server controllers

### URL Patterns

```python
urlpatterns = [
    # Active server controllers
    path('server-controllers/', ServerControllerListView.as_view(), name='server_controller_list'),
    
    # Edit
    path('server-controllers/<int:pk>/edit/', ServerControllerEditView.as_view(), name='server_controller_edit'),
    
    # Free
    path('server-controllers/<int:pk>/free/', ServerControllerFreeView.as_view(), name='server_controller_free'),
    
    # Freed list (optional separate page)
    path('server-controllers/freed/', FreedServerControllerListView.as_view(), name='freed_server_controller_list'),
    
    # Reassign
    path('server-controllers/<int:pk>/reassign/', ServerControllerReassignView.as_view(), name='server_controller_reassign'),
]
```

### Navigation Bar
Add link: **"Server Controllers"** between existing menu items

---

## 📊 Data Flow

### Freeing a Server Controller:
```
Active Server Controller (192.168.50.x)
    ↓ [Free button clicked]
Status = 'freed'
    ↓
Appears in 2 places:
    1. Free Server Controller Machines
    2. Free Systems (existing page)
```

### Reassigning:
```
Freed Server Controller
    ↓ [Reassign button clicked]
Reassignment form → Assign to user/team
    ↓
Status = 'active'
    ↓
Removed from:
    - Free Server Controller Machines
    - Free Systems
    ↓
Added to:
    - Active Server Controller Machines
```

### Scrapping:
```
Freed Server Controller
    ↓ [Scrap button clicked]
Status = 'scrapped'
    ↓
Removed from:
    - Free Server Controller Machines
    - Free Systems
    ↓
Added to:
    - Scrapped Items
```

---

## 🎨 UI/UX Design

### Server Controller Machines Page Layout:

```
┌────────────────────────────────────────────────────────┐
│ Server Controller Machines                             │
│                                                        │
│ [Active] [Freed]  ← Tabs                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Active Server Controllers (192.168.50.x)               │
│                                                        │
│ ┌──────────────────────────────────────────────────┐   │
│ │ # │ Tag │ Name │ IP │ Assigned To │ VMs │ Actions│   │
│ ├──────────────────────────────────────────────────┤   │
│ │ 1 │ SC01│ SVR1 │50.5│ John Doe │ VM1,VM2│Edit│Free│   │
│ │ 2 │ SC02│ SVR2 │50.6│ Jane Doe │    -   │Edit│Free│   │
│ └──────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘

Click [Freed] tab:

┌────────────────────────────────────────────────────────┐
│ Server Controller Machines                             │
│                                                        │
│ [Active] [Freed]  ← Tabs                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Freed Server Controllers (192.168.50.x)                │
│                                                        │
│ ┌──────────────────────────────────────────────────┐   │
│ │ # │ Tag │ IP │ Freed Date │ Actions              │   │
│ ├──────────────────────────────────────────────────┤   │
│ │ 1 │ SC05│50.9│ 2024-12-01│Reassign│Scrap│History│   │
│ │ 2 │ SC08│50.3│ 2024-12-05│Reassign│Scrap│History│   │
│ └──────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

---

## ✅ Acceptance Criteria

1. ✅ New "Server Controllers" link in navigation bar
2. ✅ Server Controller Machines page shows all 192.168.50.x systems
3. ✅ Edit button opens form to edit all details including IP and VMs
4. ✅ Free button marks system as freed
5. ✅ Freed server controllers appear in both:
   - Free Server Controller Machines section/page
   - Existing Free Systems page
6. ✅ Freed systems labeled as "Server Controller Machine"
7. ✅ Reassign removes from both free locations
8. ✅ Scrap removes from both free locations
9. ✅ All standard options available (Reassign, Scrap, History)

---

## 🔧 Implementation Steps

### Phase 1: Basic Pages
1. Create ServerControllerListView (active systems)
2. Add navigation link
3. Create basic template with table

### Phase 2: Edit Functionality
1. Create ServerControllerEditView
2. Create form with all fields
3. Add IP validation (must be 192.168.50.x)

### Phase 3: Free Functionality
1. Create ServerControllerFreeView
2. Update Free Systems page to show server controllers
3. Add system type identification

### Phase 4: Freed List
1. Add "Freed" tab/section to main page
2. Show freed server controllers
3. Add Reassign and Scrap actions

### Phase 5: Reassign/Scrap
1. Implement reassign functionality
2. Implement scrap functionality
3. Ensure removal from both locations

### Phase 6: Testing
1. Test IP range filtering
2. Test free → reassign workflow
3. Test free → scrap workflow
4. Test dual-location display

---

## 📦 Files to Create/Modify

### New Files:
- `assets/views/server_controller_views.py`
- `assets/templates/assets/server_controller_list.html`
- `assets/templates/assets/server_controller_form.html`
- `assets/templates/assets/freed_server_controllers.html` (optional)

### Modified Files:
- `assets/urls.py` - Add new URL patterns
- `assets/templates/assets/base.html` - Add navigation link
- `assets/templates/assets/freed_systems.html` - Show server controllers
- `assets/views.py` - Update FreedSystemsView to include server controllers

---

## 🚀 Estimated Effort

- **Basic Implementation:** 4-6 hours
- **Testing & Refinement:** 2-3 hours
- **Total:** 6-9 hours

---

## 📝 Notes

- IP range check: `192.168.50.0` to `192.168.50.255`
- Use existing Asset model, no migrations needed
- Reuse existing reassign/scrap logic where possible
- Consider adding system_type field for better categorization

---

**Status:** 📋 Specification Complete - Ready for Implementation  
**Priority:** Medium  
**Complexity:** Medium-High
