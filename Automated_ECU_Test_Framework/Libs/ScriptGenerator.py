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

#Create tsuite Object
tsuiteObj = Testsuite(testcaseFile,testcaseFileSheet,17,1,2,3,4,5,6,7,8,9,10,18)


tsuiteObj.Excel_Path()
#------------------------------------------------------------------------------------------------
tsuiteObj.fill_Test_data() # Creates dictionary of data and list of those dictionaries is created
#------------------------------------------------------------------------------------------------
tsuiteObj.openPythonFile()          #Function call
tsuiteObj.write_batchfile()         #Function call
tsuiteObj.writeCopyright()          #Function call
tsuiteObj.writePathSettings()       #Function Call
tsuiteObj.writewbinit()             #function to open wb and change ok/nok
tsuiteObj.writeReportSettings()     #function call
tsuiteObj.writeChannelSettings()    #function call
tsuiteObj.writePreconditions()      #function call
tsuiteObj.writeGetActualRespDef()   #function call
tsuiteObj.writeInvokeMsgBoxDef()    #function call
tsuiteObj.writexlrespfunction()


tsuiteObj.fo.write("\n##############################")
tsuiteObj.fo.write("\n## Test Related information ##")
tsuiteObj.fo.write("\n##############################"+ '\n' + '\n')
print "\n"+"Sheet Title : " + tsuiteObj.get_sheettitle()
print "\n"+"Sheet Author : "+tsuiteObj.get_sheetauthor()
print "\n"+"Sheet Project : "+tsuiteObj.get_sheetproject()
print "\n"+"Software Vesrion : "+tsuiteObj.get_sheetsoftwareversion()
print "\n"+"Hardware Version : "+tsuiteObj.get_sheethardwareversion()
print "\n"+"Network : "+tsuiteObj.get_sheetnetwork()
print "\n"+"CAN Channel : "+tsuiteObj.get_sheetCANchannel()
print "\n"+"CAN BAUD Rate : "+tsuiteObj.get_sheetCANchannelBR()
print "\n"+"LIN Channel : "+tsuiteObj.get_sheetLINchannel()
print "\n"+"LIN BAUD RATE : "+tsuiteObj.get_sheetLINchannelBR()
print "\n"+"Flexray Channel : "+tsuiteObj.get_sheetflexraychannel()
print "\n"+"Flexray BAUD rate"+tsuiteObj.get_sheetflexraychannelBR()
print "\n"+"DBC path : "+tsuiteObj.get_dbcpath()


count=0
testcasenumber=0
teststepnumber=0
for testcase in range(0,tsuiteObj.get_totaltests()):
    count+=1
    curr_testcount=count-1
    print "\n*************************************************************\n"
    print "Testcase "+ str(count) + " begins"
    print "\n*************************************************************\n"
    tsuiteObj.writeTestCaseDef(testcasenumber)

    tsuiteObj.writerow_number+=1# This is used to keep track of the row number. It uses the first row / tableHDR as a base (CHeck tsuiteOBJ)

    if(count<=tsuiteObj.get_totaltests):
        for teststep in range(0,int(tsuiteObj.get_numberofteststeps(testcasenumber))):
            tsuiteObj.writerow_number+=1
            if tsuiteObj.get_testcommandtype(testcasenumber,teststepnumber) == 'DIAG':
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

            print "Test_step "+str(teststepnumber+1)+"being written"

            teststepnumber+=1
    else:
        print "Error count exceeds number of test cases"
    teststepnumber=0
    testcasenumber+=1
tsuiteObj.writeEndTestDef()
tsuiteObj.writeCallingOfTestcases()
tsuiteObj.writexlsave()
tsuiteObj.closePythonFile()


print "\nTotal Number of test cases : " + str(tsuiteObj.Test_Case_Cnt)
print "\nTotal Number of test cases scripted : "+str(count)
print "\nTestcase script " + testcaseScriptFile + ".py" + " generated !!"
print "\n\n\n"

