@echo off

:: Find npm
where npm >nul 2>&1
if errorlevel 1 (echo 'npm' not found & exit /b 1)

:: Find /frontend
set "frontend=%~dp0..\frontend"
if not exist "%frontend%" (
    echo Frontend folder not found at %frontend%
    exit /b 1
)

:: Move to frontend directory
cd /d "%frontend%"

:: Install dependencies and run frontend
echo Installing dependencies...
npm install & npm audit fix & echo. & echo Hosting frontend locally... & npm run dev
