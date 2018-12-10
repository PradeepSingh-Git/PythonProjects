"""
====================================================================
Library for reading AUTOSAR ECU Extract files
(C) Copyright 2017 Lear Corporation
====================================================================
"""

__author__  = 'Xavier Cucurull'
__version__ = '1.0.3'
__email__   = 'xcucurullsalamero@lear.com'

'''
CHANGE LOG
==========
1.0.3 Get Source Address and Target Address for FlexRay target GTW PDUs.
1.0.2 Get information regarding PDU gateway and TP connections.
1.0.1 Imports cleanup. Fix bug with PDU signal instances
      Added CAN cluster
      Change update_bit_pos to updatebit to be compatible with dbc structs
      Bugfix. Get the correct PDU and Frame name from TP triggering info
      Fixed get_bitpos
      Fixed problem with unit-ref on AUTOSAR 4.2 ECUExtract
1.0.0 Initial version
'''
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.cElementTree as ET
    print "Using xml cElementTree..."
    print "Install lxml for a better performance"
import sys


class _ClusterConfig(object):
    """
    Class for storing the cluster configuration parameters. Used by COM.
    """
    def __init__(self):
        self.busGuardianEnable = 0
        self.baudrate = 0
        self.busGuardianEnable = 0
        self.busGuardianTick = 0
        self.externalClockCorrectionMode = 0
        self.gColdStartAttempts = 0
        self.gListenNoise = 0
        self.gMacroPerCycle = 0
        self.gMaxWithoutClockCorrectionFatal = 0
        self.gMaxWithoutClockCorrectionPassive = 0
        self.gNetworkManagementVectorLength = 0
        self.gNumberOfMinislots = 0
        self.gNumberOfStaticSlots = 0
        self.gOffsetCorrectionStart = 0
        self.gPayloadLengthStatic = 0
        self.gSyncNodeMax = 0
        self.gdActionPointOffset = 0
        self.gdDynamicSlotIdlePhase = 0
        self.gdMacrotick= 0
        self.gdMinislot = 0
        self.gdMiniSlotActionPointOffset = 0
        self.gdNIT = 0
        self.gdStaticSlot = 0
        self.gdSymbolWindow = 0
        self.gdTSSTransmitter = 0
        self.gdWakeupSymbolRxIdle = 0
        self.gdWakeupSymbolRxLow = 0
        self.gdWakeupSymbolRxWindow = 0
        self.gdWakeupSymbolTxIdle = 0
        self.gdWakeupSymbolTxLow = 0
        self.pAllowHaltDueToClock = 0
        self.pAllowPassiveToActive = 0
        self.pChannels = 3              # It is possible to send messages through channels A and B
        self.pClusterDriftDamping = 0
        self.pDecodingCorrection = 0
        self.pDelayCompensationA = 0
        self.pDelayCompensationB = 0
        self.pExternOffsetCorrection = 0
        self.pExternRateCorrection = 0
        self.pKeySlotUsedForStartup = 1 # must be set for xlFrStartUpAndSync
        self.pKeySlotUsedForSync = 1    # must be set for xlFrStartUpAndSync
        self.pLatestTx = 0
        self.pMacroInitialOffsetA = 0
        self.pMacroInitialOffsetB = 0
        self.pMaxPayloadLengthDynamic = 0
        self.pMicroInitialOffsetA = 0
        self.pMicroInitialOffsetB = 0
        self.pMicroPerCycle = 0
        self.pMicroPerMacroNom = 0
        self.pOffsetCorrectionOut = 0
        self.pRateCorrectionOut = 0
        self.pSamplesPerMicrotick = 0
        self.pSingleSlotEnabled = 0
        self.pWakeupChannel = 0
        self.pWakeupPattern = 0
        self.pdAcceptedStartupRange = 0
        self.pdListenTimeout = 0
        self.pdMaxDrift = 0
        self.pdMicrotick = 0
        self.gdCASRxLowMax = 0
        self.gChannels = 0
        self.vExternOffsetControl = 0
        self.vExternRateControl = 0
        self.pChannelsMTS = 0
        self.reserved = [0]*16

        self.erayID = 0
        self.coldID = 0
        self.eray_repetition = 1
        self.cold_repetition = 1
        self.eray_offset = 0
        self.cold_offset = 0
        self.erayChannel = 0

        self.key_slot_ids = []


class signalGtwObject(object):
    """
    Signal Gateway Object

    Attributes:
        source_gtw_bus (str): source bus
        source_gtw_frame (str): source frame (or PDU)
        source_gtw_signal (str): source signal
        source_gtw_UBsignal (str): source update bit signal ("YES" or "NO")
        target_gtw_bus (str): target bus
        target_gtw_frame (str): target frame (or PDU)
        target_gtw_signal (str): target signal
        target_gtw_UBsignal (str): target update bit signal ("YES" or "NO")
    """
    def __init__(self):
        self.source_gtw_bus = ""
        self.source_gtw_frame = ""
        self.source_gtw_signal = ""
        self.source_gtw_UBsignal = ""
        self.target_gtw_bus = ""
        self.target_gtw_frame = ""
        self.target_gtw_signal = ""
        self.target_gtw_UBsignal = ""


class pduGtwObject(object):
    """
    PDU Gateway Object

    Attributes:
        source_gtw_bus (str): source bus
        source_gtw_frames (list): source frame(s)
        source_gtw_pdu (str): source PDU
        target_gtw_bus (str): target bus
        target_gtw_frames (list): target frame(s)
        target_gtw_pdu (str): target PDU
        resp_pdu (str): response PDU
        source_resp : source response ID (frameName for FlexRay, canID for CAN)
        target_resp : target response ID (frameName for FlexRay, canID for CAN)
    """
    def __init__(self):
        self.source_gtw_bus = ""
        self.source_gtw_frames = []
        self.source_gtw_pdu = ""
        self.source_gtw_addr = ""
        self.target_gtw_bus = ""
        self.target_gtw_frames = []
        self.target_gtw_pdu = ""
        self.target_gtw_addr = ""
        self.resp_pdu = ""
        self.source_resp = ""
        self.target_resp = ""


class _Signal(object):
    """
    Signal parameters (name, position, endiannnes, value, etc.)
    """
    def __init__(self):
        self.signalName = 'Signal not Defined'
        self.signal_id = 0
        self.bitpos = 0
        self.bytepos = 0
        self.bitoos_in_pdu = 0
        self.endianness = 0         # 0: Intel (little en), 1: Motorola (big en)
        self.value = 0
        self.updatebit = None       # Position of the update bit
        self.coding = _Coding()
        self.unit = _Unit()


class _SignalGroup(object):
    """
    Signal group parameters (name, position, update_bit ...)
    """
    def __init__(self):
        self.group_name = 'Signal Group not Defined'
        self.bitpos = 0
        self.bytepos = 0
        self.endianness = 0         # 0: Intel (little en), 1: Motorola (big en)
        self.updatebit = None
        self.signal_instances = []


class _PDU(object):
    """
    PDU parameters (name, length, position, signals, etc.)
    """
    def __init__(self):
        self.pdu_id = 0
        self.pdu_name = 'PDU not Defined'
        self.pdu_length = 0         # PDU length in bytes
        self.pdu_type = 'Type not Defined'
        self.bitpos = 0
        self.endianness = 0         # 0: Intel (little en), 1: Motorola (big en)
        self.signal_instances = []  # list with signal_id from the associated signals
        self.cycleTime = 0          # CAN
        self.multiplexer = False
        self.switch_pdu_instances = []


class _Frame(object):
    """
    Frame parameters (name, slot ID, repetition, length, etc.)
    """
    def __init__(self):
        self.frame_id = 0           # in CAN frames this is the CAN ID
        self.triggering_id = 0
        self.name = 'Frame not Defined'
        self.type = 'Type not Defined'
        self.slot_id = []
        self.repetition = 0
        self.offset = 0             # base cycle
        self.length = 0             # bytes
        self.channel = 0
        self.cycleTime = 0          # CAN
        self.transmitter = ''
        self.receiver = []
        self.signal_instances = []  # list with signal_id from the associated signals
        self.pdu_instances = []     # list with pdu_id from the associated PDUs


class _Unit(object):
    """
    Physical unit parameters (id, name and symbol).
    """
    def __init__(self):
        self.unit_id = 0
        self.unit_name = 'Unit not Defined'
        self.display = ''


class _Coding(object):
    """
    Signal coding parameters (name, length, computation, etc.)
    """
    def __init__(self):
        self.coding_id = 0
        self.coding_name = 'Coding not Defined'
        self.bit_length = 0                         # signal length in bits
        self.constraints = 0                        # max raw value (depends on bit length)
        self.coded_type = 'Coding Type not Defined'
        self.computation_method = 'Not Defined'     # IDENTICAL: phys = raw | LINEAR: phys = mul*raw+sum
        self.compu_numerator = [0]*2                # [sum, mul]
        self.compu_denominator = 1
        self.unit_ref = 'Unit Reference not Defined'
        self.text_table = {}                        # For computation method TEXTTABLE


class _FlexRayCluster(object):
    """
    FlexRay Cluster information: cluster configuration, frames, PDUs, signals, signal groups, TPU pool
    """
    def __init__(self):
        self.frames = {}                     # Frame objects indexed by frame name
        self.pdus = {}                       # PDU objects indexed by pdu name
        self.signals = {}                    # Signal objects indexed by signal name
        self.signal_groups = {}              # Signal group objects indexed by signal group_name
        self.tp_config = _FlexrayTpConfig()
        self.cluster_config = _ClusterConfig()
        self.type = 'FLEXRAY'

        self.hTableOfFrames = self.frames   # frarray indexed by frame.name
        self.hTableOfPDUs = {}              # 2D of PDUs indexed by [frameName]+list
        self.hTableOfSignals = {}           # 2D of signals indexed by [frameName]+list
        self.hTableOfSignals3 = {}          # 2D of signals indexed by [PDUname]+list
        self.hTableOfOffsets = {}           # 2D of offsets (base) indexed by [slotID]+dict

    def get_bitpos(self, signal):
        """
        Return bitpos of the signal converted to the format used in
        Fibex v2.x (lowest bit of first byte).

        Arguments:
            signal (_Signal)
        """
        if signal.endianness:   # Motorola
            return self._bitpos_3_to_2(signal)
        else:
            return signal.bitpos

    @staticmethod
    def _bitpos_3_to_2(signal):
        '''
        Description: Converts the bit position format of a signal from 
        ECU Extract to the one used in Fibex version 2.x.
        Parameter 'signal' is an object of class Signal.
        Returns the converted bit position (Start bit) value
        '''
        byte_pos = signal.bitpos / 8
        b_l = 8*byte_pos  # lsb (bit) of the LSB (byte)
        bitpos2 = signal.bitpos - signal.coding.bit_length + 1

        if signal.coding.bit_length <= 8:
            # Check if data is divided in two bytes
            if bitpos2 >= b_l:
                # Data in 1 byte
                bitpos = signal.bitpos - signal.coding.bit_length + 1
            else:
                # Data divided in two bytes
                bits2 = b_l - bitpos2
                b_h2 = 8*(byte_pos + 1) + 7
                bitpos = b_h2 - bits2 + 1

        else:
            # Calculate number of bytes
            bits2 = b_l - bitpos2   # Number of bits not in LSB
            n_bytes = 1 + bits2 / 8
            if bits2 % 8:
                n_bytes += 1

            bl = 8*(signal.bitpos / 8) + 7      # msb (bit) of the LSB (byte) (right)
            br = bl + 8*(n_bytes - 1)           # msb (bit) of the MSB (byte) (left)

            el = bl - signal.bitpos  # Empty bits left
            er = n_bytes*8 - signal.coding.bit_length - el  # Empty bits right

            bitpos = br - (7 - er)

        return bitpos

    @staticmethod
    def create_empty_frame():
        frame = _Frame()
        return frame


class _CanCluster(object):
    """
    Can Cluster information: frames, PDUs, signals, signal groups
    """
    def __init__(self):
        self.frames = {}
        self.pdus = {}
        self.signals = {}
        self.tp_connections = []    # List of CanTPC objects
        self.signal_groups = {}
        self.type = 'CAN'

        self.hTableOfFrames = {}   # array frame indexed by frame.name
        self.hTableOfSignals = {}  # 2D of signals indexed by [name]+list
        self.framesStore = {}
        self.framesDict = {}
        self.lines = ''


class _FlexrayTpConnection(object):
    """
    FlexRay Transport Protocol Connection information
    """
    def __init__(self):
        self.bandwidth_limitation = False
        self.direct_sdu = ''
        self.reversed_sdu = ''
        self.rx_tp_pool = ''
        self.tx_tp_pool = ''
        self.transmitter = ''
        self.receiver = []
        self.multicast_ref = ''


class _FlexrayTpConfig(object):
    """
    FlexRay Transport Protocol Configuration information
    """
    def __init__(self):
        self.tp_pools = {}          # Lists of N-PDUs indexed by tp-pdu-pool name
        self.tp_connections = []    # List of FlexrayTpConnection objects
        self.tp_addresses= {}       # List of TP-ADDRESSES indexed by tp-address name
        self.tp_nodes = {}          # Lists of tp-address refs indexed by tp-node name


class _CanTPC(object):
    """
    CAN Transport Protocol Connection information
    """
    def __init__(self):
        self.addressing_format = ''
        self.data_pdu = ''
        self.flow_control_pdu = ''
        self.tp_sdu = ''
        self.transmitter = ''
        self.receiver = []


class _CanFrame(object):
    name = ''
    canid = 0
    dlc = 0
    publisher = ''
    cycleTime = 0


class _CanSignal(object):
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


class ECUextract(object):
    """
    Class for reading ECU Extract files, set cluster configuration and access frames and signals.

    Its main child variables are:

        self.clusters_dict:
            Dictionary of clusters (buses) with the corresponding frames, PDUs, signal groups and signals.
        self.pduGatewayList:
            Mapping information of gateway PDUs.
        self.signalGatewayList:
            Mapping inrformation of gateway Signals.
    """
    def __init__(self, arxml_file):

        # set ElementTree parameters
        try:
            self.tree = ET.parse(arxml_file)
        except IOError:
            print 'Error trying to open \'' + arxml_file + '\' file.'
            sys.exit()

        self.root = self.tree.getroot()

        database_type = self.root.tag.split('}')[-1]
        if database_type != "AUTOSAR":
            print 'Error: ' + arxml_file + " is a " + database_type + " file. An AUTOSAR (ECU Extract) file is needed."
            raise IOError()

        # Dictionaries and lists
        self.signal_gtw_dict = {}
        self.pdu_gtw_dict = {}
        self.frame_gtw_dict = {}
        self.compu_methods_dict = {}
        self.units_dict = {}
        self.signal_dict = {}               # Intermediate dictionary of signals
        self.pdu_dict = {}
        self.flexray_frames_dict = {}
        self.can_frames_dict = {}
        self.signal_group_dict = {}         # Intermediate dictionary of signal groups
        self.pduGatewayList = []
        self.signalGatewayList = []
        self.clusters_dict = {}
        self.input_signals_dict  ={}
        self.output_signals_dict = {}
        self.input_signal_groups_dict  ={}
        self.output_signal_groups_dict = {}
        self.flexray_clusters_ordered = []  # List used to relate clusters and controllers
                                            # (they appear in the arxml in the same order)

        # ECU name
        self.name = ''
        self._get_ecu_name()

        # All FlexRay Slot IDs
        self.key_slot_ids = []

        # Get cluster and controller information
        self._set_fr_cluster_config()
        self._set_fr_controller_config()

        # Get frame, signal, PDU and routing information
        self._get_computation_methods()
        self._get_units()
        self._get_i_signals()
        self._get_i_signal_groups()
        self._get_pdus("I-SIGNAL-I-PDU")
        self._get_pdus("DCM-I-PDU")
        self._get_pdus("N-PDU")
        self._get_pdus("NM-PDU")
        self._get_pdus("XCP-PDU")
        self._get_frames("FLEXRAY")
        self._get_frames("CAN")
        self._set_frame_signal_instances(self.flexray_frames_dict)
        self._set_frame_signal_instances(self.can_frames_dict)
        self._get_frame_triggering_info()
        self._get_pdu_routings()
        self._get_signal_routings()
        self._get_flexray_tp_config()
        self._get_can_tp_config()
        self._get_gateway_pdu_frames()
        self._get_gateway_signal_frames()
        self._get_fr_gateway_addresses()
        self._get_response_pdu()

        # Fill hTableOf_ to have compatibility with FLEXRAY (fry.py) and CAN (can.py)
        self._fill_flexray_tables()
        self._fill_can_tables()

    def set_startup_config(self, cluster_name, fr_channel, cold_start_slots):
        """
        Sets the startup configuration for a FlexRay bus. It looks for the STARTUP-SYNC ECUs
        and sets the erayID and coldID (slot IDs used to send startup and sync frames).

        Arguments:
            cluster_name (str): name of the cluster to configure
            fr_channel (str): FlexRay channel used to start communication ("A", "B" or "AB")
            cold_start_slots (list): slot IDs used to send startup and sync frames

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> ecu.set_startup_config("Front2Flx", "A", [1])

        Note:
            This function should only be called once per cluster configuration

        """
        # Get cluster configuration
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            print "Error. Cluster not found."
            return

        cluster_config = cluster.cluster_config

        # Setup correct FlexRay Channel to start communication
        if 'AB' in fr_channel:
            cluster_config.erayChannel = 3
        elif 'B' in fr_channel:
            cluster_config.erayChannel = 2
        else:
            cluster_config.erayChannel = 1

        # Set startup CC parameters
        configured_coldStart_slots = 0
        found_coldStart_slots = []

        for slot_id in self.key_slot_ids:   # All Slot IDs
            for coldStartMessage in cold_start_slots:
                if cluster_config.erayID == 0:
                    if slot_id == coldStartMessage:
                        cluster_config.erayID = slot_id
                        configured_coldStart_slots = configured_coldStart_slots + 1
                elif cluster_config.coldID == 0:
                    if slot_id == coldStartMessage:
                        cluster_config.coldID = slot_id
                        configured_coldStart_slots = configured_coldStart_slots + 1

            found_coldStart_slots.append(slot_id)

        if configured_coldStart_slots != len(cold_start_slots):
            print 'Configured ColdStart slots ' + str(cold_start_slots) + ' are not defined in AUTOSAR file'
            print 'Available ColdStart slots in AUTOSAR file are: ' + str(found_coldStart_slots)
            return

        for frame_name, frame in cluster.frames.iteritems():
            if frame.slot_id[0] == cluster_config.erayID:
                cluster_config.eray_repetition = frame.repetition
                cluster_config.eray_offset = frame.offset

    def look_for_pdu(self, pdu_name, cluster_name):
        """
        Finds the PDU containing pdu=pdu_name in the cluster (bus)
        specified by cluster_name.

        Arguments:
            pdu_name (str)
            cluster_name (str)

        Returns:
            _PDU object

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> f,p = ecu.look_for_frame_and_pdu("VcmVgmToTacmDiagDcmIpdu", "Backbone")

        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None, None

        pdu = cluster.pdus.get(pdu_name)

        return pdu

    def look_for_frame_and_signal(self, signal_name, cluster_name):
        """
        Finds the frame containing signal=signal_name in the cluster (bus)
        specified by cluster_name.

        Arguments:
            signal_name (str)
            cluster_name (str)

        Returns:
            found _Frame and _Signal objects

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> f,s = ecu.look_for_frame_and_signal('isChrgMod', 'Front1CAN')
        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return (None, None)

        signal = cluster.signals.get(signal_name)

        for frame_name, frame in cluster.frames.iteritems():
            for s in frame.signal_instances:
                if s == signal_name:
                    return frame, signal

        return None, signal

    def look_for_frame_and_signal_group(self, signal_group_name, cluster_name):
        """
        Finds the frame containing signal_group=signal_group_name in
        the cluster (bus) specified by cluster_name.

        Arguments:
            signal_group_name (str)
            cluster_name (str)

        Returns:
            found _Frame and _Signal objects

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> f,sg = ecu.look_for_frame_and_signal_group('igBrkTq', 'Front1CAN')
        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return (None, None)

        signal_group = cluster.signal_groups.get(signal_group_name)
        if signal_group:
            signal_name = signal_group.signal_instances[0]
            for frame_name, frame in cluster.frames.iteritems():
                for s in frame.signal_instances:
                    if s == signal_name:
                        return frame, signal_group

            return None, signal_group

        else:
            print 'Error: signal group {} not found in {} database'.format(signal_group_name, cluster_name)
            return None, None

    def look_for_frame_and_pdu(self, pdu_name, cluster_name):
        """
        Finds the frame and PDU containing pdu=pdu_name in the cluster (bus)
        specified by cluster_name.

        Arguments:
            pdu_name (str)
            cluster_name (str)

        Returns:
            found _Frame and _PDU objects

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> f,p = ecu.look_for_frame_and_pdu('VCMBackboneSignalIPdu00', 'Backbone')

        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None, None

        pdu = cluster.pdus.get(pdu_name)

        for f_name, frame in cluster.frames.iteritems():
            for p in frame.pdu_instances:
                if p == pdu_name:
                    return frame, pdu

        return None, pdu

    def look_for_frame(self, frame_name, cluster_name):
        """
        Finds the frame in the cluster (bus) specified by cluster_name.

        Arguments:
            frame_name (str)
            cluster_name (str)

        Returns:
            found _Frame

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> f = ecu.look_for_frame('AsdmBackBoneFr01', 'Backbone')

        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None

        return cluster.frames.get(frame_name)

    def _can_pdu_from_id(self, frame_id, cluster_name):
        """
        Get the name of the CAN PDU corresponding to the specified
        frame ID.

        Arguments:
            frame_id (int): frame id
            cluster_name (str): name of the cluster containing the PDUs

        Returns:
            (str) Name of the corresponding PDU

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> npdu = ecu._can_pdu_from_id(1713, "Rear1CAN")
        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None

        for frame_name, frame in cluster.frames.iteritems():
            if frame.frame_id == frame_id:
                return frame.pdu_instances[0]

    def _can_npdu_to_ipdu(self, npdu_name, cluster_name):
        """
        Get the I-PDU name corresponding to the N-PDU of a CAN frame using information
        from the TP connections.

        Arguments:
            npdu_name (str): name of the N-PDU
            cluster_name (str): name of the cluster containing the PDUs

        Returns:
            (str) Name of the corresponding I-PDU

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> ipdu = ecu._can_npdu_to_ipdu("MvbmToVcu1Rear1DiagResNpdu", "Rear1CAN")
        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None

        for tpc in cluster.tp_connections:
            if tpc.data_pdu == npdu_name:
                return tpc.tp_sdu

    def _can_ipdu_to_npdu(self, ipdu_name, cluster_name):
        """
        Get the N-PDU name corresponding to the I-PDU of a CAN frame using information
        from the TP connections.

        Arguments:
            ipdu_name (str): name of the I-PDU
            cluster_name (str): name of the cluster containing the PDUs

        Returns:
            (str) Name of the corresponding N-PDU

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> ipdu = ecu._can_ipdu_to_npdu("MvbmToVcmVgmDiagDcmIpdu", "Rear1CAN")
        """
        cluster = self.clusters_dict.get(cluster_name)
        if cluster is None:
            return None

        for tpc in cluster.tp_connections:
            if tpc.tp_sdu == ipdu_name:
                return tpc.data_pdu

    def _flexray_ipdu_to_npdus(self, gtw_bus, gtw_pdu, direction):
        """
        Get a list of N-PDUs from the RX/TX Pool corresponding
        to the specified Gateway I-PDU.

        Arguments:
            gtw_bus (str): name of the FlexRay bus
            gtw_pdu (str): name of the PDU
            direction (str): 'target' or 'source'

        Returns:
            (tuple): tuple containing:

                npdus (list)
                TP address (int)

        Example:
            >>> ecu = ECUextract('SystemExtract.arxml')
            >>> npdus = ecu._flexray_idu_to_npdus("Backbone", "MvbmToVcmVgmDiagDcmIpdu", "target")
        """
        cluster = self.clusters_dict.get(gtw_bus)
        pool = ''

        for tpc in cluster.tp_config.tp_connections:
            if tpc.direct_sdu == gtw_pdu or tpc.reversed_sdu == gtw_pdu:
                if self.name.lower() in tpc.transmitter.lower():    # Only nodes regarding the used ECU. This
                                                                    # shall be improved
                    if direction == "target":
                        pool = tpc.tx_tp_pool
                    elif direction == "source":
                        pool = tpc.rx_tp_pool
                else:
                    for rcv in tpc.receiver:
                        if self.name.lower() in rcv.lower():
                            if direction == "target":
                                pool = tpc.rx_tp_pool
                            elif direction == "source":
                                pool = tpc.tx_tp_pool
                            break

        npdus = cluster.tp_config.tp_pools.get(pool)
        return npdus

    def _get_ecu_name(self):
        """
        Gets the name of the ECU described in the ECU extract file and
        saves it in the self.ecu variable.
        """
        ecu_instance = self.root.find(".//{http://autosar.org/schema/r4.0}ECU-INSTANCE")
        ecu_name = ecu_instance.find("{http://autosar.org/schema/r4.0}SHORT-NAME")
        self.name = ecu_name.text

    def _set_fr_cluster_config(self):
        """
        Reads AUTOSAR file and sets the general FlexRay cluster configuration parameters.
        """
        fr_clusters = self.root.findall(".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}FLEXRAY-CLUSTER")

        for c in fr_clusters:
            cluster_config = _ClusterConfig()

            c_name = c.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            cluster = c.find("{http://autosar.org/schema/r4.0}FLEXRAY-CLUSTER-VARIANTS/{http://autosar.org/schema/r4.0}FLEXRAY-CLUSTER-CONDITIONAL")

            # Read cluster section of the AUTOSAR config file
            speed = cluster.find('{http://autosar.org/schema/r4.0}SPEED')
            if speed is not None:
                cluster_config.baudrate = int(speed.text)

            coldStartAttempts = cluster.find('{http://autosar.org/schema/r4.0}COLD-START-ATTEMPTS')
            cluster_config.gColdStartAttempts = int(coldStartAttempts.text)

            listenNoise = cluster.find('{http://autosar.org/schema/r4.0}LISTEN-NOISE')
            cluster_config.gListenNoise = int(listenNoise.text)

            macroPerCycle = cluster.find('{http://autosar.org/schema/r4.0}MACRO-PER-CYCLE')
            cluster_config.gMacroPerCycle = int(macroPerCycle.text)

            macroPerCycle = cluster.find('{http://autosar.org/schema/r4.0}MACROTICK-DURATION')

            maxWithoutClockCorrectionFatal = cluster.find(
                '{http://autosar.org/schema/r4.0}MAX-WITHOUT-CLOCK-CORRECTION-FATAL')
            cluster_config.gMaxWithoutClockCorrectionFatal = int(maxWithoutClockCorrectionFatal.text)

            maxWithoutClockCorrectionPassive = cluster.find(
                '{http://autosar.org/schema/r4.0}MAX-WITHOUT-CLOCK-CORRECTION-PASSIVE')
            cluster_config.gMaxWithoutClockCorrectionPassive = int(maxWithoutClockCorrectionPassive.text)

            networkManagementVectorLength = cluster.find('{http://autosar.org/schema/r4.0}NETWORK-MANAGEMENT-VECTOR-LENGTH')
            cluster_config.gNetworkManagementVectorLength = int(networkManagementVectorLength.text)

            numberOfMinislots = cluster.find('{http://autosar.org/schema/r4.0}NUMBER-OF-MINISLOTS')
            cluster_config.gNumberOfMinislots = int(numberOfMinislots.text)

            numberOfStaticSlots = cluster.find('{http://autosar.org/schema/r4.0}NUMBER-OF-STATIC-SLOTS')
            cluster_config.gNumberOfStaticSlots = int(numberOfStaticSlots.text)

            offsetCorrectionStart = cluster.find('{http://autosar.org/schema/r4.0}OFFSET-CORRECTION-START')
            cluster_config.gOffsetCorrectionStart = int(offsetCorrectionStart.text)

            payloadLengthStatic = cluster.find('{http://autosar.org/schema/r4.0}PAYLOAD-LENGTH-STATIC')
            cluster_config.gPayloadLengthStatic = int(payloadLengthStatic.text)

            syncNodeMax = cluster.find('{http://autosar.org/schema/r4.0}SYNC-FRAME-ID-COUNT-MAX')
            cluster_config.gSyncNodeMax = int(syncNodeMax.text)

            actionPointOffset = cluster.find('{http://autosar.org/schema/r4.0}ACTION-POINT-OFFSET')
            cluster_config.gdActionPointOffset = int(actionPointOffset.text)

            dynamicSlotIdlePhase = cluster.find('{http://autosar.org/schema/r4.0}DYNAMIC-SLOT-IDLE-PHASE')
            cluster_config.gdDynamicSlotIdlePhase = int(dynamicSlotIdlePhase.text)

            minislot = cluster.find('{http://autosar.org/schema/r4.0}MINISLOT-DURATION')
            cluster_config.gdMinislot = int(minislot.text)

            miniSlotActionPointOffset = cluster.find('{http://autosar.org/schema/r4.0}MINISLOT-ACTION-POINT-OFFSET')
            cluster_config.gdMiniSlotActionPointOffset = int(miniSlotActionPointOffset.text)

            NIT = cluster.find('{http://autosar.org/schema/r4.0}NETWORK-IDLE-TIME')
            cluster_config.gdNIT = int(NIT.text)

            staticSlot = cluster.find('{http://autosar.org/schema/r4.0}STATIC-SLOT-DURATION')
            cluster_config.gdStaticSlot = int(staticSlot.text)

            symbolWindow = cluster.find('{http://autosar.org/schema/r4.0}SYMBOL-WINDOW')
            cluster_config.gdSymbolWindow = int(symbolWindow.text)

            TSSTransmitter = cluster.find('{http://autosar.org/schema/r4.0}TRANSMISSION-START-SEQUENCE-DURATION')
            cluster_config.gdTSSTransmitter = int(TSSTransmitter.text)

            rxidle = cluster.find('{http://autosar.org/schema/r4.0}WAKEUP-RX-IDLE')
            cluster_config.gdWakeupSymbolRxIdle = int(rxidle.text)

            rxlow = cluster.find('{http://autosar.org/schema/r4.0}WAKEUP-RX-LOW')
            cluster_config.gdWakeupSymbolRxLow = int(rxlow.text)

            rxwindow = cluster.find('{http://autosar.org/schema/r4.0}WAKEUP-RX-WINDOW')
            cluster_config.gdWakeupSymbolRxWindow = int(rxwindow.text)

            txidle = cluster.find('{http://autosar.org/schema/r4.0}WAKEUP-TX-IDLE')
            cluster_config.gdWakeupSymbolTxIdle = int(txidle.text)

            txlow = cluster.find('{http://autosar.org/schema/r4.0}WAKEUP-TX-ACTIVE')
            cluster_config.gdWakeupSymbolTxLow = int(txlow.text)

            CASRxLowMax = cluster.find('{http://autosar.org/schema/r4.0}CAS-RX-LOW-MAX')
            cluster_config.gdCASRxLowMax = int(CASRxLowMax.text)

            self.clusters_dict[c_name] = _FlexRayCluster()
            self.clusters_dict[c_name].cluster_config = cluster_config

            self.flexray_clusters_ordered.append(c_name)

    def _set_fr_controller_config(self):
        """
        Reads AUTOSAR file and sets the FlexRay controller configuration parameters.
        """
        fr_controllers = self.root.findall('.//{http://autosar.org/schema/r4.0}FLEXRAY-COMMUNICATION-CONTROLLER')

        cluster_index = 0

        for c in fr_controllers:
            cluster_name = self.flexray_clusters_ordered[cluster_index]
            cluster_config = self.clusters_dict.get(cluster_name).cluster_config
            cluster_index += 1

            controller = c.find("{http://autosar.org/schema/r4.0}FLEXRAY-COMMUNICATION-CONTROLLER-VARIANTS/" +
                             "{http://autosar.org/schema/r4.0}FLEXRAY-COMMUNICATION-CONTROLLER-CONDITIONAL")

            # Read controller section of the AUTOSAR config file
            clusterDriftDamping = controller.find('{http://autosar.org/schema/r4.0}CLUSTER-DRIFT-DAMPING')
            cluster_config.pClusterDriftDamping = int(clusterDriftDamping.text)

            decodingCorrection = controller.find('{http://autosar.org/schema/r4.0}DECODING-CORRECTION')
            cluster_config.pDecodingCorrection = int(decodingCorrection.text)

            externOffsetCorrection = controller.find('{http://autosar.org/schema/r4.0}EXTERN-OFFSET-CORRECTION')
            cluster_config.pExternOffsetCorrection = int(externOffsetCorrection.text)

            externRateCorrection = controller.find('{http://autosar.org/schema/r4.0}EXTERN-RATE-CORRECTION')
            cluster_config.pExternRateCorrection = int(externRateCorrection.text)

            latestTx = controller.find('{http://autosar.org/schema/r4.0}LATEST-TX')
            cluster_config.pLatestTx = int(latestTx.text)

            microPerCycle = controller.find('{http://autosar.org/schema/r4.0}MICRO-PER-CYCLE')
            cluster_config.pMicroPerCycle = int(microPerCycle.text)

            delayCompensationA = controller.find('{http://autosar.org/schema/r4.0}DELAY-COMPENSATION-A')
            cluster_config.pDelayCompensationA = int(delayCompensationA.text)

            delayCompensationB = controller.find('{http://autosar.org/schema/r4.0}DELAY-COMPENSATION-B')
            cluster_config.pDelayCompensationB = int(delayCompensationB.text)

            wakeupPattern = controller.find('{http://autosar.org/schema/r4.0}WAKE-UP-PATTERN')
            cluster_config.pWakeupPattern = int(wakeupPattern.text)

            microPerMacroNom = controller.find('{http://autosar.org/schema/r4.0}MICRO-PER-MACRO-NOM')
            if microPerMacroNom is not None:
                try:
                    cluster_config.pMicroPerMacroNom = int(microPerMacroNom.text)
                except ValueError:
                    cluster_config.pMicroPerMacroNom = int(float(microPerMacroNom.text))

            maxPayloadLengthDynamic = controller.find('{http://autosar.org/schema/r4.0}MAXIMUM-DYNAMIC-PAYLOAD-LENGTH')
            cluster_config.pMaxPayloadLengthDynamic = int(maxPayloadLengthDynamic.text)

            offsetCorrectionOut = controller.find('{http://autosar.org/schema/r4.0}OFFSET-CORRECTION-OUT')
            cluster_config.pOffsetCorrectionOut = int(offsetCorrectionOut.text)

            rateCorrectionOut = controller.find('{http://autosar.org/schema/r4.0}RATE-CORRECTION-OUT')
            cluster_config.pRateCorrectionOut = int(rateCorrectionOut.text)

            allowHaltDueToClock = controller.find('{http://autosar.org/schema/r4.0}ALLOW-HALT-DUE-TO-CLOCK')
            if str(allowHaltDueToClock.text) == 'false':
                cluster_config.pAllowHaltDueToClock = 0
            elif str(allowHaltDueToClock.text) == 'true':
                cluster_config.pAllowHaltDueToClock = 1

            allowPassiveToActive = controller.find('{http://autosar.org/schema/r4.0}ALLOW-PASSIVE-TO-ACTIVE')
            cluster_config.pAllowPassiveToActive = int(allowPassiveToActive.text)

            acceptedStartupRange = controller.find('{http://autosar.org/schema/r4.0}ACCEPTED-STARTUP-RANGE')
            cluster_config.pdAcceptedStartupRange = int(acceptedStartupRange.text)

            macroInitialOffsetA = controller.find('{http://autosar.org/schema/r4.0}MACRO-INITIAL-OFFSET-A')
            cluster_config.pMacroInitialOffsetA = int(macroInitialOffsetA.text)

            macroInitialOffsetB = controller.find('{http://autosar.org/schema/r4.0}MACRO-INITIAL-OFFSET-B')
            cluster_config.pMacroInitialOffsetB = int(macroInitialOffsetB.text)

            microInitialOffsetA = controller.find('{http://autosar.org/schema/r4.0}MICRO-INITIAL-OFFSET-A')
            cluster_config.pMicroInitialOffsetA = int(microInitialOffsetA.text)

            microInitialOffsetB = controller.find('{http://autosar.org/schema/r4.0}MICRO-INITIAL-OFFSET-B')
            cluster_config.pMicroInitialOffsetB = int(microInitialOffsetB.text)

            listenTimeout = controller.find('{http://autosar.org/schema/r4.0}LISTEN-TIMEOUT')
            cluster_config.pdListenTimeout = int(listenTimeout.text)

            cluster_config.pdMaxDrift = cluster_config.pRateCorrectionOut     # MaxDrift not in ECU extract!

            key_slot_id = int(controller.find('{http://autosar.org/schema/r4.0}KEY-SLOT-ID').text)
            cluster_config.key_slot_ids.append(key_slot_id)

            second_key_slot_id = int(controller.find('{http://autosar.org/schema/r4.0}SECOND-KEY-SLOT-ID').text)
            if second_key_slot_id:
                cluster_config.key_slot_ids.append(second_key_slot_id)

        key_slots = self.root.findall('.//{http://autosar.org/schema/r4.0}KEY-SLOT-ID')
        for slot in key_slots:
            self.key_slot_ids.append(int(slot.text))

    def _get_computation_methods(self):
        """
        Get computation methods information and populate dictionary of compu_methods
        """
        compu_methods = self.root.findall(".//{http://autosar.org/schema/r4.0}COMPU-METHOD")

        for c in compu_methods:
            current_coding = _Coding()
            current_coding.coding_name = c.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            current_coding.computation_method = c.find("{http://autosar.org/schema/r4.0}CATEGORY").text
            unit_ref = c.find("{http://autosar.org/schema/r4.0}UNIT-REF")
            if unit_ref is None:
                current_coding.unit_ref = 'NoUnit'
            else:
                current_coding.unit_ref = unit_ref.text.split('/')[-1]

            if current_coding.computation_method == "LINEAR":
                compu_scales = c.find("{http://autosar.org/schema/r4.0}COMPU-INTERNAL-TO-PHYS/" +
                                      "{http://autosar.org/schema/r4.0}COMPU-SCALES")

                for scale in compu_scales:
                    compu_coeffs =  scale.find("{http://autosar.org/schema/r4.0}COMPU-RATIONAL-COEFFS")
                    numerator = compu_coeffs.find("{http://autosar.org/schema/r4.0}COMPU-NUMERATOR")
                    denominator = compu_coeffs.find("{http://autosar.org/schema/r4.0}COMPU-DENOMINATOR")

                    current_coding.compu_numerator[0] = float(numerator[0].text)
                    current_coding.compu_numerator[1] = float(numerator[1].text)
                    current_coding.compu_denominator =  float(denominator[0].text)

            elif current_coding.computation_method == "TEXTTABLE":
                compu_scales = c.find("{http://autosar.org/schema/r4.0}COMPU-INTERNAL-TO-PHYS/" +
                                      "{http://autosar.org/schema/r4.0}COMPU-SCALES")

                for scale in compu_scales:
                    key =  int(scale.find("{http://autosar.org/schema/r4.0}LOWER-LIMIT").text)
                    value = scale.find("{http://autosar.org/schema/r4.0}COMPU-CONST/{http://autosar.org/schema/r4.0}VT")

                    current_coding.text_table[key] = value.text

            self.compu_methods_dict[current_coding.coding_name] = current_coding

    def _get_units(self):
        """
        Get units information and populate dictionary of units
        """
        units = self.root.findall(".//{http://autosar.org/schema/r4.0}UNIT")

        for unit in units:
            current_unit = _Unit()
            current_unit.display = unit.find("{http://autosar.org/schema/r4.0}DISPLAY-NAME").text
            current_unit.unit_name = unit.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text

            self.units_dict[current_unit.unit_name] = current_unit

    def _get_i_signals(self):
        """
        Get signal information and populate "intermediate" dictionary of signals.
        Parsed information: signal name, length, value, computation method.
        """
        i_signals = self.root.findall(
            ".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}I-SIGNAL")

        for signal in i_signals:
            current_signal = _Signal()
            current_signal.signalName = signal.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            current_signal.coding.bit_length = int(signal.find("{http://autosar.org/schema/r4.0}LENGTH").text)
            current_signal.coding.constraints = 2**current_signal.coding.bit_length - 1

            init_value = signal.find("{http://autosar.org/schema/r4.0}INIT-VALUE")
            if init_value is not None:
                current_signal.value = int(init_value.find(
                    "{http://autosar.org/schema/r4.0}NUMERICAL-VALUE-SPECIFICATION").find(
                    "{http://autosar.org/schema/r4.0}VALUE").text)

            compu_method_ref = signal.find(".//{http://autosar.org/schema/r4.0}COMPU-METHOD-REF").text.split('/')[-1]

            found_compu = self.compu_methods_dict.get(compu_method_ref)
            current_signal.coding.coding_name = found_compu.coding_name
            current_signal.coding.computation_method = found_compu.computation_method
            current_signal.coding.compu_numerator = found_compu.compu_numerator
            current_signal.coding.compu_denominator = found_compu.compu_denominator
            current_signal.coding.text_table = found_compu.text_table

            found_unit = self.units_dict.get(found_compu.unit_ref)
            current_signal.unit.unit_name = found_unit.unit_name
            current_signal.unit.display = found_unit.display

            self.signal_dict[current_signal.signalName] = current_signal

    def _get_i_signal_groups(self):
        """
        Get signal groups information and populate "intermediate" dictionary of signal groups.
        Parsed information: group name, signal references.
        """
        i_signal_groups = self.root.findall(
            ".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}I-SIGNAL-GROUP")

        for group in i_signal_groups:
            group_name = group.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            signal_refs = group.find("{http://autosar.org/schema/r4.0}I-SIGNAL-REFS")

            self.signal_group_dict[group_name] = _SignalGroup()
            self.signal_group_dict[group_name].group_name = group_name

            for signal in signal_refs:
                signal_name = signal.text.split('/')[3]
                self.signal_group_dict.get(group_name).signal_instances.append(signal_name)

    def _get_pdus(self, pdu_type):
        """
        Get PDU information (name, length, type) and populate dictionary of PDUs
        Get signal to pdu mappings and populate input/output_signal dictionaries

        Arguments:
            pdu_type (str): indicates the type of PDU to look for ("I-SIGNAL-I-PDU",
                        "DCM-I-PDU", "N-PDU", "NM-PDU" or "XCP-PDU")
        """
        if pdu_type != "I-SIGNAL-I-PDU" and pdu_type != "DCM-I-PDU" and pdu_type != "N-PDU" \
                    and pdu_type != "NM-PDU" and pdu_type != "XCP-PDU":
            return

        pdus = self.root.findall(".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}" + pdu_type)

        for pdu in pdus:
            current_pdu = _PDU()

            current_pdu.pdu_type = pdu_type
            current_pdu.pdu_name = pdu.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            current_pdu.pdu_length = int(pdu.find("{http://autosar.org/schema/r4.0}LENGTH").text)

            if pdu_type == "I-SIGNAL-I-PDU":
                mappings = pdu.find("{http://autosar.org/schema/r4.0}I-SIGNAL-TO-PDU-MAPPINGS")
                pdu_timing = pdu.find("{http://autosar.org/schema/r4.0}I-PDU-TIMING-SPECIFICATIONS/{http://autosar.org/schema/r4.0}I-PDU-TIMING")

                # Cycle Time
                if pdu_timing is not None:
                    time_period = pdu_timing.find(".//{http://autosar.org/schema/r4.0}TIME-PERIOD")
                    if time_period is not None:
                        value = float(time_period.find("{http://autosar.org/schema/r4.0}VALUE").text)
                        cycleTime = int(value*1000)
                        current_pdu.cycleTime = cycleTime

                # Signal Mapping
                for signal in mappings:
                    direction = signal.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text[-2:]  # tx or rx
                    updatebit = signal.find("{http://autosar.org/schema/r4.0}UPDATE-INDICATION-BIT-POSITION")
                    packing_order = signal.find("{http://autosar.org/schema/r4.0}PACKING-BYTE-ORDER").text
                    bitpos = int(signal.find("{http://autosar.org/schema/r4.0}START-POSITION").text)

                    signal_ref = signal.find('{http://autosar.org/schema/r4.0}I-SIGNAL-REF')
                    if signal_ref is not None:
                        current_signal = _Signal()
                        signal_name = signal_ref.text.split('/')[-1]

                        # Copy values from already saved signal
                        found_signal = self.signal_dict.get(signal_name)
                        current_signal.signalName = found_signal.signalName
                        current_signal.value = found_signal.value
                        current_signal.coding.bit_length = found_signal.coding.bit_length
                        current_signal.coding.constraints = found_signal.coding.constraints
                        current_signal.coding.coding_name = found_signal.coding.coding_name
                        current_signal.coding.computation_method =  found_signal.coding.computation_method
                        current_signal.coding.compu_numerator = found_signal.coding.compu_numerator
                        current_signal.coding.compu_denominator = found_signal.coding.compu_denominator
                        current_signal.coding.text_table = found_signal.coding.text_table
                        current_signal.unit.unit_name = found_signal.unit.unit_name
                        current_signal.unit.display = found_signal.unit.display

                        # Add new information
                        current_signal.bitpos = bitpos
                        current_signal.bytepos /= 8
                        current_signal.bitpos_in_pdu = bitpos

                        if updatebit is not None:
                            current_signal.updatebit = int(updatebit.text)

                        if packing_order == "MOST-SIGNIFICANT-BYTE-FIRST":
                            current_signal.endianness = 1
                        else:
                            current_signal.endianness = 0

                        if direction == "tx":
                            self.output_signals_dict[signal_name] = current_signal
                        else:
                            self.input_signals_dict[signal_name] = current_signal

                        current_pdu.signal_instances.append(signal_name)

                    # Signal Group
                    else:
                        current_group = _SignalGroup()
                        signal_group_ref = signal.find('{http://autosar.org/schema/r4.0}I-SIGNAL-GROUP-REF')
                        signal_group_name = signal_group_ref.text.split('/')[-1]

                        # Copy values from already saved signal group
                        found_group = self.signal_group_dict.get(signal_group_name)
                        current_group.group_name = found_group.group_name
                        current_group.signal_instances = found_group.signal_instances

                        # Add new information
                        current_group.bitpos = bitpos
                        current_group.bytepos /= 8

                        if updatebit is not None:
                            current_group.updatebit = int(updatebit.text)

                        if packing_order == "MOST-SIGNIFICANT-BYTE-FIRST":
                            current_group.endianness = 1
                        else:
                            current_group.endianness = 0

                        if direction == "tx":
                            self.output_signal_groups_dict[signal_group_name] = current_group
                        else:
                            self.input_signal_groups_dict[signal_group_name] = current_group

                        # current_pdu.signal_instances.append(signal_name)

            self.pdu_dict[current_pdu.pdu_name] = current_pdu

    def _get_pdu_routings(self):
        """
         Get PDU routing information and populate pduGatewayList
        """
        gtw_pdus = self.root.findall(".//{http://autosar.org/schema/r4.0}GATEWAY/{http://autosar.org/schema/r4.0}I-PDU-MAPPINGS/{http://autosar.org/schema/r4.0}I-PDU-MAPPING")

        for gtw_pdu_elem in gtw_pdus:
            pdu_gtw_inform = pduGtwObject()

            pdu_gtw_inform.source_gtw_bus = gtw_pdu_elem.find(".//{http://autosar.org/schema/r4.0}SOURCE-I-PDU-REF").text.split('/')[3]
            pdu_gtw_inform.source_gtw_pdu = gtw_pdu_elem.find(".//{http://autosar.org/schema/r4.0}SOURCE-I-PDU-REF").text.split('/')[5][5:]
            pdu_gtw_inform.target_gtw_bus = gtw_pdu_elem.find(".//{http://autosar.org/schema/r4.0}TARGET-I-PDU-REF").text.split('/')[3]
            pdu_gtw_inform.target_gtw_pdu = gtw_pdu_elem.find(".//{http://autosar.org/schema/r4.0}TARGET-I-PDU-REF").text.split('/')[5][5:]

            self.pduGatewayList.append(pdu_gtw_inform)

    def _get_signal_routings(self):
        """
         Get signal routing information and populate signalGatewayList
        """
        gtw_sign = self.root.findall(".//{http://autosar.org/schema/r4.0}GATEWAY/{http://autosar.org/schema/r4.0}SIGNAL-MAPPINGS/{http://autosar.org/schema/r4.0}I-SIGNAL-MAPPING")
        signalGatewayList = []

        for gtw_sign_elem in gtw_sign:
            signal_gtw_inform = signalGtwObject()

            signal_gtw_inform.source_gtw_bus = gtw_sign_elem.find(".//{http://autosar.org/schema/r4.0}SOURCE-SIGNAL-REF").text.split('/')[3]
            signal_gtw_inform.source_gtw_signal = gtw_sign_elem.find(".//{http://autosar.org/schema/r4.0}SOURCE-SIGNAL-REF").text.split('/')[5][4:][:-2]
            signal_gtw_inform.target_gtw_bus = gtw_sign_elem.find(".//{http://autosar.org/schema/r4.0}TARGET-SIGNAL-REF").text.split('/')[3]
            signal_gtw_inform.target_gtw_signal = gtw_sign_elem.find(".//{http://autosar.org/schema/r4.0}TARGET-SIGNAL-REF").text.split('/')[5][4:][:-2]

            # Source signals
            self._set_gtw_signal_ub(signal_gtw_inform, "source")

            # Target signals
            self._set_gtw_signal_ub(signal_gtw_inform, "target")

            self.signalGatewayList.append(signal_gtw_inform)

    def _set_gtw_signal_ub(self, gtw_signal, direction):
        """
        Sets the update bit signal parameter of the given gateway signal.
        It uses information from the clusters stored in self.clusters_dict.

        Arguments:
            gtw_signal (signalGtwObject)
            direction (str): identifies the direction of the signal ("source" or "target")
        """
        s_name = getattr(gtw_signal, direction + "_gtw_signal")
        c_name = getattr(gtw_signal, direction + "_gtw_bus")
        cluster = self.clusters_dict.get(c_name)

        if s_name in cluster.signals:
            updatebit = cluster.signals.get(s_name).updatebit

        # Signal Group
        else:
            updatebit = cluster.signal_groups.get(s_name).updatebit

        if updatebit is not None:
            setattr(gtw_signal, direction + "_gtw_UBsignal", "YES")
        else:
            setattr(gtw_signal, direction + "_gtw_UBsignal", "NO")

    def _get_frames(self, protocol):
        """
        Get frame information (name, length, pdu instances) and populate tables of frame type (CAN or FlexRay)

        Arguments
            protocol (str): indicates the type of frame to look for (right now only "CAN" or "FLEXRAY")
        """
        if protocol != "CAN" and protocol != "FLEXRAY":
            print protocol + "protocol not supported."
            return

        frames = self.root.findall(".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}" + protocol + "-FRAME")
        for f in frames:
            current_frame = _Frame()

            current_frame.name = f.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            current_frame.length = int(f.find("{http://autosar.org/schema/r4.0}FRAME-LENGTH").text)

            for pdu in f.find("{http://autosar.org/schema/r4.0}PDU-TO-FRAME-MAPPINGS"):
                current_pdu = _PDU()

                current_pdu.pdu_name =  pdu.find("{http://autosar.org/schema/r4.0}PDU-REF").text.split('/')[-1]
                current_pdu.bitpos = int(pdu.find("{http://autosar.org/schema/r4.0}START-POSITION").text)

                packing_order = pdu.find("{http://autosar.org/schema/r4.0}PACKING-BYTE-ORDER").text

                if packing_order == "MOST-SIGNIFICANT-BYTE-FIRST":
                    current_pdu.endianness = 1
                else:
                    current_pdu.endianness = 0

                if current_pdu.pdu_name in self.pdu_dict:
                    saved_pdu = self.pdu_dict.get(current_pdu.pdu_name)
                    saved_pdu.bitpos = current_pdu.bitpos
                    saved_pdu.endianness = current_pdu.endianness

                else:
                    self.pdu_dict[current_pdu.pdu_name] = current_pdu

                current_frame.pdu_instances.append(current_pdu.pdu_name)

            if protocol == "FLEXRAY":
                self.flexray_frames_dict[current_frame.name] = current_frame

            elif protocol == "CAN":
                # Get cycle time
                for pdu in current_frame.pdu_instances:
                    if self.pdu_dict[pdu].cycleTime:
                        current_frame.cycleTime = self.pdu_dict[pdu].cycleTime

                self.can_frames_dict[current_frame.name] = current_frame

    def _set_frame_signal_instances(self, frame_dict):
        """
        Add the signals of a pdu to the signal_instances list of a frame.

        Arguments:
            frame_dict (dict): dictionary of frames indexed by frame name.
        """
        for f_name, frame in frame_dict.iteritems():
            for pdu_name in frame.pdu_instances:
                pdu = self.pdu_dict.get(pdu_name)

                for signal in pdu.signal_instances:
                    # Check to avoid duplicate instances
                    if signal not in frame.signal_instances:
                        frame.signal_instances.append(signal)

            for signal in frame.signal_instances:
                if signal in self.signal_group_dict:        # if signal instance is a signal group
                    frame.signal_instances.remove(signal)   # remove signal group instance

    def _get_frame_triggering_info(self):
        """
        Get frame information from 'FRAME-TRIGGERINGS' and update the saved frame objects.
        Information parsed: transmitter, receiver, slot ID, offset repetition.

        Signals and signal groups are also divided deppending on direction (input or output).
        Assign frames to each bus (cluster) from the self.clusters_dict structure.
        """

        # FlexRay signals, frames and pdus
        fr_clusters = self.root.findall(".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}FLEXRAY-CLUSTER")
        for c in fr_clusters:
            c_name = c.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            cluster = self.clusters_dict.get(c_name)    # Get already saved FlexRay cluster

            phys_channels = c.find(".//{http://autosar.org/schema/r4.0}PHYSICAL-CHANNELS")

            frame_triggerings = phys_channels.find('.//{http://autosar.org/schema/r4.0}FRAME-TRIGGERINGS')

            pdu_triggerings = phys_channels.find('{http://autosar.org/schema/r4.0}FLEXRAY-PHYSICAL-CHANNEL/' +
                                                 '{http://autosar.org/schema/r4.0}PDU-TRIGGERINGS')

            signal_triggerings = phys_channels.find('{http://autosar.org/schema/r4.0}FLEXRAY-PHYSICAL-CHANNEL/' +
                                                    '{http://autosar.org/schema/r4.0}I-SIGNAL-TRIGGERINGS')

            for signal_tr in signal_triggerings:
                signal_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-REF')
                port_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-PORT-REFS/' +
                                          '{http://autosar.org/schema/r4.0}I-SIGNAL-PORT-REF')

                ecu = port_ref.text.split('/')[4]
                direction = port_ref.text.split('/')[6].split('_')[1]   # In our Out

                if signal_ref is not None:
                    signal_name = signal_ref.text.split('/')[-1]

                    if direction == "In":
                        signal = self.input_signals_dict.get(signal_name)
                    else:
                        signal = self.output_signals_dict.get(signal_name)

                    cluster.signals[signal_name] = signal

                # Signal Group
                else:
                    signal_group_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-GROUP-REF')
                    signal_group_name = signal_group_ref.text.split('/')[-1]

                    if direction == "In":
                        signal_group = self.input_signal_groups_dict.get(signal_group_name)
                    else:
                        signal_group = self.output_signal_groups_dict.get(signal_group_name)

                    cluster.signal_groups[signal_group_name] = signal_group

            for pdu_tr in pdu_triggerings:
                pdu_name = pdu_tr.find('{http://autosar.org/schema/r4.0}I-PDU-REF').text.split('/')[-1]

                pdu = self.pdu_dict.get(pdu_name)
                cluster.pdus[pdu_name] = pdu

            for fr_tr in frame_triggerings:
                frame_name = fr_tr.find('{http://autosar.org/schema/r4.0}FRAME-REF').text.split('/')[-1]

                flexray_frame = self.flexray_frames_dict.get(frame_name)

                port_ref = fr_tr.find('{http://autosar.org/schema/r4.0}FRAME-PORT-REFS/' +
                                      '{http://autosar.org/schema/r4.0}FRAME-PORT-REF')

                ecu = port_ref.text.split('/')[4]
                direction = port_ref.text.split('/')[6].split('_')[1]   # In our Out

                if direction == "In":
                    flexray_frame.receiver.append(ecu)

                elif direction == "Out":
                    flexray_frame.transmitter = ecu

                slot_id = int(fr_tr.find(".//{http://autosar.org/schema/r4.0}ABSOLUTELY-SCHEDULED-TIMINGS/" +
                                         "{http://autosar.org/schema/r4.0}FLEXRAY-ABSOLUTELY-SCHEDULED-TIMING/" +
                                         "{http://autosar.org/schema/r4.0}SLOT-ID").text)

                base_cycle = int(fr_tr.find(".//{http://autosar.org/schema/r4.0}ABSOLUTELY-SCHEDULED-TIMINGS/" +
                                            "{http://autosar.org/schema/r4.0}FLEXRAY-ABSOLUTELY-SCHEDULED-TIMING/" +
                                            "{http://autosar.org/schema/r4.0}COMMUNICATION-CYCLE/" +
                                            "{http://autosar.org/schema/r4.0}CYCLE-REPETITION/" +
                                            "{http://autosar.org/schema/r4.0}BASE-CYCLE").text)

                repetition = int(fr_tr.find(".//{http://autosar.org/schema/r4.0}ABSOLUTELY-SCHEDULED-TIMINGS/" +
                                            "{http://autosar.org/schema/r4.0}FLEXRAY-ABSOLUTELY-SCHEDULED-TIMING/" +
                                            "{http://autosar.org/schema/r4.0}COMMUNICATION-CYCLE/" +
                                            "{http://autosar.org/schema/r4.0}CYCLE-REPETITION/" +
                                            "{http://autosar.org/schema/r4.0}CYCLE-REPETITION").text[17:])  # Only the number

                flexray_frame.slot_id.append(slot_id)
                flexray_frame.offset = base_cycle
                flexray_frame.repetition = repetition

                cluster.frames[frame_name] = flexray_frame

        # CAN signals, frames and pdus
        can_clusters = self.root.findall(".//{http://autosar.org/schema/r4.0}ELEMENTS/{http://autosar.org/schema/r4.0}CAN-CLUSTER")
        for c in can_clusters:
            c_name = c.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
            cluster = _CanCluster()

            phys_channels = c.find(".//{http://autosar.org/schema/r4.0}PHYSICAL-CHANNELS")

            frame_triggerings = phys_channels.find('.//{http://autosar.org/schema/r4.0}FRAME-TRIGGERINGS')

            pdu_triggerings = phys_channels.find('{http://autosar.org/schema/r4.0}CAN-PHYSICAL-CHANNEL/' +
                                                 '{http://autosar.org/schema/r4.0}PDU-TRIGGERINGS')

            signal_triggerings = phys_channels.find('{http://autosar.org/schema/r4.0}CAN-PHYSICAL-CHANNEL/' +
                                                    '{http://autosar.org/schema/r4.0}I-SIGNAL-TRIGGERINGS')
            if signal_triggerings is not None:
                for signal_tr in signal_triggerings:
                    port_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-PORT-REFS/' +
                                          '{http://autosar.org/schema/r4.0}I-SIGNAL-PORT-REF')

                    direction = port_ref.text.split('/')[6].split('_')[1]  # In our Out

                    signal_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-REF')
                    if signal_ref is not None:
                        signal_name = signal_ref.text.split('/')[-1]

                        if direction == "In":
                            signal = self.input_signals_dict.get(signal_name)
                        else:
                            signal = self.output_signals_dict.get(signal_name)

                        cluster.signals[signal_name] = signal

                    # Signal Group
                    else:
                        signal_group_ref = signal_tr.find('{http://autosar.org/schema/r4.0}I-SIGNAL-GROUP-REF')
                        signal_group_name = signal_group_ref.text.split('/')[-1]

                        if direction == "In":
                            signal_group = self.input_signal_groups_dict.get(signal_group_name)
                        else:
                            signal_group = self.output_signal_groups_dict.get(signal_group_name)

                        cluster.signal_groups[signal_group_name] = signal_group

            for pdu_tr in pdu_triggerings:
                pdu_name = pdu_tr.find('{http://autosar.org/schema/r4.0}I-PDU-REF').text.split('/')[-1]

                pdu = self.pdu_dict.get(pdu_name)
                cluster.pdus[pdu_name] = pdu

            for fr_tr in frame_triggerings:
                frame_name = fr_tr.find('{http://autosar.org/schema/r4.0}FRAME-REF').text.split('/')[-1]

                can_frame = self.can_frames_dict.get(frame_name)

                port_ref = fr_tr.find('{http://autosar.org/schema/r4.0}FRAME-PORT-REFS/' +
                                      '{http://autosar.org/schema/r4.0}FRAME-PORT-REF')

                ecu = port_ref.text.split('/')[4]
                direction = port_ref.text.split('/')[6].split('_')[1]   # In our Out

                if direction == "In":
                    can_frame.receiver.append(ecu)

                elif direction == "Out":
                    can_frame.transmitter = ecu

                frame_id = int(fr_tr.find('{http://autosar.org/schema/r4.0}IDENTIFIER').text)

                can_frame.frame_id = frame_id

                cluster.frames[frame_name] = can_frame


            # Save CAN cluster in clusters dictionary
            self.clusters_dict[c_name] = cluster

    def _get_flexray_tp_config(self):
        """
        Get FLEXRAY-TP-CONFIG information and populate the tp_pools dict, tp_connections list
        of each FlexRay cluster
        """
        tp_configs = self.root.findall(".//{http://autosar.org/schema/r4.0}FLEXRAY-TP-CONFIG")
        for tp_config in tp_configs:
            cluster_name = tp_config.find("{http://autosar.org/schema/r4.0}COMMUNICATION-CLUSTER-REF").text.split('/')[-1]
            cluster = self.clusters_dict.get(cluster_name)

            # Get PDU POOLS information
            pdu_pools = tp_config.find("{http://autosar.org/schema/r4.0}PDU-POOLS")
            for pdu_pool in pdu_pools:
                pool_name = pdu_pool.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                cluster.tp_config.tp_pools[pool_name] = []

                pdu_refs = pdu_pool.find("{http://autosar.org/schema/r4.0}N-PDU-REFS")
                for pdu_ref in pdu_refs:
                    pdu_name = pdu_ref.text.split('/')[-1]
                    cluster.tp_config.tp_pools[pool_name].append(pdu_name)

            # Get TP CONNECTIONS information
            tp_connections = tp_config.find("{http://autosar.org/schema/r4.0}TP-CONNECTIONS")
            for tp_connection in tp_connections:
                current_tpc = _FlexrayTpConnection()

                current_tpc.direct_sdu = tp_connection.find("{http://autosar.org/schema/r4.0}DIRECT-TP-SDU-REF").text.split('/')[-1]
                current_tpc.tx_tp_pool = tp_connection.find("{http://autosar.org/schema/r4.0}TX-PDU-POOL-REF").text.split('/')[-1]
                current_tpc.transmitter = tp_connection.find("{http://autosar.org/schema/r4.0}TRANSMITTER-REF").text.split('/')[-1]

                try:
                    current_tpc.reversed_sdu = tp_connection.find("{http://autosar.org/schema/r4.0}REVERSED-TP-SDU-REF").text.split('/')[-1]
                except AttributeError:
                    pass
                try:
                    current_tpc.rx_tp_pool = tp_connection.find("{http://autosar.org/schema/r4.0}RX-PDU-POOL-REF").text.split('/')[-1]
                except AttributeError:
                    pass

                try:
                    current_tpc.multicast_ref = tp_connection.find("{http://autosar.org/schema/r4.0}MULTICAST-REF").text.split('/')[-1]
                except AttributeError:
                    pass

                bandwidth_limitation = tp_connection.find("{http://autosar.org/schema/r4.0}BANDWIDTH-LIMITATION").text
                if bandwidth_limitation == "true":
                    current_tpc.bandwidth_limitation = True
                else:
                    current_tpc.bandwidth_limitation = False

                receiver_refs = tp_connection.find("{http://autosar.org/schema/r4.0}RECEIVER-REFS")
                for receiver_ref in receiver_refs:
                    current_tpc.receiver.append(receiver_ref.text.split('/')[-1])

                cluster.tp_config.tp_connections.append(current_tpc)

            # Get TP ADDRESS information
            tp_addresses = tp_config.find("{http://autosar.org/schema/r4.0}TP-ADDRESSS")
            for tp_address in tp_addresses:
                tp_addr_name = tp_address.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                cluster.tp_config.tp_addresses[tp_addr_name] = int(tp_address.find("{http://autosar.org/schema/r4.0}TP-ADDRESS").text)

            # Get TP NODES information
            for tp_config in tp_configs:
                tp_nodes = tp_config.find("{http://autosar.org/schema/r4.0}TP-NODES")
                for tp_node in tp_nodes:
                    tp_node_name = tp_node.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    tp_addr_ref = tp_node.find("{http://autosar.org/schema/r4.0}TP-ADDRESS-REF").text
                    cluster.tp_config.tp_nodes[tp_node_name] = tp_addr_ref.split('/')[-1]

    def _get_can_tp_config(self):
        """
        Get CAN-TP-CONFIG information and populate the tp_connections list
        of each CAN cluster
        """
        tp_configs = self.root.findall(".//{http://autosar.org/schema/r4.0}CAN-TP-CONFIG")
        for tp_config in tp_configs:
            cluster_name = tp_config.find("{http://autosar.org/schema/r4.0}COMMUNICATION-CLUSTER-REF").text.split('/')[-1]
            cluster = self.clusters_dict.get(cluster_name)

            # Get TP CONNECTIONS information
            tp_connections = tp_config.find("{http://autosar.org/schema/r4.0}TP-CONNECTIONS")
            for tp_connection in tp_connections:
                current_tpc = _CanTPC()

                current_tpc.addressing_format = tp_connection.find("{http://autosar.org/schema/r4.0}ADDRESSING-FORMAT").text.split('/')[-1]
                current_tpc.data_pdu = tp_connection.find("{http://autosar.org/schema/r4.0}DATA-PDU-REF").text.split('/')[-1]
                try:
                    current_tpc.flow_control_pdu = tp_connection.find("{http://autosar.org/schema/r4.0}FLOW-CONTROL-PDU-REF").text.split('/')[-1]
                except AttributeError:
                    pass
                current_tpc.tp_sdu = tp_connection.find("{http://autosar.org/schema/r4.0}TP-SDU-REF").text.split('/')[-1]
                current_tpc.transmitter = tp_connection.find("{http://autosar.org/schema/r4.0}TRANSMITTER-REF").text.split('/')[-1]

                receiver_refs = tp_connection.find("{http://autosar.org/schema/r4.0}RECEIVER-REFS")
                for receiver_ref in receiver_refs:
                    current_tpc.receiver.append(receiver_ref.text.split('/')[-1])

                cluster.tp_connections.append(current_tpc)

    def _fill_flexray_tables(self):
        """ Fill hTableOfPDUs, hTableOfSignals, hTableOfSignals3 and
        hTableOfOffsets of each FlexRay cluster to ensure compatibility
        with the same methods used in fibex.py and fry.py.
        """
        for c_name, c in self.clusters_dict.iteritems():
            if c.type == "FLEXRAY":

                for f_name, frame in c.frames.iteritems():

                    c.hTableOfPDUs[f_name] = []
                    c.hTableOfSignals[f_name] = []

                    # Table of PDUs
                    for p_name in frame.pdu_instances:
                        pdu_instance = c.pdus.get(p_name)
                        c.hTableOfPDUs[f_name].append(pdu_instance)

                        # Table of Signals
                        for s_name in pdu_instance.signal_instances:
                            found_signal = c.signals.get(s_name)
                            # Update signal bit position by adding the PDU bitpos
                            if found_signal.bitpos == found_signal.bitpos_in_pdu:
                                found_signal.bitpos = found_signal.bitpos_in_pdu + pdu_instance.bitpos
                                found_signal.bytepos = found_signal.bitpos / 8
                                # Check to avoid duplicate instances
                                if found_signal not in c.hTableOfSignals[f_name]:
                                    c.hTableOfSignals[f_name].append(found_signal)

                    # sort signals as they are ordered in frame
                    c.hTableOfSignals[f_name].sort(key=lambda s: s.bitpos, reverse=True)
                    c.hTableOfSignals[f_name].sort(key=lambda s: s.bytepos)

                for frame in c.hTableOfFrames:
                    for slot_id in c.hTableOfFrames.get(frame).slot_id:
                        if slot_id not in c.hTableOfOffsets:
                            c.hTableOfOffsets[slot_id] = {}
                        c.hTableOfOffsets[slot_id][c.hTableOfFrames.get(frame).offset] = \
                            [c.hTableOfFrames.get(frame).repetition, frame]

                for p_name, pdu in c.pdus.iteritems():
                    if len(pdu.signal_instances):
                        c.hTableOfSignals3[p_name] = []
                        for s_name in pdu.signal_instances:
                            c.hTableOfSignals3[p_name].append(c.signals.get(s_name))

                        # sort signals as they are ordered in pdu
                        c.hTableOfSignals3[p_name].sort(key = lambda s: s.bytepos)
                        c.hTableOfSignals3[p_name].sort(key = lambda s: s.bitpos)

    def _fill_can_tables(self):
        """ Fill hTableOfSignals and hTableOfFrames of each Can
        cluster to ensure compatibility with the same methods
        used in dbc.py and can.py.
        """
        for c_name, c in self.clusters_dict.iteritems():
            if c.type == "CAN":
                for f_name, frame in c.frames.iteritems():
                    can_frame = _CanFrame()
                    can_frame.cycleTime = frame.cycleTime
                    can_frame.canid = frame.frame_id
                    can_frame.dlc = frame.length
                    can_frame.name = frame.name
                    can_frame.publisher = frame.transmitter
                    c.hTableOfFrames[f_name] = can_frame

                    c.hTableOfSignals[f_name] = []
                    if frame.signal_instances:
                        for s_name in frame.signal_instances:
                            signal = c.signals.get(s_name)
                            can_signal = _CanSignal()

                            can_signal.signalName = s_name
                            can_signal.signalLength = signal.coding.bit_length
                            can_signal.offset = signal.bitpos
                            can_signal.updatebit = signal.updatebit
                            can_signal.littleEndianStart = not signal.endianness
                            can_signal.defaultvalue = signal.value
                            can_signal.offsetConvValue = signal.coding.compu_numerator[0]
                            can_signal.factorConvValue = signal.coding.compu_numerator[1]
                            can_signal.Max = signal.coding.constraints

                            if can_signal not in c.hTableOfSignals[f_name]:
                                c.hTableOfSignals[f_name].append(can_signal)

                    else:   # If frame has no signals, use pdu information
                        for p_name in frame.pdu_instances:
                            pdu = c.pdus.get(p_name)
                            can_signal = _CanSignal()
                            can_signal.signalName = p_name
                            can_signal.signalLength = pdu.pdu_length
                            can_signal.offset = pdu.bitpos
                            can_signal.littleEndianStart = not pdu.endianness

                            if can_signal not in c.hTableOfSignals[f_name]:
                                c.hTableOfSignals[f_name].append(can_signal)

    def _get_gateway_pdu_frames(self):
        """
        Uses the CAN and FlexRay Transport Protocol information and
        the gateway PDU relations to obtain the relation between source
        and output frames.
        """
        for g in self.pduGatewayList:
            test_gateway = g

            # Source bus
            if self.clusters_dict.get(test_gateway.source_gtw_bus).type == 'CAN':
                n_pdu = self._can_ipdu_to_npdu(test_gateway.source_gtw_pdu, test_gateway.source_gtw_bus)
                can_f, can_p = self.look_for_frame_and_pdu(n_pdu, test_gateway.source_gtw_bus)

                test_gateway.source_gtw_frames.append(can_f.name)

            if self.clusters_dict.get(test_gateway.source_gtw_bus).type == 'FLEXRAY':
                npdus = self._flexray_ipdu_to_npdus(test_gateway.source_gtw_bus,
                                                       test_gateway.source_gtw_pdu, 'source')

                for pdu in npdus:
                    f, p = self.look_for_frame_and_pdu(pdu, test_gateway.source_gtw_bus)
                    test_gateway.source_gtw_frames.append(f.name)

            # Target bus
            if self.clusters_dict.get(test_gateway.target_gtw_bus).type == 'CAN':
                n_pdu = self._can_ipdu_to_npdu(test_gateway.source_gtw_pdu, test_gateway.target_gtw_bus)
                can_f, can_p = self.look_for_frame_and_pdu(n_pdu, test_gateway.target_gtw_bus)

                test_gateway.target_gtw_frames.append(can_f.name)

            if self.clusters_dict.get(test_gateway.target_gtw_bus).type == 'FLEXRAY':
                npdus = self._flexray_ipdu_to_npdus(test_gateway.target_gtw_bus,
                                                       test_gateway.target_gtw_pdu, 'target')

                for pdu in npdus:
                    f, p = self.look_for_frame_and_pdu(pdu, test_gateway.target_gtw_bus)
                    test_gateway.target_gtw_frames.append(f.name)

    def _get_gateway_signal_frames(self):
        """
        Gets the relation between source and target frames using the
        signal gateway information.
        """
        for g in self.signalGatewayList:
            test_gateway = g

            # Source bus
            f, s = self.look_for_frame_and_signal(test_gateway.source_gtw_signal, test_gateway.source_gtw_bus)
            if f is None:
                f, sg = self.look_for_frame_and_signal_group(test_gateway.source_gtw_signal, test_gateway.source_gtw_bus)

            test_gateway.source_gtw_frame = f.name

            # Target bus
            f, s = self.look_for_frame_and_signal(test_gateway.target_gtw_signal, test_gateway.target_gtw_bus)
            if f is None:
                f, sg = self.look_for_frame_and_signal_group(test_gateway.target_gtw_signal, test_gateway.target_gtw_bus)

            test_gateway.target_gtw_frame = f.name

    def _get_fr_gateway_addresses(self):
        """
        Gets the target (remote) and source (local) addresses
        of the FlexRay gateway PDUs
        """
        for g in self.pduGatewayList:
            # Check Source
            ipdu = g.source_gtw_pdu
            bus = self.clusters_dict[g.source_gtw_bus]
            if bus.type == 'FLEXRAY':
                for tpc in bus.tp_config.tp_connections:
                    if ipdu in tpc.direct_sdu:
                        if tpc.multicast_ref:
                            target_addr_ref = tpc.multicast_ref
                        else:
                            target_addr_ref = bus.tp_config.tp_nodes[tpc.receiver[0]]
                        source_addr_ref = bus.tp_config.tp_nodes[tpc.transmitter]
                        g.source_gtw_addr = bus.tp_config.tp_addresses[source_addr_ref]
                        g.target_gtw_addr = bus.tp_config.tp_addresses[target_addr_ref]

                    elif ipdu in tpc.reversed_sdu:
                        source_addr_ref = bus.tp_config.tp_nodes[tpc.receiver[0]]
                        target_addr_ref = bus.tp_config.tp_nodes[tpc.transmitter]
                        g.source_gtw_addr = bus.tp_config.tp_addresses[source_addr_ref]
                        g.target_gtw_addr = bus.tp_config.tp_addresses[target_addr_ref]
            # Check Target
            ipdu = g.target_gtw_pdu
            bus = self.clusters_dict[g.target_gtw_bus]
            if bus.type == 'FLEXRAY':
                for tpc in bus.tp_config.tp_connections:
                    if ipdu in tpc.direct_sdu:
                        if tpc.multicast_ref:
                            target_addr_ref = tpc.multicast_ref
                        else:
                            target_addr_ref = bus.tp_config.tp_nodes[tpc.receiver[0]]
                        source_addr_ref = bus.tp_config.tp_nodes[tpc.transmitter]
                        g.source_gtw_addr = bus.tp_config.tp_addresses[source_addr_ref]
                        g.target_gtw_addr = bus.tp_config.tp_addresses[target_addr_ref]

                    elif ipdu in tpc.reversed_sdu:
                        source_addr_ref = bus.tp_config.tp_nodes[tpc.receiver[0]]
                        target_addr_ref = bus.tp_config.tp_nodes[tpc.transmitter]
                        g.source_gtw_addr = bus.tp_config.tp_addresses[source_addr_ref]
                        g.target_gtw_addr = bus.tp_config.tp_addresses[target_addr_ref]

    def _get_response_pdu(self):
        """
        Gets response PDU for each GTW case.
        """
        for g in self.pduGatewayList:
            # Source
            ipdu = g.source_gtw_pdu
            bus = self.clusters_dict[g.source_gtw_bus]
            if bus.type == 'FLEXRAY':
                for tpc in bus.tp_config.tp_connections:
                        if ipdu in tpc.direct_sdu:
                            resp_ipdu = tpc.reversed_sdu
                            break
                        elif ipdu in tpc.reversed_sdu:
                            resp_ipdu = tpc.direct_sdu
                            break

                npdus = self._flexray_ipdu_to_npdus(g.source_gtw_bus, resp_ipdu, 'target')
                resp_frames = []
                if npdus:
                    for npdu in npdus:
                        f, p = self.look_for_frame_and_pdu(npdu, g.source_gtw_bus)
                        if f:
                            resp_frames.append(f.name)

            elif bus.type == 'CAN':
                for tpc in bus.tp_connections:
                    if ipdu == tpc.tp_sdu:
                        f, p = self.look_for_frame_and_pdu(tpc.flow_control_pdu, g.source_gtw_bus)
                        break
                if f:
                    resp_frames = [f.name]
                else:
                    resp_frames = []

            g.source_resp = resp_frames

            # Target
            ipdu = g.target_gtw_pdu
            bus = self.clusters_dict[g.target_gtw_bus]
            if bus.type == 'FLEXRAY':
                for tpc in bus.tp_config.tp_connections:
                    if ipdu in tpc.direct_sdu:
                        resp_ipdu = tpc.reversed_sdu
                        break
                    elif ipdu in tpc.reversed_sdu:
                        resp_ipdu = tpc.direct_sdu
                        break

                npdus = self._flexray_ipdu_to_npdus(g.target_gtw_bus, resp_ipdu, 'source')
                resp_frames = []
                if npdus:
                    for npdu in npdus:
                        f, p = self.look_for_frame_and_pdu(npdu, g.target_gtw_bus)
                        if f:
                            resp_frames.append(f.name)

            elif bus.type == 'CAN':
                for tpc in bus.tp_connections:
                    if ipdu == tpc.tp_sdu:
                        f, p = self.look_for_frame_and_pdu(tpc.flow_control_pdu, g.target_gtw_bus)
                        break
                if f:
                    resp_frames = [f.name]
                else:
                    resp_frames = []

            g.target_resp = resp_frames


    ###############################################################
    # Functions to print-test the populated dictionaries and lists
    ###############################################################
    def _test_signal_dict(self):
        """
        Print the dictionary of signals
        """
        for signal_name, signal in self.signal_dict.iteritems():
            print "---------------------------------"
            print "Signal Name: " + signal_name
            print "Bitpos: " + str(signal.bitpos)
            print "Length: " + str(signal.coding.bit_length)
            print "Endianness: " + str(signal.endianness)
            print "Unit: " + signal.unit.unit_name + ", " + signal.unit.display
            print "Coding: " + signal.coding.computation_method
            print "Update Bit: " + str(signal.updatebit)

    def _test_output_signals(self):
        """
        Print the dictionary of output signals
        """
        for signal_name, signal in self.output_signals_dict.iteritems():
            print "---------------------------------"
            print "Signal Name: " + signal_name
            print "Bitpos: " + str(signal.bitpos)
            print "Length: " + str(signal.coding.bit_length)
            print "Endianness: " + str(signal.endianness)
            print "Unit: " + signal.unit.unit_name + ", " + signal.unit.display
            print "Coding: " + signal.coding.computation_method
            print "Update Bit: " + str(signal.updatebit)

    def _test_input_signals(self):
        """
        Print the dictionary of input signals
        """
        for signal_name, signal in self.input_signals_dict.iteritems():
            print "---------------------------------"
            print "Signal Name: " + signal_name
            print "Bitpos: " + str(signal.bitpos)
            print "Length: " + str(signal.coding.bit_length)
            print "Endianness: " + str(signal.endianness)
            print "Unit: " + signal.unit.unit_name + ", " + signal.unit.display
            print "Coding: " + signal.coding.computation_method
            print "Update Bit: " + str(signal.updatebit)

    def _test_flexray_frames_dict(self):
        """
        Print the dictionary of FlexRay frames
        """
        for frame_name, frame in self.flexray_frames_dict.iteritems():
            print "---------------------------------"
            print 'Frame Name: ' + frame_name
            print 'Slot ID: ' + str(frame.slot_id)
            print 'Repetition: ' + str(frame.repetition)
            print 'Length: ' + str(frame.length)
            print 'Transmitter: ' + str(frame.transmitter)
            print 'Receiver(s): ' + str(frame.receiver)
            print 'PDUs:',
            print frame.pdu_instances
            print 'Signals:',
            print frame.signal_instances

    def _test_can_frames_dict(self):
        """
        Print the dictionary of CAN frames
        """
        for frame_name, frame in self.can_frames_dict.iteritems():
            print "---------------------------------"
            print 'Frame Name: ' + frame_name
            print 'CAN ID: ' + str(frame.frame_id)
            print 'Cycle Time: ' + str(frame.cycleTime)
            print 'Length: ' + str(frame.length)
            print 'Transmitter: ' + str(frame.transmitter)
            print 'Receiver(s): ' + str(frame.receiver)
            print 'PDUs:',
            print frame.pdu_instances
            print 'Signals:',
            print frame.signal_instances

    def _test_pdu_dict(self):
        """
        Print the dictionary of PDUs
        """
        for pdu_name, pdu in self.pdu_dict.iteritems():
            print "---------------------------------"
            print "PDU Name: " + pdu_name
            print 'PDU Type: ' + str(pdu.pdu_type)
            print 'Signals:',
            print pdu.signal_instances

    def _test_gateway_signals(self):
        """
        Print the list of gateway signals
        """
        for signal in self.signalGatewayList:
            print "-------------------------------------"
            print "Source Bus: \t\t" + signal.source_gtw_bus
            print "Source Signal: \t\t" + signal.source_gtw_signal
            print "Source UB Signal: \t" + signal.source_gtw_UBsignal
            print "Target Bus: \t\t" + signal.target_gtw_bus
            print "Target Signal: \t\t" + signal.target_gtw_signal
            print "Target UB Signal: \t" + signal.target_gtw_UBsignal

    def _test_gateway_frames(self):
        """
        Print the list of gateway frames (PDUs)
        """
        for pdu in self.pduGatewayList:
            print "-------------------------------------"
            print "Source Bus: \t\t" + pdu.source_gtw_bus
            print "Source Frame(s): \t", pdu.source_gtw_frames
            print "Target Bus: \t\t" + pdu.target_gtw_bus
            print "Target Frame(s): \t", pdu.target_gtw_frames
