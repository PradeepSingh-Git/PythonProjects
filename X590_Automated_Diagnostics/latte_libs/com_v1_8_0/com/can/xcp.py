'''
====================================================================
Library for working with XCP on CAN
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = 'Jesus Fidalgo'
__version__ = '1.0.0'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.0.0 Inital version
'''

import sys
import time
try:
    from xcp_cfg import *
except ImportError:
    print 'Configuration file xcp_cfg.py not found.'
    sys.exit()


class XCP():
    '''
    Class for sending & receiving XCP frames.
    '''

    ########################### PRIVATE FUNCTIONS ###########################

    def __init__(self):
        '''
        Description: Constructor
        '''
        # Public vars
        self.log_file = XCP_LOGFILE
        self.print_frames = True
        self.response = []
        # Private vars
        self._ag = 1 # address granularity
        self._rx_timer = 1.0
        self._all_frames = []
        self._resp_frames = []


    def _write_frame(self, data):
        '''
        Description: Writes CAN frame in the bus, with data provided as parameter.
        CAN ID is XCP_ID_RX, and DLC is the length of the data list parameter.
        This function waits also for the reception, and stores and prints the Rx frame.
        '''
        if XCP_SEND_8_BYTES:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        time_start = time.time()
        time_elapsed = 0.0
        self.write_can_frame(XCP_ID_RX, len(data), data)
        fr = self.read_can_frame(XCP_ID_RX)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.time() - time_start
            fr = self.read_can_frame(XCP_ID_RX)
        if fr != []:
            self._all_frames.append(fr)
            if self.print_frames == True:
                self._print_frame(self._all_frames[-1])
        else:
            print 'Not possible to send XCP request to the bus. Is ECU powered and running?'



    def _read_frame(self):
        '''
        Description: Reads XCP response frames in the bus. The function is blocking until a valid
        XCP response is received. It also stores and prints the Rx frame.
        '''
        time_start = time.time()
        time_elapsed = 0.0
        fr = self.read_can_frame(XCP_ID_TX)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.time() - time_start
            fr = self.read_can_frame(XCP_ID_TX)
        if fr != []:
            self._all_frames.append(fr)
            self._resp_frames.append(fr)
            if self.print_frames == True:
                self._print_frame(self._all_frames[-1])
        else:
            print 'Expecting a XCP response but nothing was received from the ECU. Is ECU running?\n'
        return fr



    def _frame_id(self, fr):
        '''
        Description: Returns frame identifier of frame 'fr'.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return fr[0]


    def _frame_data_list(self, fr):
        '''
        Description: Returns data list of frame 'fr', that is [b0, b1, b2, b3, b4, b5, b6, b7]
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return fr[3]


    def _frame_data(self, fr, i):
        '''
        Description: Returns data byte 'i' of the diagnostics response frame 'fr'.
        Parameter 'fr' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        return self._frame_data_list(fr)[i]


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


    def _format_frame(self, frame):
        '''
        Description: Formats CAN frames to be stored in the logfile similar as in CANOE logfiles.
        Parameter 'frame' is a frame with the struct: [id, dlc, time, [b0, b1, b2, b3, b4, b5, b6, b7]]
        '''
        # Format the timestamp
        temp_t = float(frame[2])
        temp_t = temp_t / 1000000000.0
        temp_t = '%.3f' % temp_t
        temp_s = ' ' * (10 - len(temp_t)) + temp_t + '  '
        # Format the CAN ID
        temp_id = str(hex(frame[0]))
        temp_id = temp_id.upper()
        temp_id = temp_id.replace('L','')
        temp_id = temp_id.replace('0X','')
        # Format de data bytes
        temp_s = temp_s + temp_id + '  '
        dlc = frame[1]
        for i in range(dlc):
            temp_s += self._convert_data_to_str(frame[3][i]) + ' '
        return temp_s


    def req_info(self):
        '''
        Description: Returns a string with the latest request + response

        Example:
            xcp=XCP()
            xcp.connect()
            print xcp.req_info()
        '''
        str = '\n'
        for i in range(self._req_log_idx_start, self._req_log_idx_end):
            str = str + self._format_frame(self._all_frames[i]) + '\n'
        return str


    def connect(self):
        '''
        Description: Sends CONNECT XCP command.

        Returns a list with the complete response
            byte 0      0xFF
            byte 1      RESOURCE
            byte 2      COMM_MODE_BASIC
            byte 3      MAX_CTO
            byte 4..5   MAX_DTO
            byte 6      XCP PROTOCOL LAYER VERSION
            byte 7      XCP TRANSPORT LAYER VERSION

        Example:
            xcp.connect()
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP CONNECT command'
        self._write_frame([0xFF, 0x00])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    # Calculation of AG (adress granularity) as specified in page 46 XCP -Part 2- Protocol Layer Specification -1.0.pdf
                    self._ag = self._frame_data(fr, 2) & 0x06
                    if self._ag == 2:
                        self._ag = 4
                    else:
                        self._ag += 1
                    print '     Positive response'
                    print '     RESOURCE =', hex(self._frame_data(fr, 1))
                    print '     COM_MODE_BASIC =', hex(self._frame_data(fr, 2))
                    print '     MAX_CTO =', str(self._frame_data(fr, 3))
                    print '     MAX_DTO =', str(0x100 * self._frame_data(fr, 4) + self._frame_data(fr, 5))
                    print '     XCP PROTOCOL LAYER VERSION =', hex(self._frame_data(fr, 6))
                    print '     XCP TRANSPORT LAYER VERSION =', hex(self._frame_data(fr, 7)), '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def disconnect(self):
        '''
        Description: Sends DISCONNECT XCP command.

        Returns a list with the complete response.

        Example:
            xcp.disconnect()
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP DISCONNECT command'
        self._write_frame([0xFE])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_status(self):
        '''
        Description: Sends GET_STATUS XCP command.

        Returns a list with the complete response
            byte 0      0xFF
            byte 1      Current session status
            byte 2      Current resource protection status
            byte 3      Reserved
            byte 4..5   Session configuration id
            byte 6..7   don't care

        Example:
            xcp.get_status()
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP GET_STATUS command'
        self._write_frame([0xFD])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response'
                    print '     Current session status =', hex(self._frame_data(fr, 1))
                    print '     Current resource protection status =', hex(self._frame_data(fr, 2))
                    print '     Session configuration id =', hex(0x100 * self._frame_data(fr, 4) + self._frame_data(fr, 5)), '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def synch(self):
        '''
        Description: Sends SYNCH XCP command.

        Returns a list with the complete response.

        Example:
            xcp.synch()
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP SYNCH command'
        self._write_frame([0xFC])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def set_mta(self, address, address_ext=0x00):
        '''
        Description: Sends SET_MTA XCP command.
        Parameter address contains the address to be set in MTA.

        Returns a list with the complete response.

        Example:
            xcp.set_mta(0x40002C78)
        '''
        d0 = (0x000000FF & address)
        d1 = (0x0000FF00 & address) >> 8
        d2 = (0x00FF0000 & address) >> 16
        d3 = (0xFF000000 & address) >> 24
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP SET_MTA command, MTA at address ' + hex(address).upper()
        self._write_frame([0xF6, 0x00, 0x00, address_ext, d3, d2, d1, d0])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def short_upload(self, data_elems, address, address_ext=0x00):
        '''
        Description: Sends SHORT_UPLOAD XCP command. This command is used for read a number of data elements 'data_elems' from address 'address'.
        Each data element is a byte, word o dword depending on AG parameter sent by the ECU in CONNECT command.
        Parameter data_elems contains the number of elements to be read.
        Parameter address contains the address of the vars to be read.

        Returns a list with the complete response.
            byte 0      0xFF
            byte 1..7   var contents

        Example 1:
            # if CONNECT command returned by the ECU contained AG=1 (byte access)
            result = xcp.short_upload(1, 0x40003CBC)
            print result[1]
        Example 2:
            # if CONNECT command returned by the ECU contained AG=2 (word access)
            result = xcp.short_upload(1, 0x40003CBC)
            print result[1:3]
        Example 3:
            # if CONNECT command returned by the ECU contained AG=4 (dword access)
            result = xcp.short_upload(1, 0x40003CBC)
            print result[1:5]
        '''
        d0 = (0x000000FF & address)
        d1 = (0x0000FF00 & address) >> 8
        d2 = (0x00FF0000 & address) >> 16
        d3 = (0xFF000000 & address) >> 24
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP SHORT_UPLOAD command, ' + str(data_elems) + ' elems of ' + str(self._ag) + ' bytes size at address ' + hex(address).upper()
        self._write_frame([0xF4, data_elems, 0x00, address_ext, d3, d2, d1, d0])
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def upload(self, data_elems):
        '''
        Description: Sends UPLOAD XCP command. This command, used together with SET_MTA command, is used
        for reading large amounts of data that doesn't fit in one XCP frame.
        A data block of number of data elements 'data_elems' will be read from MTA address.
        Each data element is a byte, word o dword depending on AG parameter sent by the ECU in CONNECT command.
        MTA is post-incremented by the ECU accordingly after each upload command.

        Returns a list with the complete response.

        Example:
            # Let's read 10 bytes from address 0x40002C78
            # First set MTA to the desired address to read data from
            xcp.set_mta(0x40002C78)
            # Read 10 bytes from address specified in MTA
            resp = xcp.upload(10)
            # If reading 10 bytes more, the ECU will get them from 0x40002C82 (0x40002C78 + 10)
            # because the ECU has post-incremented MTA accordingly
            resp = xcp.upload(10)
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP UPLOAD command, ' + str(data_elems) + ' elems of ' + str(self._ag) + ' bytes'
        self._write_frame([0xF5, data_elems])
        n_bytes = data_elems * self._ag + 1 # +1 for counting byte 0 0xFF
        if self._ag > 1:
            n_bytes += 1
        resp = []
        while n_bytes > 0:
            fr = self._read_frame()
            resp.extend(self._frame_data_list(fr))
            n_bytes -= len(self._frame_data_list(fr))

        if resp != []:
            if self.print_frames == True:
                if resp[0] == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return resp
        else:
            return resp


    def download(self, data_elems, data):
        '''
        Description: Sends DOWNLOAD XCP command. This command, used together with SET_MTA command, is used
        for writing small chunks of data.
        A data block of number of data elements 'data_elems' will be written in the configured MTA address.
        Each data element is a byte, word o dword depending on AG parameter sent by the ECU in CONNECT command.
        Parameter 'data' contains a list of elements.
        MTA is post-incremented by the ECU accordingly after each upload command.

        Returns a list with the complete response.

        Example:
            # Let's write 2 bytes at address 0x40002C78
            # First set MTA0 to the desired address to write data
            xcp.set_mta(0x40002C78)
            # If AG sent by the ECU in the CONNECT command is 1, writing 2 bytes would be:
            xcp.download(2, [0x01, 0x02])
            # MTA is automatically increased in 2 bytes, so we can continue writing data
            xcp.dnload(4, [0x03, 0x04, 0x05, 0x06])
            # If AG sent by the ECU in the CONNECT command is 2, writing 2 words would be:
            xcp.download(2, [0x1122, 0x3344])
        '''

        if data_elems * self._ag > 6:
            print 'XCP DOWNLOAD command in this library allows only to download data fitting in one CAN frame'
            return []

        # construct the request frame
        wr_frame = [0xF0, data_elems]
        if self._ag == 4:
            wr_frame.append(4)
        for item in data:
            if self._ag == 1:
                wr_frame.append(item)
            elif self._ag == 2:
                wr_frame.append((0xFF00 & item) >> 8)
                wr_frame.append(0x00FF & item)
            elif self._ag == 4:
                wr_frame.append((0xFF000000 & item) >> 24)
                wr_frame.append((0x00FF0000 & item) >> 16)
                wr_frame.append((0x0000FF00 & item) >> 8)
                wr_frame.append(0x000000FF & item)
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'XCP DOWNLOAD command, ' + str(data_elems) + ' elements of ' + str(self._ag) + ' bytes'
        self._write_frame(wr_frame)
        fr = self._read_frame()
        if fr != []:
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def save_logfile(self):
        '''
        Description: Writes frames to the logfile.

        Example:
            xcp=XCP()
            xcp.xonnect()
            xcp.save_logfile()
        '''
        if self._all_frames != []:
            f = open(self.log_file, 'w')
            for item in self._all_frames:
                f.writelines(self._format_frame(item) + '\n')
            f.close()
