@echo off
setlocal enabledelayedexpansion

REM Outlook Event Manager - Complete Workflow
REM Batch Script for Managing Vedic Calendar Events in Outlook
REM 
REM This script performs three main operations:
REM 1. Creates cancellation events for existing events in Outlook
REM 2. Makes all events private in the ICS files
REM 3. Provides import instructions for Windows Outlook

set "INPUT_DIR=VedicCalendarParser\input_ics_files\invites"
set "OUTPUT_DIR=output_ics_files\cancellations"
set "SKIP_CANCELLATIONS=false"
set "SKIP_PRIVATE=false"

echo ========================================
echo    Outlook Event Manager
echo    Complete Workflow Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check 'Add Python to PATH' during installation
    pause
    exit /b 1
)

REM Check if icalendar package is installed
python -c "import icalendar" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: icalendar package not installed
    echo Please install it with: pip install icalendar
    pause
    exit /b 1
)

echo ✓ Python and required packages found
echo.

REM Create output directory if it doesn't exist
if not exist "%OUTPUT_DIR%" (
    echo Creating output directory: %OUTPUT_DIR%
    mkdir "%OUTPUT_DIR%" 2>nul
)

echo Current settings:
echo   Input directory: %INPUT_DIR%
echo   Output directory: %OUTPUT_DIR%
echo   Skip cancellations: %SKIP_CANCELLATIONS%
echo   Skip private update: %SKIP_PRIVATE%
echo.

REM Check if input directory exists and has ICS files
if not exist "%INPUT_DIR%\*.ics" (
    echo No ICS files found in %INPUT_DIR%
    echo Please ensure the invites folder exists and contains ICS files
    pause
    exit /b 1
)

REM Count ICS files
set "FILE_COUNT=0"
for %%f in ("%INPUT_DIR%\*.ics") do set /a FILE_COUNT+=1

echo Found %FILE_COUNT% ICS file(s) in %INPUT_DIR%
echo.
echo Files to process:
for %%f in ("%INPUT_DIR%\*.ics") do echo   - %%~nxf
echo.

:MAIN_MENU
echo Choose an option:
echo 1. Run complete workflow (all 3 steps)
echo 2. Step 1 only: Create cancellation events
echo 3. Step 2 only: Make events private
echo 4. Step 3 only: Show import instructions
echo 5. Exit
echo.
set /p "CHOICE=Enter your choice (1-5): "

if "%CHOICE%"=="1" goto COMPLETE_WORKFLOW
if "%CHOICE%"=="2" goto STEP1_CANCELLATIONS
if "%CHOICE%"=="3" goto STEP2_PRIVATE
if "%CHOICE%"=="4" goto STEP3_INSTRUCTIONS
if "%CHOICE%"=="5" goto EXIT
echo Invalid choice. Please try again.
echo.
goto MAIN_MENU

:COMPLETE_WORKFLOW
call :STEP1_CANCELLATIONS
if errorlevel 1 (
    echo Some steps failed. Check the output above.
    goto CONTINUE_PROMPT
)
call :STEP2_PRIVATE
if errorlevel 1 (
    echo Some steps failed. Check the output above.
    goto CONTINUE_PROMPT
)
call :STEP3_INSTRUCTIONS
goto CONTINUE_PROMPT

:STEP1_CANCELLATIONS
echo ========================================
echo STEP 1: Creating Cancellation Events
echo ========================================
echo.

if "%SKIP_CANCELLATIONS%"=="true" (
    echo Skipping cancellation creation (SKIP_CANCELLATIONS=true)
    goto :eof
)

echo Creating cancellation events for existing events...

