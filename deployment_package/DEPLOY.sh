#!/bin/bash
#
# Quick Deployment Script for Asset Tracker Updates
# Run this on your Linux server after uploading the deployment_package
#
# Usage: bash DEPLOY.sh
#

set -e  # Exit on error

echo "======================================"
echo "Asset Tracker - Deployment Script"
echo "======================================"
echo ""

# Check if running from correct directory
if [ ! -f "README.md" ]; then
    echo "Error: Please run this script from the deployment_package directory"
    exit 1
fi

# Variables
APP_DIR="/var/www/asset_tracker"
BACKUP_DIR="$APP_DIR/backups/$(date +%Y%m%d_%H%M%S)"

echo "Step 1: Creating backup..."
sudo mkdir -p "$BACKUP_DIR"
sudo cp "$APP_DIR/assets/forms/asset_forms.py" "$BACKUP_DIR/" 2>/dev/null || true
sudo cp "$APP_DIR/assets/services/notification_service.py" "$BACKUP_DIR/" 2>/dev/null || true
sudo cp -r "$APP_DIR/assets/templates/assets/asset_form.html" "$BACKUP_DIR/" 2>/dev/null || true
sudo cp -r "$APP_DIR/assets/templates/assets/free_ips.html" "$BACKUP_DIR/" 2>/dev/null || true
sudo cp -r "$APP_DIR/assets/templates/assets/freed_systems.html" "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backup created at: $BACKUP_DIR"
echo ""

echo "Step 2: Copying new files..."
sudo cp -r assets/* "$APP_DIR/assets/"
echo "✓ Files copied"
echo ""

echo "Step 3: Setting permissions..."
sudo chown -R www-data:www-data "$APP_DIR/assets"
sudo chmod -R 755 "$APP_DIR/assets"
echo "✓ Permissions set"
echo ""

echo "Step 4: Collecting static files..."
cd "$APP_DIR"
source venv/bin/activate
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

echo "Step 5: Restarting application..."
sudo systemctl restart asset_tracker
sleep 2
echo "✓ Application restarted"
echo ""

echo "Step 6: Checking status..."
sudo systemctl status asset_tracker --no-pager | head -n 10
echo ""

echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Visit your website and test the changes"
echo "2. Check: Email toggle checkbox in asset forms"
echo "3. Check: IP series filter on Free IP page"
echo "4. Check: Freed Systems page (no Issues column)"
echo ""
echo "If issues occur, restore backup from:"
echo "$BACKUP_DIR"
echo ""
