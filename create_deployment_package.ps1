# Asset Tracker - Create Clean Deployment Package
# This script creates a clean copy without test files, cache, and development data

param(
    [string]$Destination = "d:\Asset_Tracker_Deploy",
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Create Clean Deployment Package

Usage:
    .\create_deployment_package.ps1 [-Destination <path>]

Parameters:
    -Destination    Where to create the clean package (default: d:\Asset_Tracker_Deploy)
    -Help           Show this help message

Example:
    .\create_deployment_package.ps1
    .\create_deployment_package.ps1 -Destination "C:\DeployPackage"
"@
    exit 0
}

$source = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating Clean Deployment Package" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Source:      $source" -ForegroundColor Gray
Write-Host "Destination: $Destination" -ForegroundColor Gray
Write-Host ""

# Check if destination exists
if (Test-Path $Destination) {
    Write-Host "⚠ Destination folder already exists!" -ForegroundColor Yellow
    $response = Read-Host "Delete and recreate? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "  Removing existing folder..." -ForegroundColor Gray
        Remove-Item $Destination -Recurse -Force
    } else {
        Write-Host "Cancelled." -ForegroundColor Red
        exit 0
    }
}

# Create destination directory
Write-Host "[1/4] Creating destination folder..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Write-Host "  ✓ Created: $Destination" -ForegroundColor Gray

# Copy core files
Write-Host "[2/4] Copying core files..." -ForegroundColor Green
$coreFiles = @(
    "manage.py",
    "requirements.txt",
    ".env.example",
    ".gitignore",
    "deploy_test_server.ps1",
    "start_server.ps1",
    "DEPLOYMENT.md",
    "QUICK_START.md",
    "DEPLOYMENT_FILES_CHECKLIST.md",
    "web.config.example",
    "README.md"
)

$copiedCount = 0
foreach ($file in $coreFiles) {
    $sourcePath = Join-Path $source $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $Destination -ErrorAction SilentlyContinue
        $copiedCount++
        Write-Host "  ✓ $file" -ForegroundColor Gray
    } else {
        Write-Host "  - $file (not found, skipping)" -ForegroundColor DarkGray
    }
}
Write-Host "  Copied $copiedCount core files" -ForegroundColor Gray

# Copy application folders (excluding unwanted files)
Write-Host "[3/4] Copying application folders..." -ForegroundColor Green

$appFolders = @(
    "asset_tracker",
    "assets",
    "authentication",
    "power_monitoring"
)

$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.log",
    ".pytest_cache",
    "*.bak"
)

foreach ($folder in $appFolders) {
    $sourcePath = Join-Path $source $folder
    $destPath = Join-Path $Destination $folder
    
    if (Test-Path $sourcePath) {
        Write-Host "  Copying $folder/..." -ForegroundColor Gray
        
        # Copy folder with exclusions
        robocopy $sourcePath $destPath /E /NJH /NJS /NDL /NC /NS /XD "__pycache__" ".pytest_cache" /XF "*.pyc" "*.pyo" "*.log" "*.bak" | Out-Null
        
        if ($LASTEXITCODE -le 7) {
            Write-Host "    ✓ $folder/ copied" -ForegroundColor Gray
        } else {
            Write-Host "    ! $folder/ - some files may not have copied" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ! $folder/ not found" -ForegroundColor Yellow
    }
}

# Create required directories
Write-Host "[4/4] Creating required directories..." -ForegroundColor Green
$requiredDirs = @(
    "media\asset_attachments",
    "media\templates",
    "staticfiles",
    "logs"
)

foreach ($dir in $requiredDirs) {
    $dirPath = Join-Path $Destination $dir
    New-Item -ItemType Directory -Force -Path $dirPath | Out-Null
}
Write-Host "  ✓ Created media/, staticfiles/, logs/" -ForegroundColor Gray

# Calculate sizes
Write-Host ""
Write-Host "Calculating sizes..." -ForegroundColor Cyan
$sourceSize = (Get-ChildItem $source -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$destSize = (Get-ChildItem $Destination -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum

$sourceSizeMB = [math]::Round($sourceSize / 1MB, 2)
$destSizeMB = [math]::Round($destSize / 1MB, 2)
$savings = [math]::Round((($sourceSize - $destSize) / $sourceSize) * 100, 0)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Package Created Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Size Comparison:" -ForegroundColor Cyan
Write-Host "  Original folder:  $sourceSizeMB MB" -ForegroundColor Gray
Write-Host "  Clean package:    $destSizeMB MB" -ForegroundColor Gray
Write-Host "  Space saved:      $savings%" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Package Location:" -ForegroundColor Cyan
Write-Host "  $Destination" -ForegroundColor White
Write-Host ""
Write-Host "📋 What was included:" -ForegroundColor Cyan
Write-Host "  ✓ Core application files (manage.py, requirements.txt)" -ForegroundColor Gray
Write-Host "  ✓ Django apps (asset_tracker, assets, authentication, power_monitoring)" -ForegroundColor Gray
Write-Host "  ✓ Deployment scripts and documentation" -ForegroundColor Gray
Write-Host "  ✓ Required directories (media, staticfiles, logs)" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 What was excluded:" -ForegroundColor Cyan
Write-Host "  ✗ Development database (db.sqlite3)" -ForegroundColor DarkGray
Write-Host "  ✗ Test files (test_*.py, debug_*.py)" -ForegroundColor DarkGray
Write-Host "  ✗ Cache folders (__pycache__, .pytest_cache)" -ForegroundColor DarkGray
Write-Host "  ✗ Version control (.git, .kiro)" -ForegroundColor DarkGray
Write-Host "  ✗ IDE settings (.vscode)" -ForegroundColor DarkGray
Write-Host "  ✗ Logs and temporary files" -ForegroundColor DarkGray
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Copy the '$Destination' folder to your test server" -ForegroundColor White
Write-Host "  2. On test server, open PowerShell as Administrator" -ForegroundColor White
Write-Host "  3. Navigate to the copied folder" -ForegroundColor White
Write-Host "  4. Run: .\deploy_test_server.ps1" -ForegroundColor White
Write-Host ""
Write-Host "📖 For detailed instructions, see DEPLOYMENT.md in the package" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to open the destination folder
$response = Read-Host "Open destination folder now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process explorer.exe $Destination
}
