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
import time

global HOST,PORT,cmdid
global latitude,longitude

def wait_processing(d,h,m):
    wait_for_seq_process=True
    if (d==0):
        wait_for_seq_process=False
    while wait_for_seq_process==True:
        time.sleep(20)
        Tcheck=time.localtime()
        if ((Tcheck.tm_mday>=d)&(Tcheck.tm_hour>=h)):
            if (Tcheck.tm_min>=m):
                wait_for_seq_process=False

def set_gain(id,valueparam):
    print("set gain")
    data = {}
    data={"id":id,"method":"set_control_value", "params":["gain",valueparam]}
    json_data =json.dumps(data)
    print(json_data)
    send_message(json_data + "\r\n")


def set_stack_settings(id,status):
    print("set stack setting")
    data = {}
    data['id'] = id
    data['method'] = 'set_stack_setting'
    params = {}
    params['save_discrete_frame'] = status
    data['params'] = params
    json_data =json.dumps(data)
    print(json_data)
    send_message(json_data + "\r\n")

def ra_dec_to_deg(Hra,MinRa,Sra, Hdec, Mindec, Sdec):
    ra_deg =Hra+MinRa/60+Sra/3600
    dec_deg=Hdec+Mindec/60+Sdec/3600
    return ra_deg, dec_deg

def convert_j2000_to_jnow(j2000_ra, j2000_dec):
# This function performs coordinate transformations from epoch J2000 to epoch on date (JNow).
# The J2000 coordinates is required to be in decimal format. RA in hours and Dec in degrees.
# Jari Backman, 'jabamula', jari@sinijari.fi
    # today
    tm = datetime.now()

    # J2000 coordinates
    j2000 = SkyCoord(ra=j2000_ra*u.hour, dec=j2000_dec*u.deg)

    # Transform to JNow
    jnow = j2000.transform_to(FK5(equinox=tm))

    # Extract JNow coordinates
    jnow_ra = jnow.ra.hour
    jnow_dec = jnow.dec.deg

    return jnow_ra, jnow_dec


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
    Autogoto_is_working=True
    while Autogoto_is_working == True:
        id = id +1
        Time.sleep(5)
        mess=json_message(id,"get_app_state")
        Autogoto_is_working= '"auto_goto":{"is_working":true' in mess
    print('GOTO '+target_name+ ' completed')
    
def autofocus(id):
    for i in range(1,3):
        id=id+1
        json_message(id,"start_auto_focuse")
        Autofocus_is_working=True
        while Autofocus_is_working == True:
            id = id +1
            Time.sleep(5)
            mess=json_message(id,"get_app_state")
            Autofocus_is_working= '"status_flag":1},"is_working":true' in mess
        time.sleep(10)
        print('Autofocus completed')

def get_nbframe_stat(id):
    mess=json_message(id,"get_app_state")
    frame_stacked = int(mess.split(sep=',')[23].split(sep=':')[1])
    frame_rejected= int(mess.split(sep=',')[24].split(sep=':')[1])
    return frame_stacked,frame_rejected