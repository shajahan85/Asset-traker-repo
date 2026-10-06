# ===========================================
# Asset Tracker - Database Backup Script
# ===========================================
#
# This script creates automated backups of the Asset Tracker database
# Schedule this with Windows Task Scheduler for regular backups
#

# Configuration
$BackupDir = "C:\AssetTracker_Backups"
$AppDir = "C:\inetpub\wwwroot\AssetTracker"
$DatabaseType = "postgresql"  # Options: postgresql, sqlite, sqlserver
$RetentionDays = 30  # Keep backups for 30 days

# PostgreSQL Configuration
$PG_USER = "asset_tracker_user"
$PG_DATABASE = "asset_tracker"
$PG_HOST = "localhost"
$PG_PORT = "5432"
# For security, use .pgpass file or environment variable for password

# Timestamp for backup file
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir\asset_tracker_$Timestamp"

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "Created backup directory: $BackupDir"
}

# Log function
function Write-Log {
    param($Message)
    $LogFile = "$BackupDir\backup_log.txt"
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    Write-Host $LogMessage
}

Write-Log "Starting database backup..."

try {
    switch ($DatabaseType) {
        "postgresql" {
            # PostgreSQL Backup using pg_dump
            Write-Log "Backing up PostgreSQL database..."
            
            $env:PGPASSWORD = $PG_PASSWORD  # Set password as environment variable
            
            $BackupFile = "$BackupFile.sql"
            
            & "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" `
                -h $PG_HOST `
                -p $PG_PORT `
                -U $PG_USER `
                -F c `
                -b `
                -v `
                -f "$BackupFile" `
                $PG_DATABASE
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "PostgreSQL backup completed successfully: $BackupFile"
                
                # Compress backup
                Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip" -Force
                Remove-Item $BackupFile -Force
                Write-Log "Backup compressed: $BackupFile.zip"
            } else {
                Write-Log "ERROR: PostgreSQL backup failed with exit code $LASTEXITCODE"
                exit 1
            }
        }
        
        "sqlite" {
            # SQLite Backup (simple file copy)
            Write-Log "Backing up SQLite database..."
            
            $SourceDB = "$AppDir\db.sqlite3"
            $BackupFile = "$BackupFile.sqlite3"
            
            if (Test-Path $SourceDB) {
                Copy-Item $SourceDB -Destination $BackupFile -Force
                
                # Compress backup
                Compress-Archive -Path $BackupFile -DestinationPath "$BackupFile.zip" -Force
                Remove-Item $BackupFile -Force
                
                Write-Log "SQLite backup completed successfully: $BackupFile.zip"
            } else {
                Write-Log "ERROR: SQLite database file not found: $SourceDB"
                exit 1
            }
        }
        
        "sqlserver" {
            # SQL Server Backup using sqlcmd
            Write-Log "Backing up SQL Server database..."
            
            $BackupFile = "$BackupFile.bak"
            $SqlQuery = @"
BACKUP DATABASE [asset_tracker] 
TO DISK = N'$BackupFile' 
WITH FORMAT, INIT, 
NAME = N'Asset Tracker Full Backup', 
SKIP, NOREWIND, NOUNLOAD, STATS = 10
"@
            
            sqlcmd -S localhost -Q $SqlQuery
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "SQL Server backup completed successfully: $BackupFile"
            } else {
                Write-Log "ERROR: SQL Server backup failed with exit code $LASTEXITCODE"
                exit 1
            }
        }
        
        default {
            Write-Log "ERROR: Unknown database type: $DatabaseType"
            exit 1
        }
    }
    
    # Backup media files
    Write-Log "Backing up media files..."
    $MediaBackup = "$BackupDir\media_$Timestamp.zip"
    $MediaDir = "$AppDir\media"
    
    if (Test-Path $MediaDir) {
        Compress-Archive -Path $MediaDir -DestinationPath $MediaBackup -Force
        Write-Log "Media files backup completed: $MediaBackup"
    }
    
    # Clean up old backups (older than retention days)
    Write-Log "Cleaning up old backups..."
    $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -File | 
        Where-Object { $_.LastWriteTime -lt $CutoffDate -and $_.Extension -in @('.zip', '.bak', '.sql') } | 
        ForEach-Object {
            Remove-Item $_.FullName -Force
            Write-Log "Deleted old backup: $($_.Name)"
        }
    
    Write-Log "Backup process completed successfully!"
    
    # Optional: Send email notification
    # Send-MailMessage -To "admin@yourdomain.com" -From "backup@yourdomain.com" `
    #     -Subject "Asset Tracker Backup Successful" `
    #     -Body "Database backup completed successfully at $(Get-Date)" `
    #     -SmtpServer "smtp.yourdomain.com"
    
    exit 0
    
} catch {
    $ErrorMessage = $_.Exception.Message
    Write-Log "ERROR: Backup failed - $ErrorMessage"
    
    # Optional: Send email notification on failure
    # Send-MailMessage -To "admin@yourdomain.com" -From "backup@yourdomain.com" `
    #     -Subject "Asset Tracker Backup FAILED" `
    #     -Body "Database backup failed: $ErrorMessage" `
    #     -SmtpServer "smtp.yourdomain.com"
    
    exit 1
}

# ===========================================
# Schedule this script with Task Scheduler:
# ===========================================
#
# schtasks /create /tn "AssetTracker_DailyBackup" /tr "powershell.exe -ExecutionPolicy Bypass -File C:\inetpub\wwwroot\AssetTracker\hosting_requirements\backup_database.ps1" /sc daily /st 02:00 /ru SYSTEM
#
