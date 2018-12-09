'''
====================================================================
Vector XL DLL wrapper
(C) Copyright 2017 Lear Corporation
====================================================================
'''

__author__  = 'Jesus Fidalgo, Miguel Periago, David Fillat, Albert Sanz'
__version__ = '1.4.6'
__email__   = 'jfidalgo@lear.com, mperiago@lear.com, dfillatcastellvi@lear.com, asanz@lear.com'

'''
CHANGE LOG
==========
1.4.6 Raising exceptions instead of sys.exit() calls.
1.4.5 Improved __init__ method for adding self path to the system.
1.4.4 Changed RX_BUFFER_SIZE of open xlOpenPort method. Increased buffer size.
      Made some functions static.
      Minor bugfixes.
1.4.3 Fixed FlexRay driver, was not able to work when more that 2 Vector HW channels were detected.
1.4.2 Modified scan_devices method to generate list of detailed channel info.
1.4.1 Reset timestamps in all channels and all buses when opening a new bus channel.
1.4.0 Added support for flexRay channels.
1.3.2 Added support for 29bits CAN IDs.
1.3.1 Added wake up response case to read_lin_frame. Dlc value indicates the response type.
1.3.0 Implemented lin master node behavior.
      Improved scan_devices could be called several times to get fresh driver information.
      Added self.xllib.xlCloseDriver call inside close_channel method.
      Added 'write_lin_frame_master' method to write LIN master frames.
      Added checksum_list list to store frames checksum to apply at write.
      Added 'send_lin_sleep' method which transmits sleep signal over a given channel.
      Some general comments added.
      Improved case 'read_lin_frame' method event.tag is XL_LIN_NOANS (no answer) is returned an empty message.
      Added more data at print code line case LinSetSlave fails.
      Commented print code line inside 'write_lin_frame'.
      Added 'init_XL_devices' method due same actions to be performed at '__init__' and 'scan_devices' methods.
1.2.4 Method open_can_channel improved, CAN channel be open even if any other external app (like CANoe) is using it.
1.2.3 Added XL_LIN_FAULTY_CHECKSUM definition.
1.2.2 Channel open and close messages added.
1.2.1 Method write_lin_frame allows optional parameter to set a faulty checksum.
1.2.0 Method open_lin_channel more robust as specified in 'XL Driver Library - Description.pdf'.
      Methods switch_on_lin_id and switch_off_lin_id to enable and disable LIN frames.
1.1.0 [MPeriago] Added send_lin_wake_up method.
1.0.0 Inital version.
'''

import time
import sys
import os
from ctypes import *


# Prints additional info while debugging this library
VXL_DEBUG = False

# CAN speed defines
XL_CAN_BITRATE_1M = 1000000
XL_CAN_BITRATE_500K = 500000
XL_CAN_BITRATE_250K = 250000
XL_CAN_BITRATE_125K = 125000
XL_CAN_BITRATE_100K = 100000
XL_CAN_BITRATE_62K = 62000
XL_CAN_BITRATE_50K = 50000
XL_CAN_BITRATE_83K = 83000
XL_CAN_BITRATE_10K = 10000

XL_MAX_MSG_LEN = 8
XL_CAN_EXT_MSG_ID = 0x80000000
XL_CAN_11BITS_MAX_ID = 0b11111111111

XL_MAX_LENGTH = 31
XL_CONFIG_MAX_CHANNELS = 64

XL_INTERFACE_VERSION_V2 = 2
XL_INTERFACE_VERSION_V3 = 3
XL_INTERFACE_VERSION_V4 = 4
XL_INTERFACE_VERSION = XL_INTERFACE_VERSION_V3

XL_BUS_TYPE_CAN =  0x00000001
XL_BUS_TYPE_LIN =  0x00000002
XL_BUS_TYPE_MOST = 0x00000010
XL_BUS_TYPE_FLEXRAY= 0x00000004

XL_LIN_MASTER = 1
XL_LIN_SLAVE  = 2
XL_LIN_VERSION_1_3 = 1
XL_LIN_VERSION_2_0 = 2

# For xlLINSetDLC
XL_LIN_UNDEFINED_DLC = 0xFF

# For xlLinSetSlave
XL_LIN_FAULTY_CHECKSUM        = 0x0000
XL_LIN_CALC_CHECKSUM          = 0x0100
XL_LIN_CALC_CHECKSUM_ENHANCED = 0x0200

# For xlLinSetChecksum
XL_LIN_CHECKSUM_CLASSIC   = 0x00
XL_LIN_CHECKSUM_ENHANCED  = 0x01
XL_LIN_CHECKSUM_UNDEFINED = 0xFF

# Defines for the SleepMode function call
XL_LIN_SET_SILENT         = 0x01 #set hardware into sleep mode
XL_LIN_SET_WAKEUPID       = 0x03 #set hardware into sleep mode and send a request at wake-up

# For xlLinSwitchSlave
XL_LIN_SLAVE_ON  = 0xFF
XL_LIN_SLAVE_OFF = 0x00

# Flags for open_can_channel function
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

XL_NO_COMMAND = 0
XL_RECEIVE_MSG = 1
XL_CHIP_STATE = 4
XL_TRANSCEIVER = 6
XL_TIMER = 8
XL_TRANSMIT_MSG = 10
XL_SYNC_PULSE = 11

# Special events for LIN
XL_LIN_MSG = 20
XL_LIN_ERRMSG = 21
XL_LIN_SYNCERR = 22
XL_LIN_NOANS = 23
XL_LIN_WAKEUP = 24
XL_LIN_SLEEP = 25
XL_LIN_CRCINFO = 26

# FlexRay defines
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
LIN_RX_QUEUE_SIZE = 256     # Power of 2 and within a range of 16...32768 bytes
CAN_RX_QUEUE_SIZE = 4096    # Power of 2 and within a range of 16...32768 bytes
FR_RX_QUEUE_SIZE = 524288   # Power of 2 and within a range of 8192...1048576 bytes

# Definitions for statusType
frStatusTypeEnum = {
 0x00 : "FR_STATUS_DEFAULT_CONFIG",
 0x01 : "FR_STATUS_READY",
 0x02 : "FR_STATUS_NORMAL_ACTIVE",
 0x03 : "FR_STATUS_NORMAL_PASSIVE",
 0x04 : "FR_STATUS_HALT",
 0x05 : "FR_STATUS_MONITOR_MODE",
 0x0f : "FR_STATUS_CONFIG",
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

# Definitions for error
frErrorTagEnum = {
 0x01 : "XL_FR_ERROR_POC_MODE",
 0x02 : "XL_FR_ERROR_SYNC_FRAMES_BELOWMIN",
 0x03 : "XL_FR_ERROR_SYNC_FRAMES_OVERLOAD",
 0x04 : "XL_FR_ERROR_CLOCK_CORR_FAILURE",
 0x05 : "XL_FR_ERROR_NIT_FAILURE",
 0x06 : "XL_FR_ERROR_CC_ERROR",
}

# Definitions for wakup status
frwakeupStatusEnum = {
0x00 : "XL_FR_WAKEUP_UNDEFINED",
0x01 : "XL_FR_WAKEUP_RECEIVED_HEADER",
0x02 : "XL_FR_WAKEUP_RECEIVED_WUP",
0x03 : "XL_FR_WAKEUP_COLLISION_HEADER",
0x04 : "XL_FR_WAKEUP_COLLISION_WUP",
0x05 : "XL_FR_WAKEUP_COLLISION_UNKNOWN",
0x06 : "XL_FR_WAKEUP_TRANSMITTED",
0x07 : "XL_FR_WAKEUP_EXTERNAL_WAKEUP",
0x10 : "XL_FR_WAKEUP_WUP_RECEIVED_WITHOUT_WUS_TX",
0xFF : "XL_FR_WAKEUP_RESERVED",
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
XL_FR_CHANNEL_AB = c_ushort(0x03)  #(XL_FR_CHANNEL_A | XL_FR_CHANNEL_B)
XL_FR_CC_COLD_A = c_ushort(0x04)
XL_FR_CC_COLD_B = c_ushort(0x08)
XL_FR_CC_COLD_AB = c_ushort(0x0C) #(XL_FR_CC_COLD_A | XL_FR_CC_COLD_B)
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

XL_SUCCESS = 0

XL_ERR_QUEUE_IS_EMPTY = 10
XL_ERR_QUEUE_IS_FULL = 11
XL_ERR_NO_LICENSE = 14
XL_ERROR = 255

XL_LICENSE_BUFFER = 1024

XL_CAN_MSG_FLAG_ERROR_FRAME = 0x01

XL_LIN_VERSION = {
    'VERSION_1_3' : XL_LIN_VERSION_1_3,
    'VERSION_2_0' : XL_LIN_VERSION_2_0,
}

DLC_NO_RESPONSE = 0
DLC_WAKE_UP = 255

# Global variable to store LIN frames list checksum
checksum_list = 60*[XL_LIN_CHECKSUM_ENHANCED]


class _XLCanParams(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "bitRate", c_uint ), \
        ( "sjw", c_ubyte ), \
        ( "tseg1", c_ubyte ), \
        ( "tseg2", c_ubyte ), \
        ( "sam", c_ubyte ), \
        ( "outputMode", c_ubyte )]

class _XLDataParams(Union):
    _pack_ = 1
    _fields_ = [ \
        ( "can", _XLCanParams ), \
        ( "raw", c_ubyte*32 )]

class _XLBusParams(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "busType", c_uint ), \
        ( "data", _XLDataParams )]

