'''
====================================================================
CAN library for working with frames/signals, diagnostics and CCP/XCP
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = 'Miguel Periago'
__version__ = '1.2.10'
__email__   = 'mperiago@lear.com'

'''
CHANGE LOG
==========
1.2.10 get_plot_signal_frame modified to give all the info needed to plot library.
1.2.9 Plot library call removed. Method to provide the data for plotting created.
1.2.8 Frames integrity improved.
1.2.7 - Added plot feature.
      - Method _frames_to_send buffer protected in case of trying to schedule an already existing frame in the buffer.
1.2.6 Update bit management removed. It should be placed in an upper layer.
1.2.5 Methods set_signal and get_signal improved for update bits management
1.2.4 Method _frames_to_send buffer protected in case of trying to schedule an already existing frame in the buffer
1.2.3 Method send_cyclic_frame has "period" parameter as optional. If omitted, the default period of the frame is used
1.2.2 Channel open message moved to vxlapi.py and kvaserapi.py
1.2.1 Added private method for stopping thread of frame reception. Will be called from com.py
1.2.0 - Added integrity update for several CAN frames
      - Methods set_signal and send_frame_immediately_with_signal allows optional param to specify frame name of the signal
      - Thread txrx_thread set as daemon
1.1.0 Using dgn.py instead of iso14229.py for diagnostics
1.0.0 Inital version
'''

import threading
import os
import time
from collections import deque
from time import clock

from .dbc import *
from ..dgn import *
try:
    from .ccp import *
    ccp_available = True
except ImportError:
    ccp_available = False
try:
    from .xcp import *
    xcp_available = True
except ImportError:
    xcp_available = False


CAN_TICK_TIME = 5 # ms
CAN_TICK_TIME_SECONDS = float(CAN_TICK_TIME)/1000


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
        self.dbc = None
        # Init some vars
        self._frames_to_send = []
        self._frames_received = []
        self._txrx_thread_active = False
        self._tx_active = False
        self._set_signal_allowed = True
        self.plot_active = False

        # Init DGN
        self._init_dgn()

        # Init CCP
        if ccp_available:
            self._init_ccp()

        # Init XCP
        if xcp_available:
            self._init_xcp()


    def _start_frame_reception(self):
        '''
        Description: Launches the TX frames scheduler section in _main_task_tx_rx thread. This will also enable the RX section.
        '''
        if self._txrx_thread_active == False:
            self._txrx_thread_active = True
            self.txrx_thread = threading.Thread(target = self._main_task_tx_rx)
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
                if found == False:
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
        if self.dbc == None:
            print 'CAN get_rx_frame_counter method can only be called if a DBC has been loaded.'
            sys.exit()
        frame, signal = self.dbc.look_for_frame_and_signal(signalName, frameName)
        if frame == None:
            return 0 # Frame not in database
        for item in self._frames_received:
            if item.canid == int(frame.canid):
                return (item.plotBuffer, signal, self.dbc, (self.plot_start_time, self.plot_stop_time)) # signal info to be used with plot class

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
        if self.dbc == None:
            print 'CAN set_signal method can only be called if a DBC has been loaded.'
            sys.exit()
        result = True
        frame = self.dbc.write_signal_to_frame(signalName, value, frameName)
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
        if self.dbc == None:
            print 'CAN get_signal method can only be called if a DBC has been loaded.'
            sys.exit()
        frame_signalName, signal_signalName = self.dbc.look_for_frame_and_signal(signalName)
        found = False
        if frame_signalName != None:
            for item in self._frames_to_send:
                if item.canid == int(frame_signalName.canid): # Check if the frame is present in received buffer
                    found = True
                    return self.dbc.read_signal_in_frame(int(signal_signalName.offset), int(signal_signalName.signalLength), item.message, signal_signalName.littleEndianStart)

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


    def _init_dgn(self):
        '''
        Description: Prepares diagnostics in this CAN channel.
        '''
        self.dgn = DGN()
        self.dgn.iso.net.read_can_frame = self.get_frame
        self.dgn.iso.net.write_can_frame = self.write_frame


    def _init_ccp(self):
        '''
        Description: Prepares CCP in this CAN channel.
        '''
        self.ccp = CCP()
        self.ccp.read_can_frame = self.get_frame
        self.ccp.write_can_frame = self.write_frame


    def _init_xcp(self):
        '''
        Description: Prepares XCP in this CAN channel.
        '''
        self.xcp = XCP()
        self.xcp.read_can_frame = self.get_frame
        self.xcp.write_can_frame = self.write_frame


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
        self.dbc = DBC(dbc_file)


    def send_cyclic_frame(self, frameName, period=0, integrityUpdate=False):
        '''
        Description: Adds a frame to the schedule buffer for periodic transmission.

        Note: This method is available only if load_dbc method has been called previously.

        Note: Parameter "period" is optional. If omitted, the default period of the frame specified
        in the DBC will be used.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
        '''
        if self.dbc == None:
            print 'CAN send_cyclic_frame method can only be called if a DBC has been loaded.'
            sys.exit()
        if frameName == 'None' or period == None:
            return
        if period < CAN_TICK_TIME:
            period = self.dbc.find_period_frame(frameName)
            #print "Default period send for " + frameName + " is "+ str(period) + " ms"
            if period == 0:
                print "The cycle time for " + frameName + " must be " + str(CAN_TICK_TIME) + " ms or greater"
                return
        fr = _CanFrameSch()
        fr.canid, fr.dlc = self.dbc.find_frame_id(frameName)
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

        Note: This method is available only if load_dbc method has been called previously.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
            hs_can.stop_cyclic_frame('FrameNameInDbc')
        '''
        if self.dbc == None:
            print 'CAN stop_cyclic_frame method can only be called if a DBC has been loaded.'
            sys.exit()
        if frameName == 'None':
            return
        found = False
        frId, frDlc = self.dbc.find_frame_id(frameName)
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
        if self.dbc == None:
            print 'CAN stop_tx_frames method can only be called if a DBC has been loaded.'
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
        if self.dbc == None:
            print 'CAN set_signal method can only be called if a DBC has been loaded.'
            sys.exit()
        result = True
        frame = self.dbc.write_signal_to_frame(signalName, value, frameName)
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
        if self.dbc == None:
            print 'CAN get_signal method can only be called if a DBC has been loaded.'
            sys.exit()
        frame_signalName, signal_signalName = self.dbc.look_for_frame_and_signal(signalName, frameName)
        found = False
        if frame_signalName != None:
            for item in self._frames_received:
                if item.canid == int(frame_signalName.canid): # Check if the frame is present in received buffer
                    found = True
                    return self.dbc.read_signal_in_frame(int(signal_signalName.offset), int(signal_signalName.signalLength), item.message[0], signal_signalName.littleEndianStart)

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
        if self.dbc == None:
            print 'CAN get_cycle_time method can only be called if a DBC has been loaded.'
            sys.exit()
        frId, frDlc = self.dbc.find_frame_id(frameName)
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
            frame_value = hs_can.get_frame(hs_can.dbc.find_frame_id('FrameNameInDbc')) # if you know the name of the frame
        '''
        for frame in self._frames_received:
            if frame.canid == frameId:
                if frame.updateFlag == True:
                    frame.updateFlag = False
                    return [frame.canid, frame.dlc, frame.time[0], frame.message[0]]
                else:
                    return []
        return []


    def get_rx_frame_counter(self,frameName):
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
        if self.dbc == None:
            print 'CAN get_rx_frame_counter method can only be called if a DBC has been loaded.'
            sys.exit()
        frId, frDlc = self.dbc.find_frame_id(frameName)
        if frId == None:
            return 0 # Frame not in database
        for item in self._frames_received:
            if item.canid == frId:
                return item.rxCounter
        return 0 # Frame not received


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
        if self.dbc == None:
            print 'CAN send_frame_immediately_with_signal method can only be called if a DBC has been loaded'
            sys.exit()
        frame = self.dbc.write_signal_to_frame(signalName, value, frameName)
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
        self.dgn.save_logfile()
        if ccp_available:
            self.ccp.save_logfile()
        if xcp_available:
            self.xcp.save_logfile()


