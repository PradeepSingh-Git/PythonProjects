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

import time


class Testsuite:
    '''
    Class for accessing the Framework functionalities.
    '''

    def __init__(self,workBookName='',workSheetName='',tableHdrRow=17,rowTypeCol=0,cmdTypeCol=1,reqIDCol=2,testNameCol=3,testDescCol=4,testCondCol=5,expResCol=6,actResCol=7,testResCol=8,commentCol=9):
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


        print "Init Called"


