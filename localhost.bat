@echo off

:: Parse args
set "only="

:parse_args
if "%1"=="-only" (set "only=%2" & shift & shift & goto parse_args)
if not "%1"=="" (echo Unknown argument: %1 & exit /b 1)

if defined only (
    if not "%only%"=="frontend" if not "%only%"=="backend" (
        echo Invalid value for -only: %only% (must be 'frontend' or 'backend'^)
        exit /b 1
    )
)

:: Check for .env file
set "env=%~dp0local.env"
if not exist "%env%" (
    echo local.env file not found at %env%, make sure you download it from https://drive.google.com/file/d/1rV0AyDjZbgwemqVbJXlSNMSvqooPO2tW/view?usp=sharing and place it in project directory
    exit /b 1
)

if "%only%"=="" (
    call :launch frontend
    call :launch backend
) else (
    call :launch %only%
)
exit /b 0

:launch
set "name=%1"
start "%name%" powershell -NoExit -Command "& '%~dp0scripts\%name%-localhost.bat'"
exit /b 0
