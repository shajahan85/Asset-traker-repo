#!/bin/bash

# Asset Tracker Backup Script
# Backs up database and media files

set -e

PROJECT_NAME="asset_tracker"
BACKUP_DIR="/var/backups/$PROJECT_NAME"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/var/www/$PROJECT_NAME"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting backup at $(date)"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
sudo -u postgres pg_dump asset_tracker_db | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# OR Backup MySQL database (uncomment if using MySQL)
# echo "Backing up MySQL database..."
# mysqldump -u asset_tracker_user -p asset_tracker_db | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Backup media files
echo "Backing up media files..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C "$PROJECT_DIR" media/

# Backup .env file
echo "Backing up environment variables..."
cp "$PROJECT_DIR/.env" "$BACKUP_DIR/.env_backup_$DATE"

# Remove backups older than 30 days
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name ".env_backup_*" -mtime +30 -delete

echo "Backup completed successfully at $(date)"
echo "Backup location: $BACKUP_DIR"
ls -lh $BACKUP_DIR | tail -5
