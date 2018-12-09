'''
====================================================================
Library for reading DBC files, that contain CAN bus description
(C) Copyright 2017 Lear Corporation
====================================================================
'''

__author__  = "Lluis Amenos, Miguel Periago"
__version__ = "1.4.6"
__email__   = "lamenosmurtra@lear.com, mperiago@lear.com"

'''
CHANGE LOG
==========
1.4.6 Signals values skipped for enviroment variables.
1.4.5 [xcucurullsalamero] Removed some methods, which are now part of the CAN library (used with DBC and ECUEXTRACT)
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

import fileinput
import re

NODE = 'TGW' # Used for the attributes that contain the node name.
DBC_CAN_EXT_MSG_ID = 0x80000000

class Frame:
    name = ''
    canid = 0
    dlc = 0
    publisher = ''
    cycleTime = 0

class Signal:
    signalName = ''
    signalLength = 0
    offset = 0
    updatebit = 9999
    littleEndianStart = False # This indicates where starts to count the offset in dbc
    defaultvalue = 0
    SNAValue = 'N/A'
    offsetConvValue = 0
    factorConvValue = 0
    timeOut = 0
    enumValue = ''
    subscriber = ''
    Max = 0
    Min = 0

class FrameToTx:
    canid = ''
    dlc = 0
    message = 8*[0]

FR_BIT_MAP = (7,6,5,4,3,2,1,0,
           15,14,13,12,11,10,9,8,
           23,22,21,20,19,18,17,16,
           31,30,29,28,27,26,25,24,
           39,38,37,36,35,34,33,32,
           47,46,45,44,43,42,41,40,
           55,54,53,52,51,50,49,48,
           63,62,61,60,59,58,57,56)

class DBC:
    '''
    Class for reading DBC files and access frames/signals.
    '''

    def __init__(self, filename=''):
        '''
        Description: Constructor
        '''
        self.hTableOfFrames = {}   # array frame indexed by frame.name
        self.hTableOfSignals = {}  # 2D of signals indexed by [name]+list
        self.framesStore = {}
        self.framesDict = {}
        self.lines = ''
        if filename != '':
            self.read_dbc(filename)

    def _test_table_of_signals(self):
        '''
        Description: Used to list the table of signals
        '''
        for i in self.hTableOfSignals:
            localslistOfSignals = list()
            localslistOfSignals = self.hTableOfSignals.get(i);
            for localsignal in localslistOfSignals:
                print "------------"
                print localsignal.offset
                print localsignal.signalLength
                print localsignal.signalName
                print localsignal.updatebit

    def _test_table_of_frames(self):
        '''
        Description: Used to list the table of frames
        '''
        for i in self.hTableOfFrames:
            testout = Frame()
            testout = self.hTableOfFrames[i]
            print "------------"
            print testout.name
            print testout.canid
            print testout.dlc
            print testout.publisher

    def _frames_table(self):
        ''' Parse the dbc file and fill the data dictionary '''
        lines = self.lines.split('\n')

        for line in lines:
            lineCond =  re.findall(r'^\s*BO_\s*(\d*)\s*(\S*)\s*:\s*(\d*)\s*(\S*)',line)
            if lineCond != []:
                item = lineCond[0]
                currentframe = Frame()
                currentframe.canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
                currentframe.name = item[1]
                currentframe.dlc = item[2]
                currentframe.publisher= item[3]
                self.hTableOfFrames[currentframe.name] = currentframe
                self.hTableOfSignals[currentframe.name] = list()
                self.framesDict[currentframe.canid] = currentframe.name # Used to do quick searches

            lineCond = re.findall(r'^\s*SG_\s*(\S*).*:\s*(.*)[\-\+]\s*\(([^)]+)\)\s*\[([^\]]+)\]\s*([\S\s]*)', line)
            if lineCond != []:
                item = lineCond[0]
                signalNew = Signal()
                if re.search("@1+",line):
                    signalNew.littleEndianStart = True
                signalNew.signalName = item[0]
                factorOffset = re.findall('([\S\s]*)\,([\S\s]*)', item[2])
                signalNew.factorConvValue = factorOffset[0][0]
                signalNew.offsetConvValue = factorOffset[0][1]
                signalNew.subscriber = item[4]
                maxMin = re.findall('([\S\s]*)\|([\S\s]*)',item[3])
                signalNew.Min = maxMin[0][0]
                signalNew.Max = maxMin[0][1]
                temp = item[1].split("|")
                signalNew.offset = temp[0]
                temp = temp[1].split("@")
                signalNew.signalLength = temp[0]
                self.hTableOfSignals[currentframe.name].append(signalNew)

        self.read_signal_attributes(self.lines)
        self.read_frame_attributes(self.lines)

    def read_dbc(self, filename):
        '''
        Description: Parses DBC file and stores all info in the structs

        Example:
            dbc = DBC()
            dbc.read_dbc('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
        '''
        f = open(filename, 'r')
        self.lines = f.read()
        f.close()

        self._frames_table()

    def find_frame_id(self, frameName):
        '''
        Description: Finds ID of frame frameName in the DBC loaded, and returns the ID and DLC

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            frame_id = dbc.find_frame_id('ABS_PT_C')
        '''
        for i in self.hTableOfFrames:
            frameList = self.hTableOfFrames[i]
            if frameName == frameList.name:
                return int(frameList.canid), int(frameList.dlc)
        return None, None

    def find_id_frame(self, frameId):
        '''
        Description: Finds frame name of ID in the DBC loaded, and returns the frame name

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            frame_id = dbc.find_id_frame(0x765)
        '''
        for i in self.hTableOfFrames:
            frameList = self.hTableOfFrames[i]
            if frameId == frameList.canid:
                return frameList.name
        return None

    def read_signal_in_frame(self, offset, length, message, littleEndianStart):
        '''
        Description: Reads signal value in a given message.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            value = dbc.read_signal_in_frame(16, 8, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08], True)
        '''
        fr_val = 0L #Long int

        if littleEndianStart == False: # Big Endian offset Start
            # Calculate Bit shifting
            pos_cnt = 65 # Count something while the index is not reached
            desp = 0
            for i in FR_BIT_MAP:
                pos_cnt += 1
                if i == offset:
                    pos_cnt = 1
                if pos_cnt == length:
                    desp = -1 # Start bits to shift count
                desp += 1

            for byte in message:
                fr_val = (fr_val << 8) + byte # single var collect
            signalVal = fr_val >> (desp % 64)
            signalVal &= (2**length) - 1
            return signalVal

        else: # Little Endian offset Start
            for byte in reversed(message):
                fr_val = (fr_val << 8) + byte # single var collect
            signalVal = fr_val >> int(offset)
            signalVal &= (2**length) - 1
            return signalVal

    def read_frame_attributes(self, lines):

        frame = Frame()
        cycleTime = re.findall(r'BA_\s*"GenMsgCycleTime"\s*BO_\s*(\d*)\s*(\d*);', lines)
        for item in cycleTime:
            frame.canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            frame.cycleTime = item[1]
            self.hTableOfFrames[self.framesDict[frame.canid]].cycleTime = frame.cycleTime

    def read_signal_attributes(self, lines):
        ''' Read dbc attributes and fill the signals dictionary '''
        signal = Signal()

        defaultVal = re.findall(r'BA_\s*"GenSigStartValue"\s*SG_\s*(\d*)\s*(\w*)\s*(\d*)\s*\;', lines)
        for item in defaultVal:
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            signal.defaultvalue = int(item[2])
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.defaultvalue = signal.defaultvalue
                    break

        snaVal = re.findall(r'BA\_\s{1,}"GenSigSNA"\s{1,}SG\_\s{1,}([0-9]*)\s{1,}(\w*)\s{1,}"(\w*)"\s*?\;',lines)
        for item in snaVal:
            signal.snaVal = re.sub("h", "", item[2])
            signal.snaVal = int(signal.snaVal, 16)
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.snaVal = signal.snaVal
                    break

        timeout = re.findall(r'BA_\s*"GenSigTimeout_%s"\s*SG_\s*(\d*)\s*(\S*)\s*(\d*)' % NODE,lines)
        for item in timeout:
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.signalName = item[1]
            signal.timeOut = item[2]
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.timeOut = signal.timeOut
                    break

        valuesList = re.findall(r'VAL_ (\d*)\s*(\S*)\s*(.*);',lines)
        for item in valuesList:
            if item[0] != '': # Is not an env variable
                canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))

                signal.enumValue = re.findall(r'(\d*\s*\"\S*\")', item[2])
                signal.signalName  = item[1]
                for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                    if signalDicc.signalName == signal.signalName:
                        signalDicc.enumValue = signal.enumValue
                        break

