#!/bin/bash
# Verification script for freeze bug fix

echo "========================================"
echo "FREEZE BUG FIX - VERIFICATION SCRIPT"
echo "========================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "WARNING: This script should be run with sudo for restart commands"
    echo ""
fi

# Set the project path
PROJECT_PATH="/var/www/asset_tracker"
FILE_PATH="$PROJECT_PATH/assets/forms/asset_forms.py"

echo "1. Checking if asset_forms.py exists..."
if [ -f "$FILE_PATH" ]; then
    echo "   ✓ File found: $FILE_PATH"
else
    echo "   ✗ File NOT found: $FILE_PATH"
    echo "   Please check the project path"
    exit 1
fi

echo ""
echo "2. Checking for IP query optimization (limit=20)..."
if grep -q "def get_filtered_free_ips(include_current_ip_id=None, limit=20):" "$FILE_PATH"; then
    echo "   ✓ IP query has limit=20 (ultra-fast)"
else
    echo "   ✗ IP query does NOT have limit=20"
    echo "   The fix has not been applied!"
    exit 1
fi

echo ""
echo "3. Checking for Operating System query optimization (limit 50)..."
if grep -q "\.only('id', 'name')\.order_by('name')\[:50\]" "$FILE_PATH"; then
    echo "   ✓ Operating System query is optimized with limit 50"
else
    echo "   ✗ Operating System query is NOT optimized"
    echo "   The fix has not been applied!"
    exit 1
fi

echo ""
echo "4. Checking for Branch query optimization (limit 50)..."
if grep -q "Branch\.objects\.filter(is_active=True)\.only('id', 'name')\.order_by('name')\[:50\]" "$FILE_PATH"; then
    echo "   ✓ Branch query is optimized with limit 50"
else
    echo "   ✗ Branch query is NOT optimized"
    echo "   The fix has not been applied!"
    exit 1
fi

echo ""
echo "5. Checking for Team query optimization (limit 50)..."
if grep -q "Team\.objects\.get_parent_teams(branch=current_branch)\.only('id', 'name')\[:50\]" "$FILE_PATH"; then
    echo "   ✓ Team queries are optimized with limit 50"
else
    echo "   ✗ Team queries are NOT optimized"
    echo "   The fix has not been applied!"
    exit 1
fi

echo ""
echo "6. Checking Django service status..."
if systemctl is-active --quiet asset_tracker; then
    echo "   ✓ Django service is running"
    echo "   Status:"
    systemctl status asset_tracker | grep "Active:"
else
    echo "   ✗ Django service is NOT running"
    echo "   Run: sudo systemctl start asset_tracker"
    exit 1
fi

echo ""
echo "========================================"
echo "VERIFICATION COMPLETE!"
echo "========================================"
echo ""
echo "All checks passed. The freeze bug fix is properly deployed."
echo ""
echo "NEXT STEPS:"
echo "1. Clear browser cache (Ctrl+Shift+Delete)"
echo "2. Test editing employee code for BIDC1326"
echo "3. Page should load instantly without freezing"
echo ""
