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

''' Adding path for loading correctly tsuite library '''
TSUITE_LIB_PATH = os.path.abspath(r'../Libs/tsuite')
sys.path.append(TSUITE_LIB_PATH)


from tsuite import *


tsuiteObj = Testsuite()