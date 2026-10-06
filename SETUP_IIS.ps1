# ============================================
# Asset Tracker - IIS Setup Script
# Server: 192.168.10.29:8081
# Location: E:\Asset-tracker tool
# ============================================
# This script sets up your Django application for IIS
#

Write-Host "===== Asset Tracker IIS Setup =====" -ForegroundColor Cyan
Write-Host "Server: 192.168.10.29:8081" -ForegroundColor White
Write-Host "Location: E:\Asset-tracker tool" -ForegroundColor White
Write-Host ""

# Get Python path
$pythonPath = (Get-Command python).Path
Write-Host "Found Python at: $pythonPath" -ForegroundColor Green

# Navigate to project directory
$projectPath = "E:\Asset-tracker tool"
Set-Location $projectPath

# Step 1: Create virtual environment
Write-Host ""
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "Virtual environment created!" -ForegroundColor Green
}

# Step 2: Activate virtual environment and install packages
Write-Host ""
Write-Host "Step 2: Installing packages..." -ForegroundColor Yellow
& "$projectPath\venv\Scripts\python.exe" -m pip install --upgrade pip
& "$projectPath\venv\Scripts\python.exe" -m pip install -r requirements.txt
& "$projectPath\venv\Scripts\python.exe" -m pip install wfastcgi

Write-Host "Packages installed!" -ForegroundColor Green

# Step 3: Enable wfastcgi
Write-Host ""
Write-Host "Step 3: Enabling wfastcgi..." -ForegroundColor Yellow
$wfastcgiOutput = & "$projectPath\venv\Scripts\wfastcgi-enable.exe"
Write-Host "wfastcgi enabled!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Copy this scriptProcessor path:" -ForegroundColor Red
Write-Host $wfastcgiOutput -ForegroundColor Cyan

# Step 4: Get paths for web.config
$venvPython = "$projectPath\venv\Scripts\python.exe"
$wfastcgiPath = & "$projectPath\venv\Scripts\python.exe" -c "import wfastcgi; print(wfastcgi.__file__)"

Write-Host ""
Write-Host "===== Configuration Paths =====" -ForegroundColor Cyan
Write-Host "Python Path: $venvPython" -ForegroundColor White
Write-Host "wfastcgi Path: $wfastcgiPath" -ForegroundColor White
Write-Host "Project Path: $projectPath" -ForegroundColor White

# Step 5: Update web.config
Write-Host ""
Write-Host "Step 4: Updating web.config..." -ForegroundColor Yellow

$webConfigPath = "$projectPath\web.config"
$webConfigContent = Get-Content $webConfigPath -Raw

# Replace Python paths in web.config
$webConfigContent = $webConfigContent -replace 'C:\\Python312\\python\.exe', $venvPython
$webConfigContent = $webConfigContent -replace 'C:\\Python312\\Lib\\site-packages\\wfastcgi\.py', $wfastcgiPath
$webConfigContent = $webConfigContent -replace 'D:\\Asset tracker', $projectPath

Set-Content -Path $webConfigPath -Value $webConfigContent

Write-Host "web.config updated!" -ForegroundColor Green

# Step 6: Run Django setup commands
Write-Host ""
Write-Host "Step 5: Running Django setup..." -ForegroundColor Yellow

# Collect static files
Write-Host "Collecting static files..."
& "$projectPath\venv\Scripts\python.exe" manage.py collectstatic --noinput

# Run migrations
Write-Host "Running database migrations..."
& "$projectPath\venv\Scripts\python.exe" manage.py migrate

Write-Host "Django setup complete!" -ForegroundColor Green

# Step 7: Set folder permissions
Write-Host ""
Write-Host "Step 6: Setting folder permissions..." -ForegroundColor Yellow

icacls "$projectPath" /grant "IIS_IUSRS:(OI)(CI)F" /T /Q
icacls "$projectPath\media" /grant "IIS_IUSRS:(OI)(CI)F" /T /Q 2>$null
icacls "$projectPath\staticfiles" /grant "IIS_IUSRS:(OI)(CI)F" /T /Q 2>$null

Write-Host "Permissions set!" -ForegroundColor Green

# Final instructions
Write-Host ""
Write-Host "===== Setup Complete! =====" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Open IIS Manager (inetmgr)"
Write-Host "2. Create Application Pool: AssetTrackerPool"
Write-Host "3. Set .NET CLR Version: No Managed Code"
Write-Host "4. Create Website pointing to: $projectPath"
Write-Host "5. Assign Application Pool: AssetTrackerPool"
Write-Host "6. Restart IIS: iisreset /restart"
Write-Host ""
Write-Host "Then access: http://192.168.10.29:8081/" -ForegroundColor Cyan
Write-Host ""
