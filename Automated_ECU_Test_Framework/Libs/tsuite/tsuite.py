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
from openpyxl import *

pythonpath="c:\Python27\python.exe"
testcaseFile = str(sys.argv[1])
testcaseFileSheet = str(sys.argv[2])
testcaseDirectory = sys.argv[3]
testcaseScriptFile = testcaseFile.split('.')[0]
testcaseScriptFile = testcaseScriptFile + "_" + testcaseFileSheet




#Before Calling the init test suite class somewhere add the message for checking the format for excel
class Testsuite:
    '''
    Class for accessing the Framework functionalities.
    '''

    def __init__(self,workBookName='',workSheetName='',tableHdrRow=17,rowTypeCol=0,cmdTypeCol=1,reqIDCol=2,testNameCol=3,testDescCol=4,testCondCol=5,expResCol=6,actResCol=7,testResCol=8,commentCol=9,first_TH_row=18):
        '''
        Description: Constructor. Access the physical communication device.

        Example:
            tsuiteObj = Testsuite()
        '''
        self.workBookName  = workBookName
        self.workSheetName = workSheetName

        self.tableHdrRow = tableHdrRow
        self.rowTypeCol  = rowTypeCol
        self.cmdTypeCol  = cmdTypeCol
        self.reqIDCol    = reqIDCol
        self.testNameCol = testNameCol
        self.testDescCol = testDescCol
        self.testCondCol = testCondCol
        self.expResCol   = expResCol
        self.actResCol   = actResCol
        self.testResCol  = testResCol
        self.commentCol  = commentCol

        self.curr_row    = first_TH_row
        self.Test_Case_Cnt = 0
        self.Test_Step_Cnt = 0
        self.writerow_number=tableHdrRow
        self.cwd =os.getcwd()



#TODO change the functions name at all instances EXCEL PATH

    def Excel_Path(self):
        '''
        Description: This function open Excel sheet in which all test cases are written.
        user shoud store excel sheet in current working directory.
        '''
        self.testcaseFile = str(sys.argv[1])
        self.testcaseFileSheet = str(sys.argv[2])
        self.testcaseDirectory = sys.argv[3]
        self.book_path = self.testcaseDirectory + "\\" + self.testcaseFile #path of excelsheet
        self.book = load_workbook(filename = str(self.book_path))
        self.xl_sheet = self.book.get_sheet_by_name(str(testcaseFileSheet))

        print "Excel_Path Called inside tsuite"

    def get_workbookpath(self):
        return str(self.testcaseDirectory + "\\" + self.testcaseFile) #path of excelsheet
    def get_worksheet(self):
        return str(self.testcaseFileSheet)
    def fill_Test_data(self):

        #-------------Check for TH at first pos
        if((str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value)=='TS')):
            print "\n#######################################"
            print "\n##Please  Begin your tests  with a TH##"
            print "\n#######################################"
            sys.exit()
        #--------------------




        if((str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value)=='END Line. Do Not Remove')):
            print "ERROR ADD SOME DATA TO THE SHEET"
        self.list_of_tests=[]
        self.Test_Case_Cnt=0


        while (str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value)!='END Line. Do Not Remove'): #Loop starts to access the test case/steps untill the END of  Line
            #check for beginning with 'TH' or 'TS'
            self.commandType=[]
            self.testDescription=[]
            self.testConditions=[]
            self.expectedResult=[]
            self.actualResult=[]
            self.testResults=[]
            self.comments=[]
            self.Test_Step_Cnt=0
            self.Test_data ={
                             'Row_TYPE' :'',
                             'TS_Command_TYPE':self.commandType,#Addded
                             'TH_Requirement_ID':'',
                             'TH_Test_NAME':'',
                             'TH_Test_DESCRIPTION':'',
                             'TS_Test_DESCRIPTION':self.testDescription,#
                             'TS_Test_CONDITION':self.testConditions,
                             'TS_Expected_RESULT':self.expectedResult,
                             'TS_Actual_RESULT':self.actualResult,
                             'TS_Test_RESULT':self.testResults,
                             'TS_Comments':self.comments,
                             'TH_Tscount':''
                          }
            if(
                     str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) != ('TH')
                and  str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) != ('TS')
               ):

                print "\nWrong data entered in row" + str(self.curr_row) + " column " +str(self.rowTypeCol)+"\n"
                print "The Cells in this column should contain TH or TS only"
                print "Make sure to begin with a TH"
                sys.exit()

                '''for test Cases'''
            if (
                str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == 'TH'
                ):

                print "Found TH/TS in column 1 Ready to Go"
                print("\n*************Filling the data for test case Number")+str(self.Test_Case_Cnt) +("*************")
                '''Row type is required for both'''
                self.Test_Case_Cnt += 1 # Increment the Test Case Count
                self.Test_data['Row_TYPE']              = self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value
                self.Test_data['TH_Requirement_ID']     =str(self.xl_sheet.cell(self.curr_row,self.reqIDCol).value)
                self.Test_data['TH_Test_NAME']          =str(self.xl_sheet.cell(self.curr_row,self.testNameCol).value)
                self.Test_data['TH_Test_DESCRIPTION']   = str(self.xl_sheet.cell(self.curr_row,self.testDescCol).value)#conditions
                self.curr_row += 1
                if str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == 'TS':
                    while(
                             str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == ('TS')
                          or str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == ('')
                          ):
                        if(str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == ('')):
                            self.curr_row +=1
                        elif(str(self.xl_sheet.cell(self.curr_row,self.rowTypeCol).value) == ('TS')):

                            ''''for test Steps'''
                            self.commandType.append(str(self.xl_sheet.cell(self.curr_row,self.cmdTypeCol).value))
                            self.testDescription.append(str(self.xl_sheet.cell(self.curr_row,self.testDescCol).value))#conditions
                            self.testConditions.append(str(self.xl_sheet.cell(self.curr_row,self.testCondCol).value))
                            self.expectedResult.append(str(self.xl_sheet.cell(self.curr_row,self.expResCol).value))
                            self.actualResult.append(str(self.xl_sheet.cell(self.curr_row,self.actResCol).value))
                            self.testResults.append(str(self.xl_sheet.cell(self.curr_row,self.testResCol).value))
                            self.comments.append(str(self.xl_sheet.cell(self.curr_row,self.commentCol).value))
                            print str(self.curr_row)
                            print "Added Test step "+str(self.Test_Step_Cnt)
                            self.Test_Step_Cnt+=1
                            self.curr_row += 1
                    self.Test_data['TH_Tscount']   = str(self.Test_Step_Cnt)
            self.list_of_tests.append(self.Test_data)
            self.totaltests=str(self.Test_Case_Cnt)
            print "Added data of row %s" %self.curr_row

