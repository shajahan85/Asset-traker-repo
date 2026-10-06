# Implementation Plan: Branch-Specific Teams

## Overview

This implementation adds branch-specific team functionality to the Django Asset Tracker. Teams will be associated with specific branches through a mandatory foreign key, preventing cross-branch team assignments while maintaining hierarchical team structure. The implementation includes database migration, form filtering, validation logic, admin interface updates, and comprehensive testing.

## Tasks

- [ ] 1. Update Team model with branch field and validation
  - Add mandatory `branch` ForeignKey field to Team model
  - Add database indexes for query optimization
  - Add unique constraint for team name per branch
  - Implement `Team.clean()` validation for branch consistency with parent teams
  - Prevent parent team branch changes when sub-teams exist
  - Update model Meta with ordering and indexes
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 1.6, 9.1, 9.2, 11.1, 11.2, 11.4, 11.5_

- [ ]* 1.1 Write property test for Team branch field mandatory validation
  - **Property 1: Branch Field is Mandatory**
  - **Validates: Requirements 1.2, 1.3**
  - Test that team creation without branch raises ValidationError or IntegrityError
  - Use Hypothesis to generate random team data without branch field
  - Verify error is raised for all cases

- [ ]* 1.2 Write property test for branch deletion protection
  - **Property 4: Branch Deletion Protection**
  - **Validates: Requirements 1.6**
  - Test that deleting a branch with teams raises ProtectedError
  - Use Hypothesis to generate branches with varying numbers of teams
  - Verify deletion is prevented for all cases

- [ ]* 1.3 Write property test for sub-team branch matching parent
  - **Property 19: Sub-Team Branch Matches Parent**
  - **Validates: Requirements 11.1, 11.2, 11.3**
  - Test that sub-team with different branch than parent raises ValidationError
  - Use Hypothesis to generate parent-child team pairs with mismatched branches
  - Verify error message contains "Sub-team must belong to the same branch as its parent team"

- [ ]* 1.4 Write property test for parent branch change prevention
  - **Property 20: Parent Branch Change Prevention**
  - **Validates: Requirements 11.5, 11.6**
  - Test that changing parent team branch when sub-teams exist raises ValidationError
  - Use Hypothesis to generate parent teams with sub-teams and attempt branch change
  - Verify error message contains "Cannot change branch - this parent team has sub-teams in the current branch"

- [ ] 2. Create database migration for Team branch field
  - Create migration file that adds branch field as nullable first
  - Implement data migration function to assign all existing teams to Kochi branch
  - Create Kochi branch if it doesn't exist (code="KCH")
  - Make branch field non-nullable after data migration
  - Add database indexes and constraints
  - Implement reverse migration function
  - Add post-migration validation to check for cross-branch assignments
  - Include transaction handling and error logging
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 10.1, 10.2, 10.3, 10.4, 10.5, 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 2.1 Write property test for migration data preservation
  - **Property 5: Migration Preserves Team Data**
  - **Validates: Requirements 2.4**
  - Test that team data (name, parent, created_at) is identical before and after migration
  - Use Hypothesis to generate varying numbers of teams with different hierarchies
  - Verify all fields preserved except new branch field

- [ ] 3. Update TeamManager with branch filtering methods
  - Add `get_teams_by_branch(branch)` method to TeamManager
  - Update `get_parent_teams()` to accept optional branch parameter
  - Update `get_sub_teams()` to accept optional branch parameter
  - Update `get_hierarchical_choices()` to accept optional branch parameter
  - Add `select_related('branch')` to all query methods for optimization
  - Ensure hierarchical ordering maintained in branch-filtered queries
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 9.3_

- [ ]* 3.1 Write property test for TeamManager branch filtering
  - **Property 16: TeamManager Branch Filtering**
  - **Validates: Requirements 6.1, 6.2**
  - Test that get_teams_by_branch returns only teams from specified branch
  - Use Hypothesis to generate multiple branches with varying numbers of teams
  - Verify returned queryset contains exactly teams matching branch

- [ ]* 3.2 Write property test for hierarchical ordering in branch queries
  - **Property 17: Hierarchical Ordering in Branch Queries**
  - **Validates: Requirements 6.3**
  - Test that get_teams_by_branch returns parents before sub-teams
  - Use Hypothesis to generate branches with parent and sub-teams
  - Verify ordering maintains hierarchy for all cases

