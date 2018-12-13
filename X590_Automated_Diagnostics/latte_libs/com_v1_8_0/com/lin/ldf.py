'''
====================================================================
Library for reading LDF files, that contain LIN bus description
(C) Copyright 2013 Lear Corporation
====================================================================
'''
from _ast import Break

__author__  = 'Miguel Periago'
__version__ = '1.2.6'
__email__   = 'mperiago@lear.com'

'''
CHANGE LOG
==========
1.2.6 Fixed hexa id numbers reading in diagnostic frames
1.2.5 Check if the scheduling tables info is present in the ldf before doing nothing.
1.2.4 read_signal_in_frame compatibility with can lib added. Needed for plot lib.
1.2.3 Signals an frames calculation methods improved.
1.2.2 Signals line regexp improved. Fixed bug in raw data sending in _prepare_tx_frame
1.2.1 Added frameName parameter in _prepare_tx_frame.
      Fixed bug in _prepare_tx_frame method.
1.2.0 [mperiago] Added scheduling tables load
      [cblanco] IMPROVES from MQB and BCM added to Official LATTE library:
                Added 'report_slaves' method which return slaves supported
                Added 'report_slave_productid_by_name' & 'report_slave_productid_by_nad' methods whom return specific slave production information
                Added 'report_slave_frames' method which returns specific slave supported frames
                Added 'find_frame_info' method which returns information for a given frame identifier
                Added 'report_slave_nad' method which returns nad of specific slave
                Added _LinNode struct                
                Added _LinSchedule struct
                Added 'find_frame_id' method which returns frame identifier for a given frame name
                Added 'report_schedules' method which returns list with schedules managed by Master
                Added 'report_schedule_frames' method which returns list with frames supported by schedule passed
                Added 'report_slave_protocol' method ,
                Added 'add_node_info' method which adds node information of selected slave
                Added 'report_schedule_frames_publisher' method which returns list with publishers of frames supported by schedule passed
                Added 'report_schedule_delays' method which returns list with delays for each frame inside schedule passed
                Improved 'read_ldf method' now loads slave protocol and frames checksum type , now _LinFrame struct supports checksumtype
                Improved 'read_ldf' methos now includes 'noise_mode' parameter to enable print checksums of slave frames
                Fixed frame.checksumtype asigments inside 'read_ldf' method
                new code lines changed:
                 ->  if '1.' in self.lin_protocol:  was  if re.search('^1\.[0-9]', self.lin_protocol):
                 ->  frame.linid = int(lineParts[1]) was frame.linid = int(lineParts[1], 0)
                 ->  signalDefault = int(lineParts[2]) was signalDefault = int(lineParts[2], 0)
1.0.8 Default values from LDF in hex format are now supported
1.0.7 Bugfix _LinFrame.linid reading from ldf file supports now hex and int numbers
1.0.6 Improved lin protocol detection
1.0.5 Added module name field to the LIN frames
1.0.4 Default value added in signals object. In case of sending a raw list, it's inverted to send it in the correct order over the lin. 
1.0.3 LDF parsing method improved. Diagnostic frames included in frames dictionary.
1.0.2 Print removed when constructing self.slave_frames
1.0.1 Method read_ldf improved, now it provides additional public vars: lin_speed, lin_protocol, and slave_nodes
1.0.0 Inital version
'''

import re

class _LinSignal:
    def __init__(self):
        self.name = 'void'
        self.startbit = 0
        self.length = 8
        self.default = 0

class _LinFrame:
    def __init__(self):
        self.name = 'void'
        self.linid = 0
        self.module = ''
        self.dlc = 0
        self.signals = []
        self.message = 8*[0]
        self.nodeType = 'void'
        self.checksumtype =0x01

class _LinSchedulingTable:
    def __init__(self):
        self.name = 'void'
        self.ids = []
        self.delay = []
        self.counter = 0

class _LinNode:
    def __init__(self, name='', configured_NAD=0, supplier_ID='', function_ID='', variant='', node_protocol=''):
        self.name = name
        self.configured_NAD = configured_NAD
        self.supplier_ID = supplier_ID
        self.function_ID = function_ID
        self.variant = variant
        self.protocol = node_protocol

