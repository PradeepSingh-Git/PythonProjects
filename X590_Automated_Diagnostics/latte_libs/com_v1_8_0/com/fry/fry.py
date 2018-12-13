import threading
from fibex import FIBEX
from ctypes import *


class _FrFrameRcv (object):
    '''
    Class for storing received frames.
    '''
    def __init__(self):
        self.slotid = 0
        self.event_type = 0
        self.cycle_count = 0
        self.base = 0
        self.payload_length = 0
        self.data = []
        self.updateFlag = False


class FLEXRAY (object):
    '''
    Class for managing FlexRay frames in a bus. Allows to work with FIBEX files.
    This class is used by COM class in com.py, so you'll see all examples below
    with the real usage in a Python script.
    '''
    def __init__(self, index, fibex_file, fr_channel, cold_start_slots):
        '''
        Description: Constructor.
        Parameter 'index' is the channel index used for tx/rx FlexRay frames.
        The channel index available are listed when creating a COM object.

        Parameter 'fibex_file' is the filename of a FIBEX file with the description
        of the FlexRay cluster, controller and events.
        '''
        self.fibex = FIBEX(fibex_file, fr_channel, cold_start_slots)
        self.index = index
        self._frames_received = {} # FrFrameRcv objects indexed by frameName
        self._frames_transmitting = set() # frame names. Used a set() so that items are not repeated
        self._rx_thread_active = False
        self._frStatus = 'FR_STATUS_UNKNOWN'

    def _start_frame_reception(self):
        '''
        Description: Launches RX thread.
        '''
        if not self._rx_thread_active:
            g_notification_handle = 0
            self._rx_thread_active = True
            self.rx_thread = threading.Thread(target = self._rx_task)
            self.rx_thread.daemon = True
            self.rx_thread.start()

    def _stop_frame_reception(self):
        '''
        Description: Stops the TX frames scheduler section in _rx_task thread. This will also disable the RX section.
        '''
        self._rx_thread_active = False
        self.rx_thread.join()

    def _rx_task(self):
        '''
        Description: Reads frames from channel and stores them in a buffer structure.
        '''
        while self._rx_thread_active:


            fr, fr_status = self.read_fr_frame(self.index) # read_fr_frame added dynamically in com.py
            if fr_status != '':
                self._frStatus = fr_status

            if fr != [] and fr != None and fr[4] != []:
                found = False
                # find offset (base) and frameName
                offsets = self.fibex.hTableOfOffsets.get(fr[0])
                cycle = fr[2]
                try:
                    for offset in offsets:
                        if (cycle-offset)%offsets[offset][0] == 0:
                            base = offset
                            frame_name = offsets[offset][1]
                            break
                except TypeError:   # don't save rx frame if slotID is not in FIBEX
                    break

                if frame_name in self._frames_received:
                    found = True
                    localframe = self._frames_received[frame_name]
                    localframe.cycle_count = fr[2]
                    localframe.data = fr[4]
                    localframe.updateFlag = True

                if not found:
                    self._add_frame_to_rcv(fr, base, frame_name)

    def _add_frame_to_rcv(self, fr, base, frame_name):
            '''
            Description: Creates a new object in the main received frames buffer.
            '''
            frRcv = _FrFrameRcv()
            frRcv.updateFlag = True
            frRcv.base = base
            (frRcv.slotid, frRcv.event_type, frRcv.cycle_count,
            frRcv.payload_length, frRcv.data) = fr
            self._frames_received[frame_name] = frRcv

    def _transmit_frame(self, frame, mode, data=[]):
        '''
        Description: Prepares and sends a frame using the given mode.
        Parameter 'frame' is an object of class Frame.
        Parameter 'mode' is an int.
        '''
        tx_frame = self.fibex.prepare_frame_to_tx(frame, data)
        for fr_id in tx_frame.fr_id:    # some frames have more than one slotID assigned
            self.write_fr_frame(self.index, fr_id , mode, tx_frame.data, tx_frame.payload_length, tx_frame.repetiton, tx_frame.offset, self.fibex.cluster_config.erayChannel)
            self._frames_transmitting.add(frame.name)

    def _check_value(self, signalName, raw_value, phys = 0):
        '''
        Description: Checks if raw_value is a valid value for the given signal.
        If the given value is not valid, prints an error message.

        Returns: True or False

        '''
        localframe, localsignal = self.fibex.look_for_frame_and_signal(signalName)
        value_type = 'raw'
        max_val = localsignal.coding.constraints

        valid = raw_value <= max_val

        if phys:
            value_type = 'physical'
            max_val = self.fibex.raw_to_phys(signalName, max_val)[0]

        if not valid:
            print 'Error, \'%s\' %s value cannot be greater than %d.' %(signalName, value_type, max_val)

        return valid

    def set_signal(self, signalName, raw_value, mode = 1):
        '''
        Description: Sends a cyclic frame containing signalName signal
        and its value set to raw_value.
        Parameter 'signalName' is a string.
        Parameter 'signalvalue' is an integer.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'set_signal_single_shot' and 'stop_signal' methods.

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal('GearLock', 0)
        '''
        localframe, localsignal = self.fibex.look_for_frame_and_signal(signalName)
        try:
            if self._check_value(signalName, raw_value):
                localsignal.value = raw_value
                self._transmit_frame(localframe, mode)

        except AttributeError:
            print 'Error, signal not in FIBEX.'

    def set_signal_single_shot(self, signalName, raw_value):
        '''
        Description: Sends a single-shot frame containing signalName signal
        and its value set to raw_value.
        Parameter 'signalName' is a string.
        Parameter 'signalvalue' is an integer.

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal_single_shot('GearLock', 0)
        '''
        self.set_signal(signalName, raw_value, 2)

    def set_phys_signal(self, signalName, phys_value, mode = 1):
        '''
        Description: Sends a cyclic frame containing signalName signal
        and its value set to raw_value.
        Parameter 'signalName' is a string.
        Parameter 'signalvalue' is an integer.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If the given value is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_phys_signal('CarSpeed', 120)
        '''
        try:
            raw_value = int(self.fibex.phys_to_raw(signalName, phys_value))
            if self._check_value(signalName, raw_value, 1):
                self.set_signal(signalName, raw_value, mode)
        except (TypeError, AttributeError):
            print 'Error, signal not in FIBEX.'

    def stop_signal(self, signalName):
        '''
        Description: Stops transmission of the frame that contanis the given signal.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.set_signal('GearLock', 0)
            fr_1.stop_signal('GearLock')
        '''
        localframe, localsignal = self.fibex.look_for_frame_and_signal(signalName)
        try:
            self._transmit_frame(localframe, 255)
        except AttributeError:
            print 'Error, signal not in FIBEX,'
            return

        self._frames_transmitting.remove(localframe.name)

    def send_frame_data(self, frameName, data, mode = 1):
        '''
        Description: Sends the selected frame periodically with its signals set to the given raw values.
        Parameter 'frameName' is a string.
        Parameter 'data' is a list with the payload bytes to be sent.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [0x15, 0x02])
        '''
        localframe = self.fibex.hTableOfFrames.get(frameName)
        if localframe is not None:
            self._transmit_frame(localframe, mode, data)
        else:
            print 'Error, frame not in FIBEX.'

    def send_frame(self, frameName, raw_values = [], mode = 1):
        '''
        Description: Sends the selected frame periodically with its signals set to the given raw values.
        Parameter 'frameName' is a string.
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
        '''
        localframe = self.fibex.hTableOfFrames.get(frameName)
        if localframe is not None:
            signals = self.fibex.hTableOfSignals.get(frameName)
            if raw_values != []:
                try:
                    for i, signal in enumerate(signals):
                        if self._check_value(signal.signalName, raw_values[i]):
                            signal.value = raw_values[i]
                        else:
                            return
                except IndexError:
                    print 'Error, not enough values.'
                    return

            self._transmit_frame(localframe, mode)
        else:
            print 'Error, frame not in FIBEX.'

    def send_frame_single_shot(self, frameName, values = []):
        '''
        Description: Sends a single-shot of the selected frame with its signals set to the given values.
        Parameter 'frameName' is a string.
        Parameter 'values' is a list with the values of the frame's signals sorted by signal position in frame.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame_single_shot('BackLightInfo', [1,0])
        '''
        self.send_frame(frameName, values, 2)

    def send_phys_frame(self, frameName, phys_values, mode = 1):
        '''
        Description: Sends the selected frame periodically with its signals set to the given physical values.
        Parameter 'frameName' is a string.
        Parameter 'phys_values' is a list with the values of the frame's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_phys_frame('BackLightInfo', [1,0])
        '''
        localframe = self.fibex.hTableOfFrames.get(frameName)
        signals = self.fibex.hTableOfSignals.get(frameName)
        try:
            for i, signal in enumerate(signals):
                raw_value = int(self.fibex.phys_to_raw(signal.signalName, phys_values[i]))
                if self._check_value(signal.signalName, raw_value, 1):
                    signal.value = raw_value
                else:
                    return
        except TypeError:
            print 'Error, frame not in FIBEX.'
            return

        except IndexError:
            print 'Error, not enough values.'
            return

        self._transmit_frame(localframe, mode)

    def stop_frame(self, frameName):
        '''
        Description: Stops transmission of the selected frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [1,0])
            fr_1.stop_frame('BackLightInfo')
        '''
        localframe = self.fibex.hTableOfFrames.get(frameName)
        try:
            self._transmit_frame(localframe, 255)
        except AttributeError:
            print 'Error, frame not in FIBEX.'
            return

        self._frames_transmitting.remove(frameName)

    def send_pdu(self, pduName, raw_values = [], mode = 1):
        '''
        Description: Sends a cyclic frame with the PDU set to the given raw values.
        Parameter 'pduName' is a string.
        Parameter 'raw_values' is a list with the values of the PDU's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Only available with FIBEX v3.0.0 files.

        Note: If any of the given values is not valid, the frame is not sent.

        Note: Parameter 'mode' is used internally in this class.
        For other modes use 'send_pdu_single_shot' and 'stop_pdu' methods.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu('CouplerAccelPedalPosition', [0x23, 0xa2])
        '''
        if self.fibex.fibex_version == '3.0.0':
            localframe = self.fibex.look_for_frame_from_pdu(pduName)
            if localframe is not None:
                signals = self.fibex.hTableOfSignals3.get(pduName)
                if raw_values != []:
                    try:
                        for i, signal in enumerate(signals):
                            if self._check_value(signal.signalName, raw_values[i]):
                                signal.value = raw_values[i]
                            else:
                                return
                    except IndexError:
                        print 'Error, not enough values.'
                        return

                self._transmit_frame(localframe, mode)
            else:
                print 'Error, PDU not in FIBEX.'
        else:
            print 'Only available with FIBEX v3.0.0 files.'

    def send_pdu_single_shot(self, pduName, raw_values = []):
        '''
        Description: Sends a single-shot frame with the PDU set to the given raw values.
        Parameter 'pduName' is a string.
        Parameter 'raw_values' is a list with the values of the PDU's signals sorted by signal position in frame.

        Note: Only available with FIBEX v3.0.0 files.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu_single_shot('CouplerAccelPedalPosition', [0x23, 0xa2])
        '''
        if self.fibex.fibex_version == '3.0.0':
            self.send_pdu(pduName, raw_values, 2)
        else:
            print 'Only available with FIBEX v3.0.0 files.'

    def send_phys_pdu(self, pduName, phys_values, mode = 1):
        '''
        Description: Sends a cyclic frame with the PDU set to the given physical values.
        Parameter 'pduName' is a string.
        Parameter 'phys_values' is a list with the values of the PDU's signals sorted by signal position in frame.
        Parameter 'mode' is an int, indicates the transmitting mode (cyclic=1, single_shot=2, none=255).

        Note: Only available with FIBEX v3.0.0 files.

        Note: If any of the given values is not valid, the frame is not sent.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_phys_pdu('CouplerAccelPedalPosition', [13, 48])
        '''
        if self.fibex.fibex_version == '3.0.0':
            localframe = self.fibex.look_for_frame_from_pdu(pduName)
            signals = self.fibex.hTableOfSignals3.get(pduName)
            try:
                for i, signal in enumerate(signals):
                    raw_value = int(self.fibex.phys_to_raw(signal.signalName, phys_values[i]))
                    if self._check_value(signal.signalName, raw_value, 1):
                        signal.value = raw_value
                    else:
                        return
            except TypeError:
                print 'Error, PDU not in FIBEX.'
                return

            except IndexError:
                print 'Error, not enough values.'
                return

            self._transmit_frame(localframe, mode)
        else:
            print 'Only available with FIBEX v3.0.0 files.'

    def stop_pdu(self, pduName):
        '''
        Description: Stops transmission of the frame that contanis the given PDU.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'FibexV3.xml')
            fr_1.send_pdu('CouplerAccelPedalPosition', [0x23, 0xa2])
            fr_1.stop_pdu('CouplerAccelPedalPosition')
        '''
        if self.fibex.fibex_version == '3.0.0':
            localframe = self.fibex.look_for_frame_from_pdu(pduName)
            try:
                self._transmit_frame(localframe, 255)
            except AttributeError:
                print 'Error, PDU not in FIBEX.'
                return

            self._frames_transmitting.remove(localframe.name)
        else:
            print 'Only available with FIBEX v3.0.0 files.'

    def stop_tx_frames(self):
        '''
        Description: Stops transmission of all frames (except sync/startup).

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            fr_1.send_frame('BackLightInfo', [1,0])
            fr_1.set_signal('GearLock', 0)
            fr_1.stop_tx_frames()
        '''
        tx_frames = list(self._frames_transmitting)    # size of tx_frames won't change during iteration
        for frame_name in tx_frames:
            self.stop_frame(frame_name)

    def get_Status(self):
        """
        Description: Reports the last status of the flexRay channel
        """
        return self._frStatus

    def get_signal(self, signalName):
        '''
        Description: Finds the signal in the received frames buffer and returns the signal raw value.
        If the signal is not in the received frames buffer, returns None.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signal of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            value = fr_1.get_signal('EngPower')
        '''
        localframe, localsignal = self.fibex.look_for_frame_and_signal(signalName)
        try:
            received_frame = self._frames_received.get(localframe.name)
        except AttributeError:
            print 'Error, signal not in FIBEX'
            return
        try:
            return self.fibex.read_signal_in_frame(localsignal, received_frame.data)
        except AttributeError:
            return None

    def get_phys_signal(self, signalName):
        '''
        Description: Finds the signal in the frames buffer and returns the signal physical value.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signal of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            speed = fr_1.get_phys_signal('CarSpeed')
        '''
        value = self.get_signal(signalName)
        if value is None:
            return value
        else:
            return self.fibex.raw_to_phys(signalName, value)

    def get_frame(self, frameName):
        '''
        Description: Finds the frame in the frames buffer and returns a list
        with the structure: [slotID, type, cycleCount, payloadLength, [B0, B1, B2, B3, B4, B5, B6, B7...]].

        Note: If a frame is returned, the frame is no longer considered as fresh, and new calls
        to this method will return an empty list [], until a new frame arrives.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            brake_control_frame = fr_1.get_frame('BrakeControl')
        '''
        frame = self._frames_received.get(frameName)
        try:
            if frame.updateFlag:
                frame.updateFlag = False
                return [frame.slotid, frame.event_type, frame.cycle_count, frame.payload_length, frame.data]
            else:
                return []
        except AttributeError:
            pass #print 'Error, frame not received.'

    def get_frame_values(self, frameName):
        '''
        Description: Finds the frame in the frames buffer and returns a dictionary
        with all the signals and their raw values.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signals of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            abs = fr_1.get_frame_values('ABSInfo')
        '''
        values = {}
        signals = self.fibex.hTableOfSignals.get(frameName)
        try:
            for signal in signals:
                values[signal.signalName] = self.get_signal(signal.signalName)
        except TypeError:
            print 'Error, frame not in FIBEX.'
            return None

        return values

    def get_frame_phys_values(self, frameName):
        '''
        Description: Finds the frame in the frames buffer and returns a dictionary
        with all the signals and their physical values.

        Note: This method does not check if latest frame was fresh or similar.
        It just returns the signals of the latest frame received. If checking the
        freshness of the frame is important, have a look at method get_frame.

        Example:
            com = COM('VECTOR')
            fr_1 = com.open_fr_channel(1, 'PowerTrain.xml')
            abs = fr_1.get_frame_phys_values('ABSInfo')
        '''
        values = {}
        signals = self.fibex.hTableOfSignals.get(frameName)
        try:
            for signal in signals:
                values[signal.signalName] = self.get_phys_signal(signal.signalName)
        except TypeError:
            print 'Error, frame not in FIBEX.'
            return None

        return values

    def find_name_by_id(self, identifier):
        for frame in self.fibex.hTableOfFrames:
            if self.fibex.hTableOfFrames.get(frame).slot_id[0] == identifier:
                return self.fibex.hTableOfFrames[frame].name

        return 'Frame id not found'