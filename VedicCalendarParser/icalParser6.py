import json
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import random
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from hora_calc import VedicAstroClient, HoraCalendar, Location, calculate_hora_for_date
except ImportError:
    # For testing purposes, use mock module
    from tests.mock_hora_calc import VedicAstroClient, HoraCalendar, Location, calculate_hora_for_date

import re
import logging
from config import DEBUG_MODE

# Set up logging
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'vedic_calendar.log')
# Clear the log file at the start of each run
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  # Use mode='w' to overwrite
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)

# Read nakshatras from file
with open(os.path.join(os.path.dirname(__file__), 'nakshatras.txt'), 'r') as f:
    SPECIAL_NAKSHATRAS = [line.strip().lower() for line in f.readlines()]
logger.info(f"Loaded special nakshatras: {SPECIAL_NAKSHATRAS}")

def extract_nakshatra_from_description(description):
    """
    Extract nakshatra names and their corresponding end times from a description string.
    Returns a list of tuples containing (nakshatra, end_time, next_date).
    """
    if not description:
        return []

    nakshatras = []
    lines = description.split('\n')
    
    for line in lines:
        if 'Nakshatramulu' in line:
            # Extract nakshatra periods - using a more flexible regex pattern
            # This will capture both "Nakshatra - time" and "Nakshatra upto time" formats
            # Also handles potential date information
            periods = re.findall(r'([A-Za-z]+)\s+(?:-|upto)\s+(\d{1,2}:\d{2}\s*[AP]M)(?:,?\s*([A-Za-z]{3}\s*\d{1,2}))?', line)
            
            # Log the raw extracted periods for debugging
            logger.info(f"Raw nakshatra periods found in line: {periods}")
            
            for nakshatra, time_str, date_str in periods:
                # Normalize nakshatra name to match the list
                nakshatra = nakshatra.lower().strip()
                time_str = time_str.strip()
                
                # Log individual extraction
                logger.info(f"Extracted nakshatra: {nakshatra}, time: {time_str}, date: {date_str}")
                
                # Check if this is a special nakshatra
                is_special = nakshatra in SPECIAL_NAKSHATRAS
                if is_special:
                    logger.info(f"Found special nakshatra: {nakshatra}")
                
                nakshatras.append((nakshatra, time_str, date_str))
    
    return nakshatras

def create_ics_event(start_time, end_time, base_date, summary, description=None, categories=None):
    try:
        # Check if start_time and end_time are datetime objects
        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            event = Event()
            event.add('summary', summary)
            event.add('dtstart', start_time)
            event.add('dtend', end_time)
            if description:
                event.add('description', description)
            if categories:
                event.add('categories', categories)
            event.add('transp', 'OPAQUE')
            return event

        # Handle string inputs
        if isinstance(start_time, str) and isinstance(end_time, str):
            # Extract date from time strings if present
            start_date = base_date
            end_date = base_date
            
            # Check for explicit date in start time
            if ',' in start_time:
                time_part, date_part = start_time.split(',')
                start_time = time_part.strip()
                # Parse the date part (e.g., "Apr 02")
                try:
                    month_day = date_part.strip().split()
                    if len(month_day) == 2:
                        month = month_day[0]
                        day = int(month_day[1])
                        start_date = datetime(base_date.year, datetime.strptime(month, "%b").month, day)
                except ValueError:
                    pass

            # Check for explicit date in end time
            if ',' in end_time:
                time_part, date_part = end_time.split(',')
                end_time = time_part.strip()
                # Parse the date part (e.g., "Apr 02")
                try:
                    month_day = date_part.strip().split()
                    if len(month_day) == 2:
                        month = month_day[0]
                        day = int(month_day[1])
                        end_date = datetime(base_date.year, datetime.strptime(month, "%b").month, day)
                except ValueError:
                    pass

            # Parse the time components
            try:
                start_dt = datetime.strptime(start_time, "%I:%M:%S %p")
                end_dt = datetime.strptime(end_time, "%I:%M:%S %p")
            except ValueError:
                try:
                    start_dt = datetime.strptime(start_time, "%I:%M %p")
                    end_dt = datetime.strptime(end_time, "%I:%M %p")
                except ValueError as e:
                    logging.error(f"Error creating event: Invalid time format - {str(e)}")
                    logging.error(f"Start time: {start_time}, End time: {end_time}")
                    return None

            # Create datetime objects with the appropriate dates
            start_datetime = datetime.combine(start_date.date(), start_dt.time())
            end_datetime = datetime.combine(end_date.date(), end_dt.time())

            # Handle cases where end time is before start time (overnight events)
            if end_datetime <= start_datetime and end_date == start_date:
                # If no explicit date was given for end time, assume it's the next day
                end_datetime = end_datetime + timedelta(days=1)

            # Create the event
            event = Event()
            event.add('summary', summary)
            event.add('dtstart', start_datetime)
            event.add('dtend', end_datetime)
            if description:
                event.add('description', description)
            if categories:
                event.add('categories', categories)
            event.add('transp', 'OPAQUE')
            
            logging.info(f"Created event: {summary} from {start_datetime} to {end_datetime}")
            return event

    except Exception as e:
        logging.error(f"Error creating event: {str(e)}")
        logging.error(f"Start time: {start_time}, End time: {end_time}")
        return None

