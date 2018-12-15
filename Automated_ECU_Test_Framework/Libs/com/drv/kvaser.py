"""
====================================================================
KVASER DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""

__author__ = 'Jesus Fidalgo'
__version__ = '1.1.0'
__email__ = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.1.0 PEP8 rework
1.0.3 Raising exceptions instead of sys.exit() calls.
1.0.2 Modified scan_devices method to generate list of detailed channel info.
1.0.1 Added support for 29bits CAN IDs.
1.0.0 Inital version.
'''

from ctypes import *
import sys
import os

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
# noinspection PyTypeChecker
MsgDataType = c_uint8 * 8


class KVASER:

    def __init__(self):
        """
        Description: Constructor. Loads canlib32.dll_core, opens drivers and reads conencted Kvaser devices.
        """
        self.canlib_loaded = True
        self.canlib_txhnd = {}
        self.canlib_rxhnd = {}
        self.channel_list = []  # List of strings with channel info
        self.scan_devices_executed = False

        # Add kvaser.py file path to the environment for loading the DLL
        this_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        os.environ['PATH'] = this_path + ';' + os.environ['PATH']
        try:
            self.canlib = windll.canlib32
        except WindowsError:
            print "INFO: Failed to load canlib32.dll_core, reasons could be:"
            print "  - 64 bits version of Python installed. It must be 32 bits version (also called x86)"
            print "  - KVASER drivers not installed. Please execute " \
                  "LATTE\Com\Trunk\drivers\kvaser\kvaser_drivers_w2k_xp.exe"
            self.canlib_loaded = False
            raise WindowsError("ERROR: Failed to load canlib32.dll_core")

        self.canlib.canInitializeLibrary()
        self.scan_devices()

    def scan_devices(self):
        """
        Description: Scans all Kvaser devices connected.
        Returns list of devices found, and prints useful info describing the devices connected and channels available

        Example:
            com = KVASER()
            com.scan_devices()
        """
        if not self.scan_devices_executed:
            n_channels = c_int(0)
            state = self.canlib.canGetNumberOfChannels(pointer(n_channels))
            if state < 0:
                raise Exception('ERROR: KVASER device can not be accessed')

            hw_channels_found = False
            name = create_string_buffer(64)
            for i in range(n_channels.value):
                self.canlib.canGetChannelData(c_int(i), c_int(KV_CHANNELDATA_CHANNEL_NAME), pointer(name), c_int(64))
                if 'Virtual' not in name.value:
                    print 'INFO: The following KVASER device channel is ' \
                          'available as LATTE "KVASER" channel ID {0}: '.format(str(i))
                    print '      {} {}'.format('Channel:', name.value)
                    self.channel_list.append(name.value)
                    hw_channels_found = True

            if not hw_channels_found:
                raise Exception('ERROR: KVASER device not found')

        self.scan_devices_executed = True
        return self.channel_list

    def open_can_channel(self, index, speed):
        """
        Description: Opens CAN channel.
        Parameter 'index' must contain the Kvaser channel index.
        Parameter 'speed' is the speed in bps.

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
        """
        txhnd = self.canlib.canOpenChannel(c_int(index), c_int(0))
        if txhnd < 0:
            print '\nERROR: When opening KVASER CAN Tx channel in LATTE "KVASER" channel ID {}'.format(str(index))
            sys.exit()

        stat = self.canlib.canSetBitrate(c_int(txhnd), c_int(speed))
        if stat < 0:
            print '\nERROR: When setting KVASER CAN Tx bitrate in LATTE "KVASER" channel ID {}'.format(str(index))
            self.canlib.canClose(txhnd)
            sys.exit()

        stat = self.canlib.canBusOn(c_int(txhnd))
        if stat < 0:
            print '\nERROR: When setting on KVASER CAN Tx in LATTE "KVASER" channel ID {}'.format(str(index))
            self.canlib.canClose(c_int(txhnd))
            sys.exit()

        rxhnd = self.canlib.canOpenChannel(c_int(index), c_int(0))
        if rxhnd < 0:
            print '\nERROR: When opening KVASER CAN Rx channel in LATTE "KVASER" channel ID {}'.format(str(index))
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        stat = self.canlib.canSetBitrate(c_int(rxhnd), c_int(speed))
        if stat < 0:
            print '\nERROR: When setting KVASER CAN Rx bitrate in LATTE "KVASER" channel ID {}'.format(str(index))
            self.canlib.canClose(c_int(txhnd))
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        stat = self.canlib.canBusOn(c_int(rxhnd))
        if stat < 0:
            print '\nERROR: When setting on KVASER CAN Rx in LATTE "KVASER" channel ID {}'.format(str(index))
            self.canlib.canClose(c_int(txhnd))
            self.canlib.canClose(c_int(rxhnd))
            sys.exit()

        set_value = c_int(1)  # 1 microsecond
        self.canlib.canIoCtl(c_int(txhnd), KV_IOCTL_SET_TIMER_SCALE, pointer(set_value), 4)

        set_value = c_int(1)  # 1 microsecond
        self.canlib.canIoCtl(c_int(rxhnd), KV_IOCTL_SET_TIMER_SCALE, pointer(set_value), 4)

        # Handle 2 will send transmit acknowledge.
        set_value = c_int(1)  # Turn on transmit acknowledge
        self.canlib.canIoCtl(c_int(rxhnd), KV_IOCTL_SET_TXACK, pointer(set_value), 4)

        self.canlib_txhnd[index] = txhnd
        self.canlib_rxhnd[index] = rxhnd

        print 'INFO: KVASER device CAN channel open in LATTE "KVASER" channel ID {}'.format(str(index))
        return True

    def write_can_frame(self, index, canid, dlc, data):
        """
        Description: Writes CAN frame to channel.
        Parameter 'index' is the Kvaser channel index.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' os the data length code.
        Parameter 'data' is a list with the data bytes.

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            com.write_can_frame(0x151, 3, [0x5A, 0x23, 0x78])
        """
        if not (index in self.canlib_txhnd.keys()):
            print 'ERROR: Trying to send CAN frame to KVASER device, ' \
                  'but not open LATTE "KVASER" channel ID {}'.format(str(index))
            sys.exit()

        # noinspection PyCallingNonCallable
        msg = MsgDataType()
        for i in range(8):
            msg[i] = data[i]

        flags = 0
        if canid > KV_CAN_11BITS_MAX_ID:
            flags = KV_CAN_EXTENDED_ID_FLAG

        self.canlib.canWrite(c_int(self.canlib_txhnd[index]), c_int(canid), pointer(msg), c_uint(dlc), c_uint(flags))

    def read_can_frame(self, index):
        """
        Description: Reads CAN frame from channel 'index'.
        CAN frames are stored in an internal buffer in the Kvaser device.
        If nothing has been received, it returns an empty list.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            frame_rx = com.read_can_frame()
        """
        if not (index in self.canlib_txhnd.keys()):
            print 'ERROR: Trying to read CAN frame from KVASER device, ' \
                  'but not open LATTE "KVASER" channel ID {}'.format(str(index))
            sys.exit()

        # noinspection PyCallingNonCallable
        rx_msg = MsgDataType()
        rx_id = c_int()
        rx_dlc = c_int()
        rx_flags = c_int()
        rx_time = c_int()

        stat = self.canlib.canRead(c_int(self.canlib_rxhnd[index]),
                                   pointer(rx_id), pointer(rx_msg), pointer(rx_dlc),
                                   pointer(rx_flags), pointer(rx_time))

        if stat == KV_ERR_NOMSG or rx_dlc.value == 0:
            return []  # No message

        # noinspection PyCallingNonCallable
        data = MsgDataType()

        for i in range(8):
            data[i] = rx_msg[i]

        return [rx_id.value, rx_dlc.value, rx_flags.value, 1000L * rx_time.value, list(data)]

    def close_channel(self, index):
        """
        Description: Closes communication channel.

        Example:
            com = KVASER()
            com.open_can_channel(0, 500000)
            ...
            com.close_channel(0)
        """
        self.canlib.canClose(c_int(self.canlib_txhnd[index]))
        self.canlib.canClose(c_int(self.canlib_rxhnd[index]))

        print 'INFO: KVASER device channel closed in LATTE "KVASER" channel ID {}'.format(str(index))
        return True