class _XLChannelConfig(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "name", c_char*(XL_MAX_LENGTH+1) ), \
        ( "hwType", c_ubyte ), \
        ( "hwIndex", c_ubyte ), \
        ( "hwChannel", c_ubyte ), \
        ( "transceiverType", c_ushort ), \
        ( "transceiverState", c_uint ), \
        ( "channelIndex", c_ubyte ), \
        ( "channelMask", c_ulonglong ), \
        ( "channelCapabilities", c_uint ), \
        ( "channelBusCapabilities", c_uint ), \

        ( "isOnBus", c_ubyte ), \
        ( "connectedBusType", c_uint ), \
        ( "busParams", _XLBusParams ), \

        ( "driverVersion", c_uint ), \
        ( "interfaceVersion", c_uint ), \
        ( "raw_data", c_uint*10 ), \

        ( "serialNumber", c_uint ), \
        ( "articleNumber", c_uint ), \

        ( "transceiverName", c_char*(XL_MAX_LENGTH+1) ), \

        ( "specialCabFlags", c_uint ), \
        ( "dominantTimeout", c_uint ), \
        ( "dominantRecessiveDelay", c_ubyte ), \
        ( "recessiveDominantDelay", c_ubyte ), \
        ( "reserved01", c_ushort ), \
        ( "reserved", c_uint*7 )]

class _XLDriverConfig(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "dllVersion", c_uint ), \
        ( "channelCount", c_uint ), \
        ( "reserved", c_uint*10 ), \
        ( "channel", _XLChannelConfig * XL_CONFIG_MAX_CHANNELS )]

class _XLCanMsg(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "id", c_ulong ), \
        ( "flags", c_ushort ), \
        ( "dlc", c_ushort ), \
        ( "res1", c_ulonglong ), \
        ( "data", c_ubyte * XL_MAX_MSG_LEN ), \
        ( "res2", c_ulonglong )]

class _XLChipState(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "busStatus", c_ubyte ), \
        ( "txErrorCounter", c_ubyte ), \
        ( "rxErrorCounter", c_ubyte )]

class _XLSyncPulse(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "pulseCode", c_ubyte ), \
        ( "time", c_ulonglong )]

class _XLDaioData(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "flags", c_ushort ), \
        ( "timestamp_correction", c_uint ), \
        ( "mask_digital", c_ubyte ), \
        ( "value_digital", c_ubyte ), \
        ( "mask_analog", c_ubyte ), \
        ( "reserved0", c_ubyte ), \
        ( "value_analog", c_ushort*4 ), \
        ( "pwm_frequency", c_uint ), \
        ( "pwm_value", c_ushort ), \
        ( "reserved1", c_uint ), \
        ( "reserved2", c_uint )]

class _XLTransceiver(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "event_reason", c_ubyte ), \
        ( "is_present", c_ubyte )]

class _XLLinMsg(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "id", c_ubyte ), \
        ( "dlc", c_ubyte ), \
        ( "flags", c_ushort ), \
        ( "data", c_ubyte*8 ), \
        ( "crc", c_ubyte )]

class _XLLinSleep(Structure):
    _pack_ = 1
    _fields_ = [( "flag", c_ubyte )]

class _XLLinNoAns(Structure):
    _pack_ = 1
    _fields_ = [( "id", c_ubyte )]

class _XLLinWakeUp(Structure):
    _pack_ = 1
    _fields_ = [( "flag", c_ubyte )]

class _XLLinCrcInfo(Structure):
    _pack_ = 1
    _fields_ = [( "id", c_ubyte ), ( "flags", c_ubyte )]

class _XLLinMsgApi(Union):
    _pack_ = 1
    _fields_ = [ \
        ( "linMsg", _XLLinMsg ), \
        ( "linNoAns", _XLLinNoAns ), \
        ( "linWakeUp", _XLLinWakeUp ), \
        ( "linSleep", _XLLinSleep ), \
        ( "linCRCinfo", _XLLinCrcInfo )]

class _XLTagData(Union):
    _pack_ = 1
    _fields_ = [ \
        ( "msg", _XLCanMsg ), \
        ( "chipState", _XLChipState ), \
        ( "linMsgApi", _XLLinMsgApi ), \
        ( "syncPulse", _XLSyncPulse ), \
        ( "daioData", _XLDaioData ), \
        ( "transceiver", _XLTransceiver )]

class _XLEvent(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "tag", c_ubyte ), \
        ( "chanIndex", c_ubyte ), \
        ( "transId", c_ushort ), \
        ( "portHandle", c_ushort ), \
        ( "reserved", c_ushort ), \
        ( "timeStamp", c_ulonglong ), \
        ( "tagData", _XLTagData )]

class _XLLinStatPar(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "LINMode", c_uint ), \
        ( "baudrate", c_int ), \
        ( "LINVersion", c_uint ), \
        ( "reserved", c_uint )]