def extract_and_create_events(events_list, start_date, end_date):
    """Extract events from calendar data and create ICS events."""
    # Initialize calendars
    regular_calendar = Calendar()
    hora_calendar = Calendar()
    
    # Add calendar properties
    regular_calendar.add('prodid', '-//Vedic Calendar//EN')
    regular_calendar.add('version', '2.0')
    hora_calendar.add('prodid', '-//Vedic Calendar Hora//EN')
    hora_calendar.add('version', '2.0')
    
    # Generate a dictionary of processed events by date
    calendar_data = {}
    
    # First pass: collect all nakshatra information by date
    for event_data in events_list:
        description = event_data.get("description", "")
        dtstart = event_data.get("dtstart", "")
        
        if not dtstart:
            continue
        
        # Convert date string to datetime object
        try:
            date_obj = datetime.strptime(dtstart, "%Y-%m-%d")
            date_str = date_obj.strftime('%d/%m/%Y')
            
            # Initialize date entry if not exists
            if date_str not in calendar_data:
                calendar_data[date_str] = {
                    'nakshatra_periods': [],
                    'regular_events': []
                }
            
            # Extract nakshatra information
            nakshatras = extract_nakshatra_from_description(description)
            for nakshatra, time_str, date_str_from_desc in nakshatras:
                try:
                    # Parse the end time
                    time_format = "%I:%M %p"
                    end_time = datetime.strptime(time_str, time_format)
                    
                    # Add to nakshatra periods
                    calendar_data[date_str]['nakshatra_periods'].append({
                        'nakshatra': nakshatra,
                        'end_time': end_time.strftime('%H:%M')
                    })
                    
                    logger.info(f"Added nakshatra period: {nakshatra} ending at {end_time.strftime('%H:%M')} for {date_str}")
                except ValueError as e:
                    logger.error(f"Error parsing time {time_str}: {e}")
                    continue
            
            # Extract regular events (Dur Muhurtamulu and Varjyam)
            for line in description.split('\n'):
                if 'Dur Muhurtamulu' in line:
                    match = re.search(r'Dur Muhurtamulu - (\d{1,2}:\d{2} [AP]M) to (\d{1,2}:\d{2} [AP]M)', line)
                    if match:
                        start_time = match.group(1)
                        end_time = match.group(2)
                        
                        # Convert to 24-hour format
                        start_24h = datetime.strptime(start_time, "%I:%M %p").strftime('%H:%M')
                        end_24h = datetime.strptime(end_time, "%I:%M %p").strftime('%H:%M')
                        
                        calendar_data[date_str]['regular_events'].append({
                            'type': 'DUS',
                            'start_time': start_24h,
                            'end_time': end_24h
                        })
                        
                        logger.info(f"Added Dur Muhurtamulu event: {start_time} to {end_time} for {date_str}")
                
                elif 'Varjyam' in line:
                    match = re.search(r'Varjyam - (\d{1,2}:\d{2} [AP]M) to (\d{1,2}:\d{2} [AP]M)', line)
                    if match:
                        start_time = match.group(1)
                        end_time = match.group(2)
                        
                        # Convert to 24-hour format
                        start_24h = datetime.strptime(start_time, "%I:%M %p").strftime('%H:%M')
                        end_24h = datetime.strptime(end_time, "%I:%M %p").strftime('%H:%M')
                        
                        calendar_data[date_str]['regular_events'].append({
                            'type': 'VAR',
                            'start_time': start_24h,
                            'end_time': end_24h
                        })
                        
                        logger.info(f"Added Varjyam event: {start_time} to {end_time} for {date_str}")
            
        except ValueError as e:
            logger.error(f"Error parsing date {dtstart}: {e}")
            continue
    
    # Define special nakshatra transitions
    SPECIAL_NAKSHATRA_TRANSITIONS = []
    for nakshatra in SPECIAL_NAKSHATRAS:
        for next_nakshatra in SPECIAL_NAKSHATRAS:
            if nakshatra != next_nakshatra:
                SPECIAL_NAKSHATRA_TRANSITIONS.append((nakshatra, next_nakshatra))
    
    logger.info(f"Created {len(SPECIAL_NAKSHATRA_TRANSITIONS)} special nakshatra transition combinations")
    
    # Process each date in the range
    current_date = start_date
    while current_date <= end_date:
        # Get events for current date
        date_str = current_date.strftime('%d/%m/%Y')
        events = calendar_data.get(date_str, {})
        
        # Process nakshatra periods
        nakshatras = events.get('nakshatra_periods', [])
        if nakshatras:
            # Sort nakshatras by end_time
            nakshatras.sort(key=lambda x: datetime.strptime(x['end_time'], '%H:%M'))
            
            # Process each special nakshatra (not just transitions)
            for i in range(len(nakshatras)):
                current_nakshatra = nakshatras[i]['nakshatra']
                
                # Check if the current nakshatra is in the special list
                if current_nakshatra in SPECIAL_NAKSHATRAS:
                    logger.info(f"Found special nakshatra: {current_nakshatra}")
                    
                    # Set start_time and end_time for the special nakshatra period
                    start_time = datetime.strptime('00:00', '%H:%M') if i == 0 else datetime.strptime(nakshatras[i-1]['end_time'], '%H:%M')
                    end_time = datetime.strptime(nakshatras[i]['end_time'], '%H:%M')
                    
                    # Create datetime objects for the period
                    period_start = datetime.combine(current_date, start_time.time())
                    period_end = datetime.combine(current_date, end_time.time())
                    
                    # If end time is before start time, it's the next day
                    if period_end < period_start:
                        period_end += timedelta(days=1)
                    
                    logger.info(f"Calculating hora events from {period_start} to {period_end}")
                    
                    # Get hora data from API
                    client = VedicAstroClient()
                    location = Location(37.33939, -121.89496)  # San Jose coordinates
                    hora_result = calculate_hora_for_date(client, location, period_start)
                    
                    if hora_result and hora_result.get('status') == 200:
                        hora_data = hora_result.get('response', {}).get('horas', [])
                        logger.info(f"Received {len(hora_data)} hora events from API")
                        
                        # Process each hora period
                        for hora in hora_data:
                            logger.info(f"Raw hora data - start: {hora.get('start')}, end: {hora.get('end')}, planet: {hora.get('hora')}")
                            
                            # Parse datetime strings
                            try:
                                start_dt = datetime.strptime(hora.get('start'), "%a %b %d %Y %I:%M:%S %p")
                                end_dt = datetime.strptime(hora.get('end'), "%a %b %d %Y %I:%M:%S %p")
                                
                                # Only create events for Jupiter, Moon, and Mercury
                                if hora.get('hora') in ['Jupiter', 'Moon', 'Mercury']:
                                    # Create hora event
                                    event = Event()
                                    event.add('summary', f"Hora: {hora.get('hora')}")
                                    event.add('dtstart', start_dt)
                                    event.add('dtend', end_dt)
                                    event.add('description', f"Benefits: {hora.get('benefits', '')}\nLucky Gem: {hora.get('lucky_gem', '')}")
                                    event.add('categories', [hora.get('hora')])
                                    event.add('class', 'FREE')
                                    
                                    hora_calendar.add_component(event)
                                    logger.info(f"Created hora event: {hora.get('hora')} from {start_dt} to {end_dt}")
                            except ValueError as e:
                                logger.error(f"Error parsing datetime: {e}")
                                continue
                    else:
                        logger.error(f"Error getting hora data: {hora_result}")
                else:
                    logger.info(f"Not a special nakshatra: {current_nakshatra}")
                    
            # Also process special nakshatra transitions for completeness
            for i in range(len(nakshatras) - 1):
                current_nakshatra = nakshatras[i]['nakshatra']
                next_nakshatra = nakshatras[i + 1]['nakshatra']
                
                logger.info(f"Checking transition: {current_nakshatra} -> {next_nakshatra}")
                
                # Check if both nakshatras are in the special list
                if current_nakshatra in SPECIAL_NAKSHATRAS and next_nakshatra in SPECIAL_NAKSHATRAS:
                    logger.info(f"Found special nakshatra transition: {current_nakshatra} -> {next_nakshatra}")
                    
                    # First nakshatra ends at its end_time, next nakshatra starts at the same time
                    start_time = datetime.strptime(nakshatras[i]['end_time'], '%H:%M')
                    end_time = datetime.strptime(nakshatras[i + 1]['end_time'], '%H:%M')
                    
                    # Create datetime objects for the transition period
                    transition_start = datetime.combine(current_date, start_time.time())
                    transition_end = datetime.combine(current_date, end_time.time())
                    
                    # If end time is before start time, it's the next day
                    if transition_end < transition_start:
                        transition_end += timedelta(days=1)
                    
                    logger.info(f"Calculating hora events from {transition_start} to {transition_end}")
                    
                    # Get hora data from API
                    client = VedicAstroClient()
                    location = Location(37.33939, -121.89496)  # San Jose coordinates
                    
                    try:
                        hora_result = calculate_hora_for_date(client, location, transition_start)
                        
                        if hora_result and hora_result.get('status') == 200:
                            hora_data = hora_result.get('response', {}).get('horas', [])
                            logger.info(f"Received {len(hora_data)} hora events from API for transition")
                            
                            # Process each hora period
                            for hora in hora_data:
                                logger.info(f"Raw hora data - start: {hora.get('start')}, end: {hora.get('end')}, planet: {hora.get('hora')}")
                                
                                # Parse datetime strings
                                try:
                                    start_dt = datetime.strptime(hora.get('start'), "%a %b %d %Y %I:%M:%S %p")
                                    end_dt = datetime.strptime(hora.get('end'), "%a %b %d %Y %I:%M:%S %p")
                                    
                                    # Only create events for Jupiter, Moon, and Mercury
                                    if hora.get('hora') in ['Jupiter', 'Moon', 'Mercury']:
                                        # Create hora event
                                        event = Event()
                                        event.add('summary', f"Hora: {hora.get('hora')} (Transition)")
                                        event.add('dtstart', start_dt)
                                        event.add('dtend', end_dt)
                                        event.add('description', f"Transition: {current_nakshatra} → {next_nakshatra}\nBenefits: {hora.get('benefits', '')}\nLucky Gem: {hora.get('lucky_gem', '')}")
                                        event.add('categories', [hora.get('hora')])
                                        event.add('class', 'FREE')
                                        
                                        hora_calendar.add_component(event)
                                        logger.info(f"Created transition hora event: {hora.get('hora')} from {start_dt} to {end_dt}")
                                except ValueError as e:
                                    logger.error(f"Error parsing datetime: {e}")
                                    continue
                        else:
                            logger.error(f"Error getting hora data for transition: {hora_result}")
                    except Exception as e:
                        logger.error(f"Exception during hora calculation: {str(e)}")
                else:
                    logger.info(f"Not a special transition. Current: {current_nakshatra} in special list: {current_nakshatra in SPECIAL_NAKSHATRAS}, Next: {next_nakshatra} in special list: {next_nakshatra in SPECIAL_NAKSHATRAS}")
        
        # Process regular events (Dur Muhurtamulu and Varjyam)
        regular_events = events.get('regular_events', [])
        for event in regular_events:
            event_type = event['type']
            start_time = datetime.strptime(event['start_time'], '%H:%M')
            end_time = datetime.strptime(event['end_time'], '%H:%M')
            
            # Create datetime objects
            event_start = datetime.combine(current_date, start_time.time())
            event_end = datetime.combine(current_date, end_time.time())
            
            # If end time is before start time, it's the next day
            if event_end < event_start:
                event_end += timedelta(days=1)
            
            # Create event
            event = Event()
            event.add('summary', f"{event_type}")
            event.add('dtstart', event_start)
            event.add('dtend', event_end)
            event.add('description', f"{event_type} period")
            if event_type == 'DUS':
                event.add('categories', ['Dur Muhurtamulu'])
                logger.info(f"Created Dur Muhurtamulu event: {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}")
            elif event_type == 'VAR':
                event.add('categories', ['Varjyam'])
                logger.info(f"Created Varjyam event: {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}")
            
            regular_calendar.add_component(event)
        
        # Move to next date
        current_date += timedelta(days=1)
    
    return regular_calendar, hora_calendar

# Read JSON file
try:
    # Convert ICS to JSON first
    from icalendar import Calendar
    import json
    
    # Read the ICS file
    with open('April2025.ics', 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    # Convert to JSON format
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {
                "dtstart": component.get('dtstart').dt.strftime("%Y-%m-%d"),
                "description": component.get('description', ''),
                "summary": component.get('summary', '')
            }
            events.append(event)
    
    # Save to JSON file
    with open('icalJson.json', 'w') as f:
        json.dump(events, f, indent=2)
    
    logger.info("Successfully converted ICS to JSON")
except Exception as e:
    logger.error(f"Error reading April2025.ics: {e}")
    events = []