- [ ]* 3.3 Write property test for optional branch parameter in manager methods
  - **Property 18: Optional Branch Parameter in Manager Methods**
  - **Validates: Requirements 6.4, 6.5, 6.6**
  - Test that manager methods with branch parameter filter correctly
  - Use Hypothesis to test get_parent_teams, get_sub_teams, get_hierarchical_choices
  - Verify all methods respect branch filter when provided

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Add Asset model validation for branch-team consistency
  - Update `Asset.clean()` to validate team.branch equals asset.branch
  - Add validation to require branch when team is assigned
  - Raise ValidationError with message "Team must belong to the same branch as the asset"
  - Ensure validation applies to both new and existing assets
  - Allow validation to pass when team is None
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 5.1 Write property test for cross-branch assignment validation
  - **Property 11: Cross-Branch Assignment Validation**
  - **Validates: Requirements 4.1, 4.2**
  - Test that asset with team from different branch raises ValidationError
  - Use Hypothesis to generate assets and teams with mismatched branches
  - Verify validation error is raised in all cases

- [ ]* 5.2 Write property test for validation error message content
  - **Property 12: Validation Error Message Content**
  - **Validates: Requirements 4.3**
  - Test that ValidationError message contains specific text
  - Use Hypothesis to generate mismatched asset-team combinations
  - Verify message contains "Team must belong to the same branch as the asset"

- [ ]* 5.3 Write property test for validation without team
  - **Property 15: Validation Passes Without Team**
  - **Validates: Requirements 4.7**
  - Test that assets without teams pass validation regardless of branch
  - Use Hypothesis to generate assets with team=None and various branches
  - Verify validation succeeds for all cases

- [ ] 6. Update AssetForm with branch-filtered team dropdowns
  - Filter parent_team queryset by asset's branch in form __init__
  - Filter sub_team queryset by parent.branch in form __init__
  - Handle branch selection in form initialization for new assets
  - Handle POST data to filter teams during form submission
  - Set empty queryset when no branch is selected
  - Add onchange handler to branch field widget
  - Pre-populate team dropdowns correctly for existing assets
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 7.1, 7.2, 7.3, 7.4, 7.6, 7.7_

- [ ]* 6.1 Write property test for team dropdown filtered by branch
  - **Property 8: Team Dropdown Filtered by Branch**
  - **Validates: Requirements 3.1, 3.2, 3.5, 3.7**
  - Test that AssetForm team queryset contains only teams from selected branch
  - Use Hypothesis to generate assets with branches and teams in multiple branches
  - Verify parent_team and sub_team querysets filter correctly

- [ ]* 6.2 Write property test for empty team dropdown without branch
  - **Property 9: Empty Team Dropdown Without Branch**
  - **Validates: Requirements 3.3**
  - Test that team queryset is empty when no branch selected
  - Use Hypothesis to generate form states without branch
  - Verify team dropdown queryset is empty for all cases

- [ ] 7. Update ReassignmentForm with branch-filtered team dropdowns
  - Accept asset instance in __init__ and extract branch
  - Filter parent_team queryset by asset.branch
  - Filter sub_team queryset by asset.branch and parent
  - Handle POST data to maintain branch filtering during submission
  - Pre-populate team fields with asset's current team if exists
  - Add validation in clean() to ensure team belongs to asset's branch
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ] 8. Create JavaScript functions for branch-team coordination
  - Implement `handleBranchChange(branchId)` to clear team selections and reload parent teams
  - Implement `handleParentTeamChange(parentTeamId)` to load sub-teams filtered by branch
  - Add AJAX calls to team filtering API endpoints
  - Handle empty responses and error cases gracefully
  - Update hidden team field when selections change
  - Show/hide sub-team dropdown based on availability
  - _Requirements: 7.5, 7.6_

