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

REPORT_NAME = 'TLA_Service_14'

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

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0xFD ,0x00], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62FD00083411'

    if (CompareResults(Expec_res,Actual_res)): 
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

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0xF1 ,0x09], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62F109080303'

    if (CompareResults(Expec_res,Actual_res)): 
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
    test_case_name = '\n\nTest Case 2: Configure the  ECU to OBD (D7u) '
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
    #Code block generated for row no = 8  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Select D7u From VehSim Panel To configure the ECU to OBD'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 3       ##
#######################

def test_3():
    test_case_name = '\n\nTest Case 3: Check session support for Service 14'
    test_case_desc = 'Clear DTC in Default Session using Service 0x14 '
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 10  #
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
    #Code block generated for row no = 11  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read DID 499E to check the "PROX_DET_S3_CLOSED"'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0x49 ,0x9E], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62499E059D03030140'

    if (CompareResults(Expec_res,Actual_res)): 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 49 9E 05 9D 03 03 01 40',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 12  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Set Fault,Proximity Detection Circuit  Open'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 13  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read DID 499E to check the "PROX_DET_OPEN"'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0x49 ,0x9E], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62499E000A04000000'

    if (CompareResults(Expec_res,Actual_res)): 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 49 9E 00 0A 04 00 00 00 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 14  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 01-reportNumberOfDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x01, 0x27])
    time.sleep(1)

    Expec_res = '5901FF01'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 01 FF 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 15  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x02, 0x27])
    time.sleep(1)

    Expec_res = '5902FF0D561327'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 FF 0D 56 13 27',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 16 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 17  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Remove the fault condition'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 18  #
    ##################################### #

    ###################################
    ## Clear Diagnostics Information  ##
    ###################################

    test_step_desc='ClearDiagnosticInformation'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x14 ,0xFF ,0xFF ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '54'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'54',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 19 #
    #######################################

    test_step_desc='Wait for 5 sec'
    print test_step_desc
    time.sleep(5.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 20  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask to check DTC 0D5611 is not logged'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x02, 0x27])
    time.sleep(1)

    Expec_res = '590200'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 00 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 21 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


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

    ###################################
    ## Clear Diagnostics Information  ##
    ###################################

    test_step_desc='ClearDiagnosticInformation'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x14 ,0xFF ,0xFF ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F1411'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 14 11',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 24 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 4       ##
#######################

def test_4():
    test_case_name = '\n\nTest Case 4: Check session support for Service 14'
    test_case_desc = 'Clear DTC in Extended Session using Service 0x14 '
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 26  #
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
    #Code block generated for row no = 27  #
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
    #Code block generated for row no = 28  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask to check DTC 0D5611 is not logged'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x02, 0x27])
    time.sleep(1)

    Expec_res = '5902FF00'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 FF 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 29 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 30  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read DID 499E to check the "PROX_DET_S3_CLOSED"'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0x49 ,0x9E], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62499E059D03030140'

    if (CompareResults(Expec_res,Actual_res)): 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 49 9E 05 9D 03 03 01 40',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 31  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Set Fault,Proximity Detection Circuit  Open'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 32  #
    ##################################### #

    ################################
    ##          Read DID          ##
    ################################

    test_step_desc='Read DID 499E to check the "PROX_DET_OPEN"'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    Actual_res=can1.dgn.iso.net.send_request([0x22 ,0x49 ,0x9E], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '62499E000A04000000'

    if (CompareResults(Expec_res,Actual_res)): 
          result = True
          comment ='Test Successful.'
    else: 
          result = False
          comment ='Test Fails!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'62 49 9E 00 0A 04 00 00 00 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 33  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 01-reportNumberOfDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x01, 0x27])
    time.sleep(1)

    Expec_res = '5901FF01'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 01 FF 01',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 34  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x02, 0x27])
    time.sleep(1)

    Expec_res = '5902FF0D561327'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 FF 0D 56 13 27',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 35 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 36  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Remove the fault condition'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 37  #
    ##################################### #

    ###################################
    ## Clear Diagnostics Information  ##
    ###################################

    test_step_desc='ClearDiagnosticInformation'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x14 ,0xFF ,0xFF ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '54'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'54',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 38  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask to check DTC 0D5611 is not logged'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.read_dtcs([0x02, 0x27])
    time.sleep(1)

    Expec_res = '590200'
    Actual_res = GetActualResponseFrames()

    if Expec_res == Actual_res[0:len(Expec_res)]: 
          result = True
          comment ='Read DTC Successful.'
    else: 
          result = False
          comment ='Read DTC Failed!!'
    for j in range(len(can1.dgn.iso.net._all_frames)): 
          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])
          response_str =  response_str + '\n'
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 00 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 5       ##
#######################

def test_5():
    test_case_name = '\n\nTest Case 5: Check Service 14 Supported NRC'
    test_case_desc = 'Check Service 0x14 behaviour'
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

    ###################################
    ## Clear Diagnostics Information  ##
    ###################################

    test_step_desc='Send Request with service 0x14 with  incorrect Mesaage Length'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x14, ], 'PHYSICAL')
    time.sleep(1)

    Expec_res = '7F1413'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 14 13',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 41  #
    ##################################### #

    ###################################
    ## Clear Diagnostics Information  ##
    ###################################

    test_step_desc='Send Request with service 0x14 with  incorrect  Data'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x14 ,0x00 ,0x01 ,0x00], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '7F1431'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'7F 14 31',comment + '\n' + '')
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

# Save CAN Log Files
can1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)
# Generate the final report
endTest()