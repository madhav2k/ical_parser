# Outlook Event Manager - Complete Workflow
# PowerShell Script for Managing Vedic Calendar Events in Outlook
# 
# This script performs three main operations:
# 1. Creates cancellation events for existing events in Outlook
# 2. Makes all events private in the ICS files
# 3. Provides import instructions for Windows Outlook

param(
    [string]$InputDir = "VedicCalendarParser/input_ics_files/invites",
    [string]$OutputDir = "output_ics_files/cancellations",
    [switch]$SkipCancellations = $false,
    [switch]$SkipPrivate = $false,
    [switch]$Force = $false
)

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "   Outlook Event Manager" -ForegroundColor Cyan
    Write-Host "   Complete Workflow Script" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    # Check if required Python packages are installed
    try {
        python -c "import icalendar" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "icalendar package not found"
        }
        Write-Host "✓ icalendar package found" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ ERROR: icalendar package not installed" -ForegroundColor Red
        Write-Host "Please install it with: pip install icalendar" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

function Initialize-Directories {
    # Create output directory if it doesn't exist
    if (-not (Test-Path $OutputDir)) {
        Write-Host "Creating output directory: $OutputDir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    Write-Host ""
    Write-Host "Current settings:" -ForegroundColor Cyan
    Write-Host "  Input directory: $InputDir" -ForegroundColor White
    Write-Host "  Output directory: $OutputDir" -ForegroundColor White
    Write-Host "  Skip cancellations: $SkipCancellations" -ForegroundColor White
    Write-Host "  Skip private update: $SkipPrivate" -ForegroundColor White
    Write-Host ""
}

function Get-ICSFiles {
    $icsFiles = Get-ChildItem -Path $InputDir -Filter "*.ics" -ErrorAction SilentlyContinue
    
    if ($icsFiles.Count -eq 0) {
        Write-Host "No ICS files found in $InputDir" -ForegroundColor Red
        Write-Host "Please ensure the invites folder exists and contains ICS files" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "Found $($icsFiles.Count) ICS file(s) in $InputDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "Files to process:" -ForegroundColor Cyan
    $icsFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    Write-Host ""

    return $icsFiles
}

function Step1-CreateCancellations {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 1: Creating Cancellation Events" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""

    if ($SkipCancellations) {
        Write-Host "Skipping cancellation creation (--SkipCancellations flag used)" -ForegroundColor Gray
        return $true
    }

    # Create the cancellation script content
    $cancellationScript = @'
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from icalendar import Calendar, Event
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_cancellation_calendar(original_calendar, filename):
    cancellation_calendar = Calendar()
    cancellation_calendar.add('prodid', '-//Calendar Cancellation Generator//EN')
    cancellation_calendar.add('version', '2.0')
    cancellation_calendar.add('calscale', 'GREGORIAN')
    cancellation_calendar.add('method', 'CANCEL')
    
    for component in original_calendar.walk():
        if component.name == "VEVENT":
            cancel_event = Event()
            
            uid = component.get('uid')
            if uid:
                cancel_event.add('uid', uid)
            
            dtstart = component.get('dtstart')
            if dtstart:
                cancel_event.add('dtstart', dtstart)
            
            dtend = component.get('dtend')
            if dtend:
                cancel_event.add('dtend', dtend)
            
            summary = component.get('summary')
            if summary:
                cancel_event.add('summary', summary)
            
            sequence = component.get('sequence', 0)
            cancel_event.add('sequence', sequence)
            
            organizer = component.get('organizer')
            if organizer:
                cancel_event.add('organizer', organizer)
            
            attendees = component.get('attendee')
            if attendees:
                if isinstance(attendees, list):
                    for attendee in attendees:
                        cancel_event.add('attendee', attendee)
                else:
                    cancel_event.add('attendee', attendees)
            
            cancel_event.add('status', 'CANCELLED')
            cancel_event.add('class', 'PRIVATE')
            
            cancellation_calendar.add_component(cancel_event)
            logger.info(f"Created cancellation for event: {summary} (UID: {uid})")
    
    return cancellation_calendar

def process_ics_file(input_file, output_dir):
    try:
        logger.info(f"Processing: {input_file}")
        
        with open(input_file, 'rb') as file:
            original_calendar = Calendar.from_ical(file.read())
        
        filename = Path(input_file).stem
        cancellation_calendar = create_cancellation_calendar(original_calendar, filename)
        
        output_filename = f"{filename}_cancellations.ics"
        output_path = Path(output_dir) / output_filename
        
        with open(output_path, 'wb') as file:
            file.write(cancellation_calendar.to_ical())
        
        logger.info(f"Created cancellation file: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {input_file}: {e}")
        return False

def main():
    input_dir = Path("' + $InputDir + '")
    output_dir = Path("' + $OutputDir + '")
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    output_dir.mkdir(parents=True, exist_ok=True)
    ics_files = list(input_dir.glob("*.ics"))
    
    if not ics_files:
        logger.warning(f"No ICS files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(ics_files)} ICS file(s) to process")
    
    successful_files = 0
    for ics_file in ics_files:
        if process_ics_file(ics_file, output_dir):
            successful_files += 1
    
    logger.info(f"Successfully processed {successful_files}/{len(ics_files)} files")
    return successful_files > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'@

    # Write the temporary script
    $tempScript = "temp_cancellation_script.py"
    $cancellationScript | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        Write-Host "Creating cancellation events for existing events..." -ForegroundColor Yellow
        $result = & python $tempScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Cancellation events created successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to create cancellation events" -ForegroundColor Red
            return $false
        }
    }
    finally {
        # Clean up temporary script
        if (Test-Path $tempScript) {
            Remove-Item $tempScript
        }
    }
}

