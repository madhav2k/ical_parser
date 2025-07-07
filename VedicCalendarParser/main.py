from icaltoJson import convert_ical_to_json, save_json_to_file
from icalParser6 import extract_and_create_events
import os
import sys
import argparse
from datetime import datetime, timedelta
import re
from icalendar import Calendar

def extract_month_from_filename(filename):
    """Extract month information from filename for output naming"""
    # Remove path and extension
    basename = os.path.splitext(os.path.basename(filename))[0]
    
    # Try to extract month from common patterns
    month_patterns = [
        r'(\w+)(\d{4})',  # April2025, March2024, etc.
        r'(\d{1,2})[-_](\d{4})',  # 04-2025, 4_2025, etc.
        r'(\w+)[-_](\d{4})',  # April-2025, March_2024, etc.
    ]
    
    for pattern in month_patterns:
        match = re.search(pattern, basename, re.IGNORECASE)
        if match:
            month_part = match.group(1)
            year_part = match.group(2)
            
            # Convert month name to number if it's a name
            month_names = {
                'january': '01', 'jan': '01',
                'february': '02', 'feb': '02', 
                'march': '03', 'mar': '03',
                'april': '04', 'apr': '04',
                'may': '05',
                'june': '06', 'jun': '06',
                'july': '07', 'jul': '07',
                'august': '08', 'aug': '08',
                'september': '09', 'sep': '09', 'sept': '09',
                'october': '10', 'oct': '10',
                'november': '11', 'nov': '11',
                'december': '12', 'dec': '12'
            }
            
            if month_part.lower() in month_names:
                month_num = month_names[month_part.lower()]
            else:
                # Assume it's already a number
                month_num = month_part.zfill(2)
            
            return f"{month_num}_{year_part}"
    
    # If no pattern matches, use current date
    return datetime.now().strftime("%m_%Y")

def extract_date_range_from_ics(ics_file_path):
    """Extract the date range from an ICS file"""
    try:
        with open(ics_file_path, 'rb') as file:
            cal = Calendar.from_ical(file.read())
        
        dates = []
        for component in cal.walk():
            if component.name == "VEVENT":
                dtstart = component.get('dtstart').dt
                if hasattr(dtstart, 'date'):
                    dates.append(dtstart.date())
                else:
                    dates.append(dtstart)
        
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            return min_date, max_date
        else:
            return None, None
            
    except Exception as e:
        print(f"Warning: Could not extract date range from ICS file: {e}")
        return None, None

def process_single_file(input_file, args):
    """Process a single ICS file and return output file paths"""
    try:
        # Check if the file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' does not exist.")
            return None

        # Auto-detect date range from ICS file if not provided
        start_date = args.start_date
        end_date = args.end_date
        
        if start_date is None or end_date is None:
            print(f"Auto-detecting date range from ICS file: {input_file}")
            min_date, max_date = extract_date_range_from_ics(input_file)
            
            if min_date and max_date:
                if start_date is None:
                    start_date = min_date.strftime('%Y-%m-%d')
                if end_date is None:
                    end_date = max_date.strftime('%Y-%m-%d')
                print(f"Auto-detected date range: {start_date} to {end_date}")
            else:
                print("Warning: Could not auto-detect date range, using defaults")
                if start_date is None:
                    start_date = '2025-03-31'
                if end_date is None:
                    end_date = '2025-05-01'

        # Parse the date arguments
        try:
            requested_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            requested_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError as e:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD format. Error: {e}")
            return None
        
        # Extract year and month from start date for processing
        requested_year = requested_start_date.year
        requested_month = requested_start_date.month

        # Always add a day to the end date for extraction/patching
        processing_start_date = requested_start_date
        processing_end_date = requested_end_date + timedelta(days=1)

        # Extract month information from filename for output naming
        month_suffix = extract_month_from_filename(input_file)
        
        print(f"Processing ICS file: {input_file}")
        print(f"Date range: {requested_start_date.strftime('%Y-%m-%d')} to {requested_end_date.strftime('%Y-%m-%d')}")
        print(f"Year: {requested_year}, Month: {requested_month}")
        print(f"Output files will include month suffix: {month_suffix}")
        if args.no_hora:
            print("Hora events generation: DISABLED")
        else:
            print("Hora events generation: ENABLED")

        # Step 1: Convert ICS to JSON
        json_file_path = os.path.join(args.output_dir, f'{args.output_prefix}_{month_suffix}_events.json')

        print(f"Converting ICS to JSON from {input_file}...")
        events = convert_ical_to_json(input_file)
        if not events:
            print("Error: No events were found in the ICS file.")
            return None

        save_json_to_file(events, json_file_path)
        print(f"JSON file created successfully at {json_file_path}.")

        # Step 2: Convert JSON to ICS
        print("Converting JSON to ICS...")
        ics_calendar, hora_calendar = extract_and_create_events(
            events,
            processing_start_date,
            processing_end_date,
            requested_year,
            requested_month,
            requested_start_date,
            requested_end_date
        )
        if not ics_calendar:
            print("Error: Failed to create ICS calendar from events.")
            return None

        # Save the original events
        output_ics_path = os.path.join(args.output_dir, f'{args.output_prefix}_{month_suffix}_events.ics')
        with open(output_ics_path, 'wb') as ics_file:
            ics_file.write(ics_calendar.to_ical())
        print(f"Vedic events saved to {output_ics_path}")

        # Save the hora events only if not disabled
        output_files = [json_file_path, output_ics_path]
        if not args.no_hora and hora_calendar:
            hora_ics_path = os.path.join(args.output_dir, f'{args.output_prefix}_{month_suffix}_hora_events.ics')
            with open(hora_ics_path, 'wb') as ics_file:
                ics_file.write(hora_calendar.to_ical())
            print(f"Hora events saved to {hora_ics_path}")
            output_files.append(hora_ics_path)
        elif args.no_hora:
            print("Skipped hora events generation (--no-hora flag used)")
        else:
            print("No hora events were generated (API may be unavailable)")
        
        print(f"Processing complete for {input_file}!")
        return output_files

    except Exception as e:
        print(f"An error occurred while processing {input_file}: {e}")
        return None

