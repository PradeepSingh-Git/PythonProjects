"""
====================================================================
Library for reading LDF files, that contain LIN bus description
(C) Copyright 2018 Lear Corporation
====================================================================
"""
import re


__author__ = 'Miguel Periago'
__version__ = '1.3.0'
__email__ = 'mperiago@lear.com'


"""
CHANGE LOG
==========
1.3.0 PEP8 rework
1.2.7 Fixed-Removed character " inside method read_ldf when analyzing Node_attributes
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
                Added 'report_slave_productid_by_name' & 'report_slave_productid_by_nad' methods whom return specific 
                slave production information
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
                Added 'report_schedule_frames_publisher' method which returns list with publishers of frames supported 
                by schedule passed
                Added 'report_schedule_delays' method which returns list with delays for each frame inside 
                schedule passed
                Improved 'read_ldf method' now loads slave protocol and frames checksum type , now _LinFrame struct 
                supports checksum_type
                Improved 'read_ldf' methos now includes 'noise_mode' parameter to enable print checksums of slave frames
                Fixed frame.checksum_type asigments inside 'read_ldf' method
                new code lines changed:
                 ->  if '1.' in self.lin_protocol:  was  if re.search('^1\.[0-9]', self.lin_protocol):
                 ->  frame.lin_id = int(lineParts[1]) was frame.lin_id = int(lineParts[1], 0)
                 ->  signalDefault = int(lineParts[2]) was signalDefault = int(lineParts[2], 0)
1.0.8 Default values from LDF in hex format are now supported
1.0.7 Bugfix _LinFrame.lin_id reading from ldf file supports now hex and int numbers
1.0.6 Improved lin protocol detection
1.0.5 Added module name field to the LIN frames
1.0.4 Default value added in signals object. In case of sending a raw list, it's inverted to send it in the correct 
      order over the lin.
1.0.3 LDF parsing method improved. Diagnostic frames included in frames dictionary.
1.0.2 Print removed when constructing self.slave_frames
1.0.1 Method read_ldf improved, now it provides additional public vars: lin_speed, lin_protocol, and slave_nodes
1.0.0 Inital version
"""


class _LinSignal:
    def __init__(self):
        self.name = 'void'
        self.start_bit = 0
        self.length = 8
        self.default = 0


class _LinFrame:
    def __init__(self):
        self.name = 'void'
        self.lin_id = 0
        self.module = ''
        self.dlc = 0
        self.signals = []
        self.message = 8*[0]
        self.node_type = 'void'
        self.checksum_type = 0x01


class _LinSchedulingTable:
    def __init__(self):
        self.name = 'void'
        self.ids = []
        self.delay = []
        self.counter = 0


class _LinNode:
    def __init__(self, name='', configured_nad=0, supplier_id='', function_id='', variant='', node_protocol=''):
        self.name = name
        self.configured_nad = configured_nad
        self.supplier_id = supplier_id
        self.function_id = function_id
        self.variant = variant
        self.protocol = node_protocol


