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

import sys
import xlrd
import py_compile


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

testcaseScriptFile = testcaseFile.split('.')[0]
testcaseScriptFile = testcaseScriptFile + "_" + testcaseFileSheet

py_compile.compile("LatteScriptGenerator.py")


#------------------------------Initialization of Variables---------------------------------------#
def initVariables():
    '''
    Description: This function assigns names to excel sheet columns.
    '''
    global col_ReqId
    global col_TestType
    global col_IOType
    global col_Type
    global col_TestName
    global col_TestDesc
    global col_TestCondn
    global col_ExpecRes
    global col_Comments
    global Test_Case_Cnt
    global Test_Step_Cnt
    global curr_row

    col_ReqId = 0
    col_TestType = 1
    col_IOType = 2
    col_Type = 3
    col_TestName = 4
    col_TestDesc = 5
    col_TestCondn = 6
    col_ExpecRes = 7
    col_Comments = 8

    Test_Case_Cnt = 0
    Test_Step_Cnt = 0
    curr_row = 1

#------------------------------ Open Testcase Workbook ---------------------------------------#
def openWorkbook():
    '''
    Description: This function open Excel sheet in which all test cases are written.
    user shoud store excel sheet in current working directory.
    '''

    global xl_sheet #xlsheet var
    global book

    book_path = testcaseDirectory + "\\" + testcaseFile #path of excelsheet
    book = xlrd.open_workbook(book_path)  #open excelsheet"Test_Details"


#---------------------------- Create Python File for each WorkSheet -----------------------------------#
def openPythonFile():
    '''
    Description:This function will create new Python file i.e .py file for each testSheet
    '''
    global fo

    if testcaseScriptFile != "":
        pytitle = testcaseDirectory + "\\"  + testcaseScriptFile +'.py'
    else:
        raw_input('\nUser has not entered valid choice')
        sys.exit()

    fo = open(pytitle,'w') #open file in write mode

#----------------------------Create Batch File for each Python file----------------------------------#
def createBatchFile():
    '''
    Description: This Function creates and writes to batch file that executes corresponding .py file
    '''
    global batchfo

    if testcaseScriptFile != "":
        batchtitle = testcaseDirectory + "\\"  + testcaseScriptFile +'.bat'
    else:
        raw_input('\nUser has not entered valid choice')
        sys.exit()

    batchfo = open(batchtitle,'w')#open file in write mode
    batchfo.write("c:\Python27\python.exe %s" %(testcaseScriptFile +'.py'))
    batchfo.close()


#----------------------------Read tla_library sheet from Workbook---------------------------------#
def readTLALibrarySheet():
    '''
    Description:Extracting values from sheet tla_library e.g TLA,Component_VERSION,SW_BRANCH etc.
    '''
    global TLA
    global Component_VERSION
    global TLA_VERSION
    global SW_BRANCH
    global SVN_REVISION
    global HW_VERSION
    global AUTHOR
    global TLA_Description
    global REPORT_NAME

    TLA                 = xl_sheet.cell(2,2).value
    Component_VERSION   = xl_sheet.cell(4,2).value
    TLA_VERSION         = xl_sheet.cell(6,2).value
    SW_BRANCH           = xl_sheet.cell(8,2).value
    SVN_REVISION        = xl_sheet.cell(10,2).value
    HW_VERSION          = xl_sheet.cell(12,2).value
    AUTHOR              = xl_sheet.cell(14,2).value
    TLA_Description     = xl_sheet.cell(16,2).value
    REPORT_NAME         = TLA_Description + "_" + testcaseFileSheet


#---------------------------- Generate Copyright header -------------------------------------------#
def writeCopyright():
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

#---------------------------- Generate Path Settings -----------------------------------------------#
def writePathSettings():
    '''
    Description: This function write all project related path to py file.
    Example:
         Tools_PATH,CODE_PATH
    creates object for t32,com
    '''
    fo.write("\n\nREPORT_API_PATH = os.path.abspath(r'../latte_libs/report')")
    fo.write("\nCOM_API_PATH = os.path.abspath(r'../latte_libs/com')\n")

    fo.write("\n\n# Adding paths for loading correctly .py libraries")
    fo.write("\nsys.path.append(REPORT_API_PATH)")
    fo.write("\nsys.path.append(COM_API_PATH)")

    fo.write("\n\nfrom report import *")
    fo.write("\nfrom com import *")

