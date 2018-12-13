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

REPORT_NAME = 'TLA_Service_3E'

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

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
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
    test_case_name = '\n\nTest Case 2: Check Service 3E Functionality'
    test_case_desc = 'Check Service 0x3E behaviour'
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

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present()
    time.sleep(1)

    Expec_res = '7E00'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7E 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 9  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 10  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 11  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service 0x10'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.programming_session() 
    time.sleep(0.3)

    Expec_res = '5002001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 02 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 12  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Programming Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10002'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 13 #
    #######################################

    test_step_desc='Wait for 30 Sec'
    print test_step_desc
    time.sleep(30.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 14  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Programming Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10002'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 15  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 16 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 17  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 18  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 19  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
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
    #Code block generated for row no = 20  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 21 #
    #######################################

    test_step_desc='Wait for 30 Sec'
    print test_step_desc
    time.sleep(30.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 22  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 23  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 24 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 25  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 26  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E with SF 80'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present_spr()
    time.sleep(1)

    Expec_res = ''
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 27  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session '
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
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 29  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service 0x10'
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
    #Code block generated for row no = 30  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Programming Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10002'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 31 #
    #######################################

    test_step_desc='Wait for 2 Sec'
    print test_step_desc
    time.sleep(2.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 32  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Programming Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10002'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 33  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 34 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 35  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 36  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E with SF 80'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present_spr()
    time.sleep(1)

    Expec_res = ''
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 37  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
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
    #Code block generated for row no = 38  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 39 #
    #######################################

    test_step_desc='Wait for 2 Sec'
    print test_step_desc
    time.sleep(2.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 40  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 41  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 42 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 43  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 3       ##
#######################

def test_3():
    test_case_name = '\n\nTest Case 3: Check Service 3E Functionality'
    test_case_desc = 'Check Service 0x3E behaviour'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 45  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session Using Service 0x10'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 46  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 47  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present()
    time.sleep(1)

    Expec_res = '7E00'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7E 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 48  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU Reset'
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
    #Code block generated for row no = 49  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 50  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service 0x10'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.programming_session() 
    time.sleep(0.3)

    Expec_res = '5002001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 02 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 51  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Programming Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10002'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 52  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present()
    time.sleep(1)

    Expec_res = '7E00'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7E 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 53  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU Reset'
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
    #Code block generated for row no = 54  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 55  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service 0x10'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 56  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 4       ##
#######################

def test_4():
    test_case_name = '\n\nTest Case 4: Check Service 3E Supported NRC'
    test_case_desc = 'Check Service 0x3E behaviour'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 58  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Send Request with service 0x3E with  invalid subfunction '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present_custom(0x02)
    time.sleep(1)

    Expec_res = '7F3E12'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 3E 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 59  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Send Request with service 0x3E with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x3E, ], 'PHYSICAL')
    time.sleep(1)

    Expec_res = '7F3E13'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F  3E 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 5       ##
#######################

def test_5():
    test_case_name = '\n\nTest Case 5: Check Service 3E Functionality'
    test_case_desc = 'Check Service 0x3E behaviour with  Security Access Level - 03'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 61  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 62  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 63  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 64  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 65  #
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


    #######################################
    #Code block generated for row no = 66  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 67 #
    #######################################

    test_step_desc='Wait for 30 Sec'
    print test_step_desc
    time.sleep(30.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 68  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 69  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 70 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 71  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 72  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E with SF 80'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present_spr()
    time.sleep(1)

    Expec_res = ''
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 73  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 74  #
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


    #######################################
    #Code block generated for row no = 75  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 76 #
    #######################################

    test_step_desc='Wait for 2 Sec'
    print test_step_desc
    time.sleep(2.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 77  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 78  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 79 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 80  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 6       ##
#######################

def test_6():
    test_case_name = '\n\nTest Case 6: Check Service 3E Functionality'
    test_case_desc = 'Check Service 0x3E behaviour with  Security Access Level - 0F'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 82  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.default_session() 
    time.sleep(0.3)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 83  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 84  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 85  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 86  #
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


    #######################################
    #Code block generated for row no = 87  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 88 #
    #######################################

    test_step_desc='Wait for 30 Sec'
    print test_step_desc
    time.sleep(30.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 89  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 90  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 91 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 92  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 93  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON Using Service 3E with SF 80'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.tester_present_spr()
    time.sleep(1)

    Expec_res = ''
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Failed.'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 94  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.extended_session() 
    time.sleep(0.3)

    Expec_res = '5003001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 03 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 95  #
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


    #######################################
    #Code block generated for row no = 96  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 97 #
    #######################################

    test_step_desc='Wait for 2 Sec'
    print test_step_desc
    time.sleep(2.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 98  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in  Extended Session continuously'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10003'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 03',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 99  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 100 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 101  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Check Response  of PID  D100 in Default Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_did(0xD100) 
    time.sleep(0.3)

    Expec_res = '62D10001'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 D1 00 01',comment + '\n' + '')
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

# Save CAN Log Files
can1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)
# Generate the final report
endTest()