class LDF:
    """
    Class that contains all the signals in a ldf file.
    """

    def __init__(self, filename=''):
        """
        Description: Constructor.
        Parameter 'filename' is the LDF file and it's optional.
        """
        self.frames = {}
        self.scheduling_tables = []
        self.master_node = 'void'
        self.slave_nodes = []
        self.product_id = []
        self.slave_frames = []
        self.master_frames = []
        self.schedules = []
        self.lin_speed = 0
        self.lin_protocol = 'VERSION_1_3'
        if filename != '':
            self.read_ldf(filename)

    def add_node(self, name):
        """
        Description: Creates slave_nodes list object
        Parameter 'name' is the LDF extracted node name.
        """
        self.slave_nodes.append(_LinNode(name, 0, '0', '0', '0', '0.0'))

    def add_node_info(self, slave, slave_info_value, slave_info_type):
        """
        Description: adds node information of selected slave
        Parameter 'slave' indicates node to which add 'slave_info_value' and 'slave_info_type'
        indicates which part to store value.
        """
        for node in self.slave_nodes:
            if slave == node.name:
                if slave_info_type == 'NAD':
                    node.configured_nad = slave_info_value
                elif slave_info_type == 'SUPP_ID':
                    node.supplier_id = slave_info_value
                elif slave_info_type == 'FUNC_ID':
                    node.function_id = slave_info_value
                elif slave_info_type == 'VAR':
                    node.variant = slave_info_value
                elif slave_info_type == 'PROTOCOL':
                    node.protocol = slave_info_value

    def report_slaves(self):
        """
        Description: Returns slaves list inside loaded LDF.
        """
        return [node.name for node in self.slave_nodes]

    def report_slave_protocol(self, slave):
        """
        Description: Returns protocol supported for a specific Slave Name
        """
        for node in self.slave_nodes:
            if slave == node.name:
                return node.protocol
        return 0

    def report_slave_productid_by_name(self, slave):
        """
        Description: Returns production id information (function,supplier,variant) supported for a specific Slave Name
        """
        for node in self.slave_nodes:
            if slave == node.name:
                return [node.supplier_id, node.function_id, node.variant]
        return []

    def report_slave_productid_by_nad(self, nad):
        """
        Description: Returns production id information (function,supplier,variant) supported for a specific Slave Nad
        (passed as string containing hexadecimal value without 0x  Ex. 4b)
        """
        nad = nad.upper()
        for node in self.slave_nodes:
            if nad == node.configured_nad:
                return [node.supplier_id, node.function_id, node.variant]
        return []

    def report_slave_nad(self, slave):
        """
        Description: Returns NAD supported for a specific slave.
        """
        for node in self.slave_nodes:
            if slave == node.name:
                return node.configured_nad
        return 0

    def report_schedules(self):
        """
        Description: Returns list with schedules managed by Master
        Returns: list of schedules supported by Master
        """
        return [schedule.name for schedule in self.schedules]

    def report_schedule_frames(self, schedule_name):
        """
        Description: Returns list with frames supported by schedule passed
        Returns: list of frames inside specific schedule table
        """
        for schedule in self.schedules:
            if schedule.name == schedule_name:
                return schedule.id_list
        return []

    def report_schedule_frames_publisher(self, schedule_name):
        """
        Description: Returns list with publishers of frames supported by schedule passed
        Returns: list of publishers of frames inside specific schedule table
        """
        schedule_frm_pub = []
        for schedule in self.schedules:
            if schedule.name == schedule_name:
                for identifier in schedule.id_list:
                    for k, frame in self.frames.items():
                        if identifier == frame.lin_id:
                            schedule_frm_pub.append(frame.node_type)
                            break
        return schedule_frm_pub

    def report_schedule_delays(self, schedule_name):
        """
        Description: Returns list with delays for each frame inside schedule passed
        Returns: list of delays to apply for each frame  inside specific schedule table
        """
        for schedule in self.schedules:
            if schedule.name == schedule_name:
                return schedule.delay
        return []

    def find_frame_id(self, frame_name):
        """
        Description: Returns frame identifier for a given frame name.
        Returns: frame identifier
        """
        for k, frame in self.frames.items():
            if frame.name == frame_name:
                return frame.lin_id
        return []

    def _prepare_tx_frame(self, signal_name, signal_value, frame_name):
        """
        Description: Returns the message ready to be sent with a signal value set.
        Returns lin_id, dlc, message, message_mask
        """
        def little_endian(signal, value):
            def create_message(m_value, m_offset):
                temp_message = 8*[0]
                m_val = m_value << m_offset
                for i in range(8):
                    temp_message[i] = m_val
                    temp_message[i] &= 0xff
                    m_val = m_val >> 8
                return temp_message

            offset = int(signal.start_bit)
            length = int(signal.length)

            if isinstance(value, list):
                fr_val = 0L
                for item in value:
                    fr_val = fr_val << 8
                    fr_val += item
                value = fr_val

            value &= (2 ** length) - 1
            maskvalue = (2 ** length) - 1

            message = create_message(value, offset)
            message_mask = create_message(maskvalue, offset)

            return message, message_mask

        temp_signal = None
        frame = None
        if not frame_name:
            found = False
            for k, frame in self.frames.items():
                for temp_signal in frame.signals:
                    if signal_name == temp_signal.name:
                        found = True
                        break
                if found:
                    break
        else:
            frame = self.frames[frame_name]
            for temp_signal in frame.signals:
                if signal_name == temp_signal.name:
                    break

        msg, msg_mask = little_endian(temp_signal, signal_value)

        return frame.lin_id, frame.dlc, msg, msg_mask

    def read_ldf(self, filename):
        """
        Description: Parses ldf file and fills frame objects.

        Example:
            ldf = LDF()
            ldf.read_ldf('lin1.ldf')
        """
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
        lin_speed = re.findall(r'LIN_speed\s*=\s*(.*)\s*kbps', lines)
        lin_speed = lin_speed[0].strip()
        temp_speed = lin_speed.split('.')
        while len(temp_speed[1]) < 3:
            temp_speed[1] += '0'
        self.lin_speed = int(temp_speed[0] + temp_speed[1])

        # Get Master/Slave
        node_lines = re.search(r'(Nodes)\s{([\S\s]*?)\n\}\n', lines)
        node_lines = node_lines.group(0)
        node_lines = node_lines.split('\n')

        for line in node_lines:
            line = re.sub("[:,;]", '', line)
            line_parts = line.split()
            if re.search('Master', line):
                self.master_node = line_parts[1]
            if re.search('Slaves', line):
                for i in range(1, len(line_parts)):
                    self.add_node(line_parts[i])

        # Once slave nodes added create a list
        slave_nodes = self.report_slaves()

        # Node attributes
        if self.lin_protocol == 'VERSION_2_0':
            node_found = 'NOTFOUND'
            attribute_lines = self._parse_text_in_claudator(lines, 'Node_attributes\s*\t*\{').split('\n')
            for line in attribute_lines:
                if node_found != 'NOTFOUND':
                    line = line.replace(' ', '')
                    line = line.replace('\t', '')
                    line = line.replace('0x', '')
                    line = line.replace(';', '')
                    line = line.replace('=', '')
                    line = line.replace('"', '')
                    # Get slave protocol
                    if 'LIN_protocol' in line:
                        line = line.replace('LIN_protocol', '')
                        self.add_node_info(node_found, line, 'PROTOCOL')
                    # Get slave NAD
                    if 'configured_nad' in line:
                        line = line.replace('configured_nad', '')
                        self.add_node_info(node_found, line, 'NAD')
                    # Get LIN product id of slaves, product_id = <supplier_id>, <function_id>, <variant>
                    if 'product_id' in line:
                        line = line.replace('product_id', '')
                        line = line.split(',')
                        self.add_node_info(node_found, line[0], 'SUPP_ID')
                        self.add_node_info(node_found, line[1], 'FUNC_ID')
                        self.add_node_info(node_found, line[2], 'VAR')
                        node_found = 'NOTFOUND'
                else:
                    i = 0
                    for item in slave_nodes:
                        if item in line:
                            if '{' in line:
                                node_found = item
                            else:
                                i = i + 1
                        else:
                            i = i + 1

        # Get Frames
        frame_lines = self._parse_text_in_claudator(lines, 'Frames\s*\t*\{').split('\n')
        first_frame = True
        frame = None

        for line in frame_lines:
            if re.search(".*:.*{\s*$", line):  # Frame Line
                line_parts = re.findall(r"[\w']+", line)
                if not first_frame:
                    self.frames[frame.name] = frame

                frame = _LinFrame()
                frame.name = line_parts[0]
                frame.lin_id = int(line_parts[1], 0)
                frame.module = line_parts[2]
                frame.dlc = int(line_parts[3])
                node = line_parts[2]
                if node in slave_nodes:
                    frame.node_type = 'Slave'
                elif node == self.master_node:
                    frame.node_type = 'Master'
                first_frame = False

                # as per vxlapi.py XL_LIN_CHECKSUM_CLASSIC=0x00, XL_LIN_CHECKSUM_ENHANCED=0x01
                if node == self.master_node:
                    frame.node_type = 'Master'
                    if self.lin_protocol == 'VERSION_1_3':
                        frame.checksum_type = 0x00
                    else:
                        frame.checksum_type = 0x01
                else:
                    frame.node_type = 'Slave'
                    if self.report_slave_protocol(node) == '1.3':
                        frame.checksum_type = 0x00
                    else:
                        frame.checksum_type = 0x01

            elif re.search(";\s*$", line):  # Signal Line
                line_parts = re.findall(r"[\w']+", line)
                signal = _LinSignal()
                signal.name = line_parts[0]
                signal.start_bit = int(line_parts[1])
                frame.signals.append(signal)

        self.frames[frame.name] = frame  # Add the last frame

        # Read signals
        signal_lines = re.search(r'(Signals)\s{([\S\s]*?)\n\}\n', lines)
        signal_lines = signal_lines.group(0)
        signal_lines = signal_lines.split('\n')

        for line in signal_lines:
            if re.search("^[\s|\w]*:.*;", line):  # Signal Line
                line_parts = re.findall(r"[\w']+", line)
                signal_name = line_parts[0]
                signal_length = int(line_parts[1])
                signal_default = int(line_parts[2], 0)
                for (k, frame) in self.frames.items():
                    for signal in frame.signals:
                        if signal.name == signal_name:
                            signal.length = signal_length
                            signal.default = signal_default

        # Read diagnostic frames
        diag_frames = self._parse_text_in_claudator(lines, 'Diagnostic_frames\s*\t*\{')
        if diag_frames:
            diag_frames = diag_frames.split('\n')

            first_frame = True
            for line in diag_frames:
                if re.search(".*:.*{", line):  # Frame Line
                    if not first_frame:
                        self.frames[frame.name] = frame
                    line_parts = re.findall(r"[\w']+", line)
                    frame = _LinFrame()
                    frame.name = line_parts[0]
                    frame.lin_id = int(line_parts[1], 0)
                    frame.dlc = 8
                    if 'Slave' in frame.name:
                        frame.node_type = 'Slave'
                    elif 'Master' in frame.name:
                        frame.node_type = 'Master'
                    # Diagnostics frames are classic checksum allways
                    frame.checksum_type = 0x00
                    first_frame = False
                elif re.search('.*,.*;', line):  # Signal line
                    line_parts = re.findall(r"[\w']+", line)
                    signal = _LinSignal()
                    signal.name = line_parts[0]
                    signal.start_bit = int(line_parts[1])
                    signal.length = 8
                    frame.signals.append(signal)
            self.frames[frame.name] = frame  # Add the last frame

            # Read diagnostics signals
            diag_signals = re.search(r'(Diagnostic_signals)\s{([\S\s]*?)\n\}\n', lines)
            if diag_signals:
                diag_signals = diag_signals.group(0)
                diag_signals = diag_signals.split('\n')
                for line in diag_signals:
                    if re.search(".*,.*;", line):  # Signal Line
                        line_parts = re.findall(r"[\w']+", line)
                        signal_name = line_parts[0]
                        signal_length = int(line_parts[1])
                        for k, frame in self.frames.items():
                            for signal in frame.signals:
                                if signal.name == signal_name:
                                    signal.length = signal_length

        # List with slave frame IDs and slave frame DLCs: [[ID1, DLC1], [ID2, DLC2], ...]
        for k, frame in self.frames.items():
            if frame.node_type == 'Slave':
                self.slave_frames.append([frame.lin_id, frame.dlc, frame.checksum_type])
            if frame.node_type == 'Master':
                self.master_frames.append([frame.lin_id, frame.dlc, frame.checksum_type])

        # Read scheduling tables
        scheduling_lines = self._parse_text_in_claudator(lines, 'Schedule_tables\s*\t*\{')
        if scheduling_lines:
            scheduling_lines = scheduling_lines.split('\n')
            sch_table = None
            for line in scheduling_lines[1:len(scheduling_lines)-1]:  # Skip first line
                if re.search('\S*\s*{', line):  # Table name
                    line_parts = re.findall('(\S*)\s*{', line)
                    if sch_table:
                        self.scheduling_tables.append(sch_table)
                    sch_table = _LinSchedulingTable()
                    sch_table.name = line_parts[0]
                if re.search('\S*\s*delay\s*\d*\.?\d*\s*ms', line):  # Frame and delay
                    line_parts = re.findall('(\S*)\s*delay\s*(\d*)\.?\d*\s*ms', line)[0]
                    sch_table.delay.append(int(line_parts[1]))
                    sch_table.ids.append(self.get_lin_id_from_frame_name(line_parts[0]))

            self.scheduling_tables.append(sch_table)  # last element

    def get_lin_id_from_frame_name(self, name):
        """
        Description: Returns the LIN ID of a LIN frame name loaded from LDF
        """
        for k, frame in self.frames.items():
            if frame.name == name:
                return frame.lin_id
        return None

    @staticmethod
    def _parse_text_in_claudator(lines, regex):
        """
        Description: return text contained in { }, from a given start pattern.
        Ex: Frames { xxx } will return xxx. xxx could contain more indenting. Regex should search for Frames {
        """
        frame_str = re.findall(regex, lines)
        if not frame_str:
            return None

        frame_index = lines.find(frame_str[0])
        frames_end = False
        indent_count = 0
        indent_start = False
        frame_start = frame_index
        while not frames_end:
            if lines[frame_index] == r'{':
                indent_count += 1
                indent_start = True
            if lines[frame_index] == r'}':
                indent_count -= 1
            if indent_count == 0 and indent_start:
                frames_end = True
            frame_index += 1
        return lines[frame_start:frame_index]

    def report_slave_frames(self, slave):
        """
        Description: Returns messages id supported for a specific slave.
        """
        slave_frames = []
        for k, frame in self.frames.items():
            if frame.module == slave:
                slave_frames.append(frame.lin_id)
        return slave_frames

    def find_signal_info(self, signal_name):
        """
        Description: Returns info for a given signal.
        Returns: frame id, signal start_bit, signal length
        """
        for k, frame in self.frames.items():
            for signal in frame.signals:
                if signal.name == signal_name:
                    return frame.lin_id, signal.start_bit, signal.length
        return []

    def find_frame_info(self, frame_id):
        """
        Description: Returns info for a given frame identifier.
        Returns: frame name, frame dlc
        """
        for k, frame in self.frames.items():
            if frame.lin_id == frame_id:
                return frame.name, frame.dlc
        return []

    def write_signal_to_frame(self, signal_name, signal_value, frame_name):
        """
        Description: Fills the frames dictionary with a new signal value.
        Returns (lin_id, dlc, message) of the updated frame.

        Example:
            ldf = LDF('lin1.ldf')
            ldf.write_signal_to_frame('SignalName', 1)
        """

        lin_id, dlc, message, message_mask = self._prepare_tx_frame(signal_name, signal_value, frame_name)

        frame = None
        for k, frame in self.frames.items():
            if frame.lin_id == lin_id:
                for i in range(0, len(frame.message)):
                    frame.message[i] &= ~message_mask[i]
                    frame.message[i] |= message[i]
                break
        return lin_id, dlc, frame.message

    @staticmethod
    def read_signal_in_frame(start_bit, length, message):
        """
        Description: Reads signal value in a given message.
        Note: little_endian_start is set just for compatibility with can lib in pltot library.
        Example:
            ldf = LDF('lin1.ldf')
            value = ldf.read_signal_in_frame(14, 4, 'MessageName')
        """
        fr_val = 0L
        for byte in reversed(message):
            fr_val = (fr_val << 8) + byte  # single var collect
        signal_val = fr_val >> start_bit
        signal_val &= (2**length) - 1
        return signal_val
