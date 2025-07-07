# Vedic Calendar Event Cleaner - Windows Automation

This package provides Windows automation scripts to remove VAR and DUS events from ICS calendar files.

## 📁 Files Included

- `calendar_invite_remover.py` - Main Python script for processing ICS files
- `calendar_cleaner_windows.bat` - Windows Batch script (simple interface)
- `calendar_cleaner_windows.ps1` - Windows PowerShell script (advanced interface)
- `README_Windows_Automation.md` - This documentation

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed and added to PATH
   - Download from: https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Required Python packages:**
   ```bash
   pip install icalendar
   ```

### Setup

1. **Place your ICS files** in the `input_ics_files` folder
2. **Run one of the automation scripts** (see options below)

## 🎯 Usage Options

### Option 1: PowerShell Script (Recommended)

**Features:**
- ✅ Color-coded output
- ✅ Better error handling
- ✅ Progress tracking
- ✅ Parameter customization
- ✅ Detailed logging

**Run the script:**
```powershell
# Right-click calendar_cleaner_windows.ps1 → "Run with PowerShell"
# OR
powershell -ExecutionPolicy Bypass -File calendar_cleaner_windows.ps1
```

**Custom parameters:**
```powershell
powershell -ExecutionPolicy Bypass -File calendar_cleaner_windows.ps1 -InputDir "my_files" -OutputDir "my_output" -StartDate "2025-01-01" -EndDate "2025-12-31"
```

### Option 2: Batch Script (Simple)

**Features:**
- ✅ Simple interface
- ✅ Works on all Windows versions
- ✅ No PowerShell required

**Run the script:**
```cmd
# Double-click calendar_cleaner_windows.bat
# OR
calendar_cleaner_windows.bat
```

## 📋 What the Scripts Do

### Step-by-Step Process

1. **Check Prerequisites**
   - Verify Python is installed
   - Verify calendar_invite_remover.py exists
   - Create input/output directories if needed

2. **Process ICS Files**
   - **Step 1:** Remove VAR events (with `SUMMARY:VAR` and `CATEGORIES:VARJYAM`)
   - **Step 2:** Remove DUS events (with `SUMMARY:DUS` and `DESCRIPTION:DUS PERIOD`)
   - Filter by date range: July 1, 2025 to December 31, 2025

3. **Generate Output Files**
   - `*_cleaned_cleaned.ics` - Final cleaned calendar file
   - `*_cleaned_cleaned_cancellations.ics` - Cancellation events for import

## 📂 File Structure

```
your_project_folder/
├── calendar_invite_remover.py
├── calendar_cleaner_windows.bat
├── calendar_cleaner_windows.ps1
├── input_ics_files/
│   ├── July_output_2025.ics
│   ├── August_output_2025.ics
│   └── ...
└── output_ics_files/
    ├── July_output_2025_cleaned_cleaned.ics
    ├── July_output_2025_cleaned_cleaned_cancellations.ics
    └── ...
```

## 🔧 Import Instructions

### Windows Outlook

1. **Open Outlook**
2. **Go to:** File → Open & Export → Import/Export
3. **Choose:** "Import an iCalendar (.ics) file"
4. **Select:** `*_cleaned_cleaned_cancellations.ics` file
5. **Choose:** Your target calendar
6. **Import:** The cancellation events will remove matching events

### macOS Calendar

1. **Double-click** the cancellation file
2. **If import fails:**
   - Create a new calendar
   - Import the cleaned file (`*_cleaned_cleaned.ics`) instead

### Google Calendar

1. **Go to:** Settings → Import & Export
2. **Upload:** The cancellation file
3. **Choose:** Your calendar and import

## ⚠️ Troubleshooting

### Common Issues

**"Python is not installed"**
- Install Python from https://python.org
- Make sure to check "Add Python to PATH"

**"calendar_invite_remover.py not found"**
- Ensure all files are in the same directory
- Check file permissions

**"No ICS files found"**
- Place your .ics files in the `input_ics_files` folder
- Check file extensions are `.ics`

**Import fails in calendar app**
- Try the cleaned file instead of cancellation file
- Check if original events have matching UIDs
- Some calendar apps don't support cancellations

### PowerShell Execution Policy

If you get execution policy errors:

```powershell
# Run as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📊 Expected Results

### Input File Example
```
BEGIN:VEVENT
SUMMARY:VAR
CATEGORIES:Varjyam
DESCRIPTION:VAR period
DTSTART:20250714T000900
DTEND:20250714T014300
UID:8C3CBCF41B05825BB6A302EC82EF725B9A9DDE97_37
END:VEVENT
```

### Output File
- **VAR events:** Removed
- **DUS events:** Removed
- **Other events:** Preserved
- **Date range:** Only July 1 - December 31, 2025

## 🔄 Batch Processing

### Process Multiple Files

1. **Place all ICS files** in `input_ics_files/`
2. **Run the script** and choose "Process all ICS files"
3. **All files** will be processed automatically

### Custom Date Ranges

**PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File calendar_cleaner_windows.ps1 -StartDate "2025-01-01" -EndDate "2025-06-30"
```

**Batch:** Edit the script to change date parameters

## 📝 Logging

### PowerShell Script
- **Green:** Success messages
- **Yellow:** Warnings and progress
- **Red:** Errors
- **Cyan:** Headers and menus

### Batch Script
- **Standard output:** Processing information
- **Error messages:** Clear error descriptions

## 🆘 Support

### Getting Help

1. **Check the troubleshooting section** above
2. **Verify file structure** matches the expected layout
3. **Test with a single file** first before batch processing
4. **Check Python installation** with `python --version`

### File Locations

- **Input files:** `input_ics_files/`
- **Output files:** `output_ics_files/`
- **Scripts:** Same directory as Python script

## 🔒 Security Notes

- Scripts only read/write ICS files
- No network access or data transmission
- All processing is local
- No personal data is collected or stored

---

**Version:** 1.0  
**Last Updated:** July 2025  
**Compatibility:** Windows 7/8/10/11 