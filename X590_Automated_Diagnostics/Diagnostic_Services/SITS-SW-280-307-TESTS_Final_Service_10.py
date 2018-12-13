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

REPORT_NAME = 'TLA_Service_10'

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



def CompareResults(ExpectedRes,ActualRes):
    returnVal = True
    temp_List = []
    for i in range(0,len(ExpectedRes),2):
          byteStr = ''
          byteStr = byteStr + ExpectedRes[i]
          byteStr = byteStr + ExpectedRes[i+1]
          byteHex_str = '0x'+ byteStr
          temp_List.append(byteHex_str)
    for j in range(0,len(temp_List)):
          if(ActualRes[j] == int(temp_List[j],16)):
                  continue
          else:
                  returnVal = False
    return returnVal



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
    test_case_name = '\n\nTest Case 2: Check Service 10 Functionality'
    test_case_desc = 'Check Service   10 behaviour'
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
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session Using Service   10'
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
    #Code block generated for row no = 9  #
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
    #Code block generated for row no = 10  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service   10'
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
    #Code block generated for row no = 11  #
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
    #Code block generated for row no = 12  #
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
    #Code block generated for row no = 13  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 14  #
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


    #######################################
    #Code block generated for row no = 15  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session Using Service   10 with SF 81'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 16  #
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
    #Code block generated for row no = 17  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service   10 with SF 82'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 18  #
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
    #Code block generated for row no = 19  #
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
    #Code block generated for row no = 20  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10 with SF 83'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 21  #
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
## Test Case 3       ##
#######################

def test_3():
    test_case_name = '\n\nTest Case 3: Check Service 10 Functionality'
    test_case_desc = 'Check Service 0x10 behaviour for timeout in Prog Session'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
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
    #Code block generated for row no = 24  #
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

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service 10'
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
    #Code block generated for row no = 27  #
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
    #Code block generated for row no = 28 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 29  #
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
    #Code block generated for row no = 30  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 31  #
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


    #######################################
    #Code block generated for row no = 32 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 33  #
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
    #Code block generated for row no = 34  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Programming Session  Using Service   10 with SF 82'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 35  #
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
    #Code block generated for row no = 36 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 37  #
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
    #Code block generated for row no = 38  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10 with SF 83'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 39  #
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


    #######################################
    #Code block generated for row no = 40 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 41  #
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
    #Code block generated for row no = 42  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 4       ##
#######################

def test_4():
    test_case_name = '\n\nTest Case 4: Check Service 10 Supported NRC'
    test_case_desc = 'Check Service   10 behaviour'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 44  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Send Request with service   10 with  invalid subfunction '
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x05)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 45  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Send Request with service   10 with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10, ], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 5       ##
#######################

def test_5():
    test_case_name = '\n\nTest Case 5: Check Service 10 Functionality'
    test_case_desc = 'Check Service   10 behaviour After Power RESET'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 47  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session Using Service   10'
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
    #Code block generated for row no = 48  #
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
    #Code block generated for row no = 49  #
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
    #Code block generated for row no = 50  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 51  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 52  #
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
    #Code block generated for row no = 53  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 54  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 55  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended without Security Access'
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
    #Code block generated for row no = 57  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    test_case_name = '\n\nTest Case 6: Check Service 10 Functionality'
    test_case_desc = 'Check Service   10 behaviour After Power RESET'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 59  #
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
    #Code block generated for row no = 60  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 61  #
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


    #######################################
    #Code block generated for row no = 62  #
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
    #Code block generated for row no = 63  #
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
    #Code block generated for row no = 64  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 65  #
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
    #Code block generated for row no = 66  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 67  #
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


    #######################################
    #Code block generated for row no = 68  #
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
    #Code block generated for row no = 69  #
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
    #Code block generated for row no = 70  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 7       ##
#######################

def test_7():
    test_case_name = '\n\nTest Case 7: Check Service 10 Functionality'
    test_case_desc = 'Check Service   10 behaviour After ECU HARD RESET'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 72  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Default Session Using Service   10'
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
    #Code block generated for row no = 73  #
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
    #Code block generated for row no = 74  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HARD RESET'
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
    #Code block generated for row no = 75  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 76  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 77  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 78  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HARD RESET'
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
    #Code block generated for row no = 79  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 80  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 81  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended without Security Access'
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
    #Code block generated for row no = 82  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 83  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 84  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 85  #
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
    #Code block generated for row no = 86  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 87  #
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


    #######################################
    #Code block generated for row no = 88  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 89  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 90  #
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
    #Code block generated for row no = 91  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 92  #
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


    #######################################
    #Code block generated for row no = 93  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 94  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 8       ##
#######################

