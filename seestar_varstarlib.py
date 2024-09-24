# -*- coding: utf-8 -*-
"""
Created on a cloudy night in 2024

@author: skelle
"""


import socket
import json
import geocoder
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time
import numpy as np
import math
from datetime import datetime
import time
import ephem
import pytz

global HOST,PORT,cmdid
global latitude,longitude

def get_coord_object(target_names):
    result_table = Simbad.query_objects(target_names)
    object_ra = result_table['RA'].data  # Right Ascension
    object_dec = result_table['DEC'].data  # Declination
    coord=SkyCoord(object_ra, object_dec,unit=(u.deg))
    return coord.ra.deg, coord.dec.deg

def calc_twilight():
    S50Observer = ephem.Observer()
    # Set the date and time 
    S50Observer.date = datetime.today().strftime('%Y-%m-%d')#"2024-07-14"

    # Location 
    S50Observer.lon = str(latitude)
    S50Observer.lat = str(longitude)

    # Elevation 
    S50Observer.elev = 500

    # To get U.S. Naval Astronomical Almanac values, use these settings
    S50Observer.pressure = 0
    S50Observer.horizon = '-0:34'

    # Calculate sunrise, solar noon, and sunset
    S50Observer.horizon = '-12'  # -6=civil twilight, -12=nautical, -18=astronomical
    beg_twilight = S50Observer.next_rising(ephem.Sun(), use_center=True)
    end_twilight = S50Observer.next_setting(ephem.Sun(), use_center=True)
    return(beg_twilight.datetime().replace(tzinfo=pytz.utc), end_twilight.datetime().replace(tzinfo=pytz.utc))
