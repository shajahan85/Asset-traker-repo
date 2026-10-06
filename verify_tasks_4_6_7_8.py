"""
Verification script for tasks 4.6, 4.7, and 4.8
This script verifies that history recording has been added to:
- update_freed_asset (Task 4.6)
- create_freed_asset (Task 4.7)
- create_scrapped_asset (Task 4.8)
"""

import re

def verify_task_implementation():
    """Verify that all three tasks have been implemented correctly."""
    
    with open('assets/services/asset_service.py', 'r') as f:
        content = f.read()
    
    results = {
        'task_4_6': False,
        'task_4_7': False,
        'task_4_8': False
    }
    
    # Task 4.6: Check update_freed_asset method
    # Looking for: old_health_status capture and record_health_status_update call
    update_freed_pattern = r'def update_freed_asset.*?old_health_status = asset\.health_status.*?HistoryService\.record_health_status_update\(asset, old_health_status, user\)'
    if re.search(update_freed_pattern, content, re.DOTALL):
        results['task_4_6'] = True
        print("✓ Task 4.6: update_freed_asset has history recording")
        print("  - Captures old_health_status value")
        print("  - Calls HistoryService.record_health_status_update()")
    else:
        print("✗ Task 4.6: update_freed_asset missing history recording")
    
    # Task 4.7: Check create_freed_asset method
    # Looking for: HistoryService.record_creation call
    create_freed_pattern = r'def create_freed_asset.*?HistoryService\.record_creation\(asset, user\)'
    if re.search(create_freed_pattern, content, re.DOTALL):
        results['task_4_7'] = True
        print("\n✓ Task 4.7: create_freed_asset has history recording")
        print("  - Calls HistoryService.record_creation()")
    else:
        print("\n✗ Task 4.7: create_freed_asset missing history recording")
    
    # Task 4.8: Check create_scrapped_asset method
    # Looking for: HistoryService.record_creation call
    create_scrapped_pattern = r'def create_scrapped_asset.*?HistoryService\.record_creation\(asset, user\)'
    if re.search(create_scrapped_pattern, content, re.DOTALL):
        results['task_4_8'] = True
        print("\n✓ Task 4.8: create_scrapped_asset has history recording")
        print("  - Calls HistoryService.record_creation()")
    else:
        print("\n✗ Task 4.8: create_scrapped_asset missing history recording")
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_complete = all(results.values())
    
    if all_complete:
        print("✓ All tasks (4.6, 4.7, 4.8) are COMPLETE")
        print("\nImplementation details:")
        print("- Task 4.6: update_freed_asset captures old health_status")
        print("            and calls HistoryService.record_health_status_update()")
        print("- Task 4.7: create_freed_asset calls HistoryService.record_creation()")
        print("- Task 4.8: create_scrapped_asset calls HistoryService.record_creation()")
    else:
        incomplete = [task for task, status in results.items() if not status]
        print(f"✗ Incomplete tasks: {', '.join(incomplete)}")
    
    return all_complete

if __name__ == '__main__':
    verify_task_implementation()
