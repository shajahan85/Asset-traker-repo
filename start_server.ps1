# Asset Tracker - Start Development Server
# Simple script to start the Django development server

param(
    [string]$IP = "0.0.0.0",
    [int]$Port = 8000
)

Write-Host "Starting Asset Tracker Test Server..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
$activateScript = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run deploy_test_server.ps1 first to set up the environment." -ForegroundColor Yellow
    exit 1
}

# Get local IP for display
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object -First 1).IPAddress

Write-Host "Access URLs:" -ForegroundColor Green
Write-Host "  Local:   http://localhost:$Port" -ForegroundColor White
Write-Host "  Network: http://${localIP}:$Port" -ForegroundColor White
Write-Host ""

# Start server
python manage.py runserver "${IP}:${Port}"
