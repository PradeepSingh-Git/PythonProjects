# -*- coding: cp1252 -*-

#============================================================================================================================================================
#
# Integration Test script file
# (c) Copyright 2012 Lear Corporation
#
#============================================================================================================================================================


'''
Comment Starts
File History
'**************************************************************************************************************************'
'   V  1.0.0:                                                                                                                '
'   [3/2/2017][psingh02]:                                                                                                  '
'   Changes done :                                                                                                         '
'   1)Changed the template as per convenience for North America Projects                                                                                   '
'***************************************************************************************************************************'

Comments End
'''

import os
import xlrd
#import xlutils
from os.path import exists
import sys
import win32com.client, win32api, win32con, pythoncom
import py_compile #for .pyc file
#import termcolor

if len(sys.argv) != 4:
    print "\nWrong Input !!"
    print "\nExpected Format is : LatteScriptGenerator.py TestcaseFileName TestcaseSheetName TestcaseDirectoryPath\n"
    sys.exit()

print 'File Name : ', str(sys.argv[1])
print 'FileSheet Name : ', str(sys.argv[2])
print 'Path Name : ', str(sys.argv[3])
testcaseFile = str(sys.argv[1])
testcaseFileSheet = str(sys.argv[2])
testcaseDirectory = sys.argv[3]

if ".xlsm" in testcaseFile:
    testcaseScriptFile = testcaseFile.replace('.xlsm', '')
elif ".xlsx" in testcaseFile:
    testcaseScriptFile = testcaseFile.replace('.xlsx', '')
elif ".XLSX" in testcaseFile:
    testcaseScriptFile = testcaseFile.replace('.XLSX', '')
elif ".XLS" in testcaseFile:
    testcaseScriptFile = testcaseFile.replace('.XLS', '')
elif ".xls" in testcaseFile:
    testcaseScriptFile = testcaseFile.replace('.xls', '')

testcaseScriptFile = testcaseScriptFile + "_" + testcaseFileSheet

py_compile.compile("LatteScriptGenerator.py")



def Excel_Path():
    '''
    Description: This function open Excel sheet in which all test cases are written.
    user shoud store excel sheet in current working directory.
    '''

    global xl_sheet #xlsheet var
    global book

    book_path = testcaseDirectory + "\\" + testcaseFile #path of excelsheet
    book = xlrd.open_workbook(book_path)  #open excelsheet"Test_Details"

    xl_sheet = book.sheet_by_name('tla_library')  #Open sheet

Excel_Path() #Function call


def file_creation():
  '''
  Description:This function will create new Python file i.e .py file.
  '''

  global fo
  global batchfo

  '****************************************************************************'
  'file_creation function code updated to create the IT Test file. '
  '****************************************************************************'

  if testcaseScriptFile != "":
      pytitle = testcaseDirectory + "\\"  + testcaseScriptFile +'.py'
      batchtitle = testcaseDirectory + "\\"  + testcaseScriptFile +'.bat'

  else:
    raw_input('\nUser has not entered valid choice')
    sys.exit()

  fo = open(pytitle,'w') #open file in write mode
  batchfo = open(batchtitle,'w')#open file in write mode

file_creation() #Function call



def write_batchfile():
    '''
    Description: This Function writes to batch file that executes corresponding .py file
    '''
batchfo.write("c:\Python27\python.exe %s" %(testcaseScriptFile +'.py'))
batchfo.close()

write_batchfile() #Function call

def lear_copyPrint():
    '''
    Description: This Function import packages in .py file
    '''
    global div
    div = '======================================='
    fo.write('#' + div * 4)
    fo.write("\n#")
    fo.write("\n# Integration Test script file")
    fo.write("\n# (c) Copyright 2012 Lear Corporation ")
    fo.write("\n#")
    fo.write('\n#' + div * 4 + '\n')

    fo.write("\nimport sys")
    fo.write("\nimport os")
    fo.write("\nimport time")
    fo.write("\nimport Tkinter as tk")
    fo.write("\nimport tkMessageBox")

lear_copyPrint() #Function call


'''
Description:Extracting valus from sheet tla_library
e.g TLA,Component_VERSION,SW_BRANCH etc.
'''

TLA = xl_sheet.cell(2,2).value
Component_VERSION = xl_sheet.cell(4,2).value
TLA_VERSION = xl_sheet.cell(6,2).value
SW_BRANCH = xl_sheet.cell(8,2).value
SVN_REVISION = xl_sheet.cell(10,2).value
HW_VERSION = xl_sheet.cell(12,2).value
AUTHOR =  xl_sheet.cell(14,2).value
TLA_Description = xl_sheet.cell(16,2).value
REPORT_NAME = TLA_Description + "_" + testcaseFileSheet

def Report_Header():
    '''
    Description:This function write all extracted values(from excel sheet) regarding the report header in .py file
    '''
    fo.write("\n\n\n# Report Header Variables")
    fo.write("\nAUTHOR = '%s'" %AUTHOR)
    fo.write("\nTLA = '%s'" % TLA )
    fo.write("\nTLA_VERSION = '%s'" % TLA_VERSION)
    fo.write("\nSVN_REVISION = '%s'" % SVN_REVISION)
    fo.write("\nHW_VERSION = '%s'" %  HW_VERSION)
    fo.write("\nSW_BRANCH = '%s'" %SW_BRANCH)
    fo.write("\nComponent_VERSION = '%s'" % Component_VERSION)
    fo.write("\nTLA_Description = '%s'\n" % TLA_Description)
    fo.write("\nREPORT_NAME = '%s'\n" % REPORT_NAME)
    fo.write('\n#' + div * 4 + '\n')
Report_Header() #function call

def Proj_Path():
    '''
    Description: This function write all project related path to py file.
    Example:
         Tools_PATH,CODE_PATH
    creates object for t32,com
    '''
    fo.write("\nREPORT_API_PATH = os.path.abspath(r'../latte_libs/report_v2_0_0')")
    fo.write("\nCOM_API_PATH = os.path.abspath(r'../latte_libs/com_v1_8_0')\n")

    fo.write("\n\n# Adding paths for loading correctly .py libraries")
    fo.write("\nsys.path.append(REPORT_API_PATH)")
    fo.write("\nsys.path.append(COM_API_PATH)")

    fo.write("\n\nfrom report import *")
    fo.write("\nfrom com import *")

    fo.write("\n\n# Create the report object, specifying the test data")
    fo.write("\nreport = ITReport(TLA, TLA_VERSION, SW_BRANCH, SVN_REVISION, HW_VERSION, AUTHOR,REPORT_NAME)")


