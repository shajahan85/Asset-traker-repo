# Asset Tracker - Quick Test Server Deployment Script
# Run this script on your test server as Administrator

param(
    [string]$ServerIP = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Asset Tracker Test Server Deployment Script

Usage:
    .\deploy_test_server.ps1 [-ServerIP <ip>] [-Port <port>]

Parameters:
    -ServerIP    IP address to bind to (default: 0.0.0.0 for all interfaces)
    -Port        Port number to run on (default: 8000)
    -Help        Show this help message

Examples:
    .\deploy_test_server.ps1
    .\deploy_test_server.ps1 -ServerIP 192.168.1.100 -Port 8080
"@
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Asset Tracker - Test Server Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "WARNING: Not running as Administrator. Some steps may fail." -ForegroundColor Yellow
    Write-Host "Press any key to continue or Ctrl+C to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Step 1: Check Python installation
Write-Host "[1/10] Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.11+ first." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check if virtual environment exists
Write-Host "[2/10] Setting up virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Gray
} else {
    Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Gray
}

# Step 3: Activate virtual environment
Write-Host "[3/10] Activating virtual environment..." -ForegroundColor Green
$activateScript = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    try {
        & $activateScript
        Write-Host "  ✓ Virtual environment activated" -ForegroundColor Gray
    } catch {
        Write-Host "  Note: If you see execution policy errors, run:" -ForegroundColor Yellow
        Write-Host "    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Activation script not found" -ForegroundColor Red
    exit 1
}

# Step 4: Upgrade pip
Write-Host "[4/10] Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet
Write-Host "  ✓ pip upgraded" -ForegroundColor Gray

# Step 5: Install dependencies
Write-Host "[5/10] Installing dependencies (this may take a few minutes)..." -ForegroundColor Green
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Dependencies installed" -ForegroundColor Gray

# Step 6: Check for .env file
Write-Host "[6/10] Checking environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Write-Host "  Creating .env file from template..." -ForegroundColor Gray
    
    # Generate secret key
    $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
    
    $envContent = @"
# Django Settings
SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,$ServerIP

# Database (SQLite for testing)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Session Settings
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Security Settings
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery Settings
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  ✓ .env file created" -ForegroundColor Gray
} else {
    Write-Host "  ✓ .env file already exists" -ForegroundColor Gray
}

# Step 7: Create directories
Write-Host "[7/10] Creating media directories..." -ForegroundColor Green
$directories = @(
    "media\asset_attachments",
    "media\templates",
    "staticfiles",
    "logs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}
Write-Host "  ✓ Directories created" -ForegroundColor Gray

# Step 8: Apply database migrations
Write-Host "[8/10] Applying database migrations..." -ForegroundColor Green
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to apply migrations" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ Migrations applied" -ForegroundColor Gray

# Step 9: Collect static files
Write-Host "[9/10] Collecting static files..." -ForegroundColor Green
python manage.py collectstatic --noinput --clear
Write-Host "  ✓ Static files collected" -ForegroundColor Gray

# Step 10: Configure firewall
Write-Host "[10/10] Configuring Windows Firewall..." -ForegroundColor Green
try {
    $ruleName = "Django Test Server - Port $Port"
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    if ($null -eq $existingRule) {
        New-NetFirewallRule -DisplayName $ruleName `
                            -Direction Inbound `
                            -LocalPort $Port `
                            -Protocol TCP `
                            -Action Allow `
                            -ErrorAction Stop | Out-Null
        Write-Host "  ✓ Firewall rule created for port $Port" -ForegroundColor Gray
    } else {
        Write-Host "  ✓ Firewall rule already exists" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ! Could not configure firewall (may need Admin rights)" -ForegroundColor Yellow
    Write-Host "    Manually allow port $Port in Windows Firewall" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if superuser exists
$superuserExists = python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" 2>$null

if ($superuserExists -match "True") {
    Write-Host "✓ Admin user already exists" -ForegroundColor Green
} else {
    Write-Host "⚠ No admin user found. Creating one now..." -ForegroundColor Yellow
    Write-Host ""
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "To start the test server, run:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver ${ServerIP}:${Port}" -ForegroundColor White
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  http://localhost:${Port}" -ForegroundColor White
if ($ServerIP -ne "localhost" -and $ServerIP -ne "127.0.0.1") {
    Write-Host "  http://${ServerIP}:${Port}" -ForegroundColor White
}
Write-Host ""
Write-Host "Admin panel:" -ForegroundColor Cyan
Write-Host "  http://localhost:${Port}/admin/" -ForegroundColor White
Write-Host ""

# Ask if user wants to start the server now
$response = Read-Host "Start the test server now? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting server... (Press Ctrl+C to stop)" -ForegroundColor Green
    Write-Host ""
    python manage.py runserver "${ServerIP}:${Port}"
} else {
    Write-Host ""
    Write-Host "Deployment complete. Start the server when ready." -ForegroundColor Green
}
