'''
====================================================================
KVASER DLL wrapper
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = 'Andreu Montiel'
__version__ = '1.0.1'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.0.1 Added support for 29bits CAN IDs.
1.0.0 Inital version
'''

from ctypes import *
import time
import sys

MAX_MSG_LEN = 8

# A few constants from canlib.h
KV_CHANNELDATA_CARD_FIRMWARE_REV = 9
KV_CHANNELDATA_DEVDESCR_ASCII = 26
KV_CHANNELDATA_CHANNEL_NAME = 13
KV_IOCTL_SET_TIMER_SCALE = 6
KV_IOCTL_SET_TXACK = 7
KV_ERR_NOMSG = -2
KV_CAN_11BITS_MAX_ID = 0b11111111111
KV_CAN_EXTENDED_ID_FLAG = 0x0004

# Define a type for the body of the CAN message. Eight bytes as usual.
MsgDataType = c_uint8 * 8


class KVASER():

    def __init__(self):
        """
        Description: Constructor. Loads canlib32.dll, opens drivers and reads conencted Kvaser devices.
        """
        self.canlib_loaded = True
        self.canlib_txhnd = {}
        self.canlib_rxhnd = {}

        try:
            self.canlib = windll.canlib32
        except WindowsError:
            print "Failed to load canlib32.dll"
            self.canlib_loaded = False
            return

        self.canlib.canInitializeLibrary()


    def scan_devices(self):
        '''
        Description: Scans all Kvaser devices connected.
        Returns nothing, but it prints useful info describing the devices connected and channels available.

        Example:
            com = KVASER()
            com.scan_devices()
        '''
        n_channels = c_int(0)
        state = self.canlib.canGetNumberOfChannels(pointer(n_channels))
        if state < 0:
            print "\nNo HW channels found"
            sys.exit()

        name = create_string_buffer(64)

        for i in range(n_channels.value):
            self.canlib.canGetChannelData(c_int(i), c_int(KV_CHANNELDATA_CHANNEL_NAME), pointer(name), c_int(64))
            if 'Virtual' not in name.value:
                print 'Channel ID : %d' % i
                print 'Channel    : %s' % name.value
                print ''


    def open_can_channel(self, index, speed):
        '''
        Description: Opens CAN channel.
        Parameter 'index' must contain the Kvaser channel index.
        Parameter 'speed' is the speed in bps. 

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
        '''
        txhnd = c_long(-1)
        rxhnd = c_long(-1)

        txhnd = self.canlib.canOpenChannel(c_int(index), c_int(0))
        if (txhnd < 0):
            print '\nError when opening CAN channel ID ' + str(index)
            sys.exit()

        stat = self.canlib.canSetBitrate(c_int(txhnd), c_int(speed))
        if (stat < 0):
            print '\nError when setting CAN bitrate in channel ID ' + str(index)
            self.canlib.canClose(txhnd)
            sys.exit()

        stat = self.canlib.canBusOn(c_int(txhnd))
        if (stat < 0):
            print '\nError when setting on CAN in channel ID ' + str(index)
            self.canlib.canClose(c_int(txhnd))
            sys.exit()

        rxhnd = self.canlib.canOpenChannel(c_int(index), c_int(0))
        if (rxhnd < 0):
            print '\nError when opening CAN channel ID ' + str(index)
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        stat = self.canlib.canSetBitrate(c_int(rxhnd), c_int(speed))
        if (stat < 0):
            print '\nError when setting CAN bitrate in channel ID ' + str(index)
            self.canlib.canClose(c_int(txhnd))
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        stat = self.canlib.canBusOn(c_int(rxhnd))
        if (stat < 0):
            print '\nError when setting on CAN in channel ID ' + str(index)
            self.canlib.canClose(c_int(txhnd))
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        set_value = c_int(1) # 1 microsecond
        self.canlib.canIoCtl(c_int(txhnd), KV_IOCTL_SET_TIMER_SCALE, pointer(set_value), 4)

        set_value = c_int(1) # 1 microsecond
        self.canlib.canIoCtl(c_int(rxhnd), KV_IOCTL_SET_TIMER_SCALE, pointer(set_value), 4)

        # Handle 2 will send transmit acknowledge.
        set_value = c_int(1) # Turn on transmit acknowledge
        self.canlib.canIoCtl(c_int(rxhnd), KV_IOCTL_SET_TXACK, pointer(set_value), 4)

        self.canlib_txhnd[index] = txhnd
        self.canlib_rxhnd[index] = rxhnd

        print 'Kvaser device: CAN channel open in channel ID ' + str(index) + '\n'


    def write_can_frame(self, index, canid, dlc, data):
        '''
        Description: Writes CAN frame to channel.
        Parameter 'index' is the Kvaser channel index.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' os the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            com.write_can_frame(0x151, 3, [0x5A, 0x23, 0x78])
        '''
        if not (index in self.canlib_txhnd.keys()):
            print '\nError, trying to write to non existing CAN channel ID ' + str(index)
            sys.exit()

        msg = MsgDataType()
        for i in range(8):
            msg[i] = data[i]

        flags = 0
        if canid > KV_CAN_11BITS_MAX_ID:
            flags = KV_CAN_EXTENDED_ID_FLAG

        self.canlib.canWrite(c_int(self.canlib_txhnd[index]), c_int(canid), pointer(msg), c_uint(dlc), c_uint(0))


    def read_can_frame(self, index):
        '''
        Description: Reads CAN frame from channel 'index'.
        CAN frames are stored in an internal buffer in the Kvaser device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            frame_rx = com.read_can_frame()
        '''
        if not (index in self.canlib_txhnd.keys()):
            print '\nError, trying to read from to non existing CAN channel ID ' + str(index)
            sys.exit()

        rx_msg = MsgDataType()
        rx_id = c_int()
        rx_dlc = c_int()
        rx_flags = c_int()
        rx_time = c_int()

        stat = self.canlib.canRead(c_int(self.canlib_rxhnd[index]), pointer(rx_id), pointer(rx_msg), pointer(rx_dlc), pointer(rx_flags), pointer(rx_time))

        if stat == KV_ERR_NOMSG:
          return [] # No message

        data_type = c_ubyte * 8
        data = data_type(0, 0, 0, 0, 0, 0, 0, 0)

        for i in range (8):
            data[i] = rx_msg[i]

        return [rx_id.value, rx_dlc.value, rx_flags.value, 1000L * rx_time.value, list(data)]


    def close_channel(self, index):
        '''
        Description: Closes communication channel.

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            ...
            com.close_channel(0)
        '''
        self.canlib.canClose(c_int(self.canlib_txhnd[index]))
        self.canlib.canClose(c_int(self.canlib_rxhnd[index]))

        print 'Kvaser device: channel closed in channel ID ' + str(index) + '\n'
