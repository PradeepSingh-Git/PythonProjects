'''
====================================================================
Library for working with CAN, LIN & FlexRay to communicate with an ECU
(C) Copyright 2017 Lear Corporation
====================================================================
'''
__author__ = 'Jesus Fidalgo, Marc Bajet, Albert Sanz'
__version__ = '1.9.0'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.9.0 Using database files from <data> folder
1.8.2 Added detection of missing libraries for Gigabox device
1.8.1 Added initial support for ECU Extract as FlexRay database
1.8.0 Added FlexRay support
1.4.3 Fixed bug in lin slave/master load
1.4.2 Import of sub-modules done before class init.
1.4.1 Implemented lin master node behavior.
1.4.0 Sub-libraries CAN/LIN/DGN/DRV loaded automatically from com.py
1.3.4 Solving problem in open_lin_channel when init signals with default values from LDF file
1.3.3 Renaming of vxlapi.py to vxl.py and kvaserapi.py to kvaser.py
1.3.2 Added method close_channel
1.3.1 Solved problem when closing channels with exit method
1.3.0 Added support for KVASER devices
1.2.4 Default values from ldf loaded in open_lin_channel
1.2.3 Methods switch_on_lin_id and switch_on_lin_id added to lin_list, needed by lin.py library version 1.3.1
1.2.2 Method open_lin_channel added to lin_list, needed by lin.py library version 1.3.0
1.2.1 Added exit method to stop CAN rx thread and close CAN and LIn channels
1.2.0 [MPeriago] Added send_lin_wake_up method
1.1.0 Method open_lin_channel does not need 'speed' and 'version' params anymore
1.0.1 Added delay of 0.5s after opening CAN channel
1.0.0 Initial version
'''

import sys
import drv
import can
import lin
import fry
import data
import time

class Com:
    '''
    Class for accessing CAN, LIN and FlexRay communications.
    '''

    def __init__(self, driver):
        '''
        Description: Constructor. Access the physical communication device. It also prints useful information about
        the devices found and the channels available.
        Parameter 'driver' can be either 'VECTOR' or 'KVASER'.

        Example:
            com = COM('VECTOR')
        '''
        self.can_list = []
        self.lin_list = []
        self.fr_list = []
        self.channels_list = []

        if driver == 'VECTOR':
            self.drv = drv.XLCOM()
        elif driver == 'KVASER':
            self.drv = drv.KVASER()
        elif driver == 'GIGABOX':
            try:
                self.drv = drv.GIGABOX()
            except AttributeError:
                raise Exception('ERROR: GIGABOX Python libraries not found. Please execute LATTE\Com\Trunk\drivers\gigabox\Install_Pythonnet_for_GtFrNET.bat')

        self.drv.scan_devices()


    def open_can_channel(self, index, speed):
        '''
        Description: Opens CAN channel.
        Parameter 'index' is one of the channel indexes provided in the info printed by the constructor.
        Parameter 'speed' is the speed in bps.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(0, 500000)
        '''
        if index in self.channels_list:
            print 'ERROR: Trying to open CAN channel with HW index ' + str(index) + ', channel already in use.'
            sys.exit()
        # Open physical channel
        self.drv.open_can_channel(index, speed)
        self.can_list.append(can.CAN(index))
        self.channels_list.append(index)
        self.can_list[-1].write_can_frame = self.drv.write_can_frame
        self.can_list[-1].read_can_frame = self.drv.read_can_frame
        self.can_list[-1].close_channel = self.drv.close_channel
        # Start thread for storing CAN frames
        self.can_list[-1]._start_frame_reception()

        return self.can_list[-1]


    def open_lin_channel(self, index, ldf_file, mode='SLAVE'):
        '''
		Description: Opens LIN channel.
        Parameter 'index' is one of the channel indexes provided in the info printed by the constructor.
        Parameter 'ldf_file' is a LDF file with the description of the LIN bus.
        Paramter 'mode' sets the behavior of the bus (MASTER or SLAVE).

        Note: The LIN device will work as a slave node in the channel open by this method.
        It will be able to put the data to a recognised header sent by the master (the ECU). The recognised
        headers will be those frames in the LDF file defined as 'slave'.

        Note: The LDF file is needed for opening the LIN channel, because the LIN driver needs to know the
        slave frame IDs.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf', 'SLAVE')
        '''
        if index in self.channels_list:
            print 'ERROR: Trying to open LIN channel with HW index ' + str(index) + ', channel already in use.'
            sys.exit()
        ldf = data.LDF(ldf_file)
        # Open physical channel
        if mode == 'MASTER':
            slave_frames = ldf.master_frames # master frames are auto-filled as slave frames
        else:
            slave_frames = ldf.slave_frames

        self.drv.open_lin_channel(index, ldf.lin_speed, ldf.lin_protocol, slave_frames, mode)
        self.lin_list.append(lin.LIN(index, ldf, mode))
        self.channels_list.append(index)
        self.lin_list[-1].write_lin_frame = self.drv.write_lin_frame
        self.lin_list[-1].read_lin_frame = self.drv.read_lin_frame
        self.lin_list[-1].switch_on_lin_id = self.drv.switch_on_lin_id
        self.lin_list[-1].switch_off_lin_id = self.drv.switch_off_lin_id
        self.lin_list[-1].send_lin_wake_up = self.drv.send_lin_wake_up
        self.lin_list[-1].send_lin_request = self.drv.send_lin_request
        self.lin_list[-1].write_lin_frame_master = self.drv.write_lin_frame_master
        self.lin_list[-1].close_channel = self.drv.close_channel
        self.lin_list[-1].send_lin_sleep = self.drv.send_lin_sleep
        # Init signals with default values from LDF file
        for (_, frame) in ldf.frames.items():
            if frame.nodeType == 'Slave':
                for signal in frame.signals:
                    self.lin_list[-1].set_signal(signal.name, signal.default)
        # Start thread for storing LIN frames
        self.lin_list[-1]._start_frame_reception()

        return self.lin_list[-1]

    def open_fr_channel(self, index, database_file, fr_channel, ecu_under_test = '', cold_start_message_list = [], bus_start_timeout = 2.0, cluster = ''):
        """
        Description: Opens FlexRay channel.
        Parameter 'index' is one of the channel indexes provided in the info printed by the constructor.
        Parameter 'database_file' is the filename of a FIBEX or AUTOSAR ECU Extract file with the description of the
                   FlexRay cluster, controller and events.
        Parameter 'fr_channel' is the FlexRay channel to be used during communication, 'FrChannel_A' or 'FrChannel_B'.
        Parameter 'ecu_under_test' is the name of the ECU under test defined in the FIBEX or AUTOSAR ECU Extract file.
        Parameter 'cold_start_message_list' list of messages to be used as cold start, none, one or two
                  (which have to be defined in FIBEX as STARTUP-SYNC slots).
        Parameter 'bus_start_timeout' function will wait until bus communication is established, NORMAL_ACTIVE state, or
                   timeout is elapsed.
		Parameter 'cluster' is the name of the FlexRay cluster to configure in case of using an ECU Extract database.

        Note: The FIBEX file is needed for opening the FlexRay channel because the cluster
        configuration must be set before activating the channel.

        Example:
            com = COM('VECTOR')
            fr1 = com.open_fr_channel(0, 'PowerTrain.xml', 'FrChannel_A', 'ECM', ['1','10'], 1.0)
        """
        if index in self.channels_list:
            print 'ERROR: Trying to open FlexRay channel with HW index ' + str(index) + ', channel already in use.'
            sys.exit()
        flexray_object = fry.FLEXRAY(index, database_file, fr_channel, cold_start_message_list, cluster)
        cluster_config = flexray_object.database.cluster_config
        message_config = flexray_object.database.hTableOfFrames
        self.drv.open_fr_channel(index, cluster_config, message_config, ecu_under_test)
        self.fr_list.append(flexray_object)
        self.channels_list.append(index)
        self.fr_list[-1].write_fr_frame = self.drv.write_fr_frame
        self.fr_list[-1].read_fr_frame = self.drv.read_fr_frame
        self.fr_list[-1].get_fr_state = self.drv.get_fr_state
        self.fr_list[-1].get_fr_cycle = self.drv.get_fr_cycle
        self.fr_list[-1]._start_frame_reception()

        # Wait till FR bus communication is established, or timeout...
        time_start = time.clock()
        time_elapsed = 0.0
        bus_state = self.drv.get_fr_state(index)
        while bus_state is not 'FR_STATUS_NORMAL_ACTIVE' and time_elapsed < bus_start_timeout:
            bus_state = self.drv.get_fr_state(index)
            time_elapsed = time.clock() - time_start
        if time_elapsed >= bus_start_timeout:
            print 'INFO: FlexRay channel open but communication not established: bus in ' + self.drv.get_fr_state(index) + '\n'
        else:
            print 'INFO: FlexRay channel open and communication established: bus in FR_STATUS_NORMAL_ACTIVE\n'

        return self.fr_list[-1]

    def close_channel(self, index):
        '''
        Description: Closes CAN or LIN channel.
        Parameter 'index' is one of the channel indexes provided in the info printed by the constructor.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            ...
            com.close_channel(0)
        '''
        if index in self.channels_list:
            self.drv.close_channel(index)
            self.channels_list.remove(index)

    def exit(self, can_log=True, lin_log=True):
        '''
        Description: Saves log files and closes CAN and LIN channels.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            ...
            com.exit()
        '''
        for can_chan in self.can_list:
            if can_log:
                can_chan.save_logfiles()
                can_chan._stop_frame_reception()
        for lin_chan in self.lin_list:
            if lin_log:
                lin_chan.save_logfiles()
            lin_chan._stop_frame_reception()

        for fr_chan in self.fr_list:
            fr_chan._stop_frame_reception()

        for index in self.channels_list:
            self.drv.close_channel(index)
        self.channels_list = []
