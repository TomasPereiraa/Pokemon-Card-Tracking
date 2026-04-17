@echo off
setlocal enabledelayedexpansion
title Pokemon Card Price Tracker

set "CSV_FILE=%~1"

if "!CSV_FILE!"=="" (
    echo.
    echo  No file provided. Opening file picker...
    echo.
    for /f "usebackq delims=" %%f in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.OpenFileDialog; $d.Filter = 'CSV Files (*.csv)|*.csv|All Files (*.*)|*.*'; $d.Title = 'Select your Pokemon cards CSV file'; $d.InitialDirectory = [Environment]::GetFolderPath('Desktop'); if ($d.ShowDialog() -eq 'OK') { $d.FileName }"`) do set "CSV_FILE=%%f"

    if "!CSV_FILE!"=="" (
        echo  No file selected. Exiting.
        echo.
        pause
        exit /b 0
    )
)

echo.
echo  Running scraper for: !CSV_FILE!
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0main.py" "!CSV_FILE!"

echo.
if errorlevel 1 (
    echo  Something went wrong. Check the error above.
) else (
    echo  All done!
)
echo.
pause
