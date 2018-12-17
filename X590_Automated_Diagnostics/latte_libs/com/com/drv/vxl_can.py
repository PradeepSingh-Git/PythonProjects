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

# Maximum data length of a CAN message
XL_MAX_MSG_LEN = 8

# Values used for extended frames (29-bit IDs)
XL_CAN_EXT_MSG_ID = 0x80000000
XL_CAN_11BITS_MAX_ID = 0b11111111111

# CAN uses the Rx queue version 3 (XL_INTERFACE_VERSION_V3) of the XL API
XL_INTERFACE_VERSION_V3 = 3
XL_INTERFACE_VERSION = XL_INTERFACE_VERSION_V3

# Bus type definition for CAN
XL_BUS_TYPE_CAN = 0x00000001

# Flags for open_can_channel function
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

# _XLEvent.tag parameter values
XL_NO_COMMAND = 0
XL_RECEIVE_MSG = 1
XL_CHIP_STATE = 4
XL_TRANSCEIVER = 6
XL_TIMER = 8
XL_TRANSMIT_MSG = 10
XL_SYNC_PULSE = 11

# Rx FIFO
CAN_RX_QUEUE_SIZE = 4096    # Power of 2 and within a range of 16...32768 bytes

# General return value used in several calls to the DLL
XL_SUCCESS = 0

# _XLEvent.tagData.msg.flags parameter can indicate an ErrorFrame
XL_CAN_MSG_FLAG_ERROR_FRAME = 0x01


# noinspection PyTypeChecker
class _XLCanMsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('id', c_ulong),
        ('flags', c_ushort),
        ('dlc', c_ushort),
        ('res1', c_ulonglong),
        ('data', c_ubyte * XL_MAX_MSG_LEN),
        ('res2', c_ulonglong)]


class _XLChipState(Structure):
    _pack_ = 1
    _fields_ = [
        ('busStatus', c_ubyte),
        ('txErrorCounter', c_ubyte),
        ('rxErrorCounter', c_ubyte)]


# noinspection PyTypeChecker
class _XLLinMsg(Structure):
    _pack_ = 1
    _fields_ = [
        ('id', c_ubyte),
        ('dlc', c_ubyte),
        ('flags', c_ushort),
        ('data', c_ubyte * 8),
        ('crc', c_ubyte)]


class _XLLinSleep(Structure):
    _pack_ = 1
    _fields_ = [('flag', c_ubyte)]


class _XLLinNoAns(Structure):
    _pack_ = 1
    _fields_ = [('id', c_ubyte)]


class _XLLinWakeUp(Structure):
    _pack_ = 1
    _fields_ = [('flag', c_ubyte)]


class _XLLinCrcInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ('id', c_ubyte),
        ('flags', c_ubyte)]


class _XLLinMsgApi(Union):
    _pack_ = 1
    _fields_ = [
        ('linMsg', _XLLinMsg),
        ('linNoAns', _XLLinNoAns),
        ('linWakeUp', _XLLinWakeUp),
        ('linSleep', _XLLinSleep),
        ('linCRCinfo', _XLLinCrcInfo)]


class _XLSyncPulse(Structure):
    _pack_ = 1
    _fields_ = [
        ('pulseCode', c_ubyte),
        ('time', c_ulonglong)]


# noinspection PyTypeChecker
class _XLDaioData(Structure):
    _pack_ = 1
    _fields_ = [
        ('flags', c_ushort),
        ('timestamp_correction', c_uint),
        ('mask_digital', c_ubyte),
        ('value_digital', c_ubyte),
        ('mask_analog', c_ubyte),
        ('reserved0', c_ubyte),
        ('value_analog', c_ushort * 4),
        ('pwm_frequency', c_uint),
        ('pwm_value', c_ushort),
        ('reserved1', c_uint),
        ('reserved2', c_uint)]


class _XLTransceiver(Structure):
    _pack_ = 1
    _fields_ = [
        ('event_reason', c_ubyte),
        ('is_present', c_ubyte)]


class _XLTagData(Union):
    _pack_ = 1
    _fields_ = [
        ('msg', _XLCanMsg),
        ('chipState', _XLChipState),
        ('linMsgApi', _XLLinMsgApi),
        ('syncPulse', _XLSyncPulse),
        ('daioData', _XLDaioData),
        ('transceiver', _XLTransceiver)]


