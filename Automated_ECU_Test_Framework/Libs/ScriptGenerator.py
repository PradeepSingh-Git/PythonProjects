'''
====================================================================
Framework for autogenerating Testcases in Python by fetching data from
excel sheet. These scripts then run the tests automatically on ECU.
(C) Copyright 2018 Lear Corporation
====================================================================
'''

__author__ = 'Pradeep Singh'
__version__ = '1.0.1'
__email__   = 'psingh02@lear.com'

'''
CHANGE LOG
==========
1.0.1 Completely redesigning the template and script files
1.0.0 Initial version
'''

import sys
import os
import time
import py_compile
from openpyxl import *

''' Adding path for loading correctly tsuite library '''
tsuite_path = os.path.abspath(r'Libs\tsuite')
sys.path.append(tsuite_path)

from tsuite import *


testcaseFile = str(sys.argv[1])
testcaseFileSheet = str(sys.argv[2])
testcaseDirectory = sys.argv[3]
testcaseScriptFile = testcaseFile.split('.')[0] + "_" + testcaseFileSheet

'''Create Object of Testsuite class'''
tsuiteObj = Testsuite(testcaseFile,testcaseFileSheet,testcaseDirectory,17,1,2,3,4,5,6,7,8,9,10,18)

tsuiteObj.readTestWorkbook()        # Load Test Workbook
tsuiteObj.createDataDictionary()    # Creates dictionary of data from Excel sheet
tsuiteObj.createFolders()           # Create Folder hierarchy which will contain python scripts
tsuiteObj.createBatchFile()         # Create batch file to invoke python scripts

'''Begin Creating and Writing to Python script'''
tsuiteObj.openPythonFile()
tsuiteObj.writeCopyright()
tsuiteObj.writePathSettings()
tsuiteObj.writeReportSettings()
tsuiteObj.writeChannelSettings()
tsuiteObj.writePreconditions()
tsuiteObj.writeGetActualRespDef()
tsuiteObj.writeInvokeMsgBoxDef()
tsuiteObj.writexlrespfunction()


print "\n------------------START OF WRITING TESTCASES TO PYTHON SCRIPT-------------------\n"

count=0
testcasenumber=0
teststepnumber=0

for testcase in range(0,tsuiteObj.get_totaltests()):
    count+=1
    curr_testcount=count-1
    print "\n"
    print "###############################"
    print "#                             #"
    print "#      Start of Testcase " + str(count) + "    #"
    print "#                             #"
    print "###############################"
    print "\n"

    tsuiteObj.writeTestCaseDef(testcasenumber)
    tsuiteObj.writerow_number+=1# This is used to keep track of the row number. It uses the first row / tableHDR as a base (CHeck tsuiteOBJ)

    if(count<=tsuiteObj.get_totaltests):
        for teststep in range(0,int(tsuiteObj.get_numberofteststeps(testcasenumber))):
            tsuiteObj.writerow_number+=1
            if tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber)   == 'DIAG':
                tsuiteObj.processTypeDIAG(testcasenumber,teststepnumber)

            elif tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'MSG_POPUP':
                tsuiteObj.processTypePOPUP(testcasenumber,teststepnumber)

            elif tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'DELAY_SEC':
                tsuiteObj.processTypeDELAY(testcasenumber,teststepnumber)

            elif tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'CAN_SIGNAL':
                tsuiteObj.processTypeCANSIGNAL(testcasenumber,teststepnumber)

            elif tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'CAN_FRAME':
                tsuiteObj.processTypeCANFRAME(testcasenumber,teststepnumber)

            elif tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'PERIODIC_TP':
                tsuiteObj.processTypePERIODIC_TP(testcasenumber,teststepnumber)


            else:  #Check if none of the Command Type is provided
                print "\nCommand Type is not selected for test step"
                print "\nCheck Row no: " + str(tsuiteObj.writerow_number)
                print "\nCheck Column no:" + str(tsuiteObj.rowTypeCol)

            print "Writing Test Step " + str(teststepnumber+1)

            teststepnumber+=1
    else:
        print "Error count exceeds number of test cases"
    teststepnumber=0
    testcasenumber+=1

tsuiteObj.writeEndTestDef()
tsuiteObj.writeCallingOfTestcases()
tsuiteObj.closePythonFile()

print "\n-------------------END OF WRITING TESTCASES TO PYTHON SCRIPT--------------------\n"

print "--------------------------------------------------------------------------------"
print "Test script " + tsuiteObj.get_pyScriptFileName() + " generated !!"
print "Total no. of testcases : " + str(tsuiteObj.Test_Case_Cnt)
print "--------------------------------------------------------------------------------"
