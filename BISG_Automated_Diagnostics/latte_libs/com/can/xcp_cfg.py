'''
====================================================================
Configuration file for XCP
(C) Copyright 2013 Lear Corporation
====================================================================
'''

# Configure here if XCP over CAN is enabled or not
xcpcan_available = True

if xcpcan_available:
    try:
        from ...latte_cfg import XCP_ID_RX, XCP_ID_TX, XCP_SEND_8_BYTES, XCP_LOGFILE
        print 'INFO: XCP over CAN enabled (using configuration parameters declared in latte_cfg.py)'

    except:
        print 'INFO: XCP over CAN enabled (using configuration parameters declared in xcp_cfg.py)'
        # Configure here the XCP CAN IDs (Rx, Tx for the ECU)
        XCP_ID_RX = 0x6F0
        XCP_ID_TX = 0x6F5

        # CCP requests frames sent can have a fixed DLC of 8 bytes, or just the length of the frame
        XCP_SEND_8_BYTES = True

        # Name of the logfile where the frames will be logged
        XCP_LOGFILE = 'xcp_logfile.txt'

else:
    print 'INFO: XCP over CAN not enabled (can be enabled in xcp_cfg.py)'