# -*- coding: utf-8 -*-
"""
Created on Sun May 12 21:18:45 2024

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
import pandas as pd

########################################
#SETUP OF USER (NETWORK INFO AND GEOLOC)

S50.HOST="10.0.0.1"
S50.PORT = 4700
S50.cmdid = 999


S50.latitude=48.799815
S50.longitude=2.257289


TargetSeq=pd.read_excel('S50Target_sequence_config.xlsx',dtype=object)

for i in range(0,TargetSeq.shape[0]-1):
    S50.wait_processing(TargetSeq['Daybegin'][i],TargetSeq['Hrbegin'][i],TargetSeq['Minbegin'][i])
    S50.cmdid+=1;S50.set_stack_settings(S50.cmdid,eval(TargetSeq['Save All Frame'][i]))
    if eval(TargetSeq['J2000'][i]):
        RA_cur,DEC_cur = S50.convert_j2000_to_jnow(TargetSeq['RA'][i],TargetSeq['DEC'][i])
    else:
        RA_cur=TargetSeq['RA'][i]
        DEC_cur=TargetSeq['DEC'][i]
    S50.cmdid+=1;S50.goto_target(S50.cmdid,RA_cur, DEC_cur, TargetSeq['NAME'][i], eval(TargetSeq['LP_filter'][i]))
    S50.cmdid+=1;S50.set_gain(S50.cmdid,TargetSeq['gain'][i])
    if eval(TargetSeq['Autofocus'][i]):
        S50.cmdid+=1;S50.autofocus(S50.cmdid)
    S50.cmdid+=1;S50.set_parameter(S50.cmdid,TargetSeq['ExpTime'][i],500,TargetSeq['DitherPix'][i],TargetSeq['DitherIntv'][i])
    S50.cmdid+=1;S50.start_stack(S50.cmdid)
    S50.cmdid+=1;S50.set_gain(S50.cmdid,TargetSeq['gain'][i])
    S50.wait_processing(TargetSeq['Dayend'][i],TargetSeq['Hrend'][i],TargetSeq['Minend'][i])
    S50.cmdid+=1;S50.stop_stack(S50.cmdid)
    # Nb_good_frame=0
    # while Nb_good_frame < TargetSeq['Number valid frame to reach'][i]:
    #     time.sleep(60)
    #     S50.cmdid+=1;Nb_good_frame,bad_frame=S50.get_nbframe_stat(S50.cmdid)
        
# S50.cmdid+=1;S50.json_message(S50.cmdid,"pi_shutdown")






    