Proj_Path()#Function Call

'''
Following code extracts macros and its respected values from tla_library sheet
Example:
OK = 1
NOK =0
these extracted values are written to the file
'''
NumRows=xl_sheet.nrows
def Macro_def():     #defining macros
    fo.write("\n\n\n# Macro Definition\n")
    macro_var = 0
    while(str(xl_sheet.cell(macro_var,1).value) != 'Name'):  #to start to write macros first find "name" column
      macro_var+=1
    macro_var+=1

    while(str(xl_sheet.cell(macro_var,1).value) != 'End of test'):  #scan rows while 'End of test' string row in excel sheet not found
        #raw_input ('enter')
        if(xl_sheet.cell(macro_var,1).value != ''):
            if(xl_sheet.cell(macro_var,2).value != ''):
                 MICRO_NAME =  xl_sheet.cell(macro_var,1).value
                 MICRO_VALUE =  (xl_sheet.cell(macro_var,2).value)
                 if isinstance(MICRO_VALUE,float):
                   MICRO_VALUE = int(MICRO_VALUE)
                 fo.write("%s = %s "  % (MICRO_NAME,MICRO_VALUE)+ '\n')
        macro_var+=1

Macro_def() #Function call

#-----------------------------------------------------------Set LIN and CAN Channels---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

fo.write("\n#Set CAN/LIN  Channel")

com_cntcan=0  #to assign can1,can2...

com_cntlin=0  #to assign lin1,lin2...

can_cnt=0  #count Total number of can channels

lin_cnt=0 ##count Total number of lin channels


can_chlist=[] #created can channel list to represent the activated CAN Chanel's Status


lin_chlist=[]  #created lin channel list to represent the activated LIN Chanel's Status

Active_CANs = 0
Active_Lins = 0
'''
Description: Extracts CAN access request values from sheet
Example:
        CAN1 = YES
        CAN2 = NO
        LIN1 = YES
'''
can1 =xl_sheet.cell(21,2).value
can2 =xl_sheet.cell(22,2).value
can3 =xl_sheet.cell(23,2).value
can4 =xl_sheet.cell(24,2).value

#Extract LIN Information from Excelsheet(tla_library)
lin1 =xl_sheet.cell(25,2).value
lin2 =xl_sheet.cell(26,2).value
lin3 =xl_sheet.cell(27,2).value
lin4 =xl_sheet.cell(28,2).value

cans = [can1,can2,can3,can4]  #stored all CAN's in one var

lins = [lin1,lin2,lin3,lin4]  #stored all LIN's in one var

#-------------------------------------------------Loading DBC's & Fixing BaudRates for all Assigned CAN & LIN Channels-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

'''
Description:This for Loop Extract can channel baud rate,Channel ID,LDf,DBC.
it Checks CAN Access req. and according to that set channel
Example:
       if CAN1 = YES
       set can channel
       can1 = com.open_can_channel(int(0.0),int(500000.0))
       can1.load_dbc(r'C:\BMW_MOTORRAD\BCL\trunk\04_SPECIFICATIONS\Customer\Bus communication\CAN\V080\MR_CAN_2010_V080_BCO_20140319.dbc')
'''

for index in range(len(cans)):
  can_cnt+=1
  if(str(cans[index])=='YES'):
     #can_cnt+=1
    Active_CANs +=1
    #str(cans[index] = str(cans[index]).split('CAN')[1]
    can_chlist.append(1) # store 1 if can present
    if (xl_sheet.cell(21+index,3).value != '') and (xl_sheet.cell(21+index,4).value != '')and (xl_sheet.cell(21+index,5).value != ''): #check all credentials are Provided
      fo.write("\ncom = Com('VECTOR')")
      fo.write("\ncan%s = com.open_can_channel(int(%s),int(%s))"%(can_cnt,xl_sheet.cell(21+index,3).value,xl_sheet.cell(21+index,4).value))
#       fo.write("\ncan%s.load_dbc(r'%s')" %(can_cnt,xl_sheet.cell(21,5).value))
      fo.write("\n# Initialize Diagnostics")
      fo.write("\ncan%s._init_dgn()\n" %(can_cnt))
      fo.write("\ncan%s.load_dbc('%s')\n" %(can_cnt,xl_sheet.cell(21,5).value))
    else:
      print "User Activated the CAN Channel " +str(index+1)+' with missing credentials of Baud Rate & Path DBC'
      if(xl_sheet.cell(21+index,3).value == ''):
          print "Missing Channel ID of CAN" +str(index+1)+ " Channel"
          sys.exit()
      if(xl_sheet.cell(21+index,4).value == ''):
          print "Missing Baud Rate of CAN" +str(index+1) + " Channel"
          sys.exit()
      if(xl_sheet.cell(21+index,5).value == ''):
          print "Missing Path DBC/LDF of CAN" +str(index+1) + " Channel"
          sys.exit()

  else:
    can_chlist.append(0)#  store 0 if its not exist
print "\nTotal Active CAN Channels:" +str(Active_CANs) +"\n"


'''
Description:This for Loop Extract lin channel baud rate,Channel ID,its LDf,DBC.
it Checks lin Access req. and according to that set channel
Example:
       if LIN1 = YES
       set lin channel
       lin1 = com.open_lin_channel(int(1.0),r'C:\BMW_MOTORRAD\BCL\trunk\04_SPECIFICATIONS\Customer\Bus communication\LIN\MR_LED_LIN_2010_V050_20140319.ldf')
'''

