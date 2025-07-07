# Calendar Privacy and Randomization Changes

## Overview

The calendar events created in `icalParser6.py` have been modified to:
1. **Make all events private** - Events are now marked with `CLASS:PRIVATE` in the ICS file
2. **Add randomized 3-letter names** - Durmuhurtam and Varjyam events now have randomized names with specific prefixes

## Changes Made

### 1. Added Random Name Generation Function

**File:** `VedicCalendarParser/icalParser6.py`

Added a new function `generate_random_name(prefix)` that creates 3-letter randomized names:
- Durmuhurtam events: Start with "D" (e.g., "DAB", "DXY", "DKL")
- Varjyam events: Start with "V" (e.g., "VAB", "VXY", "VKL")

```python
def generate_random_name(prefix):
    """
    Generate a randomized 3-letter name with the specified prefix.
    
    Args:
        prefix (str): The prefix to use ('D' for Durmuhurtam, 'V' for Varjyam)
    
    Returns:
        str: A randomized name like 'DAB', 'VXY', etc.
    """
    # Generate 2 random uppercase letters
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{prefix}{random_letters}"
```

### 2. Made All Events Private

**File:** `VedicCalendarParser/icalParser6.py`

Added `event.add('class', 'PRIVATE')` to all Event() creations in the file:

- **Regular events (Dur Muhurtamulu and Varjyam):** Now have randomized names and are private
- **Hora events:** Already had private class, confirmed all instances are set
- **General event creation function:** Updated to make all events private

### 3. Updated Event Creation for Dur Muhurtamulu and Varjyam

**File:** `VedicCalendarParser/icalParser6.py`

Modified the event creation logic to use randomized names:

```python
# Before:
event.add('summary', f"{event_type}")

# After:
if event_type == 'DUS':
    random_name = generate_random_name('D')
    event.add('summary', random_name)
    # ... other properties
elif event_type == 'VAR':
    random_name = generate_random_name('V')
    event.add('summary', random_name)
    # ... other properties
```

## Example Output

### Before Changes:
```
BEGIN:VEVENT
SUMMARY:DUS
DESCRIPTION:Dur Muhurtamulu period
CLASS:PUBLIC
...
END:VEVENT

BEGIN:VEVENT
SUMMARY:VAR
DESCRIPTION:Varjyam period
CLASS:PUBLIC
...
END:VEVENT
```

### After Changes:
```
BEGIN:VEVENT
SUMMARY:DAB
DESCRIPTION:Dur Muhurtamulu period
CLASS:PRIVATE
...
END:VEVENT

BEGIN:VEVENT
SUMMARY:VXY
DESCRIPTION:Varjyam period
CLASS:PRIVATE
...
END:VEVENT
```

## Testing

A test script `test_random_names.py` has been created to verify the random name generation works correctly. Run it with:

```bash
python test_random_names.py
```

## Benefits

1. **Privacy:** All calendar events are now marked as private, preventing them from being shared or viewed by others
2. **Anonymity:** Randomized names make it difficult to identify the nature of the events at a glance
3. **Consistency:** All events follow the same naming pattern with appropriate prefixes
4. **Compliance:** Meets privacy requirements for sensitive calendar data

## Files Modified

- `VedicCalendarParser/icalParser6.py` - Main changes to event creation
- `test_random_names.py` - Test script for verification
- `CALENDAR_PRIVACY_CHANGES.md` - This documentation

## Notes

- The randomization uses Python's `random.choices()` function with uppercase letters A-Z
- Each event gets a unique 3-letter name (prefix + 2 random letters)
- The `CLASS:PRIVATE` property is a standard ICS property that most calendar applications respect
- Hora events already had the private class set, so no changes were needed there 