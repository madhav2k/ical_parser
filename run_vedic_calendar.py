#!/usr/bin/env python3
"""
Vedic Calendar Parser - Usage Examples

This script provides examples of how to run the Vedic Calendar Parser
with different ICS files and date ranges. The application now uses
relative paths and automatically extracts month information from
input filenames for output file naming.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and show the description"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Success!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error occurred:")
        print(e.stderr)
        return False

def main():
    print("Vedic Calendar Parser - Usage Examples")
    print("=" * 50)
    print("Note: Output files now include month information from input filename")
    print("Example: April2025.ics → vedic_04_2025_events.ics")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("VedicCalendarParser/main.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Example 1: Use default file (if it exists)
    print("\n1. Using default April2025.ics file:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py"],
        "Process default April2025.ics file (creates vedic_04_2025_*.ics files)"
    )
    
    # Example 2: Specify a custom ICS file with relative path
    print("\n2. Using a custom ICS file with relative path:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py", "VedicCalendarParser/April2025.ics"],
        "Process specific ICS file using relative path"
    )
    
    # Example 3: Custom date range
    print("\n3. Using custom date range:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py", 
         "VedicCalendarParser/April2025.ics", 
         "--start-date", "2025-04-01", 
         "--end-date", "2025-04-30"],
        "Process with custom date range"
    )
    
    # Example 4: Custom output prefix
    print("\n4. Using custom output prefix:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py", 
         "VedicCalendarParser/April2025.ics", 
         "--output-prefix", "my_calendar"],
        "Process with custom output file names (creates my_calendar_04_2025_*.ics files)"
    )
    
    # Example 5: Different month file
    print("\n5. Processing a different month file:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py", 
         "VedicCalendarParser/March2025.ics", 
         "--output-prefix", "march_calendar"],
        "Process March file (creates march_calendar_03_2025_*.ics files)"
    )
    
    # Show help
    print("\n6. Show help:")
    run_command(
        ["rye", "run", "python", "VedicCalendarParser/main.py", "--help"],
        "Display help information"
    )
    
    print("\n" + "="*60)
    print("Usage Examples Complete!")
    print("="*60)
    print("\n📁 Output File Naming Examples:")
    print("  Input: April2025.ics")
    print("  Output: vedic_04_2025_events.ics, vedic_04_2025_hora_events.ics")
    print("")
    print("  Input: March2024.ics")
    print("  Output: vedic_03_2024_events.ics, vedic_03_2024_hora_events.ics")
    print("")
    print("  Input: 05-2025.ics")
    print("  Output: vedic_05_2025_events.ics, vedic_05_2025_hora_events.ics")
    print("")
    print("📋 Quick Reference:")
    print("  Basic usage: rye run python VedicCalendarParser/main.py [ics_file]")
    print("  With dates:  rye run python VedicCalendarParser/main.py [ics_file] --start-date YYYY-MM-DD --end-date YYYY-MM-DD")
    print("  Custom output: rye run python VedicCalendarParser/main.py [ics_file] --output-prefix my_prefix")
    print("  Help:        rye run python VedicCalendarParser/main.py --help")

if __name__ == "__main__":
    main() 