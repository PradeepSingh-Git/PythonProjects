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

REPORT_NAME = 'TLA_Service_19'

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
    test_case_name = '\n\nTest Case 2: Check Service 19 0A-ReportSupportedDTC'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 0A'
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
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 0A-ReportSupportedDTC'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x0A], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '590A'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 0A',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 3       ##
#######################

def test_3():
    test_case_name = '\n\nTest Case 3: Check Service 19 14-ReportDTCFaultDetectionCounter'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 14'
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
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 14-ReportDTCFaultDetectionCounter'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x14], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5914'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 14',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 11 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 4       ##
#######################

def test_4():
    test_case_name = '\n\nTest Case 4: Check Service 19 01-reportNumberOfDTCByStatusMask'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 01'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 13  #
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
    #Code block generated for row no = 14  #
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


    ################################
    ##          Send CAN signal  #
    ################################

    test_step_desc='Set MECU Supply Voltage = 0xB0FF111200131000 using CAN signal VehicleConfParameters to set Global Snapshot Data (DD00 , DD02 & DD06)'
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.send_cyclic_frame('VEHCONFIG_400PMZ',10) 
    can1.set_signal('VehicleConfParameters',[0xB0,0xFF,0x11,0x12,0x00,0x13,0x10,0x00]) 
    time.sleep(0.5)

    Expec_res = 'B0FF111200131000'
    Actual_res = can1.get_signal('VehicleConfParameters','VEHCONFIG_400PMZ')
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
    response_str = str(can1.get_frame(can1.dbc.find_frame_id('VEHCONFIG_400PMZ')))
    report.add_test_step(test_step_desc,result,'VEHCONFIG_400PMZ.VehicleConfParameters='+Actual_res,'VEHCONFIG_400PMZ.VehicleConfParameters = B0FF111200131000',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    ################################
    ##          Send CAN signal  #
    ################################

    test_step_desc='Set MECU Supply Voltage = 0xB11F001344550000 using CAN signal VehicleConfParameters to set Global Snapshot Data (DD01 , DD04 & DD05)'
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.send_cyclic_frame('VEHCONFIG_400PMZ',10) 
    can1.set_signal('VehicleConfParameters',[0xB1,0x1F,0x00,0x13,0x44,0x55,0x00,0x00]) 
    time.sleep(0.5)

    Expec_res = 'B11F001344550000'
    Actual_res = can1.get_signal('VehicleConfParameters','VEHCONFIG_400PMZ')
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
    response_str = str(can1.get_frame(can1.dbc.find_frame_id('VEHCONFIG_400PMZ')))
    report.add_test_step(test_step_desc,result,'VEHCONFIG_400PMZ.VehicleConfParameters='+Actual_res,'VEHCONFIG_400PMZ.VehicleConfParameters = B11F001344550000',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 17  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 01-reportNumberOfDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x01 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5901'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 01 ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 18 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 19  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask to check DTC 0D5613 is not logged'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x02 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5902FF'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02 FF ',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 20 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 21  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Set Fault,Proximity Detection Circuit open'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 22  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 01-reportNumberOfDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x01 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5901FF'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,' 59 01 FF',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 23 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 24  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 12-ReportNumberOfEmissionsRelatedOBDDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x12 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5912FF'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 12 FF',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 25 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 5       ##
#######################

def test_5():
    test_case_name = '\n\nTest Case 5: Check Service 19 02-reportDTCByStatusMask'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 02'
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
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 02-reportDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x02 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5902'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 02',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 6       ##
#######################

def test_6():
    test_case_name = '\n\nTest Case 6: Check Service 19 04 & 19 13 -reportDTCSnapshotRecordByDTCNumber ,ReportEmissionsRelatedOBDDTCByStatusMask'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 04 , 19 13'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 29  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 04-reportDTCSnapshotRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x04 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5904OD5613271007DD00FF111200DD011F0013DD0213DD0444DD0555DD06004994XX1107DD00XXXXXXXXDD00FF111200DD011F0013DD0213DD0444DD0555DD06004994XX'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 04 OD 56 13 27 10 07 DD 00 FF 11 12 00 DD 01 1F 00 13 DD 02 13 DD 04 44 DD 05 55 DD 06 00 49 94  XX 11 07 DD 00 XX XX XX XX DD 00 FF 11 12 00 DD 01 1F 00 13 DD 02 13 DD 04 44 DD 05 55 DD 06 00 49 94 XX',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 30  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 13-ReportEmissionsRelatedOBDDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x13 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5913FF0D561327'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 13 FF 0D 56 13 27',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 31 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 32  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 12-ReportNumberOfEmissionsRelatedOBDDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x12 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59120D561327'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 12 0D 56 13 27',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 33 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 7       ##
#######################

def test_7():
    test_case_name = '\n\nTest Case 7: Check Service 19 06 , 19 15 -reportDTCExtDataRecordByDTCNumber , ReportDTCWithPermanentStatus'
    test_case_desc = 'Check OBD DTC  P0D5613 Proximity Detection Circuit Open - Service 19 06 ,19 15'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 35  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132701000200030004000500107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 27 01 00 02 00 03 00 04 00 05 00 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 36  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Change Ignition Cycle'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 37  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132F01000200030004010500107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 2F 01 00 02 00 03 00 04 01 05 00 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 38  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 15-ReportDTCWithPermanentStatus'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x15], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5915FF0D56132F'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 15 FF 0D 56 13 2F',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 39 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 40  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Remove Falut'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 41  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Change Ignition Cycle'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 42  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132801000200030004020500107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 28 01 00 02 00 03 00 04 02 05 00 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 43  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Change Ignition Cycle'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 44  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132801000200030004020500107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 28 01 00 02 00 03 00 04 02 05 00 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 45  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Change Ignition Cycle'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 47  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132801000200030004020501107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 28 01 00 02 00 03 00 04 02 05 01 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 48  #
    ##################################### #

    ################################
    ##          Message Pop-up  #
    ################################

    test_step_desc='Change Ignition Cycle and Change Warm Up Cycle  till report number 05 reach to 40(Hex -28)'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 49  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 06-reportDTCExtDataRecordByDTCNumber'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x06 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '59060D56132001000200030004020528107F4100000000000000000000'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 06 0D 56 13 20 01 00 02 00 03 00 04 02 05 28 10 7F 41 00 00 00 00 00 00 00 00 00 00',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 50  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 12-reportNumberOfDTCByStatusMask'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x12 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5912FF'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 12 FF',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 51 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 8       ##
#######################

def test_8():
    test_case_name = '\n\nTest Case 8: Check Service 19 14-ReportDTCFaultDetectionCounter'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 14'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 53  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 14-ReportDTCFaultDetectionCounter'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x14], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = '5914'
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'59 14',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 54 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 9       ##
#######################

