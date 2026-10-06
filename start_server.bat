@echo off
echo ========================================
echo Asset Tracker Server Startup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    echo.
    
    REM Add firewall rule
    echo Adding Windows Firewall rule for port 8000...
    netsh advfirewall firewall delete rule name="Django Asset Tracker" >nul 2>&1
    netsh advfirewall firewall add rule name="Django Asset Tracker" dir=in action=allow protocol=TCP localport=8000
    echo Firewall rule added successfully!
    echo.
) else (
    echo WARNING: Not running as Administrator!
    echo Firewall rule cannot be added automatically.
    echo Please run this file as Administrator for full functionality.
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

REM Get IP address
echo Detecting IP address...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr "192.168"') do (
    set IP=%%a
    set IP=!IP:~1!
)
echo Server IP: %IP%
echo.

REM Start Django server
echo Starting Django development server...
echo Server will be accessible at:
echo   - Local: http://localhost:8000
echo   - Network: http://%IP%:8000
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000
