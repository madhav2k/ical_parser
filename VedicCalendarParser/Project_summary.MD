# Vedic Calendar Parser Project Summary

## Project Overview

This project is a specialized calendar application that processes Vedic/Hindu astrological data from ICS (iCalendar) files. It identifies key astrological events such as nakshatra transitions, hora periods, and special time periods like Dur Muhurtamulu and Varjyam. The application extracts this data, processes it, and then creates new ICS files with customized calendar events that can be imported into standard calendar applications.

## Key Features

1. **Nakshatra Processing**: Extracts and identifies nakshatra (lunar mansion) periods from calendar data.
2. **Special Transition Detection**: Identifies transitions between special nakshatras.
3. **Hora Calculation**: Uses an external API to calculate hora periods (planetary hours) for specific time periods.
4. **Filtering**: Can filter hora events to only include specific planets (Jupiter, Moon, Mercury).
5. **ICS File Generation**: Creates standard calendar files that can be imported into most calendar applications.

## Development Prompts

The project was developed using AI assistance with these key prompting strategies:

1. **Data Extraction Prompts**: 
   - Instructions to parse the description tag from JSON/ICS files and extract specific event types like 'Dur Muhurtamulu' and 'Varjyam'
   - Time format handling in the format "startTime to endTime"

2. **Event Creation Prompts**:
   - Guidelines for creating ICS format events with proper start and end times
   - Instructions for handling special cases like date transitions (when times include a comma)
   - Implementation of event classification (marking events as private)

3. **Processing Logic Prompts**:
   - Direction for filtering specific planetary events (Jupiter, Moon, Mercury)
   - Special nakshatra transition identification criteria
   - Hora calculation integration with external API services

4. **Code Structure Prompts**:
   - Function design guidance (like `create_ics_event` and `extract_and_create_events`)
   - Process flow from JSON parsing to calendar generation
   - Error handling and logging requirements

These prompts guided the development of key functions including datetime handling, event creation, ICS file formatting, and the overall processing pipeline.

## Files and Components

### Main Files

1. **main.py**
   - Entry point for the application
   - Handles command-line arguments and file I/O
   - Calls the main processing functions
   - Sets the date range for processing (April 2025)

2. **icalParser6.py**
   - Core processing module
   - Contains functions to extract data from ICS files
   - Processes nakshatra transitions
   - Filters and creates hora events
   - Generates output calendar files

3. **hora_calc.py**
   - Contains the VedicAstroClient class for API interaction
   - Provides methods to calculate hora periods
   - Manages location data for astrological calculations

4. **icaltoJson.py**
   - Converts ICS files to JSON format for easier processing
   - Provides utility functions for JSON file handling

5. **config.py**
   - Contains configuration variables (like DEBUG_MODE)
   - Centralizes configuration options

### Supporting Files

1. **nakshatras.txt**
   - List of special nakshatras to be used in the application
   - Used for filtering events

2. **April2025.ics**
   - Input calendar file containing Vedic astronomical data
   - Source of nakshatra and other event information

### Output Files

1. **vedic_events.ics**
   - Contains regular events (Dur Muhurtamulu and Varjyam)
   - Standard ICS format for calendar import

2. **hora_events.ics**
   - Contains hora events for specified planets (Jupiter, Moon, Mercury)
   - Only includes events during special nakshatra transitions
   - Standard ICS format for calendar import

3. **icalJson.json**
   - Intermediate JSON representation of the input calendar
   - Used in the processing pipeline

4. **logs/vedic_calendar.log**
   - Detailed logs of the application's execution
   - Records events, transitions, and any errors encountered

## Technical Implementation

The project follows these processing steps:

1. Read the input ICS file and convert it to JSON
2. Extract nakshatra periods and regular events by date
3. Process each date in the specified range (April 2025)
4. Identify special nakshatra transitions
5. For each transition:
   - Calculate hora events using the VedicAstroClient
   - Filter for specified planets (Jupiter, Moon, Mercury)
   - Create calendar events with appropriate metadata
6. Process regular events (Dur Muhurtamulu and Varjyam)
7. Write the results to output ICS files

This project demonstrates effective calendar data manipulation, date/time processing, and integration with external astrological calculation services to create specialized calendar events based on Vedic astrological principles. 