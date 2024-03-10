# S50lib
Python function for seestar S50 base on seestar run from Kai
S50lib contains elementary function and global variable
S50run is the main script to call function and operate seestar :
########################################
#SETUP OF USER (NETWORK INFO AND GEOLOC)

S50.HOST = "XXX.X.X.XXX"
S50.PORT = 4700
S50.cmdid = 999

# local coordinate
#myloc = geocoder.ip('me')
#S50.longitude= myloc.lng
#S50.latitude=myloc.lat
S50.latitude= XXX
S50.longitude=XXX

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

# goto target
S50.cmdid+=1;S50.goto_target(S50.cmdid,cur_ra, cur_dec, target_name, is_lp_filter)

 S50.cmdid+=1;S50.start_stack(S50.cmdid)
# time.sleep(30*60)
# S50.cmdid+=1;S50.stop_stack(S50.cmdid)