def process_batch_files(input_dir, args):
    """Process all ICS files in the input directory"""
    print(f"Starting batch processing of ICS files in: {input_dir}")
    print("=" * 60)
    
    # Get all ICS files in the input directory
    ics_files = []
    for file in os.listdir(input_dir):
        if file.lower().endswith('.ics'):
            ics_files.append(os.path.join(input_dir, file))
    
    if not ics_files:
        print(f"No ICS files found in {input_dir}")
        return
    
    print(f"Found {len(ics_files)} ICS file(s) to process:")
    for file in ics_files:
        print(f"  - {os.path.basename(file)}")
    print()
    
    # Process each file
    successful_files = 0
    failed_files = 0
    all_output_files = []
    
    for i, ics_file in enumerate(ics_files, 1):
        print(f"Processing file {i}/{len(ics_files)}: {os.path.basename(ics_file)}")
        print("-" * 40)
        
        output_files = process_single_file(ics_file, args)
        
        if output_files:
            successful_files += 1
            all_output_files.extend(output_files)
            print(f"✓ Successfully processed: {os.path.basename(ics_file)}")
        else:
            failed_files += 1
            print(f"✗ Failed to process: {os.path.basename(ics_file)}")
        
        print()
    
    # Summary
    print("=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(ics_files)}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")
    print(f"Output directory: {args.output_dir}")
    print(f"Total output files created: {len(all_output_files)}")
    
    if all_output_files:
        print("\nOutput files created:")
        for file_path in all_output_files:
            print(f"  - {file_path}")

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Vedic Calendar Parser - Process ICS files for Vedic calendar events')
    parser.add_argument('ics_file', nargs='?', default=None, 
                       help='Path to the ICS file to process (or use --batch for folder processing)')
    parser.add_argument('--batch', action='store_true',
                       help='Process all ICS files in input_ics_files folder')
    parser.add_argument('--input-dir', type=str, default='input_ics_files',
                       help='Input directory containing ICS files (default: input_ics_files)')
    parser.add_argument('--output-dir', type=str, default='output_ics_files',
                       help='Output directory for generated files (default: output_ics_files)')
    parser.add_argument('--start-date', type=str, default=None,
                       help='Start date for processing in YYYY-MM-DD format (auto-detected if not provided)')
    parser.add_argument('--end-date', type=str, default=None,
                       help='End date for processing in YYYY-MM-DD format (auto-detected if not provided)')
    parser.add_argument('--output-prefix', type=str, default='vedic',
                       help='Prefix for output files (default: vedic)')
    parser.add_argument('--no-hora', action='store_true',
                       help='Skip generation of hora events (useful when API is unavailable)')
    
    args = parser.parse_args()
    
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
            print(f"Created output directory: {args.output_dir}")
        
        # Handle batch processing
        if args.batch:
            # Check if input directory exists
            if not os.path.exists(args.input_dir):
                print(f"Error: Input directory '{args.input_dir}' does not exist.")
                print(f"Please create the directory and add ICS files to it.")
                sys.exit(1)
            
            # Process all files in the input directory
            process_batch_files(args.input_dir, args)
            
        else:
            # Single file processing
            if args.ics_file is None:
                print("Error: Please provide an ICS file path or use --batch for folder processing.")
                print("Usage examples:")
                print("  python main.py input.ics")
                print("  python main.py --batch")
                print("  python main.py --batch --input-dir my_input_folder --output-dir my_output_folder")
                sys.exit(1)
            
            # Process single file
            output_files = process_single_file(args.ics_file, args)
            
            if output_files:
                print(f"\nProcessing complete! Output files:")
                for file_path in output_files:
                    print(f"  - {file_path}")
            else:
                print("Processing failed.")
                sys.exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()