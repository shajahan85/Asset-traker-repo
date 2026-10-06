# Requirements Document

## Introduction

This feature makes teams branch-specific in the Django Asset Tracker application. Currently, teams are global across all branches, meaning any team can be assigned to assets at any branch. This enhancement adds a mandatory branch foreign key to the Team model, ensuring teams belong to specific branches and can only be assigned to assets within the same branch.

## Glossary

- **Team_Model**: The Django model representing a team (assets.models.Team)
- **Branch_Model**: The Django model representing a branch/location (assets.models.Branch)
- **Asset_Model**: The Django model representing an asset (assets.models.Asset)
- **Team_Dropdown**: The UI component displaying teams for selection in asset forms
- **Migration_Script**: Django migration that adds branch field to Team model
- **Kochi_Branch**: The default branch that existing teams will be assigned to
- **Cross_Branch_Assignment**: An invalid state where an asset's team belongs to a different branch than the asset

## Requirements

### Requirement 1: Team Branch Association

**User Story:** As a system administrator, I want teams to belong to specific branches, so that team assignments are branch-specific and organizational structure is clearer.

#### Acceptance Criteria

1. THE Team_Model SHALL include a branch field as a ForeignKey to Branch_Model
2. THE Team_Model branch field SHALL be mandatory (not null, not blank)
3. WHEN creating a new team, THE system SHALL require a branch selection
4. WHEN displaying a team, THE system SHALL show which branch it belongs to
5. THE Team_Model SHALL maintain existing hierarchical relationships (parent/sub-team structure)
6. THE Team_Model branch field SHALL use PROTECT on_delete behavior to prevent accidental branch deletion

### Requirement 2: Data Migration for Existing Teams

**User Story:** As a system administrator, I want all existing teams automatically assigned to the Kochi branch during migration, so that the system upgrade is seamless.

#### Acceptance Criteria

1. THE Migration_Script SHALL identify the Branch_Model instance with name "Kochi"
2. IF the Kochi_Branch does not exist, THE Migration_Script SHALL create it with code "KCH"
3. THE Migration_Script SHALL assign all existing Team_Model instances to the Kochi_Branch
4. THE Migration_Script SHALL preserve all existing team names, parent relationships, and created_at timestamps
5. THE Migration_Script SHALL execute within a database transaction
6. IF the Migration_Script encounters an error, THEN it SHALL roll back all changes
7. THE Migration_Script SHALL log the number of teams migrated

### Requirement 3: Branch-Filtered Team Dropdowns

**User Story:** As a user creating or editing an asset, I want to see only teams from the asset's branch in the team dropdown, so that I cannot accidentally assign cross-branch teams.

#### Acceptance Criteria

1. WHEN rendering a Team_Dropdown for asset creation, THE form SHALL filter teams by the selected branch
2. WHEN rendering a Team_Dropdown for asset editing, THE form SHALL filter teams by the asset's current branch
3. IF no branch is selected, THE Team_Dropdown SHALL be empty or disabled
4. THE Team_Dropdown SHALL maintain hierarchical display (parent teams and indented sub-teams)
5. THE Team_Dropdown SHALL only show teams where Team_Model.branch equals the asset's branch
6. WHEN the branch field changes in the asset form, THE Team_Dropdown SHALL update dynamically to show teams from the new branch
7. THE parent_team and sub_team dropdowns SHALL both filter by the selected branch

### Requirement 4: Cross-Branch Assignment Prevention

**User Story:** As a system administrator, I want the system to prevent cross-branch team assignments, so that data integrity is maintained.

#### Acceptance Criteria

1. WHEN saving an Asset_Model, THE system SHALL validate that asset.team.branch equals asset.branch
2. IF an asset's team branch does not match the asset's branch, THE system SHALL raise a validation error
3. THE validation error message SHALL clearly state "Team must belong to the same branch as the asset"
4. THE validation SHALL occur in the Asset_Model clean() method
5. THE validation SHALL occur before database save operations
6. THE validation SHALL apply to both new assets and updates to existing assets
7. IF asset.team is None (no team assigned), THE validation SHALL pass

### Requirement 5: Team Management UI Updates

**User Story:** As a system administrator, I want to see branch information when managing teams, so that I can understand which teams belong to which branches.

#### Acceptance Criteria

1. THE Django admin team list view SHALL display a "Branch" column
2. THE team list view SHALL allow filtering teams by branch
3. THE team list view SHALL allow sorting by branch name
4. WHEN creating a new team in admin, THE form SHALL include a branch selection dropdown
5. WHEN editing an existing team in admin, THE form SHALL display the current branch and allow changing it
6. THE admin form SHALL show only active branches (is_active=True) in the branch dropdown
7. THE team detail/edit form SHALL clearly indicate which branch the team belongs to

### Requirement 6: Team Query Manager Updates

**User Story:** As a developer, I want team query methods to support branch filtering, so that team queries throughout the application can be branch-aware.

