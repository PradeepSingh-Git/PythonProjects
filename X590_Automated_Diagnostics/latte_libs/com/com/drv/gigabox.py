"""
====================================================================
GigaBox FlexRay DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import time
import os
import sys
import re
try:
    import clr
except ImportError:
    raise ImportError('INFO: GIGABOX device for FLexRay not supported, because "clr" module could not be imported')
try:
    import usb
except ImportError:
    raise ImportError('INFO: GIGABOX device for FLexRay not supported, because "usb" module could not be imported')


__author__ = 'Jesus Fidalgo'
__version__ = '1.1.1'
__email__ = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.1.1 More PEP8 rework
1.1.0 PEP8 rework
1.0.6 Define separate params for max static and dynamic slots allowed.
1.0.5 Raising exceptions instead of sys.exit() calls.
1.0.4 Bugfix: allow to work with more than 2 HW channels.
1.0.3 Modified open_fr_channel, __init and close_channel with improved driver start/stop sequence.
1.0.2 Modified scan_devices method to generate list of detailed channel info.
1.0.1 When generating the message buffers, get the frames with the lower slot_id first.
1.0.0 Initial version
'''


# A few constants from NativeInterface.h
frStatusResult = {
    0x00: "GTFR_INV_REG_ADDR",              # Invalid register address
    0x01: "GTFR_SUCCESS",                   # No Error occured
    0x02: "GTFR_TIMEOUT",                   # Timeout Error
    0x03: "GTFR_INTERFACE_NOT_CONNECTED",   # Interface not connected
    0x04: "GTFR_INV_INTERFACE_IDX",         # Invalid interface index
    0x05: "GTFR_INV_CTRL_IDX",              # Invalid interface index
    0x06: "GTFR_NOT_INITIALIZED",           # This is returned in case of the GtFr_Init has not been called
    0x07: "GTFR_INV_TIMER_IDX",             # Invalid timer index
    0x08: "GTFR_INV_CTRL_STATE",            # Invalid controller state for this function
    0x09: "GTFR_INV_CFG_TAG",               # Invalid configuration tag
    0x0A: "GTFR_ERROR_USB",                 # Error in usb-transmission
    0x0B: "GTFR_INV_MSG_BUF_IDX",           # Message Buffer not configured for transmission.
    0x0C: "GTFR_INV_PARAMETER",             # Invalid parameter
    0x0D: "GTFR_INV_CONFIGURATION",         # Invalid configuration
    0x0E: "GTFR_NOT_SUPPORTED",             # Function is not supported
    0x0F: "GTFR_FIBEX_LOAD_ERRO",           # Fibex Load Error
}

# definitions for statusType
frStatusTypeEnum = {
    0x00: "FR_STATUS_DEFAULT_CONFIG",
    0x01: "FR_STATUS_READY",
    0x02: "FR_STATUS_NORMAL_ACTIVE",
    0x03: "FR_STATUS_NORMAL_PASSIVE",
    0x04: "FR_STATUS_HALT",
    0x05: "FR_STATUS_MONITOR_MODE",
    0x06: "FR_STATUS_AUTORESTART",
    0x0F: "FR_STATUS_CONFIG",
    0x10: "FR_STATUS_WAKEUP_STANDBY",
    0x11: "FR_STATUS_WAKEUP_LISTEN",
    0x12: "FR_STATUS_WAKEUP_SEND",
    0x13: "FR_STATUS_WAKEUP_DETECT",
    0x20: "FR_STATUS_STARTUP_PREPARE",
    0x21: "FR_STATUS_COLDSTART_LISTEN",
    0x22: "FR_STATUS_COLDSTART_COLLISION_RESOLUTION",
    0x23: "FR_STATUS_COLDSTART_CONSISTENCY_CHECK",
    0x24: "FR_STATUS_COLDSTART_GAP",
    0x25: "FR_STATUS_COLDSTART_JOIN",
    0x26: "FR_STATUS_INTEGRATION_COLDSTART_CHECK",
    0x27: "FR_STATUS_INTEGRATION_LISTEN",
    0x28: "FR_STATUS_INTEGRATION_CONSISTENCY_CHECK",
    0x29: "FR_STATUS_INITIALIZE_SCHEDULE",
    0x2a: "FR_STATUS_ABORT_STARTUP",
    0x2b: "FR_STATUS_STARTUP_SUCCESS",
}

# Gigabox DLL has a buffer limit for managing the FlexRay slots. Over this value, Init of the Channel is not possible
# Please keep GIGABOX_MAX_ALL_SLOTS equal to 69, and adjust GIGABOX_MAX_STATIC_SLOTS as desired. If you want to load
# all static slots and no dynamic slots, set GIGABOX_MAX_STATIC_SLOTS = GIGABOX_MAX_STATIC_SLOTS. If you want to load
# all dynamic slots, set GIGABOX_MAX_STATIC_SLOTS to a low value.
GIGABOX_MAX_STATIC_SLOTS = 40
GIGABOX_MAX_ALL_SLOTS = 69


class GIGABOX:

    def __init__(self):
        """
        Description: Constructor. Loads LearGigaBoxLib.dll_core, opens drivers and reads conencted Kvaser devices.
        """
        self.canlib_tx_hnd = {}
        self.canlib_rx_hnd = {}
        self.ecu_under_test = []
        self.message_id_size = []
        self.current_cycle = {}
        self.static_messageList_cfg_c0 = []
        self.static_messageList_cfg_c1 = []
        self.dymanic_messageList_cfg_c0 = []
        self.dynamic_messageList_cfg_c0 = []
        self.channel_list = []  # List of strings with channel info

        # Load DLL's
        try:
            self.dll_path = os.path.dirname(os.path.abspath(__file__)) + '\GtFrNET.dll'
            clr.AddReference(self.dll_path)
            self.dll_path = os.path.dirname(os.path.abspath(__file__)) + '\LearGigaBoxAPI.dll'
            clr.AddReference(self.dll_path)
        except WindowsError:
            print 'INFO: Failed to load DLL, reasons could be:'
            print '      - 64 bits version of Python being used. It must be 32 bits version (also called x86)'
            print '      - Pythonnet not installed. Please execute LATTE\Com\Trunk\drivers\gigabox' \
                  '\Install_Pythonnet_for_GtFrNET.bat'
            print '      - GIGABOX drivers not installed. Please execute LATTE\Com\Trunk\drivers\gigabox' \
                  '\gigabox-flex-i-driver-library-setup-v1-3-5_639_1466427547.exe'
            sys.exit()

        # noinspection PyUnresolvedReferences
        from GtFrNET import Types
        # noinspection PyUnresolvedReferences
        from GtFrNET import Core
        # noinspection PyUnresolvedReferences
        from LearGigaBoxAPI import LearGigaBoxAPI

        self.dll_types = Types
        self.dll_core = Core.GtFr_Api
        self.dll_lear = LearGigaBoxAPI

        print 'INFO: Initializing GIGABOX device, this may take some time...'
        result_init = self.dll_core.GtFr_Init()
        if result_init != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            self._usb_gigabox_restart()

    def _usb_gigabox_restart(self):
        # try to restart usb
        usb_devices = usb.core.find(find_all=True, idVendor=0x2918, idProduct=0x0000)
        for dev in usb_devices:
            if re.match(r'GIGABOX flex-i', usb.util.get_string(dev, dev.iProduct)):
                dev.reset()
        result_init = self.dll_core.GtFr_Init()
        if result_init != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            raise Exception('ERROR: During GIGABOX driver '
                            'initialization: {0}'.format(frStatusResult.get(result_init, 'UnknownError')))

    def scan_devices(self):
        """
        Description: Scans all gigabox devices connected.
        Returns list of devices found, and prints useful info describing the devices connected and channels available

        Example:
            com = Com('GIGABOX')
            com.scan_devices()
        """
        num_devices = 0
        result, num_devices = self.dll_core.GtFr_GetInterfaceCount(num_devices)
        if result == self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            for device_index in range(num_devices):
                devices_info_ext = self.dll_types.GtFr_InterfaceExtInfoType()
                result, devices_info_ext = self.dll_core.GtFr_GetInterfaceExtInfo(device_index, devices_info_ext)
                if result == self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
                    print 'INFO: The following GIGABOX device channel is ' \
                          'available as LATTE channel ID {}: '.format(str(device_index))
                    print '      {} {}'.format('Device S/N:', str(devices_info_ext.serial))
                    self.channel_list.append('GIGABOX {} Channel {}'.format(str(devices_info_ext.serial),
                                                                            str(device_index)))
                    devices_info = self.dll_types.GtFr_InterfaceInfoType()
                    result, devices_info = self.dll_core.GtFr_GetInterfaceInfo(device_index, devices_info)
                    if result == self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
                        print '      {} {}'.format('Version:', devices_info.hardwareInfo.firmwareVersion)
                else:
                    raise Exception('ERROR: Reading GIGABOX device '
                                    'information: {}'.format(frStatusResult.get(result, 'UnknownError')))
        else:
            raise Exception('ERROR: Reading GIGABOX device '
                            'information: {}'.format(frStatusResult.get(result, 'UnknownError')))

        return self.channel_list

    def open_fr_channel(self, index, cluster_config, message_config, ecu_under_test):
        """
        Description: Opens FlexRay channel.  E-Ray CC and Fujitsu CC will be activated based on cluster config.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'cluster_config' is an object of class ClusterConfig (defined in fibex.py),
        contains the cluster configuration parameters.
        Parameter 'ecu_under_test' defines the ECU under test to determine which messages will be defined as RX
        (messages defined as TX from the ECU under test).

        Example:
            com = XLCOM()
            com.open_fr_channel(0, cluster_config, message_config, 'ECM')
        """
        # Check if requested ecu_under_test is present in database (FIBEX, ECUextract...)
        print 'INFO: Opening GIGABOX FlexRay channel, this may take some time...'
        found_ecu = False
        if ecu_under_test:
            for message in message_config.keys():
                if message_config.get(message).transmitter == ecu_under_test:
                    found_ecu = True
                    break
        if found_ecu is False:
            print 'ERROR: While initializing GIGABOX FlexRay channel {}, ecu under ' \
                  'test {} not present in database'.format(str(index), ecu_under_test)
            sys.exit()
        self.ecu_under_test.insert(index, ecu_under_test)

        gftr_success = self.dll_types.GtFr_ReturnType.GTFR_SUCCESS

        result_init = self.dll_core.GtFr_Init()
        if result_init != gftr_success:
            # Try to restart usb
            self._usb_gigabox_restart()

        # Prepare Gigabox configuration structs based on cluster Config
        controller_cfg = self._generate_controller_config(cluster_config, cluster_config.erayID)
        protocol_cfg = self._generate_protocol_config(cluster_config)
        messagebuf_cfg = self._generate_buffer_config_controller0(index, cluster_config, message_config)

        # Setup Controller 0 configuration for startup and sync frames for E-ray
        result_ctrl = self.dll_core.GtFr_InitCtrl(index, 0, controller_cfg)
        result_protocol = self.dll_core.GtFr_InitProtocol(index, 0, protocol_cfg)
        result_msgbuf = self.dll_core.GtFr_InitMsgBuf(index, 0, messagebuf_cfg)
        if result_ctrl == gftr_success and result_protocol == gftr_success and result_msgbuf == gftr_success:
            # Initialize controller 0 with the configuration from the previous steps
            result_init = self._init_controller(index, 0)
            if result_init == gftr_success:
                print 'INFO: GIGABOX device FlexRay channel open in LATTE channel ID {}, ' \
                      'controller 0'.format(str(index))
            else:
                print 'ERROR: While initializing GIGABOX FlexRay channel {}, controller 0. ' \
                      'Error: {}'.format(str(index), frStatusResult.get(result_init, 'UnknownError'))
                sys.exit()
        else:
            print 'ERROR: While initializing GIGABOX FlexRay channel {}, controller 0. ' \
                  'Error reported:'.format(str(index))
            print '   - InitCtrl result: ' + frStatusResult.get(result_ctrl, 'UnknownError')
            print '   - InitProtocol result: ' + frStatusResult.get(result_protocol, 'UnknownError')
            print '   - InitMsgBuf result: ' + frStatusResult.get(result_msgbuf, 'UnknownError')
            sys.exit()

        # Setup just startup/sync frames for Second controller, if configured
        if cluster_config.coldID != 0:
            controller_cfg_2 = self._generate_controller_config(cluster_config, cluster_config.coldID)
            messagebuf_cfg_2 = self._generate_buffer_config_controller1(index, cluster_config, message_config)

            # Setup Controller 1 configuration
            result_ctrl = self.dll_core.GtFr_InitCtrl(index, 1, controller_cfg_2)
            result_protocol = self.dll_core.GtFr_InitProtocol(index, 1, protocol_cfg)
            result_msgbuf = self.dll_core.GtFr_InitMsgBuf(index, 1, messagebuf_cfg_2)
            if result_ctrl == gftr_success and result_protocol == gftr_success and result_msgbuf == gftr_success:
                # Initialize controller 0 with the configuration from the previous steps
                result_init = self._init_controller(index, 1)
                if result_init == gftr_success:
                    print 'INFO: GIGABOX device FlexRay channel open in LATTE channel ID {}, ' \
                          'controller 1'.format(str(index))
                else:
                    print 'ERROR: While initializing GIGABOX FlexRay channel {}, controller 1. ' \
                          'Error: {}'.format(str(index), frStatusResult.get(result_init, 'UnknownError'))

                    sys.exit()
            else:
                print 'ERROR: While initializing GIGABOX FlexRay channel {}, controller 1. ' \
                      'Error reported:'.format(str(index))
                print '   - InitCtrl result: ' + frStatusResult.get(result_ctrl, 'UnknownError')
                print '   - InitProtocol result: ' + frStatusResult.get(result_protocol, 'UnknownError')
                print '   - InitMsgBuf result: ' + frStatusResult.get(result_msgbuf, 'UnknownError')
                sys.exit()

        return True

    def _init_controller(self, index, controller, init_timeout=2.0):
        """
        Description: Execute the dll_core calls to initiate the Gigabox Flexray channel,
        configuration must be set in advance
        Parameter 'index'  contain the gigabox channel index.
        Parameter 'controller' contains the controller index, 0 or 1
        """

        # Initialize controller with the configuration from the previous steps
        result = self.dll_core.GtFr_ExecuteCommand(index, controller, self.dll_types.GtFr_CommandType.GTFR_CMD_INIT)
        if result != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            return result

        # Wait for controller initialization
        time_start = time.clock()
        time_elapsed = 0.0
        status_init = 0
        result, status_init = self.dll_core.GtFr_GetCtrlState(index, controller, status_init)
        # Wait till READY state is reached
        while status_init is not self.dll_types.GtFr_PocStateType.GTFR_PROTSTATE_READY and \
                result is self.dll_types.GtFr_ReturnType.GTFR_SUCCESS and \
                time_elapsed < init_timeout:
            result, status_init = self.dll_core.GtFr_GetCtrlState(index, controller, status_init)
            time_elapsed = time.clock() - time_start
        if result is not self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            return result
        elif time_elapsed >= init_timeout:
            return self.dll_types.GtFr_ReturnType.GTFR_TIMEOUT

        # Now start the comunication in the controller
        result = self.dll_core.GtFr_ExecuteCommand(index, controller, self.dll_types.GtFr_CommandType.GTFR_CMD_START)
        if result != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            return result

        return self.dll_types.GtFr_ReturnType.GTFR_SUCCESS

    def _generate_controller_config(self, cluster_config, cold_start):
        """
        Description: Creates the Gigabox Controller configuration based on database cluster info.

        Returns: controller_cfg of GtFr_CtrlCfgType
        """
        controller_cfg = self.dll_types.GtFr_CtrlCfgType()

        controller_cfg.AutoRestart = 0
        if cluster_config.baudrate == 5000000:
            controller_cfg.BaudRate = self.dll_types.GtFr_BaudRateType.GTFR_BAUDRATE_5M
        elif cluster_config.baudrate == 10000000:
            controller_cfg.BaudRate = self.dll_types.GtFr_BaudRateType.GTFR_BAUDRATE_10M
        else:
            controller_cfg.BaudRate = self.dll_types.GtFr_BaudRateType.GTFR_BAUDRATE_2M5
        if cluster_config.erayChannel == 1:
            controller_cfg.ChannelEnable = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_A
        elif cluster_config.erayChannel == 2:
            controller_cfg.ChannelEnable = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_B
        elif cluster_config.erayChannel == 3:
            controller_cfg.ChannelEnable = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_BOTH
        else:
            controller_cfg.ChannelEnable = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        if cold_start != 0:
            controller_cfg.ColdstartNode = long(1)
        else:
            controller_cfg.ColdstartNode = long(0)
        controller_cfg.MediaAccessTestA = 0
        controller_cfg.MediaAccessTestB = 0

        interrupt_cfg = self.dll_types.GtFr_InterruptCfgType()
        status_event_cfg = self.dll_types.GtFr_EventEnableTypes()
        status_event_cfg.wakeupStatus = 0
        status_event_cfg.collisionAvoidance = 0
        status_event_cfg.cycleStart = 1
        status_event_cfg.transmitInterrupt = 1
        status_event_cfg.receiveInterrupt = 1
        status_event_cfg.fifo = 0
        status_event_cfg.nmvChanged = 0
        status_event_cfg.stopWatch = 0
        status_event_cfg.startupCompleted = 0
        status_event_cfg.dynamicSegmentStart = 0
        status_event_cfg.wakeupPatternA = 0
        status_event_cfg.mtsReceivedA = 0
        status_event_cfg.wakeupPatternB = 0
        status_event_cfg.mtsReceivedB = 0
        interrupt_cfg.statusEventEnable = status_event_cfg
        controller_cfg.InterruptConfig = interrupt_cfg

        return controller_cfg

    def _generate_protocol_config(self, cluster_config):
        """
        Description: Creates the Gigabox Protocol configuration based on database cluster info.

        Returns: protocol_cfg of GtFr_ProtocolCfgType
        """
        protocol_cfg = self.dll_types.GtFr_ProtocolCfgType()

        protocol_cfg.gColdstartAttempts = cluster_config.gColdStartAttempts
        protocol_cfg.gListenNoise = cluster_config.gListenNoise
        protocol_cfg.pMacroInitialOffsetA = cluster_config.pMacroInitialOffsetA
        protocol_cfg.pMacroInitialOffsetB = cluster_config.pMacroInitialOffsetB
        protocol_cfg.gMacroPerCycle = cluster_config.gMacroPerCycle
        protocol_cfg.gMaxWithoutClkCorrFatal = cluster_config.gMaxWithoutClockCorrectionFatal
        protocol_cfg.gMaxWithoutClkCorrPassive = cluster_config.gMaxWithoutClockCorrectionPassive
        protocol_cfg.gNetworkManagementVectorLength = cluster_config.gNetworkManagementVectorLength
        protocol_cfg.gNumberOfMiniSlots = cluster_config.gNumberOfMinislots
        protocol_cfg.gNumberOfStaticSlots = cluster_config.gNumberOfStaticSlots
        protocol_cfg.gOffsetCorrectionStart = cluster_config.gOffsetCorrectionStart
        protocol_cfg.gPayloadLengthStatic = cluster_config.gPayloadLengthStatic
        protocol_cfg.gSyncNodeMax = cluster_config.gSyncNodeMax

        protocol_cfg.gdActionPointOffset = cluster_config.gdActionPointOffset
        protocol_cfg.gdCasRxLowMax = cluster_config.gdCASRxLowMax
        protocol_cfg.gdDynamicSlotIdlePhase = cluster_config.gdDynamicSlotIdlePhase
        protocol_cfg.gdMiniSlot = cluster_config.gdMinislot
        protocol_cfg.gdMiniSlotActionPointOffset = cluster_config.gdMiniSlotActionPointOffset
        protocol_cfg.gdNetworkIdleTime = cluster_config.gdNIT
        protocol_cfg.gdStaticSlot = cluster_config.gdStaticSlot
        protocol_cfg.gdTssTransmitter = cluster_config.gdTSSTransmitter
        protocol_cfg.gdWakeupSymbolRxIdle = cluster_config.gdWakeupSymbolRxIdle
        protocol_cfg.gdWakeupSymbolRxLow = cluster_config.gdWakeupSymbolRxLow
        protocol_cfg.gdWakeupSymbolRxWindow = cluster_config.gdWakeupSymbolRxWindow
        protocol_cfg.gdWakeupSymbolTxIdle = cluster_config.gdWakeupSymbolTxIdle
        protocol_cfg.gdWakeupSymbolTxLow = cluster_config.gdWakeupSymbolTxLow

        protocol_cfg.pAllowHaltDueToClock = cluster_config.pAllowHaltDueToClock
        protocol_cfg.pAllowPassiveToActive = cluster_config.pAllowPassiveToActive
        protocol_cfg.pClusterDriftDamping = cluster_config.pClusterDriftDamping
        protocol_cfg.pDecodingCorrection = cluster_config.pDecodingCorrection
        protocol_cfg.pDelayCompensationA = cluster_config.pDelayCompensationA
        protocol_cfg.pDelayCompensationB = cluster_config.pDelayCompensationB
        protocol_cfg.pExternOffsetCorrection = cluster_config.pExternOffsetCorrection
        protocol_cfg.pExternRateCorrection = cluster_config.pExternRateCorrection
        protocol_cfg.pKeySlotUsedForStartup = cluster_config.pKeySlotUsedForStartup
        protocol_cfg.pKeySlotUsedForSync = cluster_config.pKeySlotUsedForSync
        protocol_cfg.pLatestTx = cluster_config.pLatestTx
        protocol_cfg.pMicroInitialOffsetA = cluster_config.pMacroInitialOffsetA
        protocol_cfg.pMicroInitialOffsetB = cluster_config.pMacroInitialOffsetB
        protocol_cfg.pMicroPerCycle = cluster_config.pMicroPerCycle
        protocol_cfg.pOffsetCorrectionOut = cluster_config.pOffsetCorrectionOut
        protocol_cfg.pRateCorrectionOut = cluster_config.pRateCorrectionOut
        protocol_cfg.pSingleSlotEnabled = cluster_config.pSingleSlotEnabled
        protocol_cfg.pWakeupChannel = cluster_config.pWakeupChannel
        protocol_cfg.pWakeupPattern = cluster_config.pWakeupPattern

        protocol_cfg.pdAcceptedStartupRange = cluster_config.pdAcceptedStartupRange
        protocol_cfg.pdListenTimeout = cluster_config.pdListenTimeout
        protocol_cfg.pdMaxDrift = cluster_config.pdMaxDrift

        return protocol_cfg

    def _generate_buffer_config_controller0(self, index, cluster_config, message_config):
        """
        Description: Creates the Gigabox Buffer configuration for Controller 0.
                     It includes all Static and Dynamic messages from the database (FIBEX, ECUextract...).
                     The RX or TX configuration is based on the 'ecu_under_test' configuration.
                     Gigabox DLL has a limitation of a maximum of 24 Rx/Tx positions on the FIFO, so if more messages
                     are present in the database, they are not added. Error message will be displayed.

        Returns: messagebuf_cfg of GtFr_MsgBufCfgType
        """
        messagebuf_cfg = self.dll_types.GtFr_MsgBufCfgType()

        # Generate a list of all static message with its configuration and gigabox format
        static_message_list = []
        max_payload_length = 0
        message_id_size_temp = {}  # Dictionary which will include size of each frame from key slot_id
        if cluster_config.erayID == 0:
            buffer_index = 0
        else:
            buffer_index = 1  # Position 0 is reserved for startup synch message
        for message in sorted(message_config, key=lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] < cluster_config.gNumberOfStaticSlots:
                # Check if it has to be a RX frame in Latte:
                #  - It's a startup/Synch TX message of the Controller 1 or
                #  - It's a TX message of the ECU under test but NOT a startup/Synch TX message of the Controller 0
                if (message_config.get(message).slot_id[0] == cluster_config.coldID) or \
                   (message_config.get(message).transmitter == self.ecu_under_test[index] and
                   (message_config.get(message).slot_id[0] != cluster_config.erayID or cluster_config.erayID == 0)):
                    static_message_rx = self.dll_types.GtFr_MsgBufType()
                    static_message_rx.msgBufTag = self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_RX
                    temp_rx_msg_buf = self.dll_types.GtFr_RxMsgBufCfgType()
                    temp_rx_msg_buf.MsgBufNr = buffer_index
                    buffer_index = buffer_index + 1
                    temp_rx_msg_buf.FrameId = message_config.get(message).slot_id[0]
                    length_in_words = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_rx_msg_buf.PayloadLength = length_in_words
                    if max_payload_length < length_in_words:
                        max_payload_length = length_in_words
                    temp_rx_msg_buf.MsgBufInterruptEnable = 1
                    if cluster_config.erayChannel == 1:
                        temp_rx_msg_buf.ChannelAEnable = 1
                        temp_rx_msg_buf.ChannelBEnable = 0
                    elif cluster_config.erayChannel == 2:
                        temp_rx_msg_buf.ChannelAEnable = 0
                        temp_rx_msg_buf.ChannelBEnable = 1
                    elif cluster_config.erayChannel == 3:
                        temp_rx_msg_buf.ChannelAEnable = 1
                        temp_rx_msg_buf.ChannelBEnable = 1
                    else:
                        temp_rx_msg_buf.ChannelAEnable = 0
                        temp_rx_msg_buf.ChannelBEnable = 0
                    temp_rx_msg_buf.BaseCycle = message_config.get(message).offset
                    temp_rx_msg_buf.Repetition = message_config.get(message).repetition
                    static_message_rx.rxMsgBuf = temp_rx_msg_buf
                    static_message_list.append(static_message_rx)

                else:
                    # Message it's a RX messages from ECU under test (or not used by ECU
                    # under test), so add it as a TX in Latte
                    static_message_tx = self.dll_types.GtFr_MsgBufType()
                    static_message_tx.msgBufTag = self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX
                    temp_tx_msg_buf = self.dll_types.GtFr_TxMsgBufCfgType()
                    # Cold start message must be always in first fifo position
                    if message_config.get(message).slot_id[0] == cluster_config.erayID:
                        temp_tx_msg_buf.MsgBufNr = 0
                    else:
                        temp_tx_msg_buf.MsgBufNr = buffer_index
                        buffer_index = buffer_index + 1
                    temp_tx_msg_buf.FrameId = message_config.get(message).slot_id[0]
                    length_in_words = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_tx_msg_buf.PayloadLength = length_in_words
                    if max_payload_length < length_in_words:
                        max_payload_length = length_in_words
                    temp_tx_msg_buf.MsgBufInterruptEnable = 1
                    if cluster_config.erayChannel == 1:
                        temp_tx_msg_buf.ChannelAEnable = 1
                        temp_tx_msg_buf.ChannelBEnable = 0
                    elif cluster_config.erayChannel == 2:
                        temp_tx_msg_buf.ChannelAEnable = 0
                        temp_tx_msg_buf.ChannelBEnable = 1
                    elif cluster_config.erayChannel == 3:
                        temp_tx_msg_buf.ChannelAEnable = 1
                        temp_tx_msg_buf.ChannelBEnable = 1
                    else:
                        temp_tx_msg_buf.ChannelAEnable = 0
                        temp_tx_msg_buf.ChannelBEnable = 0
                    temp_tx_msg_buf.BaseCycle = message_config.get(message).offset
                    temp_tx_msg_buf.Repetition = message_config.get(message).repetition
                    temp_tx_msg_buf.PayloadPreamble = 0
                    temp_tx_msg_buf.HeaderCrc = 0
                    temp_tx_msg_buf.TransmissionMode = self.dll_types.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_CONTINOUS
                    static_message_tx.txMsgBuf = temp_tx_msg_buf
                    # Check if message is the cold start, in order to put in fisrt position
                    if message_config.get(message).slot_id[0] == cluster_config.erayID:
                        static_message_list.insert(0, static_message_tx)
                    else:
                        static_message_list.append(static_message_tx)
                # Add dictionary item
                message_id_size_temp[message_config.get(message).slot_id[0]] = message_config.get(message).length

            if len(static_message_list) > GIGABOX_MAX_STATIC_SLOTS:
                print 'INFO: While initializing FlexRay, number of defined Static Messages is greather than ' \
                      'the max allowed static slots ({})'.format(str(GIGABOX_MAX_STATIC_SLOTS))
                print 'INFO: There will be limitation on messages transmission/reception'
                break

        # Generate a list of all dinamic message with its configuration and gigabox format
        dinamic_message_list = []
        dinamic_buffer_index = buffer_index
        for message in sorted(message_config, key=lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] >= cluster_config.gNumberOfStaticSlots:
                # Check if it's a TX messages from ECU under test, so add it as a RX in Latte
                if message_config.get(message).transmitter == self.ecu_under_test[index]:
                    dinamic_message = self.dll_types.GtFr_MsgBufType()
                    dinamic_message.msgBufTag = self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_RX
                    temp_rx_msg_buf = self.dll_types.GtFr_RxMsgBufCfgType()
                    temp_rx_msg_buf.MsgBufNr = dinamic_buffer_index
                    dinamic_buffer_index = dinamic_buffer_index + 1
                    temp_rx_msg_buf.FrameId = message_config.get(message).slot_id[0]
                    length_in_words = message_config.get(message).length / 2 + message_config.get(message).length % 2
                    temp_rx_msg_buf.PayloadLength = length_in_words
                    if max_payload_length < length_in_words:
                        max_payload_length = length_in_words
                    temp_rx_msg_buf.MsgBufInterruptEnable = 1
                    if cluster_config.erayChannel == 1:
                        temp_rx_msg_buf.ChannelAEnable = 1
                        temp_rx_msg_buf.ChannelBEnable = 0
                    elif cluster_config.erayChannel == 2:
                        temp_rx_msg_buf.ChannelAEnable = 0
                        temp_rx_msg_buf.ChannelBEnable = 1
                    elif cluster_config.erayChannel == 3:
                        temp_rx_msg_buf.ChannelAEnable = 1
                        temp_rx_msg_buf.ChannelBEnable = 1
                    else:
                        temp_rx_msg_buf.ChannelAEnable = 0
                        temp_rx_msg_buf.ChannelBEnable = 0
                    temp_rx_msg_buf.BaseCycle = message_config.get(message).offset
                    temp_rx_msg_buf.Repetition = message_config.get(message).repetition
                    dinamic_message.rxMsgBuf = temp_rx_msg_buf
                    dinamic_message_list.append(dinamic_message)

                else:
                    # Message it's a RX messages from ECU under test (or not used by ECU
                    # under test), so add it as a TX in Latte
                    dinamic_message = self.dll_types.GtFr_MsgBufType()
                    dinamic_message.msgBufTag = self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX
                    temp_tx_msg_buf = self.dll_types.GtFr_TxMsgBufCfgType()
                    temp_tx_msg_buf.MsgBufNr = dinamic_buffer_index
                    dinamic_buffer_index = dinamic_buffer_index + 1
                    temp_tx_msg_buf.FrameId = message_config.get(message).slot_id[0]
                    length_in_words = message_config.get(message).length/2 + message_config.get(message).length % 2
                    temp_tx_msg_buf.PayloadLength = length_in_words
                    if max_payload_length < length_in_words:
                        max_payload_length = length_in_words
                    temp_tx_msg_buf.MsgBufInterruptEnable = 1
                    if cluster_config.erayChannel == 1:
                        temp_tx_msg_buf.ChannelAEnable = 1
                        temp_tx_msg_buf.ChannelBEnable = 0
                    elif cluster_config.erayChannel == 2:
                        temp_tx_msg_buf.ChannelAEnable = 0
                        temp_tx_msg_buf.ChannelBEnable = 1
                    elif cluster_config.erayChannel == 3:
                        temp_tx_msg_buf.ChannelAEnable = 1
                        temp_tx_msg_buf.ChannelBEnable = 0
                        # NOTE: If AB configured, Dynamic messages are not sent... reason unknown
                    else:
                        temp_tx_msg_buf.ChannelAEnable = 0
                        temp_tx_msg_buf.ChannelBEnable = 0
                    temp_tx_msg_buf.BaseCycle = message_config.get(message).offset
                    temp_tx_msg_buf.Repetition = message_config.get(message).repetition
                    temp_tx_msg_buf.PayloadPreamble = 0
                    temp_tx_msg_buf.HeaderCrc = 0
                    temp_tx_msg_buf.TransmissionMode = self.dll_types.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_SINGLE_SHOT
                    dinamic_message.txMsgBuf = temp_tx_msg_buf
                    dinamic_message_list.append(dinamic_message)
                # Add dictionary item
                message_id_size_temp[message_config.get(message).slot_id[0]] = message_config.get(message).length

            if (len(static_message_list) + len(dinamic_message_list)) > GIGABOX_MAX_ALL_SLOTS:
                print 'INFO: While initializing FlexRay, number of defined Static and Dynamic Messages is greather ' \
                      'than the max allowed slots: {}'.format(str(GIGABOX_MAX_ALL_SLOTS))
                print 'INFO: There will be limitation on messages transmission/reception'
                break

        # Prepare fifo configuration
        fifo_config = self.dll_types.GtFr_FifoCfgType()
        fifo_config.FifoDepth = 0  # FIFO not used
        fifo_config.FifoEntrySize = max_payload_length
        fifo_config.FifoCriticalLevel = 4
        fifo_config.RejectionFilterChannel = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        fifo_config.RejectionFilterValue = 0
        fifo_config.RejectionFilterMask = 0
        fifo_config.RejectionFilterBaseCycle = 0
        fifo_config.RejectionFilterRepetition = 0
        fifo_config.RejectStaticSegment = 0
        fifo_config.RejectNullFrames = 1

        # Create the messagebuf_cfg configuration
        messagebuf_cfg.splm = 0
        messagebuf_cfg.sec = self.dll_types.GtFr_MsgBufSecurityModeType.GTFR_MSGBUF_SEC_UNLOCK_ALL
        messagebuf_cfg.sMsgBuf = self.dll_types.GtFr_StaticMsgBufType(len(static_message_list), static_message_list)
        messagebuf_cfg.dMsgBuf = self.dll_types.GtFr_DynamicMsgBufType(len(dinamic_message_list), dinamic_message_list)
        messagebuf_cfg.fifoMsgBuf = fifo_config

        # Store buffer configuration for future use in transmit function
        self.static_messageList_cfg_c0.insert(index, static_message_list)
        self.dynamic_messageList_cfg_c0.insert(index, dinamic_message_list)
        self.message_id_size.insert(index, message_id_size_temp)

        return messagebuf_cfg

    def _generate_buffer_config_controller1(self, index, cluster_config, message_config):
        """
        Description: Creates the Gigabox Buffer configuration for Controller 1.
                     Controller 1 is only used in case of secondary Startup/Synch is confugured. So only
                     one position is configured.

        Returns: messagebuf_cfg of GtFr_MsgBufCfgType
        """
        messagebuf_cfg = self.dll_types.GtFr_MsgBufCfgType()

        # Generate a list of all static message with its configuration and gigabox format
        static_message_list = []
        dymnamic_message_list = []
        max_payload_length = 0
        buffer_index = 0
        for message in sorted(message_config, key=lambda name: message_config[name].slot_id):
            # Check if message is defined in static slots
            if message_config.get(message).slot_id[0] == cluster_config.coldID:
                static_message_tx = self.dll_types.GtFr_MsgBufType()
                static_message_tx.msgBufTag = self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX
                temp_tx_msg_buf = self.dll_types.GtFr_TxMsgBufCfgType()
                temp_tx_msg_buf.MsgBufNr = buffer_index
                temp_tx_msg_buf.FrameId = message_config.get(message).slot_id[0]
                length_in_words = message_config.get(message).length / 2 + message_config.get(message).length % 2
                temp_tx_msg_buf.PayloadLength = length_in_words
                temp_tx_msg_buf.MsgBufInterruptEnable = 0
                if cluster_config.erayChannel == 1:
                    temp_tx_msg_buf.ChannelAEnable = 1
                    temp_tx_msg_buf.ChannelBEnable = 0
                elif cluster_config.erayChannel == 2:
                    temp_tx_msg_buf.ChannelAEnable = 0
                    temp_tx_msg_buf.ChannelBEnable = 1
                elif cluster_config.erayChannel == 3:
                    temp_tx_msg_buf.ChannelAEnable = 1
                    temp_tx_msg_buf.ChannelBEnable = 1
                else:
                    temp_tx_msg_buf.ChannelAEnable = 0
                    temp_tx_msg_buf.ChannelBEnable = 0
                temp_tx_msg_buf.BaseCycle = message_config.get(message).offset
                temp_tx_msg_buf.Repetition = message_config.get(message).repetition
                temp_tx_msg_buf.PayloadPreamble = 0
                temp_tx_msg_buf.HeaderCrc = 0
                temp_tx_msg_buf.TransmissionMode = self.dll_types.GtFr_MsgBufTxModeType.GTFR_TX_MSGBUF_CONTINOUS
                static_message_tx.txMsgBuf = temp_tx_msg_buf
                static_message_list.append(static_message_tx)
                break

        if len(static_message_list) == 0:
            print 'ERROR: initializing FlexRay. Configured cold start ID ' \
                  'is not correct, check database configuration'
            sys.exit()

        # Prepare fifo configuration
        fifo_config = self.dll_types.GtFr_FifoCfgType()
        fifo_config.FifoDepth = len(static_message_list)
        fifo_config.FifoEntrySize = max_payload_length
        fifo_config.FifoCriticalLevel = 4
        fifo_config.RejectionFilterChannel = self.dll_types.GtFr_ChannelsType.GTFR_CHANNELS_NONE
        fifo_config.RejectionFilterValue = 0
        fifo_config.RejectionFilterMask = 0
        fifo_config.RejectionFilterBaseCycle = 0
        fifo_config.RejectionFilterRepetition = 0
        fifo_config.RejectStaticSegment = 1  # Not needed for Controller 1
        fifo_config.RejectNullFrames = 1

        # Create the messagebuf_cfg configuration
        messagebuf_cfg.splm = 0
        messagebuf_cfg.sec = self.dll_types.GtFr_MsgBufSecurityModeType.GTFR_MSGBUF_SEC_UNLOCK_ALL
        messagebuf_cfg.sMsgBuf = self.dll_types.GtFr_StaticMsgBufType(len(static_message_list), static_message_list)
        messagebuf_cfg.dMsgBuf = self.dll_types.GtFr_DynamicMsgBufType(len(dymnamic_message_list),
                                                                       dymnamic_message_list)
        messagebuf_cfg.fifoMsgBuf = fifo_config

        # Store buffer configuration for future use in transmit function
        self.static_messageList_cfg_c1.insert(index, static_message_list)

        return messagebuf_cfg

    # Parameter 'channel' not used, but left for compatibility with vxl_fr.py method write_fr_frame
    # noinspection PyUnusedLocal
    def write_fr_frame(self, index, fr_id, mode, data, payload_length, repetition, offset, channel=None):
        """
        Description: Writes FlexRay frame to channel.
        Parameter 'index' is the Vector channel index
        Parameter 'fr_id' is the frame ID (slot ID)
        Parameter 'mode' is the TxMode (XL_FR_TX_MODE_CYCLIC/SINGLE_SHOT/NONE) not use, fixed by bufferConfigcontroller
        Parameter 'data' is a list with the data bytes
        Parameter 'payload_length' is the payload length in words
        Parameter 'repetition' is the repetition of the TX frame
        Parameter 'offset' is the frame base
        Parameter 'channel' not used, left for compatibility with vxl_fr.py

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            com.write_fr_frame(0, 0x2B, XL_FR_TX_MODE_CYCLIC, [0x5A, 0x23, 0x78, 0xB1], 8, 2, 0, 1)
        """
        found_id = False
        buffer_index = None

        # Prepare data buffer with extra 0's in case length to transmit is greather than data
        if len(data) < payload_length * 2:
            zeroes = [0]*((payload_length * 2) - len(data))
            data.extend(zeroes)

        # Search for the buffer position which contains the requested solt Id
        controller_index = 0
        for messageCfg in self.static_messageList_cfg_c0[index]:
            if messageCfg.txMsgBuf.FrameId == fr_id:
                if messageCfg.msgBufTag == self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                    if messageCfg.txMsgBuf.BaseCycle == offset and messageCfg.txMsgBuf.Repetition == repetition:
                        found_id = True
                        buffer_index = messageCfg.txMsgBuf.MsgBufNr
                        if mode == 2:
                            print 'INFO: GIGABOX does not support to change transmission ' \
                                  'mode in runtine, all static frames are sent in Continuos Mode'
                        break
                # Check if message has been configured in controller 1, to send it
                elif self.static_messageList_cfg_c1[index][0].txMsgBuf.FrameId == fr_id:
                    if self.static_messageList_cfg_c1[index][0].msgBufTag == \
                            self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                        if self.static_messageList_cfg_c1[index][0].txMsgBuf.BaseCycle == offset and \
                                self.static_messageList_cfg_c1[index][0].txMsgBuf.Repetition == repetition:
                            found_id = True
                            controller_index = 1
                            buffer_index = self.static_messageList_cfg_c1[index][0].txMsgBuf.MsgBufNr
                            if mode == 2:
                                print 'INFO: GIGABOX does not support to change transmission ' \
                                      'mode in runtine, all static frames are sent in Continuos Mode'
                            break
                else:
                    print 'INFO: FlexRay message ID {} NOT transmitted because it''s a ' \
                          'TX message of the selected ECU under test {}'.format(str(fr_id), self.ecu_under_test[index])
                    return 0

        # Check if message has been found in static configuration and sent
        if found_id:
            result_write = self.dll_lear.SendFrame(index, controller_index, buffer_index, payload_length * 2, data)
            if result_write != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
                print 'Error: {} while transmitting frame'.format(frStatusResult.get(result_write, 'UnknownError'))
                return 0
        else:
            # Let's look for the message in dynamic configuration
            for messageCfg in self.dynamic_messageList_cfg_c0[index]:
                if messageCfg.txMsgBuf.FrameId == fr_id:
                    if messageCfg.msgBufTag == self.dll_types.GtFr_MsgBufTagType.FR_MSGBUF_TX:
                        if messageCfg.txMsgBuf.BaseCycle == offset and messageCfg.txMsgBuf.Repetition == repetition:
                            found_id = True
                            buffer_index = messageCfg.txMsgBuf.MsgBufNr
                            if mode == 1:
                                print 'INFO: GIGABOX does not support to change transmission ' \
                                      'mode in runtine, all dynamic frames are sent in Single Shoot Mode'
                            break

                    else:
                        print 'INFO: FlexRay message NOT transmitted because it is ' \
                              'a TX message of the selected ECU under test {}'.format(self.ecu_under_test[index])
                        return 0
            # Check if message has been found in dynamic configuration and sent
            if found_id:
                result_write = self.dll_lear.SendFrame(index, 0, buffer_index, payload_length * 2, data)
                if result_write != self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
                    print 'ERROR: {} while transmitting frame'.format(frStatusResult.get(result_write, 'UnknownError'))
                    return 0
            else:
                print 'INFO: FlexRay message to be sent not found in GIGABOX configuration'
                return 0
        return 1

    def read_fr_frame(self, index):
        """
        Description: Reads FlexRay frame from channel.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [slotID, type, cycleCount, payloadLength, [b0, b1, b2, b3, b4, b5, b6, b7...]]

        Type examples: 128 = START_CYCLE, 129 = RX_FRAME, 131 = TXACK_FRAME, 132 = INVALID FRAME, 136 = STATUS

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            frame_rx = com.read_fr_frame(0)
        """

        received_events = []

        fr_event = self.dll_types.GtFr_EventType()
        fr_queue_status = self.dll_types.GtFr_EventQueueStatusType()

        fr_queue_status.state = self.dll_types.GtFr_EventQueueStateType.GTFR_QUEUE_SUCCESS

        # Get all events from the queue...
        while fr_queue_status.state != self.dll_types.GtFr_EventQueueStateType.GTFR_QUEUE_EMPTY:
            result, fr_event, fr_queue_status = self.dll_core.GtFr_ReceiveEvent(index, fr_event, fr_queue_status)

            if fr_queue_status.state != self.dll_types.GtFr_EventQueueStateType.GTFR_QUEUE_EMPTY:
                if fr_event.eventTag == self.dll_types.GtFr_EventTagType.GTFR_CYCLE_START:
                    self.current_cycle[index] = fr_event.eventData.cycleStart.cycleCount
                elif fr_event.eventTag == self.dll_types.GtFr_EventTagType.GTFR_RX_FRAME:
                    databuff = []
                    data = self.dll_lear.Get_ReceiveFrame(fr_event)
                    current_message_size = self.message_id_size[index].get(fr_event.eventData.rxFrame.slotId)
                    for i in data:
                        databuff.append(i)
                        current_message_size -= 1
                        if current_message_size == 0:
                            break

                    received_events.append([fr_event.eventData.rxFrame.slotId, fr_event.eventTag,
                                            fr_event.eventData.rxFrame.cycleCount,
                                            fr_event.eventData.rxFrame.payloadLength,
                                            fr_event.timeStamp * 1000, databuff])
                elif fr_event.eventTag == self.dll_types.GtFr_EventTagType.GTFR_TX_ACKNOWLEDGE:
                    databuff = []
                    data = self.dll_lear.Get_ReceiveFrame(fr_event)
                    current_message_size = self.message_id_size[index].get(fr_event.eventData.txAckFrame.slotId)
                    for i in data:
                        databuff.append(i)
                        current_message_size -= 1
                        if current_message_size == 0:
                            break
                    received_events.append([fr_event.eventData.txAckFrame.slotId, fr_event.eventTag,
                                            fr_event.eventData.txAckFrame.cycleCount,
                                            fr_event.eventData.txAckFrame.payloadLength,
                                            fr_event.timeStamp * 1000, databuff])
                else:
                    pass

        return received_events

    def get_fr_state(self, index):
        """
        Description: Report the current FlexRay bus state.

        Returns: statuts of the bus, frStatusTypeEnum
        """
        status_init = 0
        # Just check controller 0 state, Controller 1, if configured should have same state, as it's bus state
        result, status_init = self.dll_core.GtFr_GetCtrlState(index, 0, status_init)
        if result == self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            return frStatusTypeEnum.get(status_init, 'FR_STATUS_RESERVED')
        else:
            return 'FR_STATUS_UNKNOWN'

    def get_fr_cycle(self, index):
        """
        Description: Report the current FlexRay cycle.

        Returns: cycle number, [0..63]
        """
        return self.current_cycle[index]

    def close_channel(self, index):
        """
        Description: Closes communication channel.

        Example:
            com = COM('GIGABOX')
            com.open_fr_channel(0, ...)
            ...
            com.close_channel(0)
        """
        result = self.dll_core.GtFr_DeInit()
        if result == self.dll_types.GtFr_ReturnType.GTFR_SUCCESS:
            # Try to restart usb
            self._usb_gigabox_restart()
            print 'INFO: GIGABOX device channel closed in LATTE channel ID {}'.format(str(index))
            return True
        else:
            print 'ERROR: GIGABOX device while trying to close LATTE channel ID {}'.format(str(index))
            return False
