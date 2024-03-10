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
from datetime import datetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from astroquery.simbad import Simbad
from astroquery.ipac.ned import Ned
import numpy as np
import math

########################################
#SETUP OF USER (NETWORK INFO AND GEOLOC)

S50.HOST = 
S50.PORT = 4700
S50.cmdid = 999

# local coordinate
#myloc = geocoder.ip('me')
#S50.longitude= myloc.lng
#S50.latitude=myloc.lat
S50.latitude=
S50.longitude=

is_lp_filter=True
# END SETUP
########################################

target_name='M42'
# Get object coordinate from simbad query and convert to Jnow
cur_ra,cur_dec = S50.get_coord_object(target_name)
print('Simbad',cur_ra,cur_dec)

target_name='M42'
cur_ra,cur_dec =S50.ra_dec_to_deg(5,36,28,-5,22,34)
print('seestar',cur_ra,cur_dec)



# TARGET OBSERVATION
Exposure=25000
# Dithering 12 pix every 20 subs
S50.cmdid+=1;S50.set_parameter(S50.cmdid,Exposure,500,12,20)
#save all subs
S50.cmdid+=1;S50.set_stack_settings(S50.cmdid)

# goto target
S50.cmdid+=1;S50.goto_target(S50.cmdid,cur_ra, cur_dec, target_name, is_lp_filter)

 S50.cmdid+=1;S50.start_stack(S50.cmdid)
# time.sleep(30*60)
# S50.cmdid+=1;S50.stop_stack(S50.cmdid)


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
    