for index in range(len(lins)):
##  print 'Current lin :', lins[index]
  lin_cnt+=1
  if(str(lins[index])=='YES'):
    #lin_cnt+=1
    Active_Lins +=1
    lin_chlist.append(1) # store 1 if can present
    if (xl_sheet.cell(25+index,3).value != '') and (xl_sheet.cell(25+index,5).value != ''):  #check all credentials are Provided
      fo.write("\nlin%s = com.open_lin_channel(int(%s),r'%s')\n"%(lin_cnt,xl_sheet.cell(25+index,3).value,xl_sheet.cell(25+index,5).value))
    else:
       print "User Activated the LIN Channel"+str(index+1)+' with invalid credentials of Baud Rate & Path DBC'
       if(xl_sheet.cell(25+index,3).value == ''):
          print "Missing Channel ID of LIN" +str(index+1)+ " Channel"
          sys.exit()
       if(xl_sheet.cell(25+index,5).value == ''):
          print "Missing Path DBC/LDF of LIN" +str(index+1) + " Channel"
          sys.exit()
  else:
    lin_chlist.append(0) # store 0 if its not exist
print "\nTotal Active Lin Channels:" +str(Active_Lins) +"\n"


fo.write("\n#################################################################\n")
fo.write("## Send Periodic Tester Present while doing diagnostics  ##\n")
fo.write("#################################################################\n")
fo.write("can1.dgn.ecu_reset(0x01)\n" )
fo.write("can1.dgn.start_periodic_tp()\n" )
fo.write("time.sleep(3)\n" )



#-------------------------------------------Log File Initializations-----------------------------------------
fo.write("\n# Name of the logfile where the frames will be logged\n")
fo.write("\ncan_log_file = REPORT_NAME +'_dgn_logfile.txt'\n")
fo.write("\nLog_AllFrames = []\n")


#-------------------------------------------Generate GetActualResponseFrames() Function-----------------------------------------
fo.write("\ndef GetActualResponseFrames():\n")

fo.write("    response_str = ''\n")
fo.write("    readByte = ''\n")
fo.write("    for frame_index in range(len(can1.dgn.iso.net._resp_frames)):\n")
fo.write("          if len(can1.dgn.iso.net._resp_frames) > 1 :\n")
fo.write("              if (frame_index == 0):\n")
fo.write("                  frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][2:8]\n")
fo.write("              else:\n")
fo.write("                  frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][1:8]\n")
fo.write("          else:\n")
fo.write("              frameNewList = can1.dgn.iso.net._resp_frames[frame_index][3][1:8]\n")
fo.write("          for frame_element in range(len(frameNewList)):\n")
fo.write("              readByte = str(hex(frameNewList[frame_element]))\n")
fo.write("              readByte = readByte.replace('0x','')\n")
fo.write("              if len(readByte) == 1:\n")
fo.write("                  readByte = '0' + readByte\n")
fo.write("              response_str +=readByte\n")

fo.write("    response_str = response_str.replace('0x','')\n")
fo.write("    response_str = response_str.upper()\n")
fo.write("    return response_str\n\n\n")

#---------------------------------------Compare Results-----------------------------------------------------------------
fo.write("\ndef CompareResults(ExpectedRes,ActualRes):\n")
fo.write("    returnVal = True\n")
fo.write("    temp_List = []\n")
fo.write("    for i in range(0,len(ExpectedRes),2):\n")
fo.write("          byteStr = ''\n")
fo.write("          byteStr = byteStr + ExpectedRes[i]\n")
fo.write("          byteStr = byteStr + ExpectedRes[i+1]\n")
fo.write("          byteHex_str = '0x'+ byteStr\n")
fo.write("          temp_List.append(byteHex_str)\n")
fo.write("    for j in range(0,len(temp_List)):\n")
fo.write("          if(ActualRes[j] == int(temp_List[j],16)):\n")
fo.write("                  continue\n")
fo.write("          else:\n")
fo.write("                  returnVal = False\n")

fo.write("    return returnVal\n\n\n")

#-------------------------------------------Generate InvokeMessageBox() Function-----------------------------------------
fo.write("\ndef InvokeMessageBox(MessageStr):\n")
fo.write("    MessageStr = MessageStr")
fo.write(r" + ")
fo.write(r""" "\nPress OK after performing the action." """)
fo.write("\n")
fo.write("    root = tk.Tk()\n")
fo.write("    root.withdraw()\n")
fo.write("""    root.attributes("-topmost", True)\n""")
fo.write("""    tkMessageBox.showinfo("Manual Input Required", MessageStr)\n""")
fo.write("    root.destroy()\n")

'''
Test Case Definition
'''


#fo.write('\n#' + div * 4 + '\n')
#-------------------------------------------excel columns function-----------------------------------------
def Excel_columns():
    '''
    Description: This function assigns names to excel sheet columns.
    '''

    global Doors_Req
    global Test_Type
    global IO_Type
    global Type
    global dgn_session
    global repeatibility
    global Test_Name
    global Test_Desc
    global Test_CondName
    global Test_CondValue
    global Cyclic_time
    global Resolution
    global Print_Signals
    global Comments
    global Test_Case_Cnt
    global Test_Step_Cnt
    Doors_Req = 0
    Test_Type = 1
    IO_Type = 2
    Type = 3
    Test_Name = 4
    Test_Desc = 5
    Test_CondName = 6
    Test_CondValue = 7
    Comments = 8
    dgn_session = 9
    repeatibility = 10
    Cyclic_time = 11
    Resolution = 12
    Print_Signals = 13


    Test_Case_Cnt = 0
    Test_Step_Cnt = 0
Excel_columns() #Function Call


'''Open IntegrationTest sheet'''

xl_sheet = book.sheet_by_name(testcaseFileSheet)  # IntegrationTest sheet open
numRows=xl_sheet.nrows
'''
 Initialise Test_index to 1 to start the test case's
 Starts with the second Row (Next to the Defination Row )of Sheet
 cell_type used to check the validity of current test case or test step
'''

Test_index=1
curr_row=1
#cell_type = xl_sheet.cell_type(curr_row, Test_Type)
'''
Description: Find 'DOOR_ID' name row and start row scaning from that row
'''
DOORS_ID = 0
while(str(xl_sheet.cell(DOORS_ID,0).value)!='Requirement ID'):
  DOORS_ID+=1

DOORS_ID = curr_row
cell_typ = xl_sheet.cell(curr_row, Test_Type).value
#print cell_typ
#-----------------------------------------Test Header function-----------------------------------------------------------------------------------------------------------------------