REM Create temporary Python script for cancellations
(
echo #!/usr/bin/env python3
echo import os
echo import sys
echo from pathlib import Path
echo from icalendar import Calendar, Event
echo import logging
echo.
echo logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s'^)
echo logger = logging.getLogger(__name__^)
echo.
echo def create_cancellation_calendar(original_calendar, filename^):
echo     cancellation_calendar = Calendar(^)
echo     cancellation_calendar.add('prodid', '-//Calendar Cancellation Generator//EN'^)
echo     cancellation_calendar.add('version', '2.0'^)
echo     cancellation_calendar.add('calscale', 'GREGORIAN'^)
echo     cancellation_calendar.add('method', 'CANCEL'^)
echo.    
echo     for component in original_calendar.walk(^):
echo         if component.name == "VEVENT":
echo             cancel_event = Event(^)
echo.            
echo             uid = component.get('uid'^)
echo             if uid:
echo                 cancel_event.add('uid', uid^)
echo.            
echo             dtstart = component.get('dtstart'^)
echo             if dtstart:
echo                 cancel_event.add('dtstart', dtstart^)
echo.            
echo             dtend = component.get('dtend'^)
echo             if dtend:
echo                 cancel_event.add('dtend', dtend^)
echo.            
echo             summary = component.get('summary'^)
echo             if summary:
echo                 cancel_event.add('summary', summary^)
echo.            
echo             sequence = component.get('sequence', 0^)
echo             cancel_event.add('sequence', sequence^)
echo.            
echo             organizer = component.get('organizer'^)
echo             if organizer:
echo                 cancel_event.add('organizer', organizer^)
echo.            
echo             attendees = component.get('attendee'^)
echo             if attendees:
echo                 if isinstance(attendees, list^):
echo                     for attendee in attendees:
echo                         cancel_event.add('attendee', attendee^)
echo                 else:
echo                     cancel_event.add('attendee', attendees^)
echo.            
echo             cancel_event.add('status', 'CANCELLED'^)
echo             cancel_event.add('class', 'PRIVATE'^)
echo.            
echo             cancellation_calendar.add_component(cancel_event^)
echo             logger.info(f"Created cancellation for event: {summary} (UID: {uid}^)"^)
echo.    
echo     return cancellation_calendar
echo.
echo def process_ics_file(input_file, output_dir^):
echo     try:
echo         logger.info(f"Processing: {input_file}"^)
echo.        
echo         with open(input_file, 'rb'^) as file:
echo             original_calendar = Calendar.from_ical(file.read(^)^)
echo.        
echo         filename = Path(input_file^).stem
echo         cancellation_calendar = create_cancellation_calendar(original_calendar, filename^)
echo.        
echo         output_filename = f"{filename}_cancellations.ics"
echo         output_path = Path(output_dir^) / output_filename
echo.        
echo         with open(output_path, 'wb'^) as file:
echo             file.write(cancellation_calendar.to_ical(^)^)
echo.        
echo         logger.info(f"Created cancellation file: {output_path}"^)
echo         return True
echo.        
echo     except Exception as e:
echo         logger.error(f"Error processing {input_file}: {e}"^)
echo         return False
echo.
echo def main(^):
echo     input_dir = Path("%INPUT_DIR%"^)
echo     output_dir = Path("%OUTPUT_DIR%"^)
echo.    
echo     if not input_dir.exists(^):
echo         logger.error(f"Input directory not found: {input_dir}"^)
echo         return False
echo.    
echo     output_dir.mkdir(parents=True, exist_ok=True^)
echo     ics_files = list(input_dir.glob("*.ics"^)^)
echo.    
echo     if not ics_files:
echo         logger.warning(f"No ICS files found in {input_dir}"^)
echo         return False
echo.    
echo     logger.info(f"Found {len(ics_files^)} ICS file(s^) to process"^)
echo.    
echo     successful_files = 0
echo     for ics_file in ics_files:
echo         if process_ics_file(ics_file, output_dir^):
echo             successful_files += 1
echo.    
echo     logger.info(f"Successfully processed {successful_files}/{len(ics_files^)} files"^)
echo     return successful_files ^> 0
echo.
echo if __name__ == "__main__":
echo     success = main(^)
echo     sys.exit(0 if success else 1^)
) > temp_cancellation_script.py

python temp_cancellation_script.py
if errorlevel 1 (
    echo ❌ Failed to create cancellation events
    del temp_cancellation_script.py 2>nul
    exit /b 1
) else (
    echo ✓ Cancellation events created successfully
    del temp_cancellation_script.py 2>nul
)
goto :eof

:STEP2_PRIVATE
echo ========================================
echo STEP 2: Making Events Private
echo ========================================
echo.

if "%SKIP_PRIVATE%"=="true" (
    echo Skipping private update (SKIP_PRIVATE=true)
    goto :eof
)

echo Making all events private...

