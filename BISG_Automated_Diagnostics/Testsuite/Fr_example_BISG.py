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


com_path = os.path.abspath(r'..\latte_libs')
sys.path.append (com_path)

from com import Com


'''
================================================================================
Setup Flexray and CAN channels
================================================================================
'''
com = Com('VECTOR')
frObj  = com.open_fr_channel(0, 'Flexray_FIBEX_X_NCR16W31.xml', 'FrChannel_A', 'EPICB', [10, 50], cluster='FlexRay')
canObj = com.open_can_channel(1,500000)


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
def stopTest():
    canObj.stop_cyclic_frame('PMZ_CAN_NodeGWM_NM')
    com.exit()


'''
================================================================================
TEST CASE 1
================================================================================
'''
def test_1():
    response = frObj.dgn.read_did(0xF186)
    print response


'''
================================================================================
TEST CASE 2
================================================================================
'''
def test_2():
    response = frObj.dgn.read_did(0xD021)
    print response


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
stopTest()


