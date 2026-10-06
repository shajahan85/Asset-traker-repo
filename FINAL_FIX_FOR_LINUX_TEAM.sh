#!/bin/bash
#
# FINAL FIX - Asset Tracker CSS Not Working
# Run these commands EXACTLY in this order
#

echo "════════════════════════════════════════════════════════"
echo "  Asset Tracker - Final CSS Fix"
echo "════════════════════════════════════════════════════════"
echo ""

# Step 1: Stop services
echo "1. Stopping services..."
sudo systemctl stop asset_tracker
sudo systemctl stop nginx
echo "✅ Services stopped"
echo ""

# Step 2: Verify new CSS is in source location
echo "2. Checking source CSS file..."
if [ -f /var/www/asset_tracker/assets/static/assets/css/styles.css ]; then
    SOURCE_SIZE=$(ls -lh /var/www/asset_tracker/assets/static/assets/css/styles.css | awk '{print $5}')
    SOURCE_DATE=$(ls -l /var/www/asset_tracker/assets/static/assets/css/styles.css | awk '{print $6, $7, $8}')
    echo "✅ Source CSS exists"
    echo "   Size: $SOURCE_SIZE"
    echo "   Date: $SOURCE_DATE"
    
    # Check if it has the new content
    if grep -q "overflow-y.*auto" /var/www/asset_tracker/assets/static/assets/css/styles.css; then
        echo "✅ Source CSS has NEW content (overflow-y: auto found)"
    else
        echo "❌ ERROR: Source CSS has OLD content!"
        echo "   You must copy the NEW styles.css file first!"
        echo "   Source: DEPLOY_TO_LINUX/assets/static/assets/css/styles.css"
        echo "   Dest: /var/www/asset_tracker/assets/static/assets/css/styles.css"
        exit 1
    fi
else
    echo "❌ ERROR: Source CSS file not found!"
    exit 1
fi
echo ""

# Step 3: Delete ALL old collected static files
echo "3. Deleting old staticfiles..."
rm -rf /var/www/asset_tracker/staticfiles/assets/
rm -rf /var/www/asset_tracker/staticfiles/admin/
echo "✅ Old staticfiles deleted"
echo ""

# Step 4: Go to project directory
echo "4. Changing to project directory..."
cd /var/www/asset_tracker
echo "✅ In project directory"
echo ""

# Step 5: Activate virtual environment
echo "5. Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Step 6: Run collectstatic
echo "6. Collecting static files..."
python manage.py collectstatic --clear --noinput
echo "✅ Static files collected"
echo ""

# Step 7: Verify CSS was collected correctly
echo "7. Verifying collected CSS..."
if [ -f /var/www/asset_tracker/staticfiles/assets/css/styles.css ]; then
    COLLECTED_SIZE=$(ls -lh /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $5}')
    COLLECTED_DATE=$(ls -l /var/www/asset_tracker/staticfiles/assets/css/styles.css | awk '{print $6, $7, $8}')
    echo "✅ Collected CSS exists"
    echo "   Size: $COLLECTED_SIZE"
    echo "   Date: $COLLECTED_DATE"
    
    # Check if collected file has new content
    if grep -q "overflow-y.*auto" /var/www/asset_tracker/staticfiles/assets/css/styles.css; then
        echo "✅ Collected CSS has NEW content!"
    else
        echo "❌ ERROR: Collected CSS still has OLD content!"
        echo "   Something went wrong with collectstatic"
        exit 1
    fi
    
    # Check sizes match
    SOURCE_BYTES=$(stat -c%s /var/www/asset_tracker/assets/static/assets/css/styles.css)
    COLLECTED_BYTES=$(stat -c%s /var/www/asset_tracker/staticfiles/assets/css/styles.css)
    if [ "$SOURCE_BYTES" -eq "$COLLECTED_BYTES" ]; then
        echo "✅ File sizes match - correct file copied"
    else
        echo "⚠️  WARNING: File sizes don't match!"
        echo "   Source: $SOURCE_BYTES bytes"
        echo "   Collected: $COLLECTED_BYTES bytes"
    fi
else
    echo "❌ ERROR: CSS was not collected!"
    exit 1
fi
echo ""

# Step 8: Fix permissions
echo "8. Setting permissions..."
sudo chown -R www-data:www-data /var/www/asset_tracker/staticfiles
sudo chmod -R 755 /var/www/asset_tracker/staticfiles
echo "✅ Permissions set"
echo ""

# Step 9: Clear Nginx cache
echo "9. Clearing Nginx cache..."
if [ -d /var/cache/nginx ]; then
    sudo rm -rf /var/cache/nginx/*
    echo "✅ Nginx cache cleared"
else
    echo "ℹ️  No Nginx cache directory found (OK)"
fi
echo ""

# Step 10: Start services
echo "10. Starting services..."
sudo systemctl start asset_tracker
sudo systemctl start nginx
echo "✅ Services started"
echo ""

# Step 11: Verify services are running
echo "11. Verifying services..."
sleep 2
if systemctl is-active --quiet asset_tracker; then
    echo "✅ asset_tracker is running"
else
    echo "❌ ERROR: asset_tracker failed to start!"
    echo "   Check logs: sudo journalctl -u asset_tracker -n 50"
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo "✅ nginx is running"
else
    echo "❌ ERROR: nginx failed to start!"
    exit 1
fi
echo ""

# Step 12: Final summary
echo "════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Tell user to clear browser cache (Ctrl+Shift+Delete)"
echo "2. User should close browser completely"
echo "3. User should test in Incognito/Private window"
echo "4. Check if horizontal scrollbar appears"
echo "5. Check if 'Freed Systems' title is visible"
echo "6. Check if table layout is correct"
echo ""
echo "If user still sees issues after clearing cache:"
echo "  - Tell them to try different browser"
echo "  - Tell them to try from different computer"
echo ""
echo "════════════════════════════════════════════════════════"