class LDF:
    '''
    Class that contains all the signals in a ldf file.
    '''

    def __init__(self, filename=''):
        '''
        Description: Constructor.
        Parameter 'filename' is the LDF file and it's optional.
        '''
        self.frames = {}
        self.scheduling_tables = []
        self.masterNode = 'void'
        self.slaveNodes = []
        self.product_id = []
        if filename != '':
            self.read_ldf(filename)

    def add_node(self, name):
        '''
        Description: Creates slaveNodes list object
        Parameter 'name' is the LDF extracted node name.
        '''
        self.slaveNodes.append(_LinNode(name,'0' , '0', '0', '0','0.0'))    

    def add_node_info(self, slave,slave_info_value,slave_info_type):
        '''
        Description: adds node information of selected slave
        Parameter 'slave' indicates node to which add 'slave_info_value' and 'slave_info_type' indicates which part to store value.
        '''
        i=0
        for item in self.slaveNodes:
            if (slave==self.slaveNodes[i].name):
                if(slave_info_type=='NAD'):
                    self.slaveNodes[i].configured_NAD=slave_info_value
                elif(slave_info_type=='SUPP_ID'):
                    self.slaveNodes[i].supplier_ID=slave_info_value
                elif(slave_info_type=='FUNC_ID'):
                    self.slaveNodes[i].function_ID=slave_info_value
                elif(slave_info_type=='VAR'):
                    self.slaveNodes[i].variant=slave_info_value
                elif(slave_info_type=='PROTOCOL'):
                    self.slaveNodes[i].protocol=slave_info_value
                else:
                    pass
            else:
                i=i+1

    def report_slaves (self):
        '''
        Description: Returns slaves list inside loaded LDF.
        '''
        slave_nodes=[]
        i=0
        for item in self.slaveNodes:
            slave_nodes.append(self.slaveNodes[i].name)
            i=i+1
        return slave_nodes

    def report_slave_protocol (self,slave):
        '''
        Description: Returns protocol supported for a specific Slave Name
        '''
        i=0
        for item in self.slaveNodes:
            if (slave==self.slaveNodes[i].name):
                return self.slaveNodes[i].protocol
            else:
                i=i+1
        return 0

    def report_slave_productid_by_name (self,slave):
        '''
        Description: Returns production id information (function,supplier,variant) supported for a specific Slave Name
        '''
        i=0
        product_id=[]
        for item in self.slaveNodes:
            if (slave==self.slaveNodes[i].name):
                product_id.append(self.slaveNodes[i].supplier_ID)
                product_id.append(self.slaveNodes[i].function_ID)
                product_id.append(self.slaveNodes[i].variant)
                return product_id
            else:
                i=i+1
        return product_id

    def report_slave_productid_by_nad (self,nad):
        '''
        Description: Returns production id information (function,supplier,variant) supported for a specific Slave Nad (passed as string containing hexadecimal value without 0x  Ex. 4b)
        '''
        i=0
        nad =nad.upper()
        product_id=[]
        for item in self.slaveNodes:
            if (nad==self.slaveNodes[i].configured_NAD):
                product_id.append(self.slaveNodes[i].supplier_ID)
                product_id.append(self.slaveNodes[i].function_ID)
                product_id.append(self.slaveNodes[i].variant)
                return product_id
            else:
                i=i+1
        return product_id

    def report_slave_nad (self,slave):
        '''
        Description: Returns NAD supported for a specific slave.
        '''
        i=0
        for item in self.slaveNodes:
            if (slave==self.slaveNodes[i].name):
                return self.slaveNodes[i].configured_NAD
            else:
                i=i+1
        return 0

    def report_schedules(self):
        '''
        Description: Returns list with schedules managed by Master
        Returns: list of schedules supported by Master
        '''
        i=0
        schedule_tab=[]
        for item in self.schedules:
            schedule_tab.append(self.schedules[i].name)
            i=i+1
        return schedule_tab

    def report_schedule_frames(self,schedulename):
        '''
        Description: Returns list with frames supported by schedule passed
        Returns: list of frames inside specific schedule table
        '''
        i=0
        schedule_frm=[]
        for item1 in self.schedules:
            if(self.schedules[i].name==schedulename):
                for item2 in self.schedules[i].ID_list:
                    schedule_frm.append(item2)
            i=i+1
        return schedule_frm

    def report_schedule_frames_publisher(self,schedulename):
        '''
        Description: Returns list with publishers of frames supported by schedule passed
        Returns: list of publishers of frames inside specific schedule table
        '''
        i=0
        schedule_frm_pub=[]
        for item1 in self.schedules:
            if(self.schedules[i].name==schedulename):
                for item2 in self.schedules[i].ID_list:
                    for k,frame in self.frames.items():
                        if (item2==frame.linid):
                            schedule_frm_pub.append(frame.nodeType)
                            break
            i=i+1
        return schedule_frm_pub
    def report_schedule_delays(self,schedulename):
        '''
        Description: Returns list with delays for each frame inside schedule passed
        Returns: list of delays to apply for each frame  inside specific schedule table
        '''
        i=0
        schedule_delay=[]
        for item1 in self.schedules:
            if(self.schedules[i].name==schedulename):
                for item2 in self.schedules[i].delay:
                    schedule_delay.append(item2)
            i=i+1
        return schedule_delay

    def find_frame_id(self, frameName):
        '''
        Description: Returns frame identifier for a given frame name.
        Returns: frame identifier
        '''
        for k,frame in self.frames.items():
            if frame.name == frameName:
                return frame.linid
        return []

    def _prepare_tx_frame(self, signalName, signalvalue, frameName):
        '''
        Description: Returns the message ready to be sent with a signal value set.
        Returns lin_id, dlc, message, message_mask
        '''
        def littleEndian(signal, signalvalue):
            def create_message(value, offset):
                message = 8*[0]                                        
                fr_val = value << offset                
                for i in range(8):
                    message[i] = fr_val
                    message[i] &= 0xff                    
                    fr_val = fr_val >> 8
                return message                
            
            offset = int(signal.startbit)
            length = int(signal.length)
                                                                    
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
                        
            return message, message_mask         
                
        if frameName == None:
            found = False
            for k,frame in self.frames.items():
                for signal in frame.signals:
                    if signalName == signal.name:
                        found = True
                        break
                if found:
                    break                    
        else:
            frame = self.frames[frameName]            
            for signal in frame.signals:
                if signalName == signal.name:
                    break
        
        message, message_mask = littleEndian(signal, signalvalue)
                
        return(frame.linid, frame.dlc, message, message_mask)


    def read_ldf(self, filename):
        '''
        Description: Parses ldf file and fills frame objects.

        Example:
            ldf = LDF()
            ldf.read_ldf('lin1.ldf')
        '''
        f = open(filename, 'r')
        lines = f.read()

        # Get LIN protocol version
        self.lin_protocol = re.findall(r'LIN_protocol_version\s*=\s*"(.*)"', lines)
        self.lin_protocol = self.lin_protocol[0].strip()
        if re.search('^1\.[0-9]', self.lin_protocol):
            self.lin_protocol = 'VERSION_1_3'
        else:
            self.lin_protocol = 'VERSION_2_0'

        # Get LIN speed
        self.lin_speed = re.findall(r'LIN_speed\s*=\s*(.*)\s*kbps', lines)
        self.lin_speed = self.lin_speed[0].strip()
        temp_speed = self.lin_speed.split('.')
        while len(temp_speed[1]) < 3:
            temp_speed[1] += '0'
        self.lin_speed = int(temp_speed[0] + temp_speed[1])

        # Get Master/Slave
        nodeLines = re.search(r'(Nodes)\s\{([\S\s]*?)\n\}\n', lines)
        nodeLines = nodeLines.group(0)
        nodeLines = nodeLines.split('\n')

        for line in nodeLines:
            line = re.sub(":|,|;", '', line)
            lineParts = line.split()
            if re.search('Master',line) != None:
                self.masterNode = lineParts[1]
            if re.search('Slaves',line) != None:
                for i in range(1,len(lineParts)):
                    self.add_node(lineParts[i])

        #once slave nodes added create a list        
        slave_nodes=self.report_slaves()

        #node attributes
        if self.lin_protocol == 'VERSION_2_0':
            node_found = 'NOTFOUND'
            attributeLines = self._parse_text_in_claudator(lines, 'Node_attributes\s*\t*\{').split('\n')
            for line in attributeLines:
                if(node_found!='NOTFOUND'):
                    line=line.replace(' ', '')
                    line=line.replace('\t', '')
                    line=line.replace('0x','')
                    line=line.replace(';','')
                    line=line.replace('=','')
                    #Get slave protocol
                    if 'LIN_protocol' in line:
                        line=line.replace('LIN_protocol','')
                        self.add_node_info(node_found,line,'PROTOCOL')
                    #Get slave NAD
                    if 'configured_NAD' in line:
                        line=line.replace('configured_NAD','')
                        self.add_node_info(node_found,line,'NAD')
                    #Get LIN product id of slaves, product_id = <supplier_id>, <function_id>, <variant>
                    if 'product_id' in line:
                        line=line.replace('product_id','')
                        line = line.split(',')
                        self.add_node_info(node_found,line[0],'SUPP_ID')
                        self.add_node_info(node_found,line[1],'FUNC_ID')
                        self.add_node_info(node_found,line[2],'VAR')
                        node_found='NOTFOUND'
                else:
                    i=0
                    for item in slave_nodes:
                        if item in line:
                            if '{' in line:
                                node_found=item                                
                            else:
                                i=i+1
                        else:
                            i=i+1

        # Get Frames
        frameLines = self._parse_text_in_claudator(lines, 'Frames\s*\t*\{').split('\n')
        firstFrame = True
        
        for line in frameLines:                        
            if re.search(".*:.*{\s*$",line) != None: # Frame Line
                lineParts = re.findall(r"[\w']+", line)
                if firstFrame == False:                    
                    self.frames[frame.name] = frame
                
                frame = _LinFrame()
                frame.name = lineParts[0]
                frame.linid = int(lineParts[1], 0)
                frame.module = lineParts[2]
                frame.dlc = int(lineParts[3])
                node = lineParts[2]
                if node in slave_nodes:
                    frame.nodeType = 'Slave'
                elif node == self.masterNode:
                    frame.nodeType = 'Master'
                firstFrame = False
                                
                #as per vxlapi.py XL_LIN_CHECKSUM_CLASSIC   = 0x00 , XL_LIN_CHECKSUM_ENHANCED  = 0x01
                if node == self.masterNode:
                    frame.nodeType = 'Master'            
                    if (self.lin_protocol == 'VERSION_1_3'):
                        frame.checksumtype = 0x00
                    else:
                        frame.checksumtype = 0x01
                else:
                    frame.nodeType = 'Slave'
                    if(self.report_slave_protocol(node) == '1.3'):
                        frame.checksumtype = 0x00
                    else:
                        frame.checksumtype = 0x01
                                                
            elif re.search(";\s*$",line) != None: # Signal Line
                lineParts = re.findall(r"[\w']+", line)
                signal = _LinSignal()
                signal.name = lineParts[0]
                signal.startbit = int(lineParts[1])
                frame.signals.append(signal)

        self.frames[frame.name] = frame # Add the last frame

        # Read signals
        signalLines = re.search(r'(Signals)\s\{([\S\s]*?)\n\}\n', lines)        
        signalLines = signalLines.group(0)
        signalLines = signalLines.split('\n')

        for line in signalLines:
            if re.search("^[\s|\w]*:.*;",line) != None: # Signal Line
                lineParts = re.findall(r"[\w']+", line)
                signalName = lineParts[0]
                signalLength = int(lineParts[1])
                signalDefault = int(lineParts[2], 0)
                for (k,frame) in self.frames.items():
                    for signal in frame.signals:
                        if signal.name == signalName:
                            signal.length = signalLength
                            signal.default = signalDefault
        
        # Read diagnostic frames
        diagFrames = self._parse_text_in_claudator(lines,'Diagnostic_frames\s*\t*\{')
        if diagFrames != None:            
            diagFrames = diagFrames.split('\n')
            
            firstFrame = True
            for line in diagFrames:
                if re.search(".*:.*{",line) != None: # Frame Line
                    if firstFrame == False:                        
                        self.frames[frame.name] = frame
                    lineParts = re.findall(r"[\w']+", line)
                    frame = _LinFrame()
                    frame.name = lineParts[0]
                    frame.linid = int(lineParts[1],0)
                    frame.dlc = 8
                    if 'Slave' in frame.name:
                        frame.nodeType = 'Slave'
                    elif 'Master' in frame.name:
                        frame.nodeType = 'Master'
                    #diagnostics frames are classic checksum allways
                    frame.checksumtype = 0x00
                    firstFrame = False
                elif re.search('.*,.*;', line) != None: # Signal line
                    lineParts = re.findall(r"[\w']+", line)
                    signal = _LinSignal()
                    signal.name = lineParts[0]
                    signal.startbit = int(lineParts[1])
                    signal.length = 8
                    frame.signals.append(signal)            
            self.frames[frame.name] = frame # Add the last frame
            
            # Read diagnostics signals
            diagSignals = re.search(r'(Diagnostic_signals)\s\{([\S\s]*?)\n\}\n', lines)        
            if diagSignals != None:
                diagSignals = diagSignals.group(0)
                diagSignals = diagSignals.split('\n')
                for line in diagSignals:
                    if re.search(".*,.*;",line) != None: # Signal Line
                        lineParts = re.findall(r"[\w']+", line)
                        signalName = lineParts[0]
                        signalLength = int(lineParts[1])
                        for k,frame in self.frames.items():
                            for signal in frame.signals:
                                if signal.name == signalName:
                                    signal.length = signalLength
         
        # List with slave frame IDs and slave frame DLCs: [[ID1, DLC1], [ID2, DLC2], ...]
        self.slave_frames = []
        self.master_frames = []
        for k,frame in self.frames.items():
            if frame.nodeType == 'Slave':
                self.slave_frames.append([frame.linid, frame.dlc, frame.checksumtype])
            if frame.nodeType == 'Master':
                self.master_frames.append([frame.linid, frame.dlc, frame.checksumtype])
                
        # Read scheduling tables
        schedulingLines = self._parse_text_in_claudator(lines, 'Schedule_tables\s*\t*\{')
        if schedulingLines != None:
            schedulingLines = schedulingLines.split('\n')
            sch_table = None
            for line in schedulingLines[1:len(schedulingLines)-1]: # Skip first line
                if re.search('\S*\s*\{', line) != None: # Table name
                    lineParts = re.findall('(\S*)\s*\{', line)
                    if sch_table != None:
                        self.scheduling_tables.append(sch_table)
                    sch_table = _LinSchedulingTable()
                    sch_table.name = lineParts[0]
                if re.search('\S*\s*delay\s*\d*\.?\d*\s*ms', line) != None: # Frame and delay
                    lineParts = re.findall('(\S*)\s*delay\s*(\d*)\.?\d*\s*ms', line)[0]
                    sch_table.delay.append(int(lineParts[1]))
                    sch_table.ids.append(self._get_lin_id_from_frame_name(lineParts[0]))
                    
            self.scheduling_tables.append(sch_table) # last element
                
    def _get_lin_id_from_frame_name(self, name):
        '''
        Description: Returns the LIN ID of a LIN frame name loaded from LDF
        '''
        for k,frame in self.frames.items():
            if frame.name == name:
                return frame.linid    
        return None        
                                
    def _parse_text_in_claudator(self, lines, regex):
        '''
        Description: return text contained in { }, from a given start pattern.
        Ex: Frames { xxx } will return xxx. xxx could contain more indenting. Regex should search for Frames {
        '''
        frameStr = re.findall(regex,lines)
        if frameStr == []:
            return None
        
        frameIndex = lines.find(frameStr[0])        
        framesEnd = False
        indentCount = 0
        indentStart = False
        frameStart = frameIndex
        while framesEnd == False:
            if lines[frameIndex] == r'{':
                indentCount += 1
                indentStart = True
            if lines[frameIndex] == r'}':
                indentCount -= 1
            if indentCount == 0 and indentStart == True:
                framesEnd = True
            frameIndex += 1        
        return lines[frameStart:frameIndex]
        
    def report_slave_frames (self,slave):
        '''
        Description: Returns messages id supported for a specific slave.
        '''
        slave_frames=[]
        for k,frame in self.frames.items():
            if(frame.module==slave):
                slave_frames.append(frame.linid)
        return slave_frames
                
    def find_signal_info(self, signalName):
        '''
        Description: Returns info for a given signal.
        Returns: frame id, signal startbit, signal length
        '''
        for k,frame in self.frames.items():
            for signal in frame.signals:
                if signal.name == signalName:
                    return frame.linid, signal.startbit, signal.length
        return []

    def find_frame_info(self, frameId):
        '''
        Description: Returns info for a given frame identifier.
        Returns: frame name, frame dlc
        '''
        for k,frame in self.frames.items():
            if frame.linid == frameId:
                return frame.name, frame.dlc
        return []

    def write_signal_to_frame(self, signalName, signalValue, frameName):
        '''
        Description: Fills the frames dictionary with a new signal value.
        Returns (lin_id, dlc, message) of the updated frame.

        Example:
            ldf = LDF('lin1.ldf')
            ldf.write_signal_to_frame('SignalName', 1)
        '''
        
        linid, dlc, message, message_mask = self._prepare_tx_frame(signalName, signalValue, frameName)

        i = 0
        for k,frame in self.frames.items():
            if frame.linid == linid:
                for i in range (0, len(frame.message)):
                    frame.message[i] &= ~message_mask[i]
                    frame.message[i] |= message[i]
                break
        return linid, dlc, frame.message


    def read_signal_in_frame(self, startbit, length, message, littleEndianStart=None):
        '''
        Description: Reads signal value in a given message.
        Note: littleEndianStart is set just for compatibility with can lib in pltot library.
        Example:
            ldf = LDF('lin1.ldf')
            value = ldf.read_signal_in_frame(14, 4, 'MessageName')            
        '''
        fr_val = 0L                
        for byte in reversed(message):
            fr_val = (fr_val << 8) + byte # single var collect
        signalVal = fr_val >> startbit
        signalVal &= (2**length) - 1
        return signalVal
    
    