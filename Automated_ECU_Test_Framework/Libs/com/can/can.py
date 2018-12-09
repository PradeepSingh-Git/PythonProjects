'''
====================================================================
CAN library for working with frames/signals, diagnostics and CCP/XCP
(C) Copyright 2017 Lear Corporation
====================================================================
'''

__author__  = 'Miguel Periago'
__version__ = '1.3.0'
__email__   = 'mperiago@lear.com'

'''
CHANGE LOG
==========
1.3.0 Using database files from <data> folder
      Error solved in look_for_frame_and_signal, Frame() and Signal() classes do not exist
1.2.13 Using dgn, ccp and xcp only if enabled in their configuration files.
1.2.12 Added initial support for ECU Extract as CAN database.
       Added find_frame_name method to find frameName from ID.
       Moved some methods from dbc.py to can.py (so that they can be used with a DBC or with an ECUextract)
1.2.11 Added clear_rx_frame_counter method
1.2.10 get_plot_signal_frame modified to give all the info needed to plot library.
1.2.9 Plot library call removed. Method to provide the data for plotting created.
1.2.8 Frames integrity improved.
1.2.7 Added plot feature.
      Method _frames_to_send buffer protected in case of trying to schedule an already existing frame in the buffer.
1.2.6 Update bit management removed. It should be placed in an upper layer.
1.2.5 Methods set_signal and get_signal improved for update bits management
1.2.4 Method _frames_to_send buffer protected in case of trying to schedule an already existing frame in the buffer
1.2.3 Method send_cyclic_frame has "period" parameter as optional. If omitted, the default period of the frame is used
1.2.2 Channel open message moved to vxlapi.py and kvaserapi.py
1.2.1 Added private method for stopping thread of frame reception. Will be called from com.py
1.2.0 Added integrity update for several CAN frames
      Methods set_signal and send_frame_immediately_with_signal allows optional param to specify frame name of the signal
      Thread txrx_thread set as daemon
1.1.0 Using dgn.py instead of iso14229.py for diagnostics
1.0.0 Inital version
'''

import threading
import os
import time
from collections import deque
from time import clock
from ..data import ECUextract
from ..data import DBC
from ..dgn import dgncan_available
if dgncan_available:
    from ..dgn import *
from .ccp_cfg import ccpcan_available
if ccpcan_available:
    from .ccp import *
from .xcp_cfg import xcpcan_available
if xcpcan_available:
    from .xcp import *


CAN_TICK_TIME = 5 # ms
CAN_TICK_TIME_SECONDS = float(CAN_TICK_TIME)/1000

DEQUE_SIZE = 100

class Frame:
    name = ''
    canid = 0
    dlc = 0
    publisher = ''
    cycleTime = 0

class Signal:
    signalName = ''
    signalLength = 0
    offset = 0
    updatebit = 9999
    littleEndianStart = False # This indicates where starts to count the offset

class _CanFrameSch:
    def __init__(self):
        self.canid = 0
        self.cycleTime = 0
        self.timer = 0
        self.name = 'void'
        self.dlc = 8
        self.message = 8*[0]
        self.integrityUpdate = False


class _CanFrameRcv:
    def __init__(self):
        self.canid = 0
        self.name = 'void'
        self.dlc = 8
        self.time = 5*[0]
        self.message = 5*[8*[0]]
        self.rxCounter = 1
        self.updateFlag = False
        self.plotBuffer = []


class FrameToTx:
    canid = ''
    dlc = 0
    message = 8 * [0]


FR_BIT_MAP = (7, 6, 5, 4, 3, 2, 1, 0,
              15, 14, 13, 12, 11, 10, 9, 8,
              23, 22, 21, 20, 19, 18, 17, 16,
              31, 30, 29, 28, 27, 26, 25, 24,
              39, 38, 37, 36, 35, 34, 33, 32,
              47, 46, 45, 44, 43, 42, 41, 40,
              55, 54, 53, 52, 51, 50, 49, 48,
              63, 62, 61, 60, 59, 58, 57, 56)

