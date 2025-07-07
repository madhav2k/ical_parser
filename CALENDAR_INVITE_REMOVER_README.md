# Calendar Invite Remover

A powerful Python script to remove calendar invites and events from ICS files. Works on Windows, macOS, and Linux.

## Features

- **Remove meeting/invite events** - Automatically detects and removes calendar invites
- **Pattern-based filtering** - Use regex patterns to match and remove specific events
- **Date range filtering** - Remove events within specific date ranges
- **Duplicate removal** - Remove duplicate events based on summary and time
- **Category filtering** - Keep or remove events based on categories
- **Dry run mode** - Preview what would be removed without making changes
- **Windows-friendly** - Includes batch and PowerShell scripts for easy Windows usage

## Installation

### Prerequisites

1. **Python 3.7 or higher** - Download from [python.org](https://python.org)
2. **Required Python packages** - The script will automatically install them

### Quick Setup

1. Download the files to your computer
2. Open Command Prompt or PowerShell in the folder containing the files
3. The script will automatically check for and install required packages

## Usage

### Windows Users

#### Option 1: Batch File (Command Prompt)
```cmd
# Basic usage
remove_calendar_invites.bat calendar.ics

# Remove all meeting/invite events
remove_calendar_invites.bat calendar.ics --remove-invites

# Remove events matching a pattern
remove_calendar_invites.bat calendar.ics --pattern "zoom|teams|meeting"

# Remove events in a date range
remove_calendar_invites.bat calendar.ics --start-date 2024-01-01 --end-date 2024-01-31

# Remove duplicates
remove_calendar_invites.bat calendar.ics --remove-duplicates

# Preview what would be removed (dry run)
remove_calendar_invites.bat calendar.ics --dry-run
```

#### Option 2: PowerShell Script
```powershell
# Basic usage
.\remove_calendar_invites.ps1 -InputFile calendar.ics

# Remove all meeting/invite events
.\remove_calendar_invites.ps1 -InputFile calendar.ics -RemoveInvites

# Remove events matching a pattern
.\remove_calendar_invites.ps1 -InputFile calendar.ics -Pattern "zoom|teams"

# Remove events in a date range
.\remove_calendar_invites.ps1 -InputFile calendar.ics -StartDate "2024-01-01" -EndDate "2024-01-31"

# Remove duplicates
.\remove_calendar_invites.ps1 -InputFile calendar.ics -RemoveDuplicates

# Preview what would be removed (dry run)
.\remove_calendar_invites.ps1 -InputFile calendar.ics -DryRun
```

### All Platforms (Direct Python)

```bash
# Basic usage
python calendar_invite_remover.py calendar.ics

# Remove all meeting/invite events
python calendar_invite_remover.py calendar.ics --remove-invites

# Remove events matching a pattern
python calendar_invite_remover.py calendar.ics --pattern "zoom|teams|meeting"

# Remove events in a date range
python calendar_invite_remover.py calendar.ics --start-date 2024-01-01 --end-date 2024-01-31

# Remove duplicates
python calendar_invite_remover.py calendar.ics --remove-duplicates

# Preview what would be removed (dry run)
python calendar_invite_remover.py calendar.ics --dry-run
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--remove-invites` | Remove meeting/invite events | `--remove-invites` |
| `--pattern` | Regex pattern to match events | `--pattern "zoom\|teams"` |
| `--start-date` | Start date for filtering (YYYY-MM-DD) | `--start-date 2024-01-01` |
| `--end-date` | End date for filtering (YYYY-MM-DD) | `--end-date 2024-01-31` |
| `--remove-duplicates` | Remove duplicate events | `--remove-duplicates` |
| `--keep-categories` | Keep only events with these categories | `--keep-categories "work" "personal"` |
| `--remove-categories` | Remove events with these categories | `--remove-categories "spam" "unwanted"` |
| `--dry-run` | Show what would be removed without making changes | `--dry-run` |
| `--verbose` | Enable verbose logging | `--verbose` |
| `-o, --output` | Specify output file path | `-o cleaned_calendar.ics` |

## Examples

### Example 1: Remove All Meeting Events
```cmd
remove_calendar_invites.bat my_calendar.ics --remove-invites
```
This will remove all events that are detected as meetings, invites, or calls (Zoom, Teams, etc.).

### Example 2: Remove Specific Types of Events
```cmd
remove_calendar_invites.bat my_calendar.ics --pattern "zoom|teams|webex|skype"
```
This will remove events that contain "zoom", "teams", "webex", or "skype" in the title or description.

### Example 3: Remove Events from a Specific Month
```cmd
remove_calendar_invites.bat my_calendar.ics --start-date 2024-01-01 --end-date 2024-01-31
```
This will remove all events that occur in January 2024.

### Example 4: Remove Duplicate Events
```cmd
remove_calendar_invites.bat my_calendar.ics --remove-duplicates
```
This will remove duplicate events based on the same title and time.

### Example 5: Preview Changes Before Making Them
```cmd
remove_calendar_invites.bat my_calendar.ics --remove-invites --dry-run
```
This will show you what events would be removed without actually removing them.

### Example 6: Keep Only Work Events
```cmd
remove_calendar_invites.bat my_calendar.ics --keep-categories "work" "business"
```
This will keep only events that have "work" or "business" categories.

## Output Files

The script creates the following output files:

1. **`[filename]_cleaned.ics`** - The cleaned calendar file
2. **`[filename]_cleaned_removed_events.json`** - List of removed events with reasons

## How It Works

The script uses several methods to identify calendar invites:

1. **Keyword Detection** - Looks for common meeting keywords in event titles and descriptions
2. **Property Analysis** - Checks for organizer and attendee properties
3. **Status Checking** - Identifies events with confirmed/tentative/cancelled status
4. **Pattern Matching** - Uses regex patterns to match specific event types

## Troubleshooting

### Common Issues

1. **"Python is not installed"**
   - Download and install Python from [python.org](https://python.org)
   - Make sure to check "Add Python to PATH" during installation

2. **"Required packages not found"**
   - The script will automatically install required packages
   - If it fails, manually run: `pip install icalendar`

3. **"Input file does not exist"**
   - Make sure the ICS file path is correct
   - Use the full path if the file is in a different directory

4. **"Permission denied"**
   - Run Command Prompt or PowerShell as Administrator
   - Make sure you have write permissions in the output directory

### Getting Help

Run the script with `--help` to see all available options:
```cmd
python calendar_invite_remover.py --help
```

## File Structure

```
calendar_invite_remover/
├── calendar_invite_remover.py      # Main Python script
├── remove_calendar_invites.bat     # Windows batch file
├── remove_calendar_invites.ps1     # Windows PowerShell script
└── CALENDAR_INVITE_REMOVER_README.md # This file
```

## Requirements

- Python 3.7+
- icalendar library (auto-installed)
- Windows, macOS, or Linux

## License

This script is provided as-is for educational and personal use.

## Support

If you encounter any issues or have questions, please check the troubleshooting section above or create an issue in the project repository. 