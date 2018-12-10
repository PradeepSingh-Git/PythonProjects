"""
====================================================================
Vector XL DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import sys
from ctypes import *


__author__ = 'Jesus Fidalgo'
__version__ = '1.0.0'
__email__ = 'jfidalgo@lear.com'

"""
CHANGE LOG
==========
1.0.0 Inital version.
"""


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

# CAN-FD maximum data length
XL_CAN_MAX_DATA_LEN = 64

# CAN-FD uses the Rx queue version 4 (XL_INTERFACE_VERSION_V4) of the XL API
XL_INTERFACE_VERSION_V4 = 4

XL_BUS_TYPE_CAN = 0x00000001
XL_BUS_TYPE_LIN = 0x00000002
XL_BUS_TYPE_MOST = 0x00000010
XL_BUS_TYPE_FLEXRAY = 0x00000004
XL_BUS_COMPATIBLE_CAN = XL_BUS_TYPE_CAN
XL_BUS_ACTIVE_CAP_CAN = XL_BUS_COMPATIBLE_CAN << 16
XL_CHANNEL_FLAG_CANFD_SUPPORT = 0x20000000

XL_CAN_EV_TAG_TX_MSG = 0x0440
XL_CAN_TXMSG_FLAG_EDL = 0x0001  # CAN-FD extended data length
XL_CAN_TXMSG_FLAG_BRS = 0x0002  # CAN-FD baud rate switch
XL_CAN_EV_TAG_RX_OK = 0x0400
XL_CAN_EV_TAG_TX_OK = 0x0404
XL_CAN_RXMSG_FLAG_EF = 0x0200

# Rx FIFO length
CAN_RX_QUEUE_SIZE = 4096  # Power of 2 and within a range of 16...32768 bytes

# Flags for activating a CAN-FD channel
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

# General return value used in several calls to the DLL
XL_SUCCESS = 0

# Dictionary for setting the parameter _XLCanTxEvent.tagData.canMsg.dlc value according
# the data length to be transmitted
_CAN_FD_DLC_TABLE = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    12: 9,
    16: 10,
    20: 11,
    24: 12,
    32: 13,
    48: 14,
    64: 15
}


# noinspection PyTypeChecker
class _XLCanFdConf(Structure):
    _pack_ = 1
    _fields_ = [
        ('arbitrationBitRate', c_uint),
        ('sjwAbr', c_uint),
        ('tseg1Abr', c_uint),
        ('tseg2Abr', c_uint),
        ('dataBitRate', c_uint),
        ('sjwDbr', c_uint),
        ('tseg1Dbr', c_uint),
        ('tseg2Dbr', c_uint),
        ('reserved', c_uint * 2)]


# noinspection PyTypeChecker
class _XLCanTxMsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('canId', c_uint),
        ('msgFlags', c_uint),
        ('dlc', c_ubyte),
        ('reserved', c_ubyte * 7),
        ('data', c_ubyte * XL_CAN_MAX_DATA_LEN)]


class _XLCanMsgTagData(Union):
    _pack_ = 1
    _fields_ = [
        ('canMsg', _XLCanTxMsg)]


# noinspection PyTypeChecker
class _XLCanTxEvent(Structure):
    _pack_ = 1
    _fields_ = [
        ('tag', c_ushort),
        ('transId', c_ushort),
        ('channelIndex', c_ubyte),
        ('reserved', c_ubyte * 3),
        ('tagData', _XLCanMsgTagData)]


# noinspection PyTypeChecker
class _XLCanEvRxMsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('canId', c_uint),
        ('msgFlags', c_uint),
        ('crc', c_uint),
        ('reserved1', c_ubyte * 12),
        ('totalBitCnt', c_ushort),
        ('dlc', c_ubyte),
        ('reserved', c_ubyte * 5),
        ('data', c_ubyte * XL_CAN_MAX_DATA_LEN)]


# noinspection PyTypeChecker
class _XLCanEvTxRequest(Structure):
    _pack_ = 1
    _fields_ = [
        ('canId', c_uint),
        ('msgFlags', c_uint),
        ('dlc', c_ubyte),
        ('reserved1', c_ubyte),
        ('reserved', c_ushort),
        ('data', c_ubyte * XL_CAN_MAX_DATA_LEN)]


# noinspection PyTypeChecker
class _XLCanEvError(Structure):
    _pack_ = 1
    _fields_ = [
        ('errorCode', c_ubyte),
        ('reserved', c_ubyte * 95)]


class _XLCanEvChipStateSyncPulse(Structure):
    _pack_ = 1
    _fields_ = [
        ('busStatus', c_ubyte),
        ('txErrorCounter', c_ubyte),
        ('rxErrorCounter', c_ubyte),
        ('reserved', c_ubyte),
        ('reserved0', c_uint)]


class _XLCanTagData(Union):
    _pack_ = 1
    _fields_ = [
        ('canRxOkMsg', _XLCanEvRxMsg),
        ('canTxOkMsg', _XLCanEvRxMsg),
        ('canTxRequest', _XLCanEvTxRequest),
        ('canError', _XLCanEvError),
        ('canChipState', _XLCanEvChipStateSyncPulse),
        ('canSyncPulse', _XLCanEvChipStateSyncPulse)]


class _XLCanRxEvent(Structure):
    _pack_ = 1
    _fields_ = [
        ('size', c_uint),
        ('tag', c_ushort),
        ('channelIndex', c_ubyte),
        ('reserved', c_ubyte),
        ('userHandle', c_uint),
        ('flagsChip', c_ushort),
        ('reserved0', c_ushort),
        ('reserved1', c_ulonglong),
        ('timeStamp', c_ulonglong),
        ('tagData', _XLCanTagData)]


class XLCOMCanFD(object):
    """
    Vector DLL (vxlapi.dll_core) wrapper for CAN-FD.
    """

    def __init__(self):
        """
        Description: Dummy constructor. See vxl.py constructor for more details.
        """
        self.xl_hnd = None
        self.xl_lib = None
        self.drv_config = None

    def open_canfd_channel(self, index, speed_header, speed_data, config_params=None):
        """
        Description: Opens CAN-FD channel.
        Parameter 'index' must contain the Vector channel index.
        Parameter 'speed_header' is the speed in bps of the frame header part
        Parameter 'speed_data' is the speed in bps of the frame data part
        Parameter 'config_params' is an optional list with 6 values, in this order:
            header_sjw
            header_tseg1
            header_tseg2
            data_sjw
            data_tseg1
            data_tseg2

        Note: It's NOT possible to open a CAN-FD channel from Latte that is already being used by other app, like CANoe.

        Example:
            com = XLCOM()
            com.open_canfd_channel(0, XL_CAN_BITRATE_500K, XL_CAN_BITRATE_1M)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        permission_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        xl_hnd = c_long(-1)

        if 'CAN' not in self.drv_config.channel[index].transceiverName:
            raise RuntimeError('ERROR: LATTE "VECTOR" channel ID {} is not a CAN-FD channel'.format(str(index)))

        if self.xl_lib.xlOpenPort(byref(xl_hnd), 'LEAR', channel_mask, byref(permission_mask), 8192,
                                  XL_INTERFACE_VERSION_V4, XL_BUS_TYPE_CAN) != XL_SUCCESS:
            if permission_mask.value == 0:
                print 'ERROR: Permission denied when opening CAN-FD in LATTE "VECTOR" channel ID {}'.format(str(index))
            else:
                print 'ERROR: Opening CAN-FD in LATTE "VECTOR" channel ID {}'.format(str(index))
            sys.exit()

        self.xl_hnd[index] = xl_hnd

        # Prepare CAN-FD configuration parameters
        config = _XLCanFdConf()
        config.arbitrationBitRate = speed_header
        config.dataBitRate = speed_data
        if config_params:
            config.sjwAbr = config_params[0]
            config.tseg1Abr = config_params[1]
            config.tseg2Abr = config_params[2]
            config.sjwDbr = config_params[3]
            config.tseg1Dbr = config_params[4]
            config.tseg2Dbr = config_params[5]
        else:
            # Default values, valid for VN1610 device at least. Other devices to be checked!
            config.sjwAbr = 3
            config.tseg1Abr = 59
            config.tseg2Abr = 20
            config.sjwDbr = 3
            config.tseg1Dbr = 29
            config.tseg2Dbr = 10

        # Configure CAN-FD parameters
        result = self.xl_lib.xlCanFdSetConfiguration(self.xl_hnd[index], channel_mask, byref(config))
        if result != XL_SUCCESS:
            print 'ERROR: Configuring CAN-FD in LATTE "VECTOR" channel ID {}'.format(str(index))
            sys.exit()

        # Activate the CAN channel
        if self.xl_lib.xlActivateChannel(xl_hnd, channel_mask, self.drv_config.channel[index].busParams.busType,
                                         XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print 'ERROR: Activating CAN-FD in LATTE "VECTOR" channel ID {}'.format(str(index))
            sys.exit()

        # Reset timestamps every time a channel is open
        for item in self.xl_hnd:
            self.xl_lib.xlResetClock(item)
        print 'INFO: Vector device CAN-FD channel open in LATTE "VECTOR" channel ID {}'.format(str(index))

        return True

    def write_canfd_frame(self, index, can_id, dlc, data):
        """
        Description: Writes CAN frame to channel.
        Parameter 'index' is the Vector channel index.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' os the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = XLCOM()
            com.open_canfd_channel(0, XL_CAN_BITRATE_500K, XL_CAN_BITRATE_1M)
            com.write_canfd_frame(0x151, 10, [0x5A, 0x23, 0x78, 0x5A, 0x23, 0x78, 0x5A, 0x23, 0x78, 0x5A])
        """
        if dlc not in _CAN_FD_DLC_TABLE.keys():
            return False
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        messages_to_be_sent = c_uint(1)
        messages_sent = c_uint()
        frame = _XLCanTxEvent(0)
        frame.tag = XL_CAN_EV_TAG_TX_MSG
        frame.transId = c_ushort(0xFFFF)
        frame.channelIndex = index
        frame.tagData.canMsg.canId = can_id
        frame.tagData.canMsg.msgFlags = XL_CAN_TXMSG_FLAG_EDL | XL_CAN_TXMSG_FLAG_BRS
        frame.tagData.canMsg.dlc = _CAN_FD_DLC_TABLE[dlc]
        for i in range(dlc):
            frame.tagData.canMsg.data[i] = data[i]
        for i in range(dlc, XL_CAN_MAX_DATA_LEN):
            frame.tagData.canMsg.data[i] = 0

        self.xl_lib.xlCanTransmitEx(self.xl_hnd[index], channel_mask, messages_to_be_sent,
                                    byref(messages_sent), byref(frame))

    def read_canfd_frame(self, index):
        """
        Description: Reads CAN-FD frame from channel 'index'.
        CAN frames are stored in an internal buffer in the Vector device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7, b8, b9...]]

        Example:
            com = XLCOM()
            com.open_canfd_channel(0, XL_CAN_BITRATE_500K, XL_CAN_BITRATE_1M)
            frame_rx = com.read_canfd_frame()
        """
        rx_evt = _XLCanRxEvent()
        status = self.xl_lib.xlCanReceive(self.xl_hnd[index], byref(rx_evt))
        if status == XL_SUCCESS:
            if rx_evt.tag == XL_CAN_EV_TAG_RX_OK or rx_evt.tag == XL_CAN_EV_TAG_TX_OK:
                if rx_evt.tagData.canRxOkMsg.msgFlags & XL_CAN_RXMSG_FLAG_EF:
                    return []
                dlc = _CAN_FD_DLC_TABLE.keys()[_CAN_FD_DLC_TABLE.values().index(rx_evt.tagData.canRxOkMsg.dlc)]
                data = dlc*[0]
                for i in range(dlc):
                    data[i] = rx_evt.tagData.canRxOkMsg.data[i]
                can_id = rx_evt.tagData.canRxOkMsg.canId
                return [can_id, dlc, rx_evt.tagData.canRxOkMsg.msgFlags, rx_evt.timeStamp, data]
        else:
            return []
