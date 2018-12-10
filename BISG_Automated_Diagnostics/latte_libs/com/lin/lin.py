"""
====================================================================
LIN library for working with frames/signals
(C) Copyright 2013 Lear Corporation
====================================================================
"""
from collections import deque
import threading
import time


__author__ = 'Miguel Periago'
__version__ = '1.7.0'
__email__ = 'mperiago@lear.com'

'''
CHANGE LOG
==========
1.7.0 Using database files from <data> folder
1.6.3 get_plot_signal_frame modified to give all the info needed to plot library.
1.6.2 Plot library call removed. Method to provide the data for plotting created.
1.6.1 Added frameName parameter to set_signal method.
1.6.0 [MPeriago] Implemented lin master node behavior.
      [CBlanco] IMPROVES from MQB and BCM added to Official LATTE library:
          Added 'enable_frame_response' method which enables the response of specific LIN message
          Added  _frames_enabled list
          Added 'disable_frame_response' method which disables the response of specific LIN message,e.g when no 
          response for SlaveResp is required
          Added 'report_frame_enabled' method to check if a frame was enabled or disabled
          Added 'get_bus_state' method which returns LIN bus activity state
          Added 'get_bus_slaves' method which returns list of slaves extracted from LDF
          Added 'get_slave_productid_by_name' & 'get_slave_productid_by_nad' methods which return 'supplier_id', 
          'function_id' and 'variant_id' extracted from LDF for a specific slave
          Added 'enable_slave_response' method which enables the response of specific LIN slave
          Added 'disable_slave_response' method which disables the response of specific LIN slave
          Added 'report_slave_supported_frames' method which returns specific slave supported response frames
          Added 'report_frame_info' method which returns frame information name and dlc
          Added 'get_slave_nad' method which returns node address of a specific slave
          Added 'send_sleep' method which sends a lin sleep command in channel
          Added 'get_schedules' method which returns list of schedules supported at channel
          Added 'get_schedule_frames' method which returns list of frames inside a specific schedule
          Added 'get_schedule_delays' method which returns list with delays for each frame inside schedule passed
          Added 'get_schedule_frames_publisher' method which returns list with publishers of frames supported 
          by schedule passed
          Added code line for printing of channel id opened at '__init__' method
          Added '_write_frame_master' method which writes a LIN master frame to channel when simulating master node
          Added 'get_fresh_frames' method which returns first LIN fresh frame
1.5.1 Added plot feature. Methods plot_signal, start_plot_record and stop_plot_record.
1.5.0 New methods set_frames_response and set_checksum_response more powerful and more simple
1.4.2 Rewrite frames in setting/removin faulty checksum, so they are immediately updated
1.4.1 Channel open message moved to vxlapi.py and kvaserapi.py
1.4.0 Added methods set_faulty_checksum_response and remove_faulty_checksum_response
1.3.1 Using switch_on_lin_id and switch_on_lin_id to enable and disable LIN frames
1.3.0 Added several methods for enabling and disabling specific slave modules or frames
1.2.0 - Added private method for stopping thread of frame reception. Will be called from com.py
      - Thread txrx_thread set as daemon
1.1.0 [MPeriago] Added send_lin_wake_up method
1.0.0 Inital version
'''


LIN_RX_COUNTER_MAX = 0xFFFF
LIN_TICK_TIME = 1  # ms
LIN_TICK_TIME_SECONDS = float(LIN_TICK_TIME)/1000


class _LinFrameRcv:
    def __init__(self):
        self.lin_id = 0
        self.name = 'void'
        self.dlc = 8
        self.time = [0]*5
        self.message = [[0]*8]*5
        self.rx_counter = 1
        self.update_flag = False
        self.trace_flag = False
        self.plot_buffer = []