REM Create temporary Python script for making events private
(
echo #!/usr/bin/env python3
echo import os
echo import sys
echo from pathlib import Path
echo from icalendar import Calendar
echo import logging
echo.
echo logging.basicConfig(level=logging.INFO, format='%%(asctime)s - %%(levelname)s - %%(message)s'^)
echo logger = logging.getLogger(__name__^)
echo.
echo def make_events_private(ics_file^):
echo     try:
echo         logger.info(f"Processing: {ics_file}"^)
echo.        
echo         with open(ics_file, 'rb'^) as file:
echo             calendar = Calendar.from_ical(file.read(^)^)
echo.        
echo         event_count = 0
echo         private_count = 0
echo.        
echo         for component in calendar.walk(^):
echo             if component.name == "VEVENT":
echo                 event_count += 1
echo                 summary = component.get('summary', 'Unknown Event'^)
echo.                
echo                 if component.get('class'^) == 'PRIVATE':
echo                     logger.info(f"  Event already private: {summary}"^)
echo                     private_count += 1
echo                 else:
echo                     component.add('class', 'PRIVATE'^)
echo                     logger.info(f"  Made event private: {summary}"^)
echo                     private_count += 1
echo.        
echo         with open(ics_file, 'wb'^) as file:
echo             file.write(calendar.to_ical(^)^)
echo.        
echo         logger.info(f"  Updated {event_count} events, {private_count} are now private"^)
echo         return True
echo.        
echo     except Exception as e:
echo         logger.error(f"Error processing {ics_file}: {e}"^)
echo         return False
echo.
echo def main(^):
echo     input_dir = Path("%INPUT_DIR%"^)
echo.    
echo     if not input_dir.exists(^):
echo         logger.error(f"Input directory not found: {input_dir}"^)
echo         return False
echo.    
echo     ics_files = list(input_dir.glob("*.ics"^)^)
echo.    
echo     if not ics_files:
echo         logger.warning(f"No ICS files found in {input_dir}"^)
echo         return False
echo.    
echo     logger.info(f"Found {len(ics_files^)} ICS file(s^) to process"^)
echo.    
echo     successful_files = 0
echo     for ics_file in ics_files:
echo         if make_events_private(ics_file^):
echo             successful_files += 1
echo.    
echo     logger.info(f"Successfully processed {successful_files}/{len(ics_files^)} files"^)
echo     return successful_files ^> 0
echo.
echo if __name__ == "__main__":
echo     success = main(^)
echo     sys.exit(0 if success else 1^)
) > temp_private_script.py

python temp_private_script.py
if errorlevel 1 (
    echo ❌ Failed to make events private
    del temp_private_script.py 2>nul
    exit /b 1
) else (
    echo ✓ Events made private successfully
    del temp_private_script.py 2>nul
)
goto :eof

:STEP3_INSTRUCTIONS
echo ========================================
echo STEP 3: Import Instructions
echo ========================================
echo.

REM Show cancellation files
set "CANCELLATION_COUNT=0"
for %%f in ("%OUTPUT_DIR%\*_cancellations.ics") do set /a CANCELLATION_COUNT+=1

if %CANCELLATION_COUNT% gtr 0 (
    echo Cancellation files created:
    for %%f in ("%OUTPUT_DIR%\*_cancellations.ics") do echo   - %%~nxf
    echo.
)

REM Show updated files
set "UPDATED_COUNT=0"
for %%f in ("%INPUT_DIR%\*.ics") do set /a UPDATED_COUNT+=1

if %UPDATED_COUNT% gtr 0 (
    echo Updated private files:
    for %%f in ("%INPUT_DIR%\*.ics") do echo   - %%~nxf
    echo.
)

echo ========================================
echo     WINDOWS OUTLOOK IMPORT INSTRUCTIONS
echo ========================================
echo.

if %CANCELLATION_COUNT% gtr 0 (
    echo STEP 1: Remove Existing Events (if any exist in Outlook)
    echo 1. Open Outlook
    echo 2. Go to File → Open ^& Export → Import/Export
    echo 3. Choose 'Import an iCalendar (.ics) file'
    echo 4. Select the cancellation files from: %OUTPUT_DIR%
    echo 5. Choose your calendar and import
    echo 6. This will remove any existing events with matching UIDs
    echo.
)

echo STEP 2: Import Private Events
echo 1. In Outlook, go to File → Open ^& Export → Import/Export
echo 2. Choose 'Import an iCalendar (.ics) file'
echo 3. Select the updated private files from: %INPUT_DIR%
echo 4. Choose your calendar and import
echo 5. All events will now be marked as PRIVATE
echo.

echo ========================================
echo     ALTERNATIVE: Batch Import
echo ========================================
echo.

echo If you want to import all files at once:
echo 1. Select multiple .ics files in File Explorer
echo 2. Right-click → 'Open with' → Outlook
echo 3. Outlook will import all selected files
echo.

echo ========================================
echo     TROUBLESHOOTING
echo ========================================
echo.

echo If import fails:
echo - Try importing one file at a time
echo - Check if events already exist with same UIDs
echo - Try the cancellation files first, then the private files
echo - Some calendar apps may not support all ICS features
goto :eof

:CONTINUE_PROMPT
echo.
set /p "CONTINUE=Press Enter to continue or 'q' to quit: "
if /i "%CONTINUE%"=="q" goto EXIT
goto MAIN_MENU

:EXIT
echo.
echo Thank you for using Outlook Event Manager!
echo.
pause
exit /b 0 