class CAN:
    '''
    Class for managing CAN frames in a bus. Allows to work with DBC files, diagnostics, and CCP/XCP.
    This class is used by COM class in com.py, so you'll see all examples below with the real usage
    in a Python script.
    '''

    def __init__(self, index):
        '''
        Description: Constructor.
        Parameter 'index' is the channel index used for tx/rx CAN frames. The channel index available.
        are listed when creating a COM object.
        '''
        self.index = index
        self.database = None
        # Init some vars
        self._frames_to_send = []
        self._frames_received = []
        self._rx_frames_deque = {}      # can_id: [CanFrameRcv0, CanFrameRcv1...]
        self._txrx_thread_active = False
        self._tx_active = False
        self._set_signal_allowed = True
        self.plot_active = False
        self.framesStore = {}

        # Init DGN
        if dgncan_available:
            self._init_dgn()

        # Init CCP
        if ccpcan_available:
            self._init_ccp()

        # Init XCP
        if xcpcan_available:
            self._init_xcp()

    def _start_frame_reception(self):
        '''
        Description: Launches the TX frames scheduler section in _main_task_tx_rx thread. This will also enable the RX section.
        '''
        if self._txrx_thread_active == False:
            self._txrx_thread_active = True
            self.txrx_thread = threading.Thread(target = self._main_task_tx_rx)
            self.rx_deque_lock = threading.Lock()
            self.txrx_thread.daemon = True
            self.txrx_thread.start()

    def _stop_frame_reception(self):
        '''
        Description: Stops the TX frames scheduler section in _main_task_tx_rx thread. This will also disable the RX section.
        '''
        self._txrx_thread_active = False
        self.txrx_thread.join()

    def _main_task_tx_rx(self):
        '''
        Description: Sends and receive frames on cycle timer expiration.
        '''
        start_time = clock()
        while self._txrx_thread_active:
            elapsedTime = clock() - start_time
            # Send
            if elapsedTime >= CAN_TICK_TIME_SECONDS:
                start_time = clock()
                # Send:
                if self._tx_active == True:
                    for item in self._frames_to_send:
                        item.timer -= CAN_TICK_TIME
                        if item.timer <= 0:
                            item.timer = item.cycleTime
                            if item.integrityUpdate == True:
                                self._set_signal_allowed = False
                                self._apply_integrity(item)
                                self._set_signal_allowed = True
                            self.write_frame(item.canid, item.dlc, item.message)

            # Receive: do it for each tick time
            fr = self.read_frame()
            if fr != [] and fr != None:
                found = False
                for item in self._frames_received:
                    if fr[0] == item.canid:
                        found = True
                        item.time.pop()
                        item.time.appendleft(fr[3])
                        item.message.pop()
                        item.message.appendleft(fr[4]) # New message added
                        item.rxCounter += 1
                        item.updateFlag = True
                        item.dlc = fr[1]
                        if self.plot_active == True:
                            if item.message[0] != item.message[1] or not item.plotBuffer: # Check for a different message or empty list
                                plotPoint = {}
                                plotPoint[item.time[0]] = item.message[0] #Save message and time
                                item.plotBuffer.append(plotPoint)
                        break

                if found:
                    # Store frame in FIFO/LIFO deque
                    rx_frame = _CanFrameRcv()
                    (rx_frame.canid, rx_frame.dlc, flags, rx_frame.time, rx_frame.message) = fr

                    with self.rx_deque_lock:  # acquire/release
                        rx_deque = self._rx_frames_deque[rx_frame.canid]
                        rx_deque.append(rx_frame)

                else:
                    self._add_frame_to_rcv(fr)

    def get_plot_signal_frame(self, signalName, frameName = None):
        '''
        Description: get the needed points for drawing a plot using Plot class
        Parameter signalName: Signal name to be plot.
        Parameter file_name: [optional] Name of the plot file created. If omitted the signal name is used.
        Parameter frameName: [optional] frame name where the signal is found.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
            time.sleep(2)
            v_can.stop_plot_record()
            signal_info = can.get_plot_signal_frame('signal_3', 'Frame')
        '''
        if self.database == None:
            print 'CAN get_rx_frame_counter method can only be called if a database has been loaded.'
            sys.exit()
        frame, signal = self.look_for_frame_and_signal(signalName, frameName)
        if frame == None:
            return 0 # Frame not in database
        for item in self._frames_received:
            if item.canid == int(frame.canid):
                return (item.plotBuffer, signal, self.database, (self.plot_start_time, self.plot_stop_time)) # signal info to be used with plot class

        return 0 # Frame not received

    def start_plot_record(self):
        '''
        Description: Start saving data to draw a plot of a signal from the Rx Buffer.
        Note: This will clear all the previous data stored.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
        '''
        # Clean the buffer
        self.plot_active = False
        self.plotBuffer = []
        # Start saving the frames
        self.plot_active = True
        self.plot_start_time = time.time()

    def stop_plot_record(self):
        '''
        Description: Stop saving data to draw a plot of a signal from the Rx Buffer.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
            time.sleep(2)
            v_can.stop_plot_record()
        '''
        self.plot_active = False
        self.plot_stop_time = time.time()

    def _apply_integrity(self, canFrame):
        '''
        Description: Allows to apply integrity update to a CAN frame before sending it.
        For example, increase a signal of AliveCounter, or update a signal of Checksum.
        Parameter canFrame is an object of type _CanFrameSch

        Note: The implementation of this method depends on each project requirements.

        Example:
        # Apply integrity only to frames that really need it, in this case ABS_PT_C
        if canFrame.name == 'ABS_PT_C':

            # update alive counter
            if(self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT') == 15):
                self._set_signal_to_be_sent('ABSAliveCounter_HS2_PT', 0)
            else:
                self._set_signal_to_be_sent('ABSAliveCounter_HS2_PT', self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT') + 1)

            # calculate checksum and update signal ABSChecksum_PT
            ABSPwrTrnTorqReq_sf = self._get_signal_to_be_sent('ABSPwrTrnTorqReq_HS2_PT')
            BrakePressureQF_sf = self._get_signal_to_be_sent('BrakePressureQF_HS2_PT')
            ABSAliveCounter_sf = self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT')
            VehicleSpeedQF_sf = self._get_signal_to_be_sent('VehicleSpeedQF_HS2_PT')
            checksum = ABSPwrTrnTorqReq_sf + BrakePressureQF_sf + ABSAliveCounter_sf + VehicleSpeedQF_sf
            self._set_signal_to_be_sent('ABSChecksum_PT', checksum)
        '''
        pass

    def _set_signal_to_be_sent(self, signalName, value, frameName=None):
        '''
        Description:  Once a frame has been set to be sent periodically and it contains signal "signalName",
        this method sets value of signal "signalName" just before the next time the periodic frame is sent.

        Use this method inside _apply_integrity method to write the contents of signals that are going to be sent,
        for example in the case you need to write an alive counter or a checksum.
        '''
        if self.database == None:
            print 'CAN set_signal method can only be called if a database has been loaded.'
            sys.exit()
        result = True
        frame = self.write_signal_to_frame(signalName, value, frameName)
        if frame != None:
            for item in self._frames_to_send:  # Checking if frame is already scheduled
                if frame.canid == item.canid:
                    item.message = frame.message
                    break
        else:
            result = False

        return result

    def _get_signal_to_be_sent(self, signalName):
        '''
        Description: Once a frame has been set to be sent periodically and it contains signal "signalName",
        this method returns the value of signal "signalName" that will be sent next time the periodic frame is sent.

        Use this method inside _apply_integrity method to know the contents of signals that are going to be sent,
        and modify them (for example in the case of an alive counter) or read them (for example to calculate a checksum).
        '''
        if self.database == None:
            print 'CAN get_signal method can only be called if a database has been loaded.'
            sys.exit()
        frame_signalName, signal_signalName = self.look_for_frame_and_signal(signalName)
        found = False
        if frame_signalName != None:
            for item in self._frames_to_send:
                if item.canid == int(frame_signalName.canid): # Check if the frame is present in received buffer
                    found = True
                    return self.read_signal_in_frame(int(signal_signalName.offset), int(signal_signalName.signalLength), item.message, signal_signalName.littleEndianStart)

        if not found:
            return 0

    def _add_frame_to_rcv(self,fr):
        '''
        Description: Creates a new object in the main received frames buffer.
        '''
        frRcv = _CanFrameRcv()
        frRcv.time[0] = fr[3]
        frRcv.time = deque(frRcv.time)
        frRcv.canid = fr[0]
        frRcv.message[0] = fr[4]
        frRcv.message = deque(frRcv.message)
        frRcv.updateFlag = True
        frRcv.dlc = fr[1]
        self._frames_received.append(frRcv)

        # Initialize received frames deque
        fr2 = _CanFrameRcv()
        (fr2.canid, fr2.dlc, flags, fr2.time, fr2.message) = fr
        self._rx_frames_deque[fr2.canid] = deque(maxlen=DEQUE_SIZE)
        self._rx_frames_deque[fr2.canid].append(fr2)

    def _init_dgn(self):
        '''
        Description: Prepares diagnostics in this CAN channel.
        '''
        self.dgn = DGN()
        self.dgn.iso.net.read_dgn_frame = self.get_frame
        self.dgn.iso.net.write_dgn_frame = self.write_frame

    def _init_ccp(self):
        '''
        Description: Prepares CCP in this CAN channel.
        '''
        self.ccp = CCP()
        self.ccp.read_ccp_frame = self.get_frame
        self.ccp.write_ccp_frame = self.write_frame

    def _init_xcp(self):
        '''
        Description: Prepares XCP in this CAN channel.
        '''
        self.xcp = XCP()
        self.xcp.read_xcp_frame = self.get_frame
        self.xcp.write_xcp_frame = self.write_frame

    def read_frame(self):
        '''
        Description: Reads CAN frame from channel.

        Returns: frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Note: This function is blocking. This means that the execution of the Python script will be stuck here
        until a CAN frame is received in the bus.

        Note: self.read_can_frame method has been added dinamically in com.py

        Note: Used internally in this class, not very useful if used outside, because it will read the first frame
        availbale in the bus. Anyway it has been left as public.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            frame_rx = hs_can.read_frame()
        '''
        return self.read_can_frame(self.index)

    def write_frame(self, canid, dlc, data):
        '''
        Description: Writes CAN frame to channel.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' is the data length code.
        Parameter 'data' is a list with the data bytes.

        Note: self.write_can_frame method has been added dinamically in com.py

        Note: Used internally in this class, not very useful if used outside, because this library is aimed to
        work with frames and signals loaded from a DBC file. Anyway it has been left as public.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            hs_can.write_frame(0x1A0, 8, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        '''
        self.write_can_frame(self.index, canid, dlc, data)

    def load_dbc(self, dbc_file):
        '''
        Description: Loads DBC file into several structs.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
        '''
        self.database = DBC(dbc_file)

    def load_ecu_extract(self, arxml_file, cluster_name):
        '''
        Description: Loads AUTOSAR ECU Extract file into several structs.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            hs_can.load_ecu_extract('VCU1SystemExtract.arxml', 'Rear1CAN)
        '''
        ecu = ECUextract(arxml_file)
        self.database = ecu.clusters_dict.get(cluster_name)
        if self.database is None:
            print "Error, selected cluster not present in ECU Extract"
            sys.exit()

    def send_cyclic_frame(self, frameName, period=0, integrityUpdate=False):
        '''
        Description: Adds a frame to the schedule buffer for periodic transmission.

        Note: This method is available only if a database has been called previously.

        Note: Parameter "period" is optional. If omitted, the default period of the frame specified
        in the DBC will be used.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
        '''
        if self.database == None:
            print 'CAN send_cyclic_frame method can only be called if a database has been loaded.'
            sys.exit()
        if frameName == 'None' or period == None:
            return
        if period < CAN_TICK_TIME:
            period = self.find_period_frame(frameName)
            #print "Default period send for " + frameName + " is "+ str(period) + " ms"
            if period == 0:
                print "The cycle time for " + frameName + " must be " + str(CAN_TICK_TIME) + " ms or greater"
                return
        fr = _CanFrameSch()
        fr.canid, fr.dlc = self.find_frame_id(frameName)
        if fr.canid == None:
            print frameName + " not found in dbc"
            return
        fr.cycleTime = period
        fr.timer = period
        fr.name = frameName
        fr.integrityUpdate = integrityUpdate
        frame_scheduled = False
        for item in self._frames_to_send:
            if item.canid == fr.canid:
                frame_scheduled = True
                break
        if frame_scheduled == False:
            self._frames_to_send.append(fr)
        self._tx_active = True

    def stop_cyclic_frame(self, frameName):
        '''
        Description: Removes frame from scheduling buffer.

        Note: This method is available only if a database has been called previously.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
            hs_can.stop_cyclic_frame('FrameNameInDbc')
        '''
        if self.database == None:
            print 'CAN stop_cyclic_frame method can only be called if a database has been loaded.'
            sys.exit()
        if frameName == 'None':
            return
        found = False
        frId, frDlc = self.find_frame_id(frameName)
        if frId == None:
            return
        index = 0
        for item in self._frames_to_send:
            if frId == item.canid:
                found = True
                break
            index += 1
        if found:
            del self._frames_to_send[index]

    def stop_tx_frames(self):
        '''
        Description: Stops the frame sending scheduler section in Tx/Rx thread.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
            hs_can.stop_tx_frames()
        '''
        if self.database == None:
            print 'CAN stop_tx_frames method can only be called if a database has been loaded.'
            sys.exit()
        self._tx_active = False

    def set_signal(self, signalName, value, frameName=None):
        '''
        Description: Sets value in signal for the scheduled frames. If the frame is not already scheduled, nothing is done.
        It allows to write signals of any length, up to 32 bits in numeric way, or more than 32 bits in array way. See example below.
        Returns False in case the signal is not present in the dbc.

        Note: If you need to send this signal/frame immediately because it's event/sporadic, see method send_frame_immediately_with_signal.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.set_signal('SignalNameInDbc_1', [0x11, 0x22, 0x33, 0x44, 0x55]) # for a signal of several bytes long
            hs_can.set_signal('SignalNameInDbc_2', 5) # for a signal up to 32 bits
        '''
        while self._set_signal_allowed == False:
            pass
        if self.database == None:
            print 'CAN set_signal method can only be called if a database has been loaded.'
            sys.exit()
        result = True
        frame = self.write_signal_to_frame(signalName, value, frameName)
        if frame != None:
            for item in self._frames_to_send:  # Checking if frame is already scheduled
                if frame.canid == item.canid:
                    item.message = frame.message
                    break
        else:
            result = False

        return result

    def get_signal(self, signalName, frameName = None):
        '''
        Description: Finds the latest signal in the frames buffer and returns the signal value.
        This method does not check if latest frame was fresh or similar. It just return the signal of
        the latest frame received. If checking the freshness of the frame is important, have a look
        at method get_frame.

        Note: Returns an integer for signals up to 32 bits. Dont's use this method for longer than 32 bits
        signals, use get_frame method instead.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            value = hs_can.get_signal('SignalNameInDbc_1')
        '''
        if self.database == None:
            print 'CAN get_signal method can only be called if a database has been loaded.'
            sys.exit()
        frame_signalName, signal_signalName = self.look_for_frame_and_signal(signalName, frameName)
        found = False
        if frame_signalName != None:
            for item in self._frames_received:
                if item.canid == int(frame_signalName.canid): # Check if the frame is present in received buffer
                    found = True
                    return self.read_signal_in_frame(int(signal_signalName.offset), int(signal_signalName.signalLength), item.message[0], signal_signalName.littleEndianStart)

        if not found:
            return 'void'

    def get_cycle_time(self, frameName):
        '''
        Description: Returns the cycle time calculated from the 2 last received frames.
        The time is returned in ms.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            value = hs_can.get_cycle_time('SignalNameInDbc_1') # Time in ms
        '''
        if self.database == None:
            print 'CAN get_cycle_time method can only be called if a database has been loaded.'
            sys.exit()
        frId, frDlc = self.find_frame_id(frameName)
        if frId == None:
            return 0 # Frame not in database
        for item in self._frames_received:
            if item.canid == frId:
                cycleTime = item.time[0] - item.time[1] # Time in ns
                cycleTime /= 1e6 # Time in ms
                return cycleTime
        return 0 # Frame not received

    def get_frame(self, frameId):
        '''
        Description: Returns frame content from buffer if a fresh frame is available. If a frame is returned,
        the frame is no longer considered as fresh, and new calls to this method will return an empty list [],
        until a new frame arrives.
        Returns [id, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            frame_value = hs_can.get_frame(0x1A0) # if you know the CAN ID of the frame
            frame_value = hs_can.get_frame(hs_can.find_frame_id('FrameNameInDbc')[0]) # if you know the name of the frame
        '''
        for frame in self._frames_received:
            if frame.canid == frameId:
                if frame.updateFlag == True:
                    frame.updateFlag = False
                    return [frame.canid, frame.dlc, frame.time[0], frame.message[0]]
                else:
                    return []
        return []

    def get_frame_from_deque(self, frameId, popleft=False):
        '''
        Description: Finds the frame in the frames deque buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, timeStamp, [B0, B1, B2, B3, B4...]].

        Parameter 'frameName' is a string
        Parameter 'popleft' is a boolean. It determines whether to perform a
                  pop (LIFO) or popleft (FIFO) operation.

        Example:
            >>> com = COM('VECTOR')
            >>> can1 = com.open_can_channel(1, 500000)
            >>> brake_control_frame = can1.get_frame_from_deque(125)
        '''
        rx_deque = self._rx_frames_deque.get(frameId)

        if rx_deque is None:
            return None

        with self.rx_deque_lock:    # acquire/release
            try:
                if popleft:
                    frame = rx_deque.popleft()
                else:
                    frame = rx_deque.pop()

            except IndexError:
                frame = None

        if frame is not None:
            result_fr = [frame.canid, frame.dlc, frame.time, frame.message]
            return result_fr
        else:
            return None

        # # Use existing deque
        # for frame in self._frames_received:
        #     if frame.canid == frameId:
        #         try:
        #             if popleft:
        #                 message = frame.message.popleft()
        #                 timestamp = frame.time.popleft()
        #             else:
        #                 message = frame.message.pop()
        #                 timestamp = frame.time.pop()
        #         except IndexError:
        #             message = None
        #
        #         if message is not None:
        #             return [frame.canid, frame.dlc, timestamp, message]
        #         else:
        #             return None

    def clear_rx_deque(self):
        """
        Clears the received frames deque, for each received frame ID.
        """
        with self.rx_deque_lock:
            for canid, frames_deque in self._rx_frames_deque.iteritems():
                frames_deque.clear()

    def get_rx_frame_counter(self, frameName):
        '''
        Description: Returns the value of the received frames counter. Every frame as a rx counter that is increased every time
        a frame is received. This counter is useful to check the number of messages received in a fixed elapsed time.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            count_1 = hs_can.get_rx_frame_counter('FrameNameInDbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            count_2 = hs_can.get_rx_frame_counter('FrameNameInDbc')
            print str(count_2 - count_1) + ' frames FrameNameInDbc received during 5 seconds'
        '''
        if self.database == None:
            print 'CAN get_rx_frame_counter method can only be called if a database has been loaded.'
            sys.exit()
        frId, frDlc = self.find_frame_id(frameName)
        if frId == None:
            return 0 # Frame not in database
        for item in self._frames_received:
            if item.canid == frId:
                return item.rxCounter
        return 0 # Frame not received

    def clear_rx_frame_counter(self, frameName):
        '''
        Description: Clears value of the received frames counter.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            count_1 = hs_can.clear_rx_frame_counter('FrameNameInDbc')
        '''
        for item in self._frames_received:
            if item.canid == frameName:
                item.rxCounter=0

    def send_frame_immediately_with_signal(self, signalName, value, frameName=None):
        '''
        Description: Puts a frame in the bus with signal set to provided value.
        This method is useful for sporadic/event signal/frames.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_frame_immediately_with_signal('SignalNameInDbc_1', 5) # For signals up to 32 bits
            hs_can.send_frame_immediately_with_signal('SignalNameInDbc_2', [0x11, 0x22, 0x33, 0x44, 0x55]) # For long signals
        '''
        if self.database == None:
            print 'CAN send_frame_immediately_with_signal method can only be called if a database has been loaded'
            sys.exit()
        frame = self.write_signal_to_frame(signalName, value, frameName)
        if frame != None:
            self.write_frame(frame.canid, frame.dlc, frame.message)

    def save_logfiles(self):
        '''
        Description: Saves all available log files. The file names are defined in dgn_config.py, ccp_config.py, xcp_config.py

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.dgn.service_0x10(0x01)
            hs_can.save_logfiles()
        '''
        if dgncan_available:
            self.dgn.save_logfile()
        if ccpcan_available:
            self.ccp.save_logfile()
        if xcpcan_available:
            self.xcp.save_logfile()

    def read_signal_in_frame(self, offset, length, message, littleEndianStart):
        '''
        Description: Reads signal value in a given message.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            value = dbc.read_signal_in_frame(16, 8, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], True)
        '''
        fr_val = 0L  # Long int

        if littleEndianStart == False:  # Big Endian offset Start
            # Calculate Bit shifting
            pos_cnt = 65  # Count something while the index is not reached
            desp = 0
            for i in FR_BIT_MAP:
                pos_cnt += 1
                if i == offset:
                    pos_cnt = 1
                if pos_cnt == length:
                    desp = -1  # Start bits to shift count
                desp += 1

            for byte in message:
                fr_val = (fr_val << 8) + byte  # single var collect
            signalVal = fr_val >> (desp % 64)
            signalVal &= (2 ** length) - 1
            return signalVal

        else:  # Little Endian offset Start
            for byte in reversed(message):
                fr_val = (fr_val << 8) + byte  # single var collect
            signalVal = fr_val >> int(offset)
            signalVal &= (2 ** length) - 1
            return signalVal

    def find_frame_id(self, frameName):
        '''
        Description: Finds ID of frame frameName in the DBC loaded, and returns the ID and DLC

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            frame_id = dbc.find_frame_id('ABS_PT_C')
        '''
        for i in self.database.hTableOfFrames:
            frameList = self.database.hTableOfFrames[i]
            if frameName == frameList.name:
                return int(frameList.canid), int(frameList.dlc)
        return None, None

    def write_signal_to_frame(self, signalName, signalValue, frameName=None):
        '''
        Description: Prepares the frame containing signal=signalName, by updating signalName=signalValue and keeping
        the rest of the signals unmodified. Returns an object of class FrameToTx.

        Note: Useful when there are two different CAN frames with a signal with the same name. It allows to specify
        exactly the frame to be used.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f_tx = dbc.write_signal_to_frame('PRDoorLatchStatus', 2)
            # If for example 'PRDoorRequest' exists in frames 'BP_Frame_01' and 'BP_Frame_02', it's possible
            # to specify the frame we want to use
            f_tx = dbc.write_signal_to_frame('PRDoorRequest', 1, 'BP_Frame_01')
        '''
        frame_signalName = Frame()
        signal_signalName = Signal()
        frame_to_tx = FrameToTx()
        if frameName == None:
            frame_signalName, signal_signalName = self.look_for_frame_and_signal(signalName)
        else:
            frame_signalName, signal_signalName = self.look_for_signal_in_frame(signalName, frameName)

        if frame_signalName != None:
            frame_to_tx.canid, frame_to_tx.dlc, frame_to_tx.message, message_mask = self._prepare_signal_to_tx(signal_signalName, frame_signalName, signalValue)
            # Add the signal to frames storage
            if frame_to_tx.canid in self.framesStore.keys():
                i = 0
                for byteVal in frame_to_tx.message:
                    self.framesStore[frame_to_tx.canid].message[i] &= ~message_mask[i] # clean the bytes to write
                    self.framesStore[frame_to_tx.canid].message[i] |= byteVal
                    i = i + 1
                frame_to_tx = self.framesStore[frame_to_tx.canid]
            else:
                self.framesStore[frame_to_tx.canid] = frame_to_tx
        else:
            frame_to_tx = None
            print signalName + ' not found in database file'

        return frame_to_tx

    def look_for_frame_and_signal(self, signalName, frameName=None):
        '''
        Description: Finds the frame containing signal=signalName, and returns the frame (object of class Frame) and the signalName
        the rest of the signals unmodified.
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal an object of class Signal.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_frame_and_signal('PRDoorLatchStatus')
        '''

        if frameName != None:
            localslistOfSignals = self.database.hTableOfSignals[frameName];
            for signal_i in localslistOfSignals:
                if signal_i.signalName == signalName:
                    frame_found = self.database.hTableOfFrames[frameName]
                    return (frame_found, signal_i)

        else:
            for frame_i in self.database.hTableOfSignals:
                localslistOfSignals = self.database.hTableOfSignals.get(frame_i);
                for signal_i in localslistOfSignals:
                    if signal_i.signalName == signalName:
                        frame_found = self.database.hTableOfFrames[frame_i]
                        return (frame_found, signal_i)

        return (None, None)

    def look_for_frame_and_signal_group(self, signal_group_name):
        """
        Finds the frame containing signal_group=signal_group_name.

        Arguments:
            signal_group_name (str)

        Returns:
            found _Frame and _Signal objects

        Example:
            >>> mid1 = com.open_can_channel(1, 500000)
            >>> mid1.load_ecu_extract('ECUextract.arxml', 'Mid1CAN')
            >>> f,sg = can1.look_for_frame_and_signal_group('igBrkTq')

        """
        try:
            signal_groups = self.database.signal_groups
        except AttributeError:
            print 'Error: signal group {} not found. Database does not have a table of signal groups'\
                  .format(signal_group_name)
            return None, None

        signal_group = signal_groups.get(signal_group_name)
        if signal_group:
            signal_name = signal_group.signal_instances[0]
            f, s = self.look_for_frame_and_signal(signal_name)

            return f, signal_group

        else:
            print 'Error: signal group {} not found'.format(signal_group_name)
            return None, None

    def find_period_frame(self, frame):
        return int(self.database.hTableOfFrames[frame].cycleTime)

    def _prepare_signal_to_tx(self, signal_signalName, frame_signalName, signalvalue):
        '''
        Description: Looks for signal=signal_signalName in frame=frame_signalName and updates its value with signalvalue
        Parameter 'signal_signalName' is an object of class Signal
        Parameter 'frame_signalName' is an object of class Frame
        Parameter 'signalvalue' is an integer

        Returns (frame_id, dlc, message, message_mask)
        '''
        def littleEndian(signal_signalName, signalvalue):
            def create_message(value, offset):
                message = 8*[0]
                fr_val = value << offset
                for i in range(8):
                    message[i] = fr_val
                    message[i] &= 0xff
                    fr_val = fr_val >> 8
                return message

            offset = int(signal_signalName.offset)
            length = int(signal_signalName.signalLength)

            if isinstance(signalvalue,list):
                fr_val = 0L
                for item in signalvalue:
                    fr_val = fr_val << 8
                    fr_val += item
                signalvalue = fr_val

            signalvalue &= (2**length) - 1
            maskvalue = (2**length) - 1

            message = create_message(signalvalue, offset)
            message_mask = create_message(maskvalue, offset)

            return(int(frame_signalName.canid), int(frame_signalName.dlc), message, message_mask)

        def bigEndian(signal_signalName, signalvalue):
            # Calculate Bit shifting
            def create_message(value, offset):
                message = 8*[0]
                fr_val = value << offset
                for i in range(8):
                    message[i] = fr_val
                    message[i] &= 0xff
                    fr_val = fr_val >> 8
                return list(reversed(message))

            if isinstance(signalvalue, list):
                fr_val = 0L
                for item in signalvalue:
                    fr_val = fr_val << 8
                    fr_val += item
                signalvalue = fr_val

            pos_cnt = 65 # Count something while the index is not reached
            desp = 0
            offset = int(signal_signalName.offset)
            length = int(signal_signalName.signalLength)
            # Calculate the bit shifting
            for i in FR_BIT_MAP:
                pos_cnt += 1
                if i == offset:
                    pos_cnt = 1
                if pos_cnt == length:
                    desp = -1
                desp += 1

            signalvalue &= (2**length) - 1
            maskvalue = (2**length) - 1

            message = create_message(signalvalue, desp)
            message_mask = create_message(maskvalue, desp)
            return(int(frame_signalName.canid), int(frame_signalName.dlc), message, message_mask)

        #############

        if signal_signalName.littleEndianStart == True:
            return littleEndian(signal_signalName, signalvalue)
        else:
            return bigEndian(signal_signalName, signalvalue)

    def look_for_signal_in_frame(self, signalName, frameName):
        '''
        Description: Finds a specific signal inside a specific frame and returns both objects
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal an object of class Signal.
        If signalName does not exist inside frameName, returns (None, None)

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_signal_in_frame('PRDoorLatchStatus', 'BO_Frame_A1')
        '''
        frame_found = Frame()
        signal_found = Signal()
        if frameName in self.database.hTableOfFrames:
            frame_found = self.database.hTableOfFrames.get(frameName)
            localslistOfSignals = self.database.hTableOfSignals.get(frameName)
            for signal_i in localslistOfSignals:
                if signal_i.signalName == signalName:
                    signal_found = signal_i
                    return (frame_found, signal_found)
        return (None, None)

    def find_frame_name(self, frame_id):
        """
        Finds the frame name corresponding to the given CAN ID.

        Arguments:
            frame_id (int): CAN ID of the frame

        Returns:
            frame_name (str)
        """
        for frame_name, frame in self.database.hTableOfFrames.iteritems():
            if frame.canid == frame_id:
                return frame_name
