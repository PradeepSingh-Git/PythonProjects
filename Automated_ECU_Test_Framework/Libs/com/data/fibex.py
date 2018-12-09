"""
====================================================================
Library for reading FIBEX files, that contain FLEXRAY bus description
(C) Copyright 2017 Lear Corporation
====================================================================
"""

__author__  = 'Albert Sanz, Xavier Cucurull'
__version__ = '1.0.4'
__email__   = 'asanz@lear.com, xcucurullsalamero@lear.com'

'''
CHANGE LOG
==========
1.0.5 Bugfix: if no COMPU-DENOMINATOR is present, leave default value (1)
      Added lxml import for improved performance
1.0.4 Remove some methods, which are now part of the FLEXRAY library
1.0.3 Fixed FIBEX loading problems in VCU1 example
1.0.2 Initial integration of DGN for FlexRay
1.0.1 Added capability to select between channel A or B
1.0.0 Initial version
'''

import sys
from ctypes import *
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.cElementTree as ET
    print "Using xml cElementTree..."
    print "Install lxml for a better performance"
import re


class ClusterConfig(object):
    '''
    Class for storing the cluster configuration parameters. Used by COM.
    '''
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
        self.pChannels = 3   # It is possible to send messages through channels A and B
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


class _Unit(object):
    '''
    Physical unit parameters (id, name and symbol).
    '''
    def __init__(self):
        self.unit_id = 0
        self.unit_name = 'Unit not Defined'
        self.display = ''


class _Coding(object):
    '''
    Signal coding parameters (name, length, computation, etc.)
    '''
    def __init__(self):
        self.coding_id = 0
        self.coding_name = 'Coding not Defined'
        self.bit_length = 0                         # signal length in bits
        self.constraints = 0                        # max raw value
        self.coded_type = 'Coding Type not Defined'
        self.computation_method ='Not Defined'      #IDENTICAL: phys = raw | LINEAR: phys = mul*raw+sum
        self.compu_numerator= [0]*2                 #[sum, mul]
        self.compu_denominator = 1


class _Signal(object):
    '''
    Signal parameters (name, position, endiannnes, value, etc.)
    '''
    def __init__(self):
        self.signalName = 'Signal not Defined'
        self.signal_id = 0
        self.bitpos = 0
        self.bytepos = 0
        self.endianness = 0     # 0: Intel (little en), 1: Motorola (big en)
        self.value = 0
        self.coding = _Coding()
        self.unit = _Unit()


class _PDU(object):
    '''
    PDU parameters (name, length, position, signals, etc.)
    '''
    def __init__(self):
        self.pdu_id = 0
        self.pdu_name = 'PDU not Defined'
        self.pdu_length = 0                 # PDU length in bytes
        self.pdu_type = 'Type not Defined'
        self.bitpos = 0
        self.signal_instances = []          # list with signal_id from the associated signals
        self.multiplexer = False
        self.switch_pdu_instances = []


class _Frame(object):
    '''
    Frame parameters (name, slot ID, repetition, length, etc.)
    '''
    def __init__(self):
        self.frame_id = 0
        self.triggering_id = 0
        self.name = 'Frame not Defined'
        self.type = 'Type not Defined'
        self.slot_id = []
        self.repetition = 0
        self.offset = 0
        self.length = 0             # bytes
        self.channel = 0
        self.transmitter = ''
        self.receiver = []
        self.signal_instances = []  # list with signal_id from the associated signals
        self.pdu_instances = []     # list with pdu_id from the associated PDUs


class FIBEX(object):
    '''
    Class for reading FIBEX files, set cluster configuration and access frames and signals.
    '''
    def __init__(self, fibex_file, fr_channel, cold_start_slots):

        # set ElementTree parameters
        try:
            self.tree = ET.parse(fibex_file)
        except IOError:
            print 'Error trying to open \'' + fibex_file + '\' FIBEX file.'
            sys.exit()

        self.root = self.tree.getroot()
        self.elements = self.root.find('{http://www.asam.net/xml/fbx}ELEMENTS')
        self.ecus = self.elements.find('{http://www.asam.net/xml/fbx}ECUS')

        self.fibex_version = self.root.get('VERSION')

        self.hTableOfFrames = {}        # frarray indexed by frame.name
        self.hTableOfPDUs = {}          # 2D of PDUs indexed by [frameName]+list
        self.hTableOfSignals = {}       # 2D of signals indexed by [frameName]+list
        self.hTableOfSignals3 = {}      # 2D of signals indexed by [PDUname]+list
        self.hTableOfOffsets = {}       # 2D of offsets (base) indexed by [slotID]+dict
        self.hTableOfSwitchPDUs = {}    #array indexed by pdu.id

        self._fill_frames_table()

        if re.match(r'^3\.\d\.\d', self.fibex_version):  # Fibex v3.x.x
            self._fill_pdus_table()
            self._fill_signals_table_v3()

        elif re.match(r'^2\.\d\.\d', self.fibex_version):  # Fibex v2.x.x
            self._fill_signals_table_v2()

        else:
            print 'Fibex version \'' + self.fibex_version + '\' not supported.'
            sys.exit()

        self._fill_offsets()
        self.cluster_config = ClusterConfig()
        self._set_cluster_config()
        self._set_controller_config(fr_channel, cold_start_slots)

    def _set_cluster_config(self):
        '''
        Description: Reads FIBEX file and sets the general cluster configuration parameters.
        '''
        cluster = self.elements.find('{http://www.asam.net/xml/fbx}CLUSTERS')[0]

        # Read cluster section of the FIBEX config file
        speed = cluster.find('{http://www.asam.net/xml/fbx}SPEED')
        if speed is not None:
            self.cluster_config.baudrate = int(speed.text)

        coldStartAttempts = cluster.find('{http://www.asam.net/xml/fbx/flexray}COLD-START-ATTEMPTS')
        self.cluster_config.gColdStartAttempts = int(coldStartAttempts.text)

        listenNoise = cluster.find('{http://www.asam.net/xml/fbx/flexray}LISTEN-NOISE')
        self.cluster_config.gListenNoise = int(listenNoise.text)

        macroPerCycle = cluster.find('{http://www.asam.net/xml/fbx/flexray}MACRO-PER-CYCLE')
        self.cluster_config.gMacroPerCycle = int(macroPerCycle.text)

        maxWithoutClockCorrectionFatal = cluster.find('{http://www.asam.net/xml/fbx/flexray}MAX-WITHOUT-CLOCK-CORRECTION-FATAL')
        self.cluster_config.gMaxWithoutClockCorrectionFatal = int(maxWithoutClockCorrectionFatal.text)

        maxWithoutClockCorrectionPassive = cluster.find('{http://www.asam.net/xml/fbx/flexray}MAX-WITHOUT-CLOCK-CORRECTION-PASSIVE')
        self.cluster_config.gMaxWithoutClockCorrectionPassive = int(maxWithoutClockCorrectionPassive.text)

        networkManagementVectorLength = cluster.find('{http://www.asam.net/xml/fbx/flexray}NETWORK-MANAGEMENT-VECTOR-LENGTH')
        self.cluster_config.gNetworkManagementVectorLength = int(networkManagementVectorLength.text)

        numberOfMinislots = cluster.find('{http://www.asam.net/xml/fbx/flexray}NUMBER-OF-MINISLOTS')
        self.cluster_config.gNumberOfMinislots = int(numberOfMinislots.text)

        numberOfStaticSlots = cluster.find('{http://www.asam.net/xml/fbx/flexray}NUMBER-OF-STATIC-SLOTS')
        self.cluster_config.gNumberOfStaticSlots = int(numberOfStaticSlots.text)

        offsetCorrectionStart = cluster.find('{http://www.asam.net/xml/fbx/flexray}OFFSET-CORRECTION-START')
        self.cluster_config.gOffsetCorrectionStart = int(offsetCorrectionStart.text)

        payloadLengthStatic = cluster.find('{http://www.asam.net/xml/fbx/flexray}PAYLOAD-LENGTH-STATIC')
        self.cluster_config.gPayloadLengthStatic = int(payloadLengthStatic.text)

        syncNodeMax = cluster.find('{http://www.asam.net/xml/fbx/flexray}SYNC-NODE-MAX')
        self.cluster_config.gSyncNodeMax = int(syncNodeMax.text)

        actionPointOffset = cluster.find('{http://www.asam.net/xml/fbx/flexray}ACTION-POINT-OFFSET')
        self.cluster_config.gdActionPointOffset = int(actionPointOffset.text)

        dynamicSlotIdlePhase = cluster.find('{http://www.asam.net/xml/fbx/flexray}DYNAMIC-SLOT-IDLE-PHASE')
        self.cluster_config.gdDynamicSlotIdlePhase = int(dynamicSlotIdlePhase.text)

        minislot = cluster.find('{http://www.asam.net/xml/fbx/flexray}MINISLOT')
        self.cluster_config.gdMinislot = int(minislot.text)

        miniSlotActionPointOffset = cluster.find('{http://www.asam.net/xml/fbx/flexray}MINISLOT-ACTION-POINT-OFFSET')
        self.cluster_config.gdMiniSlotActionPointOffset = int(miniSlotActionPointOffset.text)

        NIT = cluster.find('{http://www.asam.net/xml/fbx/flexray}N-I-T')
        self.cluster_config.gdNIT = int(NIT.text)

        staticSlot = cluster.find('{http://www.asam.net/xml/fbx/flexray}STATIC-SLOT')
        self.cluster_config.gdStaticSlot = int(staticSlot.text)

        symbolWindow = cluster.find('{http://www.asam.net/xml/fbx/flexray}SYMBOL-WINDOW')
        self.cluster_config.gdSymbolWindow = int(symbolWindow.text)

        TSSTransmitter = cluster.find('{http://www.asam.net/xml/fbx/flexray}T-S-S-TRANSMITTER')
        self.cluster_config.gdTSSTransmitter = int(TSSTransmitter.text)

        rxidle = cluster.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP').find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-SYMBOL-RX-IDLE')
        self.cluster_config.gdWakeupSymbolRxIdle = int(rxidle.text)

        rxlow = cluster.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP').find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-SYMBOL-RX-LOW')
        self.cluster_config.gdWakeupSymbolRxLow = int(rxlow.text)

        rxwindow = cluster.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP').find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-SYMBOL-RX-WINDOW')
        self.cluster_config.gdWakeupSymbolRxWindow = int(rxwindow.text)

        txidle = cluster.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP').find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-SYMBOL-TX-IDLE')
        self.cluster_config.gdWakeupSymbolTxIdle = int(txidle.text)

        txlow = cluster.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP').find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-SYMBOL-TX-LOW')
        self.cluster_config.gdWakeupSymbolTxLow = int(txlow.text)

        CASRxLowMax = cluster.find('{http://www.asam.net/xml/fbx/flexray}CAS-RX-LOW-MAX')
        self.cluster_config.gdCASRxLowMax = int(CASRxLowMax.text)

        clusterDriftDamping = cluster.find('{http://www.asam.net/xml/fbx/flexray}CLUSTER-DRIFT-DAMPING')
        self.cluster_config.pClusterDriftDamping = int(clusterDriftDamping.text)

    def _set_controller_config(self, fr_channel, cold_start_slots):
        '''
        Reads FIBEX file and sets the ECU controller cluster configuration parameters.
        Looks for the STARTUP-SYNC ECUs and sets the erayID and coldID (slot IDs used
        to send startup and sync frames).

        Note: It uses the configuration from the first ECU and leaves
        pKeySlotUsedForStartup and pKeySlotUsedForStartup set to 1.
        '''
        controller = self.ecus[0].find('{http://www.asam.net/xml/fbx}CONTROLLERS')[0]
        connector = self.ecus[0].find('{http://www.asam.net/xml/fbx}CONNECTORS')[0]

        # Read controller section of the FIBEX config file
        clusterDriftDamping = controller.find('{http://www.asam.net/xml/fbx/flexray}CLUSTER-DRIFT-DAMPING')
        self.cluster_config.pClusterDriftDamping = int(clusterDriftDamping.text)

        decodingCorrection = controller.find('{http://www.asam.net/xml/fbx/flexray}DECODING-CORRECTION')
        self.cluster_config.pDecodingCorrection = int(decodingCorrection.text)

        maxDrift = controller.find('{http://www.asam.net/xml/fbx/flexray}MAX-DRIFT')
        self.cluster_config.pdMaxDrift = int(maxDrift.text)

        externOffsetCorrection = controller.find('{http://www.asam.net/xml/fbx/flexray}EXTERN-OFFSET-CORRECTION')
        self.cluster_config.pExternOffsetCorrection = int(externOffsetCorrection.text)

        externRateCorrection = controller.find('{http://www.asam.net/xml/fbx/flexray}EXTERN-RATE-CORRECTION')
        self.cluster_config.pExternRateCorrection = int(externRateCorrection.text)

        latestTx = controller.find('{http://www.asam.net/xml/fbx/flexray}LATEST-TX')
        self.cluster_config.pLatestTx = int(latestTx.text)

        microPerCycle = controller.find('{http://www.asam.net/xml/fbx/flexray}MICRO-PER-CYCLE')
        self.cluster_config.pMicroPerCycle = int(microPerCycle.text)

        delayCompensationA = controller.find('{http://www.asam.net/xml/fbx/flexray}DELAY-COMPENSATION-A')
        self.cluster_config.pDelayCompensationA = int(delayCompensationA.text)

        delayCompensationB = controller.find('{http://www.asam.net/xml/fbx/flexray}DELAY-COMPENSATION-B')
        self.cluster_config.pDelayCompensationB = int(delayCompensationB.text)

        wakeupPattern = controller.find('{http://www.asam.net/xml/fbx/flexray}WAKE-UP-PATTERN')
        self.cluster_config.pWakeupPattern = int(wakeupPattern.text)

        microPerMacroNom = controller.find('{http://www.asam.net/xml/fbx/flexray}MICRO-PER-MACRO-NOM')
        if microPerMacroNom is not None:
            try:
                self.cluster_config.pMicroPerMacroNom = int(microPerMacroNom.text)
            except ValueError:
                self.cluster_config.pMicroPerMacroNom = int(float(microPerMacroNom.text))

        maxPayloadLengthDynamic = controller.find('{http://www.asam.net/xml/fbx/flexray}MAX-DYNAMIC-PAYLOAD-LENGTH')
        self.cluster_config.pMaxPayloadLengthDynamic = int(maxPayloadLengthDynamic.text)

        offsetCorrectionOut = controller.find('{http://www.asam.net/xml/fbx/flexray}OFFSET-CORRECTION-OUT')
        self.cluster_config.pOffsetCorrectionOut = int(offsetCorrectionOut.text)

        rateCorrectionOut = controller.find('{http://www.asam.net/xml/fbx/flexray}RATE-CORRECTION-OUT')
        self.cluster_config.pRateCorrectionOut = int(rateCorrectionOut.text)

        allowHaltDueToClock = controller.find('{http://www.asam.net/xml/fbx/flexray}ALLOW-HALT-DUE-TO-CLOCK')
        if str(allowHaltDueToClock.text) == 'false':
             self.cluster_config.pAllowHaltDueToClock = 0
        elif str(allowHaltDueToClock.text) == 'true':
            self.cluster_config.pAllowHaltDueToClock = 1

        allowPassiveToActive = controller.find('{http://www.asam.net/xml/fbx/flexray}ALLOW-PASSIVE-TO-ACTIVE')
        self.cluster_config.pAllowPassiveToActive = int(allowPassiveToActive.text)

        acceptedStartupRange = controller.find('{http://www.asam.net/xml/fbx/flexray}ACCEPTED-STARTUP-RANGE')
        self.cluster_config.pdAcceptedStartupRange = int(acceptedStartupRange.text)

        macroInitialOffsetA = controller.find('{http://www.asam.net/xml/fbx/flexray}MACRO-INITIAL-OFFSET-A')
        self.cluster_config.pMacroInitialOffsetA = int(macroInitialOffsetA.text)

        macroInitialOffsetB = controller.find('{http://www.asam.net/xml/fbx/flexray}MACRO-INITIAL-OFFSET-B')
        self.cluster_config.pMacroInitialOffsetB = int(macroInitialOffsetB.text)

        microInitialOffsetA = controller.find('{http://www.asam.net/xml/fbx/flexray}MICRO-INITIAL-OFFSET-A')
        self.cluster_config.pMicroInitialOffsetA = int(microInitialOffsetA.text)

        microInitialOffsetB = controller.find('{http://www.asam.net/xml/fbx/flexray}MICRO-INITIAL-OFFSET-B')
        self.cluster_config.pMicroInitialOffsetB = int(microInitialOffsetB.text)

        listenTimeout = controller.find('{http://www.asam.net/xml/fbx/flexray}LISTEN-TIMEOUT')
        self.cluster_config.pdListenTimeout = int(listenTimeout.text)

        #setup correct FlexRay Channel to start communication
        if 'AB' in fr_channel:
            self.cluster_config.erayChannel = 3
        elif 'B' in fr_channel:
            self.cluster_config.erayChannel = 2
        else:
            self.cluster_config.erayChannel = 1

        # set startup CC parameters
        configured_coldStart_slots = 0
        found_coldStart_slots = []
        for ecu in self.ecus:
            slot_usage = ecu.find('{http://www.asam.net/xml/fbx}CONTROLLERS')[0].find('{http://www.asam.net/xml/fbx/flexray}KEY-SLOT-USAGE')[0].text
            if slot_usage is not None:
                for coldStartMessage in cold_start_slots:
                    if self.cluster_config.erayID == 0:
                        if int(slot_usage) == coldStartMessage:
                            self.cluster_config.erayID = int(slot_usage)
                            configured_coldStart_slots = configured_coldStart_slots + 1
                    elif self.cluster_config.coldID == 0:
                        if int(slot_usage) == coldStartMessage:
                            self.cluster_config.coldID = int(slot_usage)
                            configured_coldStart_slots = configured_coldStart_slots + 1

                found_coldStart_slots.append(int(slot_usage))

        if configured_coldStart_slots != len(cold_start_slots):
            print 'Configured ColdStart slots ' + str(cold_start_slots) + ' are not defined in FIBEX file'
            print 'Available ColdStart slots in FIBEX file are: ' + str(found_coldStart_slots)
            sys.exit()

        invalid_frames = []
        for frame in self.hTableOfFrames:
            if self.hTableOfFrames.get(frame).slot_id:   # Check that list is not empty. Error: frames without slotID ( FIBEX 3.1)
                if self.hTableOfFrames.get(frame).slot_id[0] == self.cluster_config.erayID:
                    self.cluster_config.eray_repetition = self.hTableOfFrames.get(frame).repetition
                    self.cluster_config.eray_offset = self.hTableOfFrames.get(frame).offset
            else:
                invalid_frames.append(frame)

        for frame in invalid_frames:            # [workaround]. Delete frames that have no FRAME-TRIGGERING (slotID)
            del self.hTableOfFrames[frame]
        del invalid_frames

        for frame in self.hTableOfFrames:
            if self.hTableOfFrames.get(frame).slot_id:   # Check that list is not empty. Error: frames without slotID
                if self.hTableOfFrames.get(frame).slot_id[0] == self.cluster_config.coldID:
                    self.cluster_config.cold_repetition = self.hTableOfFrames.get(frame).repetition
                    self.cluster_config.cold_offset = self.hTableOfFrames.get(frame).offset

    def _find_frame_from_x(self, search_value, x):
        '''
        Description: Given an x attribute, finds the frame that contains the given
        attribute set to the given search_value.
        Returns an object of class Frame.
        '''
        for frame_name, value in self.hTableOfFrames.iteritems():
            x_value = getattr(self.hTableOfFrames[frame_name], x)
            if x_value == search_value:
                return self.hTableOfFrames[frame_name]

    def _find_signals_from_x(self, search_value, signals_table, x, y):
        '''
        Description: Given an x attribute,finds the signals that contains the given
        attribute set to the given search_value.
        Returns a list of objects of class Signal.
        '''
        found_signals = []
        for name, signals in signals_table.iteritems():
            for signal in signals:
                x_value = getattr(signal, x)
                x_value = getattr(x_value, y)
                if x_value == search_value:
                    found_signals.append(signal)
        return found_signals

    def _find_signal_from_sid(self, search_signal_id, signals_table):
        '''
        Description: Given a Signal ID, finds the dictionary key that contains it.
        Returns an object of class Signal.
        '''
        for name, signals in signals_table.iteritems():
            for signal in signals:
                if signal.signal_id == search_signal_id:
                    return signal

    def _find_pdu_from_pid(self, search_pdu_id):
        '''
        Description: Given a PDU ID, finds the dictionary key that contains it.
        Returns an object of class PDU.
        '''
        for frame_name, pdus in self.hTableOfPDUs.iteritems():
            for pdu in pdus:
                if pdu.pdu_id == search_pdu_id:
                    return pdu

    def _fill_frames_table(self):
        '''
        Description: Reads FIBEX file and stores info in the frames struct.
        '''
        channels = self.elements.find('{http://www.asam.net/xml/fbx}CHANNELS')
        frames = self.elements.find('{http://www.asam.net/xml/fbx}FRAMES')

        for frame in frames:
            currentframe = _Frame()
            currentframe.frame_id = frame.get('ID')
            currentframe.name = frame.find('{http://www.asam.net/xml}SHORT-NAME').text
            currentframe.length = frame.find('{http://www.asam.net/xml/fbx}BYTE-LENGTH').text
            frame_type = frame.find('{http://www.asam.net/xml/fbx}FRAME-TYPE')
            if frame_type is not None:
                currentframe.type = frame.find('{http://www.asam.net/xml/fbx}FRAME-TYPE').text

            self.hTableOfFrames[currentframe.name] = _Frame()
            self.hTableOfFrames[currentframe.name].name = currentframe.name
            self.hTableOfFrames[currentframe.name].frame_id = currentframe.frame_id
            self.hTableOfFrames[currentframe.name].length = int(currentframe.length)
            self.hTableOfFrames[currentframe.name].type = currentframe.type

            if re.match(r'^2\.\d\.\d', self.fibex_version):  # Fibex v2.x.x
                signal_instances = frame.find('{http://www.asam.net/xml/fbx}SIGNAL-INSTANCES')
                for signal in signal_instances:
                    signal_instance = signal.find('{http://www.asam.net/xml/fbx}SIGNAL-REF').get('ID-REF')
                    self.hTableOfFrames[currentframe.name].signal_instances.append(signal_instance)

            elif re.match(r'^3\.\d\.\d', self.fibex_version):  # Fibex v3.x.x
                pdu_instances = frame.find('{http://www.asam.net/xml/fbx}PDU-INSTANCES')
                for pdu in pdu_instances:
                    pdu_instance = pdu.find('{http://www.asam.net/xml/fbx}PDU-REF').get('ID-REF')
                    self.hTableOfFrames[currentframe.name].pdu_instances.append(pdu_instance)

            else:
                print 'FIBEX version ' + self.fibex_version + ' not supported!'
                sys.exit()

        for channel in channels:
            frame_triggerings = channel.find('{http://www.asam.net/xml/fbx}FRAME-TRIGGERINGS')

            for frame_trig in frame_triggerings:
                currentframe = _Frame()
                currentframe.triggering_id = frame_trig.get('ID')
                currentframe.frame_id = frame_trig.find('{http://www.asam.net/xml/fbx}FRAME-REF').get('ID-REF')
                timings = frame_trig.find('{http://www.asam.net/xml/fbx}TIMINGS').findall('{http://www.asam.net/xml/fbx}ABSOLUTELY-SCHEDULED-TIMING')
                for t in timings:
                    currentframe.slot_id.append(int(t.find('{http://www.asam.net/xml/fbx}SLOT-ID').text))
                currentframe.repetition = frame_trig.find('{http://www.asam.net/xml/fbx}TIMINGS').find('{http://www.asam.net/xml/fbx}ABSOLUTELY-SCHEDULED-TIMING').find('{http://www.asam.net/xml/fbx}CYCLE-REPETITION').text
                currentframe.offset = frame_trig.find('{http://www.asam.net/xml/fbx}TIMINGS').find('{http://www.asam.net/xml/fbx}ABSOLUTELY-SCHEDULED-TIMING').find('{http://www.asam.net/xml/fbx}BASE-CYCLE').text

                found_frame = self._find_frame_from_x(currentframe.frame_id, 'frame_id')
                found_frame.triggering_id = currentframe.triggering_id
                found_frame.slot_id = currentframe.slot_id[:]
                found_frame.repetition = int(currentframe.repetition)
                found_frame.offset = int(currentframe.offset)

        for ecu in self.ecus:
            connectors = ecu.find('{http://www.asam.net/xml/fbx}CONNECTORS')
            for connector in connectors:    # usually only one connector
                ecu_name = ecu.getchildren()[0].text

                inputs = connector.find('{http://www.asam.net/xml/fbx}INPUTS')
                if inputs is not None:
                    for input in inputs:
                        triggering_id = input.find('{http://www.asam.net/xml/fbx}FRAME-TRIGGERING-REF').get('ID-REF')
                        found_frame = self._find_frame_from_x(triggering_id, 'triggering_id')
                        if found_frame is not None:
                            found_frame.receiver.append(ecu_name)

                outputs = connector.find('{http://www.asam.net/xml/fbx}OUTPUTS')
                if outputs is not None:
                    for output in outputs:
                        triggering_id = output.find('{http://www.asam.net/xml/fbx}FRAME-TRIGGERING-REF').get('ID-REF')
                        found_frame = self._find_frame_from_x(triggering_id, 'triggering_id')
                        if found_frame is not None:
                            found_frame.transmitter = ecu_name

    def _fill_offsets(self):
        '''
        Description: From the data stored in hTableOfFrames, fills the hTableOfOfssets structure.
        This is used to differentiate frames with the same slot ID.
        '''
        for frame in self.hTableOfFrames:
            for slot_id in self.hTableOfFrames.get(frame).slot_id:
                if slot_id not in self.hTableOfOffsets:
                    self.hTableOfOffsets[slot_id] = {}
                self.hTableOfOffsets[slot_id][self.hTableOfFrames.get(frame).offset] =\
                 [self.hTableOfFrames.get(frame).repetition,frame]

    def _fill_pdus_table(self):
        '''
        Description: Reads FIBEX file and stores info in the PDUs struct.
        Note: If a PDU is not referenced in any frame, it is not stored.
        '''
        frames = self.elements.find('{http://www.asam.net/xml/fbx}FRAMES')
        pdus = self.elements.find('{http://www.asam.net/xml/fbx}PDUS')

        for frame in frames:

            frame_name = frame.find('{http://www.asam.net/xml}SHORT-NAME').text
            pdu_instances = frame.find('{http://www.asam.net/xml/fbx}PDU-INSTANCES')

            self.hTableOfPDUs[frame_name] = []

            for pdu in pdu_instances:
                currentpdu = _PDU()
                currentpdu.bitpos = int(pdu.find('{http://www.asam.net/xml/fbx}BIT-POSITION').text)
                currentpdu.pdu_id = pdu.find('{http://www.asam.net/xml/fbx}PDU-REF').get('ID-REF')
                currentpdu.endianness = pdu.find('{http://www.asam.net/xml/fbx}IS-HIGH-LOW-BYTE-ORDER').text
                if currentpdu.endianness == 'true':  # Motorola
                    currentpdu.endianness = 1
                else:   # Intel
                    currentpdu.endianness = 0
                self.hTableOfPDUs[frame_name].append(currentpdu)

        for pdu in pdus:
            currentpdu = _PDU()
            currentpdu.pdu_id = pdu.get('ID')
            currentpdu.pdu_name = pdu.find('{http://www.asam.net/xml}SHORT-NAME').text
            currentpdu.pdu_length = pdu.find('{http://www.asam.net/xml/fbx}BYTE-LENGTH').text
            currentpdu.pdu_type = pdu.find('{http://www.asam.net/xml/fbx}PDU-TYPE').text

            signal_instances = pdu.find('{http://www.asam.net/xml/fbx}SIGNAL-INSTANCES')

            if signal_instances is not None:
                for signal in signal_instances:
                    signal_instance = signal.find('{http://www.asam.net/xml/fbx}SIGNAL-REF').get('ID-REF')
                    currentpdu.signal_instances.append(signal_instance)

            # only for fibex v3.1.0
            # elif self.fibex_version=="3.1.0":
            #     currentpdu.multiplexer = True
            #     multiplexer = pdu.find('{http://www.asam.net/xml/fbx}MULTIPLEXER')
            #     switch_pdus =  multiplexer.find('{http://www.asam.net/xml/fbx}DYNAMIC-PART').find('{http://www.asam.net/xml/fbx}SWITCHED-PDU-INSTANCES')
            #     for switch_pdu in switch_pdus:
            #        sw_pdu_id = switch_pdu.find('{http://www.asam.net/xml/fbx}PDU-REF').get('ID-REF')
            #        currentpdu.switch_pdu_instances.append(sw_pdu_id)
            #
            #     currentpdu.endianness = multiplexer.find('{http://www.asam.net/xml/fbx}SWITCH').find('{http://www.asam.net/xml/fbx}IS-HIGH-LOW-BYTE-ORDER').text
            #     if currentpdu.endianness == 'true':  # Motorola
            #         currentpdu.endianness = 1
            #     else:   # Intel
            #         currentpdu.endianness = 0

            #pending fields: bitpos

            found_pdu = self._find_pdu_from_pid(currentpdu.pdu_id)

            if found_pdu is None:   # if it is None, this PDU is not instanced in any frame
                self.hTableOfSwitchPDUs[currentpdu.pdu_id] = currentpdu;    # add it to the switchPDU array

            else:   # update uninitialized fields
                found_pdu.pdu_name = currentpdu.pdu_name
                found_pdu.pdu_length = currentpdu.pdu_length
                found_pdu.pdu_type = currentpdu.pdu_type
                found_pdu.multiplexer = currentpdu.multiplexer
                found_pdu.switch_pdu_instances = currentpdu.switch_pdu_instances
                found_pdu.signal_instances = currentpdu.signal_instances

    def _fill_signals_table_v3(self):
        '''
        Description: Reads FIBEX v3.x.0 file and stores info in the signals struct.

        Note: Fills both hTableOfSignals3 (used by PDU specific methods) and hTableOfSignals
        (used by generic methods).

        '''
        frames = self.elements.find('{http://www.asam.net/xml/fbx}FRAMES')
        pdus = self.elements.find('{http://www.asam.net/xml/fbx}PDUS')
        signals = self.elements.find('{http://www.asam.net/xml/fbx}SIGNALS')

        # get signals of each pdu
        for pdu in pdus:
            pdu_name = pdu.find('{http://www.asam.net/xml}SHORT-NAME').text
            signal_instances = pdu.find('{http://www.asam.net/xml/fbx}SIGNAL-INSTANCES')

            self.hTableOfSignals3[pdu_name] = []

            # fill hTableOfSignals3 list
            if signal_instances is not None:
                for signal in signal_instances:
                    currentsignal = _Signal()
                    currentsignal.bitpos = int(signal.find('{http://www.asam.net/xml/fbx}BIT-POSITION').text)
                    currentsignal.endianness = signal.find('{http://www.asam.net/xml/fbx}IS-HIGH-LOW-BYTE-ORDER').text
                    if currentsignal.endianness == 'true':  # Motorola
                        currentsignal.endianness = 1
                    else:   # Intel
                        currentsignal.endianness = 0
                    currentsignal.signal_id = signal.find('{http://www.asam.net/xml/fbx}SIGNAL-REF').get('ID-REF')
                    self.hTableOfSignals3[pdu_name].append(currentsignal)

            # sort signals as they are ordered in pdu
            self.hTableOfSignals3[pdu_name].sort(key = lambda s: s.bytepos)
            self.hTableOfSignals3[pdu_name].sort(key = lambda s: s.bitpos)

        # parse and set processing info
        for signal in signals:
            currentsignal = _Signal()
            signal_id = signal.get('ID')

            currentsignal.signalName = signal.find('{http://www.asam.net/xml}SHORT-NAME').text
            try:
                currentsignal.value = signal.find('{http://www.asam.net/xml/fbx}DEFAULT-VALUE').text
            except:
                pass    # default value is left as 0

            currentsignal.coding.coding_id = signal.find('{http://www.asam.net/xml/fbx}CODING-REF').get('ID-REF')

            found_signal = self._find_signal_from_sid(signal_id, self.hTableOfSignals3)
            found_signal.signalName = currentsignal.signalName
            try:
                found_signal.value = int(currentsignal.value)
            except ValueError:
                found_signal.value = int(float(currentsignal.value))

            found_signal.coding.coding_id = currentsignal.coding.coding_id

        self._set_processing_info(self.hTableOfSignals3)

        # assign signals to each frame
        for frame in self.hTableOfFrames:
            self.hTableOfSignals[frame] = []

            # fill hTableOfSignals list
            p_instances = self.hTableOfPDUs.get(frame)
            for p_instance in p_instances:
                for s_id in p_instance.signal_instances:
                    found_signal = self._find_signal_from_sid(s_id, self.hTableOfSignals3)
                    found_signal.bitpos += p_instance.bitpos
                    found_signal.bytepos = found_signal.bitpos/8
                    self.hTableOfSignals[frame].append(found_signal)

            # sort signals as they are ordered in frame
            self.hTableOfSignals[frame].sort(key = lambda s: s.bitpos, reverse = True)
            self.hTableOfSignals[frame].sort(key = lambda s: s.bytepos)

    def _fill_signals_table_v2(self):
        '''
        Description: Reads FIBEX v2.0.0 file and stores info in the signals struct.
        '''
        frames = self.elements.find('{http://www.asam.net/xml/fbx}FRAMES')
        signals = self.elements.find('{http://www.asam.net/xml/fbx}SIGNALS')

        for frame in frames:

            frame_name = frame.find('{http://www.asam.net/xml}SHORT-NAME').text
            signal_instances = frame.find('{http://www.asam.net/xml/fbx}SIGNAL-INSTANCES')

            self.hTableOfSignals[frame_name] = []

            for signal in signal_instances:
                currentsignal = _Signal()
                currentsignal.bitpos = int(signal.find('{http://www.asam.net/xml/fbx}BIT-POSITION').text)
                currentsignal.bytepos = currentsignal.bitpos/8
                currentsignal.endianness = signal.find('{http://www.asam.net/xml/fbx}IS-HIGH-LOW-BYTE-ORDER').text
                if currentsignal.endianness == 'true':  # Motorola
                    currentsignal.endianness = 1
                else:   # Intel
                    currentsignal.endianness = 0
                currentsignal.signal_id = signal.find('{http://www.asam.net/xml/fbx}SIGNAL-REF').get('ID-REF')
                self.hTableOfSignals[frame_name].append(currentsignal)

            # sort signals as they are placed in frame
            self.hTableOfSignals[frame_name].sort(key = lambda s: s.bitpos, reverse = True)
            self.hTableOfSignals[frame_name].sort(key = lambda s: s.bytepos)

        for signal in signals:
            currentsignal = _Signal()
            signal_id = signal.get('ID')

            currentsignal.signalName = signal.find('{http://www.asam.net/xml}SHORT-NAME').text
            try:
                currentsignal.value = signal.find('{http://www.asam.net/xml/fbx}DEFAULT-VALUE').text
            except:
                pass    # default value is left as 0

            currentsignal.coding.coding_id = signal.find('{http://www.asam.net/xml/fbx}CODING-REF').get('ID-REF')

            found_signal = self._find_signal_from_sid(signal_id, self.hTableOfSignals)
            found_signal.signalName = currentsignal.signalName
            found_signal.value = int(currentsignal.value)
            found_signal.coding.coding_id = currentsignal.coding.coding_id

        self._set_processing_info(self.hTableOfSignals)

    def _set_processing_info(self, table):
        '''
        Description: sets signals processing information.
        Used by hTableOfSignals and hTableOfSignals3.
        '''
        processinginfo = self.root.find('{http://www.asam.net/xml/fbx}PROCESSING-INFORMATION')

        codings = processinginfo.find('{http://www.asam.net/xml/fbx}CODINGS')
        for coding in codings:
            currentsignal = _Signal()
            coded_type = coding.find('{http://www.asam.net/xml}CODED-TYPE')
            compu_methods = coding.find('{http://www.asam.net/xml}COMPU-METHODS')
            if compu_methods is not None:
                compu_method = compu_methods.find('{http://www.asam.net/xml}COMPU-METHOD')

            currentsignal.coding.coding_id = coding.get('ID')
            currentsignal.coding.coding_name = coding.find('{http://www.asam.net/xml}SHORT-NAME').text
            currentsignal.coding.bit_length = int(coded_type.find('{http://www.asam.net/xml}BIT-LENGTH').text)
            currentsignal.coding.coded_type = coded_type.get('{http://www.asam.net/xml}BASE-DATA-TYPE')
            if currentsignal.coding.coded_type == 'A_UINT16':
                currentsignal.coding.coded_type = c_uint16
            elif currentsignal.coding.coded_type == 'A_UINT8':
                currentsignal.coding.coded_type = c_uint8

            unit = None

            if compu_methods is not None:
                currentsignal.coding.computation_method = compu_method.find('{http://www.asam.net/xml}CATEGORY').text

                unit = compu_method.find('{http://www.asam.net/xml}UNIT-REF')


            if unit is not None:
                currentsignal.unit.unit_id = unit.get('ID-REF')

            if currentsignal.coding.computation_method == 'LINEAR':
                coeffs = compu_method.find('{http://www.asam.net/xml}COMPU-INTERNAL-TO-PHYS').find('{http://www.asam.net/xml}COMPU-SCALES')[0][0]
                currentsignal.coding.compu_numerator[0] = float(coeffs.find('{http://www.asam.net/xml}COMPU-NUMERATOR')[0].text)

                try:
                    currentsignal.coding.compu_numerator[1] = float(coeffs.find('{http://www.asam.net/xml}COMPU-NUMERATOR')[1].text)
                except:
                    currentsignal.coding.compu_numerator[0] = 0    # use default values
                    currentsignal.coding.compu_numerator[1] = 1    # do not convert

                try:
                    currentsignal.coding.compu_denominator = int(coeffs.find('{http://www.asam.net/xml}COMPU-DENOMINATOR')[0].text)
                except ValueError:
                    currentsignal.coding.compu_denominator = float(coeffs.find('{http://www.asam.net/xml}COMPU-DENOMINATOR')[0].text)
                except TypeError:
                    pass    # Leave default value



            found_signals = self._find_signals_from_x(currentsignal.coding.coding_id, table, 'coding', 'coding_id')
            for signal in found_signals:
                signal.coding.coding_name = currentsignal.coding.coding_name
                signal.coding.bit_length = currentsignal.coding.bit_length
                signal.coding.constraints = 2**signal.coding.bit_length - 1
                signal.coding.coded_type = currentsignal.coding.coded_type
                signal.coding.computation_method = currentsignal.coding.computation_method
                signal.coding.compu_numerator = currentsignal.coding.compu_numerator
                signal.coding.compu_denominator = currentsignal.coding.compu_denominator
                signal.unit.unit_id= currentsignal.unit.unit_id

        units = processinginfo.find('{http://www.asam.net/xml}UNIT-SPEC')
        if units is not None:
            units = units[0]
            for unit in units:
                currentunit = _Unit()
                currentunit.unit_id = unit.get('ID')
                currentunit.unit_name = unit.find('{http://www.asam.net/xml}SHORT-NAME').text
                try:
                    currentunit.display = unit.find('{http://www.asam.net/xml}DISPLAY-NAME').text
                except AttributeError:
                    currentunit.display = currentunit.unit_name

                found_signals = self._find_signals_from_x(currentunit.unit_id, table, 'unit', 'unit_id')

                for signal in found_signals:
                    signal.unit.unit_name = currentunit.unit_name
                    signal.unit.display = currentunit.display
					
    def _bitpos_3_to_2(self, signal):
        '''
        Description: Converts the bit position format of a signal from version 3.x to
        the one used in version 2.x
        Parameter 'signal' is an object of class Signal.
        Returns the converted bit position (Start bit) value
        '''
        bytes = signal.coding.bit_length / 8
        if signal.coding.bit_length % 8:
            bytes += 1

        bl = signal.bitpos
        while bl % 8:
            bl += 1
        bl -= 1  # Highest bit of the lowest byte (left)

        br = bl + 8 * (bytes - 1) 	 # Highest bit of the highest byte (right)

        el = bl - signal.bitpos 	 # Empty bits left
        er = bytes * 8 - signal.coding.bit_length - el  # Empty bits right

        bitpos = br - (7 - er)

        return bitpos
		
    def _test_table_of_signals(self):
        '''
        Description: Used to list the table of signals
        '''
        for frame in self.hTableOfSignals:
            print '\n#####################\n' + frame +'\n#####################'
            localslistOfSignals = self.hTableOfSignals.get(frame);
            for localsignal in localslistOfSignals:
                print '------------'
                print 'Name: ' + localsignal.signalName + ' (' + str(localsignal.signal_id) + ')'
                print 'Bit position: ' + str(localsignal.bitpos)
                print 'Byte Order: ',
                if localsignal.endianness == 0:
                    print 'INTEL'
                else:
                    print 'MOTOROLA'
                print 'Value: '+ str(localsignal.value)
                print 'Bit length: '+ str(localsignal.coding.bit_length)

    def _test_table_of_frames(self):
        '''
        Description: Used to list the table of frames
        '''
        for i in self.hTableOfFrames:
            testout = self.hTableOfFrames[i]
            print '\n------------'
            print 'Name: ' + testout.name
            print 'Slot ID: ' + str(testout.slot_id)
            print 'Repetition: ' + str(testout.repetition)
            print 'Length: ' + str(testout.length)
            print 'Transmitter: ' + str(testout.transmitter)
            print 'Receiver(s): ' + str(testout.receiver)
            if self.fibex_version == "2.0.0d":
                print 'Signals:',
                print testout.signal_instances
            else:
                print 'PDUs:',
                print testout.pdu_instances

    def get_bitpos(self, signal):
        """
        Return bitpos of the signal converted to the format used in
        Fibex v2.x

        Arguments:
            signal (_Signal)
        """
        if re.match(r'^3\.\d\.\d', self.fibex_version):  # Fibex v3.x.x
            return self._bitpos_3_to_2(signal)
        else:
            return signal.bitpos

    def burst_frame_to_tx(self, frame, rawdata, size):
        payload = 0
        data = []
        byte_mask = 0xff
        tx_frame = _FrameToTx()

        # Motorola (BigEndian)

        data = rawdata

        tx_frame.payload_length = (size/2 + size % 2)   # bytes to words. If odd num of bytes, add one
        tx_frame.repetition = frame.repetition
        tx_frame.offset = frame.offset
        tx_frame.data = data
        tx_frame.fr_id = frame.slot_id

        return tx_frame

    def create_empty_frame(self):
        frame = _Frame()
        return frame
