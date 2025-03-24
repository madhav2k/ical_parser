from icaltoJson import convert_ical_to_json, save_json_to_file
from icalParser6 import extract_and_create_events
import os
import sys

def validate_ics_file(file_path):
    """Validate that the file exists and has .ics extension."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False
    
    if not file_path.lower().endswith('.ics'):
        print(f"Error: File '{file_path}' is not an ICS file. Please provide a file with .ics extension.")
        return False
    
    return True

def get_input_file():
    """Get input file path from user with validation."""
    while True:
        file_path = input("Please enter the path to your ICS file: ").strip()
        if validate_ics_file(file_path):
            return file_path
        print("Please try again with a valid ICS file path.")

def main():
    try:
        # Get input file from user
        input_file = get_input_file()

        # Step 1: Convert ICS to JSON
        json_file_path = 'icalJson.json'

        print(f"Converting ICS to JSON from {input_file}...")
        events = convert_ical_to_json(input_file)
        if not events:
            print("Error: No events were found in the ICS file.")
            return

        save_json_to_file(events, json_file_path)
        print(f"JSON file created successfully at {json_file_path}.")

        # Step 2: Convert JSON to ICS
        print("Converting JSON to ICS...")
        ics_calendar = extract_and_create_events(events)
        if not ics_calendar:
            print("Error: Failed to create ICS calendar from events.")
            return

        output_ics_path = 'BlockingDVEvents.ics'
        with open(output_ics_path, 'wb') as ics_file:
            ics_file.write(ics_calendar.to_ical())
        print(f"ICS file created successfully at {output_ics_path}.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()