def Test_Header(ETest_Case_Cnt,Etest_name,Etest_case_desc,Etest_case_reqs):
        '''
        Description:This function starts to write new test case in .py file
        it writes test description ,test case requirment id to py file.
        '''

        fo.write("\n#######################")
        fo.write("\n## Test Case %s       ##" %ETest_Case_Cnt)
        fo.write("\n#######################"+ '\n' + '\n')
        file_string='def test_'+ str(ETest_Case_Cnt)+ '():\n    test_case_name = '
        fo.write(file_string)

        '''
        if user use '' to highlight some part script converts '' to "" to avoid error
        '''
        TD = Etest_name.replace('\'','\"')  #in Test Name Statement replace ' with " for indentation

        TD = TD.replace('\n',' ')   #in Test Name Statement replace \n with ' ' for indentation

        fo.write("'\\n\\nTest Case %s: %s'\n    "  %  (ETest_Case_Cnt,TD)) #Write Test Name

        TN = Etest_case_desc.replace('\n',' ')  #in Test Description Statement replace \n with ' ' for indentation
        TN = TN.replace('\'','\"')  #in Test Description Statement replace ' with " for indentation

        fo.write("test_case_desc = '%s'\n    " %TN) #Write Test Description

        fo.write("test_case_reqs = '%s'\n    " % Etest_case_reqs.replace('\n',' ') ) #Write Test Requirment ID
        file_string="report.add_test_case(test_case_name, test_case_desc, test_case_reqs)\n" #Write Report
        fo.write(file_string)
        fo.write("    test_Conclusion = 'Test Not started'\n")
        fo.write("    can1.dgn.iso.net._all_frames = []\n")
        fo.write("    can1.dgn.iso.net._resp_frames = []\n")
        fo.write("    can1.stop_tx_frames()\n")
        fo.write(r"    response_str = '\n'")
        fo.write("\n    print test_case_name\n \n \n    ")



#------------------------------------Parsing of excel sheet row start-------------------------------------------------------------------------------------------------------------------------------------

while (str(xl_sheet.cell(curr_row,Doors_Req).value)!='END Line. Do Not Remove'): #Loop starts to access the test case/steps untill the END of  Line

    cell_type = xl_sheet.cell_type(curr_row, Test_Type)

    if(xl_sheet.cell(curr_row,Doors_Req).value != ''):   # Check For Proper Data Entry in Excel sheet
        if(xl_sheet.cell(curr_row,Test_Type).value != 'TH'):
                 raw_input("\n**Error occured,to check error press Enter\n")
                 print("\nwrong data entered column 1 \n")
                 print "check row no: " +str(curr_row) + "\n"
                 print "check Column no:" +str(Test_Type) + "\n"
                 sys.exit()

    if(xl_sheet.cell(curr_row,Test_Type).value != 'TH'):   # Check For Proper Data Entry in Excel sheet
        if(xl_sheet.cell(curr_row,Test_Type).value == ''):
            if(xl_sheet.cell(curr_row,IO_Type).value != ''):
                 raw_input("\n**Error occured,to check error press Enter\n")
                 print("\nSelect TH or TS \n")
                 print "check row no: " +str(curr_row) + "\n"
                 print "check Column no:" +str(IO_Type) + "\n"

    if xl_sheet.cell(curr_row,Test_Type).value == 'TH':  #New Test Case

        Test_Case_Cnt+=1 # Increment the Test Case Count
        Test_Step_Cnt=0  # Reinitialise the Test Step Count

        print("\n*************Writing test case ")+str(Test_Case_Cnt) +("*************")

        test_name = xl_sheet.cell(curr_row,Test_Name).value   #Test Name
        test_case_desc = xl_sheet.cell(curr_row,Test_Desc).value #test Description
        test_case_reqs = xl_sheet.cell(curr_row,Doors_Req).value #Test Case Request

        Test_Header(Test_Case_Cnt,test_name,test_case_desc,test_case_reqs) #function call
        #print("\nTest Step count: ") +str(Test_Step_Cnt)




#--------------------------------------Start of TS---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    elif xl_sheet.cell(curr_row,Test_Type).value == 'TS': #New Test Step


        Test_Step_Cnt+=1 #Increment Test Step Count

        if xl_sheet.cell(curr_row,Comments).value != '':
            Comments_string = 'Note: ' + str(xl_sheet.cell(curr_row,Comments).value)
        else:
            Comments_string = ''

        if(xl_sheet.cell(curr_row,Test_Name).value != ''):  # Check For Proper Data Entry in Excel sheet
            raw_input("\n**Error occured,to check error press Enter\n")
            print("\nany data entery is not allwed in column no 4(Test Name)until new test case arrive\n")
            print "check row no: " +str(curr_row) + "\n"
            print "check Column no:" +str(Test_Name) + "\n"
            sys.exit()
        if(xl_sheet.cell(curr_row,Doors_Req).value != ''): # Check For Proper Data Entry in Excel sheet
            raw_input("\n**Error occured,to check error press Enter\n")
            print("\nany data entry is not allowed in column no 0(Requirement ID)until new test case arrive\n")
            print "check row no: " +str(curr_row) + "\n"
            print "check Column no: " +str(Doors_Req) + "\n"
            sys.exit()

        # Check for Input activation
        if xl_sheet.cell(curr_row,IO_Type).value == 'I' :  #Check for I/O


