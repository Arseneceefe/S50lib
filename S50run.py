# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 17:28:49 2024

@author: sauss
"""

import S50lib as S50
import socket
import json
import geocoder
import time
from datetime import datetime, timezone
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from astroquery.simbad import Simbad
from astroquery.ipac.ned import Ned
import numpy as np
import math
import schedule_file as sf

########################################
#SETUP OF USER (NETWORK INFO AND GEOLOC)

S50.HOST = '192.168.1.35'
S50.PORT = 4700
S50.cmdid = 1111

# local coordinate
#myloc = geocoder.ip('me')
#S50.longitude= myloc.lng
#S50.latitude=myloc.lat
S50.latitude= -35.351835
S50.longitude= 149.030122

is_lp_filter=False
# END SETUP
########################################

target_names=sf.target_names
target_seq=sf.target_seq
target_stack_times = sf.target_stack_times
target_exptimes = sf.target_exptimes
target_seq_mode = sf.target_seq_mode
# Get object coordinate from simbad query and convert to Jnow
cur_ra,cur_dec = S50.get_coord_object(target_names)

#target_name='M42'
#cur_ra,cur_dec = S50.ra_dec_to_deg(5,36,28,-5,22,34)
#print('seestar',cur_ra,cur_dec)

# CONVERT J2000 to Jnow
cur_ra,cur_dec = S50.convert_j2000_to_jnow(cur_ra,cur_dec)

# PRELIMINARY PARAMETERS
# Save all subs
S50.cmdid+=1;S50.set_stack_settings(S50.cmdid,True) 
is_lp_filter = 0 # ? 0 or 1?
# Set gain to 100 
S50.cmdid+=1;S50.set_gain(S50.cmdid,80)

# TARGET OBSERVATIONS
# determine safe limits for observing
(twilight_begin, twilght_end) = S50.calc_twilight()

print(f'Nautical Twilight is from {twilight_begin} to {twilght_end}')

S50safe = False
while not S50safe:
    if (twilight_begin <= datetime.now(timezone.utc) <= twilght_end):
        S50safe = True
    else:
        print('Outside observing times')
        print(datetime.now(timezone.utc))
        time.sleep(60)

# determine the repetition pattern requested
if (target_seq_mode not in ['r']):
    print(f'target sequence mode not known: {target_seq_mode}')
    raise RuntimeError()
else:
    if (target_seq_mode == 'r'):
        repeat = True
loop = True

while loop:
    for i in range(0, len(target_seq)):
        current_target_id = target_seq[i]-1
        current_exposure = target_exptimes[current_target_id]*1000 # ms required
        current_stack_time = target_stack_times[current_target_id] # s for this one as it is not a S50 param
        # Set Exposure and Dithering 12 pix every 20 subs
        S50.cmdid+=1;S50.set_parameter(S50.cmdid,current_exposure,500,12,20)
        # goto target
        S50.cmdid+=1;S50.goto_target(S50.cmdid,cur_ra[current_target_id], cur_dec[current_target_id], target_names[current_target_id], is_lp_filter)
    #    Autofocus - up to 4 attempts
        S50.cmdid+=1;S50.autofocus(S50.cmdid)
        S50.cmdid+=1;S50.start_stack(S50.cmdid)
        time.sleep(current_stack_time) # wait for the total stack to be taken
        S50.cmdid+=1;S50.stop_stack(S50.cmdid)
        print(f'{target_names[current_target_id]} is done...')
    print(f'All {i+1} objects are done')
    if (repeat):
        loop = True
    else:
        loop = False
    # Check the time and see if we are still safe to observe
    if not (twilight_begin <= datetime.now(timezone.utc) <= twilght_end):
        print(f'Reached morning twilight. Stopping...')
        print(f'Twilight ends at: {twilght_end} and we are at {datetime.now(timezone.utc)}')
        loop = False
# SET OF COMMANDS TO SEND TO SEESTAR
# App informations
#S50.cmdid+=1;S50.json_message(S50.cmdid,"get_app_state")
#S50.cmdid+=1;S50.json_message(S50.cmdid,"get_setting")
#S50.cmdid+=1;S50.json_message(S50.cmdid,"get_focuser_position")
#S50.cmdid+=1;S50.json_message(S50.cmdid,"scope_get_equ_coord")
#S50.cmdid+=1;S50.json_message(S50.cmdid,"get_batch_stack_setting")
#S50.cmdid+=1;S50.json_message(S50.cmdid,"scope_get_ra_dec")
# S50.cmdid+=1;S50.set_parameter(S50.cmdid,10000,250,60,2)
# S50.cmdid+=1;S50.stop_stack(S50.cmdid)
# S50.cmdid+=1;S50.start_stack(S50.cmdid)

# for i in range(10):
#     S50.cmdid+=1;S50.start_stack(S50.cmdid)
#     time.sleep(260)
#     S50.cmdid+=1;S50.stop_stack(S50.cmdid)
    