def test_8():
    test_case_name = '\n\nTest Case 8: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify the Response for each Subfunction of DiagnosticSessionControl (  10) Service with NRC 0x12 for SubfuntionNotSupported Parameters'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 96  #
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
    #Code block generated for row no = 97  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 98  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x40)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 99  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 100  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 101  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 102  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 103  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0xC0)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 104  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 105  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x40)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 106  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 107  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 108  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 109  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 110  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0xC0)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 111  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 112  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended without Security Access'
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
    #Code block generated for row no = 113  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x40)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 114  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 115  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 116  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 117  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 118  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0xC0)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 119  #
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
    #Code block generated for row no = 120  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x40)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 121  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 122  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 123  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 124  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 125  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0xC0)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 126  #
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
    #Code block generated for row no = 127  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x40)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 128  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x81)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 129  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x82)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 130  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 131  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0x83)
    time.sleep(0.3)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 132  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.service_0x10(0xC0)
    time.sleep(0.3)

    Expec_res = '7F1012'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 12',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 9       ##
#######################

def test_9():
    test_case_name = '\n\nTest Case 9: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that DiagnosticSessionControl (  10) Service will return NRC 0x13 for IncorrectMessageLengthOrInvalidFormat Parameters '
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 134  #
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
    #Code block generated for row no = 135 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 136  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Contro DefaultSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x01 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 137  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgrammingSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x02 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 138  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtendedSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x03 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 139  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x40 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 140  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x81 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 141  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x82 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 142  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x83 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 143  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0xC0 ,0x00], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 144  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Contro DefaultSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x01 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 145  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgrammingSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x02 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 146  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtendedSession'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x03 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 147  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnostic Session'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x40 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 148  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control DefaultSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x81 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 149  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUProgramming Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x82 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 150  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control ECUExtended Session(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0x83 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 151  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Diagnostic Session Control EOLExtendedDiagnosticSession(No Response Required)'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x10 ,0xC0 ,0xFF], 'PHYSICAL') 
    time.sleep(0.3)

    Expec_res = '7F1013'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 10       ##
#######################

def test_10():
    test_case_name = '\n\nTest Case 10: Check Service 10 Functionality'
    test_case_desc = 'Check Service   10 behaviour After Power RESET'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 153  #
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
    #Code block generated for row no = 154  #
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
    #Code block generated for row no = 155  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 156  #
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


    #######################################
    #Code block generated for row no = 157  #
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
    #Code block generated for row no = 158  #
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
    #Code block generated for row no = 159  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 160  #
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
    #Code block generated for row no = 161  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Enter in Extended Session  Using Service   10'
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
    #Code block generated for row no = 162  #
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


    #######################################
    #Code block generated for row no = 163  #
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
    #Code block generated for row no = 164  #
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
    #Code block generated for row no = 165  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 11       ##
#######################

