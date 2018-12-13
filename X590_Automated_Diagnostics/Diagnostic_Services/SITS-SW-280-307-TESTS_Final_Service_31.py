#============================================================================================================================================================
#
# Integration Test script file
# (c) Copyright 2012 Lear Corporation 
#
#============================================================================================================================================================

import sys
import os
import time
import Tkinter as tk
import tkMessageBox


# Report Header Variables
AUTHOR = 'Shitole Priyanka'
TLA = 'DGN'
TLA_VERSION = '1.0.0'
SVN_REVISION = 'Level 8'
HW_VERSION = 'X590'
SW_BRANCH = 'Version  (08 34 10)'
Component_VERSION = '1.0.0'
TLA_Description = 'TLA'

REPORT_NAME = 'TLA_Service_31'

#============================================================================================================================================================

REPORT_API_PATH = os.path.abspath(r'../latte_libs/report_v2_0_0')
COM_API_PATH = os.path.abspath(r'../latte_libs/com_v1_8_0')


# Adding paths for loading correctly .py libraries
sys.path.append(REPORT_API_PATH)
sys.path.append(COM_API_PATH)

from report import *
from com import *

# Create the report object, specifying the test data
report = ITReport(TLA, TLA_VERSION, SW_BRANCH, SVN_REVISION, HW_VERSION, AUTHOR,REPORT_NAME)


# Macro Definition
OFF = 0 
ON = 1 
RESULT_OK = 1 
RESULT_NOK = 0 

#Set CAN/LIN  Channel
com = Com('VECTOR')
can1 = com.open_can_channel(int(1.0),int(500000.0))
# Initialize Diagnostics
can1._init_dgn()

can1.load_dbc('BCCM_A_PMZCAN.dbc')

#################################################################
## Send Periodic Tester Present while doing diagnostics  ##
#################################################################
can1.dgn.ecu_reset(0x01)
can1.dgn.start_periodic_tp()
time.sleep(3)

# Name of the logfile where the frames will be logged

can_log_file = REPORT_NAME +'_dgn_logfile.txt'

Log_AllFrames = []

def GetActualResponseFrames():
    response_str = ''
    readByte = ''
    for frame_index in range(len(can1.dgn.iso.net._resp_frames)):
          if len(can1.dgn.iso.net._resp_frames) > 1 :
              if (frame_index == 0):
                  frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][2:8]
              else:
                  frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][1:8]
          else:
              frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][1:8]
          for frame_element in range(len(frameNewList)):
              readByte = str(hex(frameNewList[frame_element]))
              readByte = readByte.replace('0x','')
              if len(readByte) == 1:
                  readByte = '0' + readByte
              response_str +=readByte
    response_str = response_str.replace('0x','')
    response_str = response_str.upper()
    return response_str



def InvokeMessageBox(MessageStr):
    MessageStr = MessageStr +  "\nPress OK after performing the action." 
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    tkMessageBox.showinfo("Manual Input Required", MessageStr)
    root.destroy()

#######################
## Test Case 1       ##
#######################

def test_1():
    test_case_name = '\n\nTest Case 1: Check Software versions '
    test_case_desc = 'Check Application and Bootloader software version using DID: 0xFD00 and 0xF109'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 3  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='Perform ECU reset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5101'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Reset Successful.'
    else: 
          result = False
          comment ='Unable to reset.Test Fails:!!'

    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'51 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 4  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 5  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Application Software Version'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xFD00) 
    time.sleep(0.3)

    Expec_res = '62FD00083411'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 FD 00 08 34 11',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 6  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Bootloader Software Version'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xF109) 
    time.sleep(0.3)

    Expec_res = '62F109080303'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 F1 09 08 03 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 2       ##
#######################

