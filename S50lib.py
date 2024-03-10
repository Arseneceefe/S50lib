# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 17:25:27 2024

@author: sauss
"""


import socket
import json
import geocoder
from astroquery.simbad import Simbad
from astroquery.ipac.ned import Ned
from astropy.coordinates import SkyCoord, EarthLocation, AltAz,FK5
import astropy.units as u
from astropy.time import Time
import numpy as np
import math
from datetime import datetime
global HOST,PORT,cmdid
global latitude,longitude

def set_stack_settings(id):
    print("set stack setting")
    data = {}
    data['id'] = id
    data['method'] = 'set_stack_setting'
    params = {}
    params['save_discrete_frame'] = True
    data['params'] = params
    json_data =json.dumps(data)
    send_message(json_data + "\r\n")

def ra_dec_to_deg(Hra,MinRa,Sra, Hdec, Mindec, Sdec):
    ra_deg =Hra+MinRa/60+Sra/3600
    dec_deg=Hdec+Mindec/60+Sdec/3600
    return ra_deg, dec_deg

def get_max_theoric_exp_time(cur_ra,cur_dec):
    print('Theorical max exposure time for IMX462')
    print('from californiaskys')
   
    wearth=0.00418
    Pixtrav=(3.1416*wearth)/(360*0.0000029)
    cur_ra=60
    cur_dec=180
    latitude=37
    Ht=np.radians(cur_ra)
    Lat=np.radians(latitude)
    Az=np.radians(cur_dec)
    # Ht=cur_ra
    # Lat=latitude
    # Az=cur_dec

    cste=((15.04/3.6)*(2*math.pi/360))*(6.4498/2.9)
    cste=0.271
     # Pixels Traversed  =   cst x cos 37deg  x cos 180deg x t / cos 60deg
    A=(np.cos(Lat)*np.cos(Az))/(np.cos(Ht)*cste)
    MaxExptime=Pixtrav/A
    return MaxExptime

def get_coord_object(target_name):
    result_table = Simbad.query_object(target_name)
    object_ra = result_table['RA'][0]  # Right Ascension
    object_dec = result_table['DEC'][0]  # Declination
    print(object_ra,object_dec)
    loc = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg, height=0*u.m)  # Latitude, Longitude, Altitude (in meters)
    tm=datetime.utcnow()
    #Convert RA DEC to Alt-Az
    #coord =SkyCoord(object_ra, object_dec,frame='icrs', unit=(u.hourangle, u.deg))
#    coord=SkyCoord(object_ra, object_dec,unit=(u.hourangle,u.deg),frame=FK5(equinox=tm))
    coord=SkyCoord(object_ra, object_dec,unit=(u.deg),obstime=tm)
#    coord =SkyCoord(object_ra, object_dec,frame='icrs', unit=(u.deg))
#    _fk5 = FK5(equinox=Time(Time(datetime.utcnow(), scale='utc').jd, format="jd", scale="utc"))
    # Calculate ALT and AZ coordinates 
#    altaz_coords = coord.transform_to(AltAz(obstime=tm, location=loc))
    # Extract ALT and AZ values in degrees
#    altitude = altaz_coords.alt.deg
    #azimuth = altaz_coords.az.deg
    altitude = coord.ra.deg
    azimuth = coord.dec.deg
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