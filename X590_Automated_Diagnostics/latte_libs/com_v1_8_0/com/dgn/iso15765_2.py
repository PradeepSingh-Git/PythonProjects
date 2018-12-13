'''
====================================================================
Library for ISO 15765-2 on CAN (also called Network Layer)
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = 'Jesus Fidalgo'
__version__ = '1.2.10'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.2.10 Bugfix: Added _tx_semaphore.acquire() in _send_TP method.
1.2.9 Bugfix: using semaphores when sending a request, to avoid conflicts with Tester Present thread.
      Bugfix: STmin set to minimum value of 0.0005s.
1.2.8 Bugfix: multiframe request not working correctly with long requests.
1.2.7 Bugfix: multiframe request data was not correctly displayed on screen.
      Added: thread for tester present configured as daemon (change in 1.1.0 was lost).
1.2.6 Bugfix: method send_request time.clock must be time.clock().
1.2.5 Method _format_frame simplified.
1.2.4 SPR requests managed correctly when printing raw requests and responses.
1.2.3 Printing timestamp with raw requests and responses.
1.2.2 Bugfix: parenthesis problem in send_request.
1.2.1 Detecting SPR requests in send_request method to avoid retries in this case.
1.2.0 Request and response printed in screen in a compact way. It improves multiple frames responsiveness.
1.1.1 Bugfix: method _is_resp_pending now checking additonally if the response is a negative response.
1.1.0 Added: thread self.tp for tester present set as daemon.
      Added: check of consecutive frames order from the ECU. If a problem is found, original request is retried.
1.0.4 RX_TIMEOUT set to 5s. Spec ISO 15765-3 specifies P2*CAN_Client to be 5s.
1.0.3 Method _is_resp_pending more robust by checking NRC 0x7F.
1.0.2 Method stop_periodic_tp, check if start_periodic_tp has been called before.
1.0.1 Added: printing frames DLC also in the screen.
      Removed: message in the screen if diagnostics rx frame not received.
      Bugfix: clearing rx diagnostics frame before sending a new request.
      Bugfix: in multiple frame request, check if flow control received from ECU and abort if needed.
1.0.0 Inital version.
'''

import sys
import time
import threading
from dgn_cfg import *


# Prints additional info while debugging this library
NET_DEBUG = False

# Time in seconds that will produce a timeout in diagnostic response frame reception
RX_TIMEOUT = 5.0


