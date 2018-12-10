'''
====================================================================
Library for ISO 14229 UDS (Unified Diagnostic Services)
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = "Jesus Fidalgo"
__version__ = "1.4.0"
__email__   = "jfidalgo@lear.com"

'''
CHANGE LOG
==========
1.4.0 Added service_0x85
1.3.0 Method req_info_raw added
1.2.1 Bugfix in service_0x3E
1.2.0 Added services 0x23
1.1.0 Added services 0x2C and 0x2A
1.0.0 Inital version
'''

from iso15765_2 import *
from iso10681_2 import *


class ISO14229():
    '''
    Implements ISO 14229 requests & responses.
    '''

    def __init__(self, bus_type="CAN"):
        '''
        Description: Constructor
        '''
        if bus_type == "CAN":
            self.net = ISO15765_2()
        elif bus_type == "FLEXRAY":
            self.net = ISO10681_2()
        else:
            print 'Error during DGN ISO loading... check bus type used.'
            sys.exit()
        self._reqtype = 'PHYSICAL'


    def save_logfile(self):
        '''
        Description: Saves diagnostics CAN traffic to a log file.
        Should be called just before ending the script (so all frames are saved)

        Example:
            dgn=ISO14229()
            dgn.service_0x10(0x01)
            dgn.save_logfile()
        '''
        self.net.save_logfile()


    def req_info(self):
        '''
        Description: Returns a string with latest request + response(s), like a mini logfile.
        Useful for printing this info in a report.

        Example:
            dgn=ISO14229()
            dgn.service_0x22([0xF1, 0x88])
            print dgn.req_info()

            This will print:
            1.209  726  8  03 22 F1 88 00 00 00 00
            1.228  72E  8  10 1B 62 F1 88 47 58 37
            1.229  726  8  30 00 0A 00 00 00 00 00
            1.238  72E  8  21 33 2D 31 34 43 31 38
            1.248  72E  8  22 34 2D 41 41 31 32 00
            1.258  72E  8  23 00 00 00 00 00 00 00
        '''
        return self.net.req_info()


    def req_info_raw(self):
        '''
        Description: Returns a string with latest request + response(s), like a mini logfile.
        Useful for printing this info in a report.

        Example:
            dgn=ISO14229()
            dgn.service_0x22([0xF1, 0x88])
            print dgn.req_info()

            This will print:
            Request:  [22 F1 88]
            Response: [62 F1 88 47 58 37 33 2D 31 34 43 31 38 34 2D 41 41 31 32 00 00 00 00 00 00 00 00]
        '''
        return self.net.req_info_raw()


    def start_periodic_tp(self):
        '''
        Description: Starts the transmission of periodic Tester Present frames.
        Period is defined in parameter TESTER_PRESENT_PERIOD in dgncan_cfg.py or dgnflex_cfg.py files.
        Tester Present frames will be sent strictly when needed. Diagnostic requests resets the
        TESTER_PRESENT_PERIOD timer, so Tester Present frames will be only sent if a diagnostics
        inactivity period of TESTER_PRESENT_PERIOD happens.

        Example:
            dgn=ISO14229()
            dgn.start_periodic_tp()
        '''
        self.net.start_periodic_tp()


    def stop_periodic_tp(self):
        '''
        Description: Stops the transmission of periodic Tester Present frames.

        Example:
            dgn=ISO14229()
            dgn.start_periodic_tp()
            ...
            dgn.stop_periodic_tp()
        '''
        self.net.stop_periodic_tp()


    def use_physical_requests(self):
        '''
        Description: Switches diagnostic requests to use physical requests

        Example:
            dgn=ISO14229()
            dgn.use_physical_requests()
        '''
        self._reqtype   = 'PHYSICAL'


    def use_functional_requests(self):
        '''
        Description: Switches diagnostic requests to use functional requests

        Example:
            dgn=ISO14229()
            dgn.use_functional_requests()
        '''
        self._reqtype   = 'FUNCTIONAL'


    def service_0x10(self, diag_session_type):
        '''
        Description: DiagnosticSessionControl service.
        Parameter diagnosticsessiontype contains the desired session.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x10(0x81)
        '''
        self.net.is_spr_req = False
        if (diag_session_type & 0x80):
            self.net.is_spr_req = True
        return self.net.send_request([0x10, diag_session_type], self._reqtype)


    def service_0x11(self, resettype):
        '''
        Description: ECUReset service.
        Parameter resettype contains the desired reset type.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x11(0x01)
        '''
        self.net.is_spr_req = False
        if (resettype & 0x80):
            self.net.is_spr_req = True
        return self.net.send_request([0x11, resettype], self._reqtype)


    def service_0x14(self, group_of_DTC):
        '''
        Description: ClearDiagnosticInformation service.
        Parameter group_of_DTC contains a list with 3 bytes.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x14([0xFF, 0xFF, 0xFF])
        '''
        self.net.is_spr_req = False
        return self.net.send_request([0x14, group_of_DTC[0], group_of_DTC[1], group_of_DTC[2]], self._reqtype)


    def service_0x19(self, data_list):
        '''
        Description: ReadDTCInformation service.
        Parameter data_list contains a list with subfunction and all the rest of params.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x19([0x02, 0x08]) # reportDTCByStatusMask
            dgn.service_0x19([0x0A]) # reportSupportedDTC
        '''
        if (data_list[0] & 0x80):
            self.net.is_spr_req = True
        templist = [[0x19], data_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x22(self, did_list):
        '''
        Description: ReadDataByIdentifier service.
        For one DID requested, for example 0xF180, did_list must be [0xF1, 0x80]
        For multiple DIDs requested, for example 0xF180 and 0xD100, did_list must be [0xF1, 0x80, 0xD1, 0x00]
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x22([0xD1, 0x00]) # DID 0xD100
        '''
        self.net.is_spr_req = False
        templist = [[0x22], did_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x23(self, address_length_format, addr_list, size_list):
        '''
        Description: ReadMemoryByAddress service.
        Parameter address_length_format is one byte, bits 7-4 length (number of bytes) of the size parameter,
        bits 3-0 length (number of bytes) of the address parameter
        The address requested in list format, for example 0x40000000, must be [0x40, 0x00, 0x00, 0x00]
        The size requested in list format, for example 0x0010, must be [0x00, 0x10]
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            # reading 10 bytes from 0x40000000
            dgn.service_0x23(0x24, [0x40, 0x00, 0x00, 0x00], [0x00, 0x0A])
        '''
        self.net.is_spr_req = False
        templist = [[0x23], [address_length_format], addr_list, size_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x2E(self, did, data_list):
        '''
        Description: WriteDataByIdentifier service.
        For example for DID 0xF180, parameter did must be [0xF1, 0x80]
        Parameter data_list must contain bytes: [0x11, 0x22, ...]
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x2E([0x40, 0x94], [0x00, 0x00, 0x00, 0x00, 0x00]) # DID 0x4094, write 5 bytes
        '''
        self.net.is_spr_req = False
        templist = [[0x2E], did, data_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x27(self, access_type, data_list=[]):
        '''
        Description: SecurityAccess service.
        Parameter access_type is on byte with the sub-function.
        Parameter data_list is optional, is a list containing securityAccessDataRecord.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x27(0x01) # Enter Security Access level 0x01
        '''
        self.net.is_spr_req = False
        if (access_type & 0x80):
            self.net.is_spr_req = True
        templist = [[0x27], [access_type], data_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x2A(self, rate, did):
        '''
        Description: ReadDataByPeriodicIdentifer service.
        Parameter rate is a the data rate.
        Parameter did is a list with the data record(s) that are being requested.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x2A(0x01, [0x01, 0x02]) # Enter Security Access level 0x01
        '''
        self.net.is_spr_req = False
        templist = [[0x2A], [rate], did]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x2C(self, data_list):
        '''
        Description: DynamicallyDefineDataIdentifier service.
        Parameter data_list contains a list with subfunction and all the rest of params.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x2C([0x01, 0xF2, 0x00, 0xF1, 0x80, 0x01, 0x01])
        '''
        self.net.is_spr_req = False
        templist = [[0x2C], data_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x2F(self, did, control_option, control_enable_mask=[]):
        '''
        Description: InputOutputControlByIdentifier service.
        Parameter did is a list of bytes with the DID.
        Parameter control_option is a list.
        Parameter control_enable_mask is an optional list.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x2F([0x40, 0x68], [0x03], [0x99])
            dgn.service_0x2F([0x40, 0x68], [0x00])
        '''
        self.net.is_spr_req = False
        templist = [[0x2F], did, control_option, control_enable_mask]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x31(self, sub_function, did, control_option=[]):
        '''
        Description: RoutineControl service.
        Parameter sub_function is one byte.
        Parameter did is a list of bytes with the DID.
        Parameter control_option is a list, optional. Only used if the routine has input parameters.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x31([0x20, 0x1B], [0x00, 0x07])
        '''
        self.net.is_spr_req = False
        if (sub_function & 0x80):
            self.net.is_spr_req = True
        templist = [[0x31], [sub_function], did, control_option]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x34(self, data_format, address_length_format, memory_address_list, memory_size_list):
        '''
        Description: RequestDownload service.
        Parameter data_format is one byte.
        Parameter address_length_format is one byte.
        Parameter memory_address_list is a list of bytes with the memory address.
        Parameter memory_size_list is a list of bytes with the memory size.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x34(0x00, 0x44, [0x00, 0x04, 0x00, 0x00], [0x00, 0x00, 0x10, 0x00])
        '''
        self.net.is_spr_req = False
        templist = [[0x34], [data_format], [address_length_format], memory_address_list, memory_size_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x36(self, block_seq_counter, data_list):
        '''
        Description: TransferData service.
        Parameter block_seq_counter is one byte.
        Parameter data_list is a list with data bytes.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x36(0x01, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        '''
        self.net.is_spr_req = False
        templist = [[0x36], [block_seq_counter], data_list]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x37(self, transfer_request_param=[]):
        '''
        Description: RequestTransferExit service.
        Parameter transfer_request_param is optional.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x37()
        '''
        self.net.is_spr_req = False
        templist = [[0x37], transfer_request_param]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)


    def service_0x3E(self, zero_subfunction):
        '''
        Description: ECUReset service.
        Parameter zero_subfunction is one byte with 0x00 or 0x80.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x3E(0x80)
        '''
        self.net.is_spr_req = False
        if (zero_subfunction & 0x80):
            self.net.is_spr_req = True
        return self.net.send_request([0x3E, zero_subfunction], self._reqtype)


    def service_0x85(self, dtc_setting_type, control_option=[]):
        '''
        Description: ControlDTCSetting service.
        Parameter dtc_setting_type is a byte with the sub-function.
        Parameter control_option is a list, optional, with the contents of parameter DTCSettingControlOptionRecord.
        Returns: list of bytes with the ECU response.

        Example:
            dgn=ISO14229()
            dgn.service_0x85(0x00)
        '''
        self.net.is_spr_req = False
        templist = [[0x85], [dtc_setting_type], control_option]
        rawlist = [item for sublist in templist for item in sublist]
        return self.net.send_request(rawlist, self._reqtype)
