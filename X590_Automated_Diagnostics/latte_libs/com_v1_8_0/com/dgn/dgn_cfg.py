'''
====================================================================
Configuration file for Diagnostics
(C) Copyright 2013 Lear Corporation
====================================================================
'''

# Configure here network params STmin and BS of the tester.
# Keep TESTER_PARAM_STMIN = 0x0A and TESTER_PARAM_BS = 0x00 if unknown.
# For more info about these params, see ISO 15765-2
TESTER_PARAM_STMIN = 0x0A
TESTER_PARAM_BS = 0x00

# Tester present period to be sent by the tool, in seconds
TESTER_PRESENT_PERIOD = 2.0

# Configure if using Extended Addressing or Normal addressing (see ISO 15765-2)
EXTENDED_ADDRESSING = False

if EXTENDED_ADDRESSING:
    # If using Extended Addressing configure these params for the CAN IDs
    ID_BASE_ADDRESS = 0x600
    N_SA = 0xF1
    N_TA_PHYSICAL  = 0x40
    N_TA_FUNCTIONAL = 0xDF
else:
    # If using Normal Addressing configure these CAN IDs
    ID_PHYSICAL_REQ = 0x7E5
    ID_FUNCTIONAL_REQ = 0x7DF
    ID_PHYSICAL_RESP = 0x7ED

# Requests and Flow Control frames sent can have a DLC of 8 bytes, or just the length of the frame
DGN_SEND_8_BYTES = True

# Name of the logfile where the frames will be logged
DGN_LOGFILE = 'dgn_logfile.txt'
