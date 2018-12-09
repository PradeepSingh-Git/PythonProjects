"""
====================================================================
GigaBox FlexRay DLL wrapper
(C) Copyright 2017 Lear Corporation
====================================================================
"""

__author__  = 'asanz'
__version__ = '1.0.6'
__email__   = 'asanz@lear.com'

'''
CHANGE LOG
==========
1.0.6 Define separate params for max static and dynamic slots allowed.
1.0.5 Raising exceptions instead of sys.exit() calls.
1.0.4 Bugfix: allow to work with more than 2 HW channels.
1.0.3 Modified open_fr_channel, __init and close_channel with improved driver start/stop sequence.
1.0.2 Modified scan_devices method to generate list of detailed channel info.
1.0.1 When generating the message buffers, get the frames with the lower slot_id first.
1.0.0 Initial version
'''

from ctypes import *
import time
import sys
import os
import sys
import re
try:
    import clr
except:
    raise ImportError('INFO: GIGABOX device for FLexRay not supported, because "clr" module could not be imported')
try:
    import usb
except:
    raise ImportError('INFO: GIGABOX device for FLexRay not supported, because "usb" module could not be imported')


# A few constants from NativeInterface.h
frStatusResult = {
0x00 : "GTFR_INV_REG_ADDR",               #  Invalid register address
0x01 : "GTFR_SUCCESS",                    #  No Error occured
0x02 : "GTFR_TIMEOUT",                    #  Timeout Error
0x03 : "GTFR_INTERFACE_NOT_CONNECTED",    #  Interface not connected
0x04 : "GTFR_INV_INTERFACE_IDX",          #  Invalid interface index
0x05 : "GTFR_INV_CTRL_IDX",               #  Invalid interface index
0x06 : "GTFR_NOT_INITIALIZED",            #  This is returned in case of the GtFr_Init has not been called
0x07 : "GTFR_INV_TIMER_IDX",              #  Invalid timer index
0x08 : "GTFR_INV_CTRL_STATE",             #  Invalid controller state for this function
0x09 : "GTFR_INV_CFG_TAG",                #  Invalid configuration tag
0x0A : "GTFR_ERROR_USB",                  #  Error in usb-transmission
0x0B : "GTFR_INV_MSG_BUF_IDX",            #  Message Buffer not configured for transmission.
0x0C : "GTFR_INV_PARAMETER",              #  Invalid parameter
0x0D : "GTFR_INV_CONFIGURATION",          #  Invalid configuration
0x0E : "GTFR_NOT_SUPPORTED",              #  Function is not supported
0x0F : "GTFR_FIBEX_LOAD_ERRO",            #  Fibex Load Error
}

# definitions for statusType
frStatusTypeEnum = {
 0x00 : "FR_STATUS_DEFAULT_CONFIG",
 0x01 : "FR_STATUS_READY",
 0x02 : "FR_STATUS_NORMAL_ACTIVE",
 0x03 : "FR_STATUS_NORMAL_PASSIVE",
 0x04 : "FR_STATUS_HALT",
 0x05 : "FR_STATUS_MONITOR_MODE",
 0x06 : "FR_STATUS_AUTORESTART",
 0x0F : "FR_STATUS_CONFIG",
 0x10 : "FR_STATUS_WAKEUP_STANDBY",
 0x11 : "FR_STATUS_WAKEUP_LISTEN",
 0x12 : "FR_STATUS_WAKEUP_SEND",
 0x13 : "FR_STATUS_WAKEUP_DETECT",
 0x20 : "FR_STATUS_STARTUP_PREPARE",
 0x21 : "FR_STATUS_COLDSTART_LISTEN",
 0x22 : "FR_STATUS_COLDSTART_COLLISION_RESOLUTION",
 0x23 : "FR_STATUS_COLDSTART_CONSISTENCY_CHECK",
 0x24 : "FR_STATUS_COLDSTART_GAP",
 0x25 : "FR_STATUS_COLDSTART_JOIN",
 0x26 : "FR_STATUS_INTEGRATION_COLDSTART_CHECK",
 0x27 : "FR_STATUS_INTEGRATION_LISTEN",
 0x28 : "FR_STATUS_INTEGRATION_CONSISTENCY_CHECK",
 0x29 : "FR_STATUS_INITIALIZE_SCHEDULE",
 0x2a : "FR_STATUS_ABORT_STARTUP",
 0x2b : "FR_STATUS_STARTUP_SUCCESS",
 }

# Gigabox DLL has a buffer limit for managing the FlexRay slots. Over this value, Init of the Channel is not possible
# Please keep GIGABOX_MAX_ALL_SLOTS equal to 69, and adjust GIGABOX_MAX_STATIC_SLOTS as desired. If you want to load
# all static slots and no dynamic slots, set GIGABOX_MAX_STATIC_SLOTS = GIGABOX_MAX_STATIC_SLOTS. If you want to load
# all dynamic slots, set GIGABOX_MAX_STATIC_SLOTS to a low value.
GIGABOX_MAX_STATIC_SLOTS = 40
GIGABOX_MAX_ALL_SLOTS = 69

