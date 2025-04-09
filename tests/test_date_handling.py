import sys
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from icalendar import Event, Calendar

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from VedicCalendarParser.icalParser6 import extract_and_create_events, extract_nakshatra_from_description

class TestDateHandling(TestCase):
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
        mock_hora_instance.create_events = MagicMock(return_value=mock_cal)

        # Create a test event with multiple nakshatras
        test_event = {
            "dtstart": "2025-04-01",
            "description": """Nakshatramulu - Bharani upto 03:00 PM
Nakshatramulu - Kritika upto 05:07 PM, Apr 02
Dur Muhurtamulu - 10:00 AM to 11:00 AM
Varjyam - 12:00 PM to 1:00 PM"""
        }

        # Set up mock return value with correct structure
        mock_calculate_hora.return_value = {
            "status": 200,
            "response": {
                "horas": [
                    {
                        "hora": "Mercury",
                        "start": "2025-04-01 16:00",  # Changed to 24-hour format
                        "end": "2025-04-01 17:00",
                        "benefits": "Good time for business",
                        "lucky_gem": "Emerald"
                    },
                    {
                        "hora": "Moon",
                        "start": "2025-04-01 17:00",
                        "end": "2025-04-01 18:00",
                        "benefits": "Good time for social activities",
                        "lucky_gem": "Pearl"
                    }
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