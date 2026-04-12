@echo off

:: Find python.exe
set "python="
where python >nul 2>&1
if errorlevel 1 (echo 'python' not found & exit /b 1)
for /f "tokens=*" %%i in ('where python') do set "python=%%i"
echo Found python.exe at %python%

:: Find /backend
set "backend=%~dp0..\backend"
if not exist "%backend%" (
    echo Backend folder not found at %backend%
    exit /b 1
)

:: Find requirements.txt
set "requirements=%backend%\requirements.txt"
if not exist "%requirements%" (
    echo requirements.txt not found at %requirements%
    exit /b 1
)

:: Create venv if missing
set "venv=%backend%\.venv"
if not exist "%venv%" (
    echo Creating virtual environment...
    "%python%" -m venv "%venv%"
)

:: Activate venv
call "%venv%\Scripts\activate.bat"

:: Upgrade pip and install dependencies
echo Installing dependencies...
"%venv%\Scripts\pip.exe" install -r "%requirements%"

:: Find main.py
set "main=%backend%\main.py"
if not exist "%main%" (
    echo main.py not found at %main%
    exit /b 1
)

:: Run main backend script
echo Hosting backend locally...
echo.
"%venv%\Scripts\python.exe" "%main%" --local
