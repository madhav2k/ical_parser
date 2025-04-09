from unittest.mock import patch
from datetime import datetime
import sys
import os
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from VedicCalendarParser.icalParser6 import create_ics_event, extract_nakshatra_from_description, extract_and_create_events

def test_nakshatra_transition_with_events():
    """Test handling of events during nakshatra transition period."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Mock the nakshatra data
    nakshatra_data = {
        "2025-04-01": [
            {
                "nakshatra": "bharani",
                "start_time": "03:00:00",
                "end_time": "15:00:00"
            },
            {
                "nakshatra": "kritika",
                "start_time": "16:00:00",
                "end_time": "17:07:23"
            }
        ]
    }
    
    # Mock the event data with various scenarios
    event_data = [
        {
            "dtstart": "2025-04-01",
            "description": "Nakshatramulu - Bharani upto 03:00 PM\nDur Muhurtamulu - 10:00 AM to 11:00 AM\nVarjyam - 02:30 PM to 04:30 PM",
            "events": [
                {
                    "event": "DUS",
                    "start_time": "10:00 AM",
                    "end_time": "11:00 AM"
                },
                {
                    "event": "VAR",
                    "start_time": "02:30 PM",
                    "end_time": "04:30 PM"
                },
                {
                    "event": "DUS",
                    "start_time": "05:00 PM",
                    "end_time": "06:00 PM"
                }
            ]
        },
        {
            "dtstart": "2025-04-02",
            "description": "Nakshatramulu - Kritika upto 05:07 PM\nDur Muhurtamulu - 12:00 AM to 01:00 AM\nVarjyam - 04:00 PM to 05:00 PM",
            "events": [
                {
                    "event": "VAR",
                    "start_time": "12:00 AM",
                    "end_time": "01:00 AM"
                },
                {
                    "event": "DUS",
                    "start_time": "04:00 PM",
                    "end_time": "05:00 PM"
                }
            ]
        }
    ]
    
    # Mock the file reading functions
    with patch('VedicCalendarParser.icalParser6.read_json_file', side_effect=lambda x: nakshatra_data if 'nakshatra' in x else event_data):
        with patch('VedicCalendarParser.icalParser6.read_txt_file', return_value=['kritika']):
            regular_cal, hora_cal = extract_and_create_events(event_data)
            
            # Verify events were created correctly
            assert regular_cal is not None
            
            # Get all events from both calendars
            regular_events = [e for e in regular_cal.walk() if e.name == "VEVENT"]
            hora_events = [e for e in hora_cal.walk() if e.name == "VEVENT"]
            
            # Log the events we found
            logger.info(f"Found {len(regular_events)} regular events and {len(hora_events)} hora events")
            for event in regular_events:
                logger.info(f"Regular event: summary={event.get('summary')}, start={event.get('dtstart').dt}, end={event.get('dtend').dt}")
            for event in hora_events:
                logger.info(f"Hora event: summary={event.get('summary')}, start={event.get('dtstart').dt}, end={event.get('dtend').dt}")
            
            # Check regular events before transition
            assert any(e.get('summary') == 'DUS' and 
                      e.get('dtstart').dt == datetime(2025, 4, 1, 10, 0) and
                      e.get('dtend').dt == datetime(2025, 4, 1, 11, 0)
                      for e in regular_events)
            
            # Check event crossing transition
            assert any(e.get('summary') == 'VAR' and 
                      e.get('dtstart').dt == datetime(2025, 4, 1, 14, 30) and
                      e.get('dtend').dt == datetime(2025, 4, 1, 16, 30)
                      for e in regular_events)
            
            # Check event after transition
            assert any(e.get('summary') == 'DUS' and 
                      e.get('dtstart').dt == datetime(2025, 4, 1, 17, 0) and
                      e.get('dtend').dt == datetime(2025, 4, 1, 18, 0)
                      for e in regular_events)
            
            # Check next day events
            assert any(e.get('summary') == 'VAR' and 
                      e.get('dtstart').dt == datetime(2025, 4, 2, 0, 0) and
                      e.get('dtend').dt == datetime(2025, 4, 2, 1, 0)
                      for e in regular_events)
            
            assert any(e.get('summary') == 'DUS' and 
                      e.get('dtstart').dt == datetime(2025, 4, 2, 16, 0) and
                      e.get('dtend').dt == datetime(2025, 4, 2, 17, 0)
                      for e in regular_events)
            
            # Check hora events
            # Verify we have hora events for both days
            april1_horas = [e for e in hora_events if e.get('dtstart').dt.date() == datetime(2025, 4, 1).date()]
            april2_horas = [e for e in hora_events if e.get('dtstart').dt.date() == datetime(2025, 4, 2).date()]
            
            assert len(april1_horas) > 0, "No hora events found for April 1st"
            assert len(april2_horas) > 0, "No hora events found for April 2nd"
            
            # Verify hora events are properly ordered and valid
            for day_horas in [april1_horas, april2_horas]:
                # Sort events by start time
                sorted_horas = sorted(day_horas, key=lambda e: e.get('dtstart').dt)
                
                # Check that each event has valid start and end times
                for event in sorted_horas:
                    start_time = event.get('dtstart').dt
                    end_time = event.get('dtend').dt
                    assert start_time < end_time, f"Invalid event timing: starts at {start_time}, ends at {end_time}"
                
                # Check that events are properly ordered (no overlaps)
                for i in range(len(sorted_horas) - 1):
                    current_end = sorted_horas[i].get('dtend').dt
                    next_start = sorted_horas[i + 1].get('dtstart').dt
                    assert current_end <= next_start, f"Events overlap: {current_end} to {next_start}"

def test_nakshatra_transition_hora_events():
    """Test hora events are correctly generated based on nakshatra transition times."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Mock the event data for April 4th, 2025
    event_data = [{
        "dtstart": "2025-04-04",
        "description": """Nakshatramulu - Arudra upto 04:50 PM
Nakshatramulu - Punarvasu upto 04:50 PM, Apr 05
Dur Muhurtamulu - 10:00 AM to 11:00 AM
Varjyam - 12:00 PM to 1:00 PM"""
    }]

    # Mock the hora data
    mock_hora_data = {
        "status": 200,
        "response": {
            "horas": [
                {"hora": "Mercury", "start": "2025-04-04 10:00 AM", "end": "2025-04-04 11:00 AM"},
                {"hora": "Moon", "start": "2025-04-04 11:00 AM", "end": "2025-04-04 12:00 PM"},
                {"hora": "Jupiter", "start": "2025-04-04 12:00 PM", "end": "2025-04-04 1:00 PM"},
                {"hora": "Mercury", "start": "2025-04-04 4:50 PM", "end": "2025-04-04 5:50 PM"},
                {"hora": "Moon", "start": "2025-04-04 5:50 PM", "end": "2025-04-04 6:50 PM"},
                {"hora": "Jupiter", "start": "2025-04-04 6:50 PM", "end": "2025-04-04 7:50 PM"},
                {"hora": "Mercury", "start": "2025-04-05 12:00 AM", "end": "2025-04-05 1:00 AM"},
                {"hora": "Moon", "start": "2025-04-05 1:00 AM", "end": "2025-04-05 2:00 AM"},
                {"hora": "Jupiter", "start": "2025-04-05 2:00 AM", "end": "2025-04-05 3:00 AM"},
                {"hora": "Mercury", "start": "2025-04-05 4:50 PM", "end": "2025-04-05 5:50 PM"}
            ]
        }
    }

    # Mock the file reading functions
    with patch('VedicCalendarParser.icalParser6.read_json_file', return_value=mock_hora_data):
        with patch('VedicCalendarParser.icalParser6.read_txt_file', return_value=['punarvasu']):
            regular_cal, hora_cal = extract_and_create_events(event_data)
            
            # Verify events were created correctly
            assert regular_cal is not None
            assert hora_cal is not None
            
            # Get all hora events
            hora_events = [e for e in hora_cal.walk() if e.name == "VEVENT"]
            
            # Log the events we found
            logger.info(f"Found {len(hora_events)} hora events")
            for event in hora_events:
                logger.info(f"Hora event: summary={event.get('summary')}, start={event.get('dtstart').dt}, end={event.get('dtend').dt}")
            
            # Verify we have the correct number of hora events
            # Should only include events after 4:50 PM on April 4th and before 4:50 PM on April 5th
            assert len(hora_events) == 6, f"Expected 6 hora events, got {len(hora_events)}"
            
            # Verify the first hora event starts after 4:50 PM on April 4th
            first_event = hora_events[0]
            assert first_event.get('dtstart').dt >= datetime(2025, 4, 4, 16, 50), \
                f"First hora event starts too early: {first_event.get('dtstart').dt}"
            
            # Verify the last hora event ends before 4:50 PM on April 5th
            last_event = hora_events[-1]
            assert last_event.get('dtend').dt <= datetime(2025, 4, 5, 16, 50), \
                f"Last hora event ends too late: {last_event.get('dtend').dt}"
            
            # Verify no events exist before 4:50 PM on April 4th
            for event in hora_events:
                if event.get('dtstart').dt.date() == datetime(2025, 4, 4).date():
                    assert event.get('dtstart').dt >= datetime(2025, 4, 4, 16, 50), \
                        f"Event starts before transition time: {event.get('dtstart').dt}"
            
            # Verify no events exist after 4:50 PM on April 5th
            for event in hora_events:
                if event.get('dtend').dt.date() == datetime(2025, 4, 5).date():
                    assert event.get('dtend').dt <= datetime(2025, 4, 5, 16, 50), \
                        f"Event ends after transition time: {event.get('dtend').dt}" 