class GIGABOX():

    def __init__(self):
        """
        Description: Constructor. Loads LearGigaBoxLib.dll, opens drivers and reads conencted Kvaser devices.
        """
        self.canlib_txhnd = {}
        self.canlib_rxhnd = {}
        self.ecuUnderTest = []
        self.messageIdSize = []
        self.currentCycle = {}
        self.static_messageList_cfg_c0 = []
        self.static_messageList_cfg_c1 = []
        self.dymanic_messageList_cfg_c0 = []
        self.dynamic_messageList_cfg_c0 = []
        self.channel_list = [] # List of strings with channel info

        # Load DLL's
        try:
            self.dll_path = os.path.dirname(os.path.abspath(__file__)) + '\GtFrNET.dll'
            clr.AddReference(self.dll_path)
            self.dll_path = os.path.dirname(os.path.abspath(__file__)) + '\LearGigaBoxAPI.dll'
            clr.AddReference(self.dll_path)
        except WindowsError:
            print "INFO: Failed to load DLL, reasons could be:"
            print "  - 64 bits version of Python installed. It must be 32 bits version (also called x86)"
            print "  - Pythonnet not installed. Please execute LATTE\Com\Trunk\drivers\gigabox\Install_Pythonnet_for_GtFrNET.bat"
            print "  - GIGABOX drivers not installed. Please execute LATTE\Com\Trunk\drivers\gigabox\gigabox-flex-i-driver-library-setup-v1-3-5_639_1466427547.exe"
            sys.exit()

        from GtFrNET import Types
        from GtFrNET import Core
        from LearGigaBoxAPI  import LearGigaBoxAPI

        self.dllTypes = Types
        self.dll = Core.GtFr_Api
        self.dllLear = LearGigaBoxAPI

        result_init = self.dll.GtFr_Init()
        if result_init != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            self._usb_gigabox_restart()


    def _usb_gigabox_restart(self):
        # try to restart usb
        usb_devices = usb.core.find(find_all=True, idVendor=0x2918, idProduct=0x0000)  # Get devices by vendor and product id
        for dev in usb_devices:
            if re.match(r'GIGABOX flex-i', usb.util.get_string(dev, dev.iProduct)):  # Check that device is a GIGABOX flex-i
                dev.reset()
        result_init = self.dll.GtFr_Init()
        if result_init != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            raise Exception('ERROR: During GigaBox driver Initialization: ' + frStatusResult.get(result_init, "UnknownError"))


    def scan_devices(self):
        '''
        Description: Scans all gigabox devices connected.
        Returns list of devices found, and prints useful info describing the devices connected and channels available

        Example:
            com = Com('GIGABOX')
            com.scan_devices()
        '''
        num_devices = 0
        result, num_devices = self.dll.GtFr_GetInterfaceCount(num_devices)
        if result == self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            for device_index in range(num_devices):
                devices_infoExt = self.dllTypes.GtFr_InterfaceExtInfoType()
                result, devices_infoExt = self.dll.GtFr_GetInterfaceExtInfo(device_index, devices_infoExt)
                if result == self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
                    print '\nDevice     : GIGABOX'
                    print 'Channel ID : ' + str(device_index)
                    print 'Device S/N : ' + str(devices_infoExt.serial)
                    print 'License    : ' + str(devices_infoExt.license.FixedElementField)
                    self.channel_list.append('GIGABOX ' + str(devices_infoExt.serial) + ' Channel ' + str(device_index))
                    devices_info = self.dllTypes.GtFr_InterfaceInfoType()
                    result, devices_info = self.dll.GtFr_GetInterfaceInfo(device_index, devices_info)
                    if result == self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
                        print 'Version    : ' + devices_info.softwareInfo.assemblyVersion
                        print ''
                else:
                    raise Exception('ERROR: Reading GigaBox device information: ' + frStatusResult.get(result, "UnknownError"))
        else:
            raise Exception('ERROR: Reading GigaBox device information: ' + frStatusResult.get(result, "UnknownError"))

        return self.channel_list


    def open_fr_channel(self, index, clusterConfig, message_config, ecu_under_test):
        '''
        Description: Opens FlexRay channel.  E-Ray CC and Fujitsu CC will be activated based on cluster config.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'clusterConfig' is an object of class ClusterConfig (defined in fibex.py),
        contains the cluster configuration parameters.
        Parameter 'ecu_under_test' defines the ECU under test to determine which messages will be defined as RX
        (messages defined as TX from the ECU under test).

        Example:
            com = XLCOM()
            com.open_fr_channel(0, cluster_config, message_config, 'ECM')
        '''
        # Check if requested ecu_under_test is present in database (FIBEX, ECUextract...)
        found_ecu = False
        if ecu_under_test is not '':
            for message in message_config.keys():
                if message_config.get(message).transmitter == ecu_under_test:
                    found_ecu = True
                    break
        if found_ecu is False:
            print 'ERROR: While initializing GIGABOX FlexRay channel ' + str(index) + ', ecu under test ' + ecu_under_test + ' not present in database.'
            sys.exit()
        self.ecuUnderTest.insert(index, ecu_under_test)

        GTFR_SUCCESS = self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS

        result_init = self.dll.GtFr_Init()
        if result_init != GTFR_SUCCESS:
            # Try to restart usb
            self._usb_gigabox_restart()

        # Prepare Gigabox configuration structs based on cluster Config
        controller_cfg = self._generateControllerConfig(clusterConfig, clusterConfig.erayID)
        protocol_cfg   = self._generateProtocolConfig(clusterConfig)
        messagebuf_cfg = self._generateBufferConfigController0(index, clusterConfig, message_config)

        # Setup Controller 0 configuration for startup and sync frames for E-ray
        result_ctrl     = self.dll.GtFr_InitCtrl(index, 0, controller_cfg)
        result_protocol = self.dll.GtFr_InitProtocol(index, 0, protocol_cfg)
        result_msgbuf   = self.dll.GtFr_InitMsgBuf(index, 0, messagebuf_cfg)
        if result_ctrl == GTFR_SUCCESS and result_protocol == GTFR_SUCCESS and result_msgbuf == GTFR_SUCCESS:
            # Initialize controller 0 with the configuration from the previous steps
            result_init = self._init_controller(index, 0)
            if result_init == GTFR_SUCCESS:
                print 'INFO: Gigabox device FlexRay channel open in channel ID ' + str(index) + ', controller 0'
            else:
                print 'ERROR: While initializing GIGABOX FlexRay channel ' + str(index) + ', controller 0. Error: ' + \
                    frStatusResult.get(result_init, "UnknownError")
                sys.exit()
        else:
            print 'ERROR: While initializing GIGABOX FlexRay channel ' + str(index) + ', controller 0. Error reported:'
            print '   - InitCtrl result    : ' + frStatusResult.get(result_ctrl, "UnknownError")
            print '   - InitProtocol result: ' + frStatusResult.get(result_protocol, "UnknownError")
            print '   - InitMsgBuf result  : ' + frStatusResult.get(result_msgbuf, "UnknownError")
            sys.exit()

        # Setup just startup/sync frames for Second controller, if configured
        if clusterConfig.coldID != 0:
            controller_cfg_2 = self._generateControllerConfig(clusterConfig, clusterConfig.coldID)
            messagebuf_cfg_2 = self._generateBufferConfigController1(index, clusterConfig, message_config)

            # Setup Controller 1 configuration
            result_ctrl     = self.dll.GtFr_InitCtrl(index, 1, controller_cfg_2)
            result_protocol = self.dll.GtFr_InitProtocol(index, 1, protocol_cfg)
            result_msgbuf   = self.dll.GtFr_InitMsgBuf(index, 1, messagebuf_cfg_2)
            if result_ctrl == GTFR_SUCCESS and result_protocol == GTFR_SUCCESS and result_msgbuf == GTFR_SUCCESS:
                # Initialize controller 0 with the configuration from the previous steps
                result_init = self._init_controller(index, 1)
                if result_init == GTFR_SUCCESS:
                    print 'INFO: GigaBox device FlexRay channel open in channel ID ' + str(index) + ', controller 1'
                else:
                    print 'ERROR: While initializing FlexRay channel ' + str(index) + ', controller 1. Error: ' + \
                           frStatusResult.get(result_init, "UnknownError")
                    sys.exit()
            else:
                print 'ERROR: While initializing FlexRay channel ' + str(index) + ', controller 1. Error reported:'
                print '   - InitCtrl result    : ' + frStatusResult.get(result_ctrl, "UnknownError")
                print '   - InitProtocol result: ' + frStatusResult.get(result_protocol, "UnknownError")
                print '   - InitMsgBuf result  : ' + frStatusResult.get(result_msgbuf, "UnknownError")
                sys.exit()


    def _init_controller(self, index, controller, init_timeout = 2.0):
        '''
        Description: Execute the dll calls to initiate the Gigabox Flexray channel, configuration must be set before
        Parameter 'index'  contain the gigabox channel index.
        Parameter 'controller' contains the controller index, 0 or 1
        '''

        # Initialize controller with the configuration from the previous steps
        result = self.dll.GtFr_ExecuteCommand(index, controller, self.dllTypes.GtFr_CommandType.GTFR_CMD_INIT)
        if result != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            return result

        # Wait for controller initialization
        time_start = time.clock()
        time_elapsed = 0.0
        status_init = 0
        result, status_init = self.dll.GtFr_GetCtrlState(index, controller, status_init)
        # Wait till READY state is reached
        while status_init is not self.dllTypes.GtFr_PocStateType.GTFR_PROTSTATE_READY and \
              result is self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS and \
              time_elapsed < init_timeout:
            result, status_init = self.dll.GtFr_GetCtrlState(index, controller, status_init)
            time_elapsed = time.clock() - time_start
        if result is not self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            return result
        elif time_elapsed >= init_timeout:
            return self.dllTypes.GtFr_ReturnType.GTFR_TIMEOUT

        # Now start the comunication in the controller
        result = self.dll.GtFr_ExecuteCommand(index, controller, self.dllTypes.GtFr_CommandType.GTFR_CMD_START)
        if result != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            return result

        return self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS


    def _generateControllerConfig(self, clusterConfig, cold_start):
        '''
        Description: Creates the Gigabox Controller configuration based on database cluster info.

        Returns: controller_cfg of GtFr_CtrlCfgType
        '''
        controller_cfg = self.dllTypes.GtFr_CtrlCfgType()

        controller_cfg.AutoRestart = 0
        if clusterConfig.baudrate == 5000000:
            self.dllTypes.GtFr_BaudRateType.GTFR_BAUDRATE_5M
        elif clusterConfig.baudrate == 10000000:
            self.dllTypes.GtFr_BaudRateType.GTFR_BAUDRATE_10M
        else:
            self.dllTypes.GtFr_BaudRateType.GTFR_BAUDRATE_2M5
        if clusterConfig.erayChannel == 1:
            controller_cfg.ChannelEnable = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_A
        elif clusterConfig.erayChannel == 2:
            controller_cfg.ChannelEnable = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_B
        elif clusterConfig.erayChannel == 3:
            controller_cfg.ChannelEnable = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_BOTH
        else:
            controller_cfg.ChannelEnable = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        if cold_start != 0:
            controller_cfg.ColdstartNode = long(1)
        else:
            controller_cfg.ColdstartNode = long(0)
        controller_cfg.MediaAccessTestA = 0
        controller_cfg.MediaAccessTestB = 0

        interrupt_cfg = self.dllTypes.GtFr_InterruptCfgType()
        statusEvent_cfg = self.dllTypes.GtFr_EventEnableTypes()
        statusEvent_cfg.wakeupStatus = 0
        statusEvent_cfg.collisionAvoidance = 0
        statusEvent_cfg.cycleStart = 1
        statusEvent_cfg.transmitInterrupt = 1
        statusEvent_cfg.receiveInterrupt = 1
        statusEvent_cfg.fifo = 0
        statusEvent_cfg.nmvChanged = 0
        statusEvent_cfg.stopWatch = 0
        statusEvent_cfg.startupCompleted = 0
        statusEvent_cfg.dynamicSegmentStart = 0
        statusEvent_cfg.wakeupPatternA = 0
        statusEvent_cfg.mtsReceivedA = 0
        statusEvent_cfg.wakeupPatternB =  0
        statusEvent_cfg.mtsReceivedB = 0
        interrupt_cfg.statusEventEnable = statusEvent_cfg
        controller_cfg.InterruptConfig = interrupt_cfg

        return controller_cfg


    def _generateProtocolConfig(self, clusterConfig):
        '''
        Description: Creates the Gigabox Protocol configuration based on database cluster info.

        Returns: protocol_cfg of GtFr_ProtocolCfgType
        '''
        protocol_cfg = self.dllTypes.GtFr_ProtocolCfgType()

        protocol_cfg.gColdstartAttempts = clusterConfig.gColdStartAttempts
        protocol_cfg.gListenNoise = clusterConfig.gListenNoise
        protocol_cfg.pMacroInitialOffsetA = clusterConfig.pMacroInitialOffsetA
        protocol_cfg.pMacroInitialOffsetB = clusterConfig.pMacroInitialOffsetB
        protocol_cfg.gMacroPerCycle = clusterConfig.gMacroPerCycle
        protocol_cfg.gMaxWithoutClkCorrFatal = clusterConfig.gMaxWithoutClockCorrectionFatal
        protocol_cfg.gMaxWithoutClkCorrPassive = clusterConfig.gMaxWithoutClockCorrectionPassive
        protocol_cfg.gNetworkManagementVectorLength = clusterConfig.gNetworkManagementVectorLength
        protocol_cfg.gNumberOfMiniSlots = clusterConfig.gNumberOfMinislots
        protocol_cfg.gNumberOfStaticSlots = clusterConfig.gNumberOfStaticSlots
        protocol_cfg.gOffsetCorrectionStart = clusterConfig.gOffsetCorrectionStart
        protocol_cfg.gPayloadLengthStatic = clusterConfig.gPayloadLengthStatic
        protocol_cfg.gSyncNodeMax = clusterConfig.gSyncNodeMax

        protocol_cfg.gdActionPointOffset = clusterConfig.gdActionPointOffset
        protocol_cfg.gdCasRxLowMax = clusterConfig.gdCASRxLowMax
        protocol_cfg.gdDynamicSlotIdlePhase = clusterConfig.gdDynamicSlotIdlePhase
        protocol_cfg.gdMiniSlot = clusterConfig.gdMinislot
        protocol_cfg.gdMiniSlotActionPointOffset = clusterConfig.gdMiniSlotActionPointOffset
        protocol_cfg.gdNetworkIdleTime = clusterConfig.gdNIT
        protocol_cfg.gdStaticSlot = clusterConfig.gdStaticSlot
        protocol_cfg.gdTssTransmitter = clusterConfig.gdTSSTransmitter
        protocol_cfg.gdWakeupSymbolRxIdle = clusterConfig.gdWakeupSymbolRxIdle
        protocol_cfg.gdWakeupSymbolRxLow = clusterConfig.gdWakeupSymbolRxLow
        protocol_cfg.gdWakeupSymbolRxWindow = clusterConfig.gdWakeupSymbolRxWindow
        protocol_cfg.gdWakeupSymbolTxIdle = clusterConfig.gdWakeupSymbolTxIdle
        protocol_cfg.gdWakeupSymbolTxLow = clusterConfig.gdWakeupSymbolTxLow

        protocol_cfg.pAllowHaltDueToClock = clusterConfig.pAllowHaltDueToClock
        protocol_cfg.pAllowPassiveToActive = clusterConfig.pAllowPassiveToActive
        protocol_cfg.pClusterDriftDamping = clusterConfig.pClusterDriftDamping
        protocol_cfg.pDecodingCorrection = clusterConfig.pDecodingCorrection
        protocol_cfg.pDelayCompensationA = clusterConfig.pDelayCompensationA
        protocol_cfg.pDelayCompensationB = clusterConfig.pDelayCompensationB
        protocol_cfg.pExternOffsetCorrection = clusterConfig.pExternOffsetCorrection
        protocol_cfg.pExternRateCorrection = clusterConfig.pExternRateCorrection
        protocol_cfg.pKeySlotUsedForStartup = clusterConfig.pKeySlotUsedForStartup
        protocol_cfg.pKeySlotUsedForSync = clusterConfig.pKeySlotUsedForSync
        protocol_cfg.pLatestTx = clusterConfig.pLatestTx
        protocol_cfg.pMicroInitialOffsetA = clusterConfig.pMacroInitialOffsetA
        protocol_cfg.pMicroInitialOffsetB = clusterConfig.pMacroInitialOffsetB
        protocol_cfg.pMicroPerCycle = clusterConfig.pMicroPerCycle
        protocol_cfg.pOffsetCorrectionOut = clusterConfig.pOffsetCorrectionOut
        protocol_cfg.pRateCorrectionOut = clusterConfig.pRateCorrectionOut
        protocol_cfg.pSingleSlotEnabled = clusterConfig.pSingleSlotEnabled
        protocol_cfg.pWakeupChannel = clusterConfig.pWakeupChannel
        protocol_cfg.pWakeupPattern = clusterConfig.pWakeupPattern

        protocol_cfg.pdAcceptedStartupRange = clusterConfig.pdAcceptedStartupRange
        protocol_cfg.pdListenTimeout = clusterConfig.pdListenTimeout
        protocol_cfg.pdMaxDrift = clusterConfig.pdMaxDrift

        return protocol_cfg


    def _generateBufferConfigController0(self, index, clusterConfig, message_config):
        '''
        Description: Creates the Gigabox Buffer configuration for Controller 0.
                     It includes all Static and Dynamic messages from the database (FIBEX, ECUextract...).
                     The RX or TX configuration is based on the 'ecu_under_test' configuration.
                     Gigabox DLL has a limitation of a maximum of 24 Rx/Tx positions on the FIFO, so if more messages
                     are present in the database, they are not added. Error message will be displayed.

        Returns: messagebuf_cfg of GtFr_MsgBufCfgType
        '''
        messagebuf_cfg = self.dllTypes.GtFr_MsgBufCfgType()

        # Generate a list of all static message with its configuration and gigabox format
        static_messageList = []
        max_payload_length = 0
        messageIdSizeTemp = {} # Dictionary which will include size of each frame from key slot_id
        if clusterConfig.erayID == 0:
            buffer_index = 0
        else:
            buffer_index = 1 # Position 0 is reserved for startup synch message
        for message in sorted(message_config, key = lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] < clusterConfig.gNumberOfStaticSlots:
                # Check if it has to be a RX frame in Latte:
                #  - It's a startup/Synch TX message of the Controller 1 or
                #  - It's a TX message of the ECU under test but NOT a startup/Synch TX message of the Controller 0
                if (message_config.get(message).slot_id[0] == clusterConfig.coldID) or \
                   (message_config.get(message).transmitter == self.ecuUnderTest[index] and \
                   (message_config.get(message).slot_id[0] != clusterConfig.erayID or clusterConfig.erayID == 0)):
                    static_message_rx = self.dllTypes.GtFr_MsgBufType()
                    static_message_rx.msgBufTag = self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_RX
                    temp_rxMsgBuf = self.dllTypes.GtFr_RxMsgBufCfgType()
                    temp_rxMsgBuf.MsgBufNr = buffer_index
                    buffer_index = buffer_index + 1
                    temp_rxMsgBuf.FrameId = message_config.get(message).slot_id[0]
                    lengthInWords = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_rxMsgBuf.PayloadLength = lengthInWords
                    if max_payload_length < lengthInWords:
                        max_payload_length = lengthInWords
                    temp_rxMsgBuf.MsgBufInterruptEnable = 1
                    if clusterConfig.erayChannel == 1:
                        temp_rxMsgBuf.ChannelAEnable = 1
                        temp_rxMsgBuf.ChannelBEnable = 0
                    elif clusterConfig.erayChannel == 2:
                        temp_rxMsgBuf.ChannelAEnable = 0
                        temp_rxMsgBuf.ChannelBEnable = 1
                    elif clusterConfig.erayChannel == 3:
                        temp_rxMsgBuf.ChannelAEnable = 1
                        temp_rxMsgBuf.ChannelBEnable = 1
                    else:
                        temp_rxMsgBuf.ChannelAEnable = 0
                        temp_rxMsgBuf.ChannelBEnable = 0
                    temp_rxMsgBuf.BaseCycle = message_config.get(message).offset
                    temp_rxMsgBuf.Repetition = message_config.get(message).repetition
                    static_message_rx.rxMsgBuf = temp_rxMsgBuf
                    static_messageList.append(static_message_rx)

                else:
                    # Message it's a RX messages from ECU under test (or not used by ECU under test), so add it as a TX in Latte
                    static_message_tx = self.dllTypes.GtFr_MsgBufType()
                    static_message_tx.msgBufTag = self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX
                    temp_txMsgBuf = self.dllTypes.GtFr_TxMsgBufCfgType()
                    # Cold start message must be always in first fifo position
                    if message_config.get(message).slot_id[0] == clusterConfig.erayID:
                        temp_txMsgBuf.MsgBufNr = 0
                    else:
                        temp_txMsgBuf.MsgBufNr = buffer_index
                        buffer_index = buffer_index + 1
                    temp_txMsgBuf.FrameId = message_config.get(message).slot_id[0]
                    lengthInWords = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_txMsgBuf.PayloadLength = lengthInWords
                    if max_payload_length < lengthInWords:
                        max_payload_length = lengthInWords
                    temp_txMsgBuf.MsgBufInterruptEnable = 1
                    if clusterConfig.erayChannel == 1:
                        temp_txMsgBuf.ChannelAEnable = 1
                        temp_txMsgBuf.ChannelBEnable = 0
                    elif clusterConfig.erayChannel == 2:
                        temp_txMsgBuf.ChannelAEnable = 0
                        temp_txMsgBuf.ChannelBEnable = 1
                    elif clusterConfig.erayChannel == 3:
                        temp_txMsgBuf.ChannelAEnable = 1
                        temp_txMsgBuf.ChannelBEnable = 1
                    else:
                        temp_txMsgBuf.ChannelAEnable = 0
                        temp_txMsgBuf.ChannelBEnable = 0
                    temp_txMsgBuf.BaseCycle = message_config.get(message).offset
                    temp_txMsgBuf.Repetition = message_config.get(message).repetition
                    temp_txMsgBuf.PayloadPreamble = 0
                    temp_txMsgBuf.HeaderCrc = 0
                    temp_txMsgBuf.TransmissionMode =  self.dllTypes.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_CONTINOUS
                    static_message_tx.txMsgBuf = temp_txMsgBuf
                    # Check if message is the cold start, in order to put in fisrt position
                    if message_config.get(message).slot_id[0] == clusterConfig.erayID:
                        static_messageList.insert(0, static_message_tx)
                    else:
                        static_messageList.append(static_message_tx)
                # Add dictionary item
                messageIdSizeTemp[message_config.get(message).slot_id[0]] = message_config.get(message).length

            if len(static_messageList) > GIGABOX_MAX_STATIC_SLOTS:
                print '\nINFO: While initializing FlexRay: number of defined Static Messages is greather than the max allowed static slots: ' + str(GIGABOX_MAX_STATIC_SLOTS)
                print ' --> There will be limitation on messages transmission/reception'
                break

        # Generate a list of all dinamic message with its configuration and gigabox format
        dinamic_messageList = []
        dinamic_buffer_index = buffer_index
        for message in sorted(message_config, key=lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] >= clusterConfig.gNumberOfStaticSlots:
                # Check if it's a TX messages from ECU under test, so add it as a RX in Latte
                if message_config.get(message).transmitter == self.ecuUnderTest[index]:
                    dinamic_message = self.dllTypes.GtFr_MsgBufType()
                    dinamic_message.msgBufTag = self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_RX
                    temp_rxMsgBuf = self.dllTypes.GtFr_RxMsgBufCfgType()
                    temp_rxMsgBuf.MsgBufNr = dinamic_buffer_index
                    dinamic_buffer_index = dinamic_buffer_index + 1
                    temp_rxMsgBuf.FrameId = message_config.get(message).slot_id[0]
                    lengthInWords = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_rxMsgBuf.PayloadLength = lengthInWords
                    if max_payload_length < lengthInWords:
                        max_payload_length = lengthInWords
                    temp_rxMsgBuf.MsgBufInterruptEnable = 1
                    if clusterConfig.erayChannel == 1:
                        temp_rxMsgBuf.ChannelAEnable = 1
                        temp_rxMsgBuf.ChannelBEnable = 0
                    elif clusterConfig.erayChannel == 2:
                        temp_rxMsgBuf.ChannelAEnable = 0
                        temp_rxMsgBuf.ChannelBEnable = 1
                    elif clusterConfig.erayChannel == 3:
                        temp_rxMsgBuf.ChannelAEnable = 1
                        temp_rxMsgBuf.ChannelBEnable = 1
                    else:
                        temp_rxMsgBuf.ChannelAEnable = 0
                        temp_rxMsgBuf.ChannelBEnable = 0
                    temp_rxMsgBuf.BaseCycle = message_config.get(message).offset
                    temp_rxMsgBuf.Repetition = message_config.get(message).repetition
                    dinamic_message.rxMsgBuf = temp_rxMsgBuf
                    dinamic_messageList.append(dinamic_message)

                else:
                    # Message it's a RX messages from ECU under test (or not used by ECU under test), so add it as a TX in Latte
                    dinamic_message = self.dllTypes.GtFr_MsgBufType()
                    dinamic_message.msgBufTag = self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX
                    temp_txMsgBuf = self.dllTypes.GtFr_TxMsgBufCfgType()
                    temp_txMsgBuf.MsgBufNr = dinamic_buffer_index
                    dinamic_buffer_index = dinamic_buffer_index + 1
                    temp_txMsgBuf.FrameId = message_config.get(message).slot_id[0]
                    lengthInWords = message_config.get(message).length/2 + message_config.get(message).length%2
                    temp_txMsgBuf.PayloadLength = lengthInWords
                    if max_payload_length < lengthInWords:
                        max_payload_length = lengthInWords
                    temp_txMsgBuf.MsgBufInterruptEnable = 1
                    if clusterConfig.erayChannel == 1:
                        temp_txMsgBuf.ChannelAEnable = 1
                        temp_txMsgBuf.ChannelBEnable = 0
                    elif clusterConfig.erayChannel == 2:
                        temp_txMsgBuf.ChannelAEnable = 0
                        temp_txMsgBuf.ChannelBEnable = 1
                    elif clusterConfig.erayChannel == 3:
                        temp_txMsgBuf.ChannelAEnable = 1
                        temp_txMsgBuf.ChannelBEnable = 0 #TODO: if AB configured, Dynamic messages are not sent... reason unknown
                    else:
                        temp_txMsgBuf.ChannelAEnable = 0
                        temp_txMsgBuf.ChannelBEnable = 0
                    temp_txMsgBuf.BaseCycle = message_config.get(message).offset
                    temp_txMsgBuf.Repetition = message_config.get(message).repetition
                    temp_txMsgBuf.PayloadPreamble = 0
                    temp_txMsgBuf.HeaderCrc = 0
                    temp_txMsgBuf.TransmissionMode = self.dllTypes.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_SINGLE_SHOT
                    dinamic_message.txMsgBuf = temp_txMsgBuf
                    dinamic_messageList.append(dinamic_message)
                # Add dictionary item
                messageIdSizeTemp[message_config.get(message).slot_id[0]] = message_config.get(message).length

            if (len(static_messageList) + len(dinamic_messageList)) > GIGABOX_MAX_ALL_SLOTS:
                print '\INFO: While initializing FlexRay: number of defined Static and Dynamic Messages is greather than the max allowed slots: ' + str(GIGABOX_MAX_ALL_SLOTS)
                print ' --> There will be limitation on messages transmission/reception'
                break

        # Prepare fifo configuration
        fifo_config = self.dllTypes.GtFr_FifoCfgType()
        fifo_config.FifoDepth = 0 # FIFO not used
        fifo_config.FifoEntrySize = max_payload_length
        fifo_config.FifoCriticalLevel = 4
        fifo_config.RejectionFilterChannel = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        fifo_config.RejectionFilterValue = 0
        fifo_config.RejectionFilterMask = 0
        fifo_config.RejectionFilterBaseCycle = 0
        fifo_config.RejectionFilterRepetition = 0
        fifo_config.RejectStaticSegment = 0
        fifo_config.RejectNullFrames = 1

        # Create the messagebuf_cfg configuration
        messagebuf_cfg.splm = 0
        messagebuf_cfg.sec = self.dllTypes.GtFr_MsgBufSecurityModeType.GTFR_MSGBUF_SEC_UNLOCK_ALL
        messagebuf_cfg.sMsgBuf = self.dllTypes.GtFr_StaticMsgBufType(len(static_messageList), static_messageList)
        messagebuf_cfg.dMsgBuf = self.dllTypes.GtFr_DynamicMsgBufType(len(dinamic_messageList), dinamic_messageList)
        messagebuf_cfg.fifoMsgBuf = fifo_config

        # Store buffer configuration for future use in transmit function
        self.static_messageList_cfg_c0.insert(index, static_messageList)
        self.dynamic_messageList_cfg_c0.insert(index, dinamic_messageList)
        self.messageIdSize.insert(index, messageIdSizeTemp)

        return messagebuf_cfg


    def _generateBufferConfigController1(self, index, clusterConfig, message_config):
        '''
        Description: Creates the Gigabox Buffer configuration for Controller 1.
                     Controller 1 is only used in case of secondary Startup/Synch is confugured. So only
                     one position is configured.

        Returns: messagebuf_cfg of GtFr_MsgBufCfgType
        '''
        messagebuf_cfg = self.dllTypes.GtFr_MsgBufCfgType()

        # Generate a list of all static message with its configuration and gigabox format
        static_messageList = []
        dymnamic_messageList = []
        max_payload_length = 0
        buffer_index = 0
        for message in sorted(message_config, key=lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] == clusterConfig.coldID:
                static_message_tx = self.dllTypes.GtFr_MsgBufType()
                static_message_tx.msgBufTag = self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX
                temp_txMsgBuf = self.dllTypes.GtFr_TxMsgBufCfgType()
                temp_txMsgBuf.MsgBufNr = buffer_index
                temp_txMsgBuf.FrameId = message_config.get(message).slot_id[0]
                lengthInWords = message_config.get(message).length / 2 + message_config.get(message).length % 2
                temp_txMsgBuf.PayloadLength = lengthInWords
                temp_txMsgBuf.MsgBufInterruptEnable = 0
                if clusterConfig.erayChannel == 1:
                    temp_txMsgBuf.ChannelAEnable = 1
                    temp_txMsgBuf.ChannelBEnable = 0
                elif clusterConfig.erayChannel == 2:
                    temp_txMsgBuf.ChannelAEnable = 0
                    temp_txMsgBuf.ChannelBEnable = 1
                elif clusterConfig.erayChannel == 3:
                    temp_txMsgBuf.ChannelAEnable = 1
                    temp_txMsgBuf.ChannelBEnable = 1
                else:
                    temp_txMsgBuf.ChannelAEnable = 0
                    temp_txMsgBuf.ChannelBEnable = 0
                temp_txMsgBuf.BaseCycle = message_config.get(message).offset
                temp_txMsgBuf.Repetition = message_config.get(message).repetition
                temp_txMsgBuf.PayloadPreamble = 0
                temp_txMsgBuf.HeaderCrc = 0
                temp_txMsgBuf.TransmissionMode =  self.dllTypes.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_CONTINOUS
                static_message_tx.txMsgBuf = temp_txMsgBuf
                static_messageList.append(static_message_tx)
                break

        if len(static_messageList) == 0:
            print '\nError while initializing FlexRay: configured cold start ID is not correct, check database configuration.\n'
            sys.exit()

        # Prepare fifo configuration
        fifo_config = self.dllTypes.GtFr_FifoCfgType()
        fifo_config.FifoDepth = len(static_messageList)
        fifo_config.FifoEntrySize = max_payload_length
        fifo_config.FifoCriticalLevel = 4
        fifo_config.RejectionFilterChannel = self.dllTypes.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        fifo_config.RejectionFilterValue = 0
        fifo_config.RejectionFilterMask = 0
        fifo_config.RejectionFilterBaseCycle = 0
        fifo_config.RejectionFilterRepetition = 0
        fifo_config.RejectStaticSegment = 1 # Not needed for Controller 1
        fifo_config.RejectNullFrames = 1

        # Create the messagebuf_cfg configuration
        messagebuf_cfg.splm = 0
        messagebuf_cfg.sec = self.dllTypes.GtFr_MsgBufSecurityModeType.GTFR_MSGBUF_SEC_UNLOCK_ALL
        messagebuf_cfg.sMsgBuf = self.dllTypes.GtFr_StaticMsgBufType(len(static_messageList), static_messageList)
        messagebuf_cfg.dMsgBuf = self.dllTypes.GtFr_DynamicMsgBufType(len(dymnamic_messageList), dymnamic_messageList)
        messagebuf_cfg.fifoMsgBuf = fifo_config

        # Store buffer configuration for future use in transmit function
        self.static_messageList_cfg_c1.insert(index, static_messageList)

        return messagebuf_cfg


    def write_fr_frame(self, index, fr_id, mode, data, payload_length, repetition, offset, channel):

        '''
        Description: Writes FlexRay frame to channel.
        Parameter 'index' is the Vector channel index
        Parameter 'fr_id' is the frame ID (slot ID)
        Parameter 'mode' is the TxMode (XL_FR_TX_MODE_CYCLIC/SINGLE_SHOT/NONE) not use, fixed by bufferConfigcontroller
        Parameter 'data' is a list with the data bytes
        Parameter 'payload_length' is the payload length in words
        Parameter 'repetition' is the repetition of the TX frame
        Parameter 'offset' is the frame base
        Parameter 'channel' is the flexray channel used (A=1, B=2, AB=3), not use, fixed by ControlledConfig

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            com.write_fr_frame(0, 0x2B, XL_FR_TX_MODE_CYCLIC, [0x5A, 0x23, 0x78, 0xB1], 8, 2, 0, 1)
        '''
        found_id = False

        # Prepare data buffer with extra 0's in case length to transmit is greather than data
        if (len(data) < payload_length * 2):
            zeroes = [0]*((payload_length * 2) - len(data))
            data.extend(zeroes)

        # Search for the buffer position which contains the requested solt Id
        controllerIndex = 0
        for messageCfg in self.static_messageList_cfg_c0[index]:
            if messageCfg.txMsgBuf.FrameId == fr_id:
                if messageCfg.msgBufTag == self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                    if messageCfg.txMsgBuf.BaseCycle == offset and messageCfg.txMsgBuf.Repetition == repetition:
                        found_id = True
                        buffer_index = messageCfg.txMsgBuf.MsgBufNr
                        if mode == 2:
                            print 'Info send_frame(): Gigabox doesn''t support to change transmission mode in runtine, all static frames are sent in Continuos Mode'
                        break
                # Check if message has been configured in controller 1, to send it
                elif self.static_messageList_cfg_c1[index][0].txMsgBuf.FrameId == fr_id:
                    if self.static_messageList_cfg_c1[index][0].msgBufTag == self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                        if self.static_messageList_cfg_c1[index][0].txMsgBuf.BaseCycle == offset and self.static_messageList_cfg_c1[index][0].txMsgBuf.Repetition == repetition:
                            found_id = True
                            controllerIndex = 1
                            buffer_index = self.static_messageList_cfg_c1[index][0].txMsgBuf.MsgBufNr
                            if mode == 2:
                                print 'Info send_frame(): Gigabox doesn''t support to change transmission mode in runtine, all static frames are sent in Continuos Mode'
                            break
                else:
                    print 'Info send_frame(): Message ID ' + str(fr_id) + ' NOT transmitted because it''s a TX message of the selected ECU under test, ' + self.ecuUnderTest[index]
                    return 0

        # Check if message has been found in static configuration and sent
        if found_id == True:
            result_write = self.dllLear.SendFrame(index, controllerIndex, buffer_index, payload_length * 2, data)
            if result_write != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
                print 'Error: ' + frStatusResult.get(result_write, "UnknownError") + ' while transmitting frame.'
                return 0
        else:
            # Let's look for the message in dynamic configuration
            for messageCfg in self.dynamic_messageList_cfg_c0[index]:
                if messageCfg.txMsgBuf.FrameId == fr_id:
                    if messageCfg.msgBufTag == self.dllTypes.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                        if messageCfg.txMsgBuf.BaseCycle == offset and messageCfg.txMsgBuf.Repetition == repetition:
                            found_id = True
                            buffer_index = messageCfg.txMsgBuf.MsgBufNr
                            if mode == 1:
                                print 'Info send_frame(): Gigabox doesn''t support to change transmission mode in runtine, all dynamic frames are sent in Single Shoot Mode'
                            break

                    else:
                        print 'Info send_frame(): Message NOT transmitted because it''s a TX message of the selected ECU under test, ' + self.ecuUnderTest[index]
                        return 0
            # Check if message has been found in dynamic configuration and sent
            if found_id == True:
                result_write = self.dllLear.SendFrame(index, 0, buffer_index, payload_length * 2, data)
                if result_write != self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
                    print 'Error: ' + frStatusResult.get(result_write, "UnknownError") + ' while transmitting frame.'
                    return 0
            else:
                print 'Info send_frame(): Message not found in Gigabox configuration\n'
                return 0
        return 1


    def read_fr_frame(self, index):
        '''
        Description: Reads FlexRay frame from channel.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [slotID, type, cycleCount, payloadLength, [b0, b1, b2, b3, b4, b5, b6, b7...]]

        Type examples: 128 = START_CYCLE, 129 = RX_FRAME, 131 = TXACK_FRAME, 132 = INVALID FRAME, 136 = STATUS

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            frame_rx = com.read_fr_frame(0)
        '''

        received_events = []

        frEvent = self.dllTypes.GtFr_EventType()
        frQueueStatus = self.dllTypes.GtFr_EventQueueStatusType()

        frQueueStatus.state = self.dllTypes.GtFr_EventQueueStateType.GTFR_QUEUE_SUCCESS

        # Get all events from the queue...
        while frQueueStatus.state != self.dllTypes.GtFr_EventQueueStateType.GTFR_QUEUE_EMPTY:
            result, frEvent, frQueueStatus = self.dll.GtFr_ReceiveEvent(index, frEvent, frQueueStatus)

            if frQueueStatus.state != self.dllTypes.GtFr_EventQueueStateType.GTFR_QUEUE_EMPTY:
                if frEvent.eventTag == self.dllTypes.GtFr_EventTagType.GTFR_CYCLE_START:
                    self.currentCycle[index] = frEvent.eventData.cycleStart.cycleCount
                elif frEvent.eventTag == self.dllTypes.GtFr_EventTagType.GTFR_RX_FRAME:
                    databuff = []
                    data = self.dllLear.Get_ReceiveFrame(frEvent)
                    current_message_size = self.messageIdSize[index].get(frEvent.eventData.rxFrame.slotId)
                    for i in data:
                        databuff.append(i)
                        current_message_size -= 1
                        if current_message_size == 0:
                            break

                    received_events.append([frEvent.eventData.rxFrame.slotId, frEvent.eventTag, frEvent.eventData.rxFrame.cycleCount,
                                            frEvent.eventData.rxFrame.payloadLength, frEvent.timeStamp * 1000, databuff])
                elif frEvent.eventTag == self.dllTypes.GtFr_EventTagType.GTFR_TX_ACKNOWLEDGE:
                    databuff = []
                    data = self.dllLear.Get_ReceiveFrame(frEvent)
                    current_message_size = self.messageIdSize[index].get(frEvent.eventData.txAckFrame.slotId)
                    for i in data:
                        databuff.append(i)
                        current_message_size -= 1
                        if current_message_size == 0:
                            break
                    received_events.append([frEvent.eventData.txAckFrame.slotId, frEvent.eventTag, frEvent.eventData.txAckFrame.cycleCount,
                                            frEvent.eventData.txAckFrame.payloadLength, frEvent.timeStamp * 1000, databuff])
                else:
                    pass #print 'Event Other: ' + str(frEvent.eventTag)

        return received_events


    def get_fr_state(self, index):
        '''
        Description: Report the current FlexRay bus state.

        Returns: statuts of the bus, frStatusTypeEnum
        '''
        status_init = 0
        # Just check controller 0 state, Controller 1, if configured should have same state, as it's bus state
        result, status_init = self.dll.GtFr_GetCtrlState(index, 0, status_init)
        if result == self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            return frStatusTypeEnum.get(status_init, "FR_STATUS_RESERVED")
        else:
            return "FR_STATUS_UNKNOWN"


    def get_fr_cycle(self, index):
        '''
        Description: Report the current FlexRay cycle.

        Returns: cycle number, [0..63]
        '''
        return self.currentCycle[index]


    def close_channel(self, index):
        '''
        Description: Closes communication channel.

        Example:
            com = COM('GIGABOX')
            com.open_fr_channel(0, ...)
            ...
            com.close_channel(0)
        '''

        result = self.dll.GtFr_DeInit()
        if result == self.dllTypes.GtFr_ReturnType.GTFR_SUCCESS:
            # Try to restart usb
            self._usb_gigabox_restart()
            print '\nGigaBox device: channel closed in channel ID ' + str(index) + '\n'
        else:
            print '\nGigaBox device: Error while trying to close FlexRay channels' + '\n'