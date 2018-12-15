"""
====================================================================
Vector XL DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import sys
from ctypes import *


__author__ = 'Marc Teruel'
__version__ = '1.0.1'
__email__ = 'mteruel@lear.com'

"""
CHANGE LOG
==========
1.0.1 Fixed bug, _XLFrEvent struct member timestamp renamed to timeStamp
1.0.0 Inital version.
"""


# Prints additional info while debugging this library
VXL_DEBUG = False

# FLEXRAY uses the Rx queue version 4 (XL_INTERFACE_VERSION_V4) of the XL API
XL_INTERFACE_VERSION_V4 = 4
XL_INTERFACE_VERSION = XL_INTERFACE_VERSION_V4

# Bus type definition for FLEXRAY
XL_BUS_TYPE_FLEXRAY = 0x00000004

# Flags for open_fr_channel function
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

# FlexRay general defines
XL_FR_MAX_DATA_LENGTH = 254
XL_FR_RX_EVENT_HEADER_SIZE = 32
XL_FR_MAX_EVENT_SIZE = 512

# FlexRay event tags
XL_FR_START_CYCLE = 0x0080
XL_FR_RX_FRAME = 0x0081
XL_FR_TX_FRAME = 0x0082
XL_FR_TXACK_FRAME = 0x0083
XL_FR_INVALID_FRAME = 0x0084
XL_FR_WAKEUP = 0x0085
XL_FR_SYMBOL_WINDOW = 0x0086
XL_FR_ERROR = 0x0087
XL_FR_STATUS = 0x0088
XL_FR_NM_VECTOR = 0x008A
XL_FR_TRANCEIVER_STATUS = 0x008B
XL_FR_SPY_FRAME = 0x008E
XL_FR_SPY_SYMBOL = 0x008F

# Rx FIFO
FR_RX_QUEUE_SIZE = 524288   # Power of 2 and within a range of 8192...1048576 bytes

# Definitions for statusType
frStatusTypeEnum = {
    0x00: "FR_STATUS_DEFAULT_CONFIG",
    0x01: "FR_STATUS_READY",
    0x02: "FR_STATUS_NORMAL_ACTIVE",
    0x03: "FR_STATUS_NORMAL_PASSIVE",
    0x04: "FR_STATUS_HALT",
    0x05: "FR_STATUS_MONITOR_MODE",
    0x0f: "FR_STATUS_CONFIG",
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

# Definitions for error
frErrorTagEnum = {
    0x01: "XL_FR_ERROR_POC_MODE",
    0x02: "XL_FR_ERROR_SYNC_FRAMES_BELOWMIN",
    0x03: "XL_FR_ERROR_SYNC_FRAMES_OVERLOAD",
    0x04: "XL_FR_ERROR_CLOCK_CORR_FAILURE",
    0x05: "XL_FR_ERROR_NIT_FAILURE",
    0x06: "XL_FR_ERROR_CC_ERROR",
}

# Definitions for wakeup status
frwakeupStatusEnum = {
    0x00: "XL_FR_WAKEUP_UNDEFINED",
    0x01: "XL_FR_WAKEUP_RECEIVED_HEADER",
    0x02: "XL_FR_WAKEUP_RECEIVED_WUP",
    0x03: "XL_FR_WAKEUP_COLLISION_HEADER",
    0x04: "XL_FR_WAKEUP_COLLISION_WUP",
    0x05: "XL_FR_WAKEUP_COLLISION_UNKNOWN",
    0x06: "XL_FR_WAKEUP_TRANSMITTED",
    0x07: "XL_FR_WAKEUP_EXTERNAL_WAKEUP",
    0x10: "XL_FR_WAKEUP_WUP_RECEIVED_WITHOUT_WUS_TX",
    0xFF: "XL_FR_WAKEUP_RESERVED",
}

# For XLfrChannelConfig
XL_FR_CHANNEL_CFG_STATUS_INIT_APP_PRESENT = c_uint(0x01)
XL_FR_CHANNEL_CFG_STATUS_CHANNEL_ACTIVATED = c_uint(0x02)
XL_FR_CHANNEL_CFG_STATUS_VALID_CLUSTER_CFG = c_uint(0x04)
XL_FR_CHANNEL_CFG_STATUS_VALID_CFG_MODE = c_uint(0x08)
XL_FR_CHANNEL_CFG_MODE_SYNCHRONOUS = 1
XL_FR_CHANNEL_CFG_MODE_COMBINED = 2
XL_FR_CHANNEL_CFG_MODE_ASYNCHRONOUS = 3

# For xlFrSetMode
XL_FR_MODE_NORMAL = 0x00
XL_FR_MODE_COLD_NORMAL = 0x04
XL_FR_MODE_NONE = 0x00
XL_FR_MODE_WAKEUP = 0x01
XL_FR_MODE_COLDSTART_LEADING = 0x02
XL_FR_MODE_COLDSTART_FOLLOWING = 0x03
XL_FR_MODE_WAKEUP_AND_COLDSTART_LEADING = 0x04
XL_FR_MODE_WAKEUP_AND_COLDSTART_FOLLOWING = 0x05

# For flagsChip parameter
XL_FR_CHANNEL_A = c_ushort(0x01)
XL_FR_CHANNEL_B = c_ushort(0x02)
XL_FR_CHANNEL_AB = c_ushort(0x03)  # (XL_FR_CHANNEL_A | XL_FR_CHANNEL_B)
XL_FR_CC_COLD_A = c_ushort(0x04)
XL_FR_CC_COLD_B = c_ushort(0x08)
XL_FR_CC_COLD_AB = c_ushort(0x0C)  # (XL_FR_CC_COLD_A | XL_FR_CC_COLD_B)
XL_FR_SPY_CHANNEL_A = c_ushort(0x10)
XL_FR_SPY_CHANNEL_B = c_ushort(0x20)

XL_FR_QUEUE_OVERFLOW = 0x0100

# For TX_FLEXRAY_FRAME member flags
XL_FR_FRAMEFLAG_STARTUP = c_ushort(0x0001)
XL_FR_FRAMEFLAG_SYNC = c_ushort(0x0002)
XL_FR_FRAMEFLAG_NULLFRAME = c_ushort(0x0041)
XL_FR_FRAMEFLAG_PAYLOAD_PREAMBLE = c_ushort(0x0008)
XL_FR_FRAMEFLAG_FR_RESERVED = c_ushort(0x0010)
XL_FR_FRAMEFLAG_REQ_TXACK = c_ushort(0x20)

# XL_FR_TX_FRAME event: txMode flags
XL_FR_TX_MODE_CYCLIC = c_ubyte(0x01)
XL_FR_TX_MODE_SINGLE_SHOT = c_ubyte(0x02)
XL_FR_TX_MODE_NONE = c_ubyte(0xff)

# Return value used in several calls to the DLL
XL_SUCCESS = 0
XL_ERR_NO_LICENSE = 14

# _XLfrEvent.tag parameter values
XL_FR_NO_COMMAND = 0
XL_FR_RECEIVE_MSG = 1
XL_FR_CHIP_STATE = 4
XL_FR_TRANSCEIVER = 6
XL_FR_TIMER = 8
XL_FR_TRANSMIT_MSG = 10
XL_FR_SYNC_PULSE = 11


# noinspection PyTypeChecker
class _XLFrClusterConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ('busGuardianEnable', c_uint),
        ('baudrate', c_uint),
        ('busGuardianTick', c_uint),
        ('externalClockCorrectionMode', c_uint),
        ('gColdStartAttempts', c_uint),
        ('gListenNoise', c_uint),
        ('gMacroPerCycle', c_uint),
        ('gMaxWithoutClockCorrectionFatal', c_uint),
        ('gMaxWithoutClockCorrectionPassive', c_uint),
        ('gNetworkManagementVectorLength', c_uint),
        ('gNumberOfMinislots', c_uint),
        ('gNumberOfStaticSlots', c_uint),
        ('gOffsetCorrectionStart', c_uint),
        ('gPayloadLengthStatic', c_uint),
        ('gSyncNodeMax', c_uint),
        ('gdActionPointOffset', c_uint),
        ('gdDynamicSlotIdlePhase', c_uint),
        ('gdMacrotick', c_uint),
        ('gdMinislot', c_uint),
        ('gdMiniSlotActionPointOffset', c_uint),
        ('gdNIT', c_uint),
        ('gdStaticSlot', c_uint),
        ('gdSymbolWindow', c_uint),
        ('gdTSSTransmitter', c_uint),
        ('gdWakeupSymbolRxIdle', c_uint),
        ('gdWakeupSymbolRxLow', c_uint),
        ('gdWakeupSymbolRxWindow', c_uint),
        ('gdWakeupSymbolTxIdle', c_uint),
        ('gdWakeupSymbolTxLow', c_uint),
        ('pAllowHaltDueToClock', c_uint),
        ('pAllowPassiveToActive', c_uint),
        ('pChannels', c_uint),
        ('pClusterDriftDamping', c_uint),
        ('pDecodingCorrection', c_uint),
        ('pDelayCompensationA', c_uint),
        ('pDelayCompensationB', c_uint),
        ('pExternOffsetCorrection', c_uint),
        ('pExternRateCorrection', c_uint),
        ('pKeySlotUsedForStartup', c_uint),
        ('pKeySlotUsedForSync', c_uint),
        ('pLatestTx', c_uint),
        ('pMacroInitialOffsetA', c_uint),
        ('pMacroInitialOffsetB', c_uint),
        ('pMaxPayloadLengthDynamic', c_uint),
        ('pMicroInitialOffsetA', c_uint),
        ('pMicroInitialOffsetB', c_uint),
        ('pMicroPerCycle', c_uint),
        ('pMicroPerMacroNom', c_uint),
        ('pOffsetCorrectionOut', c_uint),
        ('pRateCorrectionOut', c_uint),
        ('pSamplesPerMicrotick', c_uint),
        ('pSingleSlotEnabled', c_uint),
        ('pWakeupChannel', c_uint),
        ('pWakeupPattern', c_uint),
        ('pdAcceptedStartupRange', c_uint),
        ('pdListenTimeout', c_uint),
        ('pdMaxDrift', c_uint),
        ('pdMicrotick', c_uint),
        ('gdCASRxLowMax', c_uint),
        ('gChannels', c_uint),
        ('vExternOffsetControl', c_uint),
        ('vExternRateControl', c_uint),
        ('pChannelsMTS', c_uint),
        ('reserved', c_uint * 16)]


# noinspection PyTypeChecker
class _XLFrChannelConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ('status', c_uint),
        ('cfgMode', c_uint),
        ('reserved', c_uint * 6),
        ('XLfrcluster_config', _XLFrClusterConfig)]


# noinspection PyTypeChecker
class _XLFrStartCycleEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('cycleCount', c_uint),
        ('vRateCorrection', c_int),
        ('vOffsetCorrection', c_int),
        ('vClockCorrectionFailed', c_uint),
        ('vAllowPassivToActive', c_uint),
        ('reserved', c_uint * 3)]


# noinspection PyTypeChecker
class _XLFrRxFrameEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('flags', c_ushort),
        ('headerCRC', c_ushort),
        ('slotID', c_ushort),
        ('cycleCount', c_ubyte),
        ('payloadLength', c_ubyte),
        ('data', c_ubyte * XL_FR_MAX_DATA_LENGTH)]


# noinspection PyTypeChecker
class _XLFrTxFrameEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('flags', c_ushort),
        ('slotID', c_ushort),
        ('offset', c_ubyte),
        ('repetition', c_ubyte),
        ('payloadLength', c_ubyte),
        ('txMode', c_ubyte),
        ('incrementSize', c_ubyte),
        ('incrementOffset', c_ubyte),
        ('reserved0', c_ubyte),
        ('reserved1', c_ubyte),
        ('data', c_ubyte * XL_FR_MAX_DATA_LENGTH)]


# noinspection PyTypeChecker
class _XLFrWakeupEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('cycleCount', c_ubyte),
        ('wakeupStatus', c_ubyte),
        ('reserved', c_ubyte * 6)]


# noinspection PyTypeChecker
class _XLFrSymbolWindowEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('symbol', c_uint),
        ('flags', c_uint),
        ('cycleCount', c_ubyte),
        ('reserved', c_ubyte * 7)]


# noinspection PyTypeChecker
class _XLFrErrorPocModeEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('errorMode', c_ubyte),
        ('reserved', c_ubyte * 3)]


class _XLFrErrorSyncFramesEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('evenSyncFramesA', c_ushort),
        ('oddSyncFramesA', c_ushort),
        ('evenSyncFramesB', c_ushort),
        ('oddSyncFramesB', c_ushort),
        ('reserved', c_uint)]


class _XLFrErrorClockCorrFailureEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('evenSyncFramesA', c_ushort),
        ('oddSyncFramesA', c_ushort),
        ('evenSyncFramesB', c_ushort),
        ('oddSyncFramesB', c_ushort),
        ('flags', c_uint),
        ('clockCorrFailedCounter', c_uint),
        ('reserved', c_uint)]


class _XLFrErrorNitFailureEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('flags', c_uint),
        ('reserved', c_uint)]


class _XLFrErrorCCErrorEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('ccError', c_uint),
        ('reserved', c_uint)]


class _XLFrErrorInfo(Union):
    _pack_ = 1
    _fields_ = [
        ('frPocMode', _XLFrErrorPocModeEv),
        ('frSyncFramesBelowMin', _XLFrErrorSyncFramesEv),
        ('frSyncFramesOverload', _XLFrErrorSyncFramesEv),
        ('frClockCorrectionFailure', _XLFrErrorClockCorrFailureEv),
        ('frNitFailure', _XLFrErrorNitFailureEv),
        ('frCCerrorInfo', _XLFrErrorCCErrorEv)]


# noinspection PyTypeChecker
class _XLFrErrorEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('tag', c_ubyte),
        ('cycleCount', c_ubyte),
        ('reserved', c_ubyte * 6),
        ('errorInfo', _XLFrErrorInfo)]


class _XLFrStatusEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('statusType', c_uint),
        ('reserved', c_uint)]


# noinspection PyTypeChecker
class _XLFrNmVectorEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('nmVector', c_ubyte * 12),
        ('cycleCount', c_ubyte),
        ('reserved', c_ubyte * 3)]


class _XLFrSyncPulseEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('triggerSource', c_uint),
        ('time', c_ulonglong)]


# noinspection PyTypeChecker
class _XLFrSpyFrameEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('frameLength', c_uint),
        ('frameError', c_ubyte),
        ('tssLength', c_ubyte),
        ('headerFlags', c_ushort),
        ('slotId', c_ushort),
        ('headerCRC', c_ushort),
        ('payloadLength', c_ubyte),
        ('cycleCount', c_ubyte),
        ('reserved', c_ushort),
        ('frameCRC', c_uint),
        ('data', c_ubyte * 254)]


class _XLFrSpySymbolEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('lowLength', c_ushort),
        ('reserved', c_ushort)]


# noinspection PyTypeChecker
class _XLApplicationNotificationEv(Structure):
    _pack_ = 1
    _fields_ = [
        ('notifyReason', c_uint),
        ('reserved', c_uint * 7)]


# noinspection PyTypeChecker
class _XLFrTagData(Union):
    _pack_ = 1
    _fields_ = [
        ('frStartCycle', _XLFrStartCycleEv),
        ('frRxFrame', _XLFrRxFrameEv),
        ('frTxFrame', _XLFrTxFrameEv),
        ('frWakeup', _XLFrWakeupEv),
        ('frSymbolWindow', _XLFrSymbolWindowEv),
        ('frError', _XLFrErrorEv),
        ('frStatus', _XLFrStatusEv),
        ('frNmVector', _XLFrNmVectorEv),
        ('frSpyFrame', _XLFrSpyFrameEv),
        ('frSpySymbol', _XLFrSpySymbolEv),
        ('applicationNotification', _XLApplicationNotificationEv),
        ('raw', c_ubyte * (XL_FR_MAX_EVENT_SIZE - XL_FR_RX_EVENT_HEADER_SIZE))]


class _XLFrEvent(Structure):
    _pack_ = 1
    _fields_ = [
        ('size', c_uint),
        ('tag', c_ushort),
        ('channelIndex', c_ushort),
        ('userHandle', c_uint),
        ('flagsChip', c_ushort),
        ('reserved', c_ushort),
        ('timeStamp', c_ulonglong),
        ('timeStampSync', c_ulonglong),
        ('tagData', _XLFrTagData)]


# noinspection PyTypeChecker
class _XLFrMode(Structure):
    _pack_ = 1
    _fields_ = [
        ('frMode', c_uint),
        ('frStartupAttributes', c_uint),
        ('reserved', c_uint * 30)]


# noinspection PyTypeChecker
class _XLFrHandle(Structure):
    _pack_ = 1
    _fields_ = [
        ('frMode', c_uint),
        ('frStartupAttributes', c_uint),
        ('reserved', c_uint * 30)]


class XLCOMFr:
    """
    Vector DLL (vxlapi.dll_core) wrapper.
    """

    def __init__(self):
        """
        Description: Constructor. Loads vxlapi.dll_core, opens drivers and reads conencted Vector devices.
        """
        self.xl_hnd = None
        self.xl_lib = None
        self.drv_config = None
        self.channel_license = []
        self.channel_info = []
        self.device_info = []
        self.current_cycle = []
        self.fr_bus_state = []
        self.msg_event = []

    # Parameters 'message_config' and 'ecu_under_test' not used, but left for compatibility
    # with vxl_fr.py method open_fr_channel
    # noinspection PyUnusedLocal
    def open_fr_channel(self, index, cluster_config, message_config=None, ecu_under_test=None):
        """
        Description: Opens FlexRay channel.  E-Ray CC and Fujitsu CC will be activated based on cluster config.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'cluster_config' is an object of class cluster_config (defined in fibex.py),
        contains the cluster configuration parameters.

        Example:
            com = XLCOM()
            com.open_fr_channel(0, cluster_config)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        permission_mask = channel_mask
        xl_hnd = c_long(-1)
        cluster = _XLFrClusterConfig()

        # copy cluster configuration
        cluster.busGuardianEnable = cluster_config.busGuardianEnable
        cluster.baudrate = cluster_config.baudrate
        cluster.busGuardianTick = cluster_config.busGuardianTick
        cluster.externalClockCorrectionMode = cluster_config.externalClockCorrectionMode
        cluster.gColdStartAttempts = cluster_config.gColdStartAttempts
        cluster.gListenNoise = cluster_config.gListenNoise
        cluster.gMacroPerCycle = cluster_config.gMacroPerCycle
        cluster.gMaxWithoutClockCorrectionFatal = cluster_config.gMaxWithoutClockCorrectionFatal
        cluster.gMaxWithoutClockCorrectionPassive = cluster_config.gMaxWithoutClockCorrectionPassive
        cluster.gNetworkManagementVectorLength = cluster_config.gNetworkManagementVectorLength
        cluster.gNumberOfMinislots = cluster_config.gNumberOfMinislots
        cluster.gNumberOfStaticSlots = cluster_config.gNumberOfStaticSlots
        cluster.gOffsetCorrectionStart = cluster_config.gOffsetCorrectionStart
        cluster.gPayloadLengthStatic = cluster_config.gPayloadLengthStatic
        cluster.gSyncNodeMax = cluster_config.gSyncNodeMax
        cluster.gdActionPointOffset = cluster_config.gdActionPointOffset
        cluster.gdDynamicSlotIdlePhase = cluster_config.gdDynamicSlotIdlePhase
        cluster.gdMacrotick = cluster_config.gdMacrotick
        cluster.gdMinislot = cluster_config.gdMinislot
        cluster.gdMiniSlotActionPointOffset = cluster_config.gdMiniSlotActionPointOffset
        cluster.gdNIT = cluster_config.gdNIT
        cluster.gdStaticSlot = cluster_config.gdStaticSlot
        cluster.gdSymbolWindow = cluster_config.gdSymbolWindow
        cluster.gdTSSTransmitter = cluster_config.gdTSSTransmitter
        cluster.gdWakeupSymbolRxIdle = cluster_config.gdWakeupSymbolRxIdle
        cluster.gdWakeupSymbolRxLow = cluster_config.gdWakeupSymbolRxLow
        cluster.gdWakeupSymbolRxWindow = cluster_config.gdWakeupSymbolRxWindow
        cluster.gdWakeupSymbolTxIdle = cluster_config.gdWakeupSymbolTxIdle
        cluster.gdWakeupSymbolTxLow = cluster_config.gdWakeupSymbolTxLow
        cluster.pAllowHaltDueToClock = cluster_config.pAllowHaltDueToClock
        cluster.pAllowPassiveToActive = cluster_config.pAllowPassiveToActive
        cluster.pChannels = cluster_config.pChannels
        cluster.pClusterDriftDamping = cluster_config.pClusterDriftDamping
        cluster.pDecodingCorrection = cluster_config.pDecodingCorrection
        cluster.pDelayCompensationA = cluster_config.pDelayCompensationA
        cluster.pDelayCompensationB = cluster_config.pDelayCompensationB
        cluster.pExternOffsetCorrection = cluster_config.pExternOffsetCorrection
        cluster.pExternRateCorrection = cluster_config.pExternRateCorrection
        cluster.pKeySlotUsedForStartup = cluster_config.pKeySlotUsedForStartup
        cluster.pKeySlotUsedForSync = cluster_config.pKeySlotUsedForSync
        cluster.pLatestTx = cluster_config.pLatestTx
        cluster.pMacroInitialOffsetA = cluster_config.pMacroInitialOffsetA
        cluster.pMacroInitialOffsetB = cluster_config.pMacroInitialOffsetB
        cluster.pMaxPayloadLengthDynamic = cluster_config.pMaxPayloadLengthDynamic
        cluster.pMicroInitialOffsetA = cluster_config.pMicroInitialOffsetA
        cluster.pMicroInitialOffsetB = cluster_config.pMicroInitialOffsetB
        cluster.pMicroPerCycle = cluster_config.pMicroPerCycle
        cluster.pMicroPerMacroNom = cluster_config.pMicroPerMacroNom
        cluster.pOffsetCorrectionOut = cluster_config.pOffsetCorrectionOut
        cluster.pRateCorrectionOut = cluster_config.pRateCorrectionOut
        cluster.pSamplesPerMicrotick = cluster_config.pSamplesPerMicrotick
        cluster.pSingleSlotEnabled = cluster_config.pSingleSlotEnabled
        cluster.pWakeupChannel = cluster_config.pWakeupChannel
        cluster.pWakeupPattern = cluster_config.pWakeupPattern
        cluster.pdAcceptedStartupRange = cluster_config.pdAcceptedStartupRange
        cluster.pdListenTimeout = cluster_config.pdListenTimeout
        cluster.pdMaxDrift = cluster_config.pdMaxDrift
        cluster.pdMicrotick = cluster_config.pdMicrotick
        cluster.gdCASRxLowMax = cluster_config.gdCASRxLowMax
        cluster.gChannels = cluster_config.gChannels
        cluster.vExternOffsetControl = cluster_config.vExternOffsetControl
        cluster.vExternRateControl = cluster_config.vExternRateControl
        cluster.pChannelsMTS = cluster_config.pChannelsMTS
        cluster.erayChannel = cluster_config.erayChannel

        if 'FR' not in self.drv_config.channel[index].transceiverName:
            print 'ERROR: Channel ID {} is not a FlexRay channel'.format(str(index))
            sys.exit()

        if self.xl_lib.xlOpenPort(byref(xl_hnd), 'LEAR', channel_mask,
                                  byref(permission_mask), FR_RX_QUEUE_SIZE,
                                  XL_INTERFACE_VERSION_V4, XL_BUS_TYPE_FLEXRAY) != XL_SUCCESS:
            print 'ERROR: Opening FlexRay channel ID {}'.format(str(index))
            sys.exit()

        if permission_mask.value == 0:
            # INIT access denied, some other app is already using this channel. Try to open without this permission.
            self.xl_lib.xlClosePort(xl_hnd)
            print 'ERROR: Opening Flex channel ID {}. ' \
                  'Another app may be already using this channel'.format(str(index))
            sys.exit()

        self.xl_hnd[index] = xl_hnd

        if self.xl_lib.xlFrSetConfiguration(self.xl_hnd[index], channel_mask, byref(cluster)) != XL_SUCCESS:
            print 'ERROR: Configuring FlexRay channel ID {}'.format(str(index))
            sys.exit()

        # Startup & Sync
        # XL_FR_FRAMEFLAG_STARTUP|XL_FR_FRAMEFLAG_SYNC|XL_FR_FRAMEFLAG_REQ_TXACK
        eray_frame_flags = fujitsu_frame_flags = 0x0001 | 0x0002 | 0x20

        xl_fr_config_frame = _XLFrEvent()

        # setup startup and sync frames for E-ray
        payload_length = cluster.gPayloadLengthStatic * 2     # length in bytes

        if cluster_config.erayID != 0:
            xl_fr_config_frame.tag = XL_FR_TX_FRAME
            if cluster.erayChannel == 1:
                xl_fr_config_frame.flagsChip = XL_FR_CHANNEL_A
            elif cluster.erayChannel == 2:
                xl_fr_config_frame.flagsChip = XL_FR_CHANNEL_B
            elif cluster.erayChannel == 3:
                xl_fr_config_frame.flagsChip = XL_FR_CHANNEL_AB
            xl_fr_config_frame.size = 0    # calculated inside XL-API DLL
            xl_fr_config_frame.userHandle = 0
            xl_fr_config_frame.tagData.frTxFrame.flags = eray_frame_flags
            xl_fr_config_frame.tagData.frTxFrame.offset = cluster_config.eray_offset
            xl_fr_config_frame.tagData.frTxFrame.repetition = cluster_config.eray_repetition
            xl_fr_config_frame.tagData.frTxFrame.payloadLength = cluster.gPayloadLengthStatic
            xl_fr_config_frame.tagData.frTxFrame.slotID = cluster_config.erayID
            xl_fr_config_frame.tagData.frTxFrame.txMode = XL_FR_TX_MODE_CYCLIC
            xl_fr_config_frame.tagData.frTxFrame.incrementOffset = 0
            xl_fr_config_frame.tagData.frTxFrame.incrementSize = 0

            for i in range(payload_length):
                xl_fr_config_frame.tagData.frTxFrame.data[i] = 0x00    # send zeroes by default

            status = self.xl_lib.xlFrInitStartupAndSync(self.xl_hnd[index],
                                                        channel_mask, byref(xl_fr_config_frame))
            if status == XL_ERR_NO_LICENSE:
                print 'WARNING: No license for Coldstart CC. Only E-Ray functionality available'
            elif status != XL_SUCCESS:
                print 'ERROR: E-ray startup and sync error in channel ID {} with ' \
                      'error {}'.format(str(index), str(status))
                sys.exit()

            # setup the mode for the E-Ray CC
            mode = _XLFrMode()
            mode.frMode = XL_FR_MODE_NORMAL
            mode.frStartupAttributes = XL_FR_MODE_COLDSTART_LEADING
            if self.xl_lib.xlFrSetMode(self.xl_hnd[index], channel_mask, byref(mode)) != XL_SUCCESS:
                print 'ERROR: Setting FlexRay channel ID {} E-Ray CC mode'.format(str(index))
                sys.exit()

        if cluster_config.coldID != 0:
            # setup the startup and sync frames for the COLD CC (NEEDS LICENSE)
            xl_fr_config_frame.tag = XL_FR_TX_FRAME
            if cluster.erayChannel == 1:
                xl_fr_config_frame.flagsChip = XL_FR_CC_COLD_A
            elif cluster.erayChannel == 2:
                xl_fr_config_frame.flagsChip = XL_FR_CC_COLD_B
            elif cluster.erayChannel == 3:
                xl_fr_config_frame.flagsChip = XL_FR_CC_COLD_AB
            xl_fr_config_frame.size = 0    # calculated inside XL-API DLL
            xl_fr_config_frame.userHandle = 0
            xl_fr_config_frame.tagData.frTxFrame.flags = fujitsu_frame_flags
            xl_fr_config_frame.tagData.frTxFrame.offset = cluster_config.cold_offset
            xl_fr_config_frame.tagData.frTxFrame.repetition = cluster_config.cold_repetition
            xl_fr_config_frame.tagData.frTxFrame.payloadLength = cluster.gPayloadLengthStatic
            xl_fr_config_frame.tagData.frTxFrame.slotID = cluster_config.coldID
            xl_fr_config_frame.tagData.frTxFrame.txMode = XL_FR_TX_MODE_CYCLIC
            xl_fr_config_frame.tagData.frTxFrame.incrementOffset = 0
            xl_fr_config_frame.tagData.frTxFrame.incrementSize = 0

            for i in range(payload_length):
                # Send zeroes by default
                xl_fr_config_frame.tagData.frTxFrame.data[i] = 0x00

            status = self.xl_lib.xlFrInitStartupAndSync(self.xl_hnd[index], channel_mask, byref(xl_fr_config_frame))
            if status == XL_SUCCESS:
                # Setup the mode for the Cold CC
                mode = _XLFrMode()
                mode.frMode = XL_FR_MODE_COLD_NORMAL
                mode.frStartupAttributes = XL_FR_MODE_COLDSTART_LEADING
                if self.xl_lib.xlFrSetMode(self.xl_hnd[index], channel_mask, byref(mode)) != XL_SUCCESS:
                    print 'ERROR: Setting FlexRay channel ID {} Fujitsu CC mode'.format(str(index))
                    sys.exit()
                # Activate the FlexRay channel
            elif status == XL_ERR_NO_LICENSE:
                print 'WARNING: No license for Coldstart CC. Only E-Ray functionality'
            else:
                print 'WARNING: Fujitsu CC startup and sync error'
                if cluster_config.coldID == 0:
                    print 'WARNING: FIBEX must contain two startup/sync nodes'

        if self.xl_lib.xlActivateChannel(self.xl_hnd[index], channel_mask,
                                         self.drv_config.channel[index].busParams.busType,
                                         XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print 'ERROR: Activating FlexRay channel ID {}'.format(str(index))
            sys.exit()

        # Init fr bus state
        self.fr_bus_state[index] = frStatusTypeEnum.get(0)

        print 'INFO: Vector FlexRay channel <{} {}> open in LATTE channel ' \
              'ID {}'.format(self.device_info[index], self.channel_info[index], str(index))
        try:
            if 'FLEXRAY' not in self.channel_license[index]:
                print 'WARNING: Channel ID {} does not have Flexray License, ' \
                      'it will have RX/TX limitations'.format(str(index))
        except IndexError:
            pass

        return True

    def write_fr_frame(self, index, fr_id, mode, data, payload_length, repetition, offset, channel):
        """
        Description: Writes FlexRay frame to channel.
        Parameter 'index' is the Vector channel index
        Parameter 'fr_id' is the frame ID (slot ID)
        Parameter 'mode' is the TxMode (XL_FR_TX_MODE_CYCLIC/SINGLE_SHOT/NONE)
        Parameter 'data' is a list with the data bytes
        Parameter 'payload_length' is the payload length in words
        Parameter 'repetition' is the repetition of the TX frame
        Parameter 'offset' is the frame base
        Parameter 'channel' is the flexray channel used (A=1, B=2, AB=3)

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            com.write_fr_frame(0, 0x2B, XL_FR_TX_MODE_CYCLIC, [0x5A, 0x23, 0x78, 0xB1], 8, 2, 0, 1)
        """
        # set parameters
        tx_flags = XL_FR_FRAMEFLAG_REQ_TXACK
        payload_inc = c_ubyte(0)

        # create TX event frame
        xl_fr_event = _XLFrEvent()
        xl_fr_event.tag = XL_FR_TX_FRAME
        xl_fr_event.flagsChip = channel
        xl_fr_event.size = 0    # Calculated inside XL-API DLL
        xl_fr_event.userHandle = 0
        xl_fr_event.tagData.frTxFrame.flags = tx_flags
        xl_fr_event.tagData.frTxFrame.offset = offset
        xl_fr_event.tagData.frTxFrame.repetition = repetition
        xl_fr_event.tagData.frTxFrame.payloadLength = payload_length
        xl_fr_event.tagData.frTxFrame.slotID = fr_id
        xl_fr_event.tagData.frTxFrame.txMode = mode
        xl_fr_event.tagData.frTxFrame.incrementOffset = 0
        xl_fr_event.tagData.frTxFrame.incrementSize = payload_inc

        for (i, value) in enumerate(data):
            xl_fr_event.tagData.frTxFrame.data[i] = value

        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)

        # send data
        status = self.xl_lib.xlFrTransmit(self.xl_hnd[index], channel_mask, byref(xl_fr_event))
        if status != XL_SUCCESS:
            print 'Error {} while transmitting frame'.format(str(status))
            return 0
        return 1

    def read_fr_frame(self, index):
        """
        Description: Reads FlexRay frame(s) from channel.
        If nothing has been received, it returns an empty list.

        Returns: list of received frames, which have the struct:
                 [slotID, type, cycleCount, payloadLength, [b0, b1, b2, b3, b4, b5, b6, b7...]]

        Type examples: 128 = START_CYCLE, 129 = RX_FRAME, 131 = TXACK_FRAME, 132 = INVALID FRAME, 136 = STATUS

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            frame_rx = com.read_fr_frame(0)
        """
        event = _XLFrEvent()
        received_event = []

        status = XL_SUCCESS

        while status == XL_SUCCESS:     # Keep looping xlFrReceive() till VectorDriver buffer is empty, or error
            status = self.xl_lib.xlFrReceive(self.xl_hnd[index], byref(event))
            if status == XL_SUCCESS:
                status_event = self._process_fr_event(event, index)
                if status_event == 'CYCLESTART':
                    self.current_cycle[index] = event.tagData.frStartCycle.cycleCount
                elif status_event == 'RXTX':
                    # In case of RX or TX event, process the message information
                    length = event.tagData.frRxFrame.payloadLength*2
                    data = [0]*length
                    # Copy data tp rx event
                    for i in range(length):
                        data[i] = event.tagData.frRxFrame.data[i]

                    received_event.append([event.tagData.frRxFrame.slotID, event.tag,
                                           event.tagData.frRxFrame.cycleCount,
                                           event.tagData.frRxFrame.payloadLength, event.timeStamp, data])

                elif status_event is not '':
                    self.fr_bus_state[index] = status_event

        return received_event

    def set_notification(self, index):
        msg_event = c_long(-1)
        status = self.xl_lib.xlSetNotification(self.xl_hnd[index], byref(msg_event), 1)
        self.msg_event[index] = msg_event

        return status

    @staticmethod
    def _process_fr_event(xl_fr_event=_XLFrEvent(), index=0):
        """
        Description: Process the information of the event reported by Vector Lib and print it

        Parameter 'index' is the Vector channel index
        Parameter 'xl_fr_event' event reported by vector lib
        Returns: FlexRay status update

        Example:
        """
        if xl_fr_event.flagsChip & XL_FR_QUEUE_OVERFLOW:
            if VXL_DEBUG:
                print '[' + str(index) + '] Overflow'

        if (xl_fr_event.tag == XL_FR_TXACK_FRAME) or (xl_fr_event.tag == XL_FR_RX_FRAME):
            return 'RXTX'

        elif xl_fr_event.tag == XL_FR_TX_FRAME:
            return 'RXTX'

        elif xl_fr_event.tag == XL_FR_START_CYCLE:
            return 'CYCLESTART'

        elif xl_fr_event.tag == XL_FR_SYMBOL_WINDOW:
            pass

        elif xl_fr_event.tag == XL_FR_STATUS:
            new_state = frStatusTypeEnum.get(xl_fr_event.tagData.frStatus.statusType, 'unknown')
            if VXL_DEBUG:
                print '[{}] FR status: {}, Fchip: {}'.format(str(index), new_state, str(xl_fr_event.flagsChip))
            return new_state

        elif xl_fr_event.tag == XL_FR_SYNC_PULSE:
            if VXL_DEBUG:
                print '[{}] FR sync pulse from source: {}'.format(
                    str(index),
                    str(xl_fr_event.tagData.frSyncPulse.triggerSource))

        elif xl_fr_event.tag == XL_FR_ERROR:
            if VXL_DEBUG:
                print '[{}] FR error: {}'.format(str(index), frErrorTagEnum.get(xl_fr_event.tagData.frError.tag))

        elif xl_fr_event.tag == XL_FR_INVALID_FRAME:
            if VXL_DEBUG:
                print '[{}] FR error: Invalid Frame'.format(str(index))

        elif (xl_fr_event.tag == XL_FR_SPY_FRAME) or (xl_fr_event.tag == XL_FR_SPY_SYMBOL):
            if VXL_DEBUG:
                print '[{}] FR spy frame/symbol'.format(str(index))

        elif xl_fr_event.tag == XL_FR_WAKEUP:
            if VXL_DEBUG:
                print '[{}] FR wakeup: {}, Fchip: {}'.format(
                    str(index),
                    frwakeupStatusEnum.get(xl_fr_event.tagData.frWakeup.wakeupStatus),
                    str(xl_fr_event.flagsChip))

        else:
            if VXL_DEBUG:
                print '[{}] FR unknown: {}'.format(str(index), str(xl_fr_event.tag))

        return ''

    def get_fr_state(self, index):
        """
        Description: Report the current FlexRay bus state.

        Returns: statuts of the bus, frStatusTypeEnum
        """
        return self.fr_bus_state[index]

    def get_fr_cycle(self, index):
        """
        Description: Report the current FlexRay cycle.

        Returns: cycle number, [0..63]
        """
        return self.current_cycle[index]
