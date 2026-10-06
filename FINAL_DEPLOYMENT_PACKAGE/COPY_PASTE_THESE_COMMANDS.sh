#!/bin/bash
#
# FINAL DEPLOYMENT - Copy and paste this entire file into Linux terminal
# This will deploy ALL files and fix ALL issues
#

echo "════════════════════════════════════════════════════════════════"
echo "        Asset Tracker - Final Deployment Starting..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Stop services
echo "⏸️  Stopping services..."
sudo systemctl stop asset_tracker
sudo systemctl stop nginx
echo "✅ Services stopped"
echo ""

# Go to upload location
echo "📁 Going to deployment package..."
cd /tmp/FINAL_DEPLOYMENT_PACKAGE
echo "✅ In deployment directory"
echo ""

# Copy all files
echo "📋 Copying all files..."
sudo cp -r assets/* /var/www/asset_tracker/assets/
echo "✅ Files copied"
echo ""

# Fix permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data /var/www/asset_tracker/assets
sudo chmod -R 755 /var/www/asset_tracker/assets
echo "✅ Permissions set"
echo ""

# Collect static files (CRITICAL!)
echo "📦 Collecting static files (CRITICAL STEP)..."
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --clear --noinput
echo "✅ Static files collected"
echo ""

# Restart services
echo "▶️  Restarting services..."
sudo systemctl start asset_tracker
sudo systemctl start nginx
echo "✅ Services restarted"
echo ""

# Verify
echo "════════════════════════════════════════════════════════════════"
echo "        Verification"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Checking bug fix..."
grep -q "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py && echo "✅ Bug fix deployed" || echo "❌ Bug fix NOT found"

echo "Checking CSS collected..."
test -f /var/www/asset_tracker/staticfiles/assets/css/styles.css && echo "✅ CSS file exists" || echo "❌ CSS file NOT found"

echo "Checking CSS content..."
grep -q "overflow-y.*auto" /var/www/asset_tracker/staticfiles/assets/css/styles.css && echo "✅ CSS has scrolling fix" || echo "❌ CSS fix NOT found"

echo "Checking services..."
systemctl is-active --quiet asset_tracker && echo "✅ Django running" || echo "❌ Django NOT running"
systemctl is-active --quiet nginx && echo "✅ Nginx running" || echo "❌ Nginx NOT running"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "        Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. USER: Clear browser cache (Ctrl+Shift+Delete)"
echo "2. USER: Test in Incognito window"
echo "3. USER: Verify table has scrollbar"
echo "4. USER: Verify edit asset is fast (no freeze)"
echo ""
echo "If all checks above show ✅, deployment is successful!"
echo ""
