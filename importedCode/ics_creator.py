#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 22:01:32 2020
Updated on Thu Aug 27 14:45:32 2020
Updated on Tue Jan 31 12:06:09 2022

@author: Hrishikesh Terdalkar

Create ICS by plotting the Tithis of Birthdays/Anniversaries on CE calendar

Input: CSV file containing CE birthdays/anniversaries
Output: ICS file importable in Google Calendar

Third-party Dependancies:
    ics
"""

import os
import argparse
from datetime import datetime as dt

from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from hindu_calendar import HinduCalendar

###############################################################################


def main():
    home_dir = os.path.expanduser('~')
    default_input_file = 'events.csv'
    default_output_file = 'events.ics'
    desc = 'Create Hindu Calendar ICS'
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("-i", help="Input CSV file", default=default_input_file)
    p.add_argument("-o", help="Output ICS file", default=default_output_file)
    p.add_argument("-y", help="Year", default=dt.now().year)
    args = vars(p.parse_args())

    input_file = args['i']
    output_file = args['o']
    year = args['y']

    # CSV file contains header
    header = True

    with open(input_file, 'r') as f:
        event_list = [[word.strip() for word in line.strip().split(',')]
                      for line in f.read().split('\n') if line.strip(", ")]
        if header:
            event_list.pop(0)

    calendar = Calendar()
    calendar.creator = ("HinduCalendar using drikPanchang.com "
                        "by Hrishikesh Terdalkar")
    calendar.extra.append(ContentLine(name='CALSCALE', value='GREGORIAN'))

    for event_row in event_list:
        date, regional_date, label, name, method, use_regional, include = event_row
        include = bool(int(include))

        if not include:
            continue

        use_regional = bool(int(use_regional))
        if use_regional:
            date = regional_date

        hindu_calendar = HinduCalendar(method=method)
        date_obj = hindu_calendar.find_occurrence(date,
                                                  year=year,
                                                  regional=use_regional)

        current_occurence = dt.strptime(date_obj['ce_date'], "%d/%m/%Y")
        event_description = [date_obj['regional_datestring']]
        if date_obj['event']:
            event_description.append(f"** {date_obj['event']} **")

        for key, value in date_obj['panchang'].items():
            if key.lower().startswith('tith'):
                event_description.append(f"({value})")
                break

        e = Event()
        e.name = f"{name}'s {label}"
        e.begin = current_occurence.isoformat()
        e.make_all_day()
        e.description = '\n'.join(event_description)

        calendar.events.add(e)

    with open(output_file, 'w') as f:
        f.write(str(calendar))

    return locals()

###############################################################################


if __name__ == '__main__':
    locals().update(main())