def test_9():
    test_case_name = '\n\nTest Case 9: Check Service 19 94-ReportDTCFaultDetectionCounter - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 94'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 56  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 94-ReportDTCFaultDetectionCounter - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x94 ,0x0D ,0x56 ,0x13 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


    #######################################
    #Code block generated for row no = 57 #
    #######################################

    test_step_desc='Wait for 1 sec'
    print test_step_desc
    time.sleep(1.0)
    report.add_test_step(test_step_desc,True,'','')


#######################
## Test Case 10       ##
#######################

def test_10():
    test_case_name = '\n\nTest Case 10: Check Service 19 81-ReportNumberOfDTCByStatusMask - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 81'
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
    ##          Message Pop-up  #
    ################################

    test_step_desc='Set Fault,Proximity Detection Circuit open'
    InvokeMessageBox(test_step_desc)
    report.add_test_step(test_step_desc,True,'','')


    #######################################
    #Code block generated for row no = 60  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 81-ReportNumberOfDTCByStatusMask - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x81 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 11       ##
#######################

def test_11():
    test_case_name = '\n\nTest Case 11: Check Service 19 82-DTCByStatusMask - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 82'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 62  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 82-DTCByStatusMask - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x82 ,0x27], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 12       ##
#######################

def test_12():
    test_case_name = '\n\nTest Case 12: Check Service 19 84-ReportDTCSnapshotRecordByDTCNumber - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 84'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 64  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 84-ReportDTCSnapshotRecordByDTCNumber - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x84 ,0x0D ,0x56 ,0x11 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 13       ##
#######################

def test_13():
    test_case_name = '\n\nTest Case 13: Check Service 19 86 -ReportDTCExtendedDataRecordByDTCNumber - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 86'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 66  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 86 ReportDTCExtendedDataRecordByDTCNumber - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x86 ,0x0D ,0x56 ,0x11 ,0xFF], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
    Log_AllFrames.append(response_str)


#######################
## Test Case 14       ##
#######################

def test_14():
    test_case_name = '\n\nTest Case 14: Check Service 19 8A -ReportSupportedDTC - No Response Required'
    test_case_desc = 'Check OBD DTC P0D5613 Proximity Detection Circuit Open - Service 19 8A'
    test_case_reqs = ''
    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
    test_Conclusion = 'Test Not started'
    can1.dgn.iso.net._all_frames = []
    can1.dgn.iso.net._resp_frames = []
    can1.stop_tx_frames()
    response_str = '\n'
    print test_case_name
 
 
    
    #######################################
    #Code block generated for row no = 68  #
    ##################################### #

    ################################
    ##    READ DTC Information    ##
    ################################

    test_step_desc='send request 19 8A ReportSupportedDTC - No Response Required'
    can1.dgn.iso.net._all_frames = []
    test_Result = False
    comment = '\n'
    response_str = '\n'

    can1.dgn.iso.net.send_request([0x19 ,0x8A], 'PHYSICAL') 
    time.sleep(1)

    Expec_res = ''
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
    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'',comment + '\n' + '')
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

# Save CAN Log Files
can1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)
# Generate the final report
endTest()