#-------------------------------------- Start of Diagnostics--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

              if xl_sheet.cell(curr_row,Type).value == 'DIAG':

                  #Extract values from excel sheet
                  test_step_desc = xl_sheet.cell(curr_row,Test_Desc).value #Description
                  comments = xl_sheet.cell(curr_row,Comments).value #Comments
                  Expec_res_raw=str(xl_sheet.cell(curr_row,Test_CondValue).value) #Expected value of Test Step
                  Expec_res_raw=Expec_res_raw.split('.')[0]

                  Expec_res = Expec_res_raw
                  Expec_res=Expec_res.replace('\n',' ')
                  Expec_res=Expec_res.replace(' ','')
                  Expec_res=Expec_res.upper()

                  Diag_Service=str(xl_sheet.cell(curr_row,Test_CondName).value)
                  Diag_Service=Diag_Service.split('.')[0]
                  Diag_Service = Diag_Service.replace(" ", "")


                  if Diag_Service[0:2]=='11': # Check for diagnostic service ID is "RESET"

                        PID=Diag_Service[2:4] #Extract Reset Type
                        
                        print_row = int(curr_row)+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  # Reset By Diagnostics
                        fo.write("    ## Reset By Diagnostics  ##\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if(len(Diag_Service) <= 4):
                            if(PID == ''):
                                fo.write("    can%s.dgn.iso.net.send_request([0x11, ], 'PHYSICAL')\n" % (int(1)))  
                            else:
                                fo.write("    can%s.dgn.ecu_reset(%s)\n" % (int(1),'0x'+PID))
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x11" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")
                        
                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Reset Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Unable to reset.Test Fails:!!'\n")
                        fo.write("\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile

                  elif Diag_Service[0:2]=='31': # Check for diagnostic service ID is "ROUTINE ID"

                        PID = Diag_Service[2:4]          #Extract PID Number

                        print_row = int(str(curr_row))+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #Read DID By Diagnostics
                        fo.write("    ##          ROUTINES          ##\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")


                        if(PID == ''):
                            fo.write("    can%s.dgn.iso.net.send_request([0x31, ], 'PHYSICAL')\n" % (int(1)))  

                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x31" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")

                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Routine Execution Succesful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Routine Execution Fails:!!'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile

                  elif Diag_Service[0:2]=='22': # Check for diagnostic service ID is "READ DID"

                        PID='0x'+Diag_Service[2:6] #Extract PID Number
                        if len(Diag_Service) > 6:
                            Extra_Parameter = '0x'+Diag_Service[6:8]


                        if (Expec_res.find("[MIN]:")>=0) or (Expec_res.find("[MAX]:")>=0):
                            Expec_res_length = len(Expec_res)/2
                            MIN_Expec_response = Expec_res[6:Expec_res_length]
                            MAX_Expec_response = Expec_res[Expec_res_length+6:len(Expec_res)]

                            strtindex = MIN_Expec_response.find("(",0,Expec_res_length)
                            endindex = MIN_Expec_response.find(")",0,Expec_res_length)

                            MIN_Expec_value = '0x'+ MIN_Expec_response[strtindex+1:endindex]
                            MAX_Expec_value = '0x'+ MAX_Expec_response[strtindex+1:endindex]

                        else:
                            strtindex = 0
                            endindex = 0
                            Expec_res_length = 0



                        print_row = int(str(curr_row))+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #Read DID By Diagnostics
                        fo.write("    ##          Read DID          ##\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if len(Diag_Service) > 6:
                            fo.write("    can%s.dgn.read_DID_Len_W(%s,%s) \n" % (int(1),PID,Extra_Parameter))
                        else:
                            fo.write("    can%s.dgn.read_did(%s) \n" % (int(1),PID))
                        fo.write("    time.sleep(0.3)\n" )
                        fo.write("\n")

                        if (Expec_res.find("[MIN]:")>=0) or (Expec_res.find("[MAX]:")>=0):
                            fo.write("    Expec_res = '%s'\n"%Expec_res)
                            fo.write("    Expec_min_res = '%s'\n" %MIN_Expec_response)
                            fo.write("    Expec_max_res = '%s'\n" %MAX_Expec_response)
                            fo.write("    Actual_res = GetActualResponseFrames()\n")
                            fo.write("    Actual_rangevalue = '0x' + Actual_res[%s:%s]\n" %(strtindex,(endindex-1)))
                            fo.write("    Actual_rangevalue = int(Actual_rangevalue,16)\n")
                            fo.write("    Expec_min_value = %s\n" %MIN_Expec_value)
                            fo.write("    Expec_max_value = %s\n" %MAX_Expec_value)
                            fo.write("\n")
                            fo.write("    if Expec_res[6:%s] == Actual_res[0:%s]: \n" % ((strtindex+6),strtindex))
                            fo.write("        if Expec_res[%s:%s] == Actual_res[%s:%s]: \n" % ((endindex+6+1),Expec_res_length,(endindex-1),(Expec_res_length-6-2)))
                            fo.write("            if (Actual_rangevalue >= Expec_min_value) and (Actual_rangevalue <= Expec_max_value): \n" )
                            fo.write("                result = True\n")
                            fo.write("                comment ='Test Successful.'\n")
                            fo.write("            else: \n" )
                            fo.write("                 result = False\n")
                            fo.write("                 comment ='Test Fails!!'\n")
                            fo.write("        else: \n" )
                            fo.write("            result = False\n")
                            fo.write("            comment ='Test Fails!!'\n")
                            fo.write("    else: \n" )
                            fo.write("        result = False\n")
                            fo.write("        comment ='Test Fails!!'\n")
                        else:
                            fo.write("    Expec_res = '%s'\n"%Expec_res)
                            fo.write("    Actual_res = GetActualResponseFrames()\n")
                            fo.write("\n")
                            fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                            fo.write("          result = True\n")
                            fo.write("          comment ='Test Successful.'\n")
                            fo.write("    else: \n" )
                            fo.write("          result = False\n")
                            fo.write("          comment ='Test Fails!!'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile

                  elif Diag_Service[0:2]=='10': # Check for diagnostic service ID is "Session CTRL DID"


                        PID=Diag_Service[2:4] #Extract Session Number
                        print_row = int(str(curr_row))+1
                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
                        fo.write("    ##          Session Ctrl  #\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if(len(Diag_Service) <= 4):
                            if PID =='01':
                                fo.write("    can%s.dgn.default_session() \n" % (int(1))) #evaluation of default session
                            elif PID =='02':
                                fo.write("    can%s.dgn.programming_session() \n" % (int(1))) #evaluation of programming session
                            elif PID =='03':
                                fo.write("    can%s.dgn.extended_session() \n" % (int(1))) #evaluation of extended session
                            elif PID =='':
                                fo.write("    can%s.dgn.iso.net.send_request([0x10, ], 'PHYSICAL') \n" % (int(1))) #evaluation of No session subfunction
                            else :
                                fo.write("    can%s.dgn.iso.service_0x10(%s)\n" % (int(1),'0x'+PID)) #evaluation of internal session
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x10" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")
                            

                        fo.write("    time.sleep(0.3)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Test Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Test Failed!!'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile

                  elif Diag_Service[0:2]=='27': # Check for diagnostic service ID is "Security Access ID"

                        PID=Diag_Service[2:4] #Extract Session Number
                        print_row = int(str(curr_row))+1
                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #Security Access By Diagnostics
                        fo.write("    ##          Security Access  #\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if ("Send" in TD) and ("Wrong" in TD) and ("Key" in TD):
                            fo.write("    can%s.dgn.security_access_wrong_key(%s)\n" % (int(1),'0x'+PID))
                        else:
                            fo.write("    can%s.dgn.security_access(%s)\n" % (int(1),'0x'+PID))

                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Test Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Test Failed!!'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile


                  elif Diag_Service[0:2]=='19': # Check for diagnostic service ID is "READ DTC Information"

                        PID=Diag_Service[2:4] #Extract PID Number

                        print_row = int(curr_row)+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #READ DTC Information
                        fo.write("    ##    READ DTC Information    ##\n")
                        fo.write("    ################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")
                        
                        if(PID == ''):
                            fo.write("    can%s.dgn.iso.net.send_request([0x19, ], 'PHYSICAL')\n" % (int(1)))
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x19" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")
                        
                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Read DTC Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Read DTC Failed!!'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile


                  elif Diag_Service[0:2]=='2E': # Check for diagnostic service ID is "write DID"

                        print_row = int(str(curr_row))+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ################################\n")  #Hard Reset By Diagnostics
                        fo.write("    ##          Write DID          #\n")
                        fo.write("    ################################\n")

                  elif Diag_Service[0:2]=='85': # Check for diagnostic service ID is "Control DTC Setting"

                        PID = Diag_Service[2:4] #Extract Subfunction
                        
                        print_row = int(curr_row)+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ###################################\n")  #Clear Diagnosice Information
                        fo.write("    ##       Control DTC Setting      ##\n")
                        fo.write("    ###################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if(len(Diag_Service) <= 4):
                            if(PID == ''):
                                fo.write("    can%s.dgn.iso.net.send_request([0x85, ], 'PHYSICAL')\n" % (int(1)))  
                            else:
                                fo.write("    can%s.dgn.control_dtc_setting_custom(%s)\n" % (int(1),'0x'+PID))
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x85" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")
                            

                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Test Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Test Failed.'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile  

                  elif Diag_Service[0:2]=='14': # Check for diagnostic service ID is "Clear Diagnosice Information"

                        PID = Diag_Service[2:4] #Extract Subfunction
                      
                        print_row = int(curr_row)+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ###################################\n")  #Clear Diagnosice Information
                        fo.write("    ## Clear Diagnostics Information  ##\n")
                        fo.write("    ###################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")

                        if(PID == ''):
                            fo.write("    can%s.dgn.iso.net.send_request([0x14, ], 'PHYSICAL')\n" % (int(1)))
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x14" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")
                            

                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Test Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Test Failed.'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile                        

                  elif Diag_Service[0:2]=='3E': # Check for diagnostic service ID is "Tester Present"

                        PID=Diag_Service[2:4] #Extract PID Number

                        print_row = int(curr_row)+1

                        fo.write("\n    #######################################")  #Print row number of excel sheet
                        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                        fo.write("\n    ##################################### #\n")

                        fo.write("\n    ###################################\n")  #Tester Present
                        fo.write("    ##         Tester Present         ##\n")
                        fo.write("    ###################################\n")

                        TD = test_step_desc.replace('\n',' ')
                        TD = TD.replace('\'','\"')

                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can1.dgn.iso.net._all_frames = []\n" )
                        fo.write("    test_Result = False\n" )
                        fo.write(r"    comment = '\n'" )
                        fo.write("\n")
                        fo.write(r"    response_str = '\n'" )
                        fo.write("\n")
                        fo.write("\n")


                        if(len(Diag_Service) <= 4):
                            if(PID == '00'):
                                fo.write("    can%s.dgn.tester_present()\n" % (int(1)))    
                            elif(PID == '80'):
                                fo.write("    can%s.dgn.tester_present_spr()\n" % (int(1)))
                            elif(PID == ''):
                                fo.write("    can%s.dgn.iso.net.send_request([0x3E, ], 'PHYSICAL')\n" % (int(1)))  
                            else:
                                fo.write("    can%s.dgn.tester_present_custom(%s)\n" % (int(1),'0x'+PID))
                        else:
                            fo.write("    can%s.dgn.iso.net.send_request([0x3E" % (int(1)))
                            
                            for i in range(2,len(Diag_Service),2):
                                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                            fo.write("], 'PHYSICAL') \n")


                        fo.write("    time.sleep(1)\n" )
                        fo.write("\n")
                        fo.write("    Expec_res = '%s'\n"%Expec_res)
                        fo.write("    Actual_res = GetActualResponseFrames()\n")
                        fo.write("\n")
                        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                        fo.write("          result = True\n")
                        fo.write("          comment ='Test Successful.'\n")
                        fo.write("    else: \n" )
                        fo.write("          result = False\n")
                        fo.write("          comment ='Test Failed.'\n")
                        fo.write("    for j in range(len(can1.dgn.iso.net._all_frames)): \n" )
                        fo.write("          response_str =  response_str + can1.dgn.iso.net._format_frame(can1.dgn.iso.net._all_frames[j])\n")
                        fo.write(r"          response_str =  response_str + '\n'")
                        fo.write("\n")
                        fo.write(r"    report.add_test_step(test_step_desc,result,'CAN Frame :'+ response_str,'%s',comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
                        fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile


#----------------------------------------------------------Invoke Pop-up Message----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

              elif xl_sheet.cell(curr_row,Type).value == 'MSG_POPUP': # Check for diagnostic service ID is "Session CTRL DID"

                    print_row = int(str(curr_row))+1
                    fo.write("\n    #######################################")  #Print row number of excel sheet
                    fo.write("\n    #Code block generated for row no = %s  #"%print_row)
                    fo.write("\n    ##################################### #\n")
                    
                    test_step_desc = xl_sheet.cell(curr_row,Test_Desc).value #Description

                    TD = test_step_desc.replace('\n',' ')
                    TD = TD.replace('\'','\"')
                    
                    if(test_step_desc == ''): # Check For Proper Data Entry in Excel sheet
                        print("\n**Error occured.")
                        print("\nTest Description is not provided.")
                        print("\nCheck Row no:")+str(curr_row+1)+"\n"
                        print("\nCheck column number:")+str(Test_Desc)+"\n"
                        sys.exit()
                    elif('Make Tester Present OFF' in TD):
                        fo.write("\n    ###################################\n")  #Tester Present
                        fo.write("    ##         Tester Present         ##\n")
                        fo.write("    ###################################\n")
                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can%s.dgn.stop_periodic_tp()\n" % (int(1)))
                    elif('Make Tester Present ON' in TD):
                        fo.write("\n    ###################################\n")  #Tester Present
                        fo.write("    ##         Tester Present         ##\n")
                        fo.write("    ###################################\n")
                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    can%s.dgn.start_periodic_tp()\n" % (int(1)))
                    else:
                        fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
                        fo.write("    ##          Message Pop-up  #\n")
                        fo.write("    ################################\n")
                        
                        fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                        fo.write("    InvokeMessageBox(test_step_desc)\n" )




                    fo.write(r"    report.add_test_step(test_step_desc,True,'','')") #Report
                    fo.write("\n")
                    fo.write("\n")


#----------------------------------------------------------Check for Wait----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

              elif xl_sheet.cell(curr_row,Type).value == 'DELAY_SEC':  #Test Step --> WAIT
                  description = xl_sheet.cell(curr_row,Test_Desc).value #Description
                  time = xl_sheet.cell(curr_row,Test_CondName).value #Time
                  conditn_Val = xl_sheet.cell(curr_row,Test_CondValue).value #Cyclic Time

                  if(conditn_Val != ''): # Check For Proper Data Entry in Excel sheet
                       print("\n**Error occured.\n")
                       print("\nDont enter any value in this column: Evaluation Criteria (Expected Result)")
                       print "check row no: " +str(curr_row+1) + "\n"
                       print "check Column no: " +str(Cyclic_time) + "\n"
                       sys.exit()

                  if(description == ''): # Check For Proper Data Entry in Excel sheet
                      print("\n**Error occured.\n")
                      print("\nTest Description is not provided.")
                      print("\nCheck Row no:")+str(curr_row+1)+"\n"
                      print("\nCheck column number:")+str(Test_Desc)+"\n"
                      sys.exit()

                  if(time == ''): #Time should not be blank
                      print("\n**Error occured.\n")
                      print ("Provide time(in sec) for delay\n")
                      print "check row no: " +str(curr_row+1)+"\n"
                      print "check column no:" +str(Test_CondValue)+"\n"
                      sys.exit()

                  print_row = int(str(curr_row))+1
                  fo.write("\n    #######################################")  #Print Row number
                  fo.write("\n    #Code block generated for row no = %s #"%print_row)
                  fo.write("\n    #######################################\n")

                  TD = description.replace('\n',' ') #Remove if new line is added in test description
                  TD = TD.replace('\'','\"')
                  fo.write("\n    test_step_desc='%s'\n" %TD)
                  fo.write("    print test_step_desc\n")
                  fo.write("    time.sleep(%s)"%time)
                  fo.write("\n")
                  fo.write(r"    report.add_test_step(test_step_desc,True,'','')") #Report
                  fo.write("\n")
                  fo.write("\n")

              else:
                  print "none of TH or TS selected"

        elif xl_sheet.cell(curr_row,IO_Type).value == 'O' : #Check I/O type

              if xl_sheet.cell(curr_row,Type).value == 'CAN_SIGNAL':

                  #Extract values from excel sheet
                  test_step_desc = xl_sheet.cell(curr_row,Test_Desc).value #Description
                  comments = xl_sheet.cell(curr_row,Comments).value #Comments


                  Can_Signal_Details=str(xl_sheet.cell(curr_row,Test_CondName).value)
                  #Can_Signal_Details=Can_Signal_Details.split('.')[0]
                  Can_Signal_Details=Can_Signal_Details.replace('\n',' ')

                  Test_Condition = Can_Signal_Details
                  Can_Signal_Details=Can_Signal_Details.replace(' ','')


                  Can_Signal_Value_Str = Can_Signal_Details.split('=')[1]
                  Can_Signal_Details = Can_Signal_Details.split('=')[0]
                  Can_Message=Can_Signal_Details.split('.')[0]
                  Can_Signal=Can_Signal_Details.split('.')[1]

                  Can_Signal_Value_List = []

                  for listIndex in xrange(0,len(Can_Signal_Value_Str),2):
                      byteStr = ''
                      for i in range(2):
                          byteStr = byteStr + Can_Signal_Value_Str[listIndex + i]

                      byteHex_str = '0x'+ byteStr
                      Can_Signal_Value_List.append(byteHex_str)

                  Expec_res = str(Can_Signal_Value_Str.upper())
				  				  
                  if Expec_res[0] == '0' and Expec_res[1] != '0' and len(Can_Signal_Value_Str)>1:
                      Expec_res = Expec_res[1:]
                  elif Expec_res == '00' or Expec_res == '000' or Expec_res == '0000':
                      Expec_res = '0'
				  
					  
                  if Can_Message != '' and Can_Signal != '' and Can_Signal_Value_Str != '':
                      fo.write("\n    ################################\n")
                      fo.write("    ##          Send CAN signal  #\n")
                      fo.write("    ################################\n")

                      TD = test_step_desc.replace('\n',' ')
                      TD = TD.replace('\'','\"')

                      fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                      fo.write("    test_Result = False\n" )
                      fo.write(r"    comment = '\n'" )
                      fo.write("\n")
                      fo.write(r"    response_str = '\n'" )
                      fo.write("\n")
                      fo.write("\n")
                      fo.write("    can%s.send_cyclic_frame('%s',10) \n" %(int(1),Can_Message))
                      #fo.write("    can%s.set_signal('%s',%s) \n" %(int(1),Can_Signal,Can_Signal_Value))

                      fo.write("    can%s.set_signal('%s',[" %(int(1),Can_Signal))
                      for i in range(len(Can_Signal_Value_List)):
                          if i == (len(Can_Signal_Value_List)-1):
                              fo.write("%s" %Can_Signal_Value_List[i])
                          else:
                              fo.write("%s," %Can_Signal_Value_List[i])

                      fo.write("]) \n")
                      fo.write("    time.sleep(0.5)\n" )

                      fo.write("\n")
                      fo.write("    Expec_res = '%s'\n"%Expec_res)
                      fo.write("    Actual_res = can%s.get_signal('%s','%s')\n"%(int(1),Can_Signal,Can_Message))
                      fo.write("    Actual_res = str(hex(Actual_res))\n")
                      fo.write("    Actual_res = Actual_res.replace('0x','')\n")
                      fo.write("    Actual_res = Actual_res.replace('L','')\n")
                      fo.write("    Actual_res = Actual_res.replace(' ','')\n")
                      fo.write("    Actual_res = Actual_res.upper()\n")
                      fo.write("\n")

                      fo.write("    if Expec_res == Actual_res: \n" )
                      fo.write("          result = True\n")
                      fo.write("          comment ='CAN signal set Successfully.'\n")
                      fo.write("    else: \n" )
                      fo.write("          result = False\n")
                      fo.write("          comment ='CAN signal could not be set.'\n")
                      fo.write("    response_str = str(can%s.get_frame(can%s.dbc.find_frame_id('%s')))\n"%(int(1),int(1),Can_Message))
                      fo.write(r"    report.add_test_step(test_step_desc,result,'%s.%s='+Actual_res,'%s',comment + '\n' + '%s')"%(Can_Message,Can_Signal,Test_Condition,Comments_string)) #Report
                      #fo.write(r"    report.add_test_step(test_step_desc,result,'%s' + comment + '\n' + '%s')"%(Test_Condition,Comments_string)) #Report
                      fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile
                  else:
                      print "Test Condition entered is incorrect !!"

              elif xl_sheet.cell(curr_row,Type).value == 'CAN_FRAME':

                  #Extract values from excel sheet
                  test_step_desc = xl_sheet.cell(curr_row,Test_Desc).value #Description
                  comments = xl_sheet.cell(curr_row,Comments).value #Comments
                  Expec_res=str(xl_sheet.cell(curr_row,Test_CondValue).value) #Expected value of Test Step

                  Expec_res=Expec_res.split('.')[0]
                  Expec_res=Expec_res.replace('\n',' ')
                  Expec_res=Expec_res.replace(' ','')
                  Expec_res=Expec_res.upper()

                  Can_Frame_Details=str(xl_sheet.cell(curr_row,Test_CondName).value)
                  Can_Frame_Details=Can_Frame_Details.replace('\n',' ')

                  Test_Condition = Can_Frame_Details
                  Can_Frame_Details=Can_Frame_Details.replace(' ','')

                  Can_Frame_Value_Str = Can_Frame_Details.split('=')[1]
                  Can_Frame_Details = Can_Frame_Details.split('=')[0]
                  Can_Frame_Details=Can_Frame_Details.split(']')[0]
                  Can_FrameID=Can_Frame_Details.split('[')[1]


                  Can_Frame_Value_List = []

                  for listIndex in xrange(0,len(Can_Frame_Value_Str),2):
                      byteStr = ''
                      for i in range(2):
                          byteStr = byteStr + Can_Frame_Value_Str[listIndex + i]

                      byteHex_str = '0x'+ byteStr
                      Can_Frame_Value_List.append(byteHex_str)


                  if Can_FrameID != '' and Can_Frame_Value_Str != '':
                      fo.write("\n    ################################\n")
                      fo.write("    ##          Send CAN Frame  #\n")
                      fo.write("    ################################\n")

                      TD = test_step_desc.replace('\n',' ')
                      TD = TD.replace('\'','\"')

                      fo.write("\n    test_step_desc='%s'\n" %TD)  #Test step Description
                      fo.write("    test_Result = False\n" )
                      fo.write(r"    comment = '\n'" )
                      fo.write("\n")
                      fo.write(r"    response_str = '\n'" )
                      fo.write("\n")
                      fo.write("\n")
                      fo.write("    can%s.write_frame(%s, %s, [" %(int(1),Can_FrameID,len(Can_Frame_Value_List)))
                      for i in range(len(Can_Frame_Value_List)):
                          if i == (len(Can_Frame_Value_List)-1):
                              fo.write("%s" %Can_Frame_Value_List[i])
                          else:
                              fo.write("%s," %Can_Frame_Value_List[i])

                      fo.write("]) \n")

                      fo.write("    time.sleep(0.5)\n" )
                      fo.write(r"    report.add_test_step(test_step_desc,result,'%s' + comment + '\n' + '%s')"%(Test_Condition,Comments_string)) #Report
                      fo.write("\n    Log_AllFrames.append(response_str)\n\n") #Logfile
                  else:
                      print "Test Condition entered is incorrect !!"


        else: #Check whether I/O type of test step is provided or not
            raw_input("Error occured ,to check error press enter")
            print("I/O type is not selected for test step")
            print "check row no: " +str(curr_row+1)+"\n"
            print "check column no:" +str(IO_Type)+"\n"



    curr_row+=1 #Increment row count
curr_row-=1


fo.write("\n\ndef endTest():")
fo.write("\n    report.generate_report(REPORT_API_PATH)")
fo.write("\n    sys.exit()\n\n\n\n")


#---------------------------------------------------------------Execution of Test Cases--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


# Execute the test cases
fo.write("\n#############################")
fo.write("\n## Execute the test cases  ##")
fo.write("\n#############################"+ '\n' + '\n')

print "\n"
print "Total Number of Test Cases: "+ str(Test_Case_Cnt)
print "Testcase script " + testcaseScriptFile + ".py" + " generated !!"
print "\n\n\n"

#### Start Calling all Test Cases #####

Cnt=1
while Cnt<=Test_Case_Cnt:
  fo.write("test_%s()\n" %Cnt)
  Cnt+=1
  fo.write("time.sleep(1)\n")


#--------------------------------------------------------------------Save Log Files------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

fo.write("\n# Save CAN Log Files")
fo.write("\ncan1.dgn.save_logfile_custom(Log_AllFrames,can_log_file)")

#--------------------------------------------------------------------Generate the final report------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

fo.write("\n# Generate the final report")
fo.write("\nendTest()")

fo.close()

