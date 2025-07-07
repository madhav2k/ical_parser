#!/usr/bin/env python3
"""
Outlook Event Manager - Complete Workflow
Python Script for Managing Vedic Calendar Events in Outlook

This script performs three main operations:
1. Creates cancellation events for existing events in Outlook
2. Makes all events private in the ICS files
3. Provides import instructions for Windows Outlook
"""

import os
import sys
import logging
from pathlib import Path
from icalendar import Calendar, Event
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OutlookEventManager:
    def __init__(self, input_dir="VedicCalendarParser/input_ics_files/invites", 
                 output_dir="output_ics_files/cancellations"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
    def check_prerequisites(self):
        """Check if Python and required packages are available"""
        try:
            import icalendar
            logger.info("✓ icalendar package found")
            return True
        except ImportError:
            logger.error("❌ ERROR: icalendar package not installed")
            logger.error("Please install it with: pip install icalendar")
            return False
    
    def initialize_directories(self):
        """Create output directory if it doesn't exist"""
        if not self.output_dir.exists():
            logger.info(f"Creating output directory: {self.output_dir}")
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Current settings:")
        logger.info(f"  Input directory: {self.input_dir}")
        logger.info(f"  Output directory: {self.output_dir}")
    
    def get_ics_files(self):
        """Get all ICS files from input directory"""
        if not self.input_dir.exists():
            logger.error(f"Input directory not found: {self.input_dir}")
            return []
        
        ics_files = list(self.input_dir.glob("*.ics"))
        
        if not ics_files:
            logger.warning(f"No ICS files found in {self.input_dir}")
            return []
        
        logger.info(f"Found {len(ics_files)} ICS file(s) in {self.input_dir}")
        logger.info("Files to process:")
        for ics_file in ics_files:
            logger.info(f"  - {ics_file.name}")
        
        return ics_files
    
    def create_cancellation_calendar(self, original_calendar, filename):
        """Create a cancellation calendar from an original calendar"""
        cancellation_calendar = Calendar()
        cancellation_calendar.add('prodid', '-//Calendar Cancellation Generator//EN')
        cancellation_calendar.add('version', '2.0')
        cancellation_calendar.add('calscale', 'GREGORIAN')
        cancellation_calendar.add('method', 'CANCEL')
        
        event_count = 0
        for component in original_calendar.walk():
            if component.name == "VEVENT":
                cancel_event = Event()
                
                # Copy essential fields
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
                
                # Add cancellation-specific fields
                cancel_event.add('status', 'CANCELLED')
                cancel_event.add('class', 'PRIVATE')
                
                cancellation_calendar.add_component(cancel_event)
                event_count += 1
                logger.info(f"Created cancellation for event: {summary} (UID: {uid})")
        
        logger.info(f"Total events processed: {event_count}")
        return cancellation_calendar
    
    def step1_create_cancellations(self):
        """Step 1: Create cancellation events for existing events"""
        print("=" * 40)
        print("STEP 1: Creating Cancellation Events")
        print("=" * 40)
        print()
        
        ics_files = self.get_ics_files()
        if not ics_files:
            return False
        
        successful_files = 0
        for ics_file in ics_files:
            try:
                logger.info(f"Processing: {ics_file}")
                
                with open(ics_file, 'rb') as file:
                    original_calendar = Calendar.from_ical(file.read())
                
                filename = ics_file.stem
                cancellation_calendar = self.create_cancellation_calendar(original_calendar, filename)
                
                output_filename = f"{filename}_cancellations.ics"
                output_path = self.output_dir / output_filename
                
                with open(output_path, 'wb') as file:
                    file.write(cancellation_calendar.to_ical())
                
                logger.info(f"Created cancellation file: {output_path}")
                successful_files += 1
                
            except Exception as e:
                logger.error(f"Error processing {ics_file}: {e}")
        
        logger.info(f"Successfully processed {successful_files}/{len(ics_files)} files")
        return successful_files > 0
    
    def step2_make_events_private(self):
        """Step 2: Make all events private"""
        print("=" * 40)
        print("STEP 2: Making Events Private")
        print("=" * 40)
        print()
        
        ics_files = self.get_ics_files()
        if not ics_files:
            return False
        
        successful_files = 0
        for ics_file in ics_files:
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
                successful_files += 1
                
            except Exception as e:
                logger.error(f"Error processing {ics_file}: {e}")
        
        logger.info(f"Successfully processed {successful_files}/{len(ics_files)} files")
        return successful_files > 0
    
    def step3_show_instructions(self):
        """Step 3: Show import instructions"""
        print("=" * 40)
        print("STEP 3: Import Instructions")
        print("=" * 40)
        print()
        
        # Show cancellation files
        cancellation_files = list(self.output_dir.glob("*_cancellations.ics"))
        if cancellation_files:
            print("Cancellation files created:")
            for file in cancellation_files:
                print(f"  - {file.name}")
            print()
        
        # Show updated files
        updated_files = list(self.input_dir.glob("*.ics"))
        if updated_files:
            print("Updated private files:")
            for file in updated_files:
                print(f"  - {file.name}")
            print()
        
        print("=" * 40)
        print("    WINDOWS OUTLOOK IMPORT INSTRUCTIONS")
        print("=" * 40)
        print()
        
        if cancellation_files:
            print("STEP 1: Remove Existing Events (if any exist in Outlook)")
            print("1. Open Outlook")
            print("2. Go to File → Open & Export → Import/Export")
            print("3. Choose 'Import an iCalendar (.ics) file'")
            print(f"4. Select the cancellation files from: {self.output_dir}")
            print("5. Choose your calendar and import")
            print("6. This will remove any existing events with matching UIDs")
            print()
        
        print("STEP 2: Import Private Events")
        print("1. In Outlook, go to File → Open & Export → Import/Export")
        print("2. Choose 'Import an iCalendar (.ics) file'")
        print(f"3. Select the updated private files from: {self.input_dir}")
        print("4. Choose your calendar and import")
        print("5. All events will now be marked as PRIVATE")
        print()
        
        print("=" * 40)
        print("    ALTERNATIVE: Batch Import")
        print("=" * 40)
        print()
        
        print("If you want to import all files at once:")
        print("1. Select multiple .ics files in File Explorer")
        print("2. Right-click → 'Open with' → Outlook")
        print("3. Outlook will import all selected files")
        print()
        
        print("=" * 40)
        print("    TROUBLESHOOTING")
        print("=" * 40)
        print()
        
        print("If import fails:")
        print("- Try importing one file at a time")
        print("- Check if events already exist with same UIDs")
        print("- Try the cancellation files first, then the private files")
        print("- Some calendar apps may not support all ICS features")
    
    def run_complete_workflow(self):
        """Run all three steps"""
        if not self.check_prerequisites():
            return False
        
        self.initialize_directories()
        
        step1_success = self.step1_create_cancellations()
        step2_success = self.step2_make_events_private()
        
        if step1_success and step2_success:
            self.step3_show_instructions()
            return True
        else:
            print("Some steps failed. Check the output above.")
            return False
    
    def show_menu(self):
        """Show interactive menu"""
        while True:
            print("\nChoose an option:")
            print("1. Run complete workflow (all 3 steps)")
            print("2. Step 1 only: Create cancellation events")
            print("3. Step 2 only: Make events private")
            print("4. Step 3 only: Show import instructions")
            print("5. Exit")
            print()
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                self.run_complete_workflow()
            elif choice == "2":
                if self.check_prerequisites():
                    self.initialize_directories()
                    self.step1_create_cancellations()
            elif choice == "3":
                if self.check_prerequisites():
                    self.initialize_directories()
                    self.step2_make_events_private()
            elif choice == "4":
                self.step3_show_instructions()
            elif choice == "5":
                print("\nThank you for using Outlook Event Manager!")
                break
            else:
                print("Invalid choice. Please try again.")
            
            if choice != "5":
                print()
                continue_input = input("Press Enter to continue or 'q' to quit: ")
                if continue_input.lower() == 'q':
                    break

def main():
    parser = argparse.ArgumentParser(description="Outlook Event Manager - Complete Workflow")
    parser.add_argument("--input-dir", default="VedicCalendarParser/input_ics_files/invites",
                       help="Input directory containing ICS files")
    parser.add_argument("--output-dir", default="output_ics_files/cancellations",
                       help="Output directory for cancellation files")
    parser.add_argument("--step", choices=["1", "2", "3", "all"], default="all",
                       help="Which step to run (1=cancellations, 2=private, 3=instructions, all=complete workflow)")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode with menu")
    
    args = parser.parse_args()
    
    print("=" * 40)
    print("   Outlook Event Manager")
    print("   Complete Workflow Script")
    print("=" * 40)
    print()
    
    manager = OutlookEventManager(args.input_dir, args.output_dir)
    
    if args.interactive:
        manager.show_menu()
    else:
        if args.step == "all":
            manager.run_complete_workflow()
        elif args.step == "1":
            if manager.check_prerequisites():
                manager.initialize_directories()
                manager.step1_create_cancellations()
        elif args.step == "2":
            if manager.check_prerequisites():
                manager.initialize_directories()
                manager.step2_make_events_private()
        elif args.step == "3":
            manager.step3_show_instructions()

if __name__ == "__main__":
    main() 