#---------------------------- Generate Report Settings ---------------------------------------------#
def writeReportSettings():
    '''
    Description:This function write all extracted values(from excel sheet) regarding the report header in .py file
    '''
    fo.write("\n\n\n# Report Header Variables")
    fo.write("\nAUTHOR = '%s'" %AUTHOR)
    fo.write("\nTLA = '%s'" % TLA )
    fo.write("\nPROJECT_NAME = 'JLR X590 BCCM'" )
    fo.write("\nSW_VERSION = '%s'" % SVN_REVISION)
    fo.write("\nHW_VERSION = '%s'" %  HW_VERSION)
    fo.write("\nNETWORK_TYPE = 'CAN'")
    fo.write("\n\n# Create the report object, specifying the test data")
    fo.write("\nreport = HTMLReport(TLA, PROJECT_NAME, SW_VERSION, HW_VERSION, NETWORK_TYPE, AUTHOR)")

#---------------------------- Generate CAN,LIN,FR Channel Settings ---------------------------------#
def writeChannelSettings():
    '''
    Description:This for Loop Extract can channel baud rate,Channel ID,LDf,DBC.
    it Checks CAN Access req. and according to that set channel
    '''
    fo.write("\n\n")
    fo.write("#################################################################\n")
    fo.write("##               Set CAN,LIN,FR Channels                       ##\n")
    fo.write("#################################################################\n")
    fo.write("\ncom = Com('VECTOR')")
    fo.write("\ncanObj = com.open_can_channel(int(%s),int(%s))" % (xl_sheet.cell(21,3).value, xl_sheet.cell(21,4).value))

#---------------------------- Generate Precondition Statements -------------------------------------#
def writePreconditions():
    fo.write("\n\n")
    fo.write("#################################################################\n")
    fo.write("##      Load dbc,Periodic Tester Present,Periodic NM message   ##\n")
    fo.write("#################################################################\n")
    fo.write("\ncanObj.load_dbc('%s')" % (xl_sheet.cell(21,5).value))
    fo.write("\ncanObj.send_cyclic_frame('BCCM_NM51F',100)")
    fo.write("\ncanObj.dgn.ecu_reset(0x01)" )
    fo.write("\ncanObj.dgn.start_periodic_tp()" )
    fo.write("\ntime.sleep(1)\n" )

#---------------------------- Generate GetActualResponseFrames() Function --------------------------#
def writeGetActualRespDef():
    fo.write("\ndef GetActualResponseFrames():\n")
    fo.write("    response_str = ''\n")
    fo.write("    response_str = canObj.dgn.req_info_raw().split('Rsp:')[1]\n")
    fo.write("    response_str = response_str.replace('[','')\n")
    fo.write("    response_str = response_str.replace(']','')\n")
    fo.write("    response_str = response_str.replace(' ','')\n")
    fo.write("    return response_str\n\n\n")


#---------------------------- Generate InvokeMessageBox() Function ---------------------------------#
def writeInvokeMsgBoxDef():
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

