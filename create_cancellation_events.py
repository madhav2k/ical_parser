#!/usr/bin/env python3
"""
Create Cancellation Events for Windows Outlook
==============================================

This script reads all ICS files from input_ics_files/invites and creates
cancellation events for all events in those files. The cancellation events
are designed to work with Windows Outlook for removing existing events.

Usage:
    python create_cancellation_events.py

Output:
    - Creates cancellation ICS files in output_ics_files/cancellations/
    - Each cancellation file contains METHOD:CANCEL events for all events
    - Files are named with _cancellations suffix
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from icalendar import Calendar, Event
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_cancellation_calendar(original_calendar, filename):
    """
    Create a cancellation calendar from an original calendar.
    
    Args:
        original_calendar: The original icalendar.Calendar object
        filename: Original filename for naming the output file
    
    Returns:
        icalendar.Calendar: Calendar with cancellation events
    """
    cancellation_calendar = Calendar()
    
    # Set calendar properties for cancellation
    cancellation_calendar.add('prodid', '-//Calendar Cancellation Generator//EN')
    cancellation_calendar.add('version', '2.0')
    cancellation_calendar.add('calscale', 'GREGORIAN')
    cancellation_calendar.add('method', 'CANCEL')  # This is crucial for cancellations
    
    # Process each event in the original calendar
    for component in original_calendar.walk():
        if component.name == "VEVENT":
            # Create a cancellation event
            cancel_event = Event()
            
            # Copy essential properties from original event
            uid = component.get('uid')
            if uid:
                cancel_event.add('uid', uid)
            
            # Copy start and end times
            dtstart = component.get('dtstart')
            if dtstart:
                cancel_event.add('dtstart', dtstart)
            
            dtend = component.get('dtend')
            if dtend:
                cancel_event.add('dtend', dtend)
            
            # Copy summary for reference
            summary = component.get('summary')
            if summary:
                cancel_event.add('summary', summary)
            
            # Copy sequence number (important for cancellations)
            sequence = component.get('sequence', 0)
            cancel_event.add('sequence', sequence)
            
            # Copy organizer if present
            organizer = component.get('organizer')
            if organizer:
                cancel_event.add('organizer', organizer)
            
            # Copy attendees if present
            attendees = component.get('attendee')
            if attendees:
                if isinstance(attendees, list):
                    for attendee in attendees:
                        cancel_event.add('attendee', attendee)
                else:
                    cancel_event.add('attendee', attendees)
            
            # Set status to cancelled
            cancel_event.add('status', 'CANCELLED')
            
            # Make the event private
            cancel_event.add('class', 'PRIVATE')
            
            # Add the cancellation event to the calendar
            cancellation_calendar.add_component(cancel_event)
            
            logger.info(f"Created cancellation for event: {summary} (UID: {uid})")
    
    return cancellation_calendar

def process_ics_file(input_file, output_dir):
    """
    Process a single ICS file and create its cancellation version.
    
    Args:
        input_file: Path to the input ICS file
        output_dir: Directory to save the cancellation file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Processing: {input_file}")
        
        # Read the original ICS file
        with open(input_file, 'rb') as file:
            original_calendar = Calendar.from_ical(file.read())
        
        # Get filename without extension
        filename = Path(input_file).stem
        
        # Create cancellation calendar
        cancellation_calendar = create_cancellation_calendar(original_calendar, filename)
        
        # Create output filename
        output_filename = f"{filename}_cancellations.ics"
        output_path = Path(output_dir) / output_filename
        
        # Save the cancellation calendar
        with open(output_path, 'wb') as file:
            file.write(cancellation_calendar.to_ical())
        
        logger.info(f"Created cancellation file: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {input_file}: {e}")
        return False

def main():
    """Main function to process all ICS files in the invites folder."""
    
    # Define paths
    input_dir = Path("VedicCalendarParser/input_ics_files/invites")
    output_dir = Path("output_ics_files/cancellations")
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        logger.info("Please ensure the invites folder exists in VedicCalendarParser/input_ics_files/")
        return False
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
        if process_ics_file(ics_file, output_dir):
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
    logger.info(f"Output directory: {output_dir}")
    
    if successful_files > 0:
        logger.info("")
        logger.info("Cancellation files created:")
        for file in output_dir.glob("*_cancellations.ics"):
            logger.info(f"  - {file.name}")
        
        logger.info("")
        logger.info("IMPORT INSTRUCTIONS FOR WINDOWS OUTLOOK:")
        logger.info("1. Open Outlook")
        logger.info("2. Go to File → Open & Export → Import/Export")
        logger.info("3. Choose 'Import an iCalendar (.ics) file'")
        logger.info("4. Select the cancellation files from the output directory")
        logger.info("5. Choose your calendar and import")
        logger.info("6. The events with matching UIDs will be cancelled/removed")
    
    return successful_files > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 