'''
====================================================================
Library for ISO 10681-2 on FlexRay (Communication layer services)
(C) Copyright 2016 Lear Corporation
====================================================================
'''

__author__ = "Albert Sanz"
__version__ = "1.0.7"
__email__ = "asanz@lear.com"

'''
CHANGE LOG
==========
1.0.7 Fixed multiple frame response processing, last frame data bytes where not being calculated for total response.
1.0.6 Fixed multiple frame response processing, as frames in dynamic segment can arrive unordered.
1.0.5 Only one slot ID or frame for requests llowed.
1.0.4 Fixed data_in_X_frame methods to take payload length into account.
1.0.3 Fixed clearing the Rx buffer in _send_request_once method, fixed some pylint issues.
1.0.2 Fixed last frame payload length.
1.0.1 Fixed error when getting response in several consecutive frames.
1.0.0 Initial version.
'''

import sys
import time
import threading
from operator import itemgetter
from dgnflex_cfg import *


# Prints additional info while debugging this library
NET_DEBUG = False

# Time in seconds that will produce a timeout in diagnostic response frame reception
RX_TIMEOUT = 5.0

# Number of retries for a request without response
REQUESTS_RETRIES = 3

FR_TP_FC_MAX_WAIT_RETRY = 2

FR_TP_BUFFER_SIZE = 120

# C_PCI types IDs
FR_TP_START_FRAME_ID = 0x40
FR_TP_START_FRAME_ACK_ID = 0x41
FR_TP_CONSECUTIVE_FRAME_1_ID = 0x50
FR_TP_CONSECUTIVE_FRAME_2_ID = 0x60
FR_TP_CONSECUTIVE_FRAME_EOB_ID = 0x70
FR_TP_FLOWCONTROL_FRAME_ID = 0x80
FR_TP_FLOWCONTROL_ACK_FRAME_ID = 0x84
FR_TP_LASTFRAME_ID = 0x90

# Flow Control Types IDs
FR_TP_FC_NONE = 0x00
FR_TP_FC_CTS = 0x03
FR_TP_FC_ACK_RETRY = 0x04
FR_TP_FC_WAIT = 0x05
FR_TP_FC_ABORT = 0x06
FR_TP_FC_OVERFLOW = 0x07
FR_TP_FC_TIMEOUT = 0x08

# FlexRay TP frame offsets
FR_TP_TA_OFFSET = 0
FR_TP_SA_OFFSET = 2
FR_TP_PCI_OFFSET = 4
FR_TP_FRAME_LENGTH_OFFSET = 5
FR_TP_MESSAGE_LENGTH_OFFSET = 6
FR_TP_DATA_OFFSET_FF_LF = 8
FR_TP_DATA_OFFSET_CF = 6
FR_TP_DATA_OFFSET_FC = 5

# FlexRay frame offsets
FR_FRAME_SLOT_ID = 0
FR_FRAME_TYPE = 1
FR_FRAME_CYCLE = 2
FR_FRAME_SIZE = 3
FR_TIME_STAMP = 4
FR_FRAME_DATA = 5

