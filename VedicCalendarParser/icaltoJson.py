import json
from icalendar import Calendar, Event

def convert_ical_to_json(ical_file_path):
    """
    Converts an ICS file to a JSON format.
    """
    with open(ical_file_path, 'rb') as ics_file:
        calendar = Calendar.from_ical(ics_file.read())
        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                event = {
                    "summary": str(component.get("summary", "")),
                    "dtstart": str(component.get("dtstart").dt) if component.get("dtstart") else "",
                    "dtend": str(component.get("dtend").dt) if component.get("dtend") else "",
                    "description": str(component.get("description", "")),
                }
                events.append(event)
        return events

def save_json_to_file(events, output_file_path):
    """
    Saves a list of events in JSON format to a file.
    """
    with open(output_file_path, 'w') as json_file:
        json.dump(events, json_file, indent=4)