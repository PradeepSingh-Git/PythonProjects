"""
====================================================================
Vector XL DLL wrapper
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import sys
import os
from ctypes import *
import vxl_canfd
import vxl_can
import vxl_lin
import vxl_fr


__author__ = 'Jesus Fidalgo, Miguel Periago, David Fillat'
__version__ = '1.5.1'
__email__ = 'jfidalgo@lear.com, mperiago@lear.com, dfillatcastellvi@lear.com'

"""
CHANGE LOG
==========
1.5.1 Virtual channels can be enabled with a configuration flag.
1.5.0 PEP8 rework.
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
      Added self.xl_lib.xlCloseDriver call inside close_channel method.
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
"""


# Prints additional info while debugging this library
VXL_DEBUG = False

# Used to enable virtual channels (Vector supports Virtual CAN only)
VXL_VIRTUAL_CHANNELS_ENABLED = False

# Max length os strings returned by the DLL
XL_STRING_MAX_LENGTH = 31

# Max communication channels that the DLL can manage
XL_CONFIG_MAX_CHANNELS = 64

# General value returned by the DLL in several APIs
XL_SUCCESS = 0

# Buffer for storing available licenses of the conencted devices
XL_LICENSE_BUFFER = 1024


class _XLCanParams(Structure):
    _pack_ = 1
    _fields_ = [
        ("bitRate", c_uint),
        ("sjw", c_ubyte),
        ("tseg1", c_ubyte),
        ("tseg2", c_ubyte),
        ("sam", c_ubyte),
        ("outputMode", c_ubyte)
    ]


# noinspection PyTypeChecker
class _XLDataParams(Union):
    _pack_ = 1
    _fields_ = [
        ("can", _XLCanParams),
        ("raw", c_ubyte * 32)
    ]


class _XLBusParams(Structure):
    _pack_ = 1
    _fields_ = [
        ("busType", c_uint),
        ("data", _XLDataParams)
    ]


# noinspection PyTypeChecker
class _XLChannelConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ("name", c_char * (XL_STRING_MAX_LENGTH + 1)),
        ("hwType", c_ubyte),
        ("hwIndex", c_ubyte),
        ("hwChannel", c_ubyte),
        ("transceiverType", c_ushort),
        ("transceiverState", c_uint),
        ("channelIndex", c_ubyte),
        ("channelMask", c_ulonglong),
        ("channelCapabilities", c_uint),
        ("channelBusCapabilities", c_uint),
        ("isOnBus", c_ubyte),
        ("connectedBusType", c_uint),
        ("busParams", _XLBusParams),
        ("driverVersion", c_uint),
        ("interfaceVersion", c_uint),
        ("raw_data", c_uint * 10),
        ("serialNumber", c_uint),
        ("articleNumber", c_uint),
        ("transceiverName", c_char * (XL_STRING_MAX_LENGTH + 1)),
        ("specialCabFlags", c_uint),
        ("dominantTimeout", c_uint),
        ("dominantRecessiveDelay", c_ubyte),
        ("recessiveDominantDelay", c_ubyte),
        ("reserved01", c_ushort),
        ("reserved", c_uint * 7)
    ]


# noinspection PyTypeChecker
class _XLDriverConfig(Structure):
    _pack_ = 1
    _fields_ = [
        ("dllVersion", c_uint),
        ("channelCount", c_uint),
        ("reserved", c_uint * 10),
        ("channel", _XLChannelConfig * XL_CONFIG_MAX_CHANNELS)
    ]


# noinspection PyTypeChecker
class _XLlicenseInfo(Structure):
    _pack_ = 1
    _fields_ = [
        ("bAvailable", c_ubyte),
        ("licName", c_ubyte * 65)
    ]


# noinspection PyTypeChecker
class XLCOM(vxl_can.XLCOMCan, vxl_lin.XLCOMLin, vxl_fr.XLCOMFr, vxl_canfd.XLCOMCanFD):
    """
    Vector DLL (vxlapi.dll_core) wrapper.
    """

    def __init__(self):
        """
        Description: Constructor. Loads vxlapi.dll_core, opens drivers and reads conencted Vector devices.
        """
        # Init of inherited classes
        vxl_can.XLCOMCan.__init__(self)
        vxl_lin.XLCOMLin.__init__(self)
        vxl_fr.XLCOMFr.__init__(self)
        vxl_canfd.XLCOMCanFD.__init__(self)

        # Init of internal vars
        self.xl_hnd = {}
        self.fr_bus_state = []
        self.current_cycle = {}
        self.channel_list = []
        self.msg_event = {}
        self.version = None
        self.channel_license = []
        self.channel_info = []
        self.device_info = []
        self.scan_devices_executed = False

        # Load vxlapi.dll_core
        this_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
        os.environ['PATH'] = this_path + ';' + os.environ['PATH']
        try:
            self.xl_lib = windll.vxlapi
        except WindowsError:
            print 'INFO: Failed to load vxlapi.dll_core, reasons could be:'
            print '      - 64 bits version of Python being used. It must be 32 bits version (also called x86)'
            print '      - 64 bits version of PyScripter IDE being used. It must be 32 bits version (also called x86)'
            raise WindowsError('ERROR: Failed to load vxlapi.dll_core')

        # Open XL driver
        try:
            self.xl_lib.xlOpenDriver()
        except WindowsError:
            print 'ERROR: Failed to open Vector XL driver. You need to install Vector drivers ' \
                  '\n        from the CD installation tool CANoe_7.6_LIN\Drivers\Drivers\64_Bit\setup.exe'

        self._init_xl_devices()
        self.scan_devices()

    def _init_xl_devices(self):
        """
        Description: Inits Vector XL devices connected.

        Note: This method is used internally by other public methods
        """
        self.drv_config = _XLDriverConfig()
        xlerror = self.xl_lib.xlGetDriverConfig(byref(self.drv_config))
        if xlerror != XL_SUCCESS:
            print 'ERROR: Failed to read information from xlGetDriverConfig function'
            sys.exit()
        else:
            if self.drv_config.channelCount == 0:
                print 'ERROR: No HW channels found'
                sys.exit()

        self.fr_bus_state = [0] * self.drv_config.channelCount

    def scan_devices(self):
        """
        Description: Scans all Vector devices connected.
        Returns list of devices found, and prints useful info describing the devices connected and channels available

        Example:
            com = XLCOM()
            com.scan_devices()
        """
        if not self.scan_devices_executed:
            hw_channels_found = False
            self._init_xl_devices()
            for i in range(self.drv_config.channelCount):
                if 'Virtual' not in self.drv_config.channel[i].name or VXL_VIRTUAL_CHANNELS_ENABLED:
                    print 'INFO: The following VECTOR device channel is ' \
                          'available as LATTE "VECTOR" channel ID {0}: '.format(str(i))
                    serial_number = str(self.drv_config.channel[i].articleNumber) + "-" + str(
                        self.drv_config.channel[i].serialNumber)
                    print '      {} {}'.format('Device S/N:', serial_number)
                    self.device_info.append(serial_number)
                    channel_info = self.drv_config.channel[i].name
                    print '      {} {}'.format('Channel:', channel_info)
                    self.channel_info.append(channel_info)
                    transceiver_info = self.drv_config.channel[i].transceiverName
                    print '      {} {}'.format('Transceiver:', transceiver_info)
                    self.channel_list.append('VECTOR ' + serial_number + ' ' + channel_info + ' ' + transceiver_info)
                    hw_channels_found = True
                    license_array_size = c_uint(XL_LICENSE_BUFFER)
                    # noinspection PyCallingNonCallable
                    license_array = (_XLlicenseInfo * XL_LICENSE_BUFFER)()
                    channel_mask = c_ulonglong(self.drv_config.channel[i].channelMask)
                    status = self.xl_lib.xlGetLicenseInfo(channel_mask, byref(license_array), license_array_size)
                    self.channel_license.append('')
                    if status == XL_SUCCESS:
                        for lic_loop in range(XL_LICENSE_BUFFER):
                            if license_array[lic_loop].bAvailable == 1:  # check if license is present
                                result_str = string_at(license_array[lic_loop].licName)
                                print '      {} {}'.format('License:', result_str)
                                self.channel_license[i] = self.channel_license[i] + result_str + ','
                    if self.channel_license[i] == '':
                        print '{} {}'.format('License:', 'None')
                        self.channel_license[i] = 'None'

            if not hw_channels_found:
                raise Exception('ERROR: VECTOR device not found')

        self.scan_devices_executed = True
        return self.channel_list

    def close_channel(self, index):
        """
        Description: Closes communication channel.

        Example:
            com = XLCOM()
            com.open_can_channel(0, XL_CAN_BITRATE_500K)
            ...
            com.close_channel(0)
        """
        channel_mask = c_ulonglong(self.drv_config.channel[index].channelMask)
        self.xl_lib.xlDeactivateChannel(self.xl_hnd[index], channel_mask)
        self.xl_lib.xlClosePort(self.xl_hnd[index])

        status = self.xl_lib.xlCloseDriver()
        if status == XL_SUCCESS:
            print 'INFO: Vector device channel closed in LATTE "VECTOR" channel ID {}'.format(str(index))
            return True
        else:
            print 'ERROR: When closing Vector device channel in LATTE "VECTOR" channel ID {}'.format(str(index))
            return False
