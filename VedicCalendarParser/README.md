# Vedic Calendar Parser

A Python-based tool for parsing and manipulating calendar events, with special support for Vedic astrology calculations and calendar conversions.

## Features

- Convert ICS (iCalendar) files to JSON format
- Convert JSON data back to ICS format
- Vedic astrology calculations (Hora calculations)
- Support for multiple languages (English, Hindi, Tamil, Telugu, Malayalam)
- Timezone-aware date/time handling
- Location-based calculations

## Prerequisites

- Python 3.8 or higher
- [Rye](https://rye-up.com/) for dependency and environment management

## Installation

1. **Install Rye**  
   If Rye is not already installed, run the following command:
   ```bash
   curl -sSf https://rye-up.com/get | bash
   ```

2. Clone the repository:
   ```bash
   git clone [repository-url]
   cd VedicCalendarParser
   ```

3. Install dependencies using Rye:
   ```bash
   rye sync
   ```

4. Activate the virtual environment:
   ```bash
   . .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## Project Structure

- `main.py` - Main entry point for the application
- `icaltoJson.py` - Converts ICS files to JSON format
- `icalParser6.py` - Handles ICS file parsing and event creation
- `hora_calc.py` - Vedic astrology calculations and API integration

## Running the Application

The main entry point for the application is `main.py`. To run the application:

```bash
python main.py
```

The application will:
1. Prompt you to enter the path to your ICS file
2. Validate that the file exists and has the correct .ics extension
3. Convert your input ICS file to JSON format
4. Process the events
5. Generate a new ICS file with the processed events

### Input/Output Files

The application expects and generates the following files:

- **Input File:**
  - Any file with .ics extension (entered when prompted)

- **Output Files:**
  - `icalJson.json` - Intermediate JSON representation of the calendar events
  - `BlockingDVEvents.ics` - Final processed calendar file

## Usage Examples

1. Basic ICS to JSON conversion:
```python
from icaltoJson import convert_ical_to_json, save_json_to_file

events = convert_ical_to_json('input.ics')
save_json_to_file(events, 'icalJson.json')
```

2. JSON to ICS conversion:
```python
from icalParser6 import extract_and_create_events

ics_calendar = extract_and_create_events(events)
with open('output.ics', 'wb') as ics_file:
    ics_file.write(ics_calendar.to_ical())
```

3. Vedic calculations:
```python
from hora_calc import Hora, Location, Client

client = Client()
hora = Hora(client)
hora.set_ayanamsa(1)
hora.set_timezone(timezone)
result = hora.process(location, datetime_obj, language)
```

## Dependencies

- duckdb >= 1.2.0
- requests >= 2.32.3
- beautifulsoup4 >= 4.13.3
- icalendar >= 6.1.2

## Error Handling

The application includes comprehensive error handling for:
- Validation errors
- API quota exceeded
- Rate limiting
- Authentication issues
- General API request failures

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Author

Madhav Annamraju (AgenticData@pm.me)
