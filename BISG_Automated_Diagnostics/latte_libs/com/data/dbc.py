"""
====================================================================
Library for reading DBC files, that contain CAN bus description
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import re


__author__ = 'Lluis Amenos, Miguel Periago'
__version__ = '1.5.0'
__email__ = 'lamenosmurtra@lear.com, mperiago@lear.com'

'''
CHANGE LOG
==========
1.5.0 [jfidalgo] PEP8 rework.
1.4.6 [jfidalgo] Removed more methods, which are now part of the CAN library.
      [mperiago] Signals values skipped for enviroment variables.
1.4.5 [xcucurullsalamero] Removed some methods, which are now part of the CAN library (used with DBC and ECUEXTRACT).
1.4.4 Added support for 29bits CAN IDs.
1.4.3 Fixed bug in read_signal_in_frame. _prepare_signal_to_tx improved. Signals an frames calculation method improved.
1.4.2 Fixed bug in regexp frames parsing
1.4.1 Added frameName parameter to get_signal method 
1.4.0 Dbc load method _frames_table improved. Loading performance improved. Some methods cleaned. 
1.3.4 Fixed problem with multiplexed signals attributes.
1.3.3 Fixed issue in read_signal_in_frame with multi byte signals. 
1.3.2 Fixed problem with spaces in dbc frames line description
1.3.1 Fixed bug in _prepare_signal_to_tx for little endian start signals
1.3.0 Fixed bug in read_signal_in_frame for multiple bytes signals.
1.2.0 Period of periodic frames are also parsed and stored
1.1.0 Method write_signal_to_frame allows optional parameter to specify the frame
1.0.2 Bug fix in variable name
1.0.1 Parsing problems solved for VW projects
1.0.0 Inital version
'''

NODE = 'TGW'  # Used for the attributes that contain the node name.
DBC_CAN_EXT_MSG_ID = 0x80000000


class Frame:
    def __init__(self):
        self.name = ''
        self.canid = 0
        self.dlc = 0
        self.publisher = ''
        self.cycleTime = 0


class Signal:
    def __init__(self):
        self.signalName = ''
        self.signalLength = 0
        self.offset = 0
        self.updatebit = 9999
        self.littleEndianStart = False  # This indicates where starts to count the offset in dbc
        self.defaultvalue = 0
        self.SNAValue = 'N/A'
        self.offsetConvValue = 0
        self.factorConvValue = 0
        self.timeOut = 0
        self.enumValue = ''
        self.subscriber = ''
        self.Max = 0
        self.Min = 0


class FrameToTx:
    def __init__(self):
        self.canid = ''
        self.dlc = 0
        self.message = 8*[0]
    

class DBC:
    """
    Class for reading DBC files and access frames/signals.
    """

    def __init__(self, filename=''):
        """
        Description: Constructor
        """
        self.hTableOfFrames = {}   # array frame indexed by frame.name
        self.hTableOfSignals = {}  # 2D of signals indexed by [name]+list        
        self.framesStore = {}
        self.framesDict = {}
        self.lines = ''
        if filename != '':
            self.read_dbc(filename)

    def _test_table_of_signals(self):
        """
        Description: Used to list the table of signals
        """
        for i in self.hTableOfSignals:
            local_list_of_signals = self.hTableOfSignals.get(i)
            for local_signal in local_list_of_signals:
                print "------------"
                print local_signal.offset
                print local_signal.signalLength
                print local_signal.signalName
                print local_signal.updatebit

    def _test_table_of_frames(self):
        """
        Description: Used to list the table of frames
        """
        for i in self.hTableOfFrames:
            local_frame = self.hTableOfFrames[i]
            print "------------"
            print local_frame.name
            print local_frame.canid
            print local_frame.dlc
            print local_frame.publisher

    def _frames_table(self):
        """
        Description: Parse the dbc file and fill the data dictionary
        """
        lines = self.lines.split('\n')

        current_frame = None
        for line in lines:            
            line_cond = re.findall(r'^\s*BO_\s*(\d*)\s*(\S*)\s*:\s*(\d*)\s*(\S*)', line)
            if line_cond:
                item = line_cond[0]
                current_frame = Frame()
                current_frame.canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
                current_frame.name = item[1]
                current_frame.dlc = item[2]
                current_frame.publisher = item[3]
                self.hTableOfFrames[current_frame.name] = current_frame
                self.hTableOfSignals[current_frame.name] = list()
                self.framesDict[current_frame.canid] = current_frame.name  # Used to do quick searches

            line_cond = re.findall(r'^\s*SG_\s*(\S*).*:\s*(.*)[\-+]\s*\(([^)]+)\)\s*\[([^\]]+)\]\s*([\S\s]*)', line)
            if line_cond and current_frame:
                item = line_cond[0]
                signal_new = Signal()
                if re.search("@1+", line):
                    signal_new.littleEndianStart = True
                signal_new.signalName = item[0]
                factor_offset = re.findall('([\S\s]*),([\S\s]*)', item[2])
                signal_new.factorConvValue = factor_offset[0][0]
                signal_new.offsetConvValue = factor_offset[0][1]
                signal_new.subscriber = item[4]
                max_min = re.findall('([\S\s]*)\|([\S\s]*)', item[3])
                signal_new.Min = max_min[0][0]
                signal_new.Max = max_min[0][1]
                temp = item[1].split("|")
                signal_new.offset = temp[0]
                temp = temp[1].split("@")
                signal_new.signalLength = temp[0]
                self.hTableOfSignals[current_frame.name].append(signal_new)
                
        self.read_signal_attributes(self.lines)
        self.read_frame_attributes(self.lines)
                        
    def read_dbc(self, filename):
        """
        Description: Parses DBC file and stores all info in the structs

        Example:
            dbc = DBC()
            dbc.read_dbc('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
        """
        f = open(filename, 'r')
        self.lines = f.read()
        f.close()
               
        self._frames_table()

    def find_id_frame(self, frame_id):
        """
        Description: Finds frame name of ID in the DBC loaded, and returns the frame name

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            frame_id = dbc.find_id_frame(0x765)
        """
        for i in self.hTableOfFrames:
            frame_list = self.hTableOfFrames[i]
            if frame_id == frame_list.canid:
                return frame_list.name
        return None

    def read_frame_attributes(self, lines):
        
        frame = Frame()
        cycle_time = re.findall(r'BA_\s*"GenMsgCycleTime"\s*BO_\s*(\d*)\s*(\d*);', lines)
        for item in cycle_time:
            frame.canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            frame.cycleTime = item[1]
            # noinspection PyPep8Naming
            self.hTableOfFrames[self.framesDict[frame.canid]].cycleTime = frame.cycleTime
        
    def read_signal_attributes(self, lines):
        """ Read dbc attributes and fill the signals dictionary """
        signal = Signal()
        
        default_val = re.findall(r'BA_\s*"GenSigStartValue"\s*SG_\s*(\d*)\s*(\w*)\s*(\d*)\s*;', lines)
        for item in default_val:
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            signal.defaultvalue = int(item[2])                         
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.defaultvalue = signal.defaultvalue
                    break
        
        sna_val = re.findall(r'BA_\s+"GenSigSNA"\s+SG_\s+([0-9]*)\s+(\w*)\s+"(\w*)"\s*?;', lines)
        for item in sna_val:
            signal.snaVal = re.sub("h", "", item[2])
            signal.snaVal = int(signal.snaVal, 16)            
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.snaVal = signal.snaVal
                    break
            
        timeout = re.findall(r'BA_\s*"GenSigTimeout_%s"\s*SG_\s*(\d*)\s*(\S*)\s*(\d*)' % NODE, lines)
        for item in timeout:
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            signal.timeOut = item[2]
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.timeOut = signal.timeOut
                    break
                            
        values_list = re.findall(r'VAL_ (\d*)\s*(\S*)\s*(.*);', lines)
        for item in values_list:
            if item[0] != '':  # Is not an env variable
                canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
                signal.enumValue = re.findall(r'(\d*\s*\"\S*\")', item[2])
                signal.signalName = item[1]
                for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                    if signalDicc.signalName == signal.signalName:
                        signalDicc.enumValue = signal.enumValue
                        break
