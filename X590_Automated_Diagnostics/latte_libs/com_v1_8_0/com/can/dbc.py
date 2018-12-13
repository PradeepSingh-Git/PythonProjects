'''
====================================================================
Library for reading DBC files, that contain CAN bus description
(C) Copyright 2013 Lear Corporation
====================================================================
'''

__author__  = "Lluis Amenos, Miguel Periago"
__version__ = "1.4.4"
__email__   = "lamenosmurtra@lear.com, mperiago@lear.com"

'''
CHANGE LOG
==========
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

    def _prepare_signal_to_tx(self, signal_signalName, frame_signalName, signalvalue):
        '''
        Description: Looks for signal=signal_signalName in frame=frame_signalName and updates its value with signalvalue
        Parameter 'signal_signalName' is an object of class Signal
        Parameter 'frame_signalName' is an object of class Frame
        Parameter 'signalvalue' is an integer        
        
        Returns (frame_id, dlc, message, message_mask)
        '''
        def littleEndian(signal_signalName, signalvalue):
            def create_message(value, offset):
                message = 8*[0]                                        
                fr_val = value << offset                
                for i in range(8):
                    message[i] = fr_val
                    message[i] &= 0xff                    
                    fr_val = fr_val >> 8
                return message                
            
            offset = int(signal_signalName.offset)
            length = int(signal_signalName.signalLength)
                                                                    
            if isinstance(signalvalue,list):
                fr_val = 0L                                
                for item in signalvalue:
                    fr_val = fr_val << 8
                    fr_val += item                    
                signalvalue = fr_val

            signalvalue &= (2**length) - 1
            maskvalue = (2**length) - 1
            
            message = create_message(signalvalue, offset)
            message_mask = create_message(maskvalue, offset)
                        
            return(int(frame_signalName.canid), int(frame_signalName.dlc), message, message_mask)
                    
        def bigEndian(signal_signalName, signalvalue):
            # Calculate Bit shifting  
            def create_message(value, offset):
                message = 8*[0]
                fr_val = value << offset
                for i in range(8):
                    message[i] = fr_val
                    message[i] &= 0xff                    
                    fr_val = fr_val >> 8
                return list(reversed(message))
            
            if isinstance(signalvalue, list):
                fr_val = 0L
                for item in signalvalue:
                    fr_val = fr_val << 8
                    fr_val += item
                signalvalue = fr_val            
                    
            pos_cnt = 65 # Count something while the index is not reached
            desp = 0
            offset = int(signal_signalName.offset)
            length = int(signal_signalName.signalLength)
            # Calculate the bit shifting
            for i in FR_BIT_MAP:
                pos_cnt += 1
                if i == offset:
                    pos_cnt = 1
                if pos_cnt == length:
                    desp = -1
                desp += 1
                
            signalvalue &= (2**length) - 1
            maskvalue = (2**length) - 1
            
            message = create_message(signalvalue, desp)
            message_mask = create_message(maskvalue, desp)
            return(int(frame_signalName.canid), int(frame_signalName.dlc), message, message_mask)
            
        #############
         
        if signal_signalName.littleEndianStart == True:
            return littleEndian(signal_signalName, signalvalue)
        else:
            return bigEndian(signal_signalName, signalvalue)
                
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

    def look_for_frame_and_signal(self, signalName, frameName = None):
        '''
        Description: Finds the frame containing signal=signalName, and returns the frame (object of class Frame) and the signalName
        the rest of the signals unmodified.
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal an object of class Signal.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_frame_and_signal('PRDoorLatchStatus')
        '''
        
        frame_found = Frame()
        signal_found = Signal()
        
        if frameName != None:
            localslistOfSignals = self.hTableOfSignals[frameName];
            for signal_i in localslistOfSignals:                
                if signal_i.signalName == signalName:
                    frame_found = self.hTableOfFrames[frameName]
                    return (frame_found, signal_i)
                
        else:                            
            for frame_i in self.hTableOfSignals:
                localslistOfSignals = self.hTableOfSignals.get(frame_i);
                for signal_i in localslistOfSignals:                    
                    if signal_i.signalName == signalName:
                        frame_found = self.hTableOfFrames[frame_i]
                        return (frame_found, signal_i)
                    
        return (None, None)    


    def look_for_signal_in_frame(self, signalName, frameName):
        '''
        Description: Finds a specific signal inside a specific frame and returns both objects
        Returns (frame_found, signal), being frame_found and object of class Frame, and signal an object of class Signal.
        If signalName does not exist inside frameName, returns (None, None)

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f,s = dbc.look_for_signal_in_frame('PRDoorLatchStatus', 'BO_Frame_A1')
        '''
        frame_found = Frame()
        signal_found = Signal()
        if frameName in self.hTableOfFrames:
            frame_found = self.hTableOfFrames.get(frameName)
            localslistOfSignals = self.hTableOfSignals.get(frameName)
            for signal_i in localslistOfSignals:
                if signal_i.signalName == signalName:
                    signal_found = signal_i
                    return (frame_found, signal_found)
        return (None, None)


    def write_signal_to_frame(self, signalName, signalValue, frameName=None):
        '''
        Description: Prepares the frame containing signal=signalName, by updating signalName=signalValue and keeping
        the rest of the signals unmodified. Returns an object of class FrameToTx.        

        Note: Useful when there are two different CAN frames with a signal with the same name. It allows to specify
        exactly the frame to be used.

        Example:
            dbc = DBC('BO_MSCAN_MultiCAN_15MY_IP12W38.dbc')
            f_tx = dbc.write_signal_to_frame('PRDoorLatchStatus', 2)
            # If for example 'PRDoorRequest' exists in frames 'BP_Frame_01' and 'BP_Frame_02', it's possible
            # to specify the frame we want to use
            f_tx = dbc.write_signal_to_frame('PRDoorRequest', 1, 'BP_Frame_01')
        '''
        frame_signalName = Frame()
        signal_signalName = Signal()
        frame_to_tx = FrameToTx()
        if frameName == None:
            frame_signalName, signal_signalName = self.look_for_frame_and_signal(signalName)
        else:
            frame_signalName, signal_signalName = self.look_for_signal_in_frame(signalName, frameName)

        if frame_signalName != None:
            frame_to_tx.canid, frame_to_tx.dlc, frame_to_tx.message, message_mask = self._prepare_signal_to_tx(signal_signalName, frame_signalName, signalValue)
            # Add the signal to frames storage
            if frame_to_tx.canid in self.framesStore.keys():
                i = 0
                for byteVal in frame_to_tx.message:
                    self.framesStore[frame_to_tx.canid].message[i] &= ~message_mask[i] # clean the bytes to write
                    self.framesStore[frame_to_tx.canid].message[i] |= byteVal
                    i = i + 1
                frame_to_tx = self.framesStore[frame_to_tx.canid]                
            else:                
                self.framesStore[frame_to_tx.canid] = frame_to_tx
        else:
            frame_to_tx = None
            print signalName + ' not found in dbc file'

        return frame_to_tx


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

    def find_period_frame(self, frame):
        return int(self.hTableOfFrames[frame].cycleTime)


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
            canid = str(int(item[0]) & (~DBC_CAN_EXT_MSG_ID))
            signal.enumValue = re.findall(r'(\d*\s*\"\S*\")', item[2])
            signal.signalName  = item[1]
            for signalDicc in self.hTableOfSignals[self.framesDict[canid]]:
                if signalDicc.signalName == signal.signalName:
                    signalDicc.enumValue = signal.enumValue
                    break
                        
            