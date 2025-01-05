# imports
from icalendar import Calendar, Event, vCalAddress, vText, vDatetime
from datetime import date
from datetime import datetime
from pathlib import Path
import os
import pytz
import re

# init the calendar
cal = Calendar()
calOut = Calendar()

# Some properties are required to be compliant
cal.add('prodid', '-//My calendar product//example.com//')
cal.add('version', '2.0')

# Some properties are required to be compliant
calOut.add('prodid', '-//My calendar product//example.com//')
calOut.add('version', '2.0')

# Add subcomponents
event = Event()

e = open('MyCalendar/Drik - 2024.ics', 'rb')
ecal = cal.from_ical(e.read())

directory = Path.cwd() / 'CalendarOut'
try:
   directory.mkdir(parents=True, exist_ok=False)
except FileExistsError:
   print("Folder "+str(directory)+" already exists")
else:
   print("Folder "+str(directory)+" was created")
f = open(os.path.join(directory, 'example.ics'), 'wb')

#Loop through the entire year's calendar
loopCtr = 0
for component in ecal.walk():

   if loopCtr > 2: 
      break
   if component.name == "VEVENT":
       loopCtr +=1
       eventName = component.get("name")
       eventStart = component.decoded("dtstart")
       print("printing what I got from calendar "+str(eventStart))
       
       #Convert drik date format to standard date
       eventStartObj = date.fromisoformat(str(eventStart))
       print("printing date in "+str(eventStartObj))
       
       #Parse the drik event to extract events of interest
       eventDescription = component.get("description")
      
       #descriprion has CSV events. loop through them
       lines = eventDescription.splitlines()
       print(lines)

       ctr=0

       f.write(calOut.to_ical())
       for element in lines:
          if re.match(r'^Dur', element) or re.match(r'^Var', element):
            durVarArray = element.split("-") 
            durVarFromTo = durVarArray[1].split("to")
            print("array of event start and end times from description")
            print(durVarFromTo)
            ctr+=1
            tz = pytz.timezone('America/Los_Angeles')

            militaryTimeStart = datetime.strptime(durVarFromTo[0].replace(" ", ""), '%I:%M%p').strftime('%H:%M')
            print(f"regular time is: {durVarFromTo[0]}")
            print(f"military time start is "+ militaryTimeStart)
            tzinfo=pytz.timezone('US/Pacific')
            
            #Process start date
            eventStartDateTime_str = str(eventStart)+"T"+militaryTimeStart
            eventStartDateTime = tzinfo.localize(datetime.fromisoformat(eventStartDateTime_str))
            print("event start date time is "+str(eventStartDateTime))
            
            event.add('name', 'Dur'+str(ctr))
            event.add('dtstart',vDatetime(eventStartDateTime) )
            
            #Process end date 
            dateShift = durVarFromTo[1].split(",")
            if (len(dateShift) > 1):
               print("Found more elements in the end time")
               print(dateShift[1])  
            
            militaryTimeEnd = datetime.strptime(dateShift[0].replace(" ", ""), '%I:%M%p').strftime('%H:%M')
            print(f"regular end time is: {durVarFromTo[1]}")
            print(f"military time end is "+ militaryTimeEnd)
            eventEndDateTime_str = str(eventStart)+"T"+militaryTimeEnd
            eventEndDateTime = tzinfo.localize(datetime.fromisoformat(eventEndDateTime_str))
            event.add('dtend',vDatetime(eventEndDateTime) )

            eventLocation = component.get("location")
            #eventStart = component.decoded("dtstart")
            print(event)
            # Add the event to the calendar
            calOut.add_component(event)
            f.write(cal.to_ical())
f.close()
e.close()
