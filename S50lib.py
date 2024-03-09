# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 17:25:27 2024

@author: sauss
"""


import socket
import json
import geocoder
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
import astropy.units as u
from datetime import datetime
global HOST,PORT,cmdid
global latitude,longitude

def get_coord_object(target_name):
    result_table = Simbad.query_object(target_name)
    object_ra = result_table['RA'][0]  # Right Ascension
    object_dec = result_table['DEC'][0]  # Declination
    loc = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0*u.m)  # Latitude, Longitude, Altitude (in meters)
    tm=datetime.utcnow()
    #Convert RA DEC to Alt-Az
    coord =SkyCoord(object_ra, object_dec,frame='icrs', unit=(u.hourangle, u.deg))
    # Calculate ALT and AZ coordinates 
    altaz_coords = coord.transform_to(AltAz(obstime=tm, location=loc))
    # Extract ALT and AZ values in degrees
    altitude = altaz_coords.alt.deg
    azimuth = altaz_coords.az.deg
    return altitude, azimuth


def send_message(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data.encode())
        data = s.recv(1024)
 
    print('Received', repr(data))

 
def json_message(id,instruction):
    data = {"id":id, "method":instruction}
    json_data = json.dumps(data)
    print("Sending %s" % json_data)
 
    send_message(json_data + "\r\n")
 
    return json_data

def set_parameter(id,exp_time,exp_cont,npix,interval):
    print("set exposure")
    data = {}
    data['id'] = id
    data['method'] = 'set_setting'
    params = {}
    params['exp_ms'] = {}
    params['exp_ms']['stack_l']=exp_time
    params['exp_ms']['continous']=exp_cont
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")
    print("set dither")
    data = {}
    data['id'] = id+1
    data['method'] = 'set_setting'
    params['stack_dither'] ={}   
    params['stack_dither']['pix'] = npix
    params['stack_dither']['interval'] = interval
    params['stack_dither']['enable'] = True
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")

def start_stack(id):
    print("Stack ON.")
    data = {}
    data['id'] = id
    data['method'] = 'iscope_start_stack'
    params = {}
    params['restart'] = True
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")


def stop_stack(id):
    print("Stack STOP")
    data = {}
    data['id'] = id
    data['method'] = 'iscope_stop_view'
    params = {}
    params['stage'] = 'Stack'
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")


def goto_target(id,ra, dec, target_name, is_lp_filter):
    print("GOTO TARGET")
    data = {}
    data['id'] = id
    data['method'] = 'iscope_start_view'
    params = {}
    params['mode'] = 'star'
    ra_dec = [ra, dec]
    params['target_ra_dec'] = ra_dec
    params['target_name'] = target_name
    params['lp_filter'] = is_lp_filter
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")