function Step2-MakeEventsPrivate {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 2: Making Events Private" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""

    if ($SkipPrivate) {
        Write-Host "Skipping private update (--SkipPrivate flag used)" -ForegroundColor Gray
        return $true
    }

    # Create the private update script content
    $privateScript = @'
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from icalendar import Calendar
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def make_events_private(ics_file):
    try:
        logger.info(f"Processing: {ics_file}")
        
        with open(ics_file, 'rb') as file:
            calendar = Calendar.from_ical(file.read())
        
        event_count = 0
        private_count = 0
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_count += 1
                summary = component.get('summary', 'Unknown Event')
                
                if component.get('class') == 'PRIVATE':
                    logger.info(f"  Event already private: {summary}")
                    private_count += 1
                else:
                    component.add('class', 'PRIVATE')
                    logger.info(f"  Made event private: {summary}")
                    private_count += 1
        
        with open(ics_file, 'wb') as file:
            file.write(calendar.to_ical())
        
        logger.info(f"  Updated {event_count} events, {private_count} are now private")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {ics_file}: {e}")
        return False

def main():
    input_dir = Path("' + $InputDir + '")
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    ics_files = list(input_dir.glob("*.ics"))
    
    if not ics_files:
        logger.warning(f"No ICS files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(ics_files)} ICS file(s) to process")
    
    successful_files = 0
    for ics_file in ics_files:
        if make_events_private(ics_file):
            successful_files += 1
    
    logger.info(f"Successfully processed {successful_files}/{len(ics_files)} files")
    return successful_files > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'@

    # Write the temporary script
    $tempScript = "temp_private_script.py"
    $privateScript | Out-File -FilePath $tempScript -Encoding UTF8

    try {
        Write-Host "Making all events private..." -ForegroundColor Yellow
        $result = & python $tempScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Events made private successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Failed to make events private" -ForegroundColor Red
            return $false
        }
    }
    finally {
        # Clean up temporary script
        if (Test-Path $tempScript) {
            Remove-Item $tempScript
        }
    }
}

