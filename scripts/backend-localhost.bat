@echo off

:: Find pip.exe
set "pip="
where pip >nul 2>&1
if errorlevel 1 (echo 'pip' not found & exit /b 1)
for /f "tokens=*" %%i in ('where pip') do set "pip=%%i"
echo Found pip.exe at %pip%

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

:: Upgrade pip
echo Upgrading pip...
"%python%" -m pip install --upgrade pip

:: Find requirements.txt
set "requirements=%backend%\requirements.txt"
if not exist "%requirements%" (
    echo requirements.txt not found at %requirements%
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
"%pip%" install -r "%requirements%"

:: Find main.py
set "main=%backend%\main.py"
if not exist "%main%" (
    echo main.py not found at %main%
    exit /b 1
)

:: Run main backend script
echo Hosting backend locally...
echo.
"%python%" "%main%" --local
