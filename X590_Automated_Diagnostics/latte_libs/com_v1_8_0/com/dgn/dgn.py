"""
====================================================================
Implements customer spec for Diagnostics
(C) Copyright 2013 Lear Corporation
====================================================================
"""

__author__  = 'Jesus Fidalgo'
__version__ = '1.2.0'
__email__   = 'jfidalgo@lear.com'

"""
CHANGE LOG
==========
1.2.0 Added method control_dtc_setting
1.1.0 Method req_info_raw added
1.0.1 Bugfix in security_access method
1.0.0 Inital version
"""

from iso14229 import *
from math import *
from ctypes import *


SECURITY_CONSTANTS = {
    #0x01: [0x41, 0xAA, 0x42, 0xBB, 0x43],
    0x01: [0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
    0x03: [0x17, 0xD8, 0xEB, 0x5B, 0xFB],
    0x11: [0x17, 0xCF, 0x6F, 0xA8, 0xFB],
    0x21: [0xC1, 0x15, 0xDE, 0xBE, 0x57],
    0x0F: [0x28, 0x59, 0x70, 0x5C, 0x70],
}

class u24_bits(Structure):
    _pack_ = 1
    _fields_ = [ \
        ( "b16", c_ubyte, 1 ),
        ( "b17", c_ubyte, 1 ),
        ( "b18", c_ubyte, 1 ),
        ( "b19", c_ubyte, 1 ),
        ( "b20", c_ubyte, 1 ),
        ( "b21", c_ubyte, 1 ),
        ( "b22", c_ubyte, 1 ),
        ( "b23", c_ubyte, 1 ),
        ( "b8",  c_ubyte, 1 ),
        ( "b9",  c_ubyte, 1 ),
        ( "b10", c_ubyte, 1 ),
        ( "b11", c_ubyte, 1 ),
        ( "b12", c_ubyte, 1 ),
        ( "b13", c_ubyte, 1 ),
        ( "b14", c_ubyte, 1 ),
        ( "b15", c_ubyte, 1 ),
        ( "b0",  c_ubyte, 1 ),
        ( "b1",  c_ubyte, 1 ),
        ( "b2",  c_ubyte, 1 ),
        ( "b3",  c_ubyte, 1 ),
        ( "b4",  c_ubyte, 1 ),
        ( "b5",  c_ubyte, 1 ),
        ( "b6",  c_ubyte, 1 ),
        ( "b7",  c_ubyte, 1 )]

class u24_bytes(Structure):
    _pack_ = 1
    _fields_ =     [
         ("high",  c_ubyte),
         ("mid",   c_ubyte),
         ("low",   c_ubyte)]

class u24(Union):
    _pack_ = 1
    _fields_ =     [
        ("bits",  u24_bits),
        ("bytes", u24_bytes)]



class DGN():
    """
    Implements the specific customer diagnostics requirements.
    """

    def __init__(self):
        """
        Description: Constructor
        """
        self.iso = ISO14229()
        self.print_service = True


    ############ General ############

    def save_logfile_custom(self,all_can_frames,log_file_name, write_mode='w'):
        """
        Description: Writes frames to the logfile.
        """
        if all_can_frames != []:
            f = open(log_file_name, write_mode)
            for item in all_can_frames:
                f.writelines(item + '\n')
            f.close()


    def save_logfile(self, write_mode='w'):
        """
        Description: Saves diagnostics CAN traffic to a log file. Log file name is configured in dgn_cfg.py
        Should be called just before ending the script (so all frames are saved)

        Example:
            dgn.default_session()
            dgn.save_logfile()
        """
        self.iso.save_logfile()


    def req_info(self):
        """
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
        """
        return self.iso.req_info()


    def req_info_raw(self):
        """
        Description: Returns a string with latest request + response(s), like a mini logfile.
        Useful for printing this info in a report.

        Example:
            dgn.read_did(0xF188)
            print dgn.req_info()

            This will print:
            Request:  [22 F1 88]
            Response: [62 F1 88 47 58 37 33 2D 31 34 43 31 38 34 2D 41 41 31 32 00 00 00 00 00 00 00 00]
        """
        return self.iso.req_info_raw()



    ############ Testern Present ############

    def start_periodic_tp(self):
        """
        Description: Starts the transmission of periodic Tester Present frames.
        Period is defined in parameter TESTER_PRESENT_PERIOD in dgn_cfg.py file.
        Tester Present frames will be sent strictly when needed. Diagnostic requests resets the
        TESTER_PRESENT_PERIOD timer, so Tester Present frames will be only sent if a diagnostics
        inactivity period of TESTER_PRESENT_PERIOD happens.

        Example:
            dgn.start_periodic_tp()
        """
        self.iso.start_periodic_tp()


    def stop_periodic_tp(self):
        """
        Description: Stops the transmission of periodic Tester Present frames.

        Example:
            dgn.stop_periodic_tp()
        """
        self.iso.stop_periodic_tp()



    ############ Physical & Functional requests ############

    def use_physical(self):
        """
        Description: Switches diagnostic requests to use physical requests

        Example:
            dgn.use_physical_requests()
        """
        self.iso.use_physical_requests()


    def use_functional(self):
        """
        Description: Switches diagnostic requests to use functional requests

        Example:
            dgn.use_functional()
        """
        self.iso.use_functional_requests()



    ############ Diag Session ############

    def default_session(self):
        """
        Description: Sends DiagnosticSessionChange with DefaultSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.default_session()
        """
        if self.print_service: print "Moving to default session"
        self.iso.service_0x10(0x01)
        self.response = self.iso.response

    def Wrong_session(self):
        """
        Description: Sends DiagnosticSessionChange with DefaultSession.

        Returns: Nothing, but check 'response' member variable for the service response.
        """
        if self.print_service: print "Moving to default session"
        self.iso.service_0x10(0x11)
        self.response = self.iso.response

    def Wrong_len_session(self):
        """
        Description: Sends DiagnosticSessionChange with DefaultSession.

        Returns: Nothing, but check 'response' member variable for the service response.
        """
        if self.print_service: print "Moving to default session"
        self.iso.service_0x10_len_mismatch(0x11)
        self.response = self.iso.response

    def default_session_spr(self):
        """
        Description: Sends DiagnosticSessionChange with DefaultSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.default_session_spr()
        """
        if self.print_service: print "Moving to default session SPR"
        self.iso.service_0x10(0x81)
        self.response = self.iso.response


    def programming_session(self):
        """
        Description: Sends DiagnosticSessionChange with ProgrammingSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.programming_session()
        """
        if self.print_service: print "Moving to programming session"
        self.iso.service_0x10(0x02)
        self.response = self.iso.response


    def programming_session_spr(self):
        """
        Description: Sends DiagnosticSessionChange with ProgrammingSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.programming_session_spr()
        """
        if self.print_service: print "Moving to programming session SPR"
        self.iso.service_0x10(0x82)
        self.response = self.iso.response


    def extended_session(self):
        """
        Description: Sends DiagnosticSessionChange with ExtendedSession.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
        """
        if self.print_service: print "Moving to extended session"
        self.iso.service_0x10(0x03)
        self.response = self.iso.response


    def extended_session_spr(self):
        """
        Description: Sends DiagnosticSessionChange with ExtendedSession and SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.extended_session_spr()
        """
        if self.print_service: print "Moving to extended session SPR"
        self.iso.service_0x10(0x83)
        self.response = self.iso.response



    ############ ECU Reset ############

    def ecu_reset(self,reset_type):
        """
        Description: Sends ECUReset.

        Returns: Nothing, but check 'response' member variable for the service response.
        """
        if self.print_service: print "Send ECU Reset"
        self.iso.service_0x11(reset_type)
        self.response = self.iso.response


    def ecu_reset_spr(self, reset_type=0x01):
        """
        Description: Sends ECUReset with SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.ecu_reset_spr()
        """
        if self.print_service: print "Send ECU Reset SPR"
        self.iso.service_0x11(0x81)
        self.response = self.iso.response



    ############ Tester Present ############

    def tester_present(self):
        """
        Description: Sends TesterPresent.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.tester_present()
        """
        self.iso.service_0x3E(0x00)
        self.response = self.iso.response

    ############ Tester Present stuff ############

    def tester_present_wrong_Subfunction(self):

        """
        Description: Sends TesterPresent.
        """
        self.iso.service_0x3E(0x01)
        self.response = self.iso.response

    ############ Tester Present stuff ############

    def tester_present_wrong_length(self):

        """
        Description: Sends TesterPresent.
        """
        self.iso.service_0x3E_len_NRC(0x00)
        self.response = self.iso.response
    def tester_present_spr(self):
        """
        Description: Sends TesterPresent with SuppressPositiveResponseBit.
        Returns: list of bytes with the ECU response, an empty list in this case []

        Example:
            dgn.tester_present_spr()
        """
        self.iso.service_0x3E(0x80)
        self.response = self.iso.response



    ############ IOControl ############

    def io_control(self, did, control_state):
        """
        Description: Sends IOControl service with parameter ShortTermAdjustemt.
        Parameter controlstate must contain a list of values & masks
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.io_control(0x4068, [0xFF])
        """
        if self.print_service: print "IO control DID", "%#06x" % did, 'to', control_state
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x2F([d1, d0], [0x03], control_state)
        self.response = self.iso.response


    def io_return_control(self, did, mask=[]):
        """
        Description: Sends IOControl service with parameter ReturnControl.
        Parameter mask contains the mask of the PID to return control. It's an optional parameter,
        only needed for bit-mapped and packeted DIDs.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.io_return_control(0x4068, [0xFF])
        """
        if self.print_service: print "Return control DID", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x2F([d1, d0], [0x00], mask)
        self.response = self.iso.response



    ############ Routine Control ############

    def start_routine(self, did, params_list=[]):
        """
        Description: Sends RotuineControl service with subfunction StartRoutine.
        Parameter 'params_list' must contain a list with routine parameters if needed. Otherwise can be omitted.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.start_routine(0x201B, [0x00, 0x07])
        """
        if self.print_service: print "Start routine", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x31(0x01, [d1, d0], params_list)
        self.response = self.iso.response

    def start_routine_No_Param(self, did):
        """
        Description: Sends RotuineControl service with subfunction StartRoutine.
        Parameter 'params_list' must contain a list with routine parameters if needed. Otherwise can be omitted.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.start_routine(0x201B, [0x00, 0x07])
        """
        if self.print_service: print "Start routine", hex(did)
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x31_No_Par(0x01, [d1, d0])
        self.response = self.iso.response



    def stop_routine(self, did):
        """
        Description: Sends RotuineControl service with subfunction StopRoutine.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.stop_routine(0x201B)
        """
        if self.print_service: print "Stop routine", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x31(0x02, [d1, d0])
        self.response = self.iso.response


    def request_routine_results(self, did):
        """
        Description: Sends RotuineControl service with subfunction RequestRoutineResults.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.request_routine_results(0x201B)
        """
        if self.print_service: print "Request routine results", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x31(0x03, [d1, d0])
        self.response = self.iso.response



    ############ Read & Write DIDs ############

    def read_did(self, did):
        """
        Description: Sends ReadDataByIdentifier service with one DID as parameter.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.read_did(0xF113)
        """
        if self.print_service: print "Read DID", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x22([d1, d0])
        self.response = self.iso.response

    def read_DID_Len_W(self, did, len):
        """
        Description: Sends ReadDataByIdentifier service with one DID as parameter.

        Example:
            dgn.read_DID(0xF113)
        """
        if self.print_service: print "Read DID", hex(did)
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x22([d1, d0,len])
        self.response = self.iso.response

    def write_did(self, did, datalist):
        """
        Description: Sends WriteDataByIdentifier service.
        Parameter DID contains the desired DID.
        Parameter datalist must contain a byte list with the value to write.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.extended_session()
            dgn.write_did(0x4094, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        """
        if self.print_service: print "Write DID", "%#06x" % did
        d0 = (0x00FF & did)
        d1 = (0xFF00 & did) >> 8
        self.iso.service_0x2E([d1, d0], datalist)
        self.response = self.iso.response


    def to_ascii(self, datalist):
        """
        Description: Returns a list witht he ASCII representation of a list of hex values.

        Example:
            dgn.read_did(0xF18C)
            print 'ECU serial number: ' + dgn.to_ascii(dgn.response[3:])
        """
        s = ''
        for item in datalist:
            if item != 0: s = s + chr(item)
        return s



    ############ Security Access stuff ############

    def security_access(self, level):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level)
        self.response = self.iso.response
        #seed = self.response[2:5]
        seed = self.iso.net._resp_frames[0][3][3:6]

        if seed != [0, 0, 0]:
            key = self.algorithm_EESE(level, seed)
            # Wait 0.5 seconds before sending the key
            time.sleep(0.5)
            self.iso.service_0x27(level + 1, key)
            self.response = self.iso.response


    def security_access_2219(self, level, SC1, SC2, SC3, SC4, SC5):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level)
        self.response = self.iso.response
        #seed = self.response[2:5]
        seed = self.iso.net._resp_frames[0][4][3:6]

        SECURITY_CONSTANTS[0x03] = [SC1, SC2, SC3, SC4, SC5]

        if seed != [0, 0, 0]:
            key = self.algorithm_EESE(level, seed)
            # Wait 0.5 seconds before sending the key
            time.sleep(0.5)
            self.iso.service_0x27(level + 1, key)
            self.response = self.iso.response


    def security_access_wrong_key_level(self, level):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level)
        self.response = self.iso.response
        #seed = self.response[2:5]
        seed = self.iso.net._resp_frames[0][4][3:6]

        if seed != [0, 0, 0]:
            key = self.algorithm_EESE(level, seed)
            # Wait 0.5 seconds before sending the key
            time.sleep(0.5)
            self.iso.service_0x27(level + 2, key)
            self.response = self.iso.response

    def security_access_incorrect_length(self, level,data):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level,data)
        self.response = self.iso.response
        #seed = self.response[2:5]

    def security_access_wrong_level(self, level):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level)
        self.response = self.iso.response
        #seed = self.response[2:5]


    def security_access_wrong_key(self, level):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level)
        self.response = self.iso.response
        #seed = self.response[2:5]
        seed = self.iso.net._resp_frames[0][3][3:6]

        if seed != [0, 0, 0]:
            key = self.algorithm_EESE(level, seed)
            # Wait 0.5 seconds before sending the key
            time.sleep(0.5)
            self.iso.service_0x27(level + 1, [key[0]+1, key[1],key[2]])
            self.response = self.iso.response

    def security_access_Only_key(self, level):
        """
        Description: Does the SecurityAccess seed+key process of the level provided.

        Example:
            dgn=Sbox()
            dgn.extended_session()
            dgn.security_access(0x21)
        """
        if self.print_service: print "Entering SA level", hex(level)
        self.iso.service_0x27(level + 1, [0x00, 0x01, 0x02])
        self.response = self.iso.response

    def algorithm_EESE(self, level, seed):
        """
        Description: Calculates EESE key
        Parameter level must contain the Security Access level being used
        Paramater seed must contain a list with the seed

        Note: This function is used inside securityaccess function.
        """
        # Intel PC: Little Endian (as in S12, opposite to Bolero/PowerPC)
        tmp = u24()
        tmp.bytes.high = 0xC5
        tmp.bytes.mid = 0x41
        tmp.bytes.low = 0xA9
        for i in range(64):
            offset = i >> 3
            mask = 0x01 << (i & 0x07)
            sc = SECURITY_CONSTANTS[level]
            chbitarray = [seed[0], seed[1], seed[2], sc[0], sc[1], sc[2], sc[3], sc[4]]
            chbit = (chbitarray[offset] & mask) == mask
            a0 = tmp.bits.b0
            b23 = chbit ^ a0
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
        """
        Description: Sends ClearDTC service.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.clear_dtcs()
        """
        if self.print_service: print "Clear DTCs"
        self.iso.service_0x14([0xFF, 0xFF, 0xFF])
        self.response = self.iso.response


    def read_dtcs(self, service_params):
        """
        Description: Sends ReadDTC service.
        Parameter 'service_params' contains a list with the service parameters.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.read_dtcs([0x02, 0x08])
        """
        if self.print_service: print "Read DTCs"
        self.iso.service_0x19(service_params)
        self.response = self.iso.response


    def is_dtc_in_response(self, dtc, response):
        """
        Description: Checks if provided DTC is present in the response of a readDTCs service.
        Returns: True or False

        Example:
            dtcs = dgn.read_dtcs([0x02, 0x08])
            if dgn.is_dtc_in_response([0xe0, 0x10, 0x15], dtcs):
                print 'DTC E01015 is present'
        """
        for i in range(3, len(response) - 3, 4):
            rdtc = [response[i], response[i+1], response[i+2]]
            if dtc == rdtc:
                return True
        return False


    def control_dtc_setting(self, dtc_setting_type):
        """
        Description: Sends ControlDTCSetting service.
        Parameter 'type' contains a byte with the service parameter DTCSettingType.
        Returns: list of bytes with the ECU response.

        Example:
            dgn.control_dtc_setting(0x00)
        """
        if self.print_service: print "Control DTCs setting to", hex(dtc_setting_type)
        return self.iso.service_0x85(dtc_setting_type)

    ############ SW Download stuff ############

    def ccf_set_param(self, vbf, index, value):
        CCF_PARAMS_ADDRESS = 0x00008100
        vbf.change_data_at_offset(1, 2 + index, value)
        chk = 0
        for i in range(2, vbf.blocks[1][2][0]):
            chk = chk + vbf.read_data_at_offset(1, i)
        chk = chk & 0x00FF
        vbf.blocks[1][2][1] = chk


    def vbf_download(self, vbf):
        """
        Description: Downloads VBF provided as a parameter

        Example:
            dgn=Sbox()
            sbl=VBF('DV6T-14C097-AA002.vbf')
            lcm=VBF('DV6T-14C095-AB001.vbf')
            dgn.programming_session()
            time.sleep(1) # wait 1 second
            dgn.security_access(0x01)
            dgn.vbf_download(sbl)
            dgn.vbf_download(lcm)
            dgn.ecu_reset()

        Notes: SBL is automatically activated after downloaded
        """
        if self.print_service: print "VBF download", vbf.file_name
        temp = self.iso.net.print_frames
        self.iso.net.print_frames = False

        # Erase FLASH
        if vbf.sw_part_type != 'SBL':
            for erase in vbf.erase_info:
                a0 = (0x000000FF & erase[0])
                a1 = (0x0000FF00 & erase[0]) >> 8
                a2 = (0x00FF0000 & erase[0]) >> 16
                a3 = (0xFF000000 & erase[0]) >> 24
                l0 = (0x000000FF & erase[1])
                l1 = (0x0000FF00 & erase[1]) >> 8
                l2 = (0x00FF0000 & erase[1]) >> 16
                l3 = (0xFF000000 & erase[1]) >> 24
                temp = self.print_service
                self.print_service = False
                self.start_routine(0xFF00, [a3, a2, a1, a0, l3, l2, l1, l0])
                self.print_service = temp

        # Download data
        for block in vbf.blocks:
            # block[0] contains the start address
            a0 = (0x000000FF & block[0])
            a1 = (0x0000FF00 & block[0]) >> 8
            a2 = (0x00FF0000 & block[0]) >> 16
            a3 = (0xFF000000 & block[0]) >> 24
            # block[0] contains the data length
            l0 = (0x000000FF & block[1])
            l1 = (0x0000FF00 & block[1]) >> 8
            l2 = (0x00FF0000 & block[1]) >> 16
            l3 = (0xFF000000 & block[1]) >> 24
            # RequestDownload service
            self.iso.service_0x34(0x00, 0x44, [a3, a2, a1, a0], [l3, l2, l1, l0])
            # Get max_number_of_block_length from the response
            max_number_of_block_length = 0x100 * self.iso.response[2] + self.iso.response[3] - 2
            # TransferData service, check first if data length to be downloaded exceeds max_number_of_block_length
            data_offset = 0
            data_remaining = block[1]
            block_sequence_counter = 1
            num_blocks = int(floor(block[1]/ max_number_of_block_length)) + 1
            while data_remaining > max_number_of_block_length:
                if self.print_service: print "    Block", block_sequence_counter, "of", num_blocks
                self.iso.service_0x36(block_sequence_counter, block[2][data_offset:data_offset+max_number_of_block_length])
                data_offset = data_offset + max_number_of_block_length
                block_sequence_counter = block_sequence_counter + 1
                data_remaining = data_remaining - max_number_of_block_length
            if self.print_service: print "    Block", block_sequence_counter, "of", num_blocks
            self.iso.service_0x36(block_sequence_counter, block[2][data_offset:])
            # RequestTransferExit service
            self.iso.service_0x37()

        # Activate SBL if the SW part downloaded was SBL
        if vbf.sw_part_type == 'SBL':
            a0 = (0x000000FF & vbf.call_address)
            a1 = (0x0000FF00 & vbf.call_address) >> 8
            a2 = (0x00FF0000 & vbf.call_address) >> 16
            a3 = (0xFF000000 & vbf.call_address) >> 24
            temp = self.print_service
            self.print_service = False
            self.start_routine(0x0301, [a3, a2, a1, a0])
            self.print_service = temp

        self.iso.net.print_frames = temp

    ############################### CAN signals stuff ###############################
    def sendCANSignal(self, signalName, value):
        """
        Description: Sends a can signal in a sporadic frame in the bus

        Example:
            can=Sbox()
            can.sendCANSignal('V_VEH_COG',1)
        """
        self.cansgn.sendRawSignal(signalName, value)