class _XLEvent(Structure):
    _pack_ = 1
    _fields_ = [
        ('tag', c_ubyte),
        ('chanIndex', c_ubyte),
        ('transId', c_ushort),
        ('portHandle', c_ushort),
        ('reserved', c_ushort),
        ('timeStamp', c_ulonglong),
        ('tagData', _XLTagData)]


class XLCOMCan:
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

    def open_can_channel(self, index, speed):
        """
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
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        permission_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        xl_hnd = c_long(-1)

        if 'CAN' not in self.drv_config.channel[index].transceiverName:
            raise RuntimeError('ERROR: LATTE "VECTOR" channel ID {} is not a CAN channel'.format(str(index)))

        if self.xl_lib.xlOpenPort(byref(xl_hnd), "LEAR", channel_mask, byref(permission_mask), CAN_RX_QUEUE_SIZE,
                                  XL_INTERFACE_VERSION, XL_BUS_TYPE_CAN) != XL_SUCCESS:
            if permission_mask.value == 0:
                print 'ERROR: Permission denied when opening CAN in LATTE "VECTOR" channel ID {}'.format(str(index))
            else:
                print 'ERROR: Opening CAN in LATTE "VECTOR" channel ID {}'.format(str(index))
            sys.exit()

        self.xl_hnd[index] = xl_hnd
        bitrate = c_ulong(speed)

        if permission_mask.value != 0:
            # Set the CAN channel parameters only if the channel is not used by any other app
            if self.xl_lib.xlCanSetChannelBitrate(xl_hnd, channel_mask, bitrate) != XL_SUCCESS:
                print 'ERROR: Setting CAN bitrate in LATTE "VECTOR" channel ID {}'.format(str(index))
                sys.exit()

        # Activate the CAN channel
        if self.xl_lib.xlActivateChannel(xl_hnd, channel_mask, self.drv_config.channel[index].busParams.busType,
                                         XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print 'ERROR: Activating CAN in LATTE "VECTOR" channel ID {}'.format(str(index))
            sys.exit()

        # Reset timestamps every time a channel is open
        for item in self.xl_hnd:
            self.xl_lib.xlResetClock(item)
        print 'INFO: Vector device CAN channel open in LATTE "VECTOR" channel ID {}'.format(str(index))

        return True

    def write_can_frame(self, index, can_id, dlc, data):
        """
        Description: Writes CAN frame to channel.
        Parameter 'index' is the Vector channel index.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' os the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            com.write_can_frame(0x151, 3, [0x5A, 0x23, 0x78])
        """
        message_count = c_uint(1)
        # noinspection PyTypeChecker
        data_type = c_ubyte * 8
        if len(data) < 8:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        # noinspection PyCallingNonCallable
        mdata = data_type(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
        event = _XLEvent()

        event.tag = XL_TRANSMIT_MSG
        event.tagData.msg.id = can_id
        if can_id > XL_CAN_11BITS_MAX_ID:
            event.tagData.msg.id = can_id | XL_CAN_EXT_MSG_ID
        event.tagData.msg.dlc = dlc
        event.tagData.msg.flags = 0
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)

        for i in range(8):
            event.tagData.msg.data[i] = mdata[i]

        self.xl_lib.xlCanTransmit(self.xl_hnd[index], channel_mask, byref(message_count), byref(event))

    def read_can_frame(self, index):
        """
        Description: Reads CAN frame from channel 'index'.
        CAN frames are stored in an internal buffer in the Vector device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            frame_rx = com.read_can_frame()
        """
        # noinspection PyTypeChecker
        data_type = c_ubyte * 8
        # noinspection PyCallingNonCallable
        data = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        event = _XLEvent()
        event_count = c_uint(1)

        status = self.xl_lib.xlReceive(self.xl_hnd[index], byref(event_count), byref(event))
        if status == XL_SUCCESS:
            if (event.tag == XL_RECEIVE_MSG) or (event.tag == XL_TRANSMIT_MSG) and (event_count > 0):
                if event.tagData.msg.flags & XL_CAN_MSG_FLAG_ERROR_FRAME:
                    return []
                for i in range(8):
                    data[i] = event.tagData.msg.data[i]
                can_id = event.tagData.msg.id
                if event.tagData.msg.id > XL_CAN_11BITS_MAX_ID:
                    can_id = event.tagData.msg.id & (~XL_CAN_EXT_MSG_ID)
                return [can_id, event.tagData.msg.dlc, event.tagData.msg.flags, event.timeStamp, list(data)]
        else:
            return []
