@echo off
REM Calendar Invite Remover - Windows Batch File
REM This batch file makes it easy to run the calendar invite remover on Windows

echo ========================================
echo Calendar Invite Remover for Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import icalendar" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install icalendar
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Check if input file is provided
if "%~1"=="" (
    echo Usage: remove_calendar_invites.bat [input_file.ics] [options]
    echo.
    echo Examples:
    echo   remove_calendar_invites.bat calendar.ics
    echo   remove_calendar_invites.bat calendar.ics --remove-invites
    echo   remove_calendar_invites.bat calendar.ics --pattern "zoom^|teams"
    echo   remove_calendar_invites.bat calendar.ics --start-date 2024-01-01 --end-date 2024-01-31
    echo   remove_calendar_invites.bat calendar.ics --remove-duplicates
    echo   remove_calendar_invites.bat calendar.ics --dry-run
    echo.
    echo Options:
    echo   --remove-invites     Remove meeting/invite events
    echo   --pattern PATTERN    Remove events matching regex pattern
    echo   --start-date DATE    Start date for filtering (YYYY-MM-DD)
    echo   --end-date DATE      End date for filtering (YYYY-MM-DD)
    echo   --remove-duplicates  Remove duplicate events
    echo   --keep-categories    Keep only events with these categories
    echo   --remove-categories  Remove events with these categories
    echo   --dry-run           Show what would be removed without making changes
    echo   --verbose           Enable verbose logging
    echo.
    pause
    exit /b 1
)

REM Run the Python script with all arguments
echo Running calendar invite remover...
python calendar_invite_remover.py %*

if errorlevel 1 (
    echo.
    echo ERROR: Script failed to run successfully
    pause
    exit /b 1
)

echo.
echo Script completed successfully!
pause 