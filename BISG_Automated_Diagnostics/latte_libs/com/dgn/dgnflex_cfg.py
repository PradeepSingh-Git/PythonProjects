'''
====================================================================
Configuration file for Diagnostics
(C) Copyright 2016 Lear Corporation
====================================================================
'''

# Configure here if diagnostics over Flexray are enabled or not
dgnflex_available = True

if dgnflex_available:
    try:
        from ...latte_cfg import TESTER_PARAM_STMIN, TESTER_PARAM_BS, TESTER_PRESENT_PERIOD, \
                                 ID_N_SA, ID_N_TA_FUNCTIONAL, ID_N_TA_PHYSICAL, DIAG_FRAMES_DEFINED_BY_NAME
        if DIAG_FRAMES_DEFINED_BY_NAME:
            from ...latte_cfg import FR_NAME_ID_TESTER_PHYS_REQ, FR_NAME_ID_TESTER_FUNC_REQ, FR_NAME_ID_ECU_RESP
        else:
            from ...latte_cfg import FR_SLOT_ID_TESTER_PHYS_REQ, FR_SLOT_ID_TESTER_FUNC_REQ, FR_SLOT_ID_ECU_RESP, MAX_PAYLOAD_REQUEST_APP
        from ...latte_cfg import DGN_SEND_ALL_FRAME_BYTES
        from ...latte_cfg import DGNFLEX_LOGFILE as DGN_LOGFILE
        print 'INFO: Diagnostics over Flexray enabled (using configuration parameters declared in latte_cfg.py)'

    except:
        print 'INFO: Diagnostics over Flexray enabled (using configuration parameters declared in dgnflex_cfg.py)'
        # Configure here network params STmin and BS of the tester.
        # Keep TESTER_PARAM_STMIN = 0x0A and TESTER_PARAM_BS = 0x00 if unknown.
        # For more info about these params, see ISO 15765-2
        TESTER_PARAM_STMIN = 0x0A
        TESTER_PARAM_BS = 0x00

        # Tester present period to be sent by the tool, in seconds
        TESTER_PRESENT_PERIOD = 2.0

        # Addressing configuration for tester and ECU under test
        ID_N_SA = 0x0E80 # Tester
        ID_N_TA_FUNCTIONAL = 0x1FFF # Tester functional address
        ID_N_TA_PHYSICAL = 0x1747 # EPICB

        # Configure here if FIBEX/AutosarEcuExtract DGN frames are used or manually defined. (Gigabox driver doesn't support manual definition)
        DIAG_FRAMES_DEFINED_BY_NAME = True

        if DIAG_FRAMES_DEFINED_BY_NAME:
            # Define frame names existing in Fibex/AutosarEcuExtract for DGN
            FR_NAME_ID_TESTER_PHYS_REQ = 'TST_FR_Tx_DiagReq_1'
            FR_NAME_ID_TESTER_FUNC_REQ = 'TST_FR_Tx_DiagReq_2'
            FR_NAME_ID_ECU_RESP = ['EPICB_FR_DiagResp']
        else:
            # Define frame ID slots to be used for DGN (Note: MUST not be present in Fibex/AutosarEcuExtract)
            FR_SLOT_ID_TESTER_PHYS_REQ = 88 # define here FlexRay slot ID assigned to the Tester physical request
            FR_SLOT_ID_TESTER_FUNC_REQ = 87 # define here FlexRay slot ID assigned to the Tester functional request
            FR_SLOT_ID_ECU_RESP = [69, 75, 81] # define here FlexRay slot(s) ID assigned to the ECU response
            MAX_PAYLOAD_REQUEST_APP = 32
            MAX_PAYLOAD_RESPONSE_APP = 32

        # Requests and Flow Control frames sent can have a DLC of all frame bytes, or just the length of the frame
        # If set to TRUE, max length of the frame will be sent with extra 0's
        DGN_SEND_ALL_FRAME_BYTES = False

        # Name of the logfile where the frames will be logged
        DGN_LOGFILE = 'dgn_flex_logfile.txt'

else:
    print 'INFO: Diagnostics over Flexray not enabled (can be enabled in dgnflex_cfg.py)'