def test_2():
    test_case_name = '\n\nTest Case 2: Check Service 0x31 with Routine 0404'
    test_case_desc = 'Check Service 0x31 Functionality '
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 8  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='Perform ECU reset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5101'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Reset Successful.'
    else: 
          result = False
          comment ='Unable to reset.Test Fails:!!'

    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'51 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 9  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 10  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 11  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session  Start VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '710104047B'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'71 01 04 04 7B',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 12  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session ,Stop VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '710204047A'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'71 02 04 04 7A',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 13  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session Get Result for VIN LEARN  using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '710304047A04'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'71 03 04 04 7A 04',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 3       ##
#######################

def test_3():
    test_case_name = '\n\nTest Case 3: Check Service 0x31 with Routine 0404'
    test_case_desc = 'Check Service 0x31 Functionality  in Default Session'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 15  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='Perform ECU reset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5101'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Reset Successful.'
    else: 
          result = False
          comment ='Unable to reset.Test Fails:!!'

    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'51 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 16  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 17  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session  Start VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 18  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session ,Stop VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 19  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session Get Result for VIN LEARN  using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 4       ##
#######################

def test_4():
    test_case_name = '\n\nTest Case 4: Check Service 0x31 with Routine 0404'
    test_case_desc = 'Check Service 0x31 Functionality  in Programming Session'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 21  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='Perform ECU reset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5101'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Reset Successful.'
    else: 
          result = False
          comment ='Unable to reset.Test Fails:!!'

    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'51 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 22  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.programming_session() 
    time.sleep(0.3)

    Expec_res = '5002'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 23  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session  Start VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 24  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session ,Stop VIN LEARN  Routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 25  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session Get Result for VIN LEARN  using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 5       ##
#######################

