#!/usr/bin/env python3
"""
Make Events Private
==================

This script reads all ICS files from input_ics_files/invites and updates
all events to be private by adding the CLASS:PRIVATE property.

Usage:
    python make_events_private.py

Output:
    - Updates the original ICS files in place
    - Adds CLASS:PRIVATE to all VEVENT components
"""

import os
import sys
from pathlib import Path
from icalendar import Calendar
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def make_events_private(ics_file):
    """
    Update all events in an ICS file to be private.
    
    Args:
        ics_file: Path to the ICS file to update
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Processing: {ics_file}")
        
        # Read the ICS file
        with open(ics_file, 'rb') as file:
            calendar = Calendar.from_ical(file.read())
        
        # Count events before processing
        event_count = 0
        private_count = 0
        
        # Update each event to be private
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_count += 1
                summary = component.get('summary', 'Unknown Event')
                
                # Check if event is already private
                if component.get('class') == 'PRIVATE':
                    logger.info(f"  Event already private: {summary}")
                    private_count += 1
                else:
                    # Make the event private
                    component.add('class', 'PRIVATE')
                    logger.info(f"  Made event private: {summary}")
                    private_count += 1
        
        # Write the updated calendar back to the file
        with open(ics_file, 'wb') as file:
            file.write(calendar.to_ical())
        
        logger.info(f"  Updated {event_count} events, {private_count} are now private")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {ics_file}: {e}")
        return False

def main():
    """Main function to process all ICS files in the invites folder."""
    
    # Define input directory
    input_dir = Path("VedicCalendarParser/input_ics_files/invites")
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        logger.info("Please ensure the invites folder exists in VedicCalendarParser/input_ics_files/")
        return False
    
    # Get all ICS files in the input directory
    ics_files = list(input_dir.glob("*.ics"))
    
    if not ics_files:
        logger.warning(f"No ICS files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(ics_files)} ICS file(s) to process")
    
    # Process each file
    successful_files = 0
    failed_files = 0
    
    for ics_file in ics_files:
        if make_events_private(ics_file):
            successful_files += 1
        else:
            failed_files += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files processed: {len(ics_files)}")
    logger.info(f"Successful: {successful_files}")
    logger.info(f"Failed: {failed_files}")
    
    if successful_files > 0:
        logger.info("")
        logger.info("Updated files:")
        for file in ics_files:
            logger.info(f"  - {file.name}")
        
        logger.info("")
        logger.info("All events in these files are now marked as PRIVATE")
        logger.info("You can now import these files into Windows Outlook")
    
    return successful_files > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 