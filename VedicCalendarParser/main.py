from icaltoJson import convert_ical_to_json, save_json_to_file
from icalParser6 import extract_and_create_events
import os
import sys
from datetime import datetime

def main():
    try:
        # Use April2025.ics as the default input file
        input_file = 'April2025.ics'
        if not os.path.exists(input_file):
            print(f"Error: Default input file '{input_file}' does not exist.")
            sys.exit(1)

        # Set date range for April 2025
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 30)

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
        ics_calendar, hora_calendar = extract_and_create_events(events, start_date, end_date)
        if not ics_calendar or not hora_calendar:
            print("Error: Failed to create ICS calendars from events.")
            return

        # Save the original events
        output_ics_path = 'vedic_events.ics'
        with open(output_ics_path, 'wb') as ics_file:
            ics_file.write(ics_calendar.to_ical())
        print(f"Original events saved to {output_ics_path}")

        # Save the hora events
        hora_ics_path = 'hora_events.ics'
        with open(hora_ics_path, 'wb') as ics_file:
            ics_file.write(hora_calendar.to_ical())
        print(f"Hora events saved to {hora_ics_path}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()