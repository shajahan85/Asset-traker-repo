# Implementation Plan: Asset History Tracking

## Overview

This implementation plan breaks down the Asset History Tracking feature into discrete, sequential coding tasks. The feature adds comprehensive audit trail capabilities to the Django Asset Tracker, automatically recording all asset changes throughout their lifecycle. Implementation follows a layered approach: database schema → service layer → integration hooks → views/templates → testing.

## Tasks

- [x] 1. Create AssetHistory model and database migration
  - Create `AssetHistory` model in `assets/models.py` with fields: id, asset (FK), event_type, timestamp, user, changes (JSONField), notes
  - Define EVENT_TYPE_CHOICES: created, updated, freed, scrapped, reassigned, health_status_updated
  - Add Meta class with ordering by `-timestamp` and verbose names
  - Create composite indexes: (asset, -timestamp), (event_type, -timestamp), (user, -timestamp)
  - Add `history_entries` related_name to asset ForeignKey
  - Implement `__str__` method and `get_formatted_changes()` method
  - Generate and apply Django migration
  - _Requirements: 1.1, 1.2, 1.3, 7.1, 7.2, 7.3, 7.4, 7.5, 11.3, 11.4_

- [x] 2. Implement HistoryService business logic
  - [x] 2.1 Create HistoryService class with field tracking configuration
    - Create `assets/services/history_service.py` file
    - Define TRACKED_FIELDS list with all asset fields to monitor
    - Define FIELD_LABELS dictionary for human-readable field names
    - Implement `_get_field_value()` helper to extract field values (handle ForeignKeys)
    - _Requirements: 1.6, 2.6, 6.2_

  - [ ]* 2.2 Write property test for field value extraction
    - **Property 1: Creation Event Recording**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6**

  - [x] 2.3 Implement history recording methods
    - Implement `record_creation()` method to capture initial asset values
    - Implement `record_update()` method to compare old/new values and record changes
    - Implement `record_status_change()` method for freed/scrapped/reassigned events
    - Implement `record_health_status_update()` method for freed asset health changes
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 2.4 Write property tests for history recording methods
    - **Property 2: Field Update Recording**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
    - **Property 3: Status Transition Recording**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9**
    - **Property 4: Health Status Change Recording**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**

  - [x] 2.5 Implement history query and filtering methods
    - Implement `get_asset_history()` method with filter support (event_type, user, date_from, date_to)
    - Apply filters to queryset and return ordered results
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 11.2_

  - [ ]* 2.6 Write property test for history filtering
    - **Property 9: History Filtering**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

  - [x] 2.7 Implement display formatting methods
    - Implement `format_changes_for_display()` to convert changes JSON to human-readable format
    - Implement `_format_value_for_display()` helper for field-specific formatting (dates, FKs, nulls)
    - Handle special cases: IP addresses, foreign keys, dates, null values
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 2.8 Write property test for display formatting
    - **Property 6: Human-Readable Formatting**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**

  - [x] 2.9 Implement CSV export functionality
    - Implement `export_history_to_csv()` method
    - Create CSV with columns: Timestamp, Event Type, User, Field, Previous Value, New Value, Notes
    - Implement `_format_value_for_export()` helper for CSV-safe formatting
    - Generate filename with asset_tag and timestamp
    - Apply filters if provided
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 2.10 Write property test for CSV export
    - **Property 10: CSV Export Accuracy**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

- [x] 3. Checkpoint - Verify HistoryService implementation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Integrate history recording into AssetService
  - [ ] 4.1 Add history recording to create_asset method
    - Import HistoryService in `assets/services/asset_service.py`
    - Call `HistoryService.record_creation()` after asset creation within transaction
    - Pass asset and user to recording method
    - _Requirements: 1.1, 1.4, 1.5, 1.6_

  - [ ] 4.2 Add history recording to update_asset method
    - Capture old field values before applying updates
    - Store old values in dictionary using `HistoryService._get_field_value()`
    - Call `HistoryService.record_update()` after save within transaction
    - Pass asset, old_values dict, and user to recording method
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 4.3 Add history recording to free_asset method
    - Call `HistoryService.record_status_change()` with event_type='freed' after status change
    - Pass asset, event_type, user, and notes (if applicable)
    - _Requirements: 3.1, 3.4, 3.5, 3.6, 3.7_

  - [ ] 4.4 Add history recording to scrap_asset method
    - Call `HistoryService.record_status_change()` with event_type='scrapped' after status change
    - Pass scrapping_reason as notes parameter
    - _Requirements: 3.2, 3.4, 3.5, 3.6, 3.8_

  - [ ] 4.5 Add history recording to reassign_asset method
    - Call `HistoryService.record_status_change()` with event_type='reassigned' after reassignment
    - Pass asset, event_type, user, and notes (if applicable)
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.9_

  - [ ] 4.6 Add history recording to update_freed_asset method
    - Capture old health_status value before update
    - Call `HistoryService.record_health_status_update()` after save
    - Pass asset, old_health_status, and user
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 4.7 Add history recording to create_freed_asset method
    - Call `HistoryService.record_creation()` after freed asset creation
    - Ensure event_type reflects 'created' with status 'freed'
    - _Requirements: 1.2, 1.4, 1.5, 1.6_

  - [ ] 4.8 Add history recording to create_scrapped_asset method
    - Call `HistoryService.record_creation()` after scrapped asset creation
    - Ensure event_type reflects 'created' with status 'scrapped'
    - _Requirements: 1.3, 1.4, 1.5, 1.6_

  - [ ]* 4.9 Write integration tests for AssetService history recording
    - Test that each AssetService method creates appropriate history entries
    - Verify history entries contain correct event_type, user, timestamp, and changes
    - Test transaction rollback behavior (failed operation should not create history)
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 3.2, 3.3, 4.1, 7.5_

