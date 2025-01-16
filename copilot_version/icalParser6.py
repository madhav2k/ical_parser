import json
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import random

def create_ics_event(start_time, end_time, date, summary):
    """
    Function to create an ICS event.
    - Adjusts the date if start_time or end_time contains a comma.
    - Creates an event with the given start time, end time, date, and summary.
    """
    # Check if start_time has a comma and adjust the date accordingly
    if ',' in start_time:
        start_time = start_time.split(',')[0].strip()
        date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # Check if end_time has a comma and adjust the date accordingly
    if ',' in end_time:
        end_time = end_time.split(',')[0].strip()
        date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # Create the event
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %I:%M %p"))
    event.add('dtend', datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %I:%M %p"))
    event.add('class', 'PRIVATE')  # Mark the event as private
    return event

def extract_and_create_events(events):
    """
    Function to extract 'Dur Muhurtamulu' and 'Varjyam' events from the given events list.
    - Creates ICS events for each 'Dur Muhurtamulu' and 'Varjyam' entry.
    """
    cal = Calendar()
    dur_acronyms = ["DUR", "DUM", "DUN", "DUS", "DUT"]  # Example acronyms starting with 'D'
    var_acronyms = ["VAR", "VAX", "VIN", "VET", "VIV"]  # Example acronyms starting with 'V'

    for event in events:
        description = event.get("description", "")
        dtstart = event.get("dtstart", "")

        if not dtstart:
            continue

        lines = description.split("\n")
        for line in lines:
            if "Dur Muhurtamulu" in line:
                times = line.split("-")[1].strip()
                start_time, end_time = times.split(" to ")
                acronym = random.choice(dur_acronyms)
                ics_event = create_ics_event(start_time.strip(), end_time.strip(), dtstart, acronym)
                cal.add_component(ics_event)
            elif "Varjyam" in line:
                times = line.split("-")[1].strip()
                start_time, end_time = times.split(" to ")
                acronym = random.choice(var_acronyms)
                ics_event = create_ics_event(start_time.strip(), end_time.strip(), dtstart, acronym)
                cal.add_component(ics_event)

    return cal

# Read JSON file
with open('icalJson.json', 'r') as file:
    events = json.load(file)

# Extract and create ICS events
ics_calendar = extract_and_create_events(events)

# Write to ICS file
with open('BlockingDVEvents.ics', 'wb') as ics_file:
    ics_file.write(ics_calendar.to_ical())

print("ICS file created successfully.")