# -*- coding: utf-8 -*-
"""
S550lib script to obtain sub from a list of target

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
#S50.PORT = 4350
S50.cmdid = 999

#READ YOUR TARGET LIST FROM EXCEL FILE
TargerList=pd.read_excel('MyTargetList.xlsx',dtype=object)

#SELECT YOUR TARGET
Targetname = 'Niobe'

# 
Target=TargerList.loc[TargerList['NAME']==Targetname]

cur_ra= Target['RA'].values[0]
cur_dec= Target['DEC'].values[0]
Exposure= Target['ExpTime'].values[0]
PixDither = Target['DitherPix'].values[0]
Interv_dither = Target['DitherIntv'].values[0]
gain = Target['gain'].values[0]
is_lp_filter=Target['LP_filter'].values[0]


########################################
# convert if necessary to jnow
#cur_ra, cur_dec = S50.convert_j2000_to_jnow(cur_ra, cur_dec)
#S50.cmdid+=1;S50.set_parameter(S50.cmdid,Exposure,500,PixDither,Interv_dither)
#S50.cmdid+=1;S50.goto_target(S50.cmdid,cur_ra, cur_dec, Targetname, is_lp_filter)
#S50.cmdid+=1;S50.start_stack(S50.cmdid)
#S50.cmdid+=1;S50.set_gain(S50.cmdid,gain)