class ISO15765_2():
    '''
    Implements Network Layer defined in ISO 15765-2 (Network Layer + Transport Layer).
    Does not implement Session Layer defined in ISO 15765-3.
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
        # Private vars
        self._response = []
        self._all_frames = []
        self._resp_frames = []
        if EXTENDED_ADDRESSING:
            self._req_canid = ID_BASE_ADDRESS + N_SA
        else:
            self._req_canid = ID_PHYSICAL_REQ
        self._tp_restart = False
        self._tp_stop = True
        self._rx_timer = RX_TIMEOUT
        self._tx_semaphore = threading.Semaphore(1)


    def _gen_response(self):
        '''
        Description: Reads DGN response frames stored in self._resp_frames and writes total response data in self._response.
        '''
        self._response = []
        resp_length = 0
        for item in self._resp_frames:
            # Check if response pending (NRC 78)
            if self._is_resp_pending(item):
                pass
            # Check if response is flow control
            elif self._is_resp_fc(item):
                pass
            # Check if single frame response
            elif self._resp_length(item) < 0x10:
                resp_length = self._resp_length(item)
                self._response.extend(self._data_in_single_frame(item))
            # Check if first frame response
            elif self._resp_length(item) < 0x20:
                resp_length = self._first_frame_length(item)
                self._response.extend(self._data_in_first_frame(item))
            # Else consecutive frame response
            else:
                self._response.extend(self._data_in_consecutive_frame(item))
        # Remove crap bytes at the end of self._response
        while len(self._response) > resp_length:
            self._response.pop(-1)
        return self._response


    def _frame_id(self, fr):
        '''
        Description: Returns frame identifier of frame 'fr'.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return fr[0]


    def _frame_data(self, fr, i):
        '''
        Description: Returns data byte 'i' of the diagnostics response frame 'fr'.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return fr[3][i]


    def _resp_length(self, fr):
        '''
        Description: Returns length field of a diagnostics response frame, that is, data byte 0.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return self._frame_data(fr, 1)
        else:
            return self._frame_data(fr, 0)


    def _data_in_single_frame(self, fr):
        '''
        Description: Returns a list containing the data present in a single frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return fr[3][2:self._resp_length(fr) + 2]
        else:
            return fr[3][1:self._resp_length(fr) + 1]


    def _data_in_first_frame(self, fr):
        '''
        Description: Returns a list containing the data present in a first frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return fr[3][3:8]
        else:
            return fr[3][2:8]


    def _data_in_consecutive_frame(self, fr):
        '''
        Description: Returns a list containing the data present in a consecutive frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return fr[3][2:8]
        else:
            return fr[3][1:8]


    def _index_in_consecutive_frame(self, fr):
        '''
        Description: Returns the frame index present in a consecutive frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]

        Example: In frame [0x72E, 8, 0.505, [21 FF FF FF FF FF FF FF]], this method will return 0x21
        '''
        if EXTENDED_ADDRESSING:
            return fr[3][1]
        else:
            return fr[3][0]


    def _max_data_length_in_single_frame(self):
        '''
        Description: Returns max data length possible to store in a single frame
        '''
        if EXTENDED_ADDRESSING:
            return 6
        else:
            return 7


    def _first_frame_length(self, fr):
        '''
        Description: Returns length in a first frame response
        Parameter 'fr' is a frame with the struct: [id, dlc, flags, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return 0x100 * self._frame_data(fr, 1) + self._frame_data(fr, 2) - 0x1000
        else:
            return 0x100 * self._frame_data(fr, 0) + self._frame_data(fr, 1) - 0x1000


    def _first_frame_data_length(self):
        '''
        Description: Returns length in a first frame response
        '''
        if EXTENDED_ADDRESSING:
            return 5
        else:
            return 6


    def _consecutive_frame_data_length(self):
        '''
        Description: Returns length in a first frame response
        '''
        if EXTENDED_ADDRESSING:
            return 6
        else:
            return 7


    def _is_resp_first_frame(self, fr):
        '''
        Description: Checks if frame response fr is a multiple frame response.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if fr != []:
            return self._resp_length(fr) >= 0x10 and self._resp_length(fr) < 0x20
        else:
            return False


    def _is_resp_pending(self, fr):
        '''
        Description: Checks if frame response fr is response pending.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return self._frame_data(fr, 2) == 0x7F and self._frame_data(fr, 4) == 0x78
        else:
            return self._frame_data(fr, 1) == 0x7F and self._frame_data(fr, 3) == 0x78


    def _is_resp_fc(self, fr):
        '''
        Description: Checks if frame response fr is a flow control frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return self._frame_data(fr, 1) == 0x30
        else:
            return self._frame_data(fr, 0) == 0x30


    def _send_flow_control(self):
        '''
        Description: Writes flow control CTS (Continue To Send) CAN frame in the bus.
        '''
        if EXTENDED_ADDRESSING:
            self._req_canid = ID_BASE_ADDRESS + N_SA
            self._write_frame([N_TA_PHYSICAL, 0x30, TESTER_PARAM_BS, TESTER_PARAM_STMIN])
        else:
            self._req_canid = ID_PHYSICAL_REQ
            self._write_frame([0x30, TESTER_PARAM_BS, TESTER_PARAM_STMIN])


    def _get_bs_from_fc(self, fr):
        '''
        Description: Returns BS parameter in a Flow Control frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return self._frame_data(fr, 2)
        else:
            return self._frame_data(fr, 1)


    def _get_stmin_from_fc(self, fr):
        '''
        Description: Returns STmin parameter in a Flow Control frame.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if EXTENDED_ADDRESSING:
            return self._frame_data(fr, 3)
        else:
            return self._frame_data(fr, 2)


    def _write_frame(self, data):
        '''
        Description: Writes CAN frame in the bus, with data provided as parameter (list).
        CAN ID is the one stored in self._req_canid var, and DLC is the length of the data list parameter.
        This function waits also for the reception, and stores and prints the Rx frame.
        '''
        if DGN_SEND_8_BYTES:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        self._tp_restart = True
        time_start = time.clock()
        time_elapsed = 0.0
        self.write_can_frame(self._req_canid, len(data), data)
        fr = self.read_can_frame(self._req_canid)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.clock() - time_start
            fr = self.read_can_frame(self._req_canid)
        if fr != []:
            self._all_frames.append(fr)
            if self.print_frames == True:
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
        if EXTENDED_ADDRESSING:
            temp_id = ID_BASE_ADDRESS + N_TA_PHYSICAL
        else:
            temp_id = ID_PHYSICAL_RESP
        fr = self.read_can_frame(temp_id)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.clock() - time_start
            fr = self.read_can_frame(temp_id)
        if fr != []:
            self._all_frames.append(fr)
            self._resp_frames.append(fr)
            if self.print_frames == True:
                self._print_frame(self._all_frames[-1])

        return fr


    def _print_frame(self, fr):
        '''
        Description: Prints frame on screen, with the correct format.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        print self._format_frame(fr)


    def _convert_data_to_str(self, data):
        '''
        Description: Formats CAN data bytes so CAN frames are stored in the logfile as in CANOE logfiles.
        For example, integer 0x5a is returned as the string '5A'.
        '''
        temp_data = str(hex(data))
        temp_data = temp_data.upper()
        temp_data = temp_data.replace('0X','')
        if len(temp_data) == 1:
            temp_data = '0' + temp_data
        return temp_data


    def _convert_data_to_raw(self, data):
        '''
        Description: Formats data bytes to a string of hex numbers without '0X'.
        For example, integer [10 128 255] is returned as the string [0A 80 FF]
        '''
        return '[' + ' '.join([self._convert_data_to_str(item) for item in data]) + ']'


    def _format_timestamp(self, timestamp):
        '''
        Description: Formats a timestamp integer given by the CAN driver to a string in units=seconds.
        For example, timestamp 1237123072 is converted to '     1.218  '
        '''
        temp_t = float(timestamp)
        temp_t = temp_t / 1000000000.0
        temp_t = '%.3f' % temp_t
        temp_s = ' ' * (10 - len(temp_t)) + temp_t + '  '
        return temp_s


    def _format_frame(self, frame):
        '''
        Description: Formats CAN frames to be stored in the logfile similar as in CANOE logfiles.
        Parameter 'frame' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        # Format the CAN ID
        temp_id = str(hex(frame[0]))
        temp_id = temp_id.upper()
        temp_id = temp_id.replace('L','')
        temp_id = temp_id.replace('0X','')
        # Format de data bytes
        temp_s = self._format_timestamp(frame[2]) + temp_id + '  ' + str(frame[1]) + '  '
        dlc = frame[1]
        for i in range(dlc):
            temp_s += self._convert_data_to_str(frame[3][i]) + ' '
        return temp_s


    def _send_TP(self):
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
                    temp = self._req_canid
                    if EXTENDED_ADDRESSING:
                        self._req_canid = ID_BASE_ADDRESS + N_SA
                        tp_frame = [N_TA_FUNCTIONAL, 0x02, 0x3E, 0x80]
                    else:
                        self._req_canid = ID_FUNCTIONAL_REQ
                        tp_frame = [0x02, 0x3E, 0x80]
                    temp = self.print_frames
                    self.print_frames = False
                    self._write_frame(tp_frame)
                    self.print_frames = temp
                    self._req_canid = temp
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
        if EXTENDED_ADDRESSING:
            if self._ftype == 'FUNCTIONAL':
                fr_req.append(N_TA_FUNCTIONAL)
            else:
                fr_req.append(N_TA_PHYSICAL)
        fr_req.append(len(data))
        fr_req.extend(data)
        if NET_DEBUG: print 'SEND REQUEST SF'
        self._write_frame(fr_req)


    def _send_req_ff(self, data):
        '''
        Description: Sends first frame of a multiple frame request.
        Parameter 'data' is a list with the request contents.
        '''
        fr_req = []
        if EXTENDED_ADDRESSING:
            if self._ftype == 'FUNCTIONAL':
                fr_req.append(N_TA_FUNCTIONAL)
            else:
                fr_req.append(N_TA_PHYSICAL)
        tmp_b0_b1 = 0x1000 + len(data)
        fr_req.append(tmp_b0_b1 / 0x100)
        fr_req.append(tmp_b0_b1 % 0x100)
        self._cf_idx = 0x21
        for i in range(len(fr_req), 8):
            fr_req.append(data.pop(0))
        if NET_DEBUG: print 'SEND REQUEST FF'
        self._write_frame(fr_req)


    def _send_req_cf(self, data):
        '''
        Description: Sends consecutive frames of a multiple frame request.
        Parameter 'data' is a list with the request contents (must not contain the data already sent in the first frame).
        '''
        fr = self._wait_for_ecu_fc()
        if fr != []:
            bs = self._get_bs_from_fc(fr)
            stmin = self._get_stmin_from_fc(fr)
            # Send consecutive frames
            cf_index = 0
            while len(data) > self._consecutive_frame_data_length():
                if NET_DEBUG: print 'SEND REQUEST CF'
                fr_req = []
                if EXTENDED_ADDRESSING:
                    if self._ftype == 'FUNCTIONAL':
                        fr_req.append(N_TA_FUNCTIONAL)
                    else:
                        fr_req.append(N_TA_PHYSICAL)
                fr_req.append(self._cf_idx)
                for i in range(len(fr_req), 8):
                    fr_req.append(data.pop(0))
                self._write_frame(fr_req)
                cf_index = cf_index + 1
                if cf_index == bs:
                    cf_index = 0
                    # Wait for ECU Flow Control frame
                    if NET_DEBUG: print 'CHECK RESPONSE FC'
                    fr = self._wait_for_ecu_fc()
                    bs = self._get_bs_from_fc(fr)
                    stmin = self._get_stmin_from_fc(fr)
                self._cf_idx = self._cf_idx + 1
                if self._cf_idx == 0x30:
                    self._cf_idx = 0x20
                # Wait BS before sending next consecutive frame
                time.sleep(stmin * 0.001 + 0.0005)
            # Send last consecutive frame
            if NET_DEBUG: print 'SEND REQUEST LAST CF'
            fr_req = []
            if EXTENDED_ADDRESSING:
                if self._ftype == 'FUNCTIONAL':
                    fr_req.append(N_TA_FUNCTIONAL)
                else:
                    fr_req.append(N_TA_PHYSICAL)
            fr_req.append(self._cf_idx)
            fr_req.extend(data)
            self._write_frame(fr_req)


    def _manage_resp_pending(self, fr):
        '''
        Description: Manages response pending responses from the ECU. Basically waits until the final response is given by the ECU.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        if fr != [] and self._is_resp_pending(fr):
            if NET_DEBUG: print 'RESPONSE PENDING...'
            fr = self._read_frame()
            while self._is_resp_pending(fr):
                if NET_DEBUG: print 'RESPONSE PENDING...'
                fr = self._read_frame()
        return fr


    def _manage_multiple_frame_resp(self, fr):
        '''
        Description: Manages multiple response from the ECU. It takes the first frame 'fr' from the ECU, and generates
        flow control frames accordingly, until the total response from the ECU is completed.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        Returns True if received response was complete.
        '''
        # Store total length of the multi frame response.
        # For example, length is 2EB in frame: 12 EB 59 02 FF 9D 38 16
        self._resp_mf_length = self._first_frame_length(fr)
        self._resp_mf_length -= self._first_frame_data_length()
        # Send FC
        if NET_DEBUG: print 'SEND FLOW CONTROL'
        self._send_flow_control()
        # Check response CF
        cf_index = 0
        frame_index = 0x20
        ret_value = True
        if NET_DEBUG: print 'CHECK RESPONSE CF'
        while self._resp_mf_length > 0:
            fr = self._read_frame()
            if fr != []:
                frame_index += 1
                if frame_index == 0x30:
                    frame_index = 0x20
                if frame_index != self._index_in_consecutive_frame(fr):
                    ret_value = False
                self._resp_mf_length = self._resp_mf_length - self._consecutive_frame_data_length()
                cf_index = cf_index + 1
                if cf_index == TESTER_PARAM_BS:
                    cf_index = 0
                    # Send FC
                    if NET_DEBUG: print 'SEND FLOW CONTROL'
                    self._send_flow_control()
            else:
                return False
        if NET_DEBUG: print 'END OF RESPONSE'
        return ret_value


    def _wait_for_ecu_fc(self):
        '''
        Description: Waits for the flow control frame sent by the ECU (in case of a long request sent by this tool)
        '''
        # Wait for ECU Flow Control frame
        if NET_DEBUG: print 'CHECK RESPONSE FC'
        fr = self._read_frame()
        if fr == []:
            pass
        return fr


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
        temp_data = data

        if EXTENDED_ADDRESSING:
            self._req_canid = ID_BASE_ADDRESS + N_SA
        else:
            if self._ftype == 'FUNCTIONAL':
                self._req_canid = ID_FUNCTIONAL_REQ
            else:
                self._req_canid = ID_PHYSICAL_REQ

        # Clean up diagnostic frames rx buffer
        temp = self.print_frames
        self.print_frames = False
        self._rx_timer = 0.0
        fr = self._read_frame()
        while fr != []:
            fr = self._read_frame()
        self._rx_timer = RX_TIMEOUT
        self.print_frames = temp

        self._resp_frames = []

        self._req_log_idx_start = len(self._all_frames)

        if len(temp_data) <= self._max_data_length_in_single_frame():
            # Request must be sent in one single frame
            self._send_req_sf(temp_data)
            if not self.is_spr_req:
                # Check response
                if NET_DEBUG: print 'CHECK RESPONSE'
                fr = self._read_frame()
                fr = self._manage_resp_pending(fr)
                if self._is_resp_first_frame(fr):
                    if self._manage_multiple_frame_resp(fr) == False:
                        return []
        else:
            # Request must be sent in several frames
            self._send_req_ff(temp_data)
            self._send_req_cf(temp_data)
            if not self.is_spr_req:
                # Check response
                if NET_DEBUG: print 'CHECK RESPONSE'
                fr = self._read_frame()
                fr = self._manage_resp_pending(fr)
                if self._is_resp_first_frame(fr):
                    if self._manage_multiple_frame_resp(fr) == False:
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
            self.tp.join()
        if self._all_frames != []:
            f = open(self.log_file, 'w')
            for item in self._all_frames:
                f.writelines(self._format_frame(item) + '\n')
            f.close()


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
        str = '\n'
        for i in range(self._req_log_idx_start, self._req_log_idx_end):
            str = str + self._format_frame(self._all_frames[i]) + '\n'
        return str


    def req_info_raw(self):
        '''
        Description: Returns a string with the latest request + response raw data

        Example of string returned:
            Req:  [22 F1 88]
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
            self.tp = threading.Thread(target = self._send_TP)
            self.tp.daemon = True
            self.tp.start()


    def stop_periodic_tp(self):
        '''
        Description: Stops the transmission of periodic Tester Present frames.
        '''
        # Stop thread by setting self._tp_stop = True
        if self._tp_stop == False:
            self._tp_stop = True
            self.tp.join()


    def send_request(self, data, ftype='PHYSICAL'):
        '''
        Description: Sends DGN physical or functional request, with the data specified. Data can be of any length.
        Parameter 'ftype' can be 'PHYSICAL' or 'FUNCTIONAL'.
        This function will also send the network frames needed in the transport protocol. If there's some error detected
        in the network frames received from the ECU, the request will be retried. Max 5 retries will be performed.
        '''
        self._tx_semaphore.acquire()
        result = self._send_request_once(data, ftype)
        num_retries = 5
        while result == [] and num_retries != 0 and not self.is_spr_req:
            print '     Incomplete response detected, trying again...\n'
            result = self._send_request_once(data, ftype)
            num_retries -= 1
        if num_retries == 0:
            print '     Incomplete response detected, aborting retries\n'
            result = []

        # Store request and response in raw format, useful for reporting them
        self._last_resp_raw = self._convert_data_to_raw(result)
        self._last_req_raw = self._convert_data_to_raw(data)

        # Print raw request & response, with the timestamp
        if self.print_req_resp:
          if (result == []):
            if (self.is_spr_req):
              print self._format_timestamp(self._all_frames[-1][2]) + 'Req (SPR): ' + self._last_req_raw
            else:
              print self._format_timestamp(self._all_frames[-1][2]) + 'Req: ' + self._last_req_raw
              print self._format_timestamp(time.clock()) + 'No response after 5 attempts'
          else:
            i = self._all_frames.index(self._resp_frames[0])
            print self._format_timestamp(self._all_frames[i-1][2]) + 'Req: ' + self._last_req_raw
            print self._format_timestamp(self._resp_frames[0][2]) + 'Rsp: ' + self._last_resp_raw

          print ''

        self._tx_semaphore.release()
        return result
