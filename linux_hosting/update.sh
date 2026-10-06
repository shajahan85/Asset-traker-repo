#!/bin/bash

# Asset Tracker Update Script
# Updates the application with zero downtime

set -e

PROJECT_NAME="asset_tracker"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"

echo "========================================"
echo "Asset Tracker Update Script"
echo "========================================"

# Navigate to project directory
cd $PROJECT_DIR

echo "Step 1: Backing up database..."
bash linux_hosting/backup.sh

echo "Step 2: Pulling latest code..."
git pull origin main  # Change 'main' to your branch name

echo "Step 3: Activating virtual environment..."
source $VENV_DIR/bin/activate

echo "Step 4: Installing/updating dependencies..."
pip install -r linux_hosting/requirements_production.txt

echo "Step 5: Running database migrations..."
python manage.py migrate --noinput

echo "Step 6: Collecting static files..."
python manage.py collectstatic --noinput

echo "Step 7: Restarting Gunicorn..."
sudo systemctl restart $PROJECT_NAME

echo "Step 8: Checking service status..."
sleep 2
sudo systemctl is-active $PROJECT_NAME && echo "✓ Service is running" || echo "✗ Service failed to start"

echo "========================================"
echo "Update completed at $(date)"
echo "========================================"

# Show recent logs
echo ""
echo "Recent logs:"
sudo journalctl -u $PROJECT_NAME -n 20 --no-pager
