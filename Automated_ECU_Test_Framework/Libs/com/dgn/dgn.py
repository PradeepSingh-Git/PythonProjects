'''
====================================================================
Implements customer spec for Diagnostics
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__ = 'Jesus Fidalgo'
__version__ = '1.3.0'
__email__ = 'jfidalgo@lear.com'

'''
CHANGE LOG
==========
1.3.0 Added method set_number_of_requests_retries, solved some pylint issues
1.2.0 Added method control_dtc_setting
1.1.0 Method req_info_raw added
1.0.1 Bugfix in security_access method
1.0.0 Inital version
'''

from iso14229 import *
from ctypes import *
from math import *


SECURITY_CONSTANTS = {
    0x01: [0xF5, 0xDE, 0x0E, 0xF2, 0x5D],
    0x05: [0x4A, 0x4F, 0x4E, 0x41, 0x53],
}

class _u24_bits(Structure):
    _pack_ = 1
    _fields_ = [ \
        ("b16", c_ubyte, 1),
        ("b17", c_ubyte, 1),
        ("b18", c_ubyte, 1),
        ("b19", c_ubyte, 1),
        ("b20", c_ubyte, 1),
        ("b21", c_ubyte, 1),
        ("b22", c_ubyte, 1),
        ("b23", c_ubyte, 1),
        ("b8", c_ubyte, 1),
        ("b9", c_ubyte, 1),
        ("b10", c_ubyte, 1),
        ("b11", c_ubyte, 1),
        ("b12", c_ubyte, 1),
        ("b13", c_ubyte, 1),
        ("b14", c_ubyte, 1),
        ("b15", c_ubyte, 1),
        ("b0", c_ubyte, 1),
        ("b1", c_ubyte, 1),
        ("b2", c_ubyte, 1),
        ("b3", c_ubyte, 1),
        ("b4", c_ubyte, 1),
        ("b5", c_ubyte, 1),
        ("b6", c_ubyte, 1),
        ("b7", c_ubyte, 1)]

class _u24_bytes(Structure):
    _pack_ = 1
    _fields_ = [
        ("high", c_ubyte),
        ("mid", c_ubyte),
        ("low", c_ubyte)]

class _u24(Union):
    _pack_ = 1
    _fields_ = [
        ("bits", _u24_bits),
        ("bytes", _u24_bytes)]



class DGN(object):
    '''
    Implements the specific customer diagnostics requirements.
    '''

    def __init__(self, bus_type="CAN"):
        '''
        Description: Constructor
        '''
        self.iso = ISO14229(bus_type)
        self.print_service = True


    ############ General ############

    def save_logfile(self):
        '''
        Description: Saves diagnostics CAN traffic to a log file. Log file name is configured in dgncan_cfg.py or dgnflex.py
        Should be called just before ending the script (so all frames are saved)

        Example:
            dgn.default_session()
            dgn.save_logfile()
        '''
        self.iso.save_logfile()


    def req_info(self):
        '''
        Description: Returns a string with latest request + response(s), like a mini logfile.
        Useful for printing this info in a report.

        Example:
            dgn.read_did(0xF188)
            print dgn.req_info()

            This will print:
            1.209  726  8  03 22 F1 88 00 00 00 00
            1.228  72E  8  10 1B 62 F1 88 47 58 37
            1.229  726  8  30 00 0A 00 00 00 00 00
            1.238  72E  8  21 33 2D 31 34 43 31 38
            1.248  72E  8  22 34 2D 41 41 31 32 00
            1.258  72E  8  23 00 00 00 00 00 00 00
        '''
        return self.iso.req_info()


    def req_info_raw(self):
        '''
        Description: Returns a string with latest request + response(s), like a mini logfile.
        Useful for printing this info in a report.

        Example:
            dgn.read_did(0xF188)
            print dgn.req_info()

            This will print:
            Request:  [22 F1 88]
            Response: [62 F1 88 47 58 37 33 2D 31 34 43 31 38 34 2D 41 41 31 32 00 00 00 00 00 00 00 00]
        '''
        return self.iso.req_info_raw()


    def set_number_of_requests_retries(self, retries):
        '''
        Description: Configures the number of requests retries in case of no response.

        Example:
            dgn.set_number_of_requests_retries(0)
        '''
        self.iso.net.num_retries_request = retries



    ############ Tester Present ############

    def start_periodic_tp(self):
        '''
        Description: Starts the transmission of periodic Tester Present frames.
        Period is defined in parameter TESTER_PRESENT_PERIOD in dgncan_cfg.py or dgnflex_cfg.py files.
        Tester Present frames will be sent strictly when needed. Diagnostic requests resets the
        TESTER_PRESENT_PERIOD timer, so Tester Present frames will be only sent if a diagnostics
        inactivity period of TESTER_PRESENT_PERIOD happens.

        Example:
            dgn.start_periodic_tp()
        '''
        self.iso.start_periodic_tp()


    def stop_periodic_tp(self):
        '''
        Description: Stops the transmission of periodic Tester Present frames.

        Example:
            dgn.stop_periodic_tp()
        '''
        self.iso.stop_periodic_tp()



    ############ Physical & Functional requests ############

    def use_physical(self):
        '''
        Description: Switches diagnostic requests to use physical requests

        Example:
            dgn.use_physical_requests()
        '''
        self.iso.use_physical_requests()


    def use_functional(self):
        '''
        Description: Switches diagnostic requests to use functional requests

        Example:
            dgn.use_functional()
        '''
        self.iso.use_functional_requests()



    ############ Diag Session ############

    def default_session(self):
        '''
        Description: Sends DiagnosticSessionChange with DefaultSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.default_session()
        '''
        if self.print_service: print "Moving to default session"
        return self.iso.service_0x10(0x01)


    def default_session_spr(self):
        '''
        Description: Sends DiagnosticSessionChange with DefaultSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.default_session_spr()
        '''
        if self.print_service: print "Moving to default session SPR"
        return self.iso.service_0x10(0x81)


    def programming_session(self):
        '''
        Description: Sends DiagnosticSessionChange with ProgrammingSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.programming_session()
        '''
        if self.print_service: print "Moving to programming session"
        return self.iso.service_0x10(0x02)


    def programming_session_spr(self):
        '''
        Description: Sends DiagnosticSessionChange with ProgrammingSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.programming_session_spr()
        '''
        if self.print_service: print "Moving to programming session SPR"
        return self.iso.service_0x10(0x82)


    def extended_session(self):
        '''
        Description: Sends DiagnosticSessionChange with ExtendedSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
        '''
        if self.print_service: print "Moving to extended session"
        return self.iso.service_0x10(0x03)


    def extended_session_spr(self):
        '''
        Description: Sends DiagnosticSessionChange with ExtendedSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.extended_session_spr()
        '''
        if self.print_service: print "Moving to extended session SPR"
        return self.iso.service_0x10(0x83)



    ############ ECU Reset ############

    def ecu_reset(self, reset_type=0x01):
        '''
        Description: Sends ECUReset.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.ecu_reset()
        '''
        if self.print_service: print "Send ECU Reset"
        return self.iso.service_0x11(reset_type)


    def ecu_reset_spr(self, reset_type=0x01):
        '''
        Description: Sends ECUReset with SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.ecu_reset_spr()
        '''
        if self.print_service: print "Send ECU Reset SPR"
        return self.iso.service_0x11(reset_type | 0x80)



    ############ Tester Present ############

    def tester_present(self):
        '''
        Description: Sends TesterPresent.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.tester_present()
        '''
        return self.iso.service_0x3E(0x00)


    def tester_present_spr(self):
        '''
        Description: Sends TesterPresent with SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.tester_present_spr()
        '''
        return self.iso.service_0x3E(0x80)



    ############ IOControl ############

    def io_control(self, did, control_state):
        '''
        Description: Sends IOControl service with parameter ShortTermAdjustemt.
        Parameter controlstate must contain a list of values & masks
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.io_control(0x4068, [0xFF])
        '''
        if self.print_service: print "IO control DID", "%#06x" % did, 'to', control_state
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x2F([data1, data0], [0x03], control_state)


    def io_return_control(self, did, mask=[]):
        '''
        Description: Sends IOControl service with parameter ReturnControl.
        Parameter mask contains the mask of the PID to return control. It's an optional parameter,
        only needed for bit-mapped and packeted DIDs.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.io_return_control(0x4068, [0xFF])
        '''
        if self.print_service: print "Return control DID", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x2F([data1, data0], [0x00], mask)



    ############ Routine Control ############

    def start_routine(self, did, params_list=[]):
        '''
        Description: Sends RotuineControl service with subfunction StartRoutine.
        Parameter 'params_list' must contain a list with routine parameters if needed. Otherwise can be omitted.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.start_routine(0x201B, [0x00, 0x07])
        '''
        if self.print_service: print "Start routine", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x31(0x01, [data1, data0], params_list)


    def stop_routine(self, did):
        '''
        Description: Sends RotuineControl service with subfunction StopRoutine.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.stop_routine(0x201B)
        '''
        if self.print_service: print "Stop routine", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x31(0x02, [data1, data0])


    def request_routine_results(self, did):
        '''
        Description: Sends RotuineControl service with subfunction RequestRoutineResults.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.request_routine_results(0x201B)
        '''
        if self.print_service: print "Request routine results", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x31(0x03, [data1, data0])



    ############ Read & Write DIDs ############

    def read_did(self, did):
        '''
        Description: Sends ReadDataByIdentifier service with one DID as parameter.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.read_did(0xF113)
        '''
        if self.print_service: print "Read DID", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x22([data1, data0])


    def write_did(self, did, datalist):
        '''
        Description: Sends WriteDataByIdentifier service.
        Parameter DID contains the desired DID.
        Parameter datalist must contain a byte list with the value to write.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.write_did(0x4094, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        '''
        if self.print_service: print "Write DID", "%#06x" % did
        data0 = (0x00FF & did)
        data1 = (0xFF00 & did) >> 8
        return self.iso.service_0x2E([data1, data0], datalist)


    def to_ascii(self, datalist):
        '''
        Description: Returns a list witht he ASCII representation of a list of hex values.

        Example:
            dgn.read_did(0xF18C)
            print 'ECU serial number: ' + dgn.to_ascii(dgn.response[3:])
        '''
        temp_string = ''
        for item in datalist:
            if item != 0: temp_string = temp_string + chr(item)
        return temp_string



    ############ Security Access ############

    def security_access(self, level):
        '''
        Description: Does the SecurityAccess seed+key process of the level provided.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.security_access(0x05)
        '''
        if self.print_service: print "Entering SA level", hex(level)
        resp = self.iso.service_0x27(level)
        if resp[0] == 0x67:
            seed = resp[2:5]
            if seed != [0, 0, 0]:
                key = self.algorithm_eese(level, seed)
                # Wait 0.5 seconds before sending the key
                time.sleep(0.5)
                return self.iso.service_0x27(level + 1, key)
        return resp


    def algorithm_eese(self, level, seed):
        '''
        Description: Calculates EESE key
        Parameter level must contain the Security Access level being used
        Paramater seed must contain a list with the seed

        Note: This function is used inside securityaccess function.
        '''
        # Intel PC: Little Endian (as in S12, opposite to Bolero/PowerPC)
        tmp = _u24()
        tmp.bytes.high = 0xC5
        tmp.bytes.mid = 0x41
        tmp.bytes.low = 0xA9
        for i in range(64):
            offset = i >> 3
            mask = 0x01 << (i & 0x07)
            sec_const = SECURITY_CONSTANTS[level]
            chbitarray = [seed[0], seed[1], seed[2], sec_const[0], sec_const[1], sec_const[2], sec_const[3], sec_const[4]]
            chbit = (chbitarray[offset] & mask) == mask
            byte_a0 = tmp.bits.b0
            b23 = chbit ^ byte_a0
            # Rotation of A into B
            tmp.bytes.low = tmp.bytes.low >> 1
            tmp.bits.b7 = tmp.bits.b8
            tmp.bytes.mid = tmp.bytes.mid >> 1
            tmp.bits.b15 = tmp.bits.b16
            tmp.bytes.high = tmp.bytes.high >> 1
            # Generation of b23
            tmp.bits.b23 = b23
            # Generation of C
            tmp.bits.b20 = tmp.bits.b20 ^ b23
            tmp.bits.b15 = tmp.bits.b15 ^ b23
            tmp.bits.b12 = tmp.bits.b12 ^ b23
            tmp.bits.b5 = tmp.bits.b5 ^ b23
            tmp.bits.b3 = tmp.bits.b3 ^ b23
        key = [0, 0, 0]
        key[0] = (tmp.bytes.mid & 0x0F) << 4 | (tmp.bytes.low & 0xF0) >> 4
        key[1] = (tmp.bytes.mid & 0xF0) | (tmp.bytes.high & 0xF0) >> 4
        key[2] = (tmp.bytes.low & 0x0F) << 4 | (tmp.bytes.high & 0x0F)
        return key



    ############ DTC ############

    def clear_dtcs(self):
        '''
        Description: Sends ClearDTC service.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.clear_dtcs()
        '''
        if self.print_service: print "Clear DTCs"
        return self.iso.service_0x14([0xFF, 0xFF, 0xFF])


    def read_dtcs(self, service_params):
        '''
        Description: Sends ReadDTC service.
        Parameter 'service_params' contains a list with the service parameters.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.read_dtcs([0x02, 0x08])
        '''
        if self.print_service: print "Read DTCs"
        return self.iso.service_0x19(service_params)


    def is_dtc_in_response(self, dtc, response):
        '''
        Description: Checks if provided DTC is present in the response of a readDTCs service.
        Returns: True or False

        Example:
            dtcs = dgn.read_dtcs([0x02, 0x08])
            if dgn.is_dtc_in_response([0xe0, 0x10, 0x15], dtcs):
                print 'DTC E01015 is present'
        '''
        for i in range(3, len(response) - 3, 4):
            rdtc = [response[i], response[i+1], response[i+2]]
            if dtc == rdtc:
                return True
        return False


    def control_dtc_setting(self, dtc_setting_type):
        '''
        Description: Sends ControlDTCSetting service.
        Parameter 'type' contains a byte with the service parameter DTCSettingType.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.control_dtc_setting(0x00)
        '''
        if self.print_service: print "Control DTCs setting to", hex(dtc_setting_type)
        return self.iso.service_0x85(dtc_setting_type)
  

    def diagnostic_alltypes(self,reqDataList):
        
        return self.iso.diag_service(reqDataList)
        