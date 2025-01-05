import json
from icalendar import Calendar, Event

def parse_ics_to_json(ics_file_path):
    with open(ics_file_path, 'r') as file:
        gcal = Calendar.from_ical(file.read())

    events = []
    for component in gcal.walk():
        if component.name == "VEVENT":
            event = {
                "summary": str(component.get("summary")),
                "dtstart": str(component.get("dtstart").dt) if component.get("dtstart") else None,
                "dtend": str(component.get("dtend").dt) if component.get("dtend") else None,
                "location": str(component.get("location")) if component.get("location") else None,
                "description": str(component.get("description")) if component.get("description") else None
            }
            events.append(event)

    return json.dumps(events, indent=4)

# Example usage
ics_file_path = 'Drik - 2024.ics'
json_output = parse_ics_to_json(ics_file_path)
print(json_output)
