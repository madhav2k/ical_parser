"""
VedicCalendarParser package
"""

# This file makes the VedicCalendarParser directory a Python package
from .icalParser6 import *
from .hora_calc import *

# Make the modules available at the package level
__all__ = [
    'create_ics_event',
    'extract_nakshatra_from_description',
    'extract_and_create_events',
    'VedicAstroClient',
    'HoraCalendar',
    'Location',
    'calculate_hora_for_date'
]

# Import the modules to make them available
from . import icalParser6
from . import hora_calc 