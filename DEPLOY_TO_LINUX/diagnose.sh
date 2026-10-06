#!/bin/bash
#
# Diagnostic script - Run this to check deployment status
# Usage: bash diagnose.sh
#

echo "════════════════════════════════════════════════════════════════"
echo "        Asset Tracker Deployment Diagnostic"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Bug fix deployed
echo "1. Checking bug fix in source code..."
if grep -q "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py 2>/dev/null; then
    echo -e "${GREEN}✅ Bug fix found in asset_forms.py${NC}"
else
    echo -e "${RED}❌ Bug fix NOT found! File not deployed or wrong content${NC}"
fi
echo ""

# Check 2: CSS file in source
echo "2. Checking CSS in source location..."
if [ -f /var/www/asset_tracker/assets/static/assets/css/styles.css ]; then
    SIZE=$(ls -lh /var/www/asset_tracker/assets/static/assets/css/styles.css | awk '{print $5}')
    DATE=$(ls -l /var/www/asset_tracker/assets/static/assets/css/styles.css | awk '{print $6, $7, $8}')
    echo -e "${GREEN}✅ styles.css exists in source${NC}"
    echo "   Size: $SIZE, Modified: $DATE"
else
    echo -e "${RED}❌ styles.css NOT found in source!${NC}"
fi
echo ""

# Check 3: CSS collected to staticfiles
echo "3. Checking CSS in staticfiles (SERVED location)..."
if [ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]; then
    SIZE=$(ls -lh /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $5}')
    DATE=$(ls -l /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $6, $7, $8}')
    echo -e "${GREEN}✅ styles.css exists in staticfiles${NC}"
    echo "   Size: $SIZE, Modified: $DATE"
    
    # Check if file is recent (modified today)
    FILE_DATE=$(stat -c %Y /var/www/asset_tracker/staticfiles/assets/css/styles.css 2>/dev/null)
    TODAY=$(date +%Y%m%d)
    FILE_DAY=$(date -d @$FILE_DATE +%Y%m%d 2>/dev/null)
    
    if [ "$FILE_DAY" == "$TODAY" ]; then
        echo -e "${GREEN}   ✅ File was modified TODAY - Good!${NC}"
    else
        echo -e "${RED}   ❌ File is OLD! collectstatic probably not run!${NC}"
    fi
else
    echo -e "${RED}❌ styles.css NOT found in staticfiles!${NC}"
    echo -e "${RED}   collectstatic was NOT run!${NC}"
fi
echo ""

# Check 4: CSS content
echo "4. Checking CSS content..."
if [ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]; then
    if grep -q "overflow-y.*auto" /var/www/asset_tracker/staticfiles/assets/css/styles.css; then
        echo -e "${GREEN}✅ CSS has scrolling fix (overflow-y: auto)${NC}"
    else
        echo -e "${RED}❌ CSS does NOT have fix! Shows old content${NC}"
        echo "   Checking what it shows:"
        grep "overflow-y" /var/www/asset_tracker/staticfiles/assets/css/styles.css | head -3
    fi
    
    if grep -q "max-height.*70vh" /var/www/asset_tracker/staticfiles/assets/css/styles.css; then
        echo -e "${GREEN}✅ CSS has height limit (max-height: 70vh)${NC}"
    else
        echo -e "${RED}❌ CSS does NOT have height limit!${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cannot check CSS content - file not found${NC}"
fi
echo ""

# Check 5: Services status
echo "5. Checking services..."
if systemctl is-active --quiet asset_tracker; then
    echo -e "${GREEN}✅ asset_tracker service is running${NC}"
else
    echo -e "${RED}❌ asset_tracker service is NOT running!${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ nginx service is running${NC}"
else
    echo -e "${RED}❌ nginx service is NOT running!${NC}"
fi
echo ""

# Check 6: Recent errors
echo "6. Checking for recent errors..."
ERRORS=$(sudo journalctl -u asset_tracker -n 50 --no-pager 2>/dev/null | grep -i "error" | wc -l)
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ No errors in recent logs${NC}"
else
    echo -e "${YELLOW}⚠️  Found $ERRORS error lines in logs${NC}"
    echo "   Last few errors:"
    sudo journalctl -u asset_tracker -n 50 --no-pager 2>/dev/null | grep -i "error" | tail -3
fi
echo ""

# Check 7: File permissions
echo "7. Checking file permissions..."
if [ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]; then
    PERMS=$(ls -l /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $1, $3, $4}')
    echo "   Permissions: $PERMS"
    OWNER=$(ls -l /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $3}')
    if [ "$OWNER" == "www-data" ]; then
        echo -e "${GREEN}✅ File owned by www-data${NC}"
    else
        echo -e "${YELLOW}⚠️  File owned by $OWNER (should be www-data)${NC}"
    fi
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════"
echo "        SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Count issues
ISSUES=0

grep -q "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py 2>/dev/null || ((ISSUES++))
[ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ] || ((ISSUES++))
grep -q "overflow-y.*auto" /var/www/asset_tracker/staticfiles/assets/css/styles.css 2>/dev/null || ((ISSUES++))
systemctl is-active --quiet asset_tracker || ((ISSUES++))
systemctl is-active --quiet nginx || ((ISSUES++))

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "Deployment appears to be successful."
    echo "If user still sees issues, tell them to:"
    echo "  1. Clear browser cache (Ctrl+Shift+Delete)"
    echo "  2. Close browser completely"
    echo "  3. Test in Incognito/Private window"
else
    echo -e "${RED}❌ FOUND $ISSUES ISSUES!${NC}"
    echo ""
    echo "MOST LIKELY PROBLEM:"
    if [ ! -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]; then
        echo -e "${RED}  → collectstatic was NOT run!${NC}"
        echo ""
        echo "FIX:"
        echo "  cd /var/www/asset_tracker"
        echo "  source venv/bin/activate"
        echo "  python manage.py collectstatic --clear --noinput"
        echo "  sudo systemctl restart asset_tracker nginx"
    elif ! grep -q "overflow-y.*auto" /var/www/asset_tracker/staticfiles/assets/css/styles.css 2>/dev/null; then
        echo -e "${RED}  → OLD CSS file in staticfiles!${NC}"
        echo ""
        echo "FIX:"
        echo "  rm -rf /var/www/asset_tracker/staticfiles/assets/"
        echo "  cd /var/www/asset_tracker"
        echo "  source venv/bin/activate"
        echo "  python manage.py collectstatic --clear --noinput"
        echo "  sudo systemctl restart nginx"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
