# Implementation Plan: Branch Management Completion

## Overview

Complete the partially-implemented Branch Management feature by creating missing templates, updating existing templates to display branch information, and integrating branch filtering into export functionality.

## Tasks

- [ ] 1. Create branch form and delete confirmation templates
  - [x] 1.1 Create branch_form.html template
    - Create file at `assets/templates/assets/branch_form.html`
    - Extend base template with proper page title
    - Add form with CSRF token and BranchForm fields (name, code, is_active)
    - Include field validation error display
    - Add conditional title (Create Branch / Edit Branch based on context)
    - Style form with Bootstrap classes matching existing forms
    - Add Submit and Cancel buttons (Cancel returns to branch list)
    - _Requirements: FR1_
  
  - [-] 1.2 Create branch_confirm_delete.html template
    - Create file at `assets/templates/assets/branch_confirm_delete.html`
    - Extend base template with appropriate page title
    - Display branch name being deleted prominently
    - Show warning message if branch has assets assigned (display count)
    - Add confirmation form with CSRF token
    - Add Confirm Delete and Cancel buttons
    - Style with warning colors for delete action
    - _Requirements: FR1_

- [ ] 2. Update asset list template with branch display and filtering
  - [ ] 2.1 Add branch column to asset table
    - Read current `assets/templates/assets/asset_list.html`
    - Add "Branch" column header to table thead
    - Add branch name display in table rows: `{{ asset.branch.name }}`
    - Ensure column styling matches existing columns
    - _Requirements: FR2_
  
  - [ ] 2.2 Add branch filter to filter form
    - Add branch dropdown to filter form section
    - Populate dropdown with active branches from context
    - Include "All Branches" as default/empty option
    - Set selected value based on current filter parameter
    - _Requirements: FR2_
  
  - [ ] 2.3 Update AssetListView context
    - Modify view to add branches queryset to context
    - Query active branches ordered by name
    - Ensure branches are available in template
    - _Requirements: FR2_

- [ ] 3. Verify and update asset form template
  - [ ] 3.1 Verify branch field in asset_form.html
    - Read current `assets/templates/assets/asset_form.html`
    - Check if branch field is rendered
    - Verify field has required indicator (asterisk)
    - Ensure validation errors display for branch field
    - _Requirements: FR3_
  
  - [ ] 3.2 Add branch field if missing
    - Add branch dropdown with proper styling if not present
    - Use Bootstrap form classes for consistency
    - Show only active branches in dropdown
    - Ensure current branch is pre-selected when editing
    - _Requirements: FR3_

- [ ] 4. Verify AssetService branch handling
  - [ ] 4.1 Check AssetService methods for branch handling
    - Read `assets/services/asset_service.py`
    - Verify `create_asset()` includes branch in saved data
    - Verify `update_asset()` updates branch when changed
    - Check `create_scrapped_asset()` preserves branch from original asset
    - Check `create_freed_asset()` preserves branch from original asset
    - _Requirements: FR4_
  
  - [ ] 4.2 Add branch field to service methods if missing
    - Add branch preservation to scrapped asset creation
    - Add branch preservation to freed asset creation
    - Ensure all methods handle None/missing branch gracefully
    - _Requirements: FR4_

- [ ] 5. Add branch filtering to ExportService
  - [ ] 5.1 Update export_active_assets with branch filtering
    - Read `assets/services/export_service.py`
    - Add branch_id parameter to method signature
    - Filter queryset by branch when branch_id provided
    - Get branch name and add to Excel sheet header at top
    - Use format: "Active Assets - {branch_name}" or "Active Assets - All Branches"
    - Ensure backward compatibility (no branch = all assets)
    - _Requirements: FR5_
  
  - [ ] 5.2 Update export_freed_assets with branch filtering
    - Add branch_id parameter to method signature
    - Apply same filtering logic as active assets
    - Add branch name to Excel header
    - Maintain backward compatibility
    - _Requirements: FR5_
  
  - [ ] 5.3 Update export_scrapped_assets with branch filtering
    - Add branch_id parameter to method signature
    - Apply same filtering logic
    - Add branch name to Excel header
    - Maintain backward compatibility
    - _Requirements: FR5_

- [ ] 6. Update export views with branch parameter handling
  - [ ] 6.1 Update export views to extract branch parameter
    - Read export views in `assets/views.py`
    - Extract branch_id from request.GET in active assets export view
    - Pass branch_id to ExportService.export_active_assets()
    - Update freed assets export view similarly
    - Update scrapped assets export view similarly
    - Handle missing branch parameter gracefully (None = all assets)
    - _Requirements: FR5_

- [ ] 7. Optimize database queries with select_related
  - [ ] 7.1 Add select_related for branch in asset queries
    - Find all Asset querysets in views that display branch
    - Add `.select_related('branch')` to asset list queries
    - Add `.select_related('branch')` to export queries
    - Ensure no N+1 query issues for branch data
    - _Requirements: NFR1_

- [ ] 8. Integration testing and verification
  - [ ] 8.1 Test branch CRUD operations
    - View branch list (verify all 4 branches visible with asset counts)
    - Create new test branch (verify it appears in list)
    - Edit test branch (verify changes saved)
    - Try to delete branch with assets (verify error message)
    - Delete test branch without assets (verify success)
    - _Requirements: FR1, NFR2_
  
  - [ ] 8.2 Test asset-branch integration
    - View asset list (verify branch column shows names)
    - Filter by Kochi (verify all 500 assets shown)
    - Filter by Pune (verify 0 assets initially)
    - Create new asset with Pune branch (verify requires branch)
    - Filter by Pune again (verify 1 asset)
    - Edit asset to change branch from Kochi to Bangalore
    - Verify asset now appears in Bangalore filter
    - _Requirements: FR2, FR3, FR4_
  
  - [ ] 8.3 Test export functionality
    - Export active assets with no branch filter (verify all assets)
    - Export active assets filtered by Kochi (verify 500 assets with branch name in header)
    - Export active assets filtered by Pune (verify 1 asset)
    - Verify Excel headers show branch names correctly
    - Test exports for freed and scrapped assets with branch filter
    - _Requirements: FR5_
  
  - [ ] 8.4 Test edge cases
    - Try creating asset without branch selection (verify validation error)
    - Verify inactive branch not shown in asset form dropdown
    - Verify inactive branch still shown for existing assets
    - Test all filtering combinations (status + category + branch)
    - _Requirements: NFR2, NFR3_

- [ ] 9. Documentation and cleanup
  - [ ] 9.1 Update documentation
    - Update `BRANCH_FEATURE_SUMMARY.md` with completion status
    - Mark all remaining steps as completed
    - Document branch export functionality
    - Add any necessary code comments
    - _Requirements: All_
  
  - [ ] 9.2 Cleanup and final verification
    - Remove any debug print statements
    - Verify all temporary test files removed
    - Restart Django server
    - Final smoke test of all features
    - _Requirements: All_

## Task Dependency Graph

```
1 (Templates) ─┐
               ├─→ 8 (Integration Testing) ─→ 9 (Documentation)
2 (Asset List) ┤
               │
3 (Asset Form) ┤
               │
4 (Services)   ┤
               │
5 (Export Svc) ├─→ 6 (Export Views) ─┘
               │
7 (Queries)    ┘
```

Tasks 1-4 are independent and can run in parallel.
Task 5 must complete before task 6.
Task 7 depends on tasks 2 and 4.
Task 8 requires all previous tasks.
Task 9 requires task 8.
