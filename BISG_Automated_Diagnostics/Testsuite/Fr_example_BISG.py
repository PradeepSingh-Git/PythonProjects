'''
===================================================================================
Integration of Latte libs for Diagnostics on FLEXRAY for JLR-BISG Inverter Project
(C) Copyright 2018 Lear Corporation
===================================================================================
'''

__author__  = 'Pradeep Singh'
__version__ = '1.0.0'
__email__   = 'psingh02@lear.com'

'''==============================================================================='''

import sys
import os
import time


com_path    = os.path.abspath(r'..\latte_libs')
report_path = os.path.abspath(r'..\latte_libs\report')

sys.path.append (com_path)
sys.path.append (report_path)

from com import Com
from report import HTMLReport


# Report Header Variables
AUTHOR       = 'Pradeep Singh'
TLA          = 'DGN'
PROJECT_NAME = 'JLR_BISG_D8_INVERTER'
SW_VERSION   = '1.0.0'
HW_VERSION   = 'BISG'
NETWORK_TYPE = 'Flexray'

report = HTMLReport(TLA, PROJECT_NAME, SW_VERSION, HW_VERSION, NETWORK_TYPE, AUTHOR)

'''
================================================================================
Description : Setup Flexray and CAN channels
================================================================================
'''
com = Com('VECTOR')
frObj  = com.open_fr_channel(0, 'fibex.xml', 'FrChannel_A', 'EPICB', [10, 50], cluster='FlexRay')
canObj = com.open_can_channel(1,500000)

'''
================================================================================
Description : Modifying the Response in desired Format
================================================================================
'''
def GetActualResponseFrames(response_buff):
    response_str = ''
    readByte = ''

    for element in range(len(response_buff)):
        readByte = str(hex(response_buff[element]))
        readByte = readByte.replace('0x','')
        if len(readByte) == 1:
            readByte = '0' + readByte
        response_str +=readByte

    response_str = response_str.replace('0x','')
    response_str = response_str.upper()
    return response_str


'''
================================================================================
START : Setup Pre-Conditions for the project
================================================================================
'''
def startTest():
    canObj.load_dbc('EPICB_B_PMZCAN.dbc')
    canObj.send_cyclic_frame('PMZ_CAN_NodeGWM_NM', 100) # 100 ms


'''
================================================================================
STOP : Finish Exit Conditions
================================================================================
'''
def endTest():
    #Generate HTML Report
    report.generate_report()

    #Save Logfile
    frObj.dgn.iso.net.log_file = report.get_log_dir()
    frObj.dgn.save_logfile()

    canObj.stop_cyclic_frame('PMZ_CAN_NodeGWM_NM')
    print "\nScript Execution Finished !!\n"
    com.exit()


'''
================================================================================
TEST CASE 1
================================================================================
'''
def test_1():

    test_case_name = 'Test Case 1: Check Software versions'
    test_case_desc = 'Check Application and Bootloader software version using DID: 0xFD00 and 0xF109'
    test_case_reqs = ''
    print '\n' + test_case_name + '\n'

    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)

    #######################################
    #              TEST STEP 1            #
    ##################################### #

    test_step_desc='Read Application Version - 0xFD00'
    result = False
    comment = ''

    Raw_res = frObj.dgn.read_did(0xFD00)

    Actual_res   = GetActualResponseFrames(Raw_res)
    Expected_res = '62FD00030800'

    if Expected_res == Actual_res[0:len(Expected_res)]:
        result = True
        comment ='Application Version Read Successful.'
    else:
        result = False
        comment ='Application Version Read Fails!!'

    report.add_test_step(test_step_desc,result,Actual_res,Expected_res,comment)


    #######################################
    #              TEST STEP 2            #
    ##################################### #

    test_step_desc='Read Bootloader Version - 0xF109'
    result = False
    comment = ''

    Raw_res = frObj.dgn.read_did(0xF109)

    Actual_res   = GetActualResponseFrames(Raw_res)
    Expected_res = '62F109040000'

    if Expected_res == Actual_res[0:len(Expected_res)]:
        result = True
        comment ='Bootloader Version Read Successful.'
    else:
        result = False
        comment ='Bootloader Version Read Fails!!'

    report.add_test_step(test_step_desc,result,Actual_res,Expected_res,comment)

'''
================================================================================
TEST CASE 2
================================================================================
'''
def test_2():

    test_case_name = 'Test Case 2: Check Current Diagnostic Control'
    test_case_desc = 'Check whether the control is in Application or Bootloader using DID: 0xD021'
    test_case_reqs = ''
    print '\n' + test_case_name + '\n'

    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)

    #######################################
    #              TEST STEP 1            #
    ##################################### #
    test_step_desc='Current Diagnostics Control - 0xD021'
    result = False
    comment = ''

    Raw_res = frObj.dgn.read_did(0xD021)

    Actual_res   = GetActualResponseFrames(Raw_res)
    Expected_res = '62D02100'

    if Expected_res == Actual_res[0:len(Expected_res)]:
        result = True
        comment ='Successful.'
    else:
        result = False
        comment ='Fails!!'

    report.add_test_step(test_step_desc,result,Actual_res,Expected_res,comment)

'''
================================================================================
                                 EXECUTE TEST CASES
================================================================================
'''
startTest()
time.sleep(1)
test_1()
test_2()
time.sleep(1)
endTest()


