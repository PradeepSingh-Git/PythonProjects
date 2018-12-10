'''
====================================================================
Configuration file for CCP
(C) Copyright 2013 Lear Corporation
====================================================================
'''

# Configure here if CCP over CAN is enabled or not
ccpcan_available = True

if ccpcan_available:
    try:
        from ...latte_cfg import CCP_ID_RX, CCP_ID_TX, CCP_STATION_ADDRESS, CCP_SEND_8_BYTES, CCP_LOGFILE
        print 'INFO: CCP over CAN enabled (using configuration parameters declared in latte_cfg.py)'

    except:
        print 'INFO: CCP over CAN enabled (using configuration parameters declared in ccp_cfg.py)'
        # Configure here the CCP CAN IDs (Rx, Tx for the ECU)
        CCP_ID_RX = 0x601
        CCP_ID_TX = 0x600

        # ECU Station Address
        CCP_STATION_ADDRESS = 0x0039

        # CCP requests frames sent can have a fixed DLC of 8 bytes, or just the length of the frame
        CCP_SEND_8_BYTES = True

        # Name of the logfile where the frames will be logged
        CCP_LOGFILE = 'ccp_logfile.txt'

else:
    print 'INFO: CCP over CAN not enabled (can be enabled in ccp_cfg.py)'
