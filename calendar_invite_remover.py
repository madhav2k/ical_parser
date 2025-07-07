#!/usr/bin/env python3
"""
Calendar Invite Remover - A script to remove calendar invites and events from ICS files.
Works on Windows, macOS, and Linux.

This script can filter and remove calendar events based on:
- Event type (meetings, invites, etc.)
- Summary patterns (regex matching)
- Date ranges
- Specific event properties
- Duplicate events
"""

import os
import sys
import argparse
import re
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CalendarInviteRemover:
    """Class to handle calendar invite removal operations."""
    
    def __init__(self, input_file, output_file=None):
        self.input_file = input_file
        self.output_file = output_file or self._generate_output_filename(input_file)
        self.calendar = None
        self.removed_count = 0
        self.kept_count = 0
        
    def _generate_output_filename(self, input_file):
        """Generate output filename with '_cleaned' suffix."""
        path = Path(input_file)
        return str(path.parent / f"{path.stem}_cleaned{path.suffix}")
    
    def load_calendar(self):
        """Load the ICS calendar file."""
        try:
            with open(self.input_file, 'rb') as file:
                self.calendar = Calendar.from_ical(file.read())
            logger.info(f"Loaded calendar from {self.input_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading calendar: {e}")
            return False
    
    def is_invite_event(self, event):
        """Check if an event is a calendar invite/meeting."""
        # Check for common invite indicators
        summary = str(event.get('summary', '')).lower()
        description = str(event.get('description', '')).lower()
        
        # More specific invite keywords that indicate actual meetings/invites
        invite_keywords = [
            'zoom meeting', 'teams meeting', 'webex meeting', 'skype call',
            'google meet', 'meeting invite', 'calendar invite', 'meeting invitation',
            'video call', 'conference call', 'team meeting', 'staff meeting',
            'client meeting', 'business meeting', 'appointment', 'consultation',
            'interview', 'presentation', 'webinar', 'workshop', 'training session',
            'review meeting', 'sync meeting', 'standup', 'daily standup',
            'weekly meeting', 'monthly meeting', 'quarterly review'
        ]
        
        # Check summary for invite keywords
        for keyword in invite_keywords:
            if keyword in summary:
                return True
        
        # Check description for invite keywords
        for keyword in invite_keywords:
            if keyword in description:
                return True
        
        # Check for specific properties that indicate invites
        # Only consider it an invite if it has BOTH organizer AND attendee
        organizer = event.get('organizer')
        attendee = event.get('attendee')
        if organizer and attendee:
            return True
            
        # Check for meeting-specific status properties
        status = str(event.get('status', '')).lower()
        if status in ['confirmed', 'tentative', 'cancelled'] and (organizer or attendee):
            return True
            
        # Check for meeting-specific properties
        if event.get('x-microsoft-cdo-busystatus') or event.get('x-microsoft-cdo-intendedstatus'):
            return True
            
        return False
    
    def matches_pattern(self, event, pattern):
        """Check if event matches specific patterns for Vedic calendar events."""
        if not pattern:
            return False
        summary = str(event.get('summary', '')).upper().strip()
        description = str(event.get('description', '')).upper().strip()
        categories = event.get('categories', None)
        if hasattr(categories, 'to_ical'):
            categories_str = categories.to_ical().decode().upper().strip()
        elif categories is not None:
            categories_str = str(categories).upper().strip()
        else:
            categories_str = ''
        # Check for VAR events: SUMMARY:VAR and CATEGORIES:VARJYAM
        if pattern == 'VAR':
            return (summary == 'VAR' and 'VARJYAM' in categories_str)
        # Check for DUS events: SUMMARY:DUS and DESCRIPTION:DUS PERIOD
        elif pattern == 'DUS':
            return (summary == 'DUS' and 'DUS PERIOD' in description)
        # Otherwise treat as regex
        try:
            return bool(re.search(pattern, summary, re.IGNORECASE) or 
                       re.search(pattern, description, re.IGNORECASE))
        except re.error:
            logger.warning(f"Invalid regex pattern: {pattern}")
            return False
    
    def is_in_date_range(self, event, start_date=None, end_date=None):
        """Check if event is within the specified date range."""
        if not start_date and not end_date:
            return True
            
        dtstart = event.get('dtstart')
        if not dtstart:
            return False
            
        event_date = dtstart.dt
        if hasattr(event_date, 'date'):
            event_date = event_date.date()
        else:
            event_date = event_date
            
        if start_date and event_date < start_date:
            return False
        if end_date and event_date > end_date:
            return False
            
        return True
    
    def is_duplicate(self, event, seen_events):
        """Check if event is a duplicate based on summary and time."""
        summary = str(event.get('summary', ''))
        dtstart = event.get('dtstart')
        
        if not dtstart:
            return False
            
        event_time = dtstart.dt
        if hasattr(event_time, 'date'):
            event_time = event_time.date()
        
        key = (summary.lower().strip(), event_time)
        if key in seen_events:
            return True
            
        seen_events.add(key)
        return False
    
    def remove_events(self, remove_invites=True, pattern=None, 
                     start_date=None, end_date=None, remove_duplicates=False,
                     keep_categories=None, remove_categories=None):
        """Remove events based on specified criteria."""
        if not self.calendar:
            logger.error("No calendar loaded")
            return False
        
        # Convert date strings to datetime objects
        if start_date and isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date and isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Create a new calendar
        new_calendar = Calendar()
        
        # Copy calendar properties
        for key, value in self.calendar.items():
            if key not in ['VEVENT', 'VTODO', 'VJOURNAL']:
                new_calendar.add(key, value)
        
        seen_events = set()
        removed_events = []
        
        # Process each event
        for component in self.calendar.walk():
            if component.name == "VEVENT":
                summary = str(component.get('summary', '')).upper().strip()
                description = str(component.get('description', '')).upper().strip()
                categories = component.get('categories', None)
                # Extract real value from icalendar property if possible
                if hasattr(categories, 'to_ical'):
                    categories_str = categories.to_ical().decode().upper().strip()
                elif categories is not None:
                    categories_str = str(categories).upper().strip()
                else:
                    categories_str = ''
                if summary in ['VAR', 'DUS']:
                    print(f"DEBUG: summary={summary!r}, categories={categories_str!r}, description={description!r}")
                should_remove = False
                reason = []
                
                # Check if it's an invite event
                if remove_invites and self.is_invite_event(component):
                    should_remove = True
                    reason.append("invite/meeting")
                
                # Check pattern matching
                if pattern and self.matches_pattern(component, pattern):
                    should_remove = True
                    reason.append(f"matches pattern: {pattern}")
                
                # Check date range
                if not self.is_in_date_range(component, start_date, end_date):
                    should_remove = True
                    reason.append("outside date range")
                
                # Check for duplicates
                if remove_duplicates and self.is_duplicate(component, seen_events):
                    should_remove = True
                    reason.append("duplicate")
                
                # Check categories
                if keep_categories and categories:
                    should_keep = False
                    for cat in categories:
                        if any(keep_cat.lower() in str(cat).lower() for keep_cat in keep_categories):
                            should_keep = True
                            break
                    if not should_keep:
                        should_remove = True
                        reason.append("not in keep categories")
                
                if remove_categories and categories:
                    for cat in categories:
                        if any(remove_cat.lower() in str(cat).lower() for remove_cat in remove_categories):
                            should_remove = True
                            reason.append("in remove categories")
                            break
                
                if should_remove:
                    self.removed_count += 1
                    summary = str(component.get('summary', 'Unknown Event'))
                    
                    # Capture full event details for cancellation
                    dtstart = component.get('dtstart')
                    dtend = component.get('dtend')
                    
                    event_info = {
                        'summary': summary,
                        'reason': ', '.join(reason),
                        'date': str(dtstart) if dtstart else '',
                        'uid': str(component.get('uid', '')),
                        'dtstart': str(dtstart) if dtstart else '',
                        'dtend': str(dtend) if dtend else '',
                        'description': str(component.get('description', '')),
                        'location': str(component.get('location', '')),
                        'sequence': int(component.get('sequence', 0))
                    }
                    removed_events.append(event_info)
                    logger.info(f"Removing: {summary} - {', '.join(reason)}")
                else:
                    new_calendar.add_component(component)
                    self.kept_count += 1
        
        self.calendar = new_calendar
        
        # Log summary
        logger.info(f"Removed {self.removed_count} events, kept {self.kept_count} events")
        
        # Save removed events to JSON for reference
        if removed_events:
            removed_file = self.output_file.replace('.ics', '_removed_events.json')
            with open(removed_file, 'w') as f:
                json.dump(removed_events, f, indent=2)
            logger.info(f"Removed events saved to: {removed_file}")
        
        return True
    
    def create_cancellation_calendar(self, removed_events):
        """Create a calendar with cancellation events for the removed events."""
        from icalendar import Calendar, Event
        from datetime import datetime, timedelta
        
        cancellation_calendar = Calendar()
        cancellation_calendar.add('prodid', '-//Calendar Invite Remover//EN')
        cancellation_calendar.add('version', '2.0')
        cancellation_calendar.add('calscale', 'GREGORIAN')
        cancellation_calendar.add('method', 'CANCEL')
        
        for event_info in removed_events:
            # Create a cancellation event
            cancel_event = Event()
            
            # Set the same UID as the original event (if available)
            if 'uid' in event_info:
                cancel_event.add('uid', event_info['uid'])
            else:
                # Generate a UID based on the event details
                summary = event_info.get('summary', 'Unknown')
                date = event_info.get('date', '')
                uid = f"cancel-{summary}-{date}".replace(' ', '-').replace(':', '')
                cancel_event.add('uid', uid)
            
            # Set the original event details
            cancel_event.add('summary', event_info.get('summary', 'Unknown Event'))
            
            # Set the original start time (skip for now to avoid parsing issues)
            # The cancellation will work based on UID matching
            
            # Set the original end time (skip for now to avoid parsing issues)
            # The cancellation will work based on UID matching
            
            # Mark as cancelled
            cancel_event.add('status', 'CANCELLED')
            
            # Add cancellation reason
            cancel_event.add('description', f"Event cancelled: {event_info.get('reason', 'Removed by calendar cleaner')}")
            
            # Set sequence number (increment from original if available)
            cancel_event.add('sequence', 1)
            
            # Add to calendar
            cancellation_calendar.add_component(cancel_event)
        
        return cancellation_calendar
    
    def save_calendar(self):
        """Save the cleaned calendar to file."""
        try:
            with open(self.output_file, 'wb') as file:
                file.write(self.calendar.to_ical())
            logger.info(f"Cleaned calendar saved to: {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving calendar: {e}")
            return False
    
    def save_cancellation_calendar(self, removed_events):
        """Save a cancellation calendar to file."""
        try:
            cancellation_calendar = self.create_cancellation_calendar(removed_events)
            cancellation_file = self.output_file.replace('.ics', '_cancellations.ics')
            
            with open(cancellation_file, 'wb') as file:
                file.write(cancellation_calendar.to_ical())
            logger.info(f"Cancellation calendar saved to: {cancellation_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving cancellation calendar: {e}")
            return False
    
    def get_statistics(self):
        """Get statistics about the calendar processing."""
        return {
            'input_file': self.input_file,
            'output_file': self.output_file,
            'events_removed': self.removed_count,
            'events_kept': self.kept_count,
            'total_processed': self.removed_count + self.kept_count
        }