#--------------------------- Python TestCase function Definition ----------------------------------#
def writeTestCaseDef(ETest_Case_Cnt):
        '''
        Description:This function starts to write new test case in .py file
        it writes test description ,test case requirment id to py file.
        '''
        test_name      = xl_sheet.cell(curr_row,col_TestName).value
        test_case_desc = xl_sheet.cell(curr_row,col_TestDesc).value
        test_case_reqs = xl_sheet.cell(curr_row,col_ReqId).value

        fo.write("\n#######################")
        fo.write("\n## Test Case %s       ##" %ETest_Case_Cnt)
        fo.write("\n#######################"+ '\n' + '\n')
        fo.write('def test_%s():\n' %(str(ETest_Case_Cnt)))

        TD = test_name.replace('\'','\"')  #in Test Name Statement replace ' with " for indentation
        TD = TD.replace('\n',' ')   #in Test Name Statement replace \n with ' ' for indentation
        TN = test_case_desc.replace('\n',' ')  #in Test Description Statement replace \n with ' ' for indentation
        TN = TN.replace('\'','\"')  #in Test Description Statement replace ' with " for indentation

        fo.write("    test_case_name = 'Test Case %s: %s'\n" % (ETest_Case_Cnt,TD))#Write Test Name
        fo.write("    test_case_desc = '%s'\n" %TN) #Write Test Description
        fo.write("    test_case_reqs = '%s'\n" % test_case_reqs.replace('\n',' ') ) #Write Test Requirment ID
        fo.write("    print test_case_name\n\n")
        fo.write("    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)\n\n")

