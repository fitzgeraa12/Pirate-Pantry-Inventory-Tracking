@echo off

:: Check for .env file
set "env=%~dp0.env.local"
if not exist "%env%" (
    echo local.env file not found at %env%, make sure you download it from https://drive.google.com/file/d/1rV0AyDjZbgwemqVbJXlSNMSvqooPO2tW/view?usp=sharing and place it in project directory
    exit /b 1
)

call :launch backend
call :launch frontend
exit /b 0

:launch
set "name=%1"
start "%name%" powershell -NoExit -Command "& '%~dp0scripts\%name%-localhost.bat'"
exit /b 0
