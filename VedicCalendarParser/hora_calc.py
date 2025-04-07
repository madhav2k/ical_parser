from datetime import datetime, timezone, timedelta
import requests
import http.client
import json
from icalendar import Calendar, Event
import pytz
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    def __init__(self, validation_errors):
        self.validation_errors = validation_errors
        super().__init__('Validation error occurred')

class QuotaExceededException(Exception):
    pass

class RateLimitExceededException(Exception):
    pass

class AuthenticationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class Location:
    def __init__(self, latitude, longitude, altitude=0, tz=None):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.tz = tz

class VedicAstroClient:
    """Client for interacting with the Vedic Astro API."""
    
    def __init__(self, api_key='1c998321-4363-5535-91a6-2331c3c2c012'):
        self.api_key = api_key
        self.base_url = "api.vedicastroapi.com"
        
    def get_hora_muhurta(self, date, lat, lon, tz=5.5, lang='en'):
        """
        Get hora muhurta data from Vedic API.
        
        Args:
            date (str): Date in DD/MM/YYYY format
            lat (float): Latitude
            lon (float): Longitude
            tz (float): Timezone offset (default: 5.5 for IST)
            lang (str): Language code (default: 'en')
        
        Returns:
            dict: JSON response from the API
        """
        try:
            conn = http.client.HTTPSConnection(self.base_url)
            
            # Construct the API endpoint with parameters
            endpoint = f"/v3-json/panchang/hora-muhurta?api_key={self.api_key}&date={date}&lat={lat}&lon={lon}&tz={tz}&lang={lang}"
            
            # Make the request
            conn.request("GET", endpoint)
            response = conn.getresponse()
            
            # Read and decode the response
            data = response.read().decode("utf-8")
            
            # Parse JSON response
            json_data = json.loads(data)
            
            # Close the connection
            conn.close()
            
            return json_data
            
        except Exception as e:
            print(f"Error making API request: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }

class HoraCalendar:
    """Class for creating calendar events from hora data."""
    
    def __init__(self, keywords=None):
        """
        Initialize HoraCalendar.
        
        Args:
            keywords (list): List of hora keywords to filter for. Defaults to ['Mercury', 'Moon', 'Jupiter']
        """
        self.keywords = keywords or ['Mercury', 'Moon', 'Jupiter']
    
    def create_events(self, result):
        """
        Create calendar events from hora data.
        
        Args:
            result (dict or str): API response containing hora data
        
        Returns:
            Calendar: ICS calendar with hora events
        """
        cal = Calendar()
        
        # If result is a string, try to parse it as JSON
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                return cal
        
        # Check if the result contains valid data
        if not isinstance(result, dict) or 'status' not in result:
            logger.error("Invalid API response format")
            return cal
        
        if result['status'] != 200:
            logger.error(f"API returned error status: {result.get('message', 'Unknown error')}")
            return cal
        
        # Get the hora data
        horas_data = result.get('response', {}).get('horas', [])
        if not horas_data:
            logger.error("No hora data found in response")
            return cal
        
        for hora in horas_data:
            if not isinstance(hora, dict):
                logger.error(f"Invalid hora data format: {hora}")
                continue
            
            # Get the hora value and check for keywords
            hora_value = hora.get('hora', '')
            
            # Check if the hora matches any of our keywords
            if hora_value not in self.keywords:
                continue
            
            # Get start and end times
            start_time = hora.get('start', '')
            end_time = hora.get('end', '')
            
            if not start_time or not end_time:
                logger.error(f"Missing start or end time for hora: {hora}")
                continue
            
            try:
                # Parse the datetime strings with the exact format from API response
                datetime_format = "%a %b %d %Y %I:%M:%S %p"
                start_dt = datetime.strptime(start_time, datetime_format)
                end_dt = datetime.strptime(end_time, datetime_format)
                
                # Create event
                event = Event()
                event.add('summary', f"Hora: {hora_value}")
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('description', f"Benefits: {hora.get('benefits', '')}\nLucky Gem: {hora.get('lucky_gem', '')}")
                event.add('class', 'FREE')
                
                # Add hora as category for better filtering
                event.add('categories', [hora_value])
                
                cal.add_component(event)
                logger.info(f"Added hora event: {hora_value} from {start_dt} to {end_dt}")
                
            except ValueError as e:
                logger.error(f"Error parsing datetime: {e}")
                logger.error(f"Start time: {start_time}")
                logger.error(f"End time: {end_time}")
                continue
            
        return cal
    
    def save_to_ics(self, calendar, filename='hora_events.ics'):
        """
        Save calendar events to an ICS file.
        
        Args:
            calendar (Calendar): iCalendar object to save
            filename (str): Name of the file to save to
        """
        with open(filename, 'wb') as f:
            f.write(calendar.to_ical())
        print(f"Calendar events have been saved to {filename}")
    
    def save_response(self, response, filename='hora_response.json'):
        """
        Save API response to a JSON file.
        
        Args:
            response (dict): API response to save
            filename (str): Name of the file to save to
        """
        with open(filename, 'w') as f:
            json.dump(response, f, indent=2)
        print(f"API response has been saved to {filename}")

def get_us_timezone_offset(latitude: float, longitude: float, date: datetime) -> Tuple[float, str]:
    """
    Get the correct timezone offset for US locations, accounting for daylight savings.
    
    Args:
        latitude (float): Location latitude
        longitude (float): Location longitude
        date (datetime): Date to check for daylight savings
        
    Returns:
        Tuple[float, str]: (timezone offset, timezone name)
    """
    # Map of US timezones and their approximate boundaries
    timezone_map = {
        'America/New_York': (-75, 40),  # Eastern
        'America/Chicago': (-90, 40),   # Central
        'America/Denver': (-105, 40),   # Mountain
        'America/Los_Angeles': (-120, 40)  # Pacific
    }
    
    # Find the closest timezone based on longitude
    closest_tz = min(timezone_map.items(), 
                    key=lambda x: abs(x[1][0] - longitude))
    tz_name = closest_tz[0]
    
    # Get the timezone object
    tz = pytz.timezone(tz_name)
    
    # Get the offset for the specific date
    offset = tz.utcoffset(date)
    offset_hours = offset.total_seconds() / 3600
    
    return offset_hours, tz_name

def calculate_hora_for_date(client, location, target_date: datetime, timezone_str: Optional[str] = None, language='en'):
    """
    Calculate hora data for a specific date.
    
    Args:
        client (VedicAstroClient): The API client instance
        location (Location): Location object with coordinates
        target_date (datetime): Date to calculate hora for
        timezone_str (str, optional): Timezone string. If None, will be calculated based on location
        language (str): Language code (default: 'en')
    
    Returns:
        dict: API response containing hora data for the specified date
    """
    try:
        # Format date as DD/MM/YYYY
        date_str = target_date.strftime('%d/%m/%Y')
        
        # Get timezone offset
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            offset = tz.utcoffset(target_date)
            tz_offset = offset.total_seconds() / 3600
        else:
            tz_offset = -7  # Default to Pacific time if no timezone specified
        
        result = client.get_hora_muhurta(
            date=date_str,
            lat=location.latitude,
            lon=location.longitude,
            tz=tz_offset,
            lang=language
        )
        
        print(f"Processed date: {date_str} with timezone offset: {tz_offset}")
        return result
        
    except Exception as e:
        print(f"Error processing date {target_date}: {str(e)}")
        return None

# Example usage:
if __name__ == "__main__":
    # Example parameters - using San Jose coordinates
    lat = 37.33939  # San Jose latitude
    lon = -121.89496  # San Jose longitude
    language = 'en'
    
    # Create location object
    location = Location(lat, lon)
    
    # Initialize client
    client = VedicAstroClient()
    
    # Get hora for a specific date (e.g., today)
    target_date = datetime.now(timezone.utc)
    result = calculate_hora_for_date(client, location, target_date, language=language)
    
    if result:
        # Save the result to a JSON file
        with open('hora_data.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("API response has been saved to hora_data.json")
        
        # Create calendar events
        hora_calendar = HoraCalendar()
        cal = hora_calendar.create_events(result)
        
        # Save to ICS file
        hora_calendar.save_to_ics(cal, 'hora_events.ics')

