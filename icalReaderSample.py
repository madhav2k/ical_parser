# imports
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime
from pathlib import Path
import os
import pytz

# init the calendar
cal = Calendar()

# Some properties are required to be compliant
cal.add('prodid', '-//My calendar product//example.com//')
cal.add('version', '2.0')

# Add subcomponents
event = Event()

e = open('MyCalendar/example.ics', 'rb')
ecal = cal.from_ical(e.read())
for component in ecal.walk():
   if component.name == "VEVENT":
       print(component.get("name"))
       print(component.get("description"))
       print(component.get("organizer"))
       print(component.get("location"))
       print(component.decoded("dtstart"))
       print(component.decoded("dtend"))
e.close()
