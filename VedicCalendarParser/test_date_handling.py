import unittest
from datetime import datetime, timedelta
from VedicCalendarParser import create_ics_event, extract_nakshatra_from_description, extract_and_create_events
import logging
from icalendar import Calendar, Event
from VedicCalendarParser import VedicAstroClient, HoraCalendar, Location, calculate_hora_for_date
import sys
from unittest.mock import patch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestDateHandling(unittest.TestCase):
    def setUp(self):
        # Base date for all tests
        self.base_date = datetime(2025, 4, 1)  # April 1, 2025
        # Mock special nakshatras for testing
        self.special_nakshatras = ['kriththika', 'rohini', 'mrigashira']

    def test_same_day_event(self):
        """Test event that starts and ends on the same day"""
        start_time = "10:00 AM"
        end_time = "11:00 AM"
        summary = "Test Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 10, 0))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 1, 11, 0))

    def test_overnight_event(self):
        """Test event that starts in the evening and ends the next day"""
        start_time = "11:00 PM"
        end_time = "1:00 AM"
        summary = "Overnight Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 23, 0))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 2, 1, 0))

    def test_explicit_next_day(self):
        """Test event with explicit next day in end time"""
        start_time = "10:00 PM"
        end_time = "1:00 AM, Apr 02"
        summary = "Explicit Next Day Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 22, 0))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 2, 1, 0))

    def test_late_night_event(self):
        """Test event that starts at 11 PM and ends after midnight"""
        start_time = "11:30 PM"
        end_time = "12:30 AM"
        summary = "Late Night Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 23, 30))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 2, 0, 30))

    def test_multi_day_event(self):
        """Test event that spans multiple days"""
        start_time = "11:00 PM, Apr 01"
        end_time = "1:00 AM, Apr 03"
        summary = "Multi-Day Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 23, 0))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 3, 1, 0))

    def test_edge_case_midnight(self):
        """Test event that starts at midnight"""
        start_time = "12:00 AM"
        end_time = "1:00 AM"
        summary = "Midnight Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNotNone(event)
        self.assertEqual(event.get('dtstart').dt, datetime(2025, 4, 1, 0, 0))
        self.assertEqual(event.get('dtend').dt, datetime(2025, 4, 1, 1, 0))

    def test_invalid_time_format(self):
        """Test handling of invalid time format"""
        start_time = "invalid time"
        end_time = "1:00 PM"
        summary = "Invalid Time Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNone(event)

    def test_24_hour_format(self):
        """Test handling of 24-hour time format"""
        start_time = "13:00"
        end_time = "14:00"
        summary = "24 Hour Format Event"
        
        event = create_ics_event(start_time, end_time, self.base_date, summary)
        self.assertIsNone(event)  # Should fail as we only support 12-hour format

    @patch('VedicCalendarParser.icalParser6.SPECIAL_NAKSHATRAS', ['kritika', 'rohini', 'mrigasira'])
    @patch('VedicCalendarParser.icalParser6.calculate_hora_for_date')
    @patch('VedicCalendarParser.icalParser6.HoraCalendar')
    def test_multiple_nakshatras_with_special(self, mock_hora_calendar, mock_calculate_hora):
        """Test handling of multiple nakshatras where one is special"""
        # Create mock events
        mock_event1 = Event()
        mock_event1.add('summary', 'Good Hora')
        mock_event1.add('dtstart', datetime(2025, 4, 1, 16, 0))
        mock_event1.add('dtend', datetime(2025, 4, 1, 17, 0))

        mock_event2 = Event()
        mock_event2.add('summary', 'Bad Hora')
        mock_event2.add('dtstart', datetime(2025, 4, 1, 17, 0))
        mock_event2.add('dtend', datetime(2025, 4, 1, 18, 0))

        mock_cal = Calendar()
        mock_cal.add_component(mock_event1)
        mock_cal.add_component(mock_event2)

        # Set up mock calendar
        mock_hora_instance = mock_hora_calendar.return_value
        mock_hora_instance.create_events.return_value = mock_cal

        # Create a test event with multiple nakshatras
        test_event = {
            "dtstart": "2025-04-01",
            "description": """Nakshatramulu - Bharani upto 03:00 PM
Nakshatramulu - Kritika upto 05:07 PM, Apr 02
Dur Muhurtamulu - 10:00 AM to 11:00 AM
Varjyam - 12:00 PM to 1:00 PM"""
        }

        # Set up mock return value
        mock_calculate_hora.return_value = {
            "status": 200,
            "data": {
                "hora": [
                    {"start": "04:00 PM", "end": "05:00 PM", "type": "good"},
                    {"start": "05:00 PM", "end": "06:00 PM", "type": "bad"}
                ]
            }
        }

        # Process the event
        cal, hora_cal = extract_and_create_events([test_event])
        
        # Verify that we have both regular and hora events
        self.assertIsNotNone(cal)
        self.assertIsNotNone(hora_cal)
        
        # Count the events
        regular_events = sum(1 for component in cal.walk() if component.name == "VEVENT")
        hora_events = sum(1 for component in hora_cal.walk() if component.name == "VEVENT")
        
        # We should have 2 regular events (Dur Muhurtamulu and Varjyam)
        self.assertEqual(regular_events, 2)
        
        # We should have 2 hora events (one for each hora period)
        self.assertEqual(hora_events, 2)
        
        # Verify that the nakshatras were correctly extracted
        nakshatras = extract_nakshatra_from_description(test_event["description"])
        self.assertIsNotNone(nakshatras)
        self.assertEqual(len(nakshatras), 2)
        
        # Verify the first nakshatra (Bharani)
        self.assertEqual(nakshatras[0][0], "bharani")
        self.assertEqual(nakshatras[0][1], "03:00 PM")
        self.assertIsNone(nakshatras[0][2])
        
        # Verify the second nakshatra (Kritika)
        self.assertEqual(nakshatras[1][0], "kritika")
        self.assertEqual(nakshatras[1][1], "05:07 PM")
        self.assertEqual(nakshatras[1][2], "Apr 02")
        
        # Verify mocks were called
        mock_calculate_hora.assert_called_once()
        mock_hora_instance.create_events.assert_called_once()

if __name__ == '__main__':
    unittest.main() 