- [ ] 5. Checkpoint - Verify AssetService integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Create AssetHistoryView for timeline display
  - [ ] 6.1 Implement AssetHistoryView class-based view
    - Create view in `assets/views.py` extending LoginRequiredMixin and ListView
    - Set model=AssetHistory, template_name='assets/asset_history.html', paginate_by=50
    - Implement `get_queryset()` to fetch asset and apply filters from request.GET
    - Implement `get_context_data()` to add asset, event_types, and active filters to context
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 9.1, 9.2, 9.3, 9.4, 9.5, 11.1, 11.2_

  - [ ]* 6.2 Write unit tests for AssetHistoryView
    - Test view requires authentication
    - Test queryset filtering by event_type, user, date_from, date_to
    - Test pagination with more than 50 entries
    - Test context data includes asset and filters
    - _Requirements: 5.1, 5.2, 9.1, 9.2, 9.3, 9.4, 11.2_

  - [ ] 6.3 Implement AssetHistoryExportView for CSV export
    - Create view in `assets/views.py` extending LoginRequiredMixin and View
    - Implement `get()` method to fetch asset and filters from request.GET
    - Call `HistoryService.export_history_to_csv()` and return response
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ]* 6.4 Write unit tests for AssetHistoryExportView
    - Test view requires authentication
    - Test CSV generation with and without filters
    - Test CSV filename format
    - Test CSV content structure and headers
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 7. Create URL routes for history views
  - Add URL pattern for AssetHistoryView: `path('asset/<int:pk>/history/', AssetHistoryView.as_view(), name='asset_history')`
  - Add URL pattern for AssetHistoryExportView: `path('asset/<int:pk>/history/export/', AssetHistoryExportView.as_view(), name='asset_history_export')`
  - Update `assets/urls.py` with new patterns
  - _Requirements: 5.1, 10.1, 13.1, 13.2, 13.3, 13.4, 13.5_

- [ ] 8. Create asset_history.html template
  - [ ] 8.1 Create base template structure with asset information header
    - Create `assets/templates/assets/asset_history.html`
    - Extend base template and add asset details section (asset_tag, system_type, status)
    - Add "View History" heading and back button to asset detail
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 8.2 Implement filter form section
    - Add filter form with fields: event_type (dropdown), user (text), date_from (date), date_to (date)
    - Add "Apply Filters" and "Clear Filters" buttons
    - Pre-populate form with active filter values from context
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 8.3 Implement history timeline display
    - Create timeline layout with entries in reverse chronological order
    - For each entry, display: event_type badge, timestamp, username
    - Display formatted changes using `entry.get_formatted_changes()`
    - Show field name, old value → new value for each change
    - Add notes display if present
    - Handle empty history with "No history entries found" message
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ] 8.4 Add pagination controls
    - Add Django pagination controls at bottom of timeline
    - Display page numbers and previous/next links
    - Preserve filter parameters in pagination links
    - _Requirements: 11.2_

  - [ ] 8.5 Add export button
    - Add "Export History" button linking to asset_history_export URL
    - Pass current filter parameters to export URL
    - _Requirements: 10.1_

  - [ ]* 8.6 Write template rendering tests
    - Test template renders with history entries
    - Test template renders with empty history
    - Test filter form displays correctly
    - Test pagination controls appear when needed
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 11.2_

