@echo off
echo ===================================
echo   MAUVANBAN FRONTEND SETUP
echo ===================================
echo.

echo 1. Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js and restart.
    pause
    exit /b
)

echo.
echo 2. Installing dependencies...
cd mauvanban-client
call npm install

echo.
echo 3. Starting frontend server...
echo Frontend will run at: http://localhost:3000
echo.
call npm run dev

pause