class _XLfrClusterConfig(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "busGuardianEnable", c_uint ), \
        ( "baudrate", c_uint ), \
        ( "busGuardianTick", c_uint ), \
        ( "externalClockCorrectionMode", c_uint ), \
        ( "gColdStartAttempts", c_uint ), \
        ( "gListenNoise", c_uint ), \
        ( "gMacroPerCycle", c_uint ), \
        ( "gMaxWithoutClockCorrectionFatal", c_uint ), \
        ( "gMaxWithoutClockCorrectionPassive", c_uint ), \
        ( "gNetworkManagementVectorLength", c_uint ), \
        ( "gNumberOfMinislots", c_uint ), \
        ( "gNumberOfStaticSlots", c_uint ), \
        ( "gOffsetCorrectionStart", c_uint ), \
        ( "gPayloadLengthStatic", c_uint ), \
        ( "gSyncNodeMax", c_uint ), \
        ( "gdActionPointOffset", c_uint ), \
        ( "gdDynamicSlotIdlePhase", c_uint ), \
        ( "gdMacrotick", c_uint ), \
        ( "gdMinislot", c_uint ), \
        ( "gdMiniSlotActionPointOffset", c_uint ), \
        ( "gdNIT", c_uint ), \
        ( "gdStaticSlot", c_uint ), \
        ( "gdSymbolWindow", c_uint ), \
        ( "gdTSSTransmitter", c_uint ), \
        ( "gdWakeupSymbolRxIdle", c_uint ), \
        ( "gdWakeupSymbolRxLow", c_uint ), \
        ( "gdWakeupSymbolRxWindow", c_uint ), \
        ( "gdWakeupSymbolTxIdle", c_uint ), \
        ( "gdWakeupSymbolTxLow", c_uint ), \
        ( "pAllowHaltDueToClock", c_uint ), \
        ( "pAllowPassiveToActive", c_uint ), \
        ( "pChannels", c_uint ), \
        ( "pClusterDriftDamping", c_uint ), \
        ( "pDecodingCorrection", c_uint ), \
        ( "pDelayCompensationA", c_uint ), \
        ( "pDelayCompensationB", c_uint ), \
        ( "pExternOffsetCorrection", c_uint ), \
        ( "pExternRateCorrection", c_uint ), \
        ( "pKeySlotUsedForStartup", c_uint ), \
        ( "pKeySlotUsedForSync", c_uint ), \
        ( "pLatestTx", c_uint ), \
        ( "pMacroInitialOffsetA", c_uint ), \
        ( "pMacroInitialOffsetB", c_uint ), \
        ( "pMaxPayloadLengthDynamic", c_uint ), \
        ( "pMicroInitialOffsetA", c_uint ), \
        ( "pMicroInitialOffsetB", c_uint ), \
        ( "pMicroPerCycle", c_uint ), \
        ( "pMicroPerMacroNom", c_uint ), \
        ( "pOffsetCorrectionOut", c_uint ), \
        ( "pRateCorrectionOut", c_uint ), \
        ( "pSamplesPerMicrotick", c_uint ), \
        ( "pSingleSlotEnabled", c_uint ), \
        ( "pWakeupChannel", c_uint ), \
        ( "pWakeupPattern", c_uint ), \
        ( "pdAcceptedStartupRange", c_uint ), \
        ( "pdListenTimeout", c_uint ), \
        ( "pdMaxDrift", c_uint ), \
        ( "pdMicrotick", c_uint ), \
        ( "gdCASRxLowMax", c_uint ), \
        ( "gChannels", c_uint ), \
        ( "vExternOffsetControl", c_uint ), \
        ( "vExternRateControl", c_uint ), \
        ( "pChannelsMTS", c_uint ), \
        ( "reserved", c_uint*16 )]

class _XLfrChannelConfig(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "status", c_uint ), \
        ( "cfgMode", c_uint ), \
        ( "reserved", c_uint*6 ), \
        ( "XLfrClusterConfig", _XLfrClusterConfig )]


class _XL_FR_START_CYCLE_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "cycleCount", c_uint ), \
        ( "vRateCorrection", c_int ), \
        ( "vOffsetCorrection", c_int ), \
        ( "vClockCorrectionFailed", c_uint ), \
        ( "vAllowPassivToActive", c_uint ), \
        ( "reserved", c_uint*3 )]

class _XL_FR_RX_FRAME_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "flags", c_ushort ), \
        ( "headerCRC", c_ushort ), \
        ( "slotID", c_ushort ), \
        ( "cycleCount", c_ubyte ), \
        ( "payloadLength", c_ubyte ), \
        ( "data", c_ubyte*XL_FR_MAX_DATA_LENGTH )]

class _XL_FR_TX_FRAME_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "flags", c_ushort ), \
        ( "slotID", c_ushort ), \
        ( "offset", c_ubyte ), \
        ( "repetition", c_ubyte ), \
        ( "payloadLength", c_ubyte ), \
        ( "txMode", c_ubyte ), \
        ( "incrementSize", c_ubyte ), \
        ( "incrementOffset", c_ubyte ), \
        ( "reserved0", c_ubyte ), \
        ( "reserved1", c_ubyte ), \
        ( "data", c_ubyte*XL_FR_MAX_DATA_LENGTH )]

class _XL_FR_WAKEUP_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "cycleCount", c_ubyte ), \
        ( "wakeupStatus", c_ubyte ), \
        ( "reserved", c_ubyte*6 )]

class _XL_FR_SYMBOL_WINDOW_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "symbol", c_uint ), \
        ( "flags", c_uint ), \
        ( "cycleCount", c_ubyte ), \
        ( "reserved", c_ubyte*7 )]

class _XL_FR_ERROR_POC_MODE_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "errorMode", c_ubyte ), \
        ( "reserved", c_ubyte*3 )]

class _XL_FR_ERROR_SYNC_FRAMES_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "evenSyncFramesA", c_ushort ), \
        ( "oddSyncFramesA", c_ushort ), \
        ( "evenSyncFramesB", c_ushort ), \
        ( "oddSyncFramesB", c_ushort ), \
        ( "reserved", c_uint )]

class _XL_FR_ERROR_CLOCK_CORR_FAILURE_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "evenSyncFramesA", c_ushort ), \
        ( "oddSyncFramesA", c_ushort ), \
        ( "evenSyncFramesB", c_ushort ), \
        ( "oddSyncFramesB", c_ushort ), \
        ( "flags", c_uint ), \
        ( "clockCorrFailedCounter", c_uint ), \
        ( "reserved", c_uint )]

class _XL_FR_ERROR_NIT_FAILURE_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "flags", c_uint ), \
        ( "reserved", c_uint )]

class _XL_FR_ERROR_CC_ERROR_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "ccError", c_uint ), \
        ( "reserved", c_uint )]

class _s_xl_fr_error_info(Union):
    _pack_ = 1
    _fields_ = [ \
        ( "frPocMode", _XL_FR_ERROR_POC_MODE_EV ), \
        ( "frSyncFramesBelowMin", _XL_FR_ERROR_SYNC_FRAMES_EV ), \
        ( "frSyncFramesOverload", _XL_FR_ERROR_SYNC_FRAMES_EV ), \
        ( "frClockCorrectionFailure", _XL_FR_ERROR_CLOCK_CORR_FAILURE_EV ), \
        ( "frNitFailure", _XL_FR_ERROR_NIT_FAILURE_EV ), \
        ( "frCCerrorInfo", _XL_FR_ERROR_CC_ERROR_EV )]

class _XL_FR_ERROR_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "tag", c_ubyte ), \
        ( "cycleCount", c_ubyte ), \
        ( "reserved", c_ubyte*6 ), \
        ( "errorInfo", _s_xl_fr_error_info )]

class _XL_FR_STATUS_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "statusType", c_uint ), \
        ( "reserved", c_uint )]

class _XL_FR_NM_VECTOR_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "nmVector", c_ubyte*12 ), \
        ( "cycleCount", c_ubyte ), \
        ( "reserved", c_ubyte*3 )]

class _XL_FR_SYNC_PULSE_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "triggerSource", c_uint ), \
        ( "time", c_ulonglong )]

class _XL_FR_SPY_FRAME_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "frameLength", c_uint ), \
        ( "frameError", c_ubyte ), \
        ( "tssLength", c_ubyte ), \
        ( "headerFlags", c_ushort ), \
        ( "slotId", c_ushort ), \
        ( "headerCRC", c_ushort ), \
        ( "payloadLength", c_ubyte ), \
        ( "cycleCount", c_ubyte ), \
        ( "reserved", c_ushort ), \
        ( "frameCRC", c_uint ), \
        ( "data", c_ubyte*254 )]

class _XL_FR_SPY_SYMBOL_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "lowLength", c_ushort ), \
        ( "reserved", c_ushort )]

class _XL_APPLICATION_NOTIFICATION_EV(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "notifyReason", c_uint ), \
        ( "reserved", c_uint*7 )]

class _XLfrTagData(Union):
    _pack_ = 1
    _fields_ = [ \
        ( "frStartCycle", _XL_FR_START_CYCLE_EV ), \
        ( "frRxFrame", _XL_FR_RX_FRAME_EV ), \
        ( "frTxFrame", _XL_FR_TX_FRAME_EV ), \
        ( "frWakeup", _XL_FR_WAKEUP_EV ), \
        ( "frSymbolWindow", _XL_FR_SYMBOL_WINDOW_EV ), \
        ( "frError", _XL_FR_ERROR_EV ), \
        ( "frStatus", _XL_FR_STATUS_EV ), \
        ( "frNmVector", _XL_FR_NM_VECTOR_EV ), \
        ( "frSpyFrame", _XL_FR_SPY_FRAME_EV ), \
        ( "frSpySymbol", _XL_FR_SPY_SYMBOL_EV  ), \
        ( "applicationNotification", _XL_APPLICATION_NOTIFICATION_EV ), \
        ( "raw", c_ubyte*(XL_FR_MAX_EVENT_SIZE - XL_FR_RX_EVENT_HEADER_SIZE) )]

