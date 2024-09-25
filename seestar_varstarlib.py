# -*- coding: utf-8 -*-
"""
Created on a cloudy night in 2024

@author: skelle
"""


import socket
import json
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time
from datetime import datetime
import time
import ephem
import pytz
import logging
import sys


global HOST,PORT,cmdid, is_debug
global latitude,longitude, logger

def CreateLogger():
    # Create a custom logger
    logger = logging.getLogger('seevar_logger')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('seestar_varstar.log')

    # Set levels for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return(logger)

def send_message(data):
    global s
    try:
        s.sendall(data.encode())  # TODO: would utf-8 or unicode_escaped help here
    except socket.error as e:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        send_message(data)

def json_message(instruction):
    global cmdid
    data = {"id": cmdid, "method": instruction}
    cmdid += 1
    json_data = json.dumps(data)
    if is_debug:
        logger.debug("Sending %s" % json_data)
    send_message(json_data+"\r\n")

def json_message2(data):
    if data:
        json_data = json.dumps(data)
        if is_debug:
            logger.debug("Sending2 %s" % json_data)
        send_message(json_data + "\r\n")

def goto_target(ra, dec, target_name, exp_time, exp_cont):
    global cmdid
    logger.debug(f'Setting parameters for {target_name}')
    data = {}
    data['id'] = cmdid
    cmdid += 1
    data['method'] = 'set_setting'
    params = {}
    params['exp_ms'] = {}
    params['exp_ms']['stack_l']=exp_time
    params['exp_ms']['continous']=exp_cont
    data['params'] = params
    json_message2(data)
    logger.debug("going to target...")
    data = {}
    data['id'] = cmdid
    cmdid += 1
    data['method'] = 'iscope_start_view'
    params = {}
    params['mode'] = 'star'
    ra_dec = [ra, dec]
    params['target_ra_dec'] = ra_dec
    params['target_name'] = target_name
    params['lp_filter'] = 0 # we don't want to use this filter
    data['params'] = params
    json_message2(data)

    
def set_stack_settings():
    global cmdid
    logger.debug("set stack setting to record individual frames")
    data = {}
    data['id'] = cmdid
    cmdid += 1
    data['method'] = 'set_stack_setting'
    params = {}
    params['save_discrete_frame'] = True
    data['params'] = params
    json_message2(data)

def start_stack():
    global cmdid
    logger.debug("starting to stack...")
    data = {}
    data['id'] = cmdid
    cmdid += 1
    data['method'] = 'iscope_start_stack'
    params = {}
    params['restart'] = True
    data['params'] = params
    json_message2(data)

def stop_stack():
    global cmdid
    logger.debug("stop stacking...")
    data = {}
    data['id'] = cmdid
    cmdid += 1
    data['method'] = 'iscope_stop_view'
    params = {}
    params['stage'] = 'Stack'
    data['params'] = params
    json_message2(data)

def wait_end_op():
    global op_state
    op_state = "working"
    heartbeat_timer = 0
    while op_state == "working":
        heartbeat_timer += 1
        if heartbeat_timer > 5:
            heartbeat_timer = 0
            json_message("test_connection")
        time.sleep(1)

    
def sleep_with_heartbeat(session_time):
    stacking_timer = 0
    while stacking_timer < session_time:         # stacking time per segment
        stacking_timer += 1
        if stacking_timer % 5 == 0:
            json_message("test_connection")
        time.sleep(1)

def parse_ra_to_float(ra_string):
    # Split the RA string into hours, minutes, and seconds
    hours, minutes, seconds = map(float, ra_string.split(':'))

    # Convert to decimal degrees
    ra_decimal = hours + minutes / 60 + seconds / 3600

    return ra_decimal
    
def parse_float_to_ra(ra):
    # convert the ra float to a ra str hhmmss
    hours = int(ra)
    minutes = int((ra - hours) * 60)
    seconds = int(((ra - hours) * 60 - minutes) * 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
    
def parse_dec_to_float(dec_string):
    # Split the Dec string into degrees, minutes, and seconds
    if dec_string[0] == '-':
        sign = -1
        dec_string = dec_string[1:]
    else:
        sign = 1
    logger.debug(f'dec string: {dec_string}')
    degrees, minutes, seconds = map(float, dec_string.split(':'))

    # Convert to decimal degrees
    dec_decimal = sign * (degrees + minutes / 60 + seconds / 3600)

    return dec_decimal

def parse_float_to_dec(dec):
    degrees = int(dec)
    minutes = abs(int((dec - degrees) * 60))
    seconds = abs((dec - degrees - int((dec - degrees) * 60) / 60) * 3600)
    return f"{degrees:02}:{minutes:02}:{seconds:05.2f}"

def receieve_message_thread_fn():
    global is_watch_events
    global op_state
    global s
        
    msg_remainder = ""
    while is_watch_events:
        #print("checking for msg")
        data = get_socket_msg()
        if data:
            msg_remainder += data
            first_index = msg_remainder.find("\r\n")
            
            while first_index >= 0:
                first_msg = msg_remainder[0:first_index]
                msg_remainder = msg_remainder[first_index+2:]            
                parsed_data = json.loads(first_msg)
                
                if 'Event' in parsed_data and parsed_data['Event'] == "AutoGoto":
                    state = parsed_data['state']
                    logger.debug("AutoGoto state: %s" % state)
                    if state == "complete" or state == "fail":
                        op_state = state
                
                if is_debug:
                    logger.debug(parsed_data)
                    
                first_index = msg_remainder.find("\r\n")
        time.sleep(1)

def get_socket_msg():
    global s
    try:
        data = s.recv(1024 * 60)  
    except socket.error as e:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        data = s.recv(1024 * 60)
    data = data.decode("utf-8")
    if is_debug:
        logger.debug("Received :", data)
    return data

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
