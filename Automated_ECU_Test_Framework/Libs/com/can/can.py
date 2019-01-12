"""
====================================================================
CAN library for working with frames/signals, diagnostics and CCP/XCP
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import threading
from collections import deque
from time import clock
from data import ECUextract
from data import DBC
from dgn import dgncan_available
from .ccp_cfg import ccpcan_available
from .xcp_cfg import xcpcan_available
if dgncan_available:
    from dgn import *
if ccpcan_available:
    from .ccp import *
if xcpcan_available:
    from .xcp import *


__author__ = 'Miguel Periago'
__version__ = '1.4.0'
__email__ = 'mperiago@lear.com'


"""
CHANGE LOG
==========
1.4.0 PEP8 rework
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
      Methods set_signal and send_frame_immediately_with_signal allows optional param to specify frame name 
      of the signal
      Thread _txrx_thread set as daemon
1.1.0 Using dgn.py instead of iso14229.py for diagnostics
1.0.0 Inital version
"""


CAN_TICK_TIME = 5  # ms
CAN_TICK_TIME_SECONDS = float(CAN_TICK_TIME)/1000

DEQUE_SIZE = 100


class _CanFrameSch:
    def __init__(self):
        self.canid = 0
        self.cycleTime = 0
        self.timer = 0
        self.name = 'void'
        self.dlc = 8
        self.message = 8 * [0]
        self.integrityUpdate = False


class _CanFrameRcv:
    def __init__(self):
        self.canid = 0
        self.name = 'void'
        self.dlc = 8
        self.time = 5 * [0]
        self.message = 5 * [8*[0]]
        self.rxCounter = 1
        self.updateFlag = False
        self.plotBuffer = []


class FrameToTx:
    def __init__(self):
        self.canid = ''
        self.dlc = 0
        self.message = 8 * [0]


FR_BIT_MAP = []
for idx in range(1, 64):
    start_bit = (8 * idx) - 1
    bit_list = []
    for b in range(0, 8):
        bit_list.append(start_bit)
        start_bit -= 1
    FR_BIT_MAP = FR_BIT_MAP + bit_list


class CAN:
    """
    Class for managing CAN frames in a bus. Allows to work with DBC files, diagnostics, and CCP/XCP.
    This class is used by COM class in com.py, so you'll see all examples below with the real usage
    in a Python script.
    """

    def __init__(self, index):
        """
        Description: Constructor.
        Parameter 'index' is the channel index used for tx/rx CAN frames. The channel index available.
        are listed when creating a COM object.
        """
        self.index = index
        self.database = None
        # Init some vars
        self._frames_to_send = []
        self._frames_received = []
        self._rx_frames_deque = {}  # can_id: [CanFrameRcv0, CanFrameRcv1...]
        self._txrx_thread = None
        self._txrx_thread_active = False
        self._tx_active = False
        self._rx_deque_lock = None
        self._set_signal_allowed = True
        self.plot_active = False
        self.plot_buffer = []
        self.plot_start_time = 0
        self.plot_stop_time = 0
        self.frames_store = {}

        # Init DGN
        if dgncan_available:
            self._init_dgn()

        # Init CCP
        if ccpcan_available:
            self._init_ccp()

        # Init XCP
        if xcpcan_available:
            self._init_xcp()

    def start_frame_reception(self):
        """
        Description: Launches the TX frames scheduler section in _main_task_tx_rx thread.
        This will also enable the RX section.
        """
        if not self._txrx_thread_active:
            self._txrx_thread_active = True
            self._txrx_thread = threading.Thread(target=self._main_task_tx_rx)
            self._rx_deque_lock = threading.Lock()
            self._txrx_thread.daemon = True
            self._txrx_thread.start()

    def stop_frame_reception(self):
        """
        Description: Stops the TX frames scheduler section in _main_task_tx_rx thread.
        This will also disable the RX section.
        """
        self._txrx_thread_active = False
        self._txrx_thread.join()

    def _main_task_tx_rx(self):
        """
        Description: Sends and receive frames on cycle timer expiration.
        """
        start_time = clock()
        while self._txrx_thread_active:
            elapsed_time = clock() - start_time
            if elapsed_time >= CAN_TICK_TIME_SECONDS:
                start_time = clock()
                # Send
                if self._tx_active:
                    for item in self._frames_to_send:
                        item.timer -= CAN_TICK_TIME
                        if item.timer <= 0:
                            item.timer = item.cycleTime
                            if item.integrityUpdate:
                                self._set_signal_allowed = False
                                self._apply_integrity(item)
                                self._set_signal_allowed = True
                            self.write_frame(item.canid, item.dlc, item.message)

            # Receive: do it for each tick time
            fr = self.read_frame()
            if fr:
                found = False
                for item in self._frames_received:
                    if fr[0] == item.canid:
                        found = True
                        item.time.pop()
                        item.time.appendleft(fr[3])
                        item.message.pop()
                        item.message.appendleft(fr[4])  # New message added
                        item.rxCounter += 1
                        item.updateFlag = True
                        item.dlc = fr[1]
                        if self.plot_active:
                            if item.message[0] != item.message[1] or not item.plotBuffer:
                                # Check for a different message or empty list
                                plot_point = {item.time[0]: item.message[0]}
                                item.plotBuffer.append(plot_point)
                        break

                if found:
                    # Store frame in FIFO/LIFO deque
                    rx_frame = _CanFrameRcv()
                    (rx_frame.canid, rx_frame.dlc, flags, rx_frame.time, rx_frame.message) = fr

                    with self._rx_deque_lock:  # acquire/release
                        rx_deque = self._rx_frames_deque[rx_frame.canid]
                        rx_deque.append(rx_frame)

                else:
                    self._add_frame_to_rcv(fr)

    def get_plot_signal_frame(self, signal_name, frame_name=None):
        """
        Description: get the needed points for drawing a plot using Plot class
        Parameter signal_name: Signal name to be plot.
        Parameter file_name: [optional] Name of the plot file created. If omitted the signal name is used.
        Parameter frame_name: [optional] frame name where the signal is found.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
            time.sleep(2)
            v_can.stop_plot_record()
            signal_info = can.get_plot_signal_frame('signal_3', 'Frame')
        """
        if not self.database:
            print 'ERROR: CAN get_plot_signal_frame method can only be called if a database has been loaded'
            sys.exit()
        frame, signal = self.look_for_frame_and_signal(signal_name, frame_name)
        if not frame:
            return 0  # Frame not in database
        for item in self._frames_received:
            if item.canid == int(frame.canid):
                return item.plotBuffer, signal, self.database, (self.plot_start_time, self.plot_stop_time)

        return 0

    def start_plot_record(self):
        """
        Description: Start saving data to draw a plot of a signal from the Rx Buffer.
        Note: This will clear all the previous data stored.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
        """
        # Clean the buffer
        self.plot_active = False
        self.plot_buffer = []
        # Start saving the frames
        self.plot_active = True
        self.plot_start_time = time.time()

    def stop_plot_record(self):
        """
        Description: Stop saving data to draw a plot of a signal from the Rx Buffer.
        Example:
            com = COM('VECTOR')
            v_can = com.open_can_channel(1, 500000)
            v_can.start_plot_record()
            time.sleep(2)
            v_can.stop_plot_record()
        """
        self.plot_active = False
        self.plot_stop_time = time.time()

    def _apply_integrity(self, can_frame):
        """
        Description: Allows to apply integrity update to a CAN frame before sending it.
        For example, increase a signal of AliveCounter, or update a signal of Checksum.
        Parameter can_frame is an object of type _CanFrameSch

        Note: The implementation of this method depends on each project requirements.

        Example:
        # Apply integrity only to frames that really need it, in this case ABS_PT_C
        if can_frame.name == 'ABS_PT_C':

            # update alive counter
            if(self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT') == 15):
                self._set_signal_to_be_sent('ABSAliveCounter_HS2_PT', 0)
            else:
                self._set_signal_to_be_sent('ABSAliveCounter_HS2_PT',
                self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT') + 1)

            # calculate checksum and update signal ABSChecksum_PT
            ABSPwrTrnTorqReq_sf = self._get_signal_to_be_sent('ABSPwrTrnTorqReq_HS2_PT')
            BrakePressureQF_sf = self._get_signal_to_be_sent('BrakePressureQF_HS2_PT')
            ABSAliveCounter_sf = self._get_signal_to_be_sent('ABSAliveCounter_HS2_PT')
            VehicleSpeedQF_sf = self._get_signal_to_be_sent('VehicleSpeedQF_HS2_PT')
            checksum = ABSPwrTrnTorqReq_sf + BrakePressureQF_sf + ABSAliveCounter_sf + VehicleSpeedQF_sf
            self._set_signal_to_be_sent('ABSChecksum_PT', checksum)
        """
        pass

    def _set_signal_to_be_sent(self, signal_name, value, frame_name=None):
        """
        Description:  Once a frame has been set to be sent periodically and it contains signal "signal_name",
        this method sets value of signal "signal_name" just before the next time the periodic frame is sent.

        Use this method inside _apply_integrity method to write the contents of signals that are going to be sent,
        for example in the case you need to write an alive counter or a checksum.
        """
        if not self.database:
            print 'ERROR: CAN set_signal method can only be called if a database has been loaded'
            sys.exit()
        result = True
        frame = self.write_signal_to_frame(signal_name, value, frame_name)
        if frame:
            for item in self._frames_to_send:  # Checking if frame is already scheduled
                if frame.canid == item.canid:
                    item.message = frame.message
                    break
        else:
            result = False

        return result

    def _get_signal_to_be_sent(self, signal_name):
        """
        Description: Once a frame has been set to be sent periodically and it contains signal "signal_name",
        this method returns the value of signal "signal_name" that will be sent next time the periodic frame is sent.

        Use this method inside _apply_integrity method to know the contents of signals that are going to be sent,
        and modify them (for example in the case of an alive counter) or read them (for example to
        calculate a checksum).
        """
        if not self.database:
            print 'ERROR: CAN get_signal method can only be called if a database has been loaded.'
            sys.exit()
        temp_frame_name, temp_signal_name = self.look_for_frame_and_signal(signal_name)
        if temp_frame_name:
            for item in self._frames_to_send:
                if item.canid == int(temp_frame_name.canid):
                    return self.read_signal_in_frame(int(temp_signal_name.offset),
                                                     int(temp_signal_name.signalLength),
                                                     item.message,
                                                     temp_signal_name.littleEndianStart)

        return 0

    def _add_frame_to_rcv(self, frame):
        """
        Description: Creates a new object in the main received frames buffer.
        """
        temp_frame = _CanFrameRcv()
        temp_frame.time[0] = frame[3]
        temp_frame.time = deque(temp_frame.time)
        temp_frame.canid = frame[0]
        temp_frame.message[0] = frame[4]
        temp_frame.message = deque(temp_frame.message)
        temp_frame.updateFlag = True
        temp_frame.dlc = frame[1]
        self._frames_received.append(temp_frame)

        # Initialize received frames deque
        temp_frame2 = _CanFrameRcv()
        (temp_frame2.canid, temp_frame2.dlc, flags, temp_frame2.time, temp_frame2.message) = frame
        self._rx_frames_deque[temp_frame2.canid] = deque(maxlen=DEQUE_SIZE)
        self._rx_frames_deque[temp_frame2.canid].append(temp_frame2)

    def _init_dgn(self):
        """
        Description: Prepares diagnostics in this CAN channel.
        """
        self.dgn = DGN()
        self.dgn.iso.net.read_dgn_frame = self.get_frame
        self.dgn.iso.net.write_dgn_frame = self.write_frame

    def _init_ccp(self):
        """
        Description: Prepares CCP in this CAN channel.
        """
        self.ccp = CCP()
        self.ccp.read_ccp_frame = self.get_frame
        self.ccp.write_ccp_frame = self.write_frame

    def _init_xcp(self):
        """
        Description: Prepares XCP in this CAN channel.
        """
        self.xcp = XCP()
        self.xcp.read_xcp_frame = self.get_frame
        self.xcp.write_xcp_frame = self.write_frame

    @staticmethod
    def read_can_frame(index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        Parameter 'index' is the CAN channel index from where the frame shall be read.
        """
        return index

    def read_frame(self):
        """
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
        """
        return self.read_can_frame(self.index)

    def write_can_frame(self, index, canid, dlc, data):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        Parameter 'index' is the CAN channel index where the frame shall be sent.
        Parameter 'canid' is the frame ID.
        Parameter 'dlc' is the data length code.
        Parameter 'data' is a list with the data bytes.
        """
        pass

    def write_frame(self, canid, dlc, data):
        """
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
        """
        self.write_can_frame(self.index, canid, dlc, data)

    def load_dbc(self, dbc_file):
        """
        Description: Loads DBC file into several structs.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
        """
        self.database = DBC(dbc_file)

    def load_ecu_extract(self, arxml_file, cluster_name):
        """
        Description: Loads AUTOSAR ECU Extract file into several structs.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, 500000)
            hs_can.load_ecu_extract('VCU1SystemExtract.arxml', 'Rear1CAN)
        """
        ecu = ECUextract(arxml_file)
        self.database = ecu.clusters_dict.get(cluster_name)
        if self.database is None:
            print "ERROR: Selected cluster not present in ECU Extract"
            sys.exit()

    def send_cyclic_frame(self, frame_name, period=0, integrity_update=False):
        """
        Description: Adds a frame to the schedule buffer for periodic transmission.

        Note: This method is available only if a database has been called previously.

        Note: Parameter "period" is optional. If omitted, the default period of the frame specified
        in the DBC will be used.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
        """
        if not self.database:
            print 'ERROR: CAN send_cyclic_frame method can only be called if a database has been loaded'
            sys.exit()
        temp_frame = _CanFrameSch()
        temp_frame.canid, temp_frame.dlc = self.find_frame_id(frame_name)
        if not temp_frame.canid:
            print 'WARNING: Frame {} not found in dbc'.format(frame_name)
            return
        if period < CAN_TICK_TIME:
            period = self.find_period_frame(frame_name)
            if period == 0:
                print 'WARNING: The cycle time for {} must be {} ms or greater'.format(frame_name, str(CAN_TICK_TIME))
                return
        temp_frame.cycleTime = period
        temp_frame.timer = period
        temp_frame.name = frame_name
        temp_frame.message = temp_frame.dlc * [0]
        temp_frame.integrityUpdate = integrity_update
        frame_scheduled = False
        for item in self._frames_to_send:
            if item.canid == temp_frame.canid:
                frame_scheduled = True
                break
        if not frame_scheduled:
            self._frames_to_send.append(temp_frame)
        self._tx_active = True

    def stop_cyclic_frame(self, frame_name):
        """
        Description: Removes frame from scheduling buffer.

        Note: This method is available only if a database has been called previously.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
            hs_can.stop_cyclic_frame('FrameNameInDbc')
        """
        if not self.database:
            print 'ERROR: CAN stop_cyclic_frame method can only be called if a database has been loaded'
            sys.exit()
        if frame_name == 'None':
            return
        found = False
        frame_id, frame_dlc = self.find_frame_id(frame_name)
        if not frame_id:
            return
        index = 0
        for item in self._frames_to_send:
            if frame_id == item.canid:
                found = True
                break
            index += 1
        if found:
            del self._frames_to_send[index]

    def stop_tx_frames(self):
        """
        Description: Stops the frame sending scheduler section in Tx/Rx thread.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.send_cyclic_frame('FrameNameInDbc', 100) # 100 ms
            hs_can.stop_tx_frames()
        """
        if not self.database:
            print 'ERROR: CAN stop_tx_frames method can only be called if a database has been loaded'
            sys.exit()
        self._tx_active = False

    def set_signal(self, signal_name, value, frame_name=None):
        """
        Description: Sets value in signal for the scheduled frames. If the frame is not already scheduled,
        nothing is done.
        It allows to write signals of any length, up to 32 bits in numeric way, or more than 32 bits in array way.
        See example below.
        Returns False in case the signal is not present in the dbc.

        Note: If you need to send this signal/frame immediately because it's event/sporadic, see
        method send_frame_immediately_with_signal.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            hs_can.set_signal('SignalNameInDbc_1', [0x11, 0x22, 0x33, 0x44, 0x55]) # for a signal of several bytes long
            hs_can.set_signal('SignalNameInDbc_2', 5) # for a signal up to 32 bits
        """
        while not self._set_signal_allowed:
            pass
        if not self.database:
            print 'ERROR: CAN set_signal method can only be called if a database has been loaded'
            sys.exit()
        result = True
        temp_frame = self.write_signal_to_frame(signal_name, value, frame_name)
        if temp_frame:
            for item in self._frames_to_send:  # Checking if frame is already scheduled
                if temp_frame.canid == item.canid:
                    item.message = temp_frame.message
                    break
        else:
            result = False

        return result

    def get_signal(self, signal_name, frame_name=None):
        """
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
        """
        if not self.database:
            print 'ERROR: CAN get_signal method can only be called if a database has been loaded'
            sys.exit()
        temp_frame_name, temp_signal_name = self.look_for_frame_and_signal(signal_name, frame_name)

        if temp_frame_name:
            for item in self._frames_received:
                if item.canid == int(temp_frame_name.canid):
                    return self.read_signal_in_frame(int(temp_signal_name.offset),
                                                     int(temp_signal_name.signalLength),
                                                     item.message[0],
                                                     temp_signal_name.littleEndianStart)

        return 'void'

    def get_cycle_time(self, frame_name):
        """
        Description: Returns the cycle time calculated from the 2 last received frames.
        The time is returned in ms.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            value = hs_can.get_cycle_time('SignalNameInDbc_1') # Time in ms
        """
        if not self.database:
            print 'ERROR: CAN get_cycle_time method can only be called if a database has been loaded'
            sys.exit()
        frame_id, frame_dlc = self.find_frame_id(frame_name)
        if not frame_id:
            return 0  # Frame not in database
        for item in self._frames_received:
            if item.canid == frame_id:
                cycle_time = item.time[0] - item.time[1]  # Time in ns
                cycle_time /= 1e6  # Time in ms
                return cycle_time
        return 0  # Frame not received

    def get_frame(self, frame_id):
        """
        Description: Returns frame content from buffer if a fresh frame is available. If a frame is returned,
        the frame is no longer considered as fresh, and new calls to this method will return an empty list [],
        until a new frame arrives.
        Returns [id, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            # if you know the CAN ID of the frame:
            frame_value = hs_can.get_frame(0x1A0)
            # if you know the name of the frame:
            frame_value = hs_can.get_frame(hs_can.find_frame_id('FrameNameInDbc')[0])
        """
        for frame in self._frames_received:
            if frame.canid == frame_id:
                if frame.updateFlag:
                    frame.updateFlag = False
                    return [frame.canid, frame.dlc, frame.time[0], frame.message[0]]
                else:
                    return []
        return []

    def get_frame_from_deque(self, frame_id, pop_left=False):
        """
        Description: Finds the frame in the frames deque buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, timestamp, [B0, B1, B2, B3, B4...]].

        Parameter 'frameName' is a string
        Parameter 'pop_left' is a boolean. It determines whether to perform a
                  pop (LIFO) or pop_left (FIFO) operation.

        Example:
            com = COM('VECTOR')
            can1 = com.open_can_channel(1, 500000)
            brake_control_frame = can1.get_frame_from_deque(125)
        """
        rx_deque = self._rx_frames_deque.get(frame_id)

        if rx_deque is None:
            return None

        with self._rx_deque_lock:    # acquire/release
            try:
                if pop_left:
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
        #     if frame.canid == frame_id:
        #         try:
        #             if pop_left:
        #                 message = frame.message.pop_left()
        #                 timestamp = frame.time.pop_left()
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
        with self._rx_deque_lock:
            for canid, frames_deque in self._rx_frames_deque.iteritems():
                frames_deque.clear()

    def get_rx_frame_counter(self, frame_name):
        """
        Description: Returns the value of the received frames counter. Every frame as a rx counter that is
        increased every time a frame is received. This counter is useful to check the number of messages
        received in a fixed elapsed time.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            count_1 = hs_can.get_rx_frame_counter('FrameNameInDbc')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            count_2 = hs_can.get_rx_frame_counter('FrameNameInDbc')
            print str(count_2 - count_1) + ' frames FrameNameInDbc received during 5 seconds'
        """
        if not self.database:
            print 'ERROR: CAN get_rx_frame_counter method can only be called if a database has been loaded'
            sys.exit()
        frame_id, frame_dlc = self.find_frame_id(frame_name)
        if not frame_id:
            return 0  # Frame not in database
        for item in self._frames_received:
            if item.canid == frame_id:
                return item.rxCounter
        return 0  # Frame not received

    def clear_rx_frame_counter(self, frame_name):
        """
        Description: Clears value of the received frames counter.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            count_1 = hs_can.clear_rx_frame_counter('FrameNameInDbc')
        """
        for item in self._frames_received:
            if item.canid == frame_name:
                item.rxCounter = 0

    def send_frame_immediately_with_signal(self, signal_name, value, frame_name=None):
        """
        Description: Puts a frame in the bus with signal set to provided value.
        This method is useful for sporadic/event signal/frames.

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.load_dbc('PT_HSCAN_MultiCAN_15MY_IP12W38.dbc')
            # For signals up to 32 bits:
            hs_can.send_frame_immediately_with_signal('SignalNameInDbc_1', 5)
            # For long signals:
            hs_can.send_frame_immediately_with_signal('SignalNameInDbc_2', [0x11, 0x22, 0x33, 0x44, 0x55])
        """
        if not self.database:
            print 'ERROR: CAN send_frame_immediately_with_signal method can only be called if a ' \
                  'database has been loaded'
            sys.exit()
        temp_frame = self.write_signal_to_frame(signal_name, value, frame_name)
        if temp_frame:
            self.write_frame(temp_frame.canid, temp_frame.dlc, temp_frame.message)

    def save_logfiles(self):
        """
        Description: Saves all available log files. The file names are defined in dgn_config.py,
        ccp_config.py, xcp_config.py

        Example:
            com = COM('VECTOR')
            hs_can = com.open_can_channel(1, XL_CAN_BITRATE_500K)
            hs_can.dgn.service_0x10(0x01)
            hs_can.save_logfiles()
        """
        if dgncan_available:
            self.dgn.save_logfile()
        if ccpcan_available:
            self.ccp.save_logfile()
        if xcpcan_available:
            self.xcp.save_logfile()

    @staticmethod
    def read_signal_in_frame(offset, length, message, little_endian_start):
        """
        Description: Reads signal value in a given message.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            value = dbc.read_signal_in_frame(16, 8, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], True)
        """
        fr_val = 0L  # Long int

        if not little_endian_start:  # Big Endian offset Start
            del FR_BIT_MAP[(8*len(message)):]  # Remove unused bytes
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
            signal_val = fr_val >> (desp % 64)
            signal_val &= (2 ** length) - 1
            return signal_val

        else:  # Little Endian offset Start
            for byte in reversed(message):
                fr_val = (fr_val << 8) + byte  # single var collect
            signal_val = fr_val >> int(offset)
            signal_val &= (2 ** length) - 1
            return signal_val

    def find_frame_id(self, frame_name):
        """
        Description: Finds ID of frame frame_name in the DBC loaded, and returns the ID and DLC

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            frame_id = dbc.find_frame_id('ABS_PT_C')
        """
        for i in self.database.hTableOfFrames:
            frame_list = self.database.hTableOfFrames[i]
            if frame_name == frame_list.name:
                return int(frame_list.canid), int(frame_list.dlc)
        return None, None

    def write_signal_to_frame(self, signal_name, signal_value, frame_name=None):
        """
        Description: Prepares the frame containing signal=signal_name, by updating signal_name=signal_value and keeping
        the rest of the signals unmodified. Returns an object of class FrameToTx.

        Note: Useful when there are two different CAN frames with a signal with the same name. It allows to specify
        exactly the frame to be used.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f_tx = dbc.write_signal_to_frame('PRDoorLatchStatus', 2)
            # If for example 'PRDoorRequest' exists in frames 'BP_Frame_01' and 'BP_Frame_02', it's possible
            # to specify the frame we want to use
            f_tx = dbc.write_signal_to_frame('PRDoorRequest', 1, 'BP_Frame_01')
        """
        frame_to_tx = FrameToTx()
        if not frame_name:
            frame_signal_name, signal_signal_name = self.look_for_frame_and_signal(signal_name)
        else:
            frame_signal_name, signal_signal_name = self.look_for_signal_in_frame(signal_name, frame_name)

        if frame_signal_name:
            frame_to_tx.canid, frame_to_tx.dlc, frame_to_tx.message, message_mask = \
                self._prepare_signal_to_tx(signal_signal_name, frame_signal_name, signal_value)
            # Add the signal to frames storage
            if frame_to_tx.canid in self.frames_store.keys():
                i = 0
                for byteVal in frame_to_tx.message:
                    self.frames_store[frame_to_tx.canid].message[i] &= ~message_mask[i]  # clean the bytes to write
                    self.frames_store[frame_to_tx.canid].message[i] |= byteVal
                    i = i + 1
                frame_to_tx = self.frames_store[frame_to_tx.canid]
            else:
                self.frames_store[frame_to_tx.canid] = frame_to_tx
        else:
            frame_to_tx = None
            print 'WARNING: Signal {} not found in database file'.format(signal_name)

        return frame_to_tx

    def look_for_frame_and_signal(self, signal_name, frame_name=None):
        """
        Description: Finds the frame containing signal=signal_name, and returns the frame (object of class Frame)
        and the signal_name the rest of the signals unmodified.
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal an object
        of class Signal.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_frame_and_signal('PRDoorLatchStatus')
        """

        if frame_name is not None:
            local_list_of_signals = self.database.hTableOfSignals[frame_name]
            for signal_i in local_list_of_signals:
                if signal_i.signalName == signal_name:
                    frame_found = self.database.hTableOfFrames[frame_name]
                    return frame_found, signal_i

        else:
            for frame_i in self.database.hTableOfSignals:
                local_list_of_signals = self.database.hTableOfSignals.get(frame_i)
                for signal_i in local_list_of_signals:
                    if signal_i.signalName == signal_name:
                        frame_found = self.database.hTableOfFrames[frame_i]
                        return frame_found, signal_i

        return None, None

    def look_for_frame_and_signal_group(self, signal_group_name):
        """
        Finds the frame containing signal_group=signal_group_name.

        Arguments:
            signal_group_name (str)

        Returns:
            found _Frame and _Signal objects

        Example:
            mid1 = com.open_can_channel(1, 500000)
            mid1.load_ecu_extract('ECUextract.arxml', 'Mid1CAN')
            f,sg = can1.look_for_frame_and_signal_group('igBrkTq')

        """
        try:
            signal_groups = self.database.signal_groups
        except AttributeError:
            print 'ERROR: Signal group {} not found. Database does not have a table of signal groups'\
                  .format(signal_group_name)
            return None, None

        signal_group = signal_groups.get(signal_group_name)
        if signal_group:
            signal_name = signal_group.signal_instances[0]
            f, s = self.look_for_frame_and_signal(signal_name)

            return f, signal_group

        else:
            print 'ERROR: Signal group {} not found'.format(signal_group_name)
            return None, None

    def find_period_frame(self, frame):
        return int(self.database.hTableOfFrames[frame].cycleTime)

    @staticmethod
    def _prepare_signal_to_tx(signal_name, frame_name, signal_value):
        """
        Description: Looks for signal=signal_name in frame=frame_name and updates
        its value with signal_value
        Parameter 'signal_name' is an object of class Signal
        Parameter 'frame_name' is an object of class Frame
        Parameter 'signal_value' is an integer

        Returns (frame_id, dlc, message, message_mask)
        """

        def little_endian(s_name, s_value):
            def create_message(m_value, m_offset, m_dlc):
                temp_message = m_dlc * [0]
                m_val = m_value << m_offset
                for i1 in range(m_dlc):
                    temp_message[i1] = m_val
                    temp_message[i1] &= 0xff
                    m_val = m_val >> 8
                return temp_message

            offset = int(s_name.offset)
            length = int(s_name.signalLength)

            if isinstance(s_value, list):
                fr_val = 0L
                for item in s_value:
                    fr_val = fr_val << 8
                    fr_val += item
                s_value = fr_val

            s_value &= (2 ** length) - 1
            mask_value = (2 ** length) - 1

            message = create_message(s_value, offset, int(frame_name.dlc))
            message_mask = create_message(mask_value, offset, int(frame_name.dlc))

            return int(frame_name.canid), int(frame_name.dlc), message, message_mask

        def big_endian(s_name, s_value):
            # Calculate Bit shifting
            def create_message(m_value, m_offset, m_dlc):
                temp_message = m_dlc * [0]
                m_val = m_value << m_offset
                for i2 in range(m_dlc):
                    temp_message[i2] = m_val
                    temp_message[i2] &= 0xff
                    m_val = m_val >> 8
                return list(reversed(temp_message))

            if isinstance(s_value, list):
                fr_val = 0L
                for item in s_value:
                    fr_val = fr_val << 8
                    fr_val += item
                s_value = fr_val

            pos_cnt = 65  # Count something while the index is not reached
            desp = 0
            offset = int(s_name.offset)
            length = int(s_name.signalLength)
            del FR_BIT_MAP[(8*int(frame_name.dlc)):]  # Remove unused bytes
            # Calculate the bit shifting
            for i in FR_BIT_MAP:
                pos_cnt += 1
                if i == offset:
                    pos_cnt = 1
                if pos_cnt == length:
                    desp = -1
                desp += 1

            s_value &= (2 ** length) - 1
            mask_value = (2 ** length) - 1

            message = create_message(s_value, desp, int(frame_name.dlc))
            message_mask = create_message(mask_value, desp, int(frame_name.dlc))
            return int(frame_name.canid), int(frame_name.dlc), message, message_mask

        #############

        if signal_name.littleEndianStart:
            return little_endian(signal_name, signal_value)
        else:
            return big_endian(signal_name, signal_value)

    def look_for_signal_in_frame(self, signal_name, frame_name):
        """
        Description: Finds a specific signal inside a specific frame and returns both objects
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal
        an object of class Signal.
        If signal_name does not exist inside frame_name, returns (None, None)

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_signal_in_frame('PRDoorLatchStatus', 'BO_Frame_A1')
        """
        if frame_name in self.database.hTableOfFrames:
            frame_found = self.database.hTableOfFrames.get(frame_name)
            local_list_of_signals = self.database.hTableOfSignals.get(frame_name)
            for signal_i in local_list_of_signals:
                if signal_i.signalName == signal_name:
                    signal_found = signal_i
                    return frame_found, signal_found
        return None, None

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
