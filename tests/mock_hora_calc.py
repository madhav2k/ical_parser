from icalendar import Calendar, Event
from datetime import datetime, timedelta

class VedicAstroClient:
    pass

class HoraCalendar:
    def create_events(self, result):
        cal = Calendar()
        if result and isinstance(result, dict) and result.get('status') == 200:
            horas = result.get('response', {}).get('horas', [])
            for hora in horas:
                event = Event()
                event.add('summary', f"{hora['hora']} Hora")
                
                # Handle both string and datetime timestamps
                start_time = hora['start']
                end_time = hora['end']
                
                if isinstance(start_time, str):
                    start_time = datetime.strptime(start_time, "%Y-%m-%d %I:%M %p")
                if isinstance(end_time, str):
                    end_time = datetime.strptime(end_time, "%Y-%m-%d %I:%M %p")
                
                event.add('dtstart', start_time)
                event.add('dtend', end_time)
                event.add('description', f"Benefits: {hora.get('benefits', '')}\nLucky Gem: {hora.get('lucky_gem', '')}")
                cal.add_component(event)
        return cal

class Location:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

def calculate_hora_for_date(client, location, target_date, language='en'):
    # Mock hora data for testing
    # Generate hora events for the entire day
    horas = []
    current_time = datetime(target_date.year, target_date.month, target_date.day, 0, 0)
    end_time = current_time + timedelta(days=1)
    
    while current_time < end_time:
        # Create a hora event for each hour
        next_time = current_time + timedelta(hours=1)
        horas.append({
            "hora": "Mercury",  # Just use Mercury for all events in the mock
            "start": current_time,
            "end": next_time,
            "benefits": "Good time for business",
            "lucky_gem": "Emerald"
        })
        current_time = next_time
    
    return {
        "status": 200,
        "response": {
            "horas": horas
        }
    } 