# Outlook Event Manager - Complete Workflow

This package provides comprehensive scripts to manage Vedic calendar events in Windows Outlook, including creating cancellation events and making events private.

## Files Included

- `outlook_event_manager.ps1` - PowerShell script (recommended)
- `outlook_event_manager.bat` - Batch script (alternative)
- `OUTLOOK_EVENT_MANAGER_README.md` - This documentation

## Prerequisites

1. **Python 3.6+** installed and added to PATH
   - Download from: https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Required Python packages:**
   ```bash
   pip install icalendar
   ```

3. **ICS files** in the `VedicCalendarParser/input_ics_files/invites/` directory

## What the Scripts Do

The scripts perform three main operations:

### Step 1: Create Cancellation Events
- Reads all ICS files from the input directory
- Creates cancellation events for each existing event
- Saves cancellation files to `output_ics_files/cancellations/`
- Files are named with `_cancellations.ics` suffix

### Step 2: Make Events Private
- Updates all ICS files in the input directory
- Adds `CLASS:PRIVATE` to all events
- Modifies files in place

### Step 3: Import Instructions
- Provides step-by-step instructions for Windows Outlook
- Explains how to import cancellation files first
- Then import the updated private files

## Usage

### PowerShell Script (Recommended)

1. **Open PowerShell as Administrator**
2. **Navigate to the script directory:**
   ```powershell
   cd "path\to\your\project"
   ```

3. **Run the script:**
   ```powershell
   .\outlook_event_manager.ps1
   ```

4. **Choose from the menu:**
   - Option 1: Complete workflow (all 3 steps)
   - Option 2: Create cancellations only
   - Option 3: Make events private only
   - Option 4: Show instructions only
   - Option 5: Exit

### Batch Script (Alternative)

1. **Open Command Prompt as Administrator**
2. **Navigate to the script directory:**
   ```cmd
   cd "path\to\your\project"
   ```

3. **Run the script:**
   ```cmd
   outlook_event_manager.bat
   ```

4. **Follow the same menu options as PowerShell**

## Command Line Options (PowerShell Only)

The PowerShell script supports additional parameters:

```powershell
# Custom input/output directories
.\outlook_event_manager.ps1 -InputDir "custom/input/path" -OutputDir "custom/output/path"

# Skip specific steps
.\outlook_event_manager.ps1 -SkipCancellations
.\outlook_event_manager.ps1 -SkipPrivate

# Force overwrite (if applicable)
.\outlook_event_manager.ps1 -Force
```

## Directory Structure

```
your_project/
├── VedicCalendarParser/
│   └── input_ics_files/
│       └── invites/
│           ├── file1.ics
│           ├── file2.ics
│           └── ...
├── output_ics_files/
│   └── cancellations/
│       ├── file1_cancellations.ics
│       ├── file2_cancellations.ics
│       └── ...
├── outlook_event_manager.ps1
├── outlook_event_manager.bat
└── OUTLOOK_EVENT_MANAGER_README.md
```

## Windows Outlook Import Process

### Method 1: Manual Import (Recommended)

1. **Remove Existing Events (if any):**
   - Open Outlook
   - Go to File → Open & Export → Import/Export
   - Choose "Import an iCalendar (.ics) file"
   - Select cancellation files from `output_ics_files/cancellations/`
   - Choose your calendar and import
   - This removes existing events with matching UIDs

2. **Import Private Events:**
   - In Outlook, go to File → Open & Export → Import/Export
   - Choose "Import an iCalendar (.ics) file"
   - Select updated private files from `VedicCalendarParser/input_ics_files/invites/`
   - Choose your calendar and import
   - All events will be marked as PRIVATE

### Method 2: Batch Import

1. **Select multiple .ics files** in File Explorer
2. **Right-click → "Open with" → Outlook**
3. **Outlook will import all selected files**

## Troubleshooting

### Common Issues

1. **Python not found:**
   - Install Python from https://python.org
   - Make sure to check "Add Python to PATH" during installation
   - Restart Command Prompt/PowerShell after installation

2. **icalendar package missing:**
   ```bash
   pip install icalendar
   ```

3. **No ICS files found:**
   - Ensure files exist in `VedicCalendarParser/input_ics_files/invites/`
   - Check file extensions are `.ics`

4. **Import fails in Outlook:**
   - Try importing one file at a time
   - Check if events already exist with same UIDs
   - Import cancellation files first, then private files
   - Some calendar apps may not support all ICS features

5. **Permission errors:**
   - Run PowerShell/Command Prompt as Administrator
   - Check file permissions on input/output directories

### Error Messages

- **"Python is not installed"**: Install Python and add to PATH
- **"icalendar package not found"**: Run `pip install icalendar`
- **"No ICS files found"**: Check input directory and file extensions
- **"Failed to create cancellation events"**: Check file permissions and Python installation

## File Formats

### Input Files
- Standard ICS calendar files
- Should be in `VedicCalendarParser/input_ics_files/invites/`
- Must have `.ics` extension

### Output Files
- **Cancellation files**: `filename_cancellations.ics`
- **Updated files**: Original files modified in place with `CLASS:PRIVATE`

## Security Notes

- Scripts modify files in place (for private events)
- Always backup original files before running
- Cancellation files are created as new files
- All events are marked as PRIVATE for confidentiality

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify Python and icalendar package installation
3. Ensure input files exist and are valid ICS format
4. Try running individual steps instead of complete workflow
5. Check Windows Event Viewer for system errors

## Version Information

- **Script Version**: 1.0
- **Compatible with**: Windows 10/11, Outlook 2016+
- **Python Version**: 3.6+
- **Required Packages**: icalendar

---

**Note**: These scripts are designed specifically for Windows Outlook. For other calendar applications, the ICS files may work but import procedures may differ. 