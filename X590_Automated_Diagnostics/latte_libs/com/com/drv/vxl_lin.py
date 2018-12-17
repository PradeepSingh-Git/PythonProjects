"""
====================================================================
Vector XL DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import sys
from ctypes import *


__author__ = 'Carlos Blanco'
__version__ = '1.0.0'
__email__ = 'cblanco01@lear.com'

"""
CHANGE LOG
==========
1.0.0 Inital version.
"""


# Prints additional info while debugging this library
VXL_DEBUG = False

# CAN uses the Rx queue version 3 (XL_INTERFACE_VERSION_V3) of the XL API
XL_INTERFACE_VERSION_V3 = 3
XL_INTERFACE_VERSION = XL_INTERFACE_VERSION_V3

# Bus type definition for LIN
XL_BUS_TYPE_LIN = 0x00000002

# _XLLinStatPar.LINMode parameter values
XL_LIN_MASTER = 1
XL_LIN_SLAVE = 2

# Values for For xlLINSetDLC API
XL_LIN_UNDEFINED_DLC = 0xFF

# Values for xlLinSetSlave API
XL_LIN_FAULTY_CHECKSUM = 0x0000
XL_LIN_CALC_CHECKSUM = 0x0100
XL_LIN_CALC_CHECKSUM_ENHANCED = 0x0200

# Values for xlLinSetChecksum API
XL_LIN_CHECKSUM_CLASSIC = 0x00
XL_LIN_CHECKSUM_ENHANCED = 0x01
XL_LIN_CHECKSUM_UNDEFINED = 0xFF

# Defines for the SleepMode function call
XL_LIN_SET_SILENT = 0x01  # set hardware into sleep mode
XL_LIN_SET_WAKEUPID = 0x03  # set hardware into sleep mode and send a request at wake-up

# Values for xlLinSwitchSlave API
XL_LIN_SLAVE_ON = 0xFF
XL_LIN_SLAVE_OFF = 0x00

# Flags for resetting timestamps in open_lin_channel function
XL_ACTIVATE_NONE = 0
XL_ACTIVATE_RESET_CLOCK = 8

# _XLEvent.tag parameter values
XL_LIN_MSG = 20
XL_LIN_ERRMSG = 21
XL_LIN_SYNCERR = 22
XL_LIN_NOANS = 23
XL_LIN_WAKEUP = 24
XL_LIN_SLEEP = 25
XL_LIN_CRCINFO = 26

# General return value used in several calls to the DLL
XL_SUCCESS = 0

# Possible LIN protocol versions
XL_LIN_VERSION_1_3 = 1
XL_LIN_VERSION_2_0 = 2
XL_LIN_VERSION = {
    'VERSION_1_3': XL_LIN_VERSION_1_3,
    'VERSION_2_0': XL_LIN_VERSION_2_0,
}

# Maximum data length for a LIN frame
XL_MAX_MSG_LEN = 8

# Special flags for adding information to a received frame
DLC_NO_RESPONSE = 0
DLC_WAKE_UP = 255

# Rx FIFO
LIN_RX_QUEUE_SIZE = 256     # Power of 2 and within a range of 16...32768 bytes

# Global variable to store LIN frames list checksum
checksum_list = 60 * [XL_LIN_CHECKSUM_ENHANCED]


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


class _XLLinStatPar(Structure):
    _pack_ = 1
    _fields_ = [
        ('LINMode', c_uint),
        ('baudrate', c_int),
        ('LINVersion', c_uint),
        ('reserved', c_uint)]


class XLCOMLin:
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
        self.version = None

    def open_lin_channel(self, index, speed, version, slave_frames, mode='SLAVE'):
        """
        Description: Opens LIN channel.
        Parameter speed is an integer with the baudrate.
        Parameter version is either 'VERSION_1_3' or 'VERSION_2_0'.
        Parameter slaveFrames is a list of lists with [linID, DLC]

        Note: It's NOT possible to open a LIN channel that is already being used by other app, like CANoe.

        Example:
            com = XLCOM()
            slave_frames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
        """
        # Store inside the object the LIN version
        self.version = version

        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        permission_mask = channel_mask
        xl_hnd = c_long(-1)

        if 'LIN' not in self.drv_config.channel[index].transceiverName:
            print 'ERROR: Channel ID {} is not a LIN channel'.format(str(index))
            sys.exit()

        if self.xl_lib.xlOpenPort(byref(xl_hnd), 'LEAR', channel_mask, byref(permission_mask), LIN_RX_QUEUE_SIZE,
                                  XL_INTERFACE_VERSION, XL_BUS_TYPE_LIN) != XL_SUCCESS:
            print 'ERROR: Opening LIN channel ID {}'.format(str(index))
            sys.exit()

        self.xl_hnd[index] = xl_hnd
        bitrate = c_int(speed)

        # Set the LIN channel parameters
        lin_stat_par = _XLLinStatPar()
        if mode == 'SLAVE':
            lin_stat_par.LINMode = c_uint(XL_LIN_SLAVE)
        else:
            lin_stat_par.LINMode = c_uint(XL_LIN_MASTER)

        lin_stat_par.baudrate = bitrate
        lin_stat_par.LINVersion = c_uint(XL_LIN_VERSION[version])

        if self.xl_lib.xlLinSetChannelParams(xl_hnd, channel_mask, lin_stat_par) != XL_SUCCESS:
            print 'ERROR: Setting LIN parameters on channel ID {}'.format(str(index))
            sys.exit()

        # Set the DLCs
        empty_list = 64*[XL_LIN_UNDEFINED_DLC]
        # noinspection PyTypeChecker
        # noinspection PyCallingNonCallable
        dlc_list = (c_ubyte * len(empty_list))(*empty_list)
        if self.xl_lib.xlLinSetDLC(xl_hnd, channel_mask, dlc_list) != XL_SUCCESS:
            print 'ERROR: Setting up LIN DLCs on channel ID {}'.format(str(index))
            sys.exit()

        # Set the checksums, only neeed for LIN version 2.X
        if self.version == 'VERSION_2_0':
            for i in range(60):
                for frame in slave_frames:
                    # Check for frames checksum type
                    if i == frame[0]:
                        checksum_list[i] = frame[2]
            # noinspection PyTypeChecker
            # noinspection PyCallingNonCallable
            chk_list = (c_ubyte * len(checksum_list))(*checksum_list)
            if self.xl_lib.xlLinSetChecksum(xl_hnd, channel_mask, chk_list) != XL_SUCCESS:
                print 'ERROR: Setting up LIN checksums on channel ID {}'.format(str(index))
                sys.exit()

        # Set all the slave frames in the bus
        # noinspection PyTypeChecker
        data_type = c_ubyte * 8
        # noinspection PyCallingNonCallable
        data_list = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        for frame in slave_frames:
            lin_id = frame[0]
            dlc = frame[1]
            checksum_type = XL_LIN_CALC_CHECKSUM
            if self.version == 'VERSION_2_0' and lin_id < 60:
                if frame[2]:
                    checksum_type = XL_LIN_CALC_CHECKSUM_ENHANCED
                else:
                    checksum_type = XL_LIN_CALC_CHECKSUM
            if self.xl_lib.xlLinSetSlave(xl_hnd, channel_mask, lin_id, data_list, dlc, checksum_type) != XL_SUCCESS:
                print 'ERROR: Setting up LIN as slave on channel ID {} <id:{} dlc:{} chk:{}>'.\
                    format(str(index), str(lin_id), str(dlc), str(checksum_type))
                sys.exit()

        # Activate the LIN channel
        if self.xl_lib.xlActivateChannel(xl_hnd, channel_mask, XL_BUS_TYPE_LIN, XL_ACTIVATE_RESET_CLOCK) != XL_SUCCESS:
            print 'ERROR: Activating LIN on channel ID {}'.format(str(index))
            sys.exit()

        self.xl_lib.xlResetClock(xl_hnd)
        print 'INFO: Vector device LIN channel open in LATTE channel ID {}'.format(str(index))

    def lin_init_master(self, bitrate, version, xl_hnd, channel_mask, index):
        """
        """
        # Set the LIN channel parameters
        lin_stat_par = _XLLinStatPar()
        lin_stat_par.LINMode = c_uint(XL_LIN_MASTER)

        lin_stat_par.baudrate = bitrate
        lin_stat_par.LINVersion = c_uint(XL_LIN_VERSION[version])

        if self.xl_lib.xlLinSetChannelParams(xl_hnd, channel_mask, lin_stat_par) != XL_SUCCESS:
            print 'ERROR: Setting LIN parameters on channel ID {}'.format(str(index))
            sys.exit()

        # Set the DLCs
        empty_list = 64 * [XL_LIN_UNDEFINED_DLC]
        # noinspection PyTypeChecker
        # noinspection PyCallingNonCallable
        dlc_list = (c_ubyte * len(empty_list))(*empty_list)
        if self.xl_lib.xlLinSetDLC(xl_hnd, channel_mask, dlc_list) != XL_SUCCESS:
            print 'ERROR: Setting up LIN DLCs on channel ID {}'.format(str(index))
            sys.exit()

    def write_lin_frame(self, index, lin_id, dlc, data, faulty_checksum=False):

        """
        Description: Prepares LIN frame to be sent when the master sends the header for the slave.
        Parameter 'index' is the Vector channel index.
        Parameter 'lin_id' is the frame ID.
        Parameter 'dlc' is the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = XLCOM()
            slaveFrames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slaveFrames)
            com.write_lin_frame(0, 0x21, 3, [0x01, 0x02, 0x03])
        """
        # noinspection PyTypeChecker
        data_type = c_ubyte * 8
        if len(data) < 8:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        # noinspection PyCallingNonCallable
        mdata = data_type(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])

        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)

        # Checksum for LIN 1.X is always NOT ENHANCED.
        # Checksum for LIN 2.X is always ENHANCED, except for the diagnostic IDs 60 (0x3C) and 61 (0x3D)
        if faulty_checksum:
            checksum_type = XL_LIN_FAULTY_CHECKSUM
        else:
            if lin_id < 60 and self.version == 'VERSION_2_0':
                if checksum_list[lin_id] > 0:
                    checksum_type = XL_LIN_CALC_CHECKSUM_ENHANCED
                else:
                    checksum_type = XL_LIN_CALC_CHECKSUM
            else:
                checksum_type = XL_LIN_CALC_CHECKSUM

        # Sets up a LIN slave. Must be called before activating a channel and for each slave ID separately.
        # After activating the channel it is only possible to change the data, dlc and checksum but not the linID.
        self.xl_lib.xlLinSetSlave(self.xl_hnd[index], channel_mask, lin_id, mdata, dlc, checksum_type)

    def write_lin_frame_master(self, index, lin_id, dlc, data, faulty_checksum=False):
        """
        xlLinSendRequest Input Parameters:
        - portHandle The port handle retrieved by xlOpenPort.
        - accessMask The access mask must contain the mask of channels to be accessed.
        - linID Contains the master request LIN ID.
        - flags For future use. At the moment set to '0'
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinSendRequest(self.xl_hnd[index], channel_mask, lin_id, 0)
        # Send only non empty data which means Master Frames
        if len(data) > 0:
            self.write_lin_frame(index, lin_id, dlc, data, faulty_checksum)

    def read_lin_frame(self, index):
        """
        Description: Reads LIN frame sent by the master (header + data) from channel 'index'.
        LIN frames sent by the master (header + data) are stored in an internal buffer in the Vector device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = XLCOM()
            slave_frames = [[0x20, 8], [0x21, 3], [0x27, 8]]
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            frame_rx = com.read_lin_frame()
        """
        # noinspection PyTypeChecker
        data_type = c_ubyte * 8
        # noinspection PyCallingNonCallable
        data = data_type(0, 0, 0, 0, 0, 0, 0, 0)
        event = _XLEvent()
        event_count = c_uint(1)

        status = self.xl_lib.xlReceive(self.xl_hnd[index], byref(event_count), byref(event))
        if status == XL_SUCCESS:
            if (event.tag == XL_LIN_MSG) and (event_count > 0):
                for i in range(8):
                    data[i] = event.tagData.linMsgApi.linMsg.data[i]
                return [event.tagData.linMsgApi.linMsg.id, event.tagData.linMsgApi.linMsg.dlc,
                        event.tagData.linMsgApi.linMsg.flags, event.timeStamp, list(data)]
            if event.tag == XL_LIN_NOANS:
                data = [0, 0, 0, 0, 0, 0, 0, 0]
                return [event.tagData.linMsgApi.linMsg.id, DLC_NO_RESPONSE, event.tag, 0, list(data)]
            if event.tag == XL_LIN_WAKEUP:
                data = [0, 0, 0, 0, 0, 0, 0, 0]
                return [event.tagData.linMsgApi.linMsg.id, DLC_WAKE_UP, event.tag, 0, list(data)]
        else:
            return []

    def send_lin_wake_up(self, index):
        """
        Description: Transmits a wake-up signal over a given channel.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_wake_up()
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinWakeUp(self.xl_hnd[index], channel_mask)

    def send_lin_sleep(self, index):
        """
        Description: Transmits sleep signal over a given channel.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_sleep()
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinSetSleepMode(self.xl_hnd[index], channel_mask, XL_LIN_SET_WAKEUPID, 0x3C)

    def switch_on_lin_id(self, index, lin_id):
        """
        Description: Switches on (enables) slave response for master ID=lin_id request.

        Note: By default all IDs are enabled. Use this method only after switching off a lin_id.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.switch_on_lin_id(0x30)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinSwitchSlave(self.xl_hnd[index], channel_mask, lin_id, XL_LIN_SLAVE_ON)

    def switch_off_lin_id(self, index, lin_id):
        """
        Description: Switches off (disables) slave response for master ID=lin_id request.

        Note: By default all IDs are enabled. Use this method when using a real LIN ECU in your setup,
        or to generate a response frame error.

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.switch_off_lin_id(0x30)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinSwitchSlave(self.xl_hnd[index], channel_mask, lin_id, XL_LIN_SLAVE_OFF)

    def send_lin_request(self, index, lin_id):
        """
        Description: Sends a master LIN request to the slave(s).

        Example:
            com = XLCOM()
            com.open_lin_channel(0, 9600, 'VERSION_1_3', slave_frames)
            com.send_lin_request(0x30)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlLinSendRequest(self.xl_hnd[index], channel_mask, lin_id, 0)