#------------------------------ Process DIAG type test steps ---------------------------------------#
def processTypeDIAG():
    #Extract values from excel sheet
    test_step_Desc = xl_sheet.cell(curr_row,col_TestDesc).value       #Description
    Comments_string = str(xl_sheet.cell(curr_row,col_Comments).value) #Comments
    Expec_res_raw=str(xl_sheet.cell(curr_row,col_ExpecRes).value)     #Expected value of Test Step
    Expec_res_raw=Expec_res_raw.split('.')[0]

    Expec_res = Expec_res_raw
    Expec_res=Expec_res.replace('\n',' ')
    Expec_res=Expec_res.replace(' ','')
    Expec_res=Expec_res.upper()

    Diag_Service=str(xl_sheet.cell(curr_row,col_TestCondn).value)
    Diag_Service=Diag_Service.split('.')[0]
    Diag_Service = Diag_Service.replace(" ", "")


    if Diag_Service[0:2]=='11': # Check for diagnostic service ID is "RESET"

        PID=Diag_Service[2:4] #Extract Reset Type

        print_row = int(curr_row)+1

        fo.write("    #######################################\n")  #Print row number of excel sheet
        fo.write("    #Code block generated for row no = %s  #\n" %print_row)
        fo.write("    ##################################### #\n\n")

        fo.write("    ################################\n")  # Reset By Diagnostics
        fo.write("    ## Reset By Diagnostics  ##\n")
        fo.write("    ################################\n\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        fo.write("    canObj.dgn.ecu_reset(%s)\n" % ('0x'+PID))
        fo.write("    time.sleep(1)\n" )

        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Reset Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Unable to reset.Test Fails:!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report


    elif Diag_Service[0:2]=='31': # Check for diagnostic service ID is "ROUTINE ID"

        PID = Diag_Service[2:4]          #Extract PID Number

        print_row = int(str(curr_row))+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ################################\n")  #Read DID By Diagnostics
        fo.write("    ##          ROUTINES          ##\n")
        fo.write("    ################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")


        if(PID == ''):
            fo.write("    canObj.dgn.iso.net.send_request([0x31, ], 'PHYSICAL')\n")

        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x31")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")

        fo.write("    time.sleep(1)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Routine Execution Succesful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Routine Execution Fails:!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report

    elif Diag_Service[0:2]=='22': # Check for diagnostic service ID is "READ DID"

        PID='0x'+Diag_Service[2:6] #Extract PID Number

        print_row = int(str(curr_row))+1

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


        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ################################\n")  #Read DID By Diagnostics
        fo.write("    ##          Read DID          ##\n")
        fo.write("    ################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if len(Diag_Service) > 6:
            fo.write("    canObj.dgn.read_DID_Len_W(%s,%s) \n" % (PID,Extra_Parameter))
        else:
            fo.write("    canObj.dgn.read_did(%s) \n" % (PID))
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
            fo.write("          test_step_Result = True\n")
            fo.write("          test_step_Comment ='Test Successful.'\n")
            fo.write("    else: \n" )
            fo.write("          test_step_Result = False\n")
            fo.write("          test_step_Comment ='Test Fails!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report


    elif Diag_Service[0:2]=='10': # Check for diagnostic service ID is "Session CTRL DID"

        PID=Diag_Service[2:4] #Extract Session Number

        print_row = int(str(curr_row))+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
        fo.write("    ##          Session Ctrl  #\n")
        fo.write("    ################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if(len(Diag_Service) <= 4):
            if PID =='01':
                fo.write("    canObj.dgn.default_session() \n") #evaluation of default session
            elif PID =='02':
                fo.write("    canObj.dgn.programming_session() \n") #evaluation of programming session
            elif PID =='03':
                fo.write("    canObj.dgn.extended_session() \n") #evaluation of extended session
            elif PID =='':
                fo.write("    canObj.dgn.iso.net.send_request([0x10, ], 'PHYSICAL') \n") #evaluation of No session subfunction
            else :
                fo.write("    canObj.dgn.iso.service_0x10(%s)\n" % ('0x'+PID)) #evaluation of internal session
        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x10")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")


        fo.write("    time.sleep(0.3)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Test Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Test Failed!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report


    elif Diag_Service[0:2]=='27': # Check for diagnostic service ID is "Security Access ID"

        PID=Diag_Service[2:4] #Extract Session Number

        print_row = int(str(curr_row))+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ################################\n")  #Security Access By Diagnostics
        fo.write("    ##          Security Access  #\n")
        fo.write("    ################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if ("Send" in TD) and ("Wrong" in TD) and ("Key" in TD):
            fo.write("    canObj.dgn.security_access_wrong_key(%s)\n" % ('0x'+PID))
        else:
            fo.write("    canObj.dgn.security_access(%s)\n" % ('0x'+PID))

        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Test Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Test Failed!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report


    elif Diag_Service[0:2]=='19': # Check for diagnostic service ID is "READ DTC Information"

        PID=Diag_Service[2:4] #Extract PID Number

        print_row = int(curr_row)+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ################################\n")  #READ DTC Information
        fo.write("    ##    READ DTC Information    ##\n")
        fo.write("    ################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if(PID == ''):
            fo.write("    canObj.dgn.iso.net.send_request([0x19, ], 'PHYSICAL')\n")
        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x19")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")

        fo.write("    time.sleep(1)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Read DTC Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Read DTC Failed!!'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report



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

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if(len(Diag_Service) <= 4):
            if(PID == ''):
                fo.write("    canObj.dgn.iso.net.send_request([0x85, ], 'PHYSICAL')\n")
            else:
                fo.write("    canObj.dgn.control_dtc_setting_custom(%s)\n" % ('0x'+PID))
        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x85")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")


        fo.write("    time.sleep(1)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Test Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Test Failed.'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report

    elif Diag_Service[0:2]=='14': # Check for diagnostic service ID is "Clear Diagnosice Information"

        PID = Diag_Service[2:4] #Extract Subfunction

        print_row = int(curr_row)+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ###################################\n")  #Clear Diagnosice Information
        fo.write("    ## Clear Diagnostics Information  ##\n")
        fo.write("    ###################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")

        if(PID == ''):
            fo.write("    canObj.dgn.iso.net.send_request([0x14, ], 'PHYSICAL')\n")
        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x14")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")


        fo.write("    time.sleep(1)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Test Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Test Failed.'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report


    elif Diag_Service[0:2]=='3E': # Check for diagnostic service ID is "Tester Present"

        PID=Diag_Service[2:4] #Extract PID Number

        print_row = int(curr_row)+1

        fo.write("\n    #######################################")  #Print row number of excel sheet
        fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        fo.write("\n    ##################################### #\n")

        fo.write("\n    ###################################\n")  #Tester Present
        fo.write("    ##         Tester Present         ##\n")
        fo.write("    ###################################\n")

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")


        if(len(Diag_Service) <= 4):
            if(PID == '00'):
                fo.write("    canObj.dgn.tester_present()\n")
            elif(PID == '80'):
                fo.write("    canObj.dgn.tester_present_spr()\n")
            elif(PID == ''):
                fo.write("    canObj.dgn.iso.net.send_request([0x3E, ], 'PHYSICAL')\n")
            else:
                fo.write("    canObj.dgn.tester_present_custom(%s)\n" % ('0x'+PID))
        else:
            fo.write("    canObj.dgn.iso.net.send_request([0x3E")

            for i in range(2,len(Diag_Service),2):
                fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

            fo.write("], 'PHYSICAL') \n")


        fo.write("    time.sleep(1)\n" )
        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = GetActualResponseFrames()\n")
        fo.write("\n")
        fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='Test Successful.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='Test Failed.'\n")
        fo.write("\n")
        fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
        fo.write("\n")
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report

#------------------------------ Process POPUP type test steps ---------------------------------------#
def processTypePOPUP():

    print_row = int(str(curr_row))+1

    fo.write("\n    #######################################")  #Print row number of excel sheet
    fo.write("\n    #Code block generated for row no = %s  #"%print_row)
    fo.write("\n    ##################################### #\n")

    test_step_Desc = xl_sheet.cell(curr_row,col_TestDesc).value #Description

    TD = test_step_Desc.replace('\n',' ')
    TD = TD.replace('\'','\"')

    if(test_step_Desc == ''): # Check For Proper Data Entry in Excel sheet
        print("\n**Error occured.")
        print("\nTest Description is not provided.")
        print("\nCheck Row no:")+str(curr_row+1)+"\n"
        print("\nCheck column number:")+str(col_TestDesc)+"\n"
        sys.exit()
    elif('Make Tester Present OFF' in TD):
        fo.write("\n    ###################################\n")  #Tester Present
        fo.write("    ##         Tester Present         ##\n")
        fo.write("    ###################################\n")
        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    canObj.dgn.stop_periodic_tp()\n")
    elif('Make Tester Present ON' in TD):
        fo.write("\n    ###################################\n")  #Tester Present
        fo.write("    ##         Tester Present         ##\n")
        fo.write("    ###################################\n")
        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    canObj.dgn.start_periodic_tp()\n")
    else:
        fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
        fo.write("    ##          Message Pop-up  #\n")
        fo.write("    ################################\n")

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    InvokeMessageBox(test_step_Desc)\n" )


    fo.write(r"    report.add_test_step(test_step_Desc,True,'','')") #Report
    fo.write("\n")
    fo.write("\n")

#------------------------------ Process DELAY type test steps ---------------------------------------#
def processTypeDELAY():

    description = xl_sheet.cell(curr_row,col_TestDesc).value #Description
    time = xl_sheet.cell(curr_row,col_TestCondn).value #Time
    conditn_Val = xl_sheet.cell(curr_row,col_ExpecRes).value #Cyclic Time

    if(conditn_Val != ''): # Check For Proper Data Entry in Excel sheet
        print "\n**Error occured."
        print "\nNo Need of Expected Result for DELAY type test step"
        print "\nCheck Row no: " + str(curr_row)
        print "\nCheck Column no: " + str(col_ExpecRes)
        sys.exit()

    if(description == ''): # Check For Proper Data Entry in Excel sheet
        print "\n**Error occured."
        print "\nTest Description is not provided."
        print "\nCheck Row no:" + str(curr_row)
        print "\nCheck Column no:" + str(col_TestDesc)
        sys.exit()

    if(time == ''): #Time should not be blank
        print "\n**Error occured."
        print "\nProvide time(in sec) for delay"
        print "\nCheck Row no: " + str(curr_row)
        print "\nCheck Column no:" + str(col_TestCondn)
        sys.exit()

    print_row = int(str(curr_row))+1
    fo.write("\n    #######################################")  #Print Row number
    fo.write("\n    #Code block generated for row no = %s #"%print_row)
    fo.write("\n    #######################################\n")

    TD = description.replace('\n',' ') #Remove if new line is added in test description
    TD = TD.replace('\'','\"')
    fo.write("    test_step_Desc='%s'\n" %TD)
    fo.write("    print test_step_Desc\n")
    fo.write("    time.sleep(%s)"%time)
    fo.write("\n")
    fo.write(r"    report.add_test_step(test_step_Desc,True,'','')") #Report
    fo.write("\n")
    fo.write("\n")

#------------------------------ Process CANSIGNAL type test steps ---------------------------------------#
def processTypeCANSIGNAL():
    #Extract values from excel sheet
    test_step_Desc = xl_sheet.cell(curr_row,col_TestDesc).value #Description
    Comments_string = str(xl_sheet.cell(curr_row,col_Comments).value) #Comments


    Can_Signal_Details=str(xl_sheet.cell(curr_row,col_TestCondn).value)
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

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")
        fo.write("    canObj.send_cyclic_frame('%s',10) \n" %(Can_Message))
        #fo.write("    canObj.set_signal('%s',%s) \n" %(int(1),Can_Signal,Can_Signal_Value))

        fo.write("    canObj.set_signal('%s',[" %(Can_Signal))
        for i in range(len(Can_Signal_Value_List)):
            if i == (len(Can_Signal_Value_List)-1):
                fo.write("%s" %Can_Signal_Value_List[i])
            else:
                fo.write("%s," %Can_Signal_Value_List[i])

        fo.write("]) \n")
        fo.write("    time.sleep(0.5)\n" )

        fo.write("\n")
        fo.write("    Expec_res = '%s'\n"%Expec_res)
        fo.write("    Actual_res = canObj.get_signal('%s','%s')\n"%(Can_Signal,Can_Message))
        fo.write("    Actual_res = str(hex(Actual_res))\n")
        fo.write("    Actual_res = Actual_res.replace('0x','')\n")
        fo.write("    Actual_res = Actual_res.replace('L','')\n")
        fo.write("    Actual_res = Actual_res.replace(' ','')\n")
        fo.write("    Actual_res = Actual_res.upper()\n")
        fo.write("\n")

        fo.write("    if Expec_res == Actual_res: \n" )
        fo.write("          test_step_Result = True\n")
        fo.write("          test_step_Comment ='CAN signal set Successfully.'\n")
        fo.write("    else: \n" )
        fo.write("          test_step_Result = False\n")
        fo.write("          test_step_Comment ='CAN signal could not be set.'\n")
        fo.write("    test_step_ResponseStr = str(canObj.get_frame(canObj.dbc.find_frame_id('%s')))\n"%(Can_Message))
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result,'%s.%s='+Actual_res,'%s',test_step_Comment + '\n' + '%s')"%(Can_Message,Can_Signal,Test_Condition,Comments_string)) #Report
    else:
        print "Test Condition entered is incorrect !!"


#------------------------------ Process CANFRAME type test steps ---------------------------------------#
def processTypeCANFRAME():
    #Extract values from excel sheet
    test_step_Desc = xl_sheet.cell(curr_row,col_TestDesc).value #Description
    Comments_string = str(xl_sheet.cell(curr_row,col_Comments).value) #Comments
    Expec_res=str(xl_sheet.cell(curr_row,col_ExpecRes).value) #Expected value of Test Step

    Expec_res=Expec_res.split('.')[0]
    Expec_res=Expec_res.replace('\n',' ')
    Expec_res=Expec_res.replace(' ','')
    Expec_res=Expec_res.upper()

    Can_Frame_Details=str(xl_sheet.cell(curr_row,col_TestCondn).value)
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

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
        fo.write("    test_step_Result = False\n" )
        fo.write(r"    test_step_Comment = '\n'" )
        fo.write("\n")
        fo.write(r"    test_step_ResponseStr = '\n'" )
        fo.write("\n")
        fo.write("\n")
        fo.write("    canObj.write_frame(%s, %s, [" %(Can_FrameID,len(Can_Frame_Value_List)))
        for i in range(len(Can_Frame_Value_List)):
            if i == (len(Can_Frame_Value_List)-1):
                fo.write("%s" %Can_Frame_Value_List[i])
            else:
                fo.write("%s," %Can_Frame_Value_List[i])

        fo.write("]) \n")

        fo.write("    time.sleep(0.5)\n" )
        fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result,'%s' + comment + '\n' + '%s')"%(Test_Condition,Comments_string)) #Report
    else:
        print "Test Condition entered is incorrect !!"


#------------------------------ Generate EndTest Function ---------------------------------------#
def writeEndTestDef():
    fo.write("\n\ndef endTest():")
    fo.write("\n    report.generate_report()")
    fo.write("\n    canObj.dgn.iso.net.log_file = report.get_log_dir()")
    fo.write("\n    canObj.dgn.save_logfile()")
    fo.write("\n    canObj.dgn.stop_periodic_tp()")
    fo.write("\n    canObj.stop_cyclic_frame('BCCM_NM51F')")
    fo.write("\n")
    fo.write(r"    print '\nScript Execution Finished !!'")
    fo.write("\n")
    fo.write("\n    com.exit()\n\n\n\n")

#------------------------------ Generate Calling of Test Functions -----------------------------#
def writeCallingOfTestcases():
    fo.write("\n#############################")
    fo.write("\n## Execute the test cases  ##")
    fo.write("\n#############################"+ '\n' + '\n')

    #Start Calling all Test Case
    Cnt=1
    while Cnt<=Test_Case_Cnt:
        fo.write("test_%s()\n" %Cnt)
        Cnt+=1
        fo.write("time.sleep(1)\n")

#------------------------------ Finish writing the Python file -----------------------------#
def closePythonFile():
    fo.write("\n# Perform End actions i.e Save log files, Generate Report etc..")
    fo.write("\nendTest()")
    fo.close()



'############################### FUNCTION CALLS ############################################'
initVariables()           #Function Call
openWorkbook()            #Function call

'''Open tla library sheet'''
xl_sheet = book.sheet_by_name('tla_library')  #Open sheet

readTLALibrarySheet()     #Function call
createBatchFile()         #Function call
openPythonFile()          #Function call
writeCopyright()          #Function call
writePathSettings()       #Function Call
writeReportSettings()     #function call
writeChannelSettings()    #function call
writePreconditions()      #function call
writeGetActualRespDef()   #function call
writeInvokeMsgBoxDef()    #function call


'''Open IntegrationTest sheet'''
xl_sheet = book.sheet_by_name(testcaseFileSheet)  # IntegrationTest sheet open

#---------------------- Loop starts to access the test case/steps untill the END of Line-------------------#
while (str(xl_sheet.cell(curr_row,col_ReqId).value)!='END Line. Do Not Remove'):

    if xl_sheet.cell(curr_row,col_TestType).value == 'TH':  #New Test Case

        Test_Case_Cnt+=1 # Increment the Test Case Count
        Test_Step_Cnt=0  # Reinitialize the Test Step Count

        print("\n*************Writing test case ")+str(Test_Case_Cnt) +("*************")

        writeTestCaseDef(Test_Case_Cnt) #function call
        #print("\nTest Step count: ") +str(Test_Step_Cnt)

    elif xl_sheet.cell(curr_row,col_TestType).value == 'TS': #New Test Step

        Test_Step_Cnt+=1 #Increment Test Step Count

        if xl_sheet.cell(curr_row,col_Type).value == 'DIAG':
            processTypeDIAG()

        elif xl_sheet.cell(curr_row,col_Type).value == 'MSG_POPUP':
            processTypePOPUP()

        elif xl_sheet.cell(curr_row,col_Type).value == 'DELAY_SEC':
            processTypeDELAY()

        elif xl_sheet.cell(curr_row,col_Type).value == 'CAN_SIGNAL':
            processTypeCANSIGNAL()

        elif xl_sheet.cell(curr_row,col_Type).value == 'CAN_FRAME':
            processTypeCANFRAME()

        else:
            #Check if none of the Command Type is provided
            print "\nCommand Type is not selected for test step"
            print "\nCheck Row no: " + str(curr_row+1)
            print "\nCheck Column no:" + str(col_Type)

    else:
        print ""


    #Increment row count
    curr_row+=1
#----------------------------------------------------------------------------------------------------------#

writeEndTestDef()
writeCallingOfTestcases()
closePythonFile()

print "\n"
print "Total Number of Test Cases: "+ str(Test_Case_Cnt)
print "Testcase script " + testcaseScriptFile + ".py" + " generated !!"
print "\n\n\n"