def test_5():
    test_case_name = '\n\nTest Case 5: Check routine execution in Extended Session  without Security access'
    test_case_desc = 'Check Routine 0x0E08: Reset ECU Central Configuration State/Data To Not Configured  in Extended session  without Security access'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 27  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 28  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    ################################
    ##          Send CAN signal  #
    ################################

    test_step_desc='Set PowerMode to "IgnitionOn_2" (6) '
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.send_cyclic_frame('BCM_PMZ_A',10) 
    can1.set_signal('PowerMode',[0x06]) 
    time.sleep(0.5)

    Expec_res = '6'
    Actual_res = can1.get_signal('PowerMode','BCM_PMZ_A')
    Actual_res = str(hex(Actual_res))
    Actual_res = Actual_res.replace('0x','')
    Actual_res = Actual_res.replace('L','')
    Actual_res = Actual_res.replace(' ','')
    Actual_res = Actual_res.upper()

    if Expec_res == Actual_res: 
          result = True
          comment ='CAN signal set Successfully.'
    else: 
          result = False
          comment ='CAN signal could not be set.'
    response_str = str(can1.get_frame(can1.dbc.find_frame_id('BCM_PMZ_A')))
    report.add_test_step(test_step_desc,result,'BCM_PMZ_A.PowerMode='+Actual_res,'BCM_PMZ_A.PowerMode = 06',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 30  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session without Security access,Start CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3133'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 33',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 6       ##
#######################

def test_6():
    test_case_name = '\n\nTest Case 6: Check routine execution in Extended Session with Security Level - 03'
    test_case_desc = 'Check Routine 0x0E08: Reset ECU Central Configuration State/Data To Not Configured  in Extended session  with Security Level - 03'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 32  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 33  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 34  #
    ##################################### #

    ################################
    ##          Security Access  #
    ################################

    test_step_desc='Request for  Security Access Level - 03'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.security_access(0x03)

    Expec_res = '6704'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'67 04',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    ################################
    ##          Send CAN signal  #
    ################################

    test_step_desc='Set PowerMode to "IgnitionOn_2" (6) '
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.send_cyclic_frame('BCM_PMZ_A',10) 
    can1.set_signal('PowerMode',[0x06]) 
    time.sleep(0.5)

    Expec_res = '6'
    Actual_res = can1.get_signal('PowerMode','BCM_PMZ_A')
    Actual_res = str(hex(Actual_res))
    Actual_res = Actual_res.replace('0x','')
    Actual_res = Actual_res.replace('L','')
    Actual_res = Actual_res.replace(' ','')
    Actual_res = Actual_res.upper()

    if Expec_res == Actual_res: 
          result = True
          comment ='CAN signal set Successfully.'
    else: 
          result = False
          comment ='CAN signal could not be set.'
    response_str = str(can1.get_frame(can1.dbc.find_frame_id('BCM_PMZ_A')))
    report.add_test_step(test_step_desc,result,'BCM_PMZ_A.PowerMode='+Actual_res,'BCM_PMZ_A.PowerMode = 06',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 36  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Start CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3133'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 33',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 37  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Stop CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3133'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 33',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 38  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Get Result for CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3133'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 33',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 7       ##
#######################

def test_7():
    test_case_name = '\n\nTest Case 7: Check routine execution in Extended Session with Security Level - 0F'
    test_case_desc = 'Check Routine 0x0E08: Reset ECU Central Configuration State/Data To Not Configured  in Extended session  with Security Level - 0F'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 40  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 41  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 42  #
    ##################################### #

    ################################
    ##          Security Access  #
    ################################

    test_step_desc='Request for  Security Access Level - 0F'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.security_access(0x0F)

    Expec_res = '6710'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'67 10',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    ################################
    ##          Send CAN signal  #
    ################################

    test_step_desc='Set PowerMode to "IgnitionOn_2" (6) '
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.send_cyclic_frame('BCM_PMZ_A',10) 
    can1.set_signal('PowerMode',[0x06]) 
    time.sleep(0.5)

    Expec_res = '6'
    Actual_res = can1.get_signal('PowerMode','BCM_PMZ_A')
    Actual_res = str(hex(Actual_res))
    Actual_res = Actual_res.replace('0x','')
    Actual_res = Actual_res.replace('L','')
    Actual_res = Actual_res.replace(' ','')
    Actual_res = Actual_res.upper()

    if Expec_res == Actual_res: 
          result = True
          comment ='CAN signal set Successfully.'
    else: 
          result = False
          comment ='CAN signal could not be set.'
    response_str = str(can1.get_frame(can1.dbc.find_frame_id('BCM_PMZ_A')))
    report.add_test_step(test_step_desc,result,'BCM_PMZ_A.PowerMode='+Actual_res,'BCM_PMZ_A.PowerMode = 06',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 44  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Start CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '71010E08'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'71 01 0E 08 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 45  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Stop CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3112'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 12 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 46  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='In Extended Session with Security access,Get Result for CCF Reset Routine '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x0E ,0x08], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3112'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 12 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 8       ##
#######################

def test_8():
    test_case_name = '\n\nTest Case 8: Check Service 31  Supported NRC'
    test_case_desc = 'Check Service 0x31behaviour'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 48  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='Send Request with service 0x31 with  invalid subfunction '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x04 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3112'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 31 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 49  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='stop the routine 0404  using service 0x31 without starting routine'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x04 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3124'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 24',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 50  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='send the start request with invalid routine using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x22 ,0x22], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 51  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='send the start request with invalid routine data using service 0x31'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x0E ,0x01 ,0x00 ,0x55 ,0x55], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3131'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 31',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 52  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='Send Request with service 0x31 with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x01 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3113'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 53  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='Send Request with service 0x31 with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x02 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3113'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 54  #
    ##################################### #

    ################################
    ##          ROUTINES          ##
    ################################

    test_step_desc='Send Request with service 0x31 with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x31 ,0x03 ,0x04], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F3113'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Routine Execution Succesful.'
    else: 
          result = False
          comment ='Routine Execution Fails:!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  31 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)



def endTest():
    report.generate_report(REPORT_API_PATH)
    sys.exit()




#############################
## Execute the test cases  ##
#############################

test_1()
time.sleep(1)
test_2()
time.sleep(1)
test_3()
time.sleep(1)
test_4()
time.sleep(1)
test_5()
time.sleep(1)
test_6()
time.sleep(1)
test_7()
time.sleep(1)
test_8()
time.sleep(1)

# Save CAN Log Files
can1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)
# Generate the final report
endTest()