- [ ] 9. Add history access links to existing templates
  - [ ] 9.1 Update asset_detail.html template
    - Add "View History" button in prominent location (near edit/delete buttons)
    - Link to asset_history URL with asset.pk parameter
    - _Requirements: 5.1, 13.1_

  - [ ] 9.2 Update asset_list.html template
    - Add history icon/link column to active assets table
    - Link to asset_history URL for each asset row
    - _Requirements: 13.2_

  - [ ] 9.3 Update freed_list.html template
    - Add history icon/link column to freed assets table
    - Link to asset_history URL for each asset row
    - _Requirements: 13.3_

  - [ ] 9.4 Update scrapped_list.html template
    - Add history icon/link column to scrapped assets table
    - Link to asset_history URL for each asset row
    - _Requirements: 13.4_

- [ ] 10. Checkpoint - Verify views and templates
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Add user attribution and immutability safeguards
  - [ ] 11.1 Verify user attribution in all history recording calls
    - Review all HistoryService recording calls to ensure user.username is passed
    - Add user parameter validation in HistoryService methods
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 11.2 Write property test for user attribution
    - **Property 8: User Attribution Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**

  - [ ] 11.3 Implement immutability constraints
    - Verify AssetHistory model has no update/delete methods exposed in admin
    - Add model-level permissions to prevent modifications
    - Document that history entries should only be created, never updated or deleted
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 11.4 Write property test for immutability
    - **Property 7: History Immutability**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 12. Implement IP address change tracking
  - [ ] 12.1 Enhance HistoryService to handle IP address formatting
    - Update `_get_field_value()` to extract IP address values correctly
    - Update `_format_value_for_display()` to show "IP: [address]" or "Manual IP: [address]"
    - Handle transitions between managed IP, manual IP, and no IP
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ]* 12.2 Write property test for IP address tracking
    - **Property 12: IP Address Change Tracking**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

- [ ] 13. Performance optimization and indexing verification
  - [ ] 13.1 Verify database indexes are created
    - Run migration and check database for composite indexes
    - Verify indexes on (asset, -timestamp), (event_type, -timestamp), (user, -timestamp)
    - _Requirements: 11.3, 11.4_

  - [ ] 13.2 Optimize history queries with select_related
    - Update AssetHistoryView queryset to use select_related('asset')
    - Verify single query execution for history list with asset data
    - _Requirements: 11.5_

  - [ ]* 13.3 Write property test for query performance
    - **Property 11: Query Performance**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**

- [ ] 14. Add comprehensive unit tests for edge cases
  - [ ]* 14.1 Write unit tests for history recording edge cases
    - Test history recording with empty changes (no fields modified)
    - Test history recording with null/empty field values
    - Test history recording with very long text fields
    - Test history recording with special characters in field values
    - Test transaction rollback when history recording fails
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 7.5_

  - [ ]* 14.2 Write unit tests for display formatting edge cases
    - Test formatting with missing foreign key references
    - Test formatting with invalid date values
    - Test formatting with null values in changes JSON
    - Test formatting with empty changes dictionary
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 14.3 Write unit tests for filtering edge cases
    - Test filtering with invalid date formats
    - Test filtering with non-existent event types
    - Test filtering with non-existent usernames
    - Test filtering with multiple filters combined
    - Test clearing filters returns all entries
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 14.4 Write unit tests for CSV export edge cases
    - Test export with no history entries
    - Test export with very large history datasets
    - Test export with special characters in field values
    - Test export filename generation
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 15. Final checkpoint - Complete feature verification
  - Run full test suite including property-based tests and unit tests
  - Verify all acceptance criteria are met
  - Test complete user workflows: create asset → view history, update asset → view history, free asset → view history
  - Verify history access from all locations (detail page, list pages)
  - Test filtering and export functionality end-to-end
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at logical breakpoints
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error conditions
- All history recording happens within database transactions to ensure atomicity
- History entries are immutable and permanent for audit trail integrity
- Performance is optimized through database indexes and query optimization
- The feature integrates seamlessly with existing AssetService methods

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3"] },
    { "id": 3, "tasks": ["2.4", "2.5", "2.7", "2.9"] },
    { "id": 4, "tasks": ["2.6", "2.8", "2.10"] },
    { "id": 5, "tasks": ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.8"] },
    { "id": 6, "tasks": ["4.9", "6.1", "6.3", "7"] },
    { "id": 7, "tasks": ["6.2", "6.4", "8.1"] },
    { "id": 8, "tasks": ["8.2", "8.3"] },
    { "id": 9, "tasks": ["8.4", "8.5"] },
    { "id": 10, "tasks": ["8.6", "9.1", "9.2", "9.3", "9.4"] },
    { "id": 11, "tasks": ["11.1", "12.1"] },
    { "id": 12, "tasks": ["11.2", "11.3", "12.2"] },
    { "id": 13, "tasks": ["11.4", "13.1", "13.2"] },
    { "id": 14, "tasks": ["13.3", "14.1", "14.2", "14.3", "14.4"] }
  ]
}
```
