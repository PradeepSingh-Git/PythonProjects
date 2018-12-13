'''
====================================================================
Configuration file for XCP
(C) Copyright 2013 Lear Corporation
====================================================================
'''

# Configure here the XCP CAN IDs (Rx, Tx for the ECU)
XCP_ID_RX = 0x6F0
XCP_ID_TX = 0x6F5

# CCP requests frames sent can have a fixed DLC of 8 bytes, or just the length of the frame
XCP_SEND_8_BYTES = True

# Name of the logfile where the frames will be logged
XCP_LOGFILE = 'xcp_logfile.txt'