def process_single_file(input_file, args):
    """Process a single ICS file."""
    logger.info(f"Processing: {input_file}")
    
    # Generate output filename
    output_file = args.output_dir / f"{Path(input_file).stem}_cleaned.ics"
    
    # Create remover instance
    remover = CalendarInviteRemover(input_file, str(output_file))
    
    # Load calendar
    if not remover.load_calendar():
        logger.error(f"Failed to load calendar: {input_file}")
        return False
    
    # For dry run, just show what would be removed
    if args.dry_run:
        logger.info(f"DRY RUN MODE for {input_file} - No changes will be made")
        # Create a temporary copy for analysis
        temp_remover = CalendarInviteRemover(input_file, str(output_file))
        temp_remover.load_calendar()
        temp_remover.remove_events(
            remove_invites=args.remove_invites,
            pattern=args.pattern,
            start_date=args.start_date,
            end_date=args.end_date,
            remove_duplicates=args.remove_duplicates,
            keep_categories=args.keep_categories,
            remove_categories=args.remove_categories
        )
        stats = temp_remover.get_statistics()
        logger.info(f"DRY RUN RESULTS for {input_file}: {stats['events_removed']} events would be removed, {stats['events_kept']} would be kept")
        return True
    
    # Remove events
    success = remover.remove_events(
        remove_invites=args.remove_invites,
        pattern=args.pattern,
        start_date=args.start_date,
        end_date=args.end_date,
        remove_duplicates=args.remove_duplicates,
        keep_categories=args.keep_categories,
        remove_categories=args.remove_categories
    )
    
    if not success:
        logger.error(f"Failed to process calendar: {input_file}")
        return False
    
    # Save cleaned calendar
    if not remover.save_calendar():
        logger.error(f"Failed to save calendar: {input_file}")
        return False
    
    # Save cancellation calendar if events were removed
    if remover.removed_count > 0:
        # Get the removed events from the JSON file
        removed_file = str(output_file).replace('.ics', '_removed_events.json')
        if os.path.exists(removed_file):
            with open(removed_file, 'r') as f:
                removed_events = json.load(f)
            remover.save_cancellation_calendar(removed_events)
    
    # Show statistics
    stats = remover.get_statistics()
    logger.info(f"Completed: {input_file}")
    logger.info(f"  Output: {stats['output_file']}")
    logger.info(f"  Events removed: {stats['events_removed']}")
    logger.info(f"  Events kept: {stats['events_kept']}")
    logger.info(f"  Total processed: {stats['total_processed']}")
    
    return True

