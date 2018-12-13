'''
====================================================================
Library for reporting a test sequence
(C) Copyright 2014 Lear Corporation
====================================================================
'''
__author__  = 'Jesus Fidalgo'
__version__ = '2.0.0'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
2.0.0 Not used libxml anymore.
      Report format is XML + XSL, not HMTL anymore.
      API change: add_test method is now add_test_case.
      API change: add_test_result method is now add_test_step.
      API change: add_test_step method does not need test_case_name as parameter.
      API new method: add_info_step for info steps inside a test case.
      Integration Test Report and Unit Test Report can be now used.
1.4.1 Report file name simplified, tlaVer and SvnRev removed from file name.
1.4.0 Updated XML structure according to XML standards.
      Report name generated according to SQA IT standard.
1.3.1 Add backslash to xsl_path in method generate_report.
1.3.0 Visual redesign.
      Fixed naming of XSL elements for TestCases and TestSteps.
1.2.0 Added test case field for requirements.
      Generates also a XML report file for parsing more easily the results.
1.1.0 Added NOT_TESTED case.
      Method __init__ accepts more parameters.
1.0.1 Added TLA string to indicate the SW component under test.
1.0.0 Inital version.
'''

import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime
import shutil
import os


# Version of the IT XML structure. Increase it if modified.
IT_XML_VERSION = '1.0.0'
# Version of the UT XML structure. Increase it if modified.
UT_XML_VERSION = '1.0.0'
# SQA project ID
PROJECT_ID = '000'


class Report(object):
    '''
    This class is the base class for the UTReport and ITReport classes.
    It provides common methods for adding a test case, a test step, and info step, besides some
    other private methods used internally for generating report stats or prtiffying the XML report file.
    '''

    def __init__(self):
        '''
        Description: Constructor. Creates several common tags for any kind of report.
        '''
        self.root = ET.Element('TEST_REPORT')
        self.coll = ET.SubElement(self.root, 'Collection')
        ttool = ET.SubElement(self.root, 'TestTool')
        ttool.text = 'LATTE'
        now = datetime.datetime.now()
        datenow = ET.SubElement(self.root, 'DateTime')
        datenow.text = now.strftime('%d-%m-%Y %H:%M')
        self.n_test_cases = 0
        self.tt_oks = 0
        self.tt_noks = 0
        self.tt_nts = 0


    def _prettify(self, xsl_filename):
        '''
        Description: Takes the XML struct and generates a string with the tags corrrectly tabbed.
        '''
        rough_string = ET.tostring(self.root, 'utf-8')
        rough_string = '<?xml-stylesheet type="text/xsl" href="' + str(xsl_filename) + '" ?>' + rough_string
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent = '    ')


    def _add_test_case_stats(self):
        '''
        Description: Generates tags with the total stats of the test case.
        '''
        if self.n_test_cases > 0:
            # Generate latest test case stats
            tc_oks_tag = ET.SubElement(self.tc, 'TestStepsOK')
            tc_oks_tag.text = str(self.tc_oks)
            tc_noks_tag = ET.SubElement(self.tc, 'TestStepsNOK')
            tc_noks_tag.text = str(self.tc_noks)
            tc_nts_tag = ET.SubElement(self.tc, 'TestStepsNT')
            tc_nts_tag.text = str(self.tc_nts)
            tc_tt_tag = ET.SubElement(self.tc, 'TestsTotal')
            tc_tt_tag.text = str(self.tc_oks + self.tc_noks + self.tc_nts)
        else:
            # First test case, do not generate stats
            self.n_test_cases += 1


    def _add_total_stats(self):
        '''
        Description: Generates tags with the total stats of the report.
        '''
        tt_oks_tag = ET.SubElement(self.root, 'TotalTestStepsOK')
        tt_oks_tag.text = str(self.tt_oks)
        tt_noks_tag = ET.SubElement(self.root, 'TotalTestStepsNOK')
        tt_noks_tag.text = str(self.tt_noks)
        tt_nts_tag = ET.SubElement(self.root, 'TotalTestStepsNT')
        tt_nts_tag.text = str(self.tt_nts)
        tt_tt_tag = ET.SubElement(self.root, 'TotalTestSteps')
        tt_tt_tag.text = str(self.tt_oks + self.tt_noks + self.tt_nts)


    def add_test_case(self, title, description='', reqs=''):
        '''
        Description: Adds a new test case (also called test scenario) to the report.
        Parameter 'title' is a string with the name of the test case.
        Parameter 'description' is optional, a string with a short description of the test case.
        Parameter 'reqs' is optional, a string with the requirements tested in this test case.
        If there are no requirements tested, just leave it as an empty string.

        Note: This method is available for both UTReport and ITReport classes.

        Example:
            it_report = ITReport('FrontWiper', '1.0.0', 'MY_2015', '5271', 'HW6.1', 'John Doe')
            test_case_name = 'Front Wiper low speed'
            test_case_desc = 'Testing low speed in different key positions'
            test_case_reqs = 'Req_123v2, Req_134'
            it_report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
        '''
        self._add_test_case_stats()
        self.tc_oks = 0
        self.tc_noks = 0
        self.tc_nts = 0
        self.tc = ET.SubElement(self.coll, 'Test')
        tc_title = ET.SubElement(self.tc, 'TestCase')
        tc_desc = ET.SubElement(self.tc, 'TestDescription')
        tc_reqs = ET.SubElement(self.tc, 'TestRequirements')
        tc_title.text = title
        tc_desc.text = description
        tc_reqs.text = reqs


    def add_test_step(self, description, result=None, actual='',expected='',comment=''):
        '''
        Description: Adds a new test step in the current test case.
        Parameter 'description' is a string with a short description.
        Parameter 'result' is optional, a boolen indicating the result of the test step.
        A True will generate a OK test, a False will generate a NOK test, and None will generate NOT_TESTED.
        Parameter 'comment' is optional, a string with any interesting comment.

        Note: This method is available for both UTReport and ITReport classes.

        Example:
            it_report = ITReport('FrontWiper', '1.0.0', 'MY_2015', '5271', 'HW6.1', 'John Doe')
            test_case_name = 'Front Wiper low speed'
            test_case_desc = 'Testing low speed in different key positions'
            test_case_reqs = 'Req_123v2, Req_134'
            it_report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
            # Adding a test step
            result = check_act_key_out()
            test_step_description = 'Checking here Front Wiper low speed is not activated in key out'
            it_report.add_test_step(test_step_description, result)
        '''
        ts = ET.SubElement(self.tc, 'TestStep')
        ts_desc = ET.SubElement(ts, 'Description')
        ts_result = ET.SubElement(ts, 'Result')
        ts_actual = ET.SubElement(ts, 'Actual')
        ts_expected = ET.SubElement(ts, 'Expected')
        ts_comment = ET.SubElement(ts, 'Comment')
        ts_desc.text = description
        ts_comment.text = comment
        ts_actual.text = actual
        ts_expected.text = expected
        if result == True:
            ts_result.text = '1'
            self.tc_oks += 1
            self.tt_oks += 1
        elif result == False:
            ts_result.text = '0'
            self.tc_noks += 1
            self.tt_noks += 1
        else:
            ts_result.text = '5'
            self.tc_nts += 1
            self.tt_nts += 1


    def add_info_step(self, description, comment=''):
        '''
        Description: Adds a new info step in the current test case.
        Parameter 'description' is a string with a short description.
        Parameter 'comment' is optional, a string with any interesting comment.

        Note: This method is available for both UTReport and ITReport classes.

        Example:
            it_report = ITReport('FrontWiper', '1.0.0', 'MY_2015', '5271', 'HW6.1', 'John Doe')
            test_case_name = 'Front Wiper low speed'
            test_case_desc = 'Testing low speed in different key positions'
            test_case_reqs = 'Req_123v2, Req_134'
            it_report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
            # Adding a info step
            it_report.add_info_step('Lear SW internal part number is LEAR-V1.31.217')
        '''
        ts = ET.SubElement(self.tc, 'TestStep')
        ts_desc = ET.SubElement(ts, 'Description')
        ts_result = ET.SubElement(ts, 'Result')
        ts_comment = ET.SubElement(ts, 'Comment')
        ts_desc.text = description
        ts_comment.text = comment
        ts_result.text = '2'



class ITReport(Report):
    '''
    This class generates an XML data structure containing the results of an integration test.

    Note: This class derives from Report class above. So public methods add_test_case, add_test_step and
    add_info_step are also available in this ITReport class.

    This is the XML structure:

    <TEST_REPORT>
        <Collection>
            <Test>
                <TestCase>Test Case 1 Title</TestCase>
                <TestDescription>Test Case 1 Desciption</TestDescription>
                <TestRequirements>Reqs tested: None</TestRequirements>
                <TestStep>
                    <Description>Test step 1 description here</Description>
                    <Result>1</Result>
                    <Comment>Optional comment here</Comment>
                </TestStep>
                <TestStep>
                    <Description>Test step 2 description here</Description>
                    <Result>1</Result>
                    <Comment/>
                </TestStep>
                <TestStep>
                    <Description>Info step description here</Description>
                    <Result>2</Result>
                    <Comment/>
                </TestStep>
                <TestStepsOK>2</TestStepsOK>
                <TestStepsNOK>0</TestStepsNOK>
                <TestStepsNT>0</TestStepsNT>
                <TestsTotal>2</TestsTotal>
            </Test>
            <Test>
                <TestCase>Test Case 2 Title</TestCase>
                <TestDescription>Test Case 2 Desciption</TestDescription>
                <TestRequirements>Reqs tested: None</TestRequirements>
                <TestStep>
                    <Description>Test step 1 description here</Description>
                    <Result>0</Result>
                    <Comment/>
                </TestStep>
                <TestStep>
                    <Description>Test step 2 description here</Description>
                    <Result>0</Result>
                    <Comment/>
                </TestStep>
                <TestStepsOK>0</TestStepsOK>
                <TestStepsNOK>2</TestStepsNOK>
                <TestStepsNT>0</TestStepsNT>
                <TestsTotal>2</TestsTotal>
            </Test>
        </Collection>
        <TestTool>LATTE</TestTool>
        <DateTime>21-12-2013 13:35</DateTime>
        <XMLVersion>1.0.0</XMLVersion>
        <TestType>IntegrationTest</TestType>
        <ObjectName>SPI</ObjectName>
        <TlaVer>1.0.0</TlaVer>
        <SwBranch>MY_2015</SwBranch>
        <SvnRev>1632</SvnRev>
        <HwVersion>1.0</HwVersion>
        <Author>Your name here</Author>
        <TotalTestStepsOK>2</TotalTestStepsOK>
        <TotalTestStepsNOK>2</TotalTestStepsNOK>
        <TotalTestStepsNT>0</TotalTestStepsNT>
        <TotalTestSteps>4</TotalTestSteps>
    </TEST_REPORT>
    '''

    def __init__(self, objName, tlaVer='', swBranch='', svnRev='', hwVersion='', author='', service=''):
        '''
        Description: Constructor.
        Parameter 'objName' is a string with the name of the SW being tested.
        Parameter 'tlaVer' is optional, string with the SW component version.
        Parameter 'swBranch' is optional, string with the SW branch, in case it's useful to identify it.
        Parameter 'svnRev' is optional, string with the SVN revision used to do the test in the target.
        Parameter 'hwVersion' is optional, string with the HW version used to do the test in the target.
        Parameter 'author' is optional, string with author of the test script.
        '''
        # Call the father init, in Python 3.0 would be super().__init__()
        super(ITReport, self).__init__()
        # Create and fill tag for the XML structure version
        self.xml_ver = ET.SubElement(self.root, 'XMLVersion')
        self.xml_ver.text = IT_XML_VERSION
        # Create and fill tag for the type of test
        self.test_type = ET.SubElement(self.root, 'TestType')
        self.test_type.text = 'IntegrationTest'
        # Store parameters
        self.obj_name = objName
        self.tla_ver = tlaVer
        self.svn_rev  = svnRev
        self.sw_branch = swBranch
        self.hw_ver = hwVersion
        self.author = author
        self.service = service


    def generate_report(self, xsl_path=''):
        '''
        Description: Generates the XML + XSL files with the integration test report. Must be called at the end of the script.
        Parameter 'xsl_path' is optional and contains the path to the it_template.xsl file.

        Example:
            it_report = ITReport('FrontWiper', '1.0.0', 'MY_2015', '5271', 'HW6.1', 'John Doe')
            test_case_name = 'Front Wiper low speed'
            test_case_desc = 'Testing low speed in different key positions'
            test_case_reqs = 'Req_123v2, Req_134'
            it_report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
            # Adding a test step
            result = check_act_key_out()
            test_step_description = 'Checking here Front Wiper low speed is not activated in key out'
            it_report.add_test_step(test_step_description, result)
            # Generate report
            it_report.generate_report()
        '''
        # Generate stats for the latest test case
        self._add_test_case_stats()
        # Create tags
        obj_name = ET.SubElement(self.root, 'ObjectName')
        tla_ver = ET.SubElement(self.root, 'TlaVer')
        sw_branch = ET.SubElement(self.root, 'SwBranch')
        svn_rev = ET.SubElement(self.root, 'SvnRev')
        hw_ver = ET.SubElement(self.root, 'HwVersion')
        author = ET.SubElement(self.root, 'Author')
        service = ET.SubElement(self.root, 'service')

        # Fill tags
        obj_name.text = self.obj_name
        tla_ver.text = self.tla_ver
        sw_branch.text = self.sw_branch
        svn_rev.text = self.svn_rev
        hw_ver.text = self.hw_ver
        author.text = self.author
        service.text = self.service
        # Generate total stats
        self._add_total_stats()
        # Prettify and generate the XML report
        xsl_filename = 'REPORT-' + service.text + '.xsl'
        if (not os.path.isfile(xsl_filename)) and (xsl_path != ''):
            shutil.copyfile(xsl_path + '\\it_template.xsl', xsl_filename)
        xml_str = self._prettify(xsl_filename)
        xml_filename = 'REPORT-' + service.text +"_report.xml"
        f = open(xml_filename, 'w')
        f.write(xml_str)
        f.close()
        os.startfile(xml_filename)



class UTReport(Report):
    '''
    This class generates an XML data structure containing the results of an unit test.

    Note: This class derives from Report class above. So public methods add_test_case, add_test_step and
    add_info_step are also available in this UTReport class.

    This is the XML structure:

    <TEST_REPORT>
        <Collection>
            <Test>
                <TestCase>Test Case 1 Title</TestCase>
                <TestDescription>Test Case 1 Desciption</TestDescription>
                <TestRequirements>Reqs tested: None</TestRequirements>
                <TestStep>
                    <Description>Test step 1 description here</Description>
                    <Result>1</Result>
                    <Comment>Optional comment here</Comment>
                </TestStep>
                <TestStep>
                    <Description>Test step 2 description here</Description>
                    <Result>1</Result>
                    <Comment/>
                </TestStep>
                <TestStep>
                    <Description>Info step description here</Description>
                    <Result>2</Result>
                    <Comment/>
                </TestStep>
                <TestStepsOK>2</TestStepsOK>
                <TestStepsNOK>0</TestStepsNOK>
                <TestStepsNT>0</TestStepsNT>
                <TestsTotal>2</TestsTotal>
            </Test>
            <Test>
                <TestCase>Test Case 2 Title</TestCase>
                <TestDescription>Test Case 2 Desciption</TestDescription>
                <TestRequirements>Reqs tested: None</TestRequirements>
                <TestStep>
                    <Description>Test step 1 description here</Description>
                    <Result>0</Result>
                    <Comment/>
                </TestStep>
                <TestStep>
                    <Description>Test step 2 description here</Description>
                    <Result>0</Result>
                    <Comment/>
                </TestStep>
                <TestStepsOK>0</TestStepsOK>
                <TestStepsNOK>2</TestStepsNOK>
                <TestStepsNT>0</TestStepsNT>
                <TestsTotal>2</TestsTotal>
            </Test>
        </Collection>
        <TestTool>LATTE</TestTool>
        <DateTime>21-12-2013 15:07</DateTime>
        <XMLVersion>1.0.0</XMLVersion>
        <TestType>UnitTest</TestType>
        <ObjectName>SPI</ObjectName>
        <TlaVer>1.0.0</TlaVer>
        <SwBranch>MY_2015</SwBranch>
        <Author>Your name here</Author>
        <TotalTestStepsOK>2</TotalTestStepsOK>
        <TotalTestStepsNOK>2</TotalTestStepsNOK>
        <TotalTestStepsNT>0</TotalTestStepsNT>
        <TotalTestSteps>4</TotalTestSteps>
    </TEST_REPORT>
    '''

    def __init__(self, objName, tlaVer='', swBranch='', author=''):
        # Call the father init, in Python 3.0 would be super().__init__()
        super(UTReport, self).__init__()
        # Create and fill tag for the XML structure version
        self.xml_ver = ET.SubElement(self.root, 'XMLVersion')
        self.xml_ver.text = UT_XML_VERSION
        # Create and fill tag for the type of test
        self.test_type = ET.SubElement(self.root, 'TestType')
        self.test_type.text = 'UnitTest'
        # Store parameters
        self.obj_name = objName
        self.tla_ver = tlaVer
        self.sw_branch = swBranch
        self.author = author


    def generate_report(self, xsl_path=''):
        '''
        Description: Generates the XML + XSL files with the unit test report. Must be called at the end of the script.
        Parameter 'xsl_path' is optional and contains the path to the ut_template.xsl file.

        Example:
            ut_report = UTReport('FrontWiper', '1.0.0', 'MY_2015', 'John Doe')
            test_case_name = 'Front Wiper low speed'
            test_case_desc = 'Testing low speed in different key positions'
            test_case_reqs = 'Req_123v2, Req_134'
            ut_report.add_test_case(test_case_name, test_case_desc, test_case_reqs)
            # Adding a test step
            result = check_act_key_out()
            test_step_description = 'Checking here Front Wiper low speed is not activated in key out'
            ut_report.add_test_step(test_step_description, result)
            # Generate report
            ut_report.generate_report()
        '''
        # Generate stats for the latest test case
        self._add_test_case_stats()
        # Create tags
        obj_name = ET.SubElement(self.root, 'ObjectName')
        tla_ver = ET.SubElement(self.root, 'TlaVer')
        sw_branch = ET.SubElement(self.root, 'SwBranch')
        author = ET.SubElement(self.root, 'Author')
        # Fill tags
        obj_name.text = self.obj_name
        tla_ver.text = self.tla_ver
        sw_branch.text = self.sw_branch
        author.text = self.author
        # Generate total stats
        self._add_total_stats()
        # Prettify and generate the XML report
        xsl_filename = 'SITS-SW-251-' + PROJECT_ID + '.xsl'
        if (not os.path.isfile(xsl_filename)) and (xsl_path != ''):
            shutil.copyfile(xsl_path + '\\ut_template.xsl', xsl_filename)
        xml_str = self._prettify(xsl_filename)
        xml_filename = 'SITS-SW-251-' + PROJECT_ID + "-" + self.obj_name + "_report.xml"
        f = open(xml_filename, 'w')
        f.write(xml_str)
        f.close()
        os.startfile(xml_filename)