#### Acceptance Criteria

1. THE TeamManager SHALL provide a get_teams_by_branch(branch) method
2. THE get_teams_by_branch() method SHALL return all teams for the specified branch
3. THE get_teams_by_branch() method SHALL maintain hierarchical ordering (parents before sub-teams)
4. THE get_hierarchical_choices() method SHALL accept an optional branch parameter
5. WHEN get_hierarchical_choices(branch) is called, it SHALL return only teams from that branch
6. THE existing get_parent_teams() and get_sub_teams() methods SHALL accept an optional branch filter
7. ALL team query methods SHALL use select_related('branch') for efficient queries

### Requirement 7: Asset Form Branch-Team Coordination

**User Story:** As a user, I want the asset form to automatically coordinate branch and team selections, so that I cannot create invalid assignments.

#### Acceptance Criteria

1. WHEN a branch is selected in AssetForm, THE parent_team dropdown SHALL reload with teams from that branch
2. WHEN the branch changes in AssetForm, THE selected parent_team and sub_team SHALL be cleared
3. THE parent_team dropdown SHALL show only parent teams (no parent) from the selected branch
4. WHEN a parent_team is selected, THE sub_team dropdown SHALL show sub-teams of that parent from the same branch
5. THE JavaScript for cascading dropdowns SHALL coordinate with branch filtering
6. THE form __init__ method SHALL filter team querysets by branch when instance.branch exists
7. THE form clean() method SHALL validate branch-team consistency

### Requirement 8: ReassignmentForm Branch-Team Coordination

**User Story:** As a user reassigning a freed asset, I want team selections filtered by the asset's branch, so that reassignment maintains branch consistency.

#### Acceptance Criteria

1. THE ReassignmentForm SHALL receive the asset instance and extract its branch
2. THE parent_team dropdown in ReassignmentForm SHALL filter by asset.branch
3. THE sub_team dropdown in ReassignmentForm SHALL filter by asset.branch and selected parent_team
4. IF the asset has no branch, THE ReassignmentForm SHALL require branch selection before showing teams
5. THE ReassignmentForm clean() method SHALL validate that selected team belongs to asset's branch
6. THE validation error SHALL be clear: "Selected team must belong to the asset's branch"

### Requirement 9: Database Performance Optimization

**User Story:** As a user, I want team queries to remain fast after adding branch filtering, so that the application remains responsive.

#### Acceptance Criteria

1. THE Team_Model SHALL add a database index on the branch field
2. THE Team_Model Meta.indexes SHALL include a composite index on ['branch', 'parent', 'name']
3. WHEN querying teams, THE system SHALL use select_related('branch') to avoid N+1 queries
4. THE team hierarchy cache keys SHALL include branch identifier
5. WHEN a team's branch changes, THE system SHALL invalidate branch-specific caches
6. Team dropdown queries SHALL use .filter(branch=branch) before .get_parent_teams()

### Requirement 10: Migration Reversibility

**User Story:** As a system administrator, I want the ability to reverse the migration if needed, so that I can safely test the upgrade.

#### Acceptance Criteria

1. THE Migration_Script SHALL provide a reverse migration function
2. THE reverse migration SHALL remove the branch field from Team_Model
3. THE reverse migration SHALL preserve team names and hierarchical relationships
4. THE reverse migration SHALL execute within a database transaction
5. IF the reverse migration encounters an error, it SHALL roll back all changes
6. THE Migration_Script documentation SHALL warn that reversing will lose branch assignment data

### Requirement 11: Team Admin Form Validation

**User Story:** As a system administrator, I want the admin form to validate branch consistency for hierarchical teams, so that parent and sub-team branches match.

#### Acceptance Criteria

1. WHEN creating a sub-team, THE admin form SHALL validate that the sub-team's branch matches its parent's branch
2. IF a team has a parent, THE admin form SHALL enforce team.branch == team.parent.branch
3. IF branch mismatch is detected, THE admin form SHALL display: "Sub-team must belong to the same branch as its parent team"
4. THE validation SHALL occur in Team.clean() method
5. WHEN changing a parent team's branch, THE system SHALL prevent the change if it has sub-teams in different branches
6. THE validation error for parent branch change SHALL state: "Cannot change branch - this parent team has sub-teams in the current branch"

### Requirement 12: Existing Data Integrity

**User Story:** As a system administrator, I want existing asset-team assignments validated after migration, so that I can identify and fix any inconsistencies.

#### Acceptance Criteria

1. THE Migration_Script SHALL include a post-migration data validation step
2. THE validation step SHALL check that all assets with teams have asset.team.branch == asset.branch
3. IF inconsistencies are found, THE validation SHALL log warnings with asset IDs
4. THE validation SHALL not prevent migration completion
5. THE validation log SHALL include count of assets checked and count of inconsistencies found
6. THE system SHALL provide a management command to report cross-branch assignments: python manage.py check_team_branch_consistency