XLfrEventTag = c_ushort

class _XLfrEvent(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "size", c_uint ), \
        ( "tag", XLfrEventTag), \
        ( "channelIndex", c_ushort ), \
        ( "userHandle", c_uint ), \
        ( "flagsChip", c_ushort ), \
        ( "reserved", c_ushort ), \
        ( "timeStamp", c_ulonglong ), \
        ( "timeStampSync", c_ulonglong ), \
        ( "tagData", _XLfrTagData )]

class _XLfrMode(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "frMode", c_uint ), \
        ( "frStartupAttributes", c_uint ), \
        ( "reserved", c_uint*30 )]

class _XLhandle(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "frMode", c_uint ), \
        ( "frStartupAttributes", c_uint ), \
        ( "reserved", c_uint*30 )]

class _XLlicenseInfo(Structure):
    _pack_ = 1
    _fields_ = [ \
        ("bAvailable", c_ubyte), \
        ("licName", c_ubyte * 65)]

class XLCOM:
    '''
    Vector DLL (vxlapi.dll) wrapper.
    '''

    def __init__(self):
        '''
        Description: Constructor. Loads vxlapi.dll, opens drivers and reads conencted Vector devices.
        '''
        self.xl_hnd = {}
        self.fr_bus_state = []
        self.currentCycle = {}
        self.channel_list=[]
        self.msg_event = {}

        # Load vxlapi.dll
        this_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'.'))
        os.environ['PATH'] = this_path + ';' + os.environ['PATH']
        try:
            self.xllib = windll.vxlapi
        except WindowsError:
            print "INFO: Failed to load vxlapi.dll, reasons could be:"
            print "  - 64 bits version of Python installed. It must be 32 bits version (also called x86)"
            print "  - 64 bits version of PyScripter installed. It must be 32 bits version (also called x86)"
            raise WindowsError("ERROR: Failed to load vxlapi.dll")

        # Open XL driver
        try:
            self.xllib.xlOpenDriver()
        except WindowsError:
            print "\nFailed to open Vector XL driver. You need to install Vector drivers \nfrom the CD installation tool CANoe_7.6_LIN\Drivers\Drivers\64_Bit\setup.exe"

        self._init_XL_devices()


    def _init_XL_devices(self):
        '''
        Description: Inits Vector XL devices connected.

        Note: This method is used internally by other public methods
        '''
        self.drvConfig = _XLDriverConfig()
        xlErr = self.xllib.xlGetDriverConfig(byref(self.drvConfig))
        if xlErr != XL_SUCCESS:
            print "\nFailed to read information from xlGetDriverConfig function"
            sys.exit()
        else:
            if self.drvConfig.channelCount == 0:
                print "\nNo HW channels found"
                sys.exit()


    def scan_devices(self):
        '''
        Description: Scans all Vector devices connected.
        Returns list of devices found, and prints useful info describing the devices connected and channels available

        Example:
            com = XLCOM()
            com.scan_devices()
        '''
        hw_channels_found = False
        self._init_XL_devices()
        self.channelLicense = []
        for i in range(self.drvConfig.channelCount):
            if 'Virtual' not in self.drvConfig.channel[i].name:
                print '\nDevice     : VECTOR'
                print 'Channel ID : ' + str(i)
                serial_number = str(self.drvConfig.channel[i].articleNumber) +"-"+ str(self.drvConfig.channel[i].serialNumber)
                print 'Device S/N : ' + serial_number
                channel_info = self.drvConfig.channel[i].name
                print 'Channel    : ' + channel_info
                transceiver_info = self.drvConfig.channel[i].transceiverName
                print 'Transceiver: ' + transceiver_info
                self.channel_list.append('VECTOR ' + serial_number + ' ' + channel_info + ' ' + transceiver_info)
                hw_channels_found = True
                licArraySize = c_uint(XL_LICENSE_BUFFER)
                licenseArray = (_XLlicenseInfo * XL_LICENSE_BUFFER)()
                channel_mask = c_ulonglong(self.drvConfig.channel[i].channelMask)
                status = self.xllib.xlGetLicenseInfo(channel_mask, byref(licenseArray), licArraySize)
                self.channelLicense.append('')
                if status == XL_SUCCESS:
                    for lic_loop in range(XL_LICENSE_BUFFER):
                        if licenseArray[lic_loop].bAvailable == 1: #check if license is present
                            result_str = string_at(licenseArray[lic_loop].licName)
                            print 'License    : ' + result_str
                            self.channelLicense[i] = self.channelLicense[i] + result_str + ','
                if self.channelLicense[i] == '':
                    print 'License    : None'
                    self.channelLicense[i] = 'None'

        if not hw_channels_found:
            raise Exception('ERROR: VECTOR device not found')

        self.fr_bus_state = [0] * self.drvConfig.channelCount
        return self.channel_list


    def open_can_channel(self, index, speed):
        '''
        Description: Opens CAN channel.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'speed' is the speed in bps. You can use already defined values in this file:
            XL_CAN_BITRATE_1M
            XL_CAN_BITRATE_500K
            XL_CAN_BITRATE_250K
            ...

        Note: It's possible to open a CAN channel from Latte that is already being used by other app, like CANoe.
        It's also possible for any other app to access a CAN channel being used by Latte.

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        permission_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        xl_hnd = c_long(-1)

        if 'CAN' not in self.drvConfig.channel[index].transceiverName:
            raise RuntimeError('\nError, channel ID ' + str(index) + ' is not a CAN channel')
            #print '\nError, channel ID ' + str(index) + ' is not a CAN channel'
            #sys.exit()

        if self.xllib.xlOpenPort(byref(xl_hnd), "LEAR", channel_mask, byref(permission_mask), CAN_RX_QUEUE_SIZE, XL_INTERFACE_VERSION, XL_BUS_TYPE_CAN) != XL_SUCCESS:
            print '\nError when opening CAN channel ID ' + str(index)
            sys.exit()

        if (permission_mask.value == 0):
            # INIT access denied, some other app is already using this channel. Try to open without this permission.
            self.xllib.xlClosePort(xl_hnd)
            if self.xllib.xlOpenPort(byref(xl_hnd), "LEAR", channel_mask, byref(permission_mask), CAN_RX_QUEUE_SIZE, XL_INTERFACE_VERSION, XL_BUS_TYPE_CAN) != XL_SUCCESS:
                print '\nError when opening CAN channel ID ' + str(index)
                sys.exit()

        self.xl_hnd[index] = xl_hnd
        bitrate = c_ulong(speed)

        if (permission_mask.value != 0):
            # Set the CAN channel parameters only if the channel is not used by any other app
            if self.xllib.xlCanSetChannelBitrate(xl_hnd, channel_mask, bitrate) != XL_SUCCESS:
                print '\nError when setting CAN bitrate in channel ID ' + str(index)
                sys.exit()

        # Activate the CAN channel
        if self.xllib.xlActivateChannel(xl_hnd, channel_mask, self.drvConfig.channel[index].busParams.busType, XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print '\nError when activating CAN channel ID ' + str(index)
            sys.exit()

        for item in self.xl_hnd:
            self.xllib.xlResetClock(item)
        print 'Vector device: CAN channel open in channel ID ' + str(index) + '\n'


    def open_lin_channel(self, index, speed, version, slaveFrames, mode = 'SLAVE'):
        '''
		Description: Opens LIN channel.
        Parameter speed is an integer with the baudrate.
        Parameter version is either 'VERSION_1_3' or 'VERSION_2_0'.
        Parameter slaveFrames is a list of lists with [linID, DLC]

        Note: It's NOT possible to open a LIN channel that is already being used by other app, like CANoe.

        Example:
            com = XLCOM()
            slave_frames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
        '''
        # Store inside the object the LIN version
        self.version = version

        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        permission_mask = channel_mask
        xl_hnd = c_long(-1)

        if 'LIN' not in self.drvConfig.channel[index].transceiverName:
            print '\nError, channel ID ' + str(index) + ' is not a LIN channel'
            sys.exit()

        if self.xllib.xlOpenPort(byref(xl_hnd), "LEAR", channel_mask, byref(permission_mask), LIN_RX_QUEUE_SIZE, XL_INTERFACE_VERSION, XL_BUS_TYPE_LIN) != XL_SUCCESS:
            print '\nError when opening LIN channel ID ' + str(index)
            sys.exit()

        self.xl_hnd[index] = xl_hnd
        bitrate = c_int(speed)

        # Set the LIN channel parameters
        linStatPar = _XLLinStatPar()
        if mode == 'SLAVE':
            linStatPar.LINMode = c_uint(XL_LIN_SLAVE)
        else:
            linStatPar.LINMode = c_uint(XL_LIN_MASTER)

        linStatPar.baudrate = bitrate
        linStatPar.LINVersion = c_uint(XL_LIN_VERSION[version])

        if self.xllib.xlLinSetChannelParams(xl_hnd, channel_mask, linStatPar) != XL_SUCCESS:
            print '\nError setting LIN parameters on channel ID ' + str(index)
            sys.exit()

        # Set the DLCs
        empty_list = 64*[XL_LIN_UNDEFINED_DLC]
        dlc_list = (c_ubyte * len(empty_list))(*empty_list)
        if self.xllib.xlLinSetDLC(xl_hnd, channel_mask, dlc_list) != XL_SUCCESS:
            print '\nError setting up LIN DLCs on channel ID ' + str(index)
            sys.exit()

        # Set the checksums, only neeed for LIN version 2.X
        if self.version == 'VERSION_2_0':
            for i in range(60):
                for frame in slaveFrames:
                    #check for frames checksum type
                    if i == frame[0]:
                        checksum_list[i]=frame[2]
            chk_list = (c_ubyte * len(checksum_list))(*checksum_list)
            """print 'xlLinSetChecksum '+ str(checksum_list)"""
            if self.xllib.xlLinSetChecksum(xl_hnd, channel_mask, chk_list) != XL_SUCCESS:
                print '\nError setting up LIN checksums on channel ID ' + str(index)
                sys.exit()

        # Set all the slave frames in the bus

        data_type = c_ubyte * 8
        data_list = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        for frame in slaveFrames:
            lin_id = frame[0]
            dlc = frame[1]
            checksum_type = XL_LIN_CALC_CHECKSUM
            if self.version == 'VERSION_2_0' and lin_id < 60:
                if frame[2]:
                    checksum_type = XL_LIN_CALC_CHECKSUM_ENHANCED
                else:
                    checksum_type = XL_LIN_CALC_CHECKSUM
            if self.xllib.xlLinSetSlave(xl_hnd, channel_mask, lin_id, data_list, dlc, checksum_type) != XL_SUCCESS:
                print '\nError setting up LIN as slave on channel ID ' + str(index) + '<lin id:'+str(lin_id)+' dlc:'+str(dlc)+' chk:'+str(checksum_type)+'>'
                sys.exit()

        # Activate the LIN channel
        if self.xllib.xlActivateChannel(xl_hnd, channel_mask, XL_BUS_TYPE_LIN , XL_ACTIVATE_RESET_CLOCK ) != XL_SUCCESS:
            print '\nError activating LIN on channel ID ' + str(index)
            sys.exit()

        self.xllib.xlResetClock(xl_hnd)
        print 'Vector device: LIN channel open in channel ID ' + str(index) + '\n'


    def lin_init_master(self, bitrate, version, xl_hnd, channel_mask, index):
        '''
        '''
        # Set the LIN channel parameters
        linStatPar = _XLLinStatPar()
        linStatPar.LINMode = c_uint(XL_LIN_MASTER)

        linStatPar.baudrate = bitrate
        linStatPar.LINVersion = c_uint(XL_LIN_VERSION[version])

        if self.xllib.xlLinSetChannelParams(xl_hnd, channel_mask, linStatPar) != XL_SUCCESS:
            print '\nError setting LIN parameters on channel ID ' + str(index)
            sys.exit()

        # Set the DLCs
        empty_list = 64*[XL_LIN_UNDEFINED_DLC]
        dlc_list = (c_ubyte * len(empty_list))(*empty_list)
        if self.xllib.xlLinSetDLC(xl_hnd, channel_mask, dlc_list) != XL_SUCCESS:
            print '\nError setting up LIN DLCs on channel ID ' + str(index)
            sys.exit()


    def close_channel(self, index):
        '''
        Description: Closes communication channel.

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            ...
            com.close_channel(0)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlDeactivateChannel(self.xl_hnd[index], channel_mask)
        self.xllib.xlClosePort(self.xl_hnd[index])

        self.xllib.xlCloseDriver()
        print 'Vector device: channel closed in channel ID ' + str(index) + '\n'


    def write_can_frame(self, index, can_id, dlc, data):
        '''
        Description: Writes CAN frame to channel.
        Parameter 'index' is the Vector channel index.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' os the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            com.write_can_frame(0x151, 3, [0x5A, 0x23, 0x78])
        '''
        message_count = c_uint(1)
        data_type = c_ubyte * 8
        if len(data) < 8:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        mdata = data_type(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
        event = _XLEvent()

        event.tag = XL_TRANSMIT_MSG
        event.tagData.msg.id = can_id
        if can_id > XL_CAN_11BITS_MAX_ID:
            event.tagData.msg.id = can_id | XL_CAN_EXT_MSG_ID
        event.tagData.msg.dlc = dlc
        event.tagData.msg.flags = 0
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)

        for i in range(8):
            event.tagData.msg.data[i] = mdata[i]

        self.xllib.xlCanTransmit(self.xl_hnd[index], channel_mask, byref(message_count), byref(event))


    def write_lin_frame(self, index, lin_id, dlc, data, faulty_checksum=False):

        '''
        Description: Prepares LIN frame to be sent when the master sends the header for the slave.
        Parameter 'index' is the Vector channel index.
        Parameter 'linid' is the frame ID.
        Parameter 'dlc' is the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = XLCOM()
            slaveFrames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slaveFrames)
            com.write_lin_frame(0, 0x21, 3, [0x01, 0x02, 0x03])
        '''
        data_type = c_ubyte * 8
        if len(data) < 8:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        mdata = data_type(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)

        # Checksum for LIN 1.X is always NOT ENHANCED.
        # Checksum for LIN 2.X is always ENHANCED, except for the diagnostic IDs 60 (0x3C) and 61 (0x3D)
        if faulty_checksum:
            checksum_type = XL_LIN_FAULTY_CHECKSUM
        else:
            if lin_id < 60 and self.version == 'VERSION_2_0':
                if checksum_list[lin_id]>0:
                    checksum_type = XL_LIN_CALC_CHECKSUM_ENHANCED
                else:
                    checksum_type = XL_LIN_CALC_CHECKSUM
            else:
                checksum_type = XL_LIN_CALC_CHECKSUM

        # Sets up a LIN slave. Must be called before activating a channel and for each slave ID separately.
        # After activating the channel it is only possible to change the data, dlc and checksum but not the linID.
        self.xllib.xlLinSetSlave(self.xl_hnd[index], channel_mask, lin_id, mdata, dlc, checksum_type)
        """print 'sending '+ str(lin_id)+ ' with checksum '+str(checksum_type)"""


    def write_lin_frame_master(self, index, lin_id, dlc, data, faulty_checksum=False):
        '''
        xlLinSendRequest Input Parameters:
        - portHandle The port handle retrieved by xlOpenPort.
        - accessMask The access mask must contain the mask of channels to be accessed.
        - linID Contains the master request LIN ID.
        - flags For future use. At the moment set to '0'
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinSendRequest(self.xl_hnd[index], channel_mask,lin_id,0)
        #send only non empty data which means Master Frames
        if(len(data)>0):
            self.write_lin_frame(index, lin_id, dlc, data, faulty_checksum)


    def read_can_frame(self, index):
        '''
        Description: Reads CAN frame from channel 'index'.
        CAN frames are stored in an internal buffer in the Vector device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            frame_rx = com.read_can_frame()
        '''
        data_type = c_ubyte * 8
        data = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        event = _XLEvent()
        event_count = c_uint(1)

        status = self.xllib.xlReceive(self.xl_hnd[index], byref(event_count), byref(event))
        if status == XL_SUCCESS and status != XL_ERR_QUEUE_IS_EMPTY:
            if (event.tag == XL_RECEIVE_MSG) or (event.tag == XL_TRANSMIT_MSG) and (event_count > 0):
                if event.tagData.msg.flags & XL_CAN_MSG_FLAG_ERROR_FRAME:
                    return []
                for i in range (8):
                    data[i] = event.tagData.msg.data[i]
                can_id = event.tagData.msg.id
                if event.tagData.msg.id > XL_CAN_11BITS_MAX_ID:
                    can_id = event.tagData.msg.id & (~XL_CAN_EXT_MSG_ID)
                return [can_id, event.tagData.msg.dlc, event.tagData.msg.flags, event.timeStamp, list(data)]
        else:
            return []


    def read_lin_frame(self, index):
        '''
        Description: Reads LIN frame sent by the master (header + data) from channel 'index'.
        LIN frames sent by the master (header + data) are stored in an internal buffer in the Vector device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = XLCOM()
            slave_frames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            frame_rx = com.read_lin_frame()
        '''
        data_type = c_ubyte * 8
        data = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        event = _XLEvent()
        event_count = c_uint(1)

        status = self.xllib.xlReceive(self.xl_hnd[index], byref(event_count), byref(event))
        if status == XL_SUCCESS and status != XL_ERR_QUEUE_IS_EMPTY:
            if (event.tag == XL_LIN_MSG) and (event_count > 0):
                for i in range (8):
                    data[i] = event.tagData.linMsgApi.linMsg.data[i]
                return [event.tagData.linMsgApi.linMsg.id, event.tagData.linMsgApi.linMsg.dlc, event.tagData.linMsgApi.linMsg.flags, event.timeStamp, list(data)]
            if(event.tag==XL_LIN_NOANS):
                data=[0,0,0,0,0,0,0,0]
                return [event.tagData.linMsgApi.linMsg.id, DLC_NO_RESPONSE, event.tag, 0, list(data)]
            if (event.tag==XL_LIN_WAKEUP):
                data=[0,0,0,0,0,0,0,0]
                return [event.tagData.linMsgApi.linMsg.id, DLC_WAKE_UP, event.tag, 0, list(data)]
        else:
            return []


    def send_lin_wake_up(self, index):
        '''
        Description: Transmits a wake-up signal over a given channel.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_wake_up()
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinWakeUp(self.xl_hnd[index], channel_mask)


    def send_lin_sleep(self,index):
        '''
        Description: Transmits sleep signal over a given channel.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_sleep()
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinSetSleepMode(self.xl_hnd[index], channel_mask,XL_LIN_SET_WAKEUPID,0x3C)


    def switch_on_lin_id(self, index, lin_id):
        '''
        Description: Switches on (enables) slave response for master ID=lin_id request.

        Note: By default all IDs are enabled. Use this method only after switching off a lin_id.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.switch_on_lin_id(0x30)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinSwitchSlave(self.xl_hnd[index], channel_mask, lin_id, XL_LIN_SLAVE_ON)


    def switch_off_lin_id(self, index, lin_id):
        '''
        Description: Switches off (disables) slave response for master ID=lin_id request.

        Note: By default all IDs are enabled. Use this method when using a real LIN ECU in your setup,
        or to generate a response frame error.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.switch_off_lin_id(0x30)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinSwitchSlave(self.xl_hnd[index], channel_mask, lin_id, XL_LIN_SLAVE_OFF)


    def send_lin_request(self, index, lin_id):
        '''
        Description: Sends a master LIN request to the slave(s).

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_request(0x30)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        self.xllib.xlLinSendRequest(self.xl_hnd[index], channel_mask, lin_id, 0)


    def open_fr_channel(self, index, clusterConfig, message_config, ecu_under_test):
        '''
        Description: Opens FlexRay channel.  E-Ray CC and Fujitsu CC will be activated based on cluster config.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'clusterConfig' is an object of class ClusterConfig (defined in fibex.py),
        contains the cluster configuration parameters.

        Example:
            com = XLCOM()
            com.open_fr_channel(0, cluster_config)
        '''
        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)
        permission_mask = channel_mask
        xl_hnd = c_long(-1)
        cluster = _XLfrClusterConfig()

        # copy cluster configuration
        cluster.busGuardianEnable = clusterConfig.busGuardianEnable
        cluster.baudrate = clusterConfig.baudrate
        cluster.busGuardianTick = clusterConfig.busGuardianTick
        cluster.externalClockCorrectionMode = clusterConfig.externalClockCorrectionMode
        cluster.gColdStartAttempts = clusterConfig.gColdStartAttempts
        cluster.gListenNoise = clusterConfig.gListenNoise
        cluster.gMacroPerCycle = clusterConfig.gMacroPerCycle
        cluster.gMaxWithoutClockCorrectionFatal = clusterConfig.gMaxWithoutClockCorrectionFatal
        cluster.gMaxWithoutClockCorrectionPassive = clusterConfig.gMaxWithoutClockCorrectionPassive
        cluster.gNetworkManagementVectorLength = clusterConfig.gNetworkManagementVectorLength
        cluster.gNumberOfMinislots = clusterConfig.gNumberOfMinislots
        cluster.gNumberOfStaticSlots = clusterConfig.gNumberOfStaticSlots
        cluster.gOffsetCorrectionStart = clusterConfig.gOffsetCorrectionStart
        cluster.gPayloadLengthStatic = clusterConfig.gPayloadLengthStatic
        cluster.gSyncNodeMax = clusterConfig.gSyncNodeMax
        cluster.gdActionPointOffset = clusterConfig.gdActionPointOffset
        cluster.gdDynamicSlotIdlePhase = clusterConfig.gdDynamicSlotIdlePhase
        cluster.gdMacrotick= clusterConfig.gdMacrotick
        cluster.gdMinislot = clusterConfig.gdMinislot
        cluster.gdMiniSlotActionPointOffset = clusterConfig.gdMiniSlotActionPointOffset
        cluster.gdNIT = clusterConfig.gdNIT
        cluster.gdStaticSlot = clusterConfig.gdStaticSlot
        cluster.gdSymbolWindow = clusterConfig.gdSymbolWindow
        cluster.gdTSSTransmitter = clusterConfig.gdTSSTransmitter
        cluster.gdWakeupSymbolRxIdle = clusterConfig.gdWakeupSymbolRxIdle
        cluster.gdWakeupSymbolRxLow = clusterConfig.gdWakeupSymbolRxLow
        cluster.gdWakeupSymbolRxWindow = clusterConfig.gdWakeupSymbolRxWindow
        cluster.gdWakeupSymbolTxIdle = clusterConfig.gdWakeupSymbolTxIdle
        cluster.gdWakeupSymbolTxLow = clusterConfig.gdWakeupSymbolTxLow
        cluster.pAllowHaltDueToClock = clusterConfig.pAllowHaltDueToClock
        cluster.pAllowPassiveToActive = clusterConfig.pAllowPassiveToActive
        cluster.pChannels = clusterConfig.pChannels
        cluster.pClusterDriftDamping = clusterConfig.pClusterDriftDamping
        cluster.pDecodingCorrection = clusterConfig.pDecodingCorrection
        cluster.pDelayCompensationA = clusterConfig.pDelayCompensationA
        cluster.pDelayCompensationB = clusterConfig.pDelayCompensationB
        cluster.pExternOffsetCorrection = clusterConfig.pExternOffsetCorrection
        cluster.pExternRateCorrection = clusterConfig.pExternRateCorrection
        cluster.pKeySlotUsedForStartup = clusterConfig.pKeySlotUsedForStartup
        cluster.pKeySlotUsedForSync = clusterConfig.pKeySlotUsedForSync
        cluster.pLatestTx = clusterConfig.pLatestTx
        cluster.pMacroInitialOffsetA = clusterConfig.pMacroInitialOffsetA
        cluster.pMacroInitialOffsetB = clusterConfig.pMacroInitialOffsetB
        cluster.pMaxPayloadLengthDynamic = clusterConfig.pMaxPayloadLengthDynamic
        cluster.pMicroInitialOffsetA = clusterConfig.pMicroInitialOffsetA
        cluster.pMicroInitialOffsetB = clusterConfig.pMicroInitialOffsetB
        cluster.pMicroPerCycle = clusterConfig.pMicroPerCycle
        cluster.pMicroPerMacroNom = clusterConfig.pMicroPerMacroNom
        cluster.pOffsetCorrectionOut = clusterConfig.pOffsetCorrectionOut
        cluster.pRateCorrectionOut = clusterConfig.pRateCorrectionOut
        cluster.pSamplesPerMicrotick = clusterConfig.pSamplesPerMicrotick
        cluster.pSingleSlotEnabled = clusterConfig.pSingleSlotEnabled
        cluster.pWakeupChannel = clusterConfig.pWakeupChannel
        cluster.pWakeupPattern = clusterConfig.pWakeupPattern
        cluster.pdAcceptedStartupRange = clusterConfig.pdAcceptedStartupRange
        cluster.pdListenTimeout = clusterConfig.pdListenTimeout
        cluster.pdMaxDrift = clusterConfig.pdMaxDrift
        cluster.pdMicrotick = clusterConfig.pdMicrotick
        cluster.gdCASRxLowMax = clusterConfig.gdCASRxLowMax
        cluster.gChannels = clusterConfig.gChannels
        cluster.vExternOffsetControl = clusterConfig.vExternOffsetControl
        cluster.vExternRateControl = clusterConfig.vExternRateControl
        cluster.pChannelsMTS = clusterConfig.pChannelsMTS
        cluster.erayChannel = clusterConfig.erayChannel

        if 'FR' not in self.drvConfig.channel[index].transceiverName:
            print '\nError, channel ID ' + str(index) + ' is not a FlexRay channel'
            sys.exit()

        if self.xllib.xlOpenPort(byref(xl_hnd), 'LEAR', channel_mask, byref(permission_mask), FR_RX_QUEUE_SIZE, XL_INTERFACE_VERSION_V4, XL_BUS_TYPE_FLEXRAY) != XL_SUCCESS:
            print '\nError when opening FlexRay channel ID ' + str(index)
            sys.exit()

        if (permission_mask.value == 0):
            # INIT access denied, some other app is already using this channel. Try to open without this permission.
            self.xllib.xlClosePort(xl_hnd)
            print '\nError when opening Flex channel ID ' + str(index) + '. Another app may be already using this channel.'
            sys.exit()

        self.xl_hnd[index] = xl_hnd

        if self.xllib.xlFrSetConfiguration(self.xl_hnd[index], channel_mask, byref(cluster)) != XL_SUCCESS:
            print '\nError when configuring FlexRay channel ID ' + str(index)
            sys.exit()

        # Startup & Sync
        erayFrameflags = fujitsuFrameFlags = 0x0001|0x0002|0x20     #XL_FR_FRAMEFLAG_STARTUP|XL_FR_FRAMEFLAG_SYNC|XL_FR_FRAMEFLAG_REQ_TXACK

        xlFrConfigFrame = _XLfrEvent()

        # setup startup and sync frames for E-ray
        payload_length = cluster.gPayloadLengthStatic*2     # length in bytes

        if clusterConfig.erayID != 0:
            xlFrConfigFrame.tag = XL_FR_TX_FRAME
            if cluster.erayChannel == 1:
                xlFrConfigFrame.flagsChip = XL_FR_CHANNEL_A
            elif cluster.erayChannel == 2:
                xlFrConfigFrame.flagsChip = XL_FR_CHANNEL_B
            elif cluster.erayChannel == 3:
                xlFrConfigFrame.flagsChip = XL_FR_CHANNEL_AB
            xlFrConfigFrame.size = 0    # calculated inside XL-API DLL
            xlFrConfigFrame.userHandle = 0
            xlFrConfigFrame.tagData.frTxFrame.flags = erayFrameflags
            xlFrConfigFrame.tagData.frTxFrame.offset = clusterConfig.eray_offset
            xlFrConfigFrame.tagData.frTxFrame.repetition = clusterConfig.eray_repetition
            xlFrConfigFrame.tagData.frTxFrame.payloadLength = cluster.gPayloadLengthStatic
            xlFrConfigFrame.tagData.frTxFrame.slotID = clusterConfig.erayID
            xlFrConfigFrame.tagData.frTxFrame.txMode = XL_FR_TX_MODE_CYCLIC
            xlFrConfigFrame.tagData.frTxFrame.incrementOffset = 0
            xlFrConfigFrame.tagData.frTxFrame.incrementSize = 0

            for i in range(payload_length):
                xlFrConfigFrame.tagData.frTxFrame.data[i] = 0x00    # send zeroes by default

            status = self.xllib.xlFrInitStartupAndSync(self.xl_hnd[index], channel_mask, byref(xlFrConfigFrame))
            if status == XL_ERR_NO_LICENSE:
                print '\nNo license for Coldstart CC. Only E-Ray functionality.'
            elif status != XL_SUCCESS:
                print '\nE-ray startup and sync error in channel ID ' + str(index) + ' with error ' + str(status)
                sys.exit()

            # setup the mode for the E-Ray CC
            mode = _XLfrMode()
            mode.frMode = XL_FR_MODE_NORMAL
            mode.frStartupAttributes = XL_FR_MODE_COLDSTART_LEADING
            if self.xllib.xlFrSetMode(self.xl_hnd[index], channel_mask, byref(mode)) != XL_SUCCESS:
                print '\nError when setting FlexRay channel ID ' + str(index) + ' E-Ray CC mode'
                sys.exit()

        if clusterConfig.coldID != 0:
            # setup the startup and sync frames for the COLD CC (NEEDS LICENSE)
            xlFrConfigFrame.tag =XL_FR_TX_FRAME
            if cluster.erayChannel == 1:
                xlFrConfigFrame.flagsChip = XL_FR_CC_COLD_A
            elif cluster.erayChannel == 2:
                xlFrConfigFrame.flagsChip = XL_FR_CC_COLD_B
            elif cluster.erayChannel == 3:
                xlFrConfigFrame.flagsChip = XL_FR_CC_COLD_AB
            xlFrConfigFrame.size = 0    # calculated inside XL-API DLL
            xlFrConfigFrame.userHandle = 0
            xlFrConfigFrame.tagData.frTxFrame.flags = fujitsuFrameFlags
            xlFrConfigFrame.tagData.frTxFrame.offset = clusterConfig.cold_offset
            xlFrConfigFrame.tagData.frTxFrame.repetition = clusterConfig.cold_repetition
            xlFrConfigFrame.tagData.frTxFrame.payloadLength = cluster.gPayloadLengthStatic
            xlFrConfigFrame.tagData.frTxFrame.slotID = clusterConfig.coldID
            xlFrConfigFrame.tagData.frTxFrame.txMode = XL_FR_TX_MODE_CYCLIC
            xlFrConfigFrame.tagData.frTxFrame.incrementOffset = 0
            xlFrConfigFrame.tagData.frTxFrame.incrementSize = 0

            for i in range(payload_length):
                xlFrConfigFrame.tagData.frTxFrame.data[i] = 0x00    # send zeroes by default

            status = self.xllib.xlFrInitStartupAndSync(self.xl_hnd[index], channel_mask, byref(xlFrConfigFrame))
            if status == XL_SUCCESS:
                # setup the mode for the Cold CC
                mode = _XLfrMode()
                mode.frMode = XL_FR_MODE_COLD_NORMAL
                mode.frStartupAttributes = XL_FR_MODE_COLDSTART_LEADING
                if self.xllib.xlFrSetMode(self.xl_hnd[index], channel_mask, byref(mode)) != XL_SUCCESS:
                    print '\nError when setting FlexRay channel ID ' + str(index) + ' Fujitsu CC mode'
                    sys.exit()
                # Activate the FlexRay channel
            elif status == XL_ERR_NO_LICENSE:
                print '\nNo license for Coldstart CC. Only E-Ray functionality.'
            else:
                print '\nFujitsu CC startup and sync error.\n'
                if clusterConfig.coldID == 0:
                    print 'FIBEX must contain two startup/sync nodes\n'
        if self.xllib.xlActivateChannel(self.xl_hnd[index], channel_mask, self.drvConfig.channel[index].busParams.busType, XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print '\nError when activating FlexRay channel ID ' + str(index)
            sys.exit()

        #Init fr bus state
        self.fr_bus_state[index] = frStatusTypeEnum.get(0)

        print 'Vector device: FlexRay channel open in channel ID ' + str(index)
        if 'FLEXRAY' in self.channelLicense[index]:
            print '\n'
        else:
            print '-->Warning!! ID ' + str(index) + ' doesn\'t have Flexray License, it will have RX/TX limitations.' + '\n'

    def write_fr_frame(self, index, fr_id, mode, data, payload_length, repetition, offset, channel): #(new)

        '''
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
        '''
        # set parameters
        txFlags = XL_FR_FRAMEFLAG_REQ_TXACK
        payloadInc = c_ubyte(0)
        max_words = 127

        # create TX event frame
        xlFrEvent = _XLfrEvent()
        xlFrEvent.tag = XL_FR_TX_FRAME
        xlFrEvent.flagsChip = channel
        xlFrEvent.size = 0    #calculated inside XL-API DLL
        xlFrEvent.userHandle = 0
        xlFrEvent.tagData.frTxFrame.flags = txFlags
        xlFrEvent.tagData.frTxFrame.offset = offset
        xlFrEvent.tagData.frTxFrame.repetition = repetition
        xlFrEvent.tagData.frTxFrame.payloadLength = payload_length
        xlFrEvent.tagData.frTxFrame.slotID = fr_id
        xlFrEvent.tagData.frTxFrame.txMode = mode
        xlFrEvent.tagData.frTxFrame.incrementOffset = 0
        xlFrEvent.tagData.frTxFrame.incrementSize = payloadInc

        # prepare data
        prepared_data = c_ubyte*(max_words*2)
        if (len(data)<max_words*2):
            zeroes = [0]*(max_words*2-len(data))
            data.extend(zeroes)
        prepared_data = prepared_data(*data)

        for (i, value) in enumerate(data):
            xlFrEvent.tagData.frTxFrame.data[i] = value

        channel_mask = c_ulonglong(self.drvConfig.channel[index].channelMask)

        # send data
        status = self.xllib.xlFrTransmit(self.xl_hnd[index], channel_mask, byref(xlFrEvent))
        if status != XL_SUCCESS:
            print 'Error ' + str(status) +' while transmitting frame.'
            return 0
        return 1

    def read_fr_frame(self, index):
        '''
        Description: Reads FlexRay frame(s) from channel.
        If nothing has been received, it returns an empty list.

        Returns: list of received frames, which have the struct:
                 [slotID, type, cycleCount, payloadLength, [b0, b1, b2, b3, b4, b5, b6, b7...]]

        Type examples: 128 = START_CYCLE, 129 = RX_FRAME, 131 = TXACK_FRAME, 132 = INVALID FRAME, 136 = STATUS

        Example:
            com = XLCOM()
            com.open_fr_channel(0)
            frame_rx = com.read_fr_frame(0)
        '''
        event = _XLfrEvent()
        received_event = []

        status = XL_SUCCESS

        while status == XL_SUCCESS:     # Keep looping xlFrReceive() till VectorDriver buffer is empty, or error
            status = self.xllib.xlFrReceive(self.xl_hnd[index], byref(event))
            if status == XL_SUCCESS:
                status_event = self._process_fr_event(event, index)
                if status_event == 'CYCLESTART':
                    self.currentCycle[index] = event.tagData.frStartCycle.cycleCount
                elif status_event == 'RXTX':
                    # In case of RX or TX event, process the message information
                    length = event.tagData.frRxFrame.payloadLength*2
                    data = [0]*length
                    # Copy data tp rx event
                    for i in range(length):
                        data[i] = event.tagData.frRxFrame.data[i]

                    received_event.append([event.tagData.frRxFrame.slotID, event.tag, event.tagData.frRxFrame.cycleCount,
                                           event.tagData.frRxFrame.payloadLength, event.timeStamp, data])

                elif status_event is not '':
                    self.fr_bus_state[index] = status_event

        return received_event

    def set_notification(self, index):
        msg_event = c_long(-1)
        status = self.xllib.xlSetNotification(self.xl_hnd[index], byref(msg_event), 1)
        self.msg_event[index] = msg_event

        return status

    @staticmethod
    def _process_fr_event(pxlFrEvent, index):
        '''
        Description: Process the information of the event reported by Vector Lib and print it

        Parameter 'index' is the Vector channel index
        Parameter 'pxlFrEvent' event reported by vector lib
        Returns: FlexRay status update, TODO:

        Example:
        '''
        if (pxlFrEvent.flagsChip & XL_FR_QUEUE_OVERFLOW):
            if VXL_DEBUG: print '['+ str(index) +'] Overflow\n'

        if (pxlFrEvent.tag == XL_FR_TXACK_FRAME) or (pxlFrEvent.tag == XL_FR_RX_FRAME):
            # print 'debugTime:' + str(time.clock())
            # print '['+ str(index) +'] FR RX data'
            return 'RXTX'

        elif (pxlFrEvent.tag == XL_FR_TX_FRAME):
            #print 'FR TX data'
            return 'RXTX'

        elif (pxlFrEvent.tag == XL_FR_START_CYCLE):
            return 'CYCLESTART'

        elif (pxlFrEvent.tag == XL_FR_SYMBOL_WINDOW):
            pass

        elif (pxlFrEvent.tag == XL_FR_STATUS):
            new_state = frStatusTypeEnum.get(pxlFrEvent.tagData.frStatus.statusType, "unknown")
            if VXL_DEBUG: print '['+ str(index) +'] FR status: ' + new_state + ', Fchip: ' + str(pxlFrEvent.flagsChip)
            return new_state

        elif (pxlFrEvent.tag == XL_SYNC_PULSE):
            if VXL_DEBUG: print '['+ str(index) +'] FR sync pulse from source: ' + str(pxlFrEvent.tagData.frSyncPulse.triggerSource)

        elif (pxlFrEvent.tag == XL_FR_ERROR):
            if VXL_DEBUG: print '['+ str(index) +'] FR error:  ' + frErrorTagEnum.get(pxlFrEvent.tagData.frError.tag)

        elif (pxlFrEvent.tag == XL_FR_INVALID_FRAME):
            if VXL_DEBUG: print '['+ str(index) +'] FR error:  Invalid Frame'

        elif (pxlFrEvent.tag == XL_FR_SPY_FRAME) or (pxlFrEvent.tag == XL_FR_SPY_SYMBOL):
            if VXL_DEBUG: print '['+ str(index) +'] FR spy frame/symbol'

        elif (pxlFrEvent.tag == XL_FR_WAKEUP):
            if VXL_DEBUG: print '['+ str(index) +'] FR wakeup: ' + frwakeupStatusEnum.get(pxlFrEvent.tagData.frWakeup.wakeupStatus) + ', Fchip: ' + str(pxlFrEvent.flagsChip)

        else:
            if VXL_DEBUG: print '['+ str(index) +'] FR unknown: ' + str(pxlFrEvent.tag)

        return ''

    def get_fr_state(self, index):
        '''
        Description: Report the current FlexRay bus state.

        Returns: statuts of the bus, frStatusTypeEnum
        '''
        return self.fr_bus_state[index]


    def get_fr_cycle(self, index):
        '''
        Description: Report the current FlexRay cycle.

        Returns: cycle number, [0..63]
        '''
        return self.currentCycle[index]
