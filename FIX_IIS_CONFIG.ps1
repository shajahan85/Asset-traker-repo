# ============================================
# Fix IIS Configuration for Asset Tracker
# Run as Administrator!
# ============================================

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "===== Fixing IIS Configuration =====" -ForegroundColor Cyan
Write-Host ""

$projectPath = "E:\Asset-tracker tool"
$pythonExe = "$projectPath\venv\Scripts\python.exe"
$wfastcgiPy = "$projectPath\venv\Lib\site-packages\wfastcgi.py"

# Verify paths exist
Write-Host "Verifying paths..." -ForegroundColor Yellow

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Python executable not found at: $pythonExe" -ForegroundColor Red
    Write-Host "Make sure virtual environment is created!" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $wfastcgiPy)) {
    Write-Host "ERROR: wfastcgi.py not found at: $wfastcgiPy" -ForegroundColor Red
    Write-Host "Run: pip install wfastcgi" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Python executable found" -ForegroundColor Green
Write-Host "✓ wfastcgi.py found" -ForegroundColor Green
Write-Host ""

# Configure FastCGI Application
Write-Host "Configuring FastCGI application..." -ForegroundColor Yellow

$fastCgiPath = "$pythonExe|$wfastcgiPy"

# Remove existing FastCGI configuration if exists
& "C:\Windows\system32\inetsrv\appcmd.exe" set config /section:system.webServer/fastCGI `
    "/-[fullPath='$pythonExe']" 2>$null

# Add FastCGI application
& "C:\Windows\system32\inetsrv\appcmd.exe" set config /section:system.webServer/fastCGI `
    "/+[fullPath='$pythonExe',arguments='$wfastcgiPy',signalBeforeTerminateSeconds='30']"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ FastCGI application configured" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to configure FastCGI application" -ForegroundColor Red
    Write-Host "Error code: $LASTEXITCODE" -ForegroundColor Red
}

# Add environment variables to FastCGI
Write-Host "Adding environment variables..." -ForegroundColor Yellow

& "C:\Windows\system32\inetsrv\appcmd.exe" set config /section:system.webServer/fastCGI `
    "/+[fullPath='$pythonExe'].environmentVariables.[name='PYTHONPATH',value='$projectPath']"

& "C:\Windows\system32\inetsrv\appcmd.exe" set config /section:system.webServer/fastCGI `
    "/+[fullPath='$pythonExe'].environmentVariables.[name='DJANGO_SETTINGS_MODULE',value='asset_tracker.settings']"

& "C:\Windows\system32\inetsrv\appcmd.exe" set config /section:system.webServer/fastCGI `
    "/+[fullPath='$pythonExe'].environmentVariables.[name='WSGI_HANDLER',value='asset_tracker.wsgi.application']"

Write-Host "✓ Environment variables added" -ForegroundColor Green
Write-Host ""

# Verify web.config exists
Write-Host "Checking web.config..." -ForegroundColor Yellow

if (Test-Path "$projectPath\web.config") {
    Write-Host "✓ web.config found" -ForegroundColor Green
} else {
    Write-Host "✗ web.config not found!" -ForegroundColor Red
    Write-Host "Copy web.config to: $projectPath" -ForegroundColor Yellow
}

Write-Host ""

# Print handler mapping instruction
Write-Host "===== Next Steps =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open IIS Manager (inetmgr)" -ForegroundColor White
Write-Host "2. Go to your AssetTracker site" -ForegroundColor White
Write-Host "3. Double-click 'Handler Mappings'" -ForegroundColor White
Write-Host "4. Click 'Add Module Mapping'" -ForegroundColor White
Write-Host "5. Fill in:" -ForegroundColor White
Write-Host "   - Request path: *" -ForegroundColor Gray
Write-Host "   - Module: FastCgiModule" -ForegroundColor Gray
Write-Host "   - Executable: $fastCgiPath" -ForegroundColor Yellow
Write-Host "   - Name: Django Handler" -ForegroundColor Gray
Write-Host "   - UNCHECK 'Invoke handler only if request is mapped to'" -ForegroundColor Gray
Write-Host "6. Click OK → Yes" -ForegroundColor White
Write-Host ""
Write-Host "Or copy this path for the Executable:" -ForegroundColor Cyan
Write-Host $fastCgiPath -ForegroundColor Yellow
Write-Host ""
Write-Host "7. Restart IIS:" -ForegroundColor White
Write-Host "   iisreset /restart" -ForegroundColor Yellow
Write-Host ""
Write-Host "8. Test:" -ForegroundColor White
Write-Host "   http://192.168.10.29:8081/" -ForegroundColor Yellow
Write-Host ""