def process_batch_files(input_dir, args):
    """Process all ICS files in the input directory."""
    logger.info(f"Starting batch processing of ICS files in: {input_dir}")
    logger.info("=" * 60)
    
    # Get all ICS files in the input directory
    ics_files = list(input_dir.glob("*.ics"))
    
    if not ics_files:
        logger.error(f"No ICS files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(ics_files)} ICS file(s) to process:")
    for file in ics_files:
        logger.info(f"  - {file.name}")
    logger.info("")
    
    # Process each file
    successful_files = 0
    failed_files = 0
    
    for i, ics_file in enumerate(ics_files, 1):
        logger.info(f"Processing file {i}/{len(ics_files)}: {ics_file.name}")
        logger.info("-" * 40)
        
        success = process_single_file(ics_file, args)
        
        if success:
            successful_files += 1
            logger.info(f"✓ Successfully processed: {ics_file.name}")
        else:
            failed_files += 1
            logger.error(f"✗ Failed to process: {ics_file.name}")
        
        logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("BATCH PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files processed: {len(ics_files)}")
    logger.info(f"Successful: {successful_files}")
    logger.info(f"Failed: {failed_files}")
    logger.info(f"Output directory: {args.output_dir}")
    
    return failed_files == 0

def main():
    """Main function to handle command line arguments and run the remover."""
    parser = argparse.ArgumentParser(
        description='Remove calendar invites and events from ICS files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python calendar_invite_remover.py calendar.ics --remove-invites
  
  # Process all files in input_ics_files folder
  python calendar_invite_remover.py --batch --remove-invites
  
  # Process with specific options
  python calendar_invite_remover.py --batch --pattern "zoom|teams|meeting" --start-date 2024-01-01
  
  # Dry run to see what would be removed
  python calendar_invite_remover.py --batch --dry-run --remove-invites
  
  # Single file with pattern matching
  python calendar_invite_remover.py calendar.ics --pattern "zoom|teams|meeting"
  
  # Single file with date range
  python calendar_invite_remover.py calendar.ics --start-date 2024-01-01 --end-date 2024-01-31
        """
    )
    
    # Input options
    parser.add_argument('input_file', nargs='?', help='Input ICS file path (or use --batch for folder processing)')
    parser.add_argument('--batch', action='store_true', help='Process all ICS files in input_ics_files folder')
    parser.add_argument('--input-dir', type=Path, default=Path('input_ics_files'), 
                       help='Input directory containing ICS files (default: input_ics_files)')
    parser.add_argument('--output-dir', type=Path, default=Path('output_ics_files'), 
                       help='Output directory for cleaned files (default: output_ics_files)')
    
    # Processing options
    parser.add_argument('--remove-invites', action='store_true', 
                       help='Remove meeting/invite events (default: False)')
    parser.add_argument('--pattern', help='Regex pattern to match events for removal')
    parser.add_argument('--start-date', help='Start date for filtering (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date for filtering (YYYY-MM-DD)')
    parser.add_argument('--remove-duplicates', action='store_true',
                       help='Remove duplicate events based on summary and time')
    parser.add_argument('--keep-categories', nargs='+', 
                       help='Keep only events with these categories')
    parser.add_argument('--remove-categories', nargs='+',
                       help='Remove events with these categories')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be removed without making changes')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    args.output_dir.mkdir(exist_ok=True)
    
    # Handle batch processing
    if args.batch:
        # Check if input directory exists
        if not args.input_dir.exists():
            logger.error(f"Input directory does not exist: {args.input_dir}")
            logger.error(f"Please create the directory and add ICS files to it.")
            sys.exit(1)
        
        # Process all files in the input directory
        success = process_batch_files(args.input_dir, args)
        if not success:
            sys.exit(1)
        
    else:
        # Single file processing
        if not args.input_file:
            logger.error("Please provide an ICS file path or use --batch for folder processing.")
            logger.error("Usage examples:")
            logger.error("  python calendar_invite_remover.py input.ics")
            logger.error("  python calendar_invite_remover.py --batch")
            sys.exit(1)
        
        # Validate input file
        if not os.path.exists(args.input_file):
            logger.error(f"Input file does not exist: {args.input_file}")
            sys.exit(1)
        
        # Process single file
        success = process_single_file(args.input_file, args)
        if not success:
            sys.exit(1)
    
    logger.info("All processing complete!")

if __name__ == "__main__":
    main() 