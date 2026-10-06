#!/bin/bash
#
# Deployment Verification Script
# Run this after deployment to check if everything is correctly deployed
#

echo "════════════════════════════════════════════════════════════════"
echo "           Asset Tracker - Deployment Verification"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0

# Function to check and report
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $1"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $1"
        ((FAIL++))
    fi
}

echo "Checking deployment..."
echo ""

# 1. Check if bug fix is deployed
echo "1. Checking bug fix (asset_forms.py)..."
grep -q "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py
check "Bug fix found in source code"

# 2. Check if CSS source deployed
echo "2. Checking CSS files..."
[ -f /var/www/asset_tracker/assets/static/assets/css/styles.css ]
check "styles.css found in source"

grep -q "max-height.*70vh" /var/www/asset_tracker/assets/static/assets/css/styles.css
check "CSS fix found in styles.css"

# 3. Check if static files collected
echo "3. Checking staticfiles..."
[ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]
check "styles.css found in staticfiles"

grep -q "max-height.*70vh" /var/www/asset_tracker/staticfiles/assets/css/styles.css 2>/dev/null
check "CSS fix found in collected staticfiles"

# 4. Check Server Controller views
echo "4. Checking Server Controller files..."
[ -f /var/www/asset_tracker/assets/views_server_controller.py ]
check "views_server_controller.py exists"

# 5. Check templates
echo "5. Checking templates..."
[ -f /var/www/asset_tracker/assets/templates/assets/server_controller_list.html ]
check "server_controller_list.html exists"

# 6. Check permissions
echo "6. Checking permissions..."
OWNER=$(stat -c '%U' /var/www/asset_tracker/assets/forms/asset_forms.py 2>/dev/null)
if [ "$OWNER" = "www-data" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Correct ownership (www-data)"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}: Wrong ownership ($OWNER, should be www-data)"
    ((FAIL++))
fi

# 7. Check Django service
echo "7. Checking services..."
systemctl is-active --quiet asset_tracker
check "Django service is running"

systemctl is-active --quiet nginx
check "Nginx service is running"

# 8. Check for recent errors
echo "8. Checking logs..."
ERRORS=$(sudo journalctl -u asset_tracker -n 50 --no-pager 2>/dev/null | grep -i error | wc -l)
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC}: No recent errors in logs"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  WARN${NC}: $ERRORS error(s) found in recent logs"
    echo "Run: sudo journalctl -u asset_tracker -n 50 | grep -i error"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "                    Verification Summary"
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "Deployment appears successful. If changes still not visible:"
    echo "1. Clear browser cache (Ctrl + Shift + Delete)"
    echo "2. Try incognito/private window"
    echo "3. Hard refresh (Ctrl + F5)"
else
    echo -e "${RED}❌ DEPLOYMENT INCOMPLETE${NC}"
    echo ""
    echo "Failed checks detected. Please:"
    echo "1. Review failed checks above"
    echo "2. Follow TROUBLESHOOTING.md"
    echo "3. Run deployment commands again"
    echo ""
    echo "Quick fix commands:"
    echo "  cd /tmp/COMPLETE_DEPLOYMENT"
    echo "  sudo cp -r assets/* /var/www/asset_tracker/assets/"
    echo "  sudo chown -R www-data:www-data /var/www/asset_tracker/assets"
    echo "  python manage.py collectstatic --clear --noinput"
    echo "  sudo systemctl restart asset_tracker nginx"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