def test_11():
    test_case_name = '\n\nTest Case 11: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that ProgrammingSession will revert to Default Session after 5 seconds when Tester Present is set to OFF'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 167  #
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
    #Code block generated for row no = 168  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 169  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 170 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 171  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 172  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 173  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 174 #
    #######################################

    test_step_desc='Let 3 seconds pass'
    print test_step_desc
    time.sleep(3)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 175  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 176  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 177  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 178 #
    #######################################

    test_step_desc='Let 1 second'
    print test_step_desc
    time.sleep(1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 179  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 180  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 181  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 182 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 183  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 184  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 185 #
    #######################################

    test_step_desc='Let 10 seconds pass'
    print test_step_desc
    time.sleep(10)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 186  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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


#######################
## Test Case 12       ##
#######################

def test_12():
    test_case_name = '\n\nTest Case 12: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that Extended Session will revert to Default Session after 5 seconds when Tester Present is set to OFF'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 188  #
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
    #Code block generated for row no = 189  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 190  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 191 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 192  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 193  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 194  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 195 #
    #######################################

    test_step_desc='Let 3 seconds pass'
    print test_step_desc
    time.sleep(3)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 196  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 197  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 198  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 199 #
    #######################################

    test_step_desc='Let 1 second'
    print test_step_desc
    time.sleep(1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 200  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 201  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 202  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 203 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 204  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 205  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 206 #
    #######################################

    test_step_desc='Let 10 seconds pass'
    print test_step_desc
    time.sleep(10)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 207  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 13       ##
#######################

def test_13():
    test_case_name = '\n\nTest Case 13: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that Extended Session with Security Level 03 Unlock will revert to Default Session after 5 seconds when Tester Present is set to OFF'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 209  #
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
    #Code block generated for row no = 210  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 211  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 212 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 213  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 214  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 215  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 216  #
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
    #Code block generated for row no = 217 #
    #######################################

    test_step_desc='Let 3 seconds pass'
    print test_step_desc
    time.sleep(3)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 218  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 219  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 220  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 221  #
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
    #Code block generated for row no = 222 #
    #######################################

    test_step_desc='Let 1 second'
    print test_step_desc
    time.sleep(1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 223  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 224  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 225  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 226  #
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
    #Code block generated for row no = 227 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 228  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 229  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 230  #
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
    #Code block generated for row no = 231 #
    #######################################

    test_step_desc='Let 10 seconds pass'
    print test_step_desc
    time.sleep(10)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 232  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 14       ##
#######################

def test_14():
    test_case_name = '\n\nTest Case 14: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that Extended Session with Security lvel 0F Unlock will revert to Default Session after 5 seconds when Tester Present is set to OFF'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 234  #
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
    #Code block generated for row no = 235  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present OFF'
    can1.dgn.stop_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 236  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 237 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 238  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 239  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 240  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 241  #
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
    #Code block generated for row no = 242 #
    #######################################

    test_step_desc='Let 3 seconds pass'
    print test_step_desc
    time.sleep(3)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 243  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 244  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 245  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 246  #
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
    #Code block generated for row no = 247 #
    #######################################

    test_step_desc='Let 1 second'
    print test_step_desc
    time.sleep(1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 248  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 249  #
    ##################################### #

    ###################################
    ##         Tester Present         ##
    ###################################

    test_step_desc='Make Tester Present ON'
    can1.dgn.start_periodic_tp()
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 250  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 251  #
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
    #Code block generated for row no = 252 #
    #######################################

    test_step_desc='Let 5 seconds pass'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 253  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 254  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Extended Session'
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
    #Code block generated for row no = 255  #
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
    #Code block generated for row no = 256 #
    #######################################

    test_step_desc='Let 10 seconds pass'
    print test_step_desc
    time.sleep(10)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 257  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 15       ##
#######################

def test_15():
    test_case_name = '\n\nTest Case 15: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify Supported DiagnosticSessionControl (  10) Service Transitions '
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 259  #
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
    #Code block generated for row no = 260  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 261  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 262 #
    #######################################

    test_step_desc='Let 10ms pass'
    print test_step_desc
    time.sleep(0.01)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 263  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 264  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 265  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 266 #
    #######################################

    test_step_desc='Let 10ms pass'
    print test_step_desc
    time.sleep(0.01)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 267  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 268  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 269  #
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
    #Code block generated for row no = 270 #
    #######################################

    test_step_desc='Let 50ms pass'
    print test_step_desc
    time.sleep(0.05)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 271  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 272  #
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
    #Code block generated for row no = 273  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 274 #
    #######################################

    test_step_desc='Let 10ms pass'
    print test_step_desc
    time.sleep(0.01)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 275  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 276  #
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
    #Code block generated for row no = 277  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 278 #
    #######################################

    test_step_desc='Let 10ms pass'
    print test_step_desc
    time.sleep(0.01)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 279  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 280  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 281  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 282 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 283  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 284  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
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
    #Code block generated for row no = 285  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 286  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 287 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 288  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 289  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 290  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 291  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 292 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 293  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 294  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '5001001901F4'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'50 01 00 19 01 F4',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 295  #
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
    #Code block generated for row no = 296  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Default'
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
    #Code block generated for row no = 297 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 298  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 299  #
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
    #Code block generated for row no = 300  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 301 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 302  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 303  #
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
    #Code block generated for row no = 304  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
    #Code block generated for row no = 305 #
    #######################################

    test_step_desc='Let 100ms pass'
    print test_step_desc
    time.sleep(0.1)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 306  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
    #Code block generated for row no = 307  #
    ##################################### #

    ################################
    ## Reset By Diagnostics  ##
    ################################

    test_step_desc='ECU HardReset'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.ecu_reset(0x01)
    time.sleep(1)

    Expec_res = '51'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'51',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 308  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to ExtendedLocked'
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
    #Code block generated for row no = 309  #
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
    #Code block generated for row no = 310 #
    #######################################

    test_step_desc='Let 50ms pass'
    print test_step_desc
    time.sleep(0.05)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 311  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read Current Diagnostic Session'
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
## Test Case 16       ##
#######################

def test_16():
    test_case_name = '\n\nTest Case 16: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that the Request for ProgrammingSession will return NRC 0x22 when Battery Voltage is LOW (<9.0)'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 313  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Power OFF'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 314  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Power ON'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 315  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 13.5V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 316 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 317  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 8.9V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 318  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.programming_session() 
    time.sleep(0.3)

    Expec_res = '7F1022'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 22',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 319  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 13.5V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 320  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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


#######################
## Test Case 17       ##
#######################

def test_17():
    test_case_name = '\n\nTest Case 17: Check Service 10 Functionality'
    test_case_desc = 'This scenario will verify that the Request for ProgrammingSession will return NRC 0x22 when Battery Voltage is High (>16.0)'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 322  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Power OFF'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 323  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Power ON'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 324  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 13.5V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 325 #
    #######################################

    test_step_desc='Wait for 5 Sec'
    print test_step_desc
    time.sleep(5)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 326  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 16.1V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 327  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.programming_session() 
    time.sleep(0.3)

    Expec_res = '7F1022'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 10 22',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 328  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='SUPPLY VOLTAGE = 13.5V'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 329  #
    ##################################### #

    ################################
    ##          Session Ctrl  #
    ################################

    test_step_desc='Set Diagnostic Session to Programming'
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
test_9()
time.sleep(1)
test_10()
time.sleep(1)
test_11()
time.sleep(1)
test_12()
time.sleep(1)
test_13()
time.sleep(1)
test_14()
time.sleep(1)
test_15()
time.sleep(1)
test_16()
time.sleep(1)
test_17()
time.sleep(1)

# Save CAN Log Files
can1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)
# Generate the final report
endTest()