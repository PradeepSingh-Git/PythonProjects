"""
====================================================================
FlexRay library for working with frames/signals and diagnostics
(C) Copyright 2017 Lear Corporation
====================================================================
"""
import threading
from ..data import FIBEX
from ..data import ECUextract
from ..dgn import dgnflex_available
if dgnflex_available:
    from ..dgn import DGN
from collections import deque
import re
import sys


__author__ = 'Marc Teruel'
__version__ = '1.3.2'
__email__ = 'mteruel@lear.com'


'''
CHANGE LOG
==========
1.3.2 Fixed bug _FrFrameRcv members slot_id, timestamp and update_flag used with incorrect naming
1.3.1 Fixed read_value_in_frame for bitlenght <=8
1.3.0 PEP8 rework
1.2.1 Fixed reading diagnostic frames, must be taken from queue
1.2.0 Using database files from <data> folder
1.1.5 Using diagnostics over FlexRay only if enabled in configuration file dgnflex_cfg.py
1.1.4 Use lock in clear_rx_deque method
      Changed thread Semaphore for Lock (increased performance x10)
      Made some methods static
1.1.3 Parameter 'data' of prepare_frame_to_tx set to None as default
      Save received frames in a deque (double-ended queue)
      Fixed read_value_in_frame function
1.1.2 Added initial support for ECU Extract as FlexRay database
1.1.1 Fixed FIBEX loading problems in VCU1 example
1.1.0 Added Gigabox library for FlexRay support
1.0.2 Initial integration of DGN for FlexRay
1.0.1 Added capability to select between channel A or B
1.0.0 Initial version
'''


# FlexRay frame
FR_FRAME_SLOT_ID = 0
FR_FRAME_TYPE = 1
FR_FRAME_CYCLE = 2
FR_FRAME_SIZE = 3
FR_TIME_STAMP = 4
FR_FRAME_DATA = 5

FR_UNKNOWN_NAME = 'Unknown_'

DEQUE_SIZE = 100


class _FrFrameRcv (object):
    """
    Class for storing received frames.
    """
    def __init__(self):
        self.slot_id = []
        self.event_type = 0
        self.cycle_count = 0
        self.base = 0
        self.payload_length = 0
        self.timestamp = 0
        self.data = []
        self.update_flag = False


class _FrameToTx(object):
    """
    Class with the needed parameters to send a frame:
    Slot ID, payload length, repetition, offset and data.
    """
    def __init__(self):
        self.fr_id = []
        self.payload_length = 0
        self.repetition = 0
        self.offset = 0
        self.data = []


class FLEXRAY(object):
    """
    Class for managing FlexRay frames in a bus. Allows to work with FIBEX
    and AUTOSAR ECU Extract files.
    This class is used by COM class in com.py, so you'll see all examples below
    with the real usage in a Python script.
    """
    def __init__(self, index, database_file, fr_channel, cold_start_slots, cluster_name=''):
        """
        Description: Constructor.
        Parameter 'index' is the channel index used for tx/rx FlexRay frames.
        The channel index available are listed when creating a COM object.

        Parameter 'database_file' is the filename of a FIBEX/ECUExtract file with
        the description of the FlexRay cluster, controller and events.

        Parameter 'cluster_name' is the name of the FlexRay cluster to configure in case of
        using an ECU Extract database.
        """
        # Load database_file as FIBEX or AUTOSAR ECU Extract depending on the extension
        extension = re.search("\.[a-z]+", database_file).group()
        if extension == '.xml':
            self.fibex = FIBEX(database_file, fr_channel, cold_start_slots)
            self.database = self.fibex

        elif extension == '.arxml':
            ecu = ECUextract(database_file)
            self.database = ecu.clusters_dict.get(cluster_name)
            if self.database is None:
                print "Error, selected cluster not present in ECU Extract"
                sys.exit()

            ecu.set_startup_config(cluster_name, fr_channel, cold_start_slots)

        self.index = index
        self._frames_received = {}          # FrFrameRcv objects indexed by frameName
        self._rx_frames_deque = {}          # frame_name: [FrFrameRcv0, FrFrameRcv1...]
        self._frames_transmitting = set()   # frame names. Used a set() so that items are not repeated
        self._rx_thread_active = False
        self.rx_thread = None
        self.rx_thread_lock = None
        self.rx_deque_lock = None

        # Init DGN
        if dgnflex_available:
            self._init_dgn()

    def start_frame_reception(self):
        """
        Description: Launches RX thread.
        """
        if not self._rx_thread_active:
            self._rx_thread_active = True
            self.rx_thread = threading.Thread(target=self._rx_task)
            self.rx_thread_lock = threading.Lock()
            self.rx_deque_lock = threading.Lock()
            self.rx_thread.daemon = True
            self.rx_thread.start()

    def stop_frame_reception(self):
        """
        Description: Stops the TX frames scheduler section in _rx_task thread. This will also disable the RX section.
        """
        self._rx_thread_active = False
        self.rx_thread.join()

    def _init_dgn(self):
        """
        Description: Prepares diagnostics in this FlexRay channel and checks configuration.
        """
        self.dgn = DGN("FLEXRAY")
        self.dgn.iso.net.read_dgn_frame_by_id = self.get_frame_by_id_from_deque
        self.dgn.iso.net.write_dgn_frame_by_id = self.send_frame_single_shot_by_id
        self.dgn.iso.net.get_dgn_frame_name = self.find_name_by_id
        self.dgn.iso.net.read_dgn_frame = self.get_frame_from_deque
        self.dgn.iso.net.write_dgn_frame = self.send_frame_data
        self.dgn.iso.net.get_dgn_frame_size = self.get_frame_size
        self.dgn.iso.net.get_frame_values = self.get_frame_values
        self.dgn.iso.net.check_dgn_configuration()

    @staticmethod
    def read_fr_frame(index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        return index

    # noinspection PyUnusedLocal
    @staticmethod
    def write_fr_frame(index, fr_id, mode, data, payload_length, repetition, offset, channel):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        return index

    @staticmethod
    def get_fr_state(index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        return index

    @staticmethod
    def get_fr_cycle(index):
        """
        Dummy useless method. Defined just to be aware of its existence, but in fact is created during
        runtime by com.py library.
        """
        return index

    def _rx_task(self):
        """
        Description: Reads frames from channel and stores them in a buffer structure.
        """
        while self._rx_thread_active:

            frames = self.read_fr_frame(self.index)     # Rad_fr_frame added dynamically in com.py
            # print frames

            for fr in frames:   # Process all the received frames from the list
                if fr[FR_FRAME_SIZE] != 0 and fr[FR_FRAME_DATA] != []:  # Check that the message has data
                    found = False
                    base = 0
                    frame_name = None
                    # find offset (base) and frameName
                    offsets = self.database.hTableOfOffsets.get(fr[FR_FRAME_SLOT_ID])
                    cycle = fr[FR_FRAME_CYCLE]

                    if offsets is not None:     # Check if fr has been found in Fibex
                        for offset in offsets:
                            if (cycle-offset) % offsets[offset][0] == 0:
                                base = offset
                                frame_name = offsets[offset][1]
                                found = True
                                break
                    else:  # Message received not present in Fibex, let's store it with default name
                        frame_name = self._get_default_name(fr[FR_FRAME_SLOT_ID])
                        found = True

                    # Update _frames_received buffer with new message received
                    if found:
                        if frame_name in self._frames_received:
                            self.rx_thread_lock.acquire()
                            localframe = self._frames_received[frame_name]
                            localframe.cycle_count = fr[FR_FRAME_CYCLE]
                            localframe.data = fr[FR_FRAME_DATA]
                            localframe.timestamp = fr[FR_TIME_STAMP]
                            localframe.update_flag = True
                            self.rx_thread_lock.release()
                            
                            # Store frame in FIFO/LIFO deque
                            rx_frame = _FrFrameRcv()
                            (rx_frame.slot_id, rx_frame.event_type, rx_frame.cycle_count,
                             rx_frame.payload_length, rx_frame.timestamp, rx_frame.data) = fr

                            rx_frame.update_flag = True

                            with self.rx_deque_lock:    # Acquire/release
                                rx_deque = self._rx_frames_deque[frame_name]
                                rx_deque.append(rx_frame)   # Add frame to deque
                        else:
                            self._add_frame_to_rcv(fr, base, frame_name)

    def _add_frame_to_rcv(self, fr, base, frame_name):
        """
        Description: Creates a new object in the main received frames buffer.
        and initializes the received frames deque buffer (to use as lifo/fifo)
        """
        fr_rcv = _FrFrameRcv()
        fr_rcv.update_flag = True
        fr_rcv.base = base
        (fr_rcv.slot_id, fr_rcv.event_type, fr_rcv.cycle_count,
         fr_rcv.payload_length, fr_rcv.timestamp, fr_rcv.data) = fr
        self._frames_received[frame_name] = fr_rcv

        # Initialize received frames deque
        fr2 = _FrFrameRcv()
        fr2.update_flag = True
        fr2.base = base
        (fr2.slot_id, fr2.event_type, fr2.cycle_count,
         fr2.payload_length, fr2.timestamp, fr2.data) = fr

        self._rx_frames_deque[frame_name] = deque(maxlen=DEQUE_SIZE)
        self._rx_frames_deque[frame_name].append(fr2)

    def _transmit_frame(self, frame, mode, data=None):
        """
        Description: Prepares and sends a frame using the given mode.
        Parameter 'frame' is an object of class Frame.
        Parameter 'mode' is an int.
        """
        tx_frame = self.prepare_frame_to_tx(frame, data)
        for fr_id in tx_frame.fr_id:    # some frames have more than one slotID assigned
            result = self.write_fr_frame(self.index, fr_id, mode, tx_frame.data, tx_frame.payload_length,
                                         tx_frame.repetition, tx_frame.offset, self.database.cluster_config.erayChannel)
            if result == 1:
                self._frames_transmitting.add(frame.name)

    def _check_value(self, signal_name, raw_value, phys=0):
        """
        Description: Checks if raw_value is a valid value for the given signal.
        If the given value is not valid, prints an error message.

        Returns: True or False

        """
        localframe, localsignal = self.look_for_frame_and_signal(signal_name)
        value_type = 'raw'
        max_val = localsignal.coding.constraints

        valid = raw_value <= max_val

        if phys:
            value_type = 'physical'
            max_val = self.raw_to_phys(signal_name, max_val)[0]

        if not valid:
            print 'ERROR: <{}> {} value cannot be greater than {}'.format(signal_name, value_type, str(max_val))

        return valid

    @staticmethod
    def _get_default_name(frame_id):
        return FR_UNKNOWN_NAME + str(frame_id)

    @staticmethod
    def _from_bytes(data, big_endian=True, offset_adj=0):
        """
        Description: converts an array of bytes to an int value.
                     Emulates int.from_bytes function from Python 3x.

        Arguments:
            data (list) array of bytes
            big_endian (bool)
            offset_adj (int) number of non-valid bits in LSB.
        """
        if isinstance(data, str):
            data = bytearray(data)
        if big_endian:
            data = reversed(data)
        num = 0
        for offset, byte in enumerate(data):
            shift = offset * 8
            if shift:
                shift -= offset_adj
            num += byte << shift
        return num

    def set_signal(self, signal_name, raw_value, mode=1):
        """
        Description: Sends a cyclic frame containing signal_name signal
        and its value set to raw_value.
        Parameter 'signal_name' is a string.
        Parameter 'signalvalue' is an integer.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'set_signal_single_shot' and 'stop_signal' methods.

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal('GearLock', 0)
        """
        localframe, localsignal = self.look_for_frame_and_signal(signal_name)
        try:
            if self._check_value(signal_name, raw_value):
                localsignal.value = raw_value
                self._transmit_frame(localframe, mode)

        except AttributeError:
            print 'Error, signal ' + signal_name + ' not in FIBEX'

    def set_signal_single_shot(self, signal_name, raw_value):
        """
        Description: Sends a single-shot frame containing signal_name signal
        and its value set to raw_value.
        Parameter 'signal_name' is a string.
        Parameter 'signalvalue' is an integer.

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal_single_shot('GearLock', 0)
        """
        self.set_signal(signal_name, raw_value, 2)

    def set_phys_signal(self, signal_name, phys_value, mode=1):
        """
        Description: Sends a cyclic frame containing signal_name signal
        and its value set to raw_value.
        Parameter 'signal_name' is a string.
        Parameter 'signalvalue' is an integer.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_phys_signal('CarSpeed', 120)
        """
        try:
            raw_value = int(self.phys_to_raw(signal_name, phys_value))
            if self._check_value(signal_name, raw_value, 1):
                self.set_signal(signal_name, raw_value, mode)
        except (TypeError, AttributeError):
            print 'Error, signal ' + signal_name + ' not in FIBEX'

    def stop_signal(self, signal_name):
        """
        Description: Stops transmission of the frame that contanis the given signal.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal('GearLock', 0)
            fr_1.stop_signal('GearLock')
        """
        localframe, localsignal = self.look_for_frame_and_signal(signal_name)
        try:
            self._transmit_frame(localframe, 255)
        except AttributeError:
            print 'Error, signal ' + signal_name + ' not in FIBEX'
            return

        self._frames_transmitting.remove(localframe.name)

    def send_frame_data(self, frame_name, data, mode=1, send_all_frame_byte=True):
        """
        Description: Sends the selected frame periodically with its signals set to the given raw values.
        Parameter 'frame_name' is a string.
        Parameter 'data' is a list with the payload bytes to be sent.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [0x15, 0x02])
        """
        localframe = self.database.hTableOfFrames.get(frame_name)
        if localframe is not None:
            temp_length = localframe.length       # Store current frame size configuration, in case it's changed
            if not send_all_frame_byte:
                if len(data) < localframe.length:
                    # Double checking, no more data than message configuration is requested
                    localframe.length = len(data)
            self._transmit_frame(localframe, mode, data)
            localframe.length = temp_length       # Received frame size configuration, in case has been reduced
        else:
            print 'Error, frame ' + frame_name + ' not in FIBEX.'

    def send_frame(self, frame_name, raw_values=None, mode=1):
        """
        Description: Sends the selected frame periodically with its signals set to the given raw values.
        Parameter 'frame_name' is a string.
        Parameter 'raw_values' is a list with the values of the frame's signals sorted by signal position in frame.
        If left empty, sends frame with default values.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'send_frame_single_shot' and 'stop_frame' methods.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [1,0])
        """
        localframe = self.database.hTableOfFrames.get(frame_name)
        if localframe is not None:
            signals = self.database.hTableOfSignals.get(frame_name)
            if raw_values:
                try:
                    for i, signal in enumerate(signals):
                        if self._check_value(signal.signal_name, raw_values[i]):
                            signal.value = raw_values[i]
                        else:
                            return
                except IndexError:
                    print 'Error, not enough values.'
                    return

            self._transmit_frame(localframe, mode)
        else:
            print 'Error, frame ' + frame_name + ' not in FIBEX.'

    def send_frame_single_shot_by_id(self, frame_id, raw_values=None):
        """
        Description: Sends the selected frame periodically with its signals set to the given raw values.
        Parameter 'frame_id' is the id value.
        Parameter 'raw_values' is a list with the values of the frame's signals sorted by signal position in frame.
        If left empty, sends frame with default values.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'send_frame_single_shot' and 'stop_frame' methods.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame(25, [1,0])
        """
        current_frame = self.database.create_empty_frame()
        current_frame.channel = 0
        current_frame.frame_id = 'DgnFrame'
        current_frame.length = len(raw_values)
        current_frame.name = self._get_default_name(frame_id)
        current_frame.slot_id = [frame_id]
        # NOTE: currently using just first slot ID defined in config.. to use all!! under which conditions?
        current_frame.repetition = 1

        self._transmit_frame(current_frame, 2, raw_values)

    def send_frame_single_shot(self, frame_name, values=None):
        """
        Description: Sends a single-shot of the selected frame with its signals set to the given values.
        Parameter 'frame_name' is a string.
        Parameter 'values' is a list with the values of the frame's signals sorted by signal position in frame.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame_single_shot('BackLightInfo', [1,0])
        """
        self.send_frame(frame_name, values, 2)

    def send_phys_frame(self, frame_name, phys_values, mode=1):
        """
        Description: Sends the selected frame periodically with its signals set to the given physical values.
        Parameter 'frame_name' is a string.
        Parameter 'phys_values' is a list with the values of the frame's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_phys_frame('BackLightInfo', [1,0])
        """
        localframe = self.database.hTableOfFrames.get(frame_name)
        signals = self.database.hTableOfSignals.get(frame_name)
        try:
            for i, signal in enumerate(signals):
                raw_value = int(self.phys_to_raw(signal.signal_name, phys_values[i]))
                if self._check_value(signal.signal_name, raw_value, 1):
                    signal.value = raw_value
                else:
                    return
        except TypeError:
            print 'Error, frame ' + frame_name + ' not in FIBEX.'
            return

        except IndexError:
            print 'Error, not enough values.'
            return

        self._transmit_frame(localframe, mode)

    def stop_frame(self, frame_name):
        """
        Description: Stops transmission of the selected frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [1,0])
            fr_1.stop_frame('BackLightInfo')
        """
        localframe = self.database.hTableOfFrames.get(frame_name)
        try:
            self._transmit_frame(localframe, 255)
        except AttributeError:
            print 'Error, frame ' + frame_name + ' not in FIBEX.'
            return

        self._frames_transmitting.remove(frame_name)

    def send_pdu(self, pdu_name, raw_values=None, mode=1):
        """
        Description: Sends a cyclic frame with the PDU set to the given raw values.
        Parameter 'pdu_name' is a string.
        Parameter 'raw_values' is a list with the values of the PDU's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Only available with FIBEX v3.x or AUTOSAR ECU Extracts.

        Note: If any of the given values is not valid, the frame is not sent.

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'send_pdu_single_shot' and 'stop_pdu' methods.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu('CouplerAccelPedalPosition', [0x23, 0xa2])
        """
        localframe = self.look_for_frame_from_pdu(pdu_name)
        if localframe is not None:
            signals = self.database.hTableOfSignals3.get(pdu_name)
            if raw_values:
                try:
                    for i, signal in enumerate(signals):
                        if self._check_value(signal.signal_name, raw_values[i]):
                            signal.value = raw_values[i]
                        else:
                            return
                except IndexError:
                    print 'Error, not enough values.'
                    return

            self._transmit_frame(localframe, mode)
        else:
            print 'Error, PDU not in database.'

    def send_pdu_single_shot(self, pdu_name, raw_values=None):
        """
        Description: Sends a single-shot frame with the PDU set to the given raw values.
        Parameter 'pdu_name' is a string.
        Parameter 'raw_values' is a list with the values of the PDU's signals sorted by signal position in frame.

        Note: Only available with FIBEX v3.x or AUTOSAR ECU Extracts.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu_single_shot('CouplerAccelPedalPosition', [0x23, 0xa2])
        """
        self.send_pdu(pdu_name, raw_values, 2)

    def send_phys_pdu(self, pdu_name, phys_values, mode=1):
        """
        Description: Sends a cyclic frame with the PDU set to the given physical values.
        Parameter 'pdu_name' is a string.
        Parameter 'phys_values' is a list with the values of the PDU's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Only available with FIBEX v3.x or AUTOSAR ECU Extracts.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_phys_pdu('CouplerAccelPedalPosition', [13, 48])
        """
        localframe = self.look_for_frame_from_pdu(pdu_name)
        signals = self.database.hTableOfSignals3.get(pdu_name)
        try:
            for i, signal in enumerate(signals):
                raw_value = int(self.phys_to_raw(signal.signal_name, phys_values[i]))
                if self._check_value(signal.signal_name, raw_value, 1):
                    signal.value = raw_value
                else:
                    return
        except TypeError:
            print 'Error, PDU not in database.'
            return

        except IndexError:
            print 'Error, not enough values.'
            return

        self._transmit_frame(localframe, mode)

    def stop_pdu(self, pdu_name):
        """
        Description: Stops transmission of the frame that contanis the given PDU.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu('CouplerAccelPedalPosition', [0x23, 0xa2])
            fr_1.stop_pdu('CouplerAccelPedalPosition')
        """
        localframe = self.look_for_frame_from_pdu(pdu_name)
        try:
            self._transmit_frame(localframe, 255)
        except AttributeError:
            print 'Error, PDU not in database.'
            return

        self._frames_transmitting.remove(localframe.name)

    def stop_tx_frames(self):
        """
        Description: Stops transmission of all frames (except sync/startup).

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [1,0])
            fr_1.set_signal('GearLock', 0)
            fr_1.stop_tx_frames()
        """
        tx_frames = list(self._frames_transmitting)    # size of tx_frames won't change during iteration
        for frame_name in tx_frames:
            self.stop_frame(frame_name)

    def get_status(self):
        """
        Description: Reports the last status of the flexRay channel based on frStatusTypeEnum
        """
        return self.get_fr_state(self.index)

    def get_cycle(self):
        """
        Description: Reports the flexRay cycle of the last received event
        """
        return self.get_fr_cycle(self.index)

    def get_signal(self, signal_name):
        """
        Description: Finds the signal in the received frames buffer and returns the signal raw value.
        If the signal is not in the received frames buffer, returns None.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signal of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            value = fr_1.get_signal('EngPower')
        """
        localframe, localsignal = self.look_for_frame_and_signal(signal_name)
        try:
            received_frame = self._frames_received.get(localframe.name)
        except AttributeError:
            print 'ERROR: Signal {} not in FIBEX'.format(signal_name)
            return
        try:
            return self.read_signal_in_frame(localsignal, received_frame.data)
        except AttributeError:
            return None

    def get_phys_signal(self, signal_name):
        """
        Description: Finds the signal in the frames buffer and returns the signal physical value.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signal of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            speed = fr_1.get_phys_signal('CarSpeed')
        """
        value = self.get_signal(signal_name)
        if value is None:
            return value
        else:
            return self.raw_to_phys(signal_name, value)

    def get_frame(self, frame_name):
        """
        Description: Finds the frame in the frames buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, timestamp, [B0, B1, B2, ...]].

        Note: If a frame is returned, the frame is no longer considered as fresh, and new calls
        to this method will return an empty list [], until a new frame arrives.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            brake_control_frame = fr_1.get_frame('BrakeControl')
        """
        frame = self._frames_received.get(frame_name)
        if frame:
            self.rx_thread_lock.acquire()
            result_fr = []
            if frame.update_flag:
                frame.update_flag = False
                result_fr = [frame.slot_id, frame.event_type, frame.cycle_count, frame.payload_length,
                             frame.timestamp, frame.data]
            self.rx_thread_lock.release()
            return result_fr
        else:
            return None

    def get_frame_from_deque(self, frame_name, popleft=False):
        """
        Description: Finds the frame in the frames deque buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, timestamp, [B0, B1, B2, B3, B4...]].

        Parameter 'frame_name' is a string
        Parameter 'popleft' is a boolean. It determins wheter to perform a
                   pop (LIFO) or popleft (FIFO) operation.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            brake_control_frame = fr_1.get_frame_from_deque('BrakeControl')
        """
        rx_deque = self._rx_frames_deque.get(frame_name)

        if rx_deque is None:
            return None

        with self.rx_deque_lock:    # Acquire/release
            try:
                if popleft:
                    frame = rx_deque.popleft()
                else:
                    frame = rx_deque.pop()

            except IndexError:
                frame = None

        if frame is not None:
            result_fr = [frame.slot_id, frame.event_type, frame.cycle_count, frame.payload_length,
                         frame.timestamp, frame.data]
            return result_fr
        else:
            return None

    def get_frame_by_id(self, frame_id):
        """
        Description: Finds the frame in the frames buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, [B0, B1, B2, ...]].

        Note: If a frame is returned, the frame is no longer considered as fresh, and new calls
        to this method will return an empty list [], until a new frame arrives.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            brake_control_frame = fr_1.get_frame_by_id(13)
        """
        frame_name = self._get_default_name(frame_id)
        frame = self._frames_received.get(frame_name)
        if frame is not None:
            self.rx_thread_lock.acquire()
            if frame.update_flag:
                frame.update_flag = False
                result_fr = [frame.slot_id, frame.event_type, frame.cycle_count, frame.payload_length,
                             frame.timestamp, frame.data]
                self.rx_thread_lock.release()
                return result_fr
            else:
                self.rx_thread_lock.release()
                return []
        else:
            pass

    def get_frame_by_id_from_deque(self, frame_id, popleft=False):
        """
        Description: Finds the frame in the frames deque buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, timestamp, [B0, B1, B2, B3, B4...]].

        Parameter 'frame_id' is a number indicating the slot ID
        Parameter 'popleft' is a boolean. It determins wheter to perform a
                   pop (LIFO) or popleft (FIFO) operation.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            brake_control_frame = fr_1.get_frame_from_deque('BrakeControl')
        """
        frame_name = self._get_default_name(frame_id)
        rx_deque = self._rx_frames_deque.get(frame_name)

        if rx_deque is None:
            return None

        with self.rx_deque_lock:    # Acquire/release
            try:
                if popleft:
                    frame = rx_deque.popleft()
                else:
                    frame = rx_deque.pop()

            except IndexError:
                frame = None

        if frame is not None:
            result_fr = [frame.slot_id, frame.event_type, frame.cycle_count, frame.payload_length,
                         frame.timestamp, frame.data]
            return result_fr
        else:
            return None

    def get_frame_values(self, frame_name):
        """
        Description: Finds the frame in the frames buffer and returns a dictionary
        with all the signals and their raw values.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signals of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            abs = fr_1.get_frame_values('ABSInfo')
        """
        values = {}
        signals = self.database.hTableOfSignals.get(frame_name)
        try:
            for signal in signals:
                values[signal.signal_name] = self.get_signal(signal.signal_name)
        except TypeError:
            print 'Error, frame ' + frame_name + ' not in database.'
            return None

        return values

    def get_frame_size(self, frame_name):
        """
        Description: Report the frame length.
        Parameter 'frame_name' is a string.

        Note: If frame_name is not present in FIibex, size will be reported as 0.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            size = fr_1.get_frame_size('BackLightInfo')
        """
        local_frame = self.database.hTableOfFrames.get(frame_name)
        if local_frame:
            return local_frame.length
        else:
            return 0

    def get_frame_phys_values(self, frame_name):
        """
        Description: Finds the frame in the frames buffer and returns a dictionary
        with all the signals and their physical values.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signals of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            abs = fr_1.get_frame_phys_values('ABSInfo')
        """
        values = {}
        signals = self.database.hTableOfSignals.get(frame_name)
        try:
            for signal in signals:
                values[signal.signal_name] = self.get_phys_signal(signal.signal_name)
        except TypeError:
            print 'Error, frame ' + frame_name + ' not in database.'
            return None

        return values

    def find_name_by_id(self, identifier):
        for frame in self.database.hTableOfFrames:
            if self.database.hTableOfFrames.get(frame).slot_id[0] == identifier:
                return self.database.hTableOfFrames[frame].name

        return 'Frame id not found'

    def look_for_frame_and_signal(self, signal_name):
        """
        Description: Finds the frame containing signal=signal_name.
        Returns frame_found (object of class Frame) and signal (object of class Signal).

        Example:
            >>> flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            >>> f,s = flexray.look_for_frame_and_signal('GearLock')
        """
        for frame_i in self.database.hTableOfSignals:
            local_list_of_signals = self.database.hTableOfSignals.get(frame_i)
            for signal_i in local_list_of_signals:
                if signal_i.signal_name == signal_name:   # case insensitive
                    frame_found = self.database.hTableOfFrames.get(frame_i)
                    return frame_found, signal_i
        return None, None

    def look_for_frame_and_signal_group(self, signal_group_name):
        """
        Finds the frame containing signal_group=signal_group_name.

        Arguments:
            signal_group_name (str)

        Returns:
            found _Frame and _Signal objects

        Example:
            flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            f,sg = flexray.look_for_frame_and_signal_group('igBrkTq')
        """
        try:
            signal_groups = self.database.signal_groups
        except AttributeError:
            print 'Error: signal group {} not found. Database does not have a table of signal groups'\
                  .format(signal_group_name)
            return None, None

        signal_group = signal_groups.get(signal_group_name)
        if signal_group:
            signal_name = signal_group.signal_instances[0]
            for frame_name, frame in self.database.hTableOfFrames.iteritems():
                for s in frame.signal_instances:
                    if s == signal_name:
                        return frame, signal_group

            return None, signal_group

        else:
            print 'Error: signal group {} not found'.format(signal_group_name)
            return None, None

    def look_for_frame_from_pdu(self, pdu_name):
        """
        Description: Finds the frame containing pdu=pdu_name.
        Returns frame_found (object of class Frame).

        Example:
            flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            accelgravity_frame = flexray.look_for_frame_from_pdu('AccelGravityLongitude')
        """
        for frame in self.database.hTableOfPDUs:
            pdus = self.database.hTableOfPDUs.get(frame)
            for pdu in pdus:
                if pdu.pdu_name.lower() == pdu_name.lower():    # case insensitive
                    frame_found = self.database.hTableOfFrames.get(frame)
                    return frame_found
        return None

    def prepare_frame_to_tx(self, frame, data=None):
        """
        Description: Gets the value and bit position of every signal of the
        given frame and prepares the frame to be transmitted.
        Parameter 'frame' is an object of class Frame.
        Paramter 'data' is an array of bytes.
        Returns object of class FrameToTx.

        Example:
            flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            f,s = flexray.look_for_frame_and_signal('GearLock')
            frame_to_tx = flexray.prepare_frame_to_tx(f)
        """
        payload = 0
        byte_mask = 0xff
        tx_frame = _FrameToTx()
        signals = self.database.hTableOfSignals.get(frame.name)

        if data is None:
            # Build payload with frame's signals
            # Intel (LittleEndian)
            data = []
            if signals[0].endianness == 0:
                for signal in signals:
                    bitpos = self.database.get_bitpos(signal)
                    payload |= signal.value << bitpos  # payload here is in BigEndian

                for i in range(frame.length):
                    data.append((payload >> i*8) & byte_mask)   # mask each byte and reverse order

            # Motorola (BigEndian)
            else:
                for signal in signals:
                    bitpos = self.database.get_bitpos(signal)
                    payload |= signal.value << (8 * (frame.length - 1) - ((8 * (bitpos / 8)) - (bitpos % 8)))

                data = deque()
                for i in range(frame.length):
                    data.appendleft(((payload >> i*8) & byte_mask))  # mask each byte and keep order

                data = list(data)

        tx_frame.payload_length = (frame.length / 2 + frame.length % 2)  # bytes to words. If odd num of bytes, add one
        tx_frame.repetition = frame.repetition
        tx_frame.offset = frame.offset
        tx_frame.data = data
        tx_frame.fr_id = frame.slot_id

        return tx_frame

    def read_value_in_frame(self, byte_pos, bit_pos, bit_length, data, endianness=False):
        """
        Description: Reads a value in a given message.
        Parameter 'byte_pos' is the byte location of the value to read.
        Parameter 'bit_pos' is the position of the first bit of the value to read.
        Parameter 'bit_length' is lenght in bits of the value to read.
        Parameter 'data' is a list containing the payload bytes.
        Parameter 'endianness' is the bit coding. False:Intel (little). True:Motorola (big)

        Example:
            flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            value = flexray.read_value_in_frame(3, 2, 15, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
        """
        b_h = 8 * byte_pos + 7  # msb (bit) of the MSB (byte)

        # Get number of bytes of the signal data and build array with signal bytes
        bits2 = bit_pos + bit_length - b_h  # Number of bits not in LSB
        n_bytes = 1 + bits2 / 8
        if bits2 % 8:
            n_bytes += 1

        signal_bytes = []
        if endianness:
            for i in range(0, n_bytes):
                byte = data[byte_pos - i]
                signal_bytes.insert(0, byte)

        elif not endianness:
            for i in range(0, n_bytes):
                byte = data[byte_pos + i]
                signal_bytes.append(byte)

        # Prepare mask and shift values
        n_bits_lsb = 8 - bit_pos % 8
        n_bits_msb = 8 - (8 * n_bytes - bit_length - (8 - n_bits_lsb))
        shift_first = bit_pos % 8
        mask_last = 0xFF >> (8 - n_bits_msb)

        # Apply mask and shift on first and last byte (position in byte array deppends on endianness)
        if endianness:
            signal_bytes[0] &= mask_last
            signal_bytes[-1] >>= shift_first

        elif not endianness:
            signal_bytes[0] >>= shift_first
            signal_bytes[-1] &= mask_last

        # Convert array of bytes to int value
        return self._from_bytes(signal_bytes, endianness, bit_pos % 8)

    def read_signal_in_frame(self, signal, data):
        """
        Description: Reads signal value in a given message.
        Parameter 'signal' is an object of class Signal.
        Parameter 'data' is a list containing the payload bytes.

        Example:
            flexray = FLEXRAY(0, "PowerTrain.xml", "A", [])
            value = value.read_signal_in_frame(gearlock_signal, [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08])
        """
        bitpos = self.database.get_bitpos(signal)

        value = self.read_value_in_frame(bitpos/8, bitpos, signal.coding.bit_length, data, signal.endianness)

        return value

    def raw_to_phys(self, signal_name, raw_value):
        """
        Description: Computes physical value from raw value.
        Returns physical value and unit.
        """
        local_frame, local_signal = self.look_for_frame_and_signal(signal_name)

        if local_signal.coding.computation_method == 'IDENTICAL':
            return raw_value, local_signal.unit.display

        elif local_signal.coding.computation_method == 'LINEAR':
            phys_val = (local_signal.coding.compu_numerator[1]*raw_value +
                        local_signal.coding.compu_numerator[0]) / local_signal.coding.compu_denominator
            return round(phys_val, 4), local_signal.unit.display

    def phys_to_raw(self, signal_name, phys_value):
        """
        Description: Computes raw value from physical value.
        Returns raw value.
        """
        localframe, localsignal = self.look_for_frame_and_signal(signal_name)

        if localsignal.coding.computation_method == 'IDENTICAL':
            return phys_value

        elif localsignal.coding.computation_method == 'LINEAR':
            return (localsignal.coding.compu_denominator*phys_value - localsignal.coding.compu_numerator[0]) / \
                   localsignal.coding.compu_numerator[1]

    def clear_rx_deque(self):
        """
        Clears the received frames deque, for each received frame ID.
        """
        with self.rx_deque_lock:    # Acquire/release
            for frame_name, frames_deque in self._rx_frames_deque.iteritems():
                frames_deque.clear()