- [ ] 9. Create API endpoints for team filtering
  - Create `get_parent_teams_by_branch` view accepting branch parameter
  - Create `get_sub_teams_by_parent_and_branch` view accepting parent and branch parameters
  - Return JSON responses with team id and name
  - Handle missing parameters by returning empty lists
  - Verify parent team belongs to branch before returning sub-teams
  - Add URL patterns for both endpoints
  - Require authentication for both endpoints
  - _Requirements: 3.6, 7.5_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Update Team Django admin configuration
  - Add 'branch' to list_display fields
  - Add 'branch' to list_filter
  - Add 'branch__name' to search_fields
  - Update ordering to include 'branch__name'
  - Add branch field to admin form fieldsets
  - Use select_related('branch', 'parent') in get_queryset
  - Add readonly_fields for created_at
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 12. Create management command for consistency checking
  - Create `check_team_branch_consistency` management command
  - Query all assets with teams and branches
  - Check that asset.team.branch == asset.branch for each
  - Log count of assets checked and inconsistencies found
  - Display asset details for inconsistent assignments
  - Use select_related for efficient querying
  - _Requirements: 12.6_

- [ ]* 12.1 Write unit tests for consistency check command
  - Test command with no inconsistencies
  - Test command with cross-branch assignments
  - Test command output formatting
  - Test command with assets without teams or branches
  - Verify correct counts displayed

- [ ] 13. Write unit tests for Team model
  - Test team creation with branch field
  - Test branch field is required
  - Test team string representation includes branch
  - Test hierarchical relationships preserved
  - Test unique constraint on branch + name
  - Test circular reference prevention
  - Test depth limitation (max 2 levels)
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ] 14. Write unit tests for migration
  - Test migration forward execution
  - Test Kochi branch creation if not exists
  - Test existing Kochi branch reuse
  - Test all teams assigned to Kochi
  - Test migration reverse execution
  - Test transaction rollback on error
  - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 15. Write unit tests for AssetForm and ReassignmentForm
  - Test AssetForm filters teams by branch on initialization
  - Test AssetForm handles POST data with branch selection
  - Test AssetForm clears teams when branch changes
  - Test ReassignmentForm filters teams by asset branch
  - Test form validation prevents cross-branch assignments
  - Test empty queryset when no branch selected
  - _Requirements: 3.1, 3.2, 3.3, 7.1, 7.2, 7.3, 7.6, 7.7, 8.1, 8.2, 8.3, 8.5, 8.6_

- [ ] 16. Write unit tests for API endpoints
  - Test get_parent_teams_by_branch with valid branch
  - Test get_parent_teams_by_branch with invalid branch
  - Test get_parent_teams_by_branch without branch parameter
  - Test get_sub_teams_by_parent_and_branch with valid parameters
  - Test get_sub_teams_by_parent_and_branch with mismatched branch
  - Test get_sub_teams_by_parent_and_branch with missing parameters
  - Test authentication requirement
  - _Requirements: 3.6, 7.5_

- [ ] 17. Write integration tests for complete workflows
  - Test creating new asset with team from same branch
  - Test editing asset and changing team to different branch (should fail)
  - Test changing asset branch clears team selection
  - Test reassigning freed asset with branch-filtered teams
  - Test admin interface team creation with branch
  - Test admin interface team editing with branch change validation
  - _Requirements: All_

- [ ] 18. Final checkpoint - Ensure all tests pass and documentation complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Property-based tests use Hypothesis with minimum 100 iterations per test
- Migration must be tested on development copy before production deployment
- JavaScript functions require jQuery or vanilla JS AJAX implementation
- API endpoints should be added to assets/urls.py or assets/api/urls.py
- Management command should be placed in assets/management/commands/
- Unit tests should be added to assets/tests/ directory
- Integration tests may require Django TestCase with database transactions

## Task Dependency Graph

```json
{
  "waves": [
    {
      "id": 0,
      "tasks": ["1", "13"]
    },
    {
      "id": 1,
      "tasks": ["1.1", "1.2", "1.3", "1.4", "2"]
    },
    {
      "id": 2,
      "tasks": ["2.1", "3", "14"]
    },
    {
      "id": 3,
      "tasks": ["3.1", "3.2", "3.3", "5"]
    },
    {
      "id": 4,
      "tasks": ["5.1", "5.2", "5.3", "6"]
    },
    {
      "id": 5,
      "tasks": ["6.1", "6.2", "7", "15"]
    },
    {
      "id": 6,
      "tasks": ["8", "9", "11"]
    },
    {
      "id": 7,
      "tasks": ["12", "16"]
    },
    {
      "id": 8,
      "tasks": ["12.1", "17"]
    }
  ]
}
```
