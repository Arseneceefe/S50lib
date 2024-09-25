# -*- coding: utf-8 -*-
"""
Created on a cloudy night in 2024

Designed to merge the goodness of seestar_run and S50

@author: skelle
"""
import seestar_varstarlib as S50
import socket
import time
from datetime import datetime, timezone
import threading
import sys
import argparse
import pandas as pd
import seestar_varstar_params as params

    
is_watch_events = True
    
def main():
    global HOST
    global PORT
    global session_time
    global s
    global cmdid
    global is_watch_events
    global is_debug, logger
    S50.latitude= -35.351835
    S50.longitude= 149.030122

    logger = S50.CreateLogger()
    version_string = "1.0.0b1"
    logger.debug(f'seestar_run version: {version_string}')
    
    HOST = params.ip
    PORT = 4700 
    cmdid = 999
 
    parser = setup_argparse()
    args = parser.parse_args()
    is_debug = args.is_debug


    try:
        target_df = pd.read_csv(args.schedule_file)
    except Exception as e:
         logger.error(f'Unable to load schedule - {e}')
         sys.exit(1)
    target_names=target_df['Name'].values
    target_stack_times = target_df['TotalExp'].values
    target_exptimes = target_df['ExpTime'].values
    
    # Get object coordinate from simbad query and convert to Jnow
    ras,decs = S50.get_coord_object(target_names)
    logger.info(f'list of targets {target_names, ras, decs}')

    # TARGET OBSERVATIONS
    # determine safe limits for observing
    (twilight_begin, twilght_end) = S50.calc_twilight()

    logger.info(f'Nautical Twilight is from {twilight_begin} to {twilght_end}')

    S50safe = False
    while not S50safe:
        if (twilight_begin <= datetime.now(timezone.utc) <= twilght_end):
            S50safe = True
        else:
            logger.info('Outside observing times - waiting...')
            logger.info(datetime.now(timezone.utc))
            time.sleep(1)
            break

    # determine the repetition pattern requested
    if (args.target_seq_mode not in ['repeat', 'single']):
        logger.error(f'target sequence mode not known: {args.target_seq_mode}')
        raise RuntimeError()
    elif (args.target_seq_mode == 'repeat'):
            logger.info(f'Targets will be cycled repeatedly until dawn - mode {args.target_seq_mode}')
            repeat = True
    elif (args.target_seq_mode == 'single'):
            logger.info(f'Targets will be observed in order - mode {args.target_seq_mode}')
            repeat = False

    # preliminary overall settings
    S50.set_stack_settings() # set to save frames in the stack

    loop = True
    if not is_debug:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((HOST, PORT))
        except Exception as e:
             logger.error(f'Unable to connect to device')
             sys.exit(1)
        with s:
            # flush the socket input stream for garbage
            #S50.get_socket_msg()
            # print input requests
            print("Received parameters:")
            print(f"  ip address    :  {HOST}")
            print(f"  target        :  {target_names[iloop]}")
            print(f"  RA            :  {ras[iloop]}")
            print(f"  Dec           :  {decs[iloop]}")
            print(f"  exp time      :  {target_exptimes[iloop]}")
            print(f"  session time  :  {target_stack_times[iloop]}")
            print(f"  debug         :  {is_debug}")
            sys.exit(1)
                
            get_msg_thread = threading.Thread(target=S50.receieve_message_thread_fn)
            get_msg_thread.start()
            
            print(f'Slew to {RA, Dec}')
            S50.goto_target(RA, Dec, target_name, exp_time, session_time)
            wait_end_op()
            print("Goto operation finished")
                    
            time.sleep(3)
                    
            if op_state == "complete":
                S50.start_stack()    
                S50.sleep_with_heartbeat(session_time)
                S50.stop_stack()
                print("Stacking operation finished" + target_name)
            else:
                print("Goto failed.")
                        
            
        print("Finished seestar_run")
        is_watch_events = False
        get_msg_thread.join(timeout=5)
    # end not debug
    else:
         iloop = 0
         nloops = 0
         while loop:
            # show input requests
            logger.debug("Received parameters:")
            logger.debug(f"  ip address    :  {HOST}")
            logger.debug(f"  target        :  {target_names[iloop]}")
            logger.debug(f"  RA            :  {ras[iloop]}")
            logger.debug(f"  Dec           :  {decs[iloop]}")
            logger.debug(f"  exp time      :  {target_exptimes[iloop]}")
            logger.debug(f"  session time  :  {target_stack_times[iloop]}")
            logger.debug(f"  debug         :  {is_debug}")
            logger.info(f'Slew to {target_names[iloop]} : {S50.parse_float_to_ra(ras[iloop]), S50.parse_float_to_dec(decs[iloop])}')

            #S50.goto_target(ras[iloop], decs[iloop], target_names[iloop], target_exptimes[iloop], target_stack_times[iloop])
            #wait_end_op()
            logger.debug("Goto operation finished")
            time.sleep(3)
            iloop +=1
            if (iloop>=len(target_names) and repeat):
                 iloop = 0
                 nloops +=1
                 logger.info(f'Loop {nloops} executed')
            elif (iloop>len(target_names) and not repeat):
                 loop = False    
    
def setup_argparse():
    parser = argparse.ArgumentParser(description='Seestar VarStar')
    parser.add_argument('schedule_file', type=str, help="Observation Target Schedule")
    parser.add_argument('target_seq_mode', type=str, choices=['repeat', 'single'], default='single', help='Schedule Mode: repeat or single loop through targets')
    parser.add_argument('is_debug', type=str, default=False, nargs='?', help="Print debug logs while running.")

    return parser
    

# seestar_run <ip_address> <target_name> <ra> <dec> <is_use_LP_filter> <session_time> <RA panel size> <Dec panel size> <RA offset factor> <Dec offset factor>
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '-41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '+41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' '7:24:32.5' '41:24:23.5' 0 60 2 2 1.0 1.0
# python seestar_run.py 192.168.110.30 'Castor' 7.4090278 41.4065278 0 60 2 2 1.0 1.0
if __name__ == "__main__":
    main()
    

 
