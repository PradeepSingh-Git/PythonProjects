'''
====================================================================
Library for working with CCP
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = 'Jesus Fidalgo'
__version__ = '1.0.1'
__email__   = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.0.1 Bugfix in exchange_id method
1.0.0 Inital version
'''

import sys
import time
try:
    from ccp_cfg import *
except ImportError:
    print 'Configuration file ccp_cfg.py not found.'
    sys.exit()


class CCP():
    '''
    Class for sending & receiving CCP frames.
    '''

    ########################### PRIVATE FUNCTIONS ###########################

    def __init__(self):
        '''
        Description: Constructor
        '''
        # Public vars
        self.log_file = CCP_LOGFILE
        self.print_frames = True
        self.response = []
        # Private vars
        self._rx_timer = 1.0
        self._all_frames = []
        self._resp_frames = []
        self._ctr = 0


    def _write_frame(self, data):
        '''
        Description: Writes CAN frame in the bus, with data provided as parameter.
        CAN ID is CCP_ID_RX, and DLC is the length of the data list parameter.
        This function waits also for the reception, and stores and prints the Rx frame.
        '''
        if CCP_SEND_8_BYTES:
            zeroes = [0]*(8-len(data))
            data.extend(zeroes)
        time_start = time.time()
        time_elapsed = 0.0
        self.write_ccp_frame(CCP_ID_RX, len(data), data)
        fr = self.read_ccp_frame(CCP_ID_RX)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.time() - time_start
            fr = self.read_ccp_frame(CCP_ID_RX)
        if fr != []:
            self._all_frames.append(fr)
            if self.print_frames == True:
                self._print_frame(self._all_frames[-1])
        else:
            print 'Not possible to send CCP request to the bus. Is ECU powered and running?'



    def _read_frame(self):
        '''
        Description: Reads CCP response frames in the bus. The function is blocking until a valid
        CCP response is received. It also stores and prints the Rx frame.
        '''
        time_start = time.time()
        time_elapsed = 0.0
        fr = self.read_ccp_frame(CCP_ID_TX)
        while fr == [] and time_elapsed < self._rx_timer:
            time_elapsed = time.time() - time_start
            fr = self.read_ccp_frame(CCP_ID_TX)
        if fr != []:
            self._all_frames.append(fr)
            self._resp_frames.append(fr)
            if self.print_frames == True:
                self._print_frame(self._all_frames[-1])
        else:
            print 'Expecting a CCP response but nothing was received from the ECU. Is ECU running?\n'
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
            ccp=CCP()
            ccp.connect()
            print ccp.req_info()
        '''
        str = '\n'
        for i in range(self._req_log_idx_start, self._req_log_idx_end):
            str = str + self._format_frame(self._all_frames[i]) + '\n'
        return str


    def connect(self):
        '''
        Description: Sends CONNECT CCP command.
        The slave Station Addess sent is taken from ccp_config.py file.

        Returns a list with the complete response (8 data bytes)
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   don't care

        Example:
            ccp=CCP()
            ccp.connect()
        '''
        s0 = (0x000000FF & CCP_STATION_ADDRESS)
        s1 = (0x0000FF00 & CCP_STATION_ADDRESS) >> 8
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP CONNECT command'
        self._write_frame([0x01, self._ctr, s0, s1])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def disconnect(self, disc_type):
        '''
        Description: Sends DISCONNECT CCP command.
        Parameter disc_type contains the disconnection type:
            0x00 = Temporary
            0x01 = End of session
        The slave Station Addess sent is taken from ccp_config.py file.

        Returns a list with the complete response (8 data bytes)
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   don't care

        Example:
            ccp=CCP()
            ccp.disconnect(0x01)
        '''
        s0 = (0x000000FF & CCP_STATION_ADDRESS)
        s1 = (0x0000FF00 & CCP_STATION_ADDRESS) >> 8
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP DISCONNECT command,',
            if disc_type == 0x00:
                print 'temporary'
            else:
                print 'end of session'
        self._write_frame([0x07, self._ctr, disc_type, 0x00, s0, s1])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_ccp_version(self, version_list):
        '''
        Description: Sends GET_CCP_VERSION CCP command.
        Parameter version_list contains a list with the desired CCP version, for example [0x02, 0x01] for CCP v2.1

        Returns a list with the complete response (8 data bytes)
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..4   implemented CCP version
            byte 5..7   don't care

        Example:
            ccp=CCP()
            ccp.get_ccp_version([0x02, 0x01])
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP GET_CCP_VERSION command'
        self._write_frame([0x1B, self._ctr, version_list[0], version_list[0]])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Postive response:', self._convert_data_to_str(self._frame_data(fr, 3)), self._convert_data_to_str(self._frame_data(fr, 4)), '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def short_up(self, var_size, var_address):
        '''
        Description: Sends SHORT_UP CCP command. This command is used for read T_u32, T_u16 and T_u8 vars.
        Parameter var_size contains the size of the var to be read (max 5 bytes)
        Parameter var_address contains the address of the var to be read.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   var contents

        Example:
            ccp=CCP()
            result = ccp.short_up(1, 0x40003CBC)
            print result[3]
        '''
        if var_size > 5:
            var_size = 5
        d0 = (0x000000FF & var_address)
        d1 = (0x0000FF00 & var_address) >> 8
        d2 = (0x00FF0000 & var_address) >> 16
        d3 = (0xFF000000 & var_address) >> 24
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP SHORT_UP command, ' + str(var_size) + ' bytes at address ' + hex(var_address).upper()
        self._write_frame([0x0F, self._ctr, var_size, 0x00, d3, d2, d1, d0])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    resp = []
                    print '     Positive response:',
                    for i in range(var_size):
                        resp.append(self._frame_data(fr, 3+i))
                        print self._convert_data_to_str(self._frame_data(fr, 3+i)),
                    print '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def set_mta(self, mta, var_address):
        '''
        Description: Sends SET_MTA CCP command.
        Parameter mta must be set to 0 for setting MTA0, or 1 for setting MTA1.
        Parameter var_address contains the address to be set in MTA.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   don't care

        Example:
            ccp=CCP()
            ccp.set_mta(0, 0x40002C78)
        '''
        d0 = (0x000000FF & var_address)
        d1 = (0x0000FF00 & var_address) >> 8
        d2 = (0x00FF0000 & var_address) >> 16
        d3 = (0xFF000000 & var_address) >> 24
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP SET_MTA command, MTA' + str(mta) + ' at address ' + hex(var_address).upper()
        self._write_frame([0x02, self._ctr, mta, 0x00, d3, d2, d1, d0])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def upload(self, num_bytes):
        '''
        Description: Sends UPLOAD CCP command. This command, used together with SET_MTA command, is used
        for reading chunks of data longer than 4 bytes. A data block of the specified length (num_bytes),
        starting at current MTA0, will be read. The MTA0 pointer will be post-incremented by the value of num_bytes.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   requested data bytes

        Example:
            ccp=CCP()
            # Let's read 8 bytes from address 0x40002C78
            # First set MTA0 to the desired address to read data from
            ccp.set_mta(0, 0x40002C78)
            # Read 4 bytes from address specified in MTA0
            res_1 = ccp.upload(4)
            # MTA0 is automatically increased in 4 bytes, so we can continue reading data
            res_2 = ccp.upload(4)
        '''
        if num_bytes > 5:
            num_bytes = 5
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP UPLOAD command, ' + str(num_bytes) + ' bytes'
        self._write_frame([0x04, self._ctr, num_bytes])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    resp = []
                    print '     Positive response:',
                    for i in range(num_bytes):
                        resp.append(self._frame_data(fr, 3+i))
                        print self._convert_data_to_str(self._frame_data(fr, 3+i)),
                    print '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def dnload(self, data_bytes):
        '''
        Description: Sends DNLOAD CCP command. This command, used together with SET_MTA command, is used
        for writing small chunks of data. Parameter data_bytes contains the list of the data to be written,
        maximum 5 bytes. Each DNLOAD command can write maximum 5 data bytes. The data block
        of the specified length (data_bytes length) will be copied into memory, starting at the current
        Memory Transfer Address 0 (MTA0). The MTA0 pointer will be post-incremented by the value of the
        length of data_bytes.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3      don't care
            byte 4..7   MTA0 address (after post-increment)

        Example:
            ccp=CCP()
            # Let's write 10 bytes at address 0x40002C78
            # First set MTA0 to the desired address to write data
            ccp.set_mta(0, 0x40002C78)
            # Write 5 bytes from address specified in MTA0
            ccp.dnload([0x01, 0x02, 0x03, 0x04, 0x05])
            # MTA0 is automatically increased in 5 bytes, so we can continue writing data
            ccp.dnload([0x06, 0x07, 0x08, 0x09, 0x0A])
        '''
        data_length = len(data_bytes)
        if data_length > 5:
            data_length = 5
        wr_frame = [0x03, self._ctr, data_length]
        for i in range(data_length):
            wr_frame.append(data_bytes[i])
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP DNLOAD command, ' + str(data_length) + ' bytes'
        self._write_frame(wr_frame)
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def dnload_6(self, data_bytes):
        '''
        Description: Sends DNLOAD_6 CCP command. This command, used together with SET_MTA command, is used
        for writing small chunks of data. It's faster that DNLOAD command, which can only write 5 bytes maximum.
        Parameter data_bytes contains the list of the data to be written, and must 6 exactly 6 bytes long.
        Each DNLOAD_6 command can write exactly 6 5 data bytes. The data block data_bytes will be copied
        into memory, starting at the current Memory Transfer Address 0 (MTA0). The MTA0 pointer will be
        post-incremented by 6.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3      don't care
            byte 4..7   MTA0 address (after post-increment)

        Example:
            ccp=CCP()
            # Let's write 12 bytes at address 0x40002C78
            # First set MTA0 to the desired address to write data
            ccp.set_mta(0, 0x40002C78)
            # Write 6 bytes from address specified in MTA0
            ccp.dnload_6([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
            # MTA0 is automatically increased in 6 bytes, so we can continue writing data
            ccp.dnload([0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C])
            # Note that using DNLOAD command instead of DNLOAD_6, 3 request would have been needed
        '''
        data_length = len(data_bytes)
        if data_length > 6:
            data_length = 6
        wr_frame = [0x23, self._ctr]
        for i in range(data_length):
            wr_frame.append(data_bytes[i])
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP DNLOAD_6 command, ' + str(data_length) + ' bytes'
        self._write_frame(wr_frame)
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_cal_seed(self):
        '''
        Description: Sends GET_SEED CCP command requesting a seed for CAL resource.
        For downloading data to the slave, DNLOAD and DNLOAD_6 commands usage can be protected with
        a seed&key algorithm. In CCP, there are 3 resources: CAL, PGM and DAQ. CAL resource is the
        one linked with DNLOAD and DNLOAD_6 commands.

        Returns seed data for a seed&key algorithm for computing the key to unlock CAL resource.
        If protection status = FALSE, no UNLOCK is required to unlock the CAL resource.
        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3      protection status (1 = TRUE or 0 = FALSE)
            byte 4..7   seed data

        Example:
            ccp=CCP()
            res = ccp.get_cal_seed()
                if res[3] == 0x01:
                    # CAL resource protected, read seed
                    seed = res[4:7]
                    # Calculate key using a specific seed&key algorithm
                    key = calc_key(seed)
                    # Unlock CAL resource
                    ccp.unlock(key)
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP GET_SEED command, requesting CAL resource'
        self._write_frame([0x12, self._ctr, 0x01])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response:',
                    resp = []
                    if self._frame_data(fr, 3) == 0x01:
                        print 'CAL resource protected, seed:',
                        for i in range(4,8):
                            print self._convert_data_to_str(self._frame_data(fr, i)),
                    else:
                        print 'CAL resource not protected',
                    print '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def unlock(self, key):
        '''
        Description: Sends UNLOCK CCP command, requesting ato unlock a resource requested with GET_SEED command.
        For downloading data to the slave, DNLOAD and DNLOAD_6 commands usage can be protected with
        a seed&key algorithm. In CCP, there are 3 resources: CAL, PGM and DAQ. CAL resource is the
        one linked with DNLOAD and DNLOAD_6 commands.
        Parameter key contains a list with the key, max 6 bytes long.

        Returns the current resource mask. It's a byte with the following bits:
            bit 7       not used
            bit 6       PGM resource (used for programming FLASH and EEPROM in the slave)
            bit 5       not used
            bit 4       not used
            bit 3       not used
            bit 2       not used
            bit 1       DAQ resource (used for requesting periodic data from the slave)
            bit 0       CAL resource (used for writing data into the slave)

        If protection status = FALSE, no UNLOCK is required to unlock the CAL resource.
        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3      current resource mask
            byte 4..7   don't care

        Example:
            ccp=CCP()
            res = ccp.get_cal_seed()
                if res[3] == 0x01:
                    # CAL resource protected, read seed
                    seed = res[4:7]
                    # Calculate key using a specific seed&key algorithm
                    key = calc_key(seed)
                    # Unlock CAL resource
                    ccp.unlock(key)
        '''
        wr_frame = [0x13, self._ctr]
        for i in range(len(key)):
            wr_frame.append(key[i])
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP UNLOCK command, key', self._convert_data_to_str(key[0]), self._convert_data_to_str(key[1]), self._convert_data_to_str(key[2]), self._convert_data_to_str(key[3])
        self._write_frame(wr_frame)
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response:',
                    if fr[4][3] & 0x01 != 0x00:
                        print 'CAL resource enabled',
                    if fr[4][3] & 0x02 != 0x00:
                        print 'DAQ resource enabled',
                    if fr[4][3] & 0x40 != 0x00:
                        print 'PGM resource enabled',
                    print '\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def move(self, num_bytes):
        '''
        Description: Sends MOVE CCP command. A data block of the specified length (num_bytes) will be copied
        from the address defined by MTA 0 (source pointer) to the address defined by MTA 1 (destination pointer).

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3..7   don't care

        Example:
            ccp=CCP()
            ccp.set_mta(0, 0x40002C78)
            ccp.set_mta(1, 0x40002C7C)
            ccp.move(3)
        '''
        n0 = (0x000000FF & num_bytes)
        n1 = (0x0000FF00 & num_bytes) >> 8
        n2 = (0x00FF0000 & num_bytes) >> 16
        n3 = (0xFF000000 & num_bytes) >> 24
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP MOVE command,', str(num_bytes), 'bytes to move'
        self._write_frame([0x19, self._ctr, n3, n2, n1, n0])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def exchange_id(self, master_id = []):
        '''
        Description: Sends EXCHANGE_ID CCP command. The CCP master and slave stations can
        exchange IDs for automatic session configuration. It's optional to send the master ID
        in the EXCHANGE_ID command.

        Returns a list with the complete response (8 data bytes).
            byte 0      0xFF
            byte 1      command return code
            byte 2      CTR
            byte 3      length of the slave ID in bytes
            byte 4      data type of the slave ID (optional and specific)
            byte 5      resource availability mask
            byte 6      resource protection mask
            byte 7      don't care

        Resource masks is a byte with the following bits:
            bit 7       not used
            bit 6       PGM resource (used for programming FLASH and EEPROM in the slave)
            bit 5       not used
            bit 4       not used
            bit 3       not used
            bit 2       not used
            bit 1       DAQ resource (used for requesting periodic data from the slave)
            bit 0       CAL resource (used for writing data into the slave)

        Example:
            ccp=CCP()
            ccp.exchange_id()
        '''
        wr_frame = [0x17, self._ctr]
        for i in range(len(master_id)):
            wr_frame.append(master_id[i])
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP EXCHANGE_ID command'
        self._write_frame(wr_frame)
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response:',
                    print 'slave ID length', self._frame_data(fr, 3), 'bytes',
                    print 'resource availability:',
                    if self._frame_data(fr, 5) & 0x01 != 0x00:
                        print 'CAL',
                    if self._frame_data(fr, 5) & 0x02 != 0x00:
                        print 'DAQ',
                    if self._frame_data(fr, 5) & 0x40 != 0x00:
                        print 'PGM',
                    print ', resource protection:',
                    if self._frame_data(fr, 6) & 0x01 != 0x00:
                        print 'CAL',
                    if self._frame_data(fr, 6) & 0x02 != 0x00:
                        print 'DAQ',
                    if self._frame_data(fr, 6) & 0x40 != 0x00:
                        print 'PGM',
                    print '\n'

                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def select_cal_page(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP SELECT_CAL_PAGE command'
        self._write_frame([0x11, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_daq_size(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP GET_DAQ_SIZE command'
        self._write_frame([0x14, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def set_daq_ptr(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP SET_DAQ_PTR command'
        self._write_frame([0x15, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def write_daq(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP WRITE_DAQ command'
        self._write_frame([0x16, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def start_stop(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP START_STOP command'
        self._write_frame([0x06, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def set_s_status(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP SET_S_STATUS command'
        self._write_frame([0x0C, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_s_status(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP GET_S_STATUS command'
        self._write_frame([0x0D, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def build_chksum(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP BUILD_CHKSUM command'
        self._write_frame([0x0E, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def clear_memory(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP CLEAR_MEMORY command'
        self._write_frame([0x10, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def program(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP PROGRAM command'
        self._write_frame([0x18, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def program_6(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP PROGRAM_6 command'
        self._write_frame([0x22, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def diag_service(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP DIAG_SERVICE command'
        self._write_frame([0x20, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def action_service(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP ACTION_SERVICE command'
        self._write_frame([0x21, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def test(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP TEST command'
        self._write_frame([0x05, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def start_stop_all(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP START_STOP_ALL command'
        self._write_frame([0x08, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
                    print '     Positive response\n'
                else:
                    print '     Negative response\n'
            self._req_log_idx_end = len(self._all_frames)
            return self._frame_data_list(fr)
        else:
            return fr


    def get_active_cal_page(self):
        '''
        Not implemented
        '''
        self._req_log_idx_start = len(self._all_frames)
        if self.print_frames == True:
            print 'CCP GET_ACTIVE_CAL_PAGE command'
        self._write_frame([0x09, self._ctr])
        fr = self._read_frame()
        if fr != []:
            self._ctr = self._ctr + 1
            if self.print_frames == True:
                if self._frame_data(fr, 0) == 0xFF and self._frame_data(fr, 1) == 0x00:
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
            ccp=CCP()
            ccp.connect()
            ccp.save_logfile()
        '''
        if self._all_frames != []:
            f = open(self.log_file, 'w')
            for item in self._all_frames:
                f.writelines(self._format_frame(item) + '\n')
            f.close()