class ISO10681_2(object):
    '''
    Implements Network Layer defined in ISO 10681-2 (Network Layer + Transport Layer).
    '''

    ########################### PRIVATE FUNCTIONS ###########################

    def __init__(self):
        '''
        Description: Constructor
        '''
        # Public vars
        self.log_file = DGN_LOGFILE
        self.print_frames = False
        self.print_req_resp = True
        self.is_spr_req = False
        self.num_retries_request = REQUESTS_RETRIES
        # Private vars
        self._response = []
        self._all_frames = []
        self._resp_frames = []
        self._req_flexid = None
        self._res_flexid = []
        self._tp_restart = False
        self._tp_stop = True
        self._rx_timer = RX_TIMEOUT
        self._cf_idx = 0
        self._ftype = 'PHYSICAL'
        self._last_req_raw = ''
        self._last_resp_raw = ''
        self._fc_state = FR_TP_FC_NONE
        self._tp_threading = None
        self._req_log_idx_start = 0
        self._req_log_idx_end = 0
        self._request_message_length = 0
        self._tx_semaphore = threading.Semaphore(1)
        self._programming_session_active = False #TODO: Implement api to change it to True from dgn.py or iso.py


    def check_dgn_configuration(self):
        '''
        Description: Check paramenters set in dgnflex_cfg.py
        '''
        if DIAG_FRAMES_DEFINED_BY_NAME:
            frame_tester = self.get_frame_values(FR_NAME_ID_TESTER_FUNC_REQ)
            if frame_tester is None:
                print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                print '    DIAG_FRAMES_DEFINED_BY_NAME is set to TRUE and frame [' + FR_NAME_ID_TESTER_FUNC_REQ + '] is not defined in FIBEX/ARXML.\n'
                sys.exit()
            frame_tester = self.get_frame_values(FR_NAME_ID_TESTER_PHYS_REQ)
            if frame_tester is None:
                print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                print '    DIAG_FRAMES_DEFINED_BY_NAME is set to TRUE and frame [' + FR_NAME_ID_TESTER_PHYS_REQ + '] is not defined in FIBEX/ARXML.\n'
                sys.exit()
            for resp_frame in FR_NAME_ID_ECU_RESP:
                frame_ecu = self.get_frame_values(resp_frame)
                if frame_ecu is None:
                    print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                    print '    DIAG_FRAMES_DEFINED_BY_NAME is set to TRUE and frame [' + resp_frame + '] is not defined in FIBEX/ARXML.\n'
                    sys.exit()
        else:
            frame_tester = self.get_dgn_frame_name(FR_SLOT_ID_TESTER_FUNC_REQ)
            if frame_tester != 'Frame id not found':
                print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                print '    DIAG_FRAMES_DEFINED_BY_NAME is set to FALSE and slot ID configured [' + str(FR_SLOT_ID_TESTER_FUNC_REQ) + '] is already in use by FIBEX/ARXML.\n'
                sys.exit()
            frame_tester = self.get_dgn_frame_name(FR_SLOT_ID_TESTER_PHYS_REQ)
            if frame_tester != 'Frame id not found':
                print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                print '    DIAG_FRAMES_DEFINED_BY_NAME is set to FALSE and slot ID configured [' + str(FR_SLOT_ID_TESTER_PHYS_REQ) + '] is already in use by FIBEX/ARXML.\n'
                sys.exit()
            for resp_frame in FR_SLOT_ID_ECU_RESP:
                frame_ecu = self.get_dgn_frame_name(resp_frame)
                if frame_ecu != 'Frame id not found':
                    print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                    print '    DIAG_FRAMES_DEFINED_BY_NAME is set to FALSE and slot ID configured [' + str(resp_frame) + '] is already in use by FIBEX/ARXML.\n'
                    sys.exit()
            if MAX_PAYLOAD_REQUEST_APP > 254:
                print 'ERROR: Check DGN FlexRay configuration (dgnflex_cfg.py):'
                print '    MAX_PAYLOAD_REQUEST_APP can be never greather than 254 MAX FlexRay frame size.'
                sys.exit()


    def _gen_response(self):
        '''
        Description: Reads DGN response frames stored in self._resp_frames and writes total response data in self._response.
        '''
        self._response = []
        resp_length = 0
        # Order response frames by timestamp
        temp_response = sorted(self._resp_frames, key=itemgetter(4))
        # Check if receiver cancelled transmission
        if self._fc_state == FR_TP_FC_TIMEOUT:
            print '     Transmission cancelled by FlowControl Timeout'
        elif self._fc_state != FR_TP_FC_NONE:
            print '     Transmission cancelled by receiver FlowControl: ' + str(self._fc_state)
        else:
            # Process the response frames to generate the complete response
            for item in temp_response:
                # Check if response pending (NRC 78)
                if self._is_resp_pending(item):
                    pass
                # Check if response is flow control
                elif self._is_resp_fc(item):
                    pass
                # Check if start frame response to get the message length and add its data
                elif self._is_resp_start_frame(item):
                    resp_length = self._resp_message_length(item)
                    self._response.extend(self._data_in_first_frame(item))
                # Check if ist consecutive frame response
                elif self._is_resp_consecutive_frame(item):
                    self._response.extend(self._data_in_consecutive_frame(item))
                # Check if last frame response
                elif self._is_resp_last_frame(item):
                    self._response.extend(self._data_in_first_frame(item)) # data position same as fisrt frame
                    # No more items should be added, should be the last item but just in case, break the for loop
                    break
                else:
                    # Error situation... a frame different from SF, CF or LF has been received..
                    break
            # Remove crap bytes at the end of self._response
            while len(self._response) > resp_length:
                self._response.pop(-1)
        return self._response


    def get_dgn_frame_size(self, frame):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def write_dgn_frame_by_id(self, frame_id, raw_values=[]):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def write_dgn_frame(self, frame_name, data, mode=1, send_all_frame_byte=True):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass

    def read_dgn_frame_by_id(self, frame_id, popleft=True):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def read_dgn_frame(self, frame_id, popleft=True):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def get_frame_values(self, frame_name):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def get_dgn_frame_name(self, frame_id):
        '''
        Description: Method injected at runtime when this class is created.
        '''
        pass


    def _frame_id(self, frame):
        '''
        Description: Returns frame identifier of frame 'frame'.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return frame[FR_FRAME_SLOT_ID]


    def _frame_data(self, frame, i):
        '''
        Description: Returns data byte 'i' of the diagnostics response frame 'frame'.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return frame[FR_FRAME_DATA][i]


    def _resp_message_length(self, frame):
        '''
        Description: Returns length of the message contained in the Start frame. Function only valid in Start frames!!!
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return 0x100 * self._frame_data(frame, FR_TP_MESSAGE_LENGTH_OFFSET) + self._frame_data(frame, FR_TP_MESSAGE_LENGTH_OFFSET + 1)


    def _resp_payload_length(self, frame):
        '''
        Description: Returns length of the Payload of a Start Frame, or Consecutive Frame or Last frame
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return  self._frame_data(frame, FR_TP_FRAME_LENGTH_OFFSET)


    def _data_in_single_frame(self, frame):
        '''
        Description: Returns a list containing the data present in a single frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return frame[FR_FRAME_DATA][FR_TP_DATA_OFFSET_FF_LF:FR_TP_DATA_OFFSET_FF_LF + self._resp_payload_length(frame)]


    def _data_in_first_frame(self, frame):
        '''
        Description: Returns a list containing the data present in a first frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return frame[FR_FRAME_DATA][FR_TP_DATA_OFFSET_FF_LF:FR_TP_DATA_OFFSET_FF_LF + self._resp_payload_length(frame)]


    def _data_in_consecutive_frame(self, frame):
        '''
        Description: Returns a list containing the data present in a consecutive frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return frame[FR_FRAME_DATA][FR_TP_DATA_OFFSET_CF:FR_TP_DATA_OFFSET_CF + self._resp_payload_length(frame)]


    def _index_in_consecutive_frame(self, frame):
        '''
        Description: Returns the frame index present in a consecutive frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example:
        '''
        return self._frame_data(frame, FR_TP_PCI_OFFSET) & 0x0F


    def _max_data_length_req_sf(self):
        '''
        Description: Returns max data length for requesting a single frame
        '''
        if DIAG_FRAMES_DEFINED_BY_NAME:
            if self._ftype == 'FUNCTIONAL':
                return self.get_dgn_frame_size(FR_NAME_ID_TESTER_FUNC_REQ) - FR_TP_DATA_OFFSET_FF_LF
            else:
                return self.get_dgn_frame_size(FR_NAME_ID_TESTER_PHYS_REQ) - FR_TP_DATA_OFFSET_FF_LF
        else:
            return MAX_PAYLOAD_REQUEST_APP


    def _max_data_length_req_cf(self):
        '''
        Description: Returns max data length for a consecutive frame
        '''
        if DIAG_FRAMES_DEFINED_BY_NAME:
            if self._ftype == 'FUNCTIONAL':
                return self.get_dgn_frame_size(FR_NAME_ID_TESTER_FUNC_REQ) - FR_TP_DATA_OFFSET_CF
            else:
                return self.get_dgn_frame_size(FR_NAME_ID_TESTER_PHYS_REQ) - FR_TP_DATA_OFFSET_CF
        else:
            return MAX_PAYLOAD_REQUEST_APP


    def _max_data_length_res_sf(self):
        '''
        Description: Returns max data length for response per frame
        '''
        if DIAG_FRAMES_DEFINED_BY_NAME:
            return self.get_dgn_frame_size(FR_NAME_ID_ECU_RESP[0]) - FR_TP_DATA_OFFSET_FF_LF
        else:
            return MAX_PAYLOAD_RESPONSE_APP


    def _is_resp_multi_frame(self, frame):
        '''
        Description: Checks if frame response 'frame' is a multiple frame response.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            return self._resp_message_length(frame) > self._resp_payload_length(frame)
        else:
            return False


    def _is_resp_pending(self, frame):
        '''
        Description: Checks if frame response fr is response pending.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            return self._frame_data(frame, FR_TP_DATA_OFFSET_FF_LF) == 0x7F and self._frame_data(frame, FR_TP_DATA_OFFSET_FF_LF + 2) == 0x78
        else:
            return False


    def _is_resp_fc(self, frame):
        '''
        Description: Checks if frame response fr is a flow control frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            return self._frame_data(frame, FR_TP_PCI_OFFSET) & 0xF0 == FR_TP_FLOWCONTROL_FRAME_ID
        else:
            return False


    def _is_resp_start_frame(self, frame):
        '''
        Description: Checks if frame response fr is a flow control frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            pci_type = self._frame_data(frame, FR_TP_PCI_OFFSET) & 0xF0
            return pci_type == FR_TP_START_FRAME_ID or pci_type == FR_TP_START_FRAME_ACK_ID
        else:
            return False


    def _is_resp_last_frame(self, frame):
        '''
        Description: Checks if frame response 'frame' is a flow control frame.
        Parameter 'framefr' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            return self._frame_data(frame, FR_TP_PCI_OFFSET) & 0xF0 == FR_TP_LASTFRAME_ID
        else:
            return False

    def _is_resp_consecutive_frame(self, frame):
        '''
        Description: Checks if frame response 'frame' is a flow control frame.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None:
            pci_type = self._frame_data(frame, FR_TP_PCI_OFFSET) & 0xF0
            return pci_type == FR_TP_CONSECUTIVE_FRAME_1_ID or pci_type == FR_TP_CONSECUTIVE_FRAME_2_ID or pci_type == FR_TP_CONSECUTIVE_FRAME_EOB_ID
        else:
            return False


    def _send_flow_control(self):
        '''
        Description: Writes flow control CTS (Continue To Send) FlexRay frame in the bus.
        '''
        fr_fc = []
        self._build_addressing(fr_fc, 'PHYSICAL')
        fr_fc.append(FR_TP_FLOWCONTROL_FRAME_ID | FR_TP_FC_CTS)
        fr_fc.extend([0, 0, 0]) # Add BC = 0 (no Bandwidth control) and BfS = 0 (no more FC)
        self._ftype = 'PHYSICAL' # Force physical addressing for the rest of the request
        self._write_frame(fr_fc)


    def _get_bandwidth_from_fc(self, frame):
        '''
        Description: Returns BC (BandWidth) parameter in a Flow Control frame type CTS (ContinueToSend).
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return self._frame_data(frame, FR_TP_DATA_OFFSET_FC)


    def _get_buffer_size_from_fc(self, frame):
        '''
        Description: Returns BfS (BufferSize) parameter in a Flow Control frame type CTS (ContinueToSend).
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return (0x100 * self._frame_data(frame, FR_TP_DATA_OFFSET_FC + 1)) + self._frame_data(frame, FR_TP_DATA_OFFSET_FC + 2)


    def _build_addressing(self, fr_req, req_type):
        # Add Target address
        if req_type == 'FUNCTIONAL':
            tmp_b0_b1 = ID_N_TA_FUNCTIONAL
            fr_req.append(tmp_b0_b1 / 0x100)
            fr_req.append(tmp_b0_b1 % 0x100)
        else:
            tmp_b0_b1 = ID_N_TA_PHYSICAL
            fr_req.append(tmp_b0_b1 / 0x100)
            fr_req.append(tmp_b0_b1 % 0x100)
        # Add Source address
        tmp_b0_b1 = ID_N_SA
        fr_req.append(tmp_b0_b1 / 0x100)
        fr_req.append(tmp_b0_b1 % 0x100)
        return fr_req


    def _write_frame(self, data):
        '''
        Description: Writes FR frame in the bus, with data provided as parameter (list).
        FR slot ID is the one stored in self._req_flexid var, and DLC is the length of the data list parameter.
        This function waits also for the reception, and stores and prints the Rx frame.
        '''
        self._tp_restart = True
        time_start = time.clock()
        time_elapsed = 0.0

        if DIAG_FRAMES_DEFINED_BY_NAME is False:
            if DGN_SEND_ALL_FRAME_BYTES is True:
                zeroes = [0] * (MAX_PAYLOAD_REQUEST_APP - len(data))
                data.extend(zeroes)
            self.write_dgn_frame_by_id(self._req_flexid, data)
        else:
            self.write_dgn_frame(self._req_flexid, data, 2, DGN_SEND_ALL_FRAME_BYTES)
        # Check for the correct transmission of the request
        frame = []
        while (frame == [] or frame is None) and time_elapsed < self._rx_timer:
            time_elapsed = time.clock() - time_start
            if not DIAG_FRAMES_DEFINED_BY_NAME:
                frame = self.read_dgn_frame_by_id(self._req_flexid, popleft=True)
            else:
                frame = self.read_dgn_frame(self._req_flexid, popleft=True)
        if frame != [] and frame != None:
            self._all_frames.append(frame)
            if self.print_frames:
                self._print_frame(self._all_frames[-1])
        else:
            print 'Not possible to send diagnostic request to the bus. Is ECU powered and running?'


    def _read_frame(self):
        '''
        Description: Reads diagnostics response frames in the bus. The function is blocking until a valid
        diagnostic response is received. It also stores and prints the Rx frame.
        '''
        time_start = time.clock()
        time_elapsed = 0.0
        frame = []
        while (frame == [] or frame is None) and time_elapsed < self._rx_timer:
            # search for a response message
            for resp_frame in self._res_flexid:
                if not DIAG_FRAMES_DEFINED_BY_NAME:
                    frame = self.read_dgn_frame_by_id(resp_frame, popleft=True)
                else:
                    frame = self.read_dgn_frame(resp_frame, popleft=True)
                if frame:
                    if NET_DEBUG: print 'RESPONSE RECEIVED IN ' + resp_frame
                    break
            time_elapsed = time.clock() - time_start
        if frame != [] and frame != None:
            # fr frame format: [slotID, type, cycleCount, payloadLength, timestamp, [B0, B1, B2, B3, B4, B5, B6, B7...]].
            self._all_frames.append(frame)
            self._resp_frames.append(frame)
            if self.print_frames:
                self._print_frame(self._all_frames[-1])

        return frame


    def _print_frame(self, frame):
        '''
        Description: Prints frame on screen, with the correct format.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        print self._format_frame(frame)


    def _convert_data_to_str(self, data, nbytes):
        '''
        Description: Formats data bytes so FR frames are stored in the logfile as in CANOE logfiles.
        For example, integer 0x5a is returned as the string '5A'.
        '''
        temp_data = str(hex(data))
        temp_data = temp_data.upper()
        temp_data = temp_data.replace('0X', '')
        hex_string_characters = nbytes * 2
        while len(temp_data) < hex_string_characters:
            temp_data = '0' + temp_data
        return temp_data


    def _convert_data_to_raw(self, data):
        '''
        Description: Formats data bytes to a string of hex numbers without '0X'.
        For example, integer [10 128 255] is returned as the string [0A 80 FF]
        '''
        return '[' + ' '.join([self._convert_data_to_str(item, 1) for item in data]) + ']'


    def _format_timestamp(self, timestamp):
        '''
        Description: Formats a timestamp integer given by the Vector driver to a string in units=seconds.
        For example, timestamp 1237123072 is converted to '     1.218  '
        '''
        temp_t = float(timestamp)
        temp_t = temp_t / 1000000000.0
        temp_t = '%.3f' % temp_t
        temp_s = ' ' * (10 - len(temp_t)) + temp_t + '  '
        return temp_s


    def _format_frame(self, frame):
        '''
        Description: Formats FlexRay frames to be stored in a logfile.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        # Format the FlexRay data and the data bytes
        dlc = len(frame[FR_FRAME_DATA]) #frame[FR_FRAME_SIZE] * 2
        temp_s = self._format_timestamp(frame[FR_TIME_STAMP])
        temp_s += str(frame[FR_FRAME_SLOT_ID]).rjust(3) + '  ' +  str(dlc).rjust(3) + '  '
        for i in range(dlc):
            temp_s += self._convert_data_to_str(frame[FR_FRAME_DATA][i], 1) + ' '
        return temp_s


    def _send_tester_present(self):
        '''
        Description: Starts a thread for sending periodic tester present frames.
        '''
        # This function is launched as a thread
        start_time = time.clock()
        elapsed_time = 0
        # Keep running until stopTP function is called and sets self._tp_stop to False
        while not self._tp_stop:
            # Check if timer needs to be restarted (that's happens when because _write_frame was called)
            if self._tp_restart:
                self._tp_restart = False
                start_time = time.clock()
                elapsed_time = 0
            else:
                # Check if TP needs to be sent
                elapsed_time = time.clock() - start_time
                if elapsed_time > TESTER_PRESENT_PERIOD:
                    start_time = time.clock()
                    elapsed_time = 0.0
                    self._tx_semaphore.acquire()
                    # Build TP frame
                    tp_frame = []
                    self._build_addressing(tp_frame, 'FUNCTIONAL')
                    tp_frame.append(FR_TP_START_FRAME_ID)
                    tp_frame.extend([0x02, 0x00, 0x02, 0x3E, 0x80])

                    temp = self.print_frames
                    self.print_frames = False
                    temp_ftype = self._ftype
                    self._ftype = 'FUNCTIONAL'
                    self._write_frame(tp_frame)
                    self._ftype = temp_ftype
                    self.print_frames = temp
                    self._tx_semaphore.release()
                else:
                    time.sleep(TESTER_PRESENT_PERIOD - elapsed_time + 0.001)


    def _send_req_sf(self, data):
        '''
        Description: Sends diagnostic request that fits in one single frame.
        Parameter 'data' is a list with the request contents.
        '''
        # Request can be sent in one frame
        fr_req = []
        fr_req = self._build_addressing(fr_req, self._ftype)

        # Build PCI data
        frame_payload = min(len(data), self._max_data_length_req_sf())
        fr_req.append(FR_TP_START_FRAME_ID)
        fr_req.append(frame_payload)
        fr_req.append(len(data) / 0x100)
        fr_req.append(len(data) % 0x100)

        # Add Message data
        for _ in range(frame_payload):
            fr_req.append(data.pop(0))
        if NET_DEBUG: print 'SEND REQUEST FF'
        self._write_frame(fr_req)


    def _send_req_cf(self, data):
        '''
        Description: Sends consecutive frames of a multiple frame request.
        Parameter 'data' is a list with the request contents (must not contain the data already sent in the first frame).
        '''
        frame = self._wait_process_ecu_fc()
        if frame != [] and frame != None:
            bfsize_receiver_pending = self._get_buffer_size_from_fc(frame)
            if bfsize_receiver_pending == 0:
                bfsize_receiver_pending = 0x10000 # No buffer allocation requested by receiver, so force invalid value to send all CF consecutively
            # bw = self._get_bandwitch_from_fc(fr) # TODO: Not used in current TP version!!

            # Send consecutive frames, till buffer is empty
            while len(data) > 0:
                fr_req = []
                fr_req = self._build_addressing(fr_req, 'PHYSICAL')

                # Build PCI data for consecutive frame depending pending data and pending buffer size of receiver
                if len(data) <= self._max_data_length_req_sf():
                    if len(data) <= bfsize_receiver_pending:
                        if NET_DEBUG: print 'SEND REQUEST LF'
                        frame_payload = len(data)
                        fr_req.append(FR_TP_LASTFRAME_ID)
                        fr_req.append(frame_payload)
                        fr_req.append(self._request_message_length / 0x100)
                        fr_req.append(self._request_message_length % 0x100)
                    else:
                        if NET_DEBUG: print 'SEND REQUEST CF_EOB'
                        frame_payload = bfsize_receiver_pending
                        fr_req.append(FR_TP_CONSECUTIVE_FRAME_EOB_ID + self._cf_idx)
                        fr_req.append(frame_payload)
                else:
                    if bfsize_receiver_pending <= self._max_data_length_req_cf():
                        if NET_DEBUG: print 'SEND REQUEST CF_EOB'
                        frame_payload = bfsize_receiver_pending
                        fr_req.append(FR_TP_CONSECUTIVE_FRAME_EOB_ID + self._cf_idx)
                        fr_req.append(frame_payload)
                    else:
                        if NET_DEBUG: print 'SEND REQUEST CF'
                        frame_payload = self._max_data_length_req_cf()
                        fr_req.append(FR_TP_CONSECUTIVE_FRAME_1_ID + self._cf_idx)
                        fr_req.append(frame_payload)
                bfsize_receiver_pending -= frame_payload
                self._cf_idx += 1
                if self._cf_idx == 16:
                    self._cf_idx = 0

                # Add Message data
                for _ in range(frame_payload):
                    fr_req.append(data.pop(0))
                # Wait at least 6 cycles before sending next consecutive frame (Fr library timing limitations)
                time.sleep(0.03)
                self._write_frame(fr_req)
                # If receiver buffer is empty and not Last Frame, wait for ECU Flow Control frame
                if bfsize_receiver_pending == 0 and data:
                    frame = self._wait_process_ecu_fc()
                    if frame != [] and frame != None:
                        bfsize_receiver_pending = self._get_buffer_size_from_fc(frame)
                        if bfsize_receiver_pending == 0:
                            bfsize_receiver_pending = 0x10000
                    else:
                        break # Missing Flow Control Frame or cancel... stop transmission


    def _manage_resp_pending(self, frame):
        '''
        Description: Manages response pending responses from the ECU. Basically waits until the final response is given by the ECU.
        Parameter 'frame' is a frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if frame != [] and frame != None and self._is_resp_pending(frame):
            if NET_DEBUG: print 'RESPONSE PENDING...'
            frame = self._read_frame()
            while self._is_resp_pending(frame):
                if NET_DEBUG: print 'RESPONSE PENDING...'
                frame = self._read_frame()
        return frame


    def _manage_multiple_frame_resp(self, frame):
        '''
        Description: Manages multiple response from the ECU. It takes the first frame 'frame' from the ECU, and generates
        flow control frames accordingly, until the total response from the ECU is completed.
        Parameter 'frame' is the Fisrt Frame with the struct: [id, type, cycle, dlc, timestamp, [b0, b1, b2, b3, b4, b5, b6, b7]]
        Returns True if received response was complete.
        '''
        # Store total length of the multi frame response.
        resp_mf_length = self._resp_message_length(frame)
        if NET_DEBUG: print 'MULTIPLE FRAME RESPONSE ON PROGRESS, TOTAL LENGTH', resp_mf_length, 'BYTES'
        resp_mf_length -= self._resp_payload_length(frame)
        if NET_DEBUG: print 'FIRST FRAME RECEIVED, STILL REMAINING', resp_mf_length, 'BYTES'
        # Send FC
        if NET_DEBUG: print 'SEND FLOW CONTROL'
        self._send_flow_control()
        # Check response CF
        last_frame_received = False
        if NET_DEBUG: print 'CHECK RESPONSE CF'
        while resp_mf_length > 0 or last_frame_received == False:
            if NET_DEBUG: print 'WAITING RESPONSE CF...'
            frame = self._read_frame()
            if frame != [] and frame != None:
                resp_mf_length = resp_mf_length - self._resp_payload_length(frame)
                if not self._is_resp_last_frame(frame):
                    if last_frame_received:
                        if NET_DEBUG: print 'RESPONSE CF RECEIVED, STILL REMAINING', resp_mf_length, 'BYTES. LAST FRAME RECEIVED'
                    else:
                        if NET_DEBUG: print 'RESPONSE CF RECEIVED, STILL REMAINING', resp_mf_length, 'BYTES. LAST FRAME NOT RECEIVED'
                else:
                    last_frame_received = True
                    if NET_DEBUG: print 'LAST CF RECEIVED, STILL REMAINING', resp_mf_length, 'BYTES'
            else:
                return False # Timeout...
        if NET_DEBUG: print 'END OF RESPONSE'
        return True


    def _wait_process_ecu_fc(self):
        '''
        Description: Waits for the flow control frame sent by the ECU (in case of a long request sent by this tool)
                     and process the received FC type
        '''
        # Wait for ECU Flow Control frame
        if NET_DEBUG: print 'CHECK RESPONSE FC'
        fc_retry_count = 0
        fc_type = FR_TP_FC_NONE
        while fc_retry_count < FR_TP_FC_MAX_WAIT_RETRY:
            fc_retry_count += 1
            frame = self._read_frame()
            if self._is_resp_fc(frame):
                fc_type = self._frame_data(frame, FR_TP_PCI_OFFSET) & 0x0F
                if fc_type == FR_TP_FC_ACK_RETRY:
                    self._fc_state = FR_TP_FC_ACK_RETRY
                    if NET_DEBUG: print '    ECU Flow Control Requested RETRY, not supported yet :('
                    break
                elif fc_type == FR_TP_FC_WAIT or fc_type == FR_TP_FC_NONE:
                    if NET_DEBUG: print '    ECU Flow Control Requested WAIT, or not received, retry, wait next frame.'
                    # Do not break!
                elif fc_type == FR_TP_FC_ABORT or fc_type == FR_TP_FC_OVERFLOW:
                    self._fc_state = fc_type
                    if NET_DEBUG: print '    ECU Flow Control aborted transmission'
                    break
                elif fc_type == FR_TP_FC_CTS:
                    break
                else:
                    print '    Invalid FlowControl FS received: ' + str(fc_type)
                    break
            else:
                # No FC message received or timeout...
                break

        # Return FC if valid or none with corresponding error code
        if fc_type == FR_TP_FC_CTS:
            return frame
        else:
            if fc_type == FR_TP_FC_NONE:
                self._fc_state = FR_TP_FC_TIMEOUT
            return []


    def _send_request_once(self, data, ftype):
        '''
        Description: Sends DGN physical or functional request, with the data specified. Data can be of any length.
        Parameter 'ftype' can be 'PHYSICAL' or 'FUNCTIONAL'.
        This function will also send the network frames needed.
        Returns True if transmission was successful.
        Returns False if there was a network frame missing or not detected from the ECU.
        '''
        self._ftype = ftype
        # Create a copy of data in temp_data and work with it, because it's going to be modified
        temp_data = list(data)
        self._request_message_length = len(data)
        self._fc_state = FR_TP_FC_NONE

        # Prepare the flexray slots IDs
        if DIAG_FRAMES_DEFINED_BY_NAME:
            self._res_flexid = FR_NAME_ID_ECU_RESP
            if self._ftype == 'FUNCTIONAL':
                self._req_flexid = FR_NAME_ID_TESTER_FUNC_REQ
            else:
                self._req_flexid = FR_NAME_ID_TESTER_PHYS_REQ
        if not DIAG_FRAMES_DEFINED_BY_NAME:
            self._res_flexid = FR_SLOT_ID_ECU_RESP
            if self._ftype == 'FUNCTIONAL':
                self._req_flexid = FR_SLOT_ID_TESTER_FUNC_REQ
            else:
                self._req_flexid = FR_SLOT_ID_TESTER_PHYS_REQ

        # Clean up diagnostic frames rx buffer
        temp = self.print_frames
        self.print_frames = False
        self._rx_timer = 0.01
        frame = self._read_frame()
        while frame != [] and frame != None:
            frame = self._read_frame()
        self._rx_timer = RX_TIMEOUT
        self.print_frames = temp

        self._resp_frames = []

        self._req_log_idx_start = len(self._all_frames)

        if len(temp_data) <= self._max_data_length_req_sf():
            # Request must be sent in one single frame
            self._send_req_sf(temp_data)
            if not self.is_spr_req:
                # Check response
                if NET_DEBUG: print 'CHECK RESPONSE'
                frame = self._read_frame()
                frame = self._manage_resp_pending(frame)
                if self._is_resp_multi_frame(frame):
                    if not self._manage_multiple_frame_resp(frame):
                        return []
        else:
            # Request must be sent in several frames
            self._send_req_sf(temp_data)
            self._cf_idx = 1                # SN = 1 after STF
            self._send_req_cf(temp_data)
            if not self.is_spr_req and self._fc_state == FR_TP_FC_NONE:
                # Check response
                if NET_DEBUG: print 'CHECK RESPONSE'
                frame = self._read_frame()
                frame = self._manage_resp_pending(frame)
                if self._is_resp_multi_frame(frame):
                    if not self._manage_multiple_frame_resp(frame):
                        return []

        self._req_log_idx_end = len(self._all_frames)

        # Request sent and response received. Generate raw response calling self._gen_response()
        return self._gen_response()


    ########################### PUBLIC FUNCTIONS ###########################

    def save_logfile(self):
        '''
        Description: Writes frames to the logfile.
        '''
        # Stop TP frames if not already stopped
        if not self._tp_stop:
            self._tp_stop = True
            self._tp_threading.join()
        if self._all_frames != []:
            logfile = open(self.log_file, 'w')
            for item in self._all_frames:
                logfile.writelines(self._format_frame(item) + '\n')
            logfile.close()


    def req_info(self):
        '''
        Description: Returns a string with the latest request + response frames

        Example of string returned:
            1.209  726  8  03 22 F1 88 00 00 00 00
            1.228  72E  8  10 1B 62 F1 88 47 58 37
            1.229  726  8  30 00 0A 00 00 00 00 00
            1.238  72E  8  21 33 2D 31 34 43 31 38
            1.248  72E  8  22 34 2D 41 41 31 32 00
            1.258  72E  8  23 00 00 00 00 00 00 00
        '''
        temp_str = '\n'
        for i in range(self._req_log_idx_start, self._req_log_idx_end):
            temp_str = temp_str + self._format_frame(self._all_frames[i]) + '\n'
        return temp_str


    def req_info_raw(self):
        '''
        Description: Returns a string with the latest request + response raw data

        Example of string returned:
            Req: [22 F1 88]
            Rsp: [62 F1 88 47 58 37 33 2D 31 34 43 31 38 34 2D 41 41 31 32 00 00 00 00 00 00 00 00]
        '''
        return '\nReq:' + self._last_req_raw + '\nRsp:' + self._last_resp_raw + '\n'


    def start_periodic_tp(self):
        '''
        Description: Starts the transmission of periodic Tester Present frames.
        Period is defined in parameter TESTER_PRESENT_PERIOD in config.py file.
        Tester Present frames will be sent strictly when needed. Diagnostic requests resets the
        TESTER_PRESENT_PERIOD timer, so Tester Present frames will be only sent if a diagnostics
        inactivity period of TESTER_PRESENT_PERIOD happens.
        '''
        # Start sending TP frames only if they're not being sent
        if self._tp_stop:
            self._tp_stop = False
            self._tp_restart = False
            # Launch thread with function self._sendTP
            self._tp_threading = threading.Thread(target=self._send_tester_present)
            self._tp_threading.daemon = True
            self._tp_threading.start()


    def stop_periodic_tp(self):
        '''
        Description: Stops the transmission of periodic Tester Present frames.
        '''
        # Stop thread by setting self._tp_stop = True
        if not self._tp_stop:
            self._tp_stop = True
            self._tp_threading.join()


    def send_request(self, data, ftype='PHYSICAL'):
        '''
        Description: Sends DGN physical or functional request, with the data specified. Data can be of any length.
        Parameter 'ftype' can be 'PHYSICAL' or 'FUNCTIONAL'.
        This function will also send the network frames needed in the transport protocol. If there's some error detected
        in the network frames received from the ECU, the request will be retried. Max 5 retries will be performed.
        '''
        self._tx_semaphore.acquire()
        result = self._send_request_once(data, ftype)
        num_retries = self.num_retries_request
        while result == [] and num_retries != 0 and not self.is_spr_req:
            print '     Incomplete response detected, trying again...\n'
            result = self._send_request_once(data, ftype)
            num_retries -= 1
        if num_retries == 0 and self.num_retries_request > 0:
            print '     Incomplete response detected, aborting retries\n'
            result = []

        # Store request and response in raw format, useful for reporting them
        self._last_resp_raw = self._convert_data_to_raw(result)
        self._last_req_raw = self._convert_data_to_raw(data)

        # Print raw request & response, with the timestamp
        if self.print_req_resp:
            if result == []:
                if self._all_frames != []:
                    if self.is_spr_req:
                        print self._format_timestamp(self._all_frames[-1][FR_TIME_STAMP]) + 'Req (SPR): ' + self._last_req_raw
                    else:
                        print self._format_timestamp(self._all_frames[-1][FR_TIME_STAMP]) + 'Req: ' + self._last_req_raw
                        print '------> No response after '+ str(self.num_retries_request+1) +' attempts'
                else:
                    print self._format_timestamp(time.clock()*10e9) + 'Not possible to send Request after '+ str(self.num_retries_request+1) +' attempts, check bus communication'
            else:
                i = self._all_frames.index(self._resp_frames[0])
                print self._format_timestamp(self._all_frames[i-1][FR_TIME_STAMP]) + 'Req: ' + self._last_req_raw
                print self._format_timestamp(self._resp_frames[0][FR_TIME_STAMP]) + 'Rsp: ' + self._last_resp_raw

            print ''

        self._tx_semaphore.release()
        return result
