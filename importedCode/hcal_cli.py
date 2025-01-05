#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 21:12:00 2020
Updated on Thu Aug 27 14:19:52 2020
Updated on Sat Sep 12 15:33:58 2020

@author: Hrishikesh Terdalkar

CLI using HinduCalendar Class

Requirements:
    - geocoder (only for auto-detection of the city)
"""

import os
import json
import logging
import argparse
from datetime import datetime as dt

import geocoder

from hindu_calendar import HinduCalendar

###############################################################################
# GeoNames username for auto-detecting city

GEONAMES_USERNAME = 'hindu_calendar'

###############################################################################


def configure(fresh=False, **kwargs):
    """
    Get or set configuration
    config will be stored in ~/.hcal/config
    Function call will first try to read from this file, if it exists.

    Parameters
    ----------
    fresh : bool, optional
        If True, existing configuration, if any, will be ignored.
        The default is False.

    Returns
    -------
    config : dict
        Configuration dictionary. Various (config_name, config_value)

    """
    # ----------------------------------------------------------------------- #
    home_dir = os.path.expanduser('~')
    hcal_dir = os.path.join(home_dir, '.hcal')
    storage_dir = os.path.join(hcal_dir, 'data')
    config_file = os.path.join(hcal_dir, 'config')
    log_file = os.path.join(hcal_dir, 'log')

    if not os.path.isdir(hcal_dir):
        os.makedirs(hcal_dir)

    logging.basicConfig(filename=log_file,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    # ----------------------------------------------------------------------- #

    if os.path.isfile(config_file) and not fresh:
        with open(config_file, 'r') as f:
            config = json.loads(f.read())
    else:
        logging.info("Initiating fresh config ...")

        # default config
        config = {
            'geonames_username': GEONAMES_USERNAME,
            'city': 'auto',
            'method': 'marathi',
            'regional_language': True,
            'geonames_id': '',
            'storage_dir': storage_dir
        }

        # ------------------------------------------------------------------- #
        # City
        default_value = config['city']
        detected_city = False
        while True:
            # --------------------------------------------------------------- #
            if detected_city:
                answer = detected_city
            else:
                prompt = f"City (default: {default_value}): "
                answer = input(prompt).strip()
            # --------------------------------------------------------------- #

            if answer:
                options = HinduCalendar.find_city(answer, n=10)
                n_opt = len(options)
                if n_opt == 1:
                    config['city'] = options[0]['city']
                    config['geonames_id'] = options[0]['id']
                    print(f"{options[0]['city']}, "
                          f"{options[0]['state']}, "
                          f"{options[0]['country']}")
                    break
                else:
                    for idx, option in enumerate(options):
                        print(f"\t[{idx}]\t{option['city']}, "
                              f"{option['state']}, {option['country']}")
                    while True:
                        _prompt = f"Please choose your city [0-{n_opt-1}]: "
                        choice = input(_prompt).strip()
                        try:
                            choice = int(choice)
                        except Exception:
                            continue

                        if choice == -1:
                            ask_again = True
                            detected_city = False
                            break
                        else:
                            if 0 <= choice < n_opt:
                                config['city'] = options[choice]['city']
                                config['geonames_id'] = options[choice]['id']
                                ask_again = False
                                break
                    if not ask_again:
                        break
            else:
                ip = geocoder.ip('me', key=config['geonames_username'])
                detected_city = ip.city
            # --------------------------------------------------------------- #
        # ------------------------------------------------------------------- #
        # Method
        default_value = config['method']
        while True:
            valid_methods = list(HinduCalendar.methods.keys())
            prompt = f"Method (default: {default_value}): "
            answer = input(prompt).strip().lower()
            if answer:
                if answer not in valid_methods:
                    logging.warning(f"Invalid method: {answer}")
                    print("Warning: no such method.\n"
                          f"Available: {valid_methods}")
                else:
                    config['method'] = answer
                    break
            else:
                break
        # ------------------------------------------------------------------- #
        # ------------------------------------------------------------------- #
        # Regional Language
        default_value = 'yes' if config['regional_language'] else 'no'
        while True:
            valid_values = ['yes', 'no']
            prompt = f"Use regional language? (default: {default_value}): "
            answer = input(prompt).strip().lower()
            if answer:
                if answer not in valid_values:
                    logging.warning(f"Invalid value: {answer}")
                    print(f"Please answer {'/'.join(valid_values)}.")
                else:
                    config['regional_language'] = answer == 'yes'
                    break
            else:
                break
        # ------------------------------------------------------------------- #
        # ------------------------------------------------------------------- #
        # Storage Directory
        prompt = f"Storage Path (default: {storage_dir}): "
        answer = input(prompt).strip()
        if not answer:
            answer = storage_dir
        if not os.path.isdir(answer):
            os.makedirs(answer)
        # ------------------------------------------------------------------- #

        with open(config_file, 'w') as f:
            f.write(json.dumps(config))
            logging.info("Written config.")

    if kwargs:
        for arg, val in kwargs.items():
            config[arg] = val
        with open(config_file, 'w') as f:
            f.write(json.dumps(config))
            logging.info("Written config.")

    return config

###############################################################################


def main():
    desc = 'Hindu Calendar Utilities'
    p = argparse.ArgumentParser(description=desc)
    p.add_argument("-d", metavar='date', help="Date in dd/mm/yyyy")
    p.add_argument("-f", help="Fresh configuration", action='store_true')
    p.add_argument("-r", help="Input regional date", action='store_true')
    p.add_argument("-m", help="Regional method to use")
    p.add_argument("-c", action='store_true', help=("Find re-occurrence of "
                                                    "Tithi of the 'date' in "
                                                    "the current year"))
    p.add_argument("-y", metavar='year', help="Use with '-c' to specify year")
    p.add_argument("-l", action='store_true', help=("Display in regional "
                                                    "language"))
    p.add_argument("-s", help="Show config and exit", action='store_true')
    args = vars(p.parse_args())

    # arguments
    fresh = args['f']
    date = args['d']
    method = args['m']
    regional = args['r']
    show = args['s']

    reoccurrence = args['c']
    reyear = args['y']

    # config
    config = configure(fresh=fresh)

    regional_language = (True
                         if args['l'] else
                         config['regional_language'])

    if show:
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return locals()

    if method is None:
        method = config['method']

    if date is None:
        date = dt.now().strftime("%d/%m/%Y")

    calendar = HinduCalendar(method, city=config['city'],
                             regional_language=regional_language,
                             geonames_id=config['geonames_id'],
                             storage_dir=config['storage_dir'])

    if reoccurrence:
        if not reyear:
            reyear = dt.now().year
        date = calendar.find_occurrence(date, year=reyear, regional=regional)
    else:
        date = calendar.get_date(date, regional=regional)

    print(json.dumps(date, indent=2, ensure_ascii=False))
    return locals()

###############################################################################


if __name__ == '__main__':
    locals().update(main())