#     def printdata(self): #to print ids(/addr) of all the list items
#         for i in self.list_of_tests:
#             print "points to",id(i)
    def get_totaltests(self):
        return self.Test_Case_Cnt
    def get_keys(self):
        if(
           self.list_of_tests[0].keys()!=None
           ):
            return self.list_of_tests[0].keys()
        else:
            print "Error\nDictionary not filled\n"


    def get_sheettitle(self):
        return str(self.xl_sheet.cell(4,self.testNameCol).value)
    def get_sheetauthor(self):
        return str(self.xl_sheet.cell(6,self.testNameCol).value)
    def get_sheetproject(self):
        return str(self.xl_sheet.cell(8,self.testNameCol).value)
    def get_sheetsoftwareversion(self):
        return str(self.xl_sheet.cell(10,self.testNameCol).value)
    def get_sheethardwareversion(self):
        return str(self.xl_sheet.cell(12,self.testNameCol).value)
    def get_sheetnetwork(self):
        return str(self.xl_sheet.cell(14,self.testNameCol).value)

    def get_sheetCANchannel(self):
        return str(self.xl_sheet.cell(4,self.actResCol).value)
    def get_sheetCANchannelBR(self):
        return str(self.xl_sheet.cell(4,self.testResCol).value)

    def get_sheetLINchannel(self):
        return str(self.xl_sheet.cell(6,self.actResCol).value)
    def get_sheetLINchannelBR(self):
        return str(self.xl_sheet.cell(6,self.testResCol).value)

    def get_sheetflexraychannel(self):
        return str(self.xl_sheet.cell(8,self.actResCol).value)
    def get_sheetflexraychannelBR(self):
        return str(self.xl_sheet.cell(8,self.testResCol).value)

    def get_dbcpath(self):
        return str(self.xl_sheet.cell(10,self.actResCol).value)