function Step3-ShowInstructions {
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "STEP 3: Import Instructions" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""

    # Show cancellation files
    $cancellationFiles = Get-ChildItem -Path $OutputDir -Filter "*_cancellations.ics" -ErrorAction SilentlyContinue
    if ($cancellationFiles.Count -gt 0) {
        Write-Host "Cancellation files created:" -ForegroundColor Green
        $cancellationFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
        Write-Host ""
    }

    # Show updated files
    $updatedFiles = Get-ChildItem -Path $InputDir -Filter "*.ics" -ErrorAction SilentlyContinue
    if ($updatedFiles.Count -gt 0) {
        Write-Host "Updated private files:" -ForegroundColor Green
        $updatedFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
        Write-Host ""
    }

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    WINDOWS OUTLOOK IMPORT INSTRUCTIONS" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    if ($cancellationFiles.Count -gt 0) {
        Write-Host "STEP 1: Remove Existing Events (if any exist in Outlook)" -ForegroundColor Yellow
        Write-Host "1. Open Outlook" -ForegroundColor White
        Write-Host "2. Go to File → Open & Export → Import/Export" -ForegroundColor White
        Write-Host "3. Choose 'Import an iCalendar (.ics) file'" -ForegroundColor White
        Write-Host "4. Select the cancellation files from: $OutputDir" -ForegroundColor White
        Write-Host "5. Choose your calendar and import" -ForegroundColor White
        Write-Host "6. This will remove any existing events with matching UIDs" -ForegroundColor White
        Write-Host ""
    }

    Write-Host "STEP 2: Import Private Events" -ForegroundColor Yellow
    Write-Host "1. In Outlook, go to File → Open & Export → Import/Export" -ForegroundColor White
    Write-Host "2. Choose 'Import an iCalendar (.ics) file'" -ForegroundColor White
    Write-Host "3. Select the updated private files from: $InputDir" -ForegroundColor White
    Write-Host "4. Choose your calendar and import" -ForegroundColor White
    Write-Host "5. All events will now be marked as PRIVATE" -ForegroundColor White
    Write-Host ""

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    ALTERNATIVE: Batch Import" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "If you want to import all files at once:" -ForegroundColor White
    Write-Host "1. Select multiple .ics files in File Explorer" -ForegroundColor White
    Write-Host "2. Right-click → 'Open with' → Outlook" -ForegroundColor White
    Write-Host "3. Outlook will import all selected files" -ForegroundColor White
    Write-Host ""

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "    TROUBLESHOOTING" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "If import fails:" -ForegroundColor White
    Write-Host "- Try importing one file at a time" -ForegroundColor Gray
    Write-Host "- Check if events already exist with same UIDs" -ForegroundColor Gray
    Write-Host "- Try the cancellation files first, then the private files" -ForegroundColor Gray
    Write-Host "- Some calendar apps may not support all ICS features" -ForegroundColor Gray
}

function Show-Menu {
    Write-Host "Choose an option:" -ForegroundColor Cyan
    Write-Host "1. Run complete workflow (all 3 steps)" -ForegroundColor White
    Write-Host "2. Step 1 only: Create cancellation events" -ForegroundColor White
    Write-Host "3. Step 2 only: Make events private" -ForegroundColor White
    Write-Host "4. Step 3 only: Show import instructions" -ForegroundColor White
    Write-Host "5. Exit" -ForegroundColor White
    Write-Host ""
    $choice = Read-Host "Enter your choice (1-5)"
    return $choice
}

# Main script execution
try {
    Write-Header
    Test-Prerequisites
    Initialize-Directories
    
    do {
        $choice = Show-Menu
        
        switch ($choice) {
            "1" { 
                $step1 = Step1-CreateCancellations
                $step2 = Step2-MakeEventsPrivate
                if ($step1 -and $step2) {
                    Step3-ShowInstructions
                } else {
                    Write-Host "Some steps failed. Check the output above." -ForegroundColor Red
                }
            }
            "2" { Step1-CreateCancellations }
            "3" { Step2-MakeEventsPrivate }
            "4" { Step3-ShowInstructions }
            "5" { 
                Write-Host ""
                Write-Host "Thank you for using Outlook Event Manager!" -ForegroundColor Green
                Write-Host ""
                break
            }
            default { 
                Write-Host "Invalid choice. Please try again." -ForegroundColor Red
                Write-Host ""
            }
        }
        
        if ($choice -ne "5") {
            Write-Host ""
            $continue = Read-Host "Press Enter to continue or 'q' to quit"
            if ($continue -eq "q") { break }
        }
    } while ($choice -ne "5")
}
catch {
    Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} 