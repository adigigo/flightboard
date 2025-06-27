import requests
import datetime
from FlightRadar24 import FlightRadar24API
import sqlite3
from contextlib import closing
import os

import config

ROOT_DIR = os.path.dirname(os.path.abspath(__name__))

def start_fr():
    
    fr_api = FlightRadar24API()
    bounds = fr_api.get_bounds_by_point(latitude=config.LAT,longitude=config.LON,radius=15000)

    return(fr_api,bounds)

def TimeExtract(flight):
    if flight['time']['real']['departure'] is not None:
        dep = datetime.datetime.fromtimestamp(flight['time']['real']['departure'], datetime.UTC).strftime('%H:%M')   
    elif flight.get('time', {}).get('scheduled', {}).get('departure') is not None:
        dep = datetime.datetime.fromtimestamp(flight['time']['scheduled']['departure'], datetime.UTC).strftime('%H:%M')
    else:
        dep = "N/A"  

    if flight['time']['real']['arrival'] is not None:
        arr = datetime.datetime.fromtimestamp(flight['time']['real']['arrival'], datetime.UTC).strftime('%H:%M')
    elif flight.get('time', {}).get('scheduled', {}).get('arrival') is not None:
        arr = datetime.datetime.fromtimestamp(flight['time']['scheduled']['arrival'], datetime.UTC).strftime('%H:%M')
    else:
        arr = "N/A"

    return(dep,arr)

def get_flight():

    fr_api,bounds = start_fr()
    flights = fr_api.get_flights(bounds= bounds)

    # get a list of flights already read flights
    # so that we don't see the same flight again

    with closing(sqlite3.connect(f"{ROOT_DIR}/Projects/flightboard/flights.db")) as connection:
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute("select * from flights").fetchall()
            existing_ids = [id for (id,) in rows]

    # iterate through list of found flights and set the first "new" flight
    # break after the first new flight is found

    for result in flights:
        if result.id in existing_ids:       # if flight is already displayed, skip!
            continue
        elif result.altitude < 1000:         # skips flights which have altitude < 1000 ft
            continue                        # this helps skip flights which have already landed or just taken off.
        else:
            chosen_flight = result          # BINGO!
            break
    
    # now that we choose a flight - write to the db first
    with closing(sqlite3.connect(f"{ROOT_DIR}/Projects/flightboard/flights.db")) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("INSERT INTO flights VALUES (?)",(chosen_flight.id,))
        connection.commit()

    # get more details of the chosen flight
    flight = fr_api.get_flight_details(chosen_flight)
    
    dct = {}

    dct['airline'] = "N/A" if flight.get('airline') is None else flight.get('airline', ).get('name')
    dct['flight_no'] = flight.get('identification',{}).get('number').get('default') or "N/A"
    dct['aircraft'] = flight['aircraft']['model']['text']
    dct['dep_time_utc'],dct['arr_time_utc'] = TimeExtract(flight)
    dct['altitude'] = chosen_flight.altitude
    dct['ground_speed'] = chosen_flight.ground_speed
    dct['heading'] = chosen_flight.heading
    dct['airline_icao'] = chosen_flight.airline_icao
    dct['o_code'] = "N/A" if flight.get('airport').get('origin') is None else flight.get('airport', {}).get('origin', {}).get('code', {}).get('iata')
    dct['o_name'] = "N/A" if flight.get('airport').get('origin') is None else flight.get('airport', {}).get('origin', {}).get('position', {}).get('region', {}).get('city') or "N/A"
    dct['d_code'] = "N/A" if flight.get('airport').get('origin') is None else flight.get('airport', {}).get('destination', {}).get('code', {}).get('iata') or "N/A"
    dct['d_name'] = "N/A" if flight.get('airport').get('origin') is None else flight.get('airport', {}).get('destination', {}).get('position', {}).get('region', {}).get('city') or "N/A"

    return dct