class LIN:
    """
    Class for managing LIN frames in a bus. Allows to work with LDF files.
    This class is used by COM class in com.py, so you'll see all examples below with the real usage
    in a Python script.
    """
    def __init__(self, index, ldf, mode):
        """
        Description: Constructor.
        Parameter 'index' is the channel index used for tx/rx LIN frames. The channel index available
        are listed when creating a COM object.
        Parameter 'ldf' is an object of type LDF (see ldf.py)
        Paramter 'mode' sets the behavior of the bus (MASTER or SLAVE).
        """
        self.index = index
        self.ldf = ldf
        # Init some vars
        self._frames_received = []
        self._frames_enabled = []
        self._frames_faulty_checksum = []
        self.txrx_thread = None
        self._txrx_thread_active = False
        self.linBusActive = False
        self._slaves = self.ldf.report_slaves()
        self.plot_active = False
        self.plot_buffer = []
        self.plot_start_time = 0
        self.plot_stop_time = 0
        self.is_master = False
        self.active_table_index = 0
        self.sch_frame_index = 0
        self._diag_frames = []
        if mode == 'MASTER':
            self.is_master = True
        else:
            self.is_master = False

    def start_frame_reception(self):
        """
        Description: Launches TX/RX thread.
        """
        if not self._txrx_thread_active:
            self._txrx_thread_active = True            
            self.txrx_thread = threading.Thread(target=self._main_task_tx_rx)
            self.txrx_thread.daemon = True
            self.txrx_thread.start()
            self.linBusActive = False

    def stop_frame_reception(self):
        """
        Description: Stops the TX frames scheduler section in _main_task_tx_rx thread.
        This will also disable the RX section.
        """
        self._txrx_thread_active = False
        self.txrx_thread.join()

    def _main_task_tx_rx(self):
        """
        Description: Sends and receive frames on cycle timer expiration.
        """
        start_time = time.clock()        
        time_start = time.time()
        time_elapsed = 0.0
        while self._txrx_thread_active:
            if self.is_master:
                if self.ldf.scheduling_tables[self.active_table_index].ids:  # There is something to be sent
                    elapsed_time = time.clock() - start_time
                    # Send requests to the slaves
                    if elapsed_time >= LIN_TICK_TIME_SECONDS:
                        start_time = time.clock()
                        self.ldf.scheduling_tables[self.active_table_index].counter += LIN_TICK_TIME
                        if self.ldf.scheduling_tables[self.active_table_index].counter >= \
                                self.ldf.scheduling_tables[self.active_table_index].delay[self.sch_frame_index]:
                            self._send_request(self.ldf.scheduling_tables[self.active_table_index].ids[
                                                   self.sch_frame_index])
                            self.ldf.scheduling_tables[self.active_table_index].counter = 0
                            self.sch_frame_index += 1
                            if self.sch_frame_index == len(self.ldf.scheduling_tables[self.active_table_index].ids):
                                self.sch_frame_index = 0                                                                                            
                        
            # Receive
            fr = self._read_frame()
            if fr:
                # store received diagnostics frames if valid NAD (1..7F)
                if fr[0] == 61:
                    if fr[4][0] > 0:
                        self._diag_frames.append(fr)
                if fr[0] == 60:
                    if fr[4][0] > 0:
                        self._diag_frames.append(fr)
                time_start = time.time()
                self.linBusActive = True
                found = False
                for item in self._frames_received:
                    if fr[0] == item.linid:
                        found = True
                        item.time.pop()
                        item.time.appendleft(fr[3])
                        item.message.pop()
                        item.message.appendleft(fr[4])  # New message added
                        item.rxCounter = ((item.rxCounter + 1) % LIN_RX_COUNTER_MAX)
                        item.dlc = fr[1]
                        item.updateFlag = True
                        item.traceFlag = True
                        if self.plot_active:
                            # Check for a different message or empty list:
                            if item.message[0] != item.message[1] or not item.plotBuffer:
                                plot_point = {item.time[0]: item.message[0]}
                                item.plotBuffer.append(plot_point)
                        break
                if not found:
                    self._add_frame_to_rcv(fr)
            else:
                time_elapsed = time.time() - time_start
            if time_elapsed > 1.0:
                self.linBusActive = False

    def get_plot_signal_frame(self, signal_name):
        """
        Description: Get the data to create a plot using plot library.
        Parameter signal_name: Signal name to be plot.
        Parameter frame_name: [optional] frame name where the signal is found.
        Example:
            com = COM('VECTOR')
            lin = com.open_lin_channel(1, ''file.ldf)            
            lin.start_plot_record() 
            lin.stop_plot_record()
            lin.plot_signal('Signal_1')       
        """
        class Signal:
            def __init__(self):
                self.offset = 0
                self.signal_length = 0
                self.little_endian_start = False
                self.signal_name = ''
            
        signal = Signal()
        signal.signalName = signal_name
        linid, signal.offset, signal.signal_length = self.ldf.find_signal_info(signal_name)
        if linid:
            for item in self._frames_received:
                if item.linid == linid:
                    # signal info to be used with plot class
                    return item.plotBuffer, signal, self.ldf, (self.plot_start_time, self.plot_stop_time)
        return 0  # No data found for this signal
        
    def start_plot_record(self):
        """
        Description: Start saving data to draw a plot of a signal from the Rx Buffer.
        Note: This will clear all the previous data stored.
        Example:
            com = COM('VECTOR')
            lin = com.open_can_channel(1, 'file.ldf')            
            lin.start_plot_record()
        """
        # Clean the buffer
        self.plot_buffer = []
        # Start saving the frames        
        self.plot_active = True
        self.plot_start_time = time.time()       
        
    def stop_plot_record(self):
        """
        Description: Stop saving data to draw a plot of a signal from the Rx Buffer.        
        Example:
            com = COM('VECTOR')
            lin = com.open_can_channel(1, 'file.ldf')            
            lin.start_plot_record()
            time.sleep(2)
            lin.stop_plot_record()
        """        
        self.plot_active = False
        self.plot_stop_time = time.time()

    def _add_frame_to_rcv(self, fr):
        """
        Description: Creates a new object in the main received frames buffer.
        """
        fr_rcv = _LinFrameRcv()
        fr_rcv.time[0] = fr[3]
        fr_rcv.time = deque(fr_rcv.time)
        fr_rcv.lin_id = fr[0]
        fr_rcv.message[0] = fr[4]
        fr_rcv.message = deque(fr_rcv.message)
        fr_rcv.update_flag = True
        fr_rcv.trace_flag = True
        fr_rcv.dlc = fr[1]
        self._frames_received.append(fr_rcv)

    @staticmethod
    def read_lin_frame(index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        return index

    def write_lin_frame(self, index, lin_id, dlc, data, faulty_checksum):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def write_lin_frame_master(self, index, lin_id, dlc, data, faulty_checksum):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def send_lin_wake_up(self, index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def send_lin_request(self, index, lin_id):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def send_lin_sleep(self, index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def switch_off_lin_id(self, index, item):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def switch_on_lin_id(self, index, item):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        pass

    def _read_frame(self):
        """
        Description: Reads LIN frame from channel.
        """
        return self.read_lin_frame(self.index)

    def _write_frame(self, lin_id, dlc, data, faulty_checksum=False):
        """
        Description: Writes LIN frame to channel.
        """
        self.write_lin_frame(self.index, lin_id, dlc, data, faulty_checksum)

    def _write_frame_master(self, lin_id, dlc, data, faulty_checksum=False):
        """
        Description: Writes LIN master frame to channel.
        """
        self.write_lin_frame_master(self.index, lin_id, dlc, data, faulty_checksum)

    def _find_frames_modules(self, modules):
        """
        Description: Returns a list of frameids sent by a module(s).
        """
        if type(modules) not in [tuple, list]:
            modules = [modules]
        
        return [frame.linid for frame in self.ldf.frames if frame.module in modules]

    def send_wake_up(self):
        """
        Description: Sends a lin wake up in channel.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.send_wake_up()
        """
        return self.send_lin_wake_up(self.index)
    
    def _send_request(self, lin_id):
        """
        Description: Sends a lin master request in channel.
        
        """
        self.send_lin_request(self.index, lin_id)
        
    def send_sleep(self):
        """
        Description: Sends a lin sleep command in channel.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.send_sleep()
        """
        return self.send_lin_sleep(self.index)

    def disable_all_modules_response(self):
        """
        Description: Disables the response of all the LIN slaves.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.disable_all_modules_response()
        """
        for item in self.ldf.slave_frames:
            time.sleep(0.01)
            self.switch_off_lin_id(self.index, item[0])

    def enable_all_modules_response(self):
        """
        Description: Enables the response of all the LIN slaves.

        Note: All slaves are enabled by default. Use this method to enable all slaves after disabling one or several.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.enable_all_modules_response()
        """
        for item in self.ldf.slave_frames:
            self.switch_on_lin_id(self.index, item[0])

    def disable_slave_response(self, slave):
        """
        Description: Disables the response of specific LIN slave.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.disable_slave_response('NAME_OF_SLAVE')
        """
        supported_frames = self.ldf.report_slave_frames(slave)
        for item in self.ldf.slave_frames:
            for frms in supported_frames:
                if frms == item[0]:
                    self.switch_off_lin_id(self.index, item[0])

    def enable_slave_response(self, slave):
        """
        Description: Enables the response of specific LIN slave.
        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.enable_slave_response('NAME_OF_SLAVE')
        """
        supported_frames = self.ldf.report_slave_frames(slave)
        for item in self.ldf.slave_frames:
            for frms in supported_frames:
                if frms == item[0]:
                    self.switch_on_lin_id(self.index, item[0])

    def report_slave_supported_frames(self, slave):
        """
        Description: returns specific slave supported response frames
        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.report_slave_supported_frames('NAME_OF_SLAVE')
        """
        return self.ldf.report_slave_frames(slave)

    def disable_frame_response(self, lin_id):
        """
        Description: Disables the response of specific LIN message.
        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.disable_frame_response(0x3D)
        """
        self.switch_off_lin_id(self.index, lin_id)
        if lin_id in self._frames_enabled:
            self._frames_enabled.remove(lin_id)

    def enable_frame_response(self, lin_id):
        """
        Description: Enables the response of specific LIN message.
        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            lin1.enable_frame_response(0x3D)
        """
        self.switch_on_lin_id(self.index, lin_id)
        if lin_id not in self._frames_enabled:
            self._frames_enabled.append(lin_id)

    def report_frame_enabled(self, lin_id):
        """
        Description: Returns 1 if frame id was enabled
        """
        if lin_id in self._frames_enabled:
            return 1
        return 0

    def set_frames_response(self, element_list, enable):
        """
        Description: Enables/disables the response of a list of frames or modules.
        These frames can be the name of the frame, the frame identifier or a module name.
        It's also possible to pass one item, not a list. So param 'element_list' can be:
            - A module name, frame name or frame id.
            - A list of a combination of the above.
        Parameter 'enable' must be True or False.

        Note: All slaves are enabled by default. Use this method to disable one or several, and then enabling them back.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            # You can use LIN id's to list the frames to enable
            lin1.set_frames_response([0x12, 0x15, 0x21, 0x22], True)
            # You can use LIN frame names to list the frames to disable
            lin1.set_frames_response(['SWS_LIN1_C', 'SWM_L1_P00'], False)
            # You can use one element instead of a list
            lin1.set_frames_response(0x12, True)
            lin1.set_frames_response('SWS_LIN1_C', False)
            # All frames of a module can also be used
            lin1.set_frames_response('WMM', True)
        """
        if type(element_list) not in [tuple, list]: 
            element_list = [element_list]

        # Expand (possible) modules to frames
        element_list += self._find_frames_modules(element_list)

        # Modify each frame
        for item in element_list:
            linid = None
            if type(item) == str:
                linid = self.ldf.get_lin_id_from_frame_name(item)
            elif type(item) in [int, long]:
                linid = item
          
            if linid:
                if enable:
                    self.switch_on_lin_id(self.index, linid)
                else:
                    self.switch_off_lin_id(self.index, linid)

    def set_checksum_response(self, element_list, faulty):
        """
        Description: Sets/unsets a faulty checksum in the response of a list of frames or modules.
        These frames can be the name of the frame, the frame identifier or a module name.
        It's also possible to pass one item, not a list. So param 'element_list' can be:
            - A module name, frame name or frame id.
            - A list of a combination of the above.
        Parameter 'faulty' must be True or False.

        Note: All frames have correct checksum by default. Use this method to set faulty checksum to one or several.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            # You can use LIN id's to list the frames to set a faulty checksum
            lin1.set_faulty_checksum_response([0x12, 0x15, 0x21, 0x22], True)
            # You can use LIN frame names to list the frames to set a faulty checksum
            lin1.set_faulty_checksum_response(['SWS_LIN1_C', 'SWM_L1_P00'], True)
            # You can use one element instead of a list
            lin1.set_faulty_checksum_response(0x12, False)
            lin1.set_faulty_checksum_response('SWS_LIN1_C', True)
            # All frames of a module can also be used
            lin1.set_faulty_checksum_response('WMM', True)
        """ 
        if type(element_list) not in [tuple, list]: 
            element_list = [element_list]

        # Expand (possible) modules to frames
        element_list += self._find_frames_modules(element_list)

        # Modify each frame
        for item in element_list:
            linid = None
            if type(item) == str:
                linid = self.ldf.get_lin_id_from_frame_name(item)
            elif type(item) in [int, long]:
                linid = item
          
            if linid:
                if faulty and (linid not in self._frames_faulty_checksum):
                    self._frames_faulty_checksum.append(linid)
                elif not faulty and (linid in self._frames_faulty_checksum):
                    self._frames_faulty_checksum.remove(linid)

                for frame in self.ldf.frames:
                    if linid == frame.linid:
                        self._write_frame(frame.linid, frame.dlc, frame.message, faulty)

    def set_signal(self, signal_name, value, frame_name=None):
        """
        Description: Sets value in signal. The frame with this signal will be sent when the master (ECU) puts
        the header in the bus. It allows to write signals of any length, up to 32 bits in numeric way, or more
        than 32 bits in array way. See example below.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            # Writing a signal up tp 32 bits long
            lin1.set_signal('CCButtons', 2)
            # Writing a of several bytes long
            lin1.set_signal('SecRKE', [0x11, 0x22, 0x33, 0x44, 0x55])
        """
        linid, dlc, frame = self.ldf.write_signal_to_frame(signal_name, value, frame_name)
        if linid in self._frames_faulty_checksum:
            self._write_frame(linid, dlc, frame, faulty_checksum=True)
        else:
            self._write_frame(linid, dlc, frame, faulty_checksum=False)

    def get_signal(self, signal_name):
        """
        Description: Finds the signal in the frames buffer and return the signal value.
        The signal is usually a frame that the master (ECU) puts the header and data,
        or that other real slave as sent to the bus after a request from the master.

        Note: Returns an integer for signals up to 32 bits. Dont's use this method for longer than 32 bits
        signals, use get_frame method instead.

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            time.sleep(1)
            print lin1.get_signal('PowerModeL1') # PowerModeL1 is a signal in a frame sent by the master
        """
        linid, startbit, length = self.ldf.find_signal_info(signal_name)
        if linid:
            for frame in self._frames_received:
                if frame.linid == linid:
                    return self.ldf.read_signal_in_frame(startbit, length, frame.message[0])
        return 'void'

    def get_frame(self, frame_id):
        """
        Description: Returns frame content from buffer if a fresh frame is available. If a frame is returned,
        the frame is no longer considered as fresh, and new calls to this method will return an empty list [],
        until a new frame arrives.
        Returns [id, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
            com = COM('VECTOR')
            lin1 = com.open_lin_channel(0, 'LIN1_BCM.ldf')
            time.sleep(5) # Let the system work for 5s to send/receive frames
            # if you know the LIN ID of the frame
            frame_value = lin1.get_frame(0x1A)
            # if you know the name of one of the signals
            lin_id, start_bit, length = lin1.ldf.find_signal_info('SignalName')
            frame_value = lin1.get_frame(lin_id)
        """
        for frame in self._frames_received:
            if frame.linid == frame_id:
                if frame.updateFlag:
                    frame.updateFlag = False
                    return [frame.linid, frame.dlc, frame.time[0], frame.message[0]]
                else:
                    return []
        return []
    
    def set_schedule_table(self, index):
        """
        Description: activate the selected scheduling table from ldf using a numerical index or the name of the table.
        """
        if self.is_master:                
            if not isinstance(index, int):                
                for i in range(len(self.ldf.scheduling_tables)):
                    if index == self.ldf.scheduling_tables[i].name:
                        index = i
                        break
                    
            if index < len(self.ldf.scheduling_tables):
                self.ldf.scheduling_tables[index].counter = 0
                self.active_table_index = index
                print 'Schedule table set:', self.ldf.scheduling_tables[index].name             
            else:
                print 'Schedule table index out of range'
        else:
            print 'Not possible to set any schedule table. Channel should be configured as Master node.'
            
    def report_frame_info(self, frame_id):
        """
        Description: Returns frame information
        Returns [name, dlc]
        """
        return self.ldf.find_frame_info(frame_id)

    def get_fresh_frames(self):
        """
        Description: Returns first LIN fresh frame
        Returns [id, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        """
        all_lin_frames_lst = [[]]
        for frame in self._frames_received:
            if frame.traceFlag:
                frame.traceFlag = False
                all_lin_frames_lst[0] = [frame.linid, frame.dlc,  frame.time[0], frame.message[0]]
                return all_lin_frames_lst
        return all_lin_frames_lst

    def get_bus_state(self):
        """
        Description:
            returns LIN bus activity state
        """
        return self.linBusActive

    def get_bus_slaves(self):
        """
        Description:
            returns list of slaves from LDF
        """
        return self._slaves

    def get_slave_productid_by_name(self, slave):
        return self.ldf.report_slave_productid_by_name(slave)

    def get_slave_productid_by_nad(self, nad):
        return self.ldf.report_slave_productid_by_nad(nad)

    def get_slave_nad(self, slave):
        return self.ldf.report_slave_nad(slave)

    def get_schedules(self):
        return self.ldf.report_schedules()

    def get_schedule_frames(self, schedule):
        return self.ldf.report_schedule_frames(schedule)

    def get_schedule_frames_publisher(self, schedule):
        return self.ldf.report_schedule_frames_publisher(schedule)

    def get_schedule_delays(self, schedule):
        return self.ldf.report_schedule_delays(schedule)
    
    @staticmethod
    def _convert_data_to_str(data):
        """
        Description: Formats LIN data bytes so LIN frames are stored in the logfile as in CANOE logfiles.
        For example, integer 0x5a is returned as the string '5A'.
        """
        temp_data = str(hex(data))
        temp_data = temp_data.upper()
        temp_data = temp_data.replace('0X', '')
        if len(temp_data) == 1:
            temp_data = '0' + temp_data
        return temp_data

    def _format_frame(self, frame):
        """
        Description: Formats LIN frames to be stored in the logfile similar as in CANOE logfiles.
        Parameter 'frame' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        """
        # Format the timestamp
        temp_t = float(frame[3])
        temp_t = temp_t / 1000000000.0
        temp_t = '%.3f' % temp_t
        temp_s = ' ' * (10 - len(temp_t)) + temp_t + '  '
        # Format the LIN ID
        temp_id = str(hex(frame[0]))
        temp_id = temp_id.upper()
        temp_id = temp_id.replace('0X', '')
        # Format de data bytes
        temp_s = temp_s + temp_id + '  ' + str(frame[1]) + '  '
        dlc = frame[1]
        for i in range(dlc):
            temp_s += self._convert_data_to_str(frame[4][i]) + ' '
        return temp_s

    def save_logfiles(self):
        """
        Description:
            saves _diag_frames list containing diagnostics frames received
        """
        if self._diag_frames:
            f = open('dgn_body_logfile_lin.txt', 'w')
            for item in self._diag_frames:
                f.writelines(self._format_frame(item)+'\n')
            f.close()