#                              'Row_TYPE' :'',
#                              'TS_Command_TYPE':self.commandType,#Addded
#                              'TH_Requirement_ID':'',
#                              'TH_Test_NAME':'',
#                              'TH_Test_DESCRIPTION':'',
#                              'TS_Test_DESCRIPTION':self.testDescription,#
#                              'TS_Test_CONDITION':self.testConditions,
#                              'TS_Expected_RESULT':self.expectedResult,
#                              'TS_Actual_RESULT':self.actualResult,
#                              'TS_Test_RESULT':self.testResults,
#                              'TS_Comments':self.comments,
#                              'TH_Tscount':''
    def get_testcommandtype(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Command_TYPE'][teststepnumber])

    def get_testrequirementid(self,testcasenumber):
        return str(self.list_of_tests[testcasenumber]['TH_Requirement_ID'])

    def get_testname(self,testcasenumber):
        return str(self.list_of_tests[testcasenumber]['TH_Test_NAME'])

    def get_testdescription(self,testcasenumber):
        return str(self.list_of_tests[testcasenumber]['TH_Test_DESCRIPTION'])

    def get_teststepdescription(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Test_DESCRIPTION'][teststepnumber])

    def get_testconditions(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Test_CONDITION'][teststepnumber])

    def get_expectedresult(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Expected_RESULT'][teststepnumber])

    def get_actualresult(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Actual_RESULT'][teststepnumber])

    def get_testresults(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Test_RESULT'][teststepnumber])

    def get_comments(self,testcasenumber,teststepnumber):
        return str(self.list_of_tests[testcasenumber]['TS_Comments'][teststepnumber])

    def get_numberofteststeps(self,testcasenumber):
        return str(self.list_of_tests[testcasenumber]['TH_Tscount'])

#-------------------------Function Definitons related to Script writing begin from here---------------------------------------------------

#----------------------------Opening the python file-----------------------------------------------------------------
    def openPythonFile(self):
        '''
        Description:This function will create new Python file i.e .py file for each testSheet
        '''

        if ".xlsm" in self.testcaseFile:
            self.testcaseScriptFile = self.testcaseFile.replace('.xlsm', '')
        elif ".xlsx" in self.testcaseFile:
            self.testcaseScriptFile = self.testcaseFile.replace('.xlsx', '')
        elif ".XLSX" in self.testcaseFile:
            self.testcaseScriptFile = self.testcaseFile.replace('.XLSX', '')
        elif ".XLS" in self.testcaseFile:
            self.testcaseScriptFile = self.testcaseFile.replace('.XLS', '')
        elif ".xls" in self.testcaseFile:
            self.testcaseScriptFile = self.testcaseFile.replace('.xls', '')

        if self.testcaseScriptFile != "":
            newpath = self.cwd + "\\"  + 'Testsuite\\' + self.testcaseScriptFile + "\\" + self.testcaseFileSheet
            #self.testcaseScriptFile = self.testcaseScriptFile + "_" + self.testcaseFileSheet
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            self.pytitle = newpath + "\\"  + self.testcaseScriptFile + "_" + self.testcaseFileSheet +'.py'
            self.batchtitle = newpath + "\\"  + self.testcaseScriptFile+ "_" + self.testcaseFileSheet +'.bat'

            #===================================================================
            # self.pytitle = self.cwd + "\\"  + 'Libs\\' + self.testcaseScriptFile +'.py'
            # self.batchtitle = self.cwd + "\\" + 'Libs\\'  + self.testcaseScriptFile +'.bat'
            #===================================================================

        else:
            raw_input('\nUser has not entered valid choice')
            sys.exit()

        self.fo = open(self.pytitle,'w') #open file in write mode
        self.batchfo = open(self.batchtitle,'w')#open file in write mode
        print "file_creation Called inside tsuite"
#--------------------------------------------------------------------------------------------------------------------
#-----------------------------Write Batchfile------------------------------
    def write_batchfile(self):
        '''
        Description: This Function writes to batch file that executes corresponding .py file
        '''
        self.batchfo = open(self.batchtitle,'w')#open file in write mode
        self.batchfo.write(pythonpath + " %s" %(testcaseScriptFile +'.py'))
        self.batchfo.close()
        print "write_batchfile Called inside tsuite"
#-------------------------------------------------------------------
#--------------------------- Python TestCase function Definition ----------------------------------#

    def writeTestCaseDef(self,testcasenumber):
            '''
            Description:This function starts to write new test case in .py file
            it writes test description ,test case requirment id to py file.
            '''
            test_name      = self.get_testname(testcasenumber)
            test_case_desc = self.get_testdescription(testcasenumber)
            test_case_reqs = self.get_testrequirementid(testcasenumber)

            self.fo.write("\n#######################")
            self.fo.write("\n## Test Case %s       ##" %(testcasenumber+1))
            self.fo.write("\n#######################"+ '\n' + '\n')
            self.fo.write('def test_%s():\n' %(str(testcasenumber)))


            self.TD = test_name.replace('\'','\"')  #in Test Name Statement replace ' with " for indentation
            self.TD = self.TD.replace('\n',' ')   #in Test Name Statement replace \n with ' ' for indentation
            self.TN = test_case_desc.replace('\n',' ')  #in Test Description Statement replace \n with ' ' for indentation
            self.TN = self.TN.replace('\'','\"')  #in Test Description Statement replace ' with " for indentation

            self.fo.write("    test_case_name = 'Test Case %s: %s'\n" % (testcasenumber+1,self.TD))#Write Test Name
            self.fo.write("    test_case_desc = '%s'\n" %self.TN) #Write Test Description
            self.fo.write("    test_case_reqs = '%s'\n" % test_case_reqs.replace('\n',' ') ) #Write Test Requirment ID
            self.fo.write("    print test_case_name\n\n")
            self.fo.write("    report.add_test_case(test_case_name, test_case_desc, test_case_reqs)\n\n")


#---------------------------- Generate Copyright header -------------------------------------------#
    def writeCopyright(self):
        '''
        Description: This Function import packages in .py file
        '''
        global div
        div = '======================================='
        self.fo.write('#' + div * 4)
        self.fo.write("\n#")
        self.fo.write("\n# Integration Test script file")
        self.fo.write("\n# (c) Copyright 2012 Lear Corporation ")
        self.fo.write("\n#")
        self.fo.write('\n#' + div * 4 + '\n')

        self.fo.write("\nimport sys")
        self.fo.write("\nimport os")
        self.fo.write("\nimport time")
        self.fo.write("\nimport Tkinter as tk")
        self.fo.write("\nimport tkMessageBox")

#---------------------------------------------------------------------------------------------------------

#---------------------------- Generate Path Settings -----------------------------------------------#
    def writePathSettings(self):
        '''
        Description: This function write all project related path to py file.
        Example:
             Tools_PATH,CODE_PATH
        creates object for t32,com
        '''
        self.fo.write("\n\nREPORT_API_PATH = os.path.abspath(r'../../../Libs/report')")
        self.fo.write("\nCOM_API_PATH = os.path.abspath(r'../../../Libs/com')\n")

        self.fo.write("\n\n# Adding paths for loading correctly .py libraries")
        self.fo.write("\nsys.path.append(REPORT_API_PATH)")
        self.fo.write("\nsys.path.append(COM_API_PATH)")

        self.fo.write("\n\nfrom report import *")
        self.fo.write("\nfrom com import *")
        self.fo.write("\nfrom openpyxl import *")

        self.fo.write("\nextrasfunc_path = os.path.abspath(r'../../../Testsuite/')")
        self.fo.write("\nsys.path.insert(0,extrasfunc_path)")
        self.fo.write("\nfrom Extras import *")

#--------------------------------------------------------------------------------------------------
#---------------------------- Generate Report Settings ---------------------------------------------#
    def writeReportSettings(self):
        '''
        Description:This function write all extracted values(from excel sheet) regarding the report header in .py file
        '''
        self.fo.write("\n\n\n# Report Header Variables")
        self.fo.write("\nAUTHOR = '%s'" %self.get_sheetauthor())
        self.fo.write("\nTLA = '%s'" % self.get_sheettitle() )
        self.fo.write("\nPROJECT_NAME = '%s'" % self.get_sheetproject() )
        self.fo.write("\nHW_VERSION = '%s'" %  self.get_sheethardwareversion())
        self.fo.write("\nNETWORK_TYPE = '%s'" % self.get_sheetnetwork())
        self.fo.write("\nSW_VERSION = '%s'" % self.get_sheetsoftwareversion())
        self.fo.write("\n\n# Create the report object, specifying the test data")
        self.fo.write("\nreport = HTMLReport(TLA, PROJECT_NAME, SW_VERSION, HW_VERSION, NETWORK_TYPE, AUTHOR)")
#--------------------------------------------------------------------------------------------------
#--------------------------------Open Workbook/worksheet-------------------------------------------
    def writewbinit(self):

        self.fo.write("\nbook = load_workbook(filename = '%s')"%self.get_workbookpath())
        self.fo.write("\nxl_sheet = book.get_sheet_by_name('%s')" %self.get_worksheet())
#---------------------------------------------------------------------------------------------------
#--------------------------------required line to save the modified xl data ----------------------------------------
    def writexlsave(self):
        self.fo.write("book.save('%s'+'/'+'result.xlsx')\n"%self.testcaseDirectory)
#---------------------------------------------------------------------------------------------------
#-----------Writes the code required fot Actual response part of the excel sheet---------------------
    def writexlrespfunction(self):
        self.fo.write("\ndef xl_response(print_row,print_column):")
        self.fo.write("\n    response_str = ''")
        self.fo.write("\n    response_str = 'Response :' + canObj.dgn.req_info_raw().split('Rsp:')[1]")
        self.fo.write("\n    xl_sheet.cell(row=print_row,column=print_column,value=str(response_str))\n")


        self.fo.write("\n    return str(response_str)")

#---------------------------------------------------------------------------------------------------
#---------------------------Wrtie Channel setting to the py file------------------------------------
    def writeChannelSettings(self):
        '''
        Description:This for Loop Extract can channel baud rate,Channel ID,LDf,DBC.
        it Checks CAN Access req. and according to that set channel
        '''
        self.fo.write("\n\n")
        self.fo.write("#################################################################\n")
        self.fo.write("##               Set CAN,LIN,FR Channels                       ##\n")
        self.fo.write("#################################################################\n")
        self.fo.write("\ncom = Com('VECTOR')")
        self.fo.write("\ncanObj = com.open_can_channel(int(%s),int(%s))" % (self.get_sheetCANchannel(), self.get_sheetCANchannelBR()))
#---------------------------------------------------------------------------------------------------
#---------------------------- Generate Precondition Statements -------------------------------------#

    def processTypePERIODIC_TP(self,testcasenumber,teststepnumber):
        self.fo.write("    #######################################\n")  #Print row number of excel sheet
        self.fo.write("    #Code block generated for row no = %s #\n" %self.writerow_number)
        self.fo.write("    #######################################\n\n")

        self.fo.write("    ################################\n")  # Reset By Diagnostics
        self.fo.write("    ## PERIODIC_TP SWITCHING      ##\n")
        self.fo.write("    ################################\n\n")

        if(self.get_testconditions(testcasenumber,teststepnumber)=='ON'):
            self.fo.write("\n    canObj.dgn.start_periodic_tp()" )
            self.fo.write("\n    print 'PERIODIC_TP -->> ON'")
        elif(self.get_testconditions(testcasenumber,teststepnumber)=='OFF'):
            self.fo.write("\n    canObj.dgn.stop_periodic_tp()\n")
            self.fo.write("\n    print 'PERIODIC_TP -->> OFF'")
        else:
            print "\n.py Generation related to Periodic TP failed\n"

#---------------------------------------------------------------------------------------------------
#---------------------------- Generate Precondition Statements -------------------------------------#
    def writePreconditions(self):
        self.fo.write("\n\n")
        self.fo.write("#################################################################\n")
        self.fo.write("##      Load dbc,Periodic Tester Present,Periodic NM message   ##\n")
        self.fo.write("#################################################################\n")
        self.fo.write("\ncanObj.load_dbc('%s')" % self.get_dbcpath())
        self.fo.write("\ncanObj.send_cyclic_frame('BCCM_NM51F',100)")
        self.fo.write("\ncanObj.dgn.ecu_reset(0x01)" )
        self.fo.write("\ntime.sleep(1)\n" )
#---------------------------------------------------------------------------------------------------
#---------------------------- Generate GetActualResponseFrames() Function --------------------------#
    def writeGetActualRespDef(self):
        self.fo.write("\ndef GetActualResponseFrames():\n")
        self.fo.write("    response_str = ''\n")
        self.fo.write("    response_str = canObj.dgn.req_info_raw().split('Rsp:')[1]\n")
        self.fo.write("    response_str = response_str.replace('[','')\n")
        self.fo.write("    response_str = response_str.replace(']','')\n")
        self.fo.write("    response_str = response_str.replace(' ','')\n")
        self.fo.write("    return response_str\n\n\n")
#---------------------------------------------------------------------------------------------------
#---------------------------- Generate InvokeMessageBox() Function ---------------------------------#
    def writeInvokeMsgBoxDef(self):
        self.fo.write("\ndef InvokeMessageBox(MessageStr):\n")
        self.fo.write("    MessageStr = MessageStr")
        self.fo.write(r" + ")
        self.fo.write(r""" "\nPress OK after performing the action." """)
        self.fo.write("\n")
        self.fo.write("    root = tk.Tk()\n")
        self.fo.write("    root.withdraw()\n")
        self.fo.write("""    root.attributes("-topmost", True)\n""")
        self.fo.write("""    tkMessageBox.showinfo("Manual Input Required", MessageStr)\n""")
        self.fo.write("    root.destroy()\n")
#---------------------------------------------------------------------------------------------------
#-------------------------process DIAG_EVAL FOR special handling------------------------------------
# refet to extra.py in the TEstsuite for the function def
#refet to extra.py in the TEstsuite for the function def
    def processTypeDIAG_EVAL(self,testcasenumber,teststepnumber):
        self.fo.write("    #######################################\n")  #Print row number of excel sheet
        self.fo.write("    #Code block generated for row no = %s  #\n" %self.writerow_number)
        self.fo.write("    ##################################### #\n\n")



#---------------------------------------------------------------------------------------------------

#------------------------------ Process DIAG type test steps ---------------------------------------#
    def processTypeDIAG(self,testcasenumber,teststepnumber):
        #Extract values from excel sheet

        test_step_Desc  = self.get_teststepdescription(testcasenumber, teststepnumber)#Description
        Comments_string = self.get_comments(testcasenumber, teststepnumber) #Comments
        Expec_res_raw   = self.get_expectedresult(testcasenumber,teststepnumber)     #Expected value of Test Step
        Expec_res_raw  = Expec_res_raw.replace('\n',' ')
        Expec_res_raw   = Expec_res_raw.split('.')[0]
        Expec_res  = Expec_res_raw
        Expec_res  = Expec_res.replace('\n',' ')
        Expec_res  = Expec_res.replace(' ','')
        Expec_res  = Expec_res.upper()

        Diag_Service=self.get_testconditions(testcasenumber, teststepnumber)
        Diag_Service=Diag_Service.split('.')[0]
        Diag_Service = Diag_Service.replace(" ", "")
        print_row = str(self.writerow_number)

        if Diag_Service[0:2]=='11': # Check for diagnostic service ID is "RESET"

            PID=Diag_Service[2:4] #Extract Reset Type

            self.fo.write("    #######################################\n")  #Print row number of excel sheet
            self.fo.write("    #Code block generated for row no = %s  #\n" %self.writerow_number)
            self.fo.write("    ##################################### #\n\n")

            self.fo.write("    ################################\n")  # Reset By Diagnostics
            self.fo.write("    ## Reset By Diagnostics  ##\n")
            self.fo.write("    ################################\n\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            self.fo.write("    canObj.dgn.ecu_reset(%s)\n" % ('0x'+PID))
            self.fo.write("    time.sleep(1)\n" )

            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("\n")
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Reset Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
    #self.fo.write("\n%d" %self.writerow_number)
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Unable to reset.Test Fails:!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string))#Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#
        elif Diag_Service[0:2]=='31': # Check for diagnostic service ID is "ROUTINE ID"

            PID = Diag_Service[2:4]          #Extract PID Number



            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #Read DID By Diagnostics
            self.fo.write("    ##          ROUTINES          ##\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if(PID == ''):
                self.fo.write("    canObj.dgn.iso.net.send_request([0x31, ], 'PHYSICAL')\n")

            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x31")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")

            self.fo.write("    time.sleep(1)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Routine Execution Succesful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Routine Execution Fails:!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#
        elif Diag_Service[0:2]=='22': # Check for diagnostic service ID is "READ DID"

            PID='0x'+Diag_Service[2:6] #Extract PID Number



            if len(Diag_Service) > 6:
                Extra_Parameter = '0x'+Diag_Service[6:8]

            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #Read DID By Diagnostics
            self.fo.write("    ##          Read DID          ##\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if len(Diag_Service) > 6:
                self.fo.write("    canObj.dgn.read_DID_Len_W(%s,%s) \n" % (PID,Extra_Parameter))
            else:
                self.fo.write("    canObj.dgn.read_did(%s) \n" % (PID))
            self.fo.write("    time.sleep(0.3)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Fails!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report

            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#


        elif Diag_Service[0:2]=='10': # Check for diagnostic service ID is "Session CTRL DID"

            PID=Diag_Service[2:4] #Extract Session Number



            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
            self.fo.write("    ##          Session Ctrl  #\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if(len(Diag_Service) <= 4):
                if PID =='01':
                    self.fo.write("    canObj.dgn.default_session() \n") #evaluation of default session
                elif PID =='02':
                    self.fo.write("    canObj.dgn.programming_session() \n") #evaluation of programming session
                elif PID =='03':
                    self.fo.write("    canObj.dgn.extended_session() \n") #evaluation of extended session
                elif PID =='':
                    self.fo.write("    canObj.dgn.iso.net.send_request([0x10, ], 'PHYSICAL') \n") #evaluation of No session subfunction
                else :
                    self.fo.write("    canObj.dgn.iso.service_0x10(%s)\n" % ('0x'+PID)) #evaluation of internal session
            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x10")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")

            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    time.sleep(0.3)\n" )
                self.fo.write("\n")
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Failed!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#
        elif Diag_Service[0:2]=='27': # Check for diagnostic service ID is "Security Access ID"

            PID=Diag_Service[2:4] #Extract Session Number



            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #Security Access By Diagnostics
            self.fo.write("    ##          Security Access  #\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if ("Send" in TD) and ("Wrong" in TD) and ("Key" in TD):
                self.fo.write("    canObj.dgn.security_access_wrong_key(%s)\n" % ('0x'+PID))
            else:
                self.fo.write("    canObj.dgn.security_access(%s)\n" % ('0x'+PID))
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("\n")
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Failed!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#

        elif Diag_Service[0:2]=='19': # Check for diagnostic service ID is "READ DTC Information"

            PID=Diag_Service[2:4] #Extract PID Number


            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #READ DTC Information
            self.fo.write("    ##    READ DTC Information    ##\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if(PID == ''):
                self.fo.write("    canObj.dgn.iso.net.send_request([0x19, ], 'PHYSICAL')\n")
            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x19")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")

            self.fo.write("    time.sleep(1)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Read DTC Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Read DTC Failed!!'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#

        elif Diag_Service[0:2]=='2E': # Check for diagnostic service ID is "write DID"

            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ################################\n")  #Hard Reset By Diagnostics
            self.fo.write("    ##          Write DID          #\n")
            self.fo.write("    ################################\n")

        elif Diag_Service[0:2]=='85': # Check for diagnostic service ID is "Control DTC Setting"

            PID = Diag_Service[2:4] #Extract Subfunction


            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ###################################\n")  #Clear Diagnosice Information
            self.fo.write("    ##       Control DTC Setting      ##\n")
            self.fo.write("    ###################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if(len(Diag_Service) <= 4):
                if(PID == ''):
                    self.fo.write("    canObj.dgn.iso.net.send_request([0x85, ], 'PHYSICAL')\n")
                else:
                    self.fo.write("    canObj.dgn.control_dtc_setting_custom(%s)\n" % ('0x'+PID))
            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x85")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")


            self.fo.write("    time.sleep(1)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Failed.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#
        elif Diag_Service[0:2]=='14': # Check for diagnostic service ID is "Clear Diagnosice Information"

            PID = Diag_Service[2:4] #Extract Subfunction

            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ###################################\n")  #Clear Diagnosice Information
            self.fo.write("    ## Clear Diagnostics Information  ##\n")
            self.fo.write("    ###################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")

            if(PID == ''):
                self.fo.write("    canObj.dgn.iso.net.send_request([0x14, ], 'PHYSICAL')\n")
            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x14")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")


            self.fo.write("    time.sleep(1)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found

                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Failed.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
#

        elif Diag_Service[0:2]=='3E': # Check for diagnostic service ID is "Tester Present"

            PID=Diag_Service[2:4] #Extract PID Number

            self.fo.write("\n    #######################################")  #Print row number of excel sheet
            self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
            self.fo.write("\n    ##################################### #\n")

            self.fo.write("\n    ###################################\n")  #Tester Present
            self.fo.write("    ##         Tester Present         ##\n")
            self.fo.write("    ###################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")


            if(len(Diag_Service) <= 4):
                if(PID == '00'):
                    self.fo.write("    canObj.dgn.tester_present()\n")
                elif(PID == '80'):
                    self.fo.write("    canObj.dgn.tester_present_spr()\n")
                elif(PID == ''):
                    self.fo.write("    canObj.dgn.iso.net.send_request([0x3E, ], 'PHYSICAL')\n")
                else:
                    self.fo.write("    canObj.dgn.tester_present_custom(%s)\n" % ('0x'+PID))
            else:
                self.fo.write("    canObj.dgn.iso.net.send_request([0x3E")

                for i in range(2,len(Diag_Service),2):
                    self.fo.write(" ,%s" % ('0x'+ Diag_Service[i:i+2])) #Invalid Length

                self.fo.write("], 'PHYSICAL') \n")


            self.fo.write("    time.sleep(1)\n" )
            self.fo.write("\n")
            if(self.get_expectedresult(testcasenumber, teststepnumber).find("FUNC")<0 ):#if string not found
                self.fo.write("    Expec_res = '%s'\n"%Expec_res)
                self.fo.write("    Actual_res = GetActualResponseFrames()\n")
                self.fo.write("\n")
                self.fo.write("    if Expec_res == Actual_res[0:len(Expec_res)]: \n" )
                self.fo.write("          test_step_Result = True\n")
                self.fo.write("          test_step_Comment ='Test Successful.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("    else: \n" )
                self.fo.write("          test_step_Result = False\n")
                self.fo.write("          test_step_Comment ='Test Failed.'\n")
                self.fo.write("          xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n")
                self.fo.write("    test_step_ResponseStr = canObj.dgn.req_info_raw()\n")
                self.fo.write("\n")
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, test_step_ResponseStr,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
            else:
                self.fo.write("\n    #refer to extra.py in the TEstsuite for the function def\n")
                funct_name=self.get_expectedresult(testcasenumber, teststepnumber)
                funct_name = funct_name.split(':')[1]
                funct_name = funct_name.replace('"','')
                self.fo.write("\n    Actual_resp=GetActualResponseFrames()")
                self.fo.write("\n    if(Actual_resp[0:2]!='7F'):")
                self.fo.write("\n        ret=%s(Actual_resp)"%funct_name)
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n        ret=0")
                self.fo.write("\n    if(ret==1):")
                self.fo.write("\n        test_step_Result = True")
                self.fo.write("\n        test_step_Comment ='Test Sucessful.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='OK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write("\n    else:")
                self.fo.write("\n        test_step_Result = False")
                self.fo.write("\n        test_step_Comment ='Test Fails.'")
                self.fo.write("\n        xl_sheet.cell(row=%s,column=%s,value='NOK')\n"%(self.writerow_number,self.testResCol))
                self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result, Actual_resp,'%s',test_step_Comment + '\n' + '%s')"%(Expec_res_raw,Comments_string)) #Report
        self.fo.write("\n    xl_response(%s,%s)\n"%(self.writerow_number,self.actResCol))

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------ Process POPUP type test steps ---------------------------------------#
    def processTypePOPUP(self,testcasenumber, teststepnumber):

        print_row = str(self.writerow_number)

        self.fo.write("\n    #######################################")  #Print row number of excel sheet
        self.fo.write("\n    #Code block generated for row no = %s  #"%print_row)
        self.fo.write("\n    ##################################### #\n")

        test_step_Desc = self.get_teststepdescription(testcasenumber, teststepnumber) #Description

        TD = test_step_Desc.replace('\n',' ')
        TD = TD.replace('\'','\"')

        if(test_step_Desc == ''): # Check For Proper Data Entry in Excel sheet
            print("\n**Error occured.")
            print("\nTest Description is not provided.")
            print("\nCheck Row no:")+str(self.writerow_number)+"\n"
            print("\nCheck column number:")+str(self.testDescCol)+"\n"
            sys.exit()
        else:
            self.fo.write("\n    ################################\n")  #Session Ctrl By Diagnostics
            self.fo.write("    ##          Message Pop-up  #\n")
            self.fo.write("    ################################\n")

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    InvokeMessageBox(test_step_Desc)\n" )

        self.fo.write("\n    print '%s'\n"%self.get_teststepdescription(testcasenumber, teststepnumber))
        self.fo.write(r"    report.add_test_step(test_step_Desc,True,'','')") #Report
        self.fo.write("\n")
        self.fo.write("\n")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------ Process DELAY type test steps ---------------------------------------#
    def processTypeDELAY(self,testcasenumber, teststepnumber):
        print_row = str(self.writerow_number)

        description = self.get_teststepdescription(testcasenumber, teststepnumber) #Description
        time = self.get_testconditions(testcasenumber, teststepnumber) #Time
        conditn_Val = self.get_expectedresult(testcasenumber, teststepnumber)#Cyclic Time

        if(conditn_Val != 'None'): # Check For Proper Data Entry in Excel sheet
            print "\n**Error occured."
            print "\nNo Need of Expected Result for DELAY type test step"
            print "\nCheck Row no: " + str(print_row)
            print "\nCheck Column no: " + str(self.expResCol)
            print "Value at this cell is %s"%str(conditn_Val)
            sys.exit()

        if(description ==''): # Check For Proper Data Entry in Excel sheet
            print "\n**Error occured."
            print "\nTest Description is not provided."
            print "\nCheck Row no:" + str(print_row)
            print "\nCheck Column no:" + str(self.testDescCol)
            sys.exit()

        if(time == ''): #Time should not be blank
            print "\n**Error occured."
            print "\nProvide time(in sec) for delay"
            print "\nCheck Row no: " + str(print_row)
            print "\nCheck Column no:" + str(self.testCondCol)
            sys.exit()


        self.fo.write("\n    #######################################")  #Print Row number
        self.fo.write("\n    #Code block generated for row no = %s #"%print_row)
        self.fo.write("\n    #######################################\n")

        TD = description.replace('\n',' ') #Remove if new line is added in test description
        TD = TD.replace('\'','\"')
        self.fo.write("    test_step_Desc='%s'\n" %TD)
        self.fo.write("    print test_step_Desc\n")
        self.fo.write("    time.sleep(%s)"%time)
        self.fo.write("\n")

        self.fo.write(r"    report.add_test_step(test_step_Desc,True,'','')") #Report
        self.fo.write("\n")
        self.fo.write("\n")
#-----------------------------------------------------------------------------------------------------------------------------

#------------------------------ Process CANSIGNAL type test steps ---------------------------------------#
    def processTypeCANSIGNAL(self,testcasenumber, teststepnumber):
        #Extract values from excel sheet
        print_row = str(self.writerow_number)
        test_step_Desc = self.get_teststepdescription(testcasenumber, teststepnumber) #Description
        Comments_string = self.get_comments(testcasenumber, teststepnumber) #Comments


        Can_Signal_Details=self.get_testconditions(testcasenumber, teststepnumber)
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
            self.fo.write("\n    ################################\n")
            self.fo.write("    ##          Send CAN signal  #\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")
            self.fo.write("    canObj.send_cyclic_frame('%s',10) \n" %(Can_Message))
            #self.fo.write("    canObj.set_signal('%s',%s) \n" %(int(1),Can_Signal,Can_Signal_Value))

            self.fo.write("    canObj.set_signal('%s',[" %(Can_Signal))
            for i in range(len(Can_Signal_Value_List)):
                if i == (len(Can_Signal_Value_List)-1):
                    self.fo.write("%s" %Can_Signal_Value_List[i])
                else:
                    self.fo.write("%s," %Can_Signal_Value_List[i])

            self.fo.write("]) \n")
            self.fo.write("    time.sleep(0.5)\n" )

            self.fo.write("\n")
            self.fo.write("    Expec_res = '%s'\n"%Expec_res)
            self.fo.write("    Actual_res = canObj.get_signal('%s','%s')\n"%(Can_Signal,Can_Message))
            self.fo.write("    Actual_res = str(hex(Actual_res))\n")
            self.fo.write("    Actual_res = Actual_res.replace('0x','')\n")
            self.fo.write("    Actual_res = Actual_res.replace('L','')\n")
            self.fo.write("    Actual_res = Actual_res.replace(' ','')\n")
            self.fo.write("    Actual_res = Actual_res.upper()\n")
            self.fo.write("\n")

            self.fo.write("    if Expec_res == Actual_res: \n" )
            self.fo.write("          test_step_Result = True\n")
            self.fo.write("          test_step_Comment ='CAN signal set Successfully.'\n")
            self.fo.write("    else: \n" )
            self.fo.write("          test_step_Result = False\n")
            self.fo.write("          test_step_Comment ='CAN signal could not be set.'\n")
            self.fo.write("    test_step_ResponseStr = str(canObj.get_frame(canObj.find_frame_id('%s')))\n"%(Can_Message))
            self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result,'%s.%s='+Actual_res,'%s',test_step_Comment + '\n' + '%s')"%(Can_Message,Can_Signal,Test_Condition,Comments_string)) #Report
            self.fo.write("\n    print '%s'\n"%self.get_teststepdescription(testcasenumber, teststepnumber))
        else:
            print "Test Condition entered is incorrect !!"

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------ Process CANFRAME type test steps ---------------------------------------#
    def processTypeCANFRAME(self,testcasenumber, teststepnumber):
        #Extract values from excel sheet
        test_step_Desc = self.get_teststepdescription(testcasenumber, teststepnumber) #Description
        Comments_string = self.get_comments(testcasenumber, teststepnumber) #Comments
        Expec_res=self.get_expectedresult(testcasenumber, teststepnumber) #Expected value of Test Step

        Expec_res=Expec_res.split('.')[0]
        Expec_res=Expec_res.replace('\n',' ')
        Expec_res=Expec_res.replace(' ','')
        Expec_res=Expec_res.upper()

        Can_Frame_Details=self.get_testconditions(testcasenumber, teststepnumber)
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
            self.fo.write("\n    ################################\n")
            self.fo.write("    ##          Send CAN Frame  #\n")
            self.fo.write("    ################################\n")

            TD = test_step_Desc.replace('\n',' ')
            TD = TD.replace('\'','\"')

            self.fo.write("    test_step_Desc='%s'\n" %TD)  #Test step Description
            self.fo.write("    test_step_Result = False\n" )
            self.fo.write(r"    test_step_Comment = '\n'" )
            self.fo.write("\n")
            self.fo.write(r"    test_step_ResponseStr = '\n'" )
            self.fo.write("\n")
            self.fo.write("\n")
            self.fo.write("    canObj.write_frame(%s, %s, [" %(Can_FrameID,len(Can_Frame_Value_List)))
            for i in range(len(Can_Frame_Value_List)):
                if i == (len(Can_Frame_Value_List)-1):
                    self.fo.write("%s" %Can_Frame_Value_List[i])
                else:
                    self.fo.write("%s," %Can_Frame_Value_List[i])
            self.fo.write("]) \n")
            self.fo.write("    time.sleep(0.5)\n" )
            self.fo.write(r"    report.add_test_step(test_step_Desc,test_step_Result,'%s' + 'Comment' + '\n' + '%s')"%(Test_Condition,Comments_string)) #Report
            self.fo.write("\n    print '%s'\n"%self.get_teststepdescription(testcasenumber, teststepnumber))
        else:
            print "Test Condition entered is incorrect !!"
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------- Generate EndTest Function ---------------------------------------#
    def writeEndTestDef(self):
        self.fo.write("\n\ndef endTest():")
        self.fo.write("\n    report.generate_report()")
        self.fo.write("\n    canObj.dgn.iso.net.log_file = report.get_log_dir()")
        self.fo.write("\n    canObj.dgn.save_logfile()")
        self.fo.write("\n    canObj.dgn.stop_periodic_tp()")
        self.fo.write("\n    canObj.stop_cyclic_frame('BCCM_NM51F')")
        self.fo.write("\n")
        self.fo.write(r"    print '\nScript Execution Finished !!'")
        self.fo.write("\n")
        self.fo.write("\n    com.exit()\n\n\n\n")
#--------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------ Generate Calling of Test Functions ------------------------------------------#
    def writeCallingOfTestcases(self):
        self.fo.write("\n#############################")
        self.fo.write("\n## Execute the test cases  ##")
        self.fo.write("\n#############################"+ '\n' + '\n')

        #Start Calling all Test Case
        Cnt=0
        while Cnt<self.get_totaltests():
            self.fo.write("test_%s()\n" %Cnt)
            Cnt+=1
            self.fo.write("time.sleep(1)\n")
#---------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------- Finish writing the Python file -------------------------------------------------#
    def closePythonFile(self):
        self.fo.write("\n# Perform End actions i.e Save log files, Generate Report etc..")
        self.fo.write("\nendTest()")
        self.fo.write("\nos.startfile('%s'+'/'+'result.xlsx')\n"%self.testcaseDirectory)
        self.fo.close()

#------------------------------------------------------------------------------------------------------------------------------------





