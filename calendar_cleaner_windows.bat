@echo off
setlocal enabledelayedexpansion

:: Calendar Cleaner for Windows - Vedic Calendar Event Remover
:: This script removes VAR and DUS events from ICS files

echo ========================================
echo    Vedic Calendar Event Cleaner
echo    Windows Batch Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

:: Check if the calendar_invite_remover.py script exists
if not exist "calendar_invite_remover.py" (
    echo ERROR: calendar_invite_remover.py not found in current directory
    echo Please ensure the script is in the same folder as this batch file
    pause
    exit /b 1
)

:: Set default directories
set "INPUT_DIR=input_ics_files"
set "OUTPUT_DIR=output_ics_files"

:: Create directories if they don't exist
if not exist "%INPUT_DIR%" (
    echo Creating input directory: %INPUT_DIR%
    mkdir "%INPUT_DIR%"
)

if not exist "%OUTPUT_DIR%" (
    echo Creating output directory: %OUTPUT_DIR%
    mkdir "%OUTPUT_DIR%"
)

echo.
echo Current settings:
echo   Input directory: %INPUT_DIR%
echo   Output directory: %OUTPUT_DIR%
echo.

:: Check if there are ICS files in input directory
set "ICS_COUNT=0"
for %%f in ("%INPUT_DIR%\*.ics") do set /a ICS_COUNT+=1

if %ICS_COUNT%==0 (
    echo No ICS files found in %INPUT_DIR%
    echo Please place your ICS files in the %INPUT_DIR% folder
    echo.
    pause
    exit /b 1
)

echo Found %ICS_COUNT% ICS file(s) in %INPUT_DIR%
echo.

:: Show available files
echo Available ICS files:
for %%f in ("%INPUT_DIR%\*.ics") do echo   - %%~nxf
echo.

:: Ask user for action
echo Choose an option:
echo 1. Process all ICS files in %INPUT_DIR%
echo 2. Process a specific file
echo 3. Exit
echo.
set /p "choice=Enter your choice (1-3): "

if "%choice%"=="1" goto :process_all
if "%choice%"=="2" goto :process_specific
if "%choice%"=="3" goto :exit
echo Invalid choice. Please try again.
goto :menu

:process_all
echo.
echo Processing all ICS files...
echo.

for %%f in ("%INPUT_DIR%\*.ics") do (
    echo Processing: %%~nxf
    call :process_file "%%f"
    echo.
)
goto :summary

:process_specific
echo.
echo Available files:
set "file_num=1"
for %%f in ("%INPUT_DIR%\*.ics") do (
    echo !file_num!. %%~nxf
    set "file_!file_num!=%%f"
    set /a file_num+=1
)
echo.
set /p "file_choice=Enter file number: "

set "selected_file=!file_%file_choice%!"
if not defined selected_file (
    echo Invalid file number.
    goto :process_specific
)

echo.
echo Processing: %~nx1!selected_file!
call :process_file "!selected_file!"
goto :summary

:process_file
set "input_file=%~1"
set "filename=%~n1"
set "output_file=%OUTPUT_DIR%\%filename%_cleaned.ics"

echo   Input: %input_file%
echo   Output: %output_file%

:: Step 1: Remove VAR events
echo   Step 1: Removing VAR events...
python calendar_invite_remover.py "%input_file%" --pattern "VAR" --start-date 2025-07-01 --end-date 2025-12-31
if errorlevel 1 (
    echo   ERROR: Failed to remove VAR events
    goto :error
)

:: Step 2: Remove DUS events from the cleaned file
echo   Step 2: Removing DUS events...
python calendar_invite_remover.py "%output_file%" --pattern "DUS" --start-date 2025-07-01 --end-date 2025-12-31
if errorlevel 1 (
    echo   ERROR: Failed to remove DUS events
    goto :error
)

echo   SUCCESS: File processed successfully
goto :eof

:error
echo   ERROR: Processing failed for %input_file%
goto :eof

:summary
echo.
echo ========================================
echo    Processing Complete
echo ========================================
echo.
echo Output files created in %OUTPUT_DIR%:
for %%f in ("%OUTPUT_DIR%\*_cleaned_cleaned.ics") do echo   - %%~nxf
echo.
echo Cancellation files for import:
for %%f in ("%OUTPUT_DIR%\*_cleaned_cleaned_cancellations.ics") do echo   - %%~nxf
echo.

:: Instructions for different platforms
echo ========================================
echo    Import Instructions
echo ========================================
echo.
echo For Windows Outlook:
echo 1. Open Outlook
echo 2. Go to File ^> Open ^& Export ^> Import/Export
echo 3. Choose "Import an iCalendar (.ics) file"
echo 4. Select the cancellation file: *_cleaned_cleaned_cancellations.ics
echo 5. Choose your calendar and import
echo.
echo For macOS Calendar:
echo 1. Double-click the cancellation file
echo 2. If import fails, use the cleaned file instead
echo 3. Or create a new calendar and import the cleaned file
echo.
echo For Google Calendar:
echo 1. Go to Settings ^> Import ^& Export
echo 2. Upload the cancellation file
echo 3. Choose your calendar and import
echo.

:menu
echo.
echo Choose an option:
echo 1. Process all ICS files again
echo 2. Process a specific file
echo 3. Exit
echo.
set /p "choice=Enter your choice (1-3): "

if "%choice%"=="1" goto :process_all
if "%choice%"=="2" goto :process_specific
if "%choice%"=="3" goto :exit
echo Invalid choice. Please try again.
goto :menu

:exit
echo.
echo Thank you for using Vedic Calendar Event Cleaner!
echo.
pause
exit /b 0 