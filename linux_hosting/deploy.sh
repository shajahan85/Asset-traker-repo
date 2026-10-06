#!/bin/bash

# Asset Tracker Django Application Deployment Script
# This script automates the deployment process on a Linux server

set -e  # Exit on any error

echo "========================================="
echo "Asset Tracker Deployment Script"
echo "========================================="

# Configuration
PROJECT_NAME="asset_tracker"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"
GROUP="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Step 1: Creating project directory..."
mkdir -p $PROJECT_DIR
mkdir -p /var/log/$PROJECT_NAME
mkdir -p /var/run/$PROJECT_NAME

print_status "Step 2: Setting up Python virtual environment..."
cd $PROJECT_DIR
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

print_status "Step 3: Installing Python dependencies..."
pip install --upgrade pip
pip install -r linux_hosting/requirements_production.txt
pip install gunicorn

print_status "Step 4: Collecting static files..."
python manage.py collectstatic --noinput

print_status "Step 5: Running database migrations..."
python manage.py migrate --noinput

print_status "Step 6: Setting up Nginx..."
cp linux_hosting/nginx.conf /etc/nginx/sites-available/$PROJECT_NAME
ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
nginx -t  # Test nginx configuration

print_status "Step 7: Setting up Gunicorn systemd service..."
cp linux_hosting/gunicorn.service /etc/systemd/system/$PROJECT_NAME.service
cp linux_hosting/gunicorn.socket /etc/systemd/system/$PROJECT_NAME.socket
systemctl daemon-reload

print_status "Step 8: Setting file permissions..."
chown -R $USER:$GROUP $PROJECT_DIR
chown -R $USER:$GROUP /var/log/$PROJECT_NAME
chown -R $USER:$GROUP /var/run/$PROJECT_NAME
chmod -R 755 $PROJECT_DIR

print_status "Step 9: Starting services..."
systemctl start $PROJECT_NAME.socket
systemctl enable $PROJECT_NAME.socket
systemctl start $PROJECT_NAME
systemctl enable $PROJECT_NAME
systemctl restart nginx

print_status "Step 10: Checking service status..."
systemctl status $PROJECT_NAME --no-pager

echo ""
echo "========================================="
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "========================================="
echo ""
echo "Service status:"
systemctl is-active $PROJECT_NAME && echo -e "${GREEN}✓${NC} Gunicorn is running" || echo -e "${RED}✗${NC} Gunicorn is not running"
systemctl is-active nginx && echo -e "${GREEN}✓${NC} Nginx is running" || echo -e "${RED}✗${NC} Nginx is not running"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u $PROJECT_NAME -f"
echo "  - Restart service: sudo systemctl restart $PROJECT_NAME"
echo "  - Restart Nginx: sudo systemctl restart nginx"
echo "  - Check status: sudo systemctl status $PROJECT_NAME"
echo ""
