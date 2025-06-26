import requests
import datetime
from FlightRadar24 import FlightRadar24API

import config

def start_fr():
    
    fr_api = FlightRadar24API()
    bounds = fr_api.get_bounds_by_point(latitude=config.LAT,longitude=config.LON,radius=15000)

    return(fr_api,bounds)

def TimeExtract(flight):
    if flight['time']['real']['departure'] is not None:
        dep = datetime.datetime.fromtimestamp(flight['time']['real']['departure'], datetime.UTC).strftime('%H:%M')
        
    else:
        dep = datetime.datetime.fromtimestamp(flight['time']['scheduled']['departure'], datetime.UTC).strftime('%H:%M')
       
    if flight['time']['real']['arrival'] is not None:
        arr = datetime.datetime.fromtimestamp(flight['time']['real']['arrival'], datetime.UTC).strftime('%H:%M')
    else:
        arr = datetime.datetime.fromtimestamp(flight['time']['scheduled']['arrival'], datetime.UTC).strftime('%H:%M')

    return(dep,arr)

def get_flight():

    fr_api,bounds = start_fr()
    flights = fr_api.get_flights(bounds= bounds)

    chosen_flight = flights[0]

    flight = fr_api.get_flight_details(chosen_flight)
    dct = {}

    dct['airline'] = flight['airline']['name']
    dct['flight_no'] = flight['identification']['number']['default']
    dct['aircraft'] = flight['aircraft']['model']['text']
    dct['dep_time_utc'],dct['arr_time_utc'] = TimeExtract(flight)
    dct['altitude'] = chosen_flight.altitude
    dct['ground_speed'] = chosen_flight.ground_speed
    dct['heading'] = chosen_flight.heading
    dct['airline_icao'] = chosen_flight.airline_icao
    dct['o_code'] = flight['airport']['origin']['code']['iata']
    dct['o_name'] = flight['airport']['origin']['position']['region']['city']
    dct['d_code'] = flight['airport']['destination']['code']['iata']
    dct['d_name'] = flight['airport']['destination']['position']['region']['city']

    return dct
