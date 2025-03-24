from icaltoJson import convert_ical_to_json, save_json_to_file
from icalParser6 import extract_and_create_events

def main():
    # Step 1: Convert ICS to JSON
    ical_file_path = 'input.ics'  # Replace with your ICS file path
    json_file_path = 'icalJson.json'

    print("Converting ICS to JSON...")
    events = convert_ical_to_json(ical_file_path)
    save_json_to_file(events, json_file_path)
    print(f"JSON file created successfully at {json_file_path}.")

    # Step 2: Convert JSON to ICS
    print("Converting JSON to ICS...")
    ics_calendar = extract_and_create_events(events)
    output_ics_path = 'BlockingDVEvents.ics'

    with open(output_ics_path, 'wb') as ics_file:
        ics_file.write(ics_calendar.to_ical())
    print(f"ICS file created successfully at {output_ics_path}.")

if __name__ == "__main__":
    main()