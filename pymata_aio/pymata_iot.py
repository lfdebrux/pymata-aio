#!/usr/bin/env python3

"""
Copyright (c) 2015 Alan Yorinks All rights reserved.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU  General Public
License as published by the Free Software Foundation; either
version 3 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import json
import asyncio
import datetime
import argparse

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from pymata_aio.pymata_core import PymataCore
from pymata_aio.constants import Constants


class PymataIOT(WebSocketServerProtocol):
    """
    This class implements the PyMata Websocket interface. JSON command messages are received via Websocket connection,
    decoded and mapped to an associated PyMata method to be executed
    operation.

    The methods below are not intended to be called directly. The JSON message format is documented as part of the
    method description. All JSON reply messages (to be handled by the client)  will also be documented for
    within the description.

    usage: pymata_iot.py [-h] [-host HOSTNAME] [-port PORT] [-wait WAIT]
                     [-comport COM] [-sleep SLEEP]

        optional arguments:
          -h, --help      show this help message and exit
          -host HOSTNAME  Server name or IP address
          -port PORT      Server port number
          -wait WAIT      Arduino wait time
          -comport COM    Arduino COM port
          -sleep SLEEP    sleep tune in ms.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", dest="hostname", default="localhost", help="Server name or IP address")
    parser.add_argument("-port", dest="port", default="9000", help="Server port number")
    parser.add_argument("-wait", dest="wait", default="2", help="Arduino wait time")
    parser.add_argument("-comport", dest="com", default="None", help="Arduino COM port")
    parser.add_argument("-sleep", dest="sleep", default=".001", help="sleep tune in ms.")
    args = parser.parse_args()

    ip_addr = args.hostname
    ip_port = args.port

    if args.com == 'None':
        comport = None
    else:
        comport = args.com

    core = PymataCore(int(args.wait), float(args.sleep), comport)
    core.start()

    def __init__(self):
        """
        This is the "constructor" for PymataIOT. It sets up a translation dictionary using incoming JSON commands
        and maps them to command methods.
        @return: No Return.
        """

        self.command_map = {
            "analog_read": self.analog_read,
            "analog_write": self.analog_write,
            "digital_read": self.digital_read,
            "digital_write": self.digital_write,
            "disable_analog_reporting": self.disable_analog_reporting,
            "disable_digital_reporting": self.disable_digital_reporting,
            "enable_analog_reporting": self.disable_analog_reporting,
            "enable_digital_reporting": self.disable_digital_reporting,
            "encoder_config": self.encoder_config,
            "encoder_read": self.encoder_read,
            "get_analog_latch_data": self.get_analog_latch_data,
            "get_analog_map": self.get_analog_map,
            "get_capability_report": self.get_capability_report,
            "get_digital_latch_data": self.get_digital_latch_data,
            "get_firmware_version": self.get_firmware_version,
            "get_pin_state": self.get_pinstate_report,
            "get_protocol_version": self.get_protocol_version,
            "get_pymata_version": self.get_pymata_version,
            "i2c_config": self.i2c_config,
            "i2c_read_data": self.i2c_read_data,
            "i2c_read_request": self.i2c_read_request,
            "i2c_write_request": self.i2c_write_request,
            "play_tone": self.play_tone,
            "set_analog_latch": self.set_analog_latch,
            "set_digital_latch": self.set_digital_latch,
            "set_pin_mode": self.set_pin_mode,
            "set_sampling_interval": self.set_sampling_interval,
            "sonar_config": self.sonar_config,
            "sonar_read": self.sonar_read,
            "servo_config": self.servo_config,
            "stepper_config": self.stepper_config,
            "stepper_step": self.stepper_step
        }

    @asyncio.coroutine
    def analog_read(self, command):
        """
        This method reads and returns the last reported value for an analog pin.
        Normally not used since analog pin updates will be provided automatically
        as they occur with the analog_message_reply being sent to the client after set_pin_mode is called.
        (see enable_analog_reporting for message format).

        @param command: {"method": "analog_read", "params": [ANALOG_PIN]}
        @return: {"method": "analog_read_reply", "params": [PIN, ANALOG_DATA_VALUE]}
        """
        pin = int(command[0])
        data_val = yield from self.core.analog_read(pin)
        reply = json.dumps({"method": "analog_read_reply", "params": [pin, data_val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def analog_write(self, command):
        """
        This method writes a value to an analog pin.

        It is used to set the output of a PWM pin or the angle of a Servo.
        @param command: {"method": "analog_write", "params": [PIN, WRITE_VALUE]}
        @return: No return message.
        """
        pin = int(command[0])
        value = int(command[1])
        yield from self.core.analog_write(pin, value)

    @asyncio.coroutine
    def digital_read(self, command):
        """
        This method reads and returns the last reported value for a digital pin.
        Normally not used since digital pin updates will be provided automatically
        as they occur with the digital_message_reply being sent to the client after set_pin_mode is called..
        (see enable_digital_reporting for message format)

        @param command: {"method": "digital_read", "params": [PIN]}
        @return: {"method": "digital_read_reply", "params": [PIN, DIGITAL_DATA_VALUE]}
        """
        pin = int(command[0])
        data_val = yield from self.core.digital_read(pin)
        reply = json.dumps({"method": "digital_read_reply", "params": [pin, data_val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def digital_write(self, command):
        """
        This method writes a zero or one to a digital pin.
        @param command: {"method": "digital_write", "params": [PIN, DIGITAL_DATA_VALUE]}
        @return: No return message..
        """
        pin = int(command[0])
        value = int(command[1])
        yield from self.core.digital_write(pin, value)

    @asyncio.coroutine
    def disable_analog_reporting(self, command):
        """
        Disable Firmata reporting for an analog pin.
        @param command: {"method": "disable_analog_reporting", "params": [PIN]}
        @return: No return message..
        """
        pin = int(command[0])
        yield from self.core.disable_analog_reporting(pin)

    @asyncio.coroutine
    def disable_digital_reporting(self, command):
        """
        Disable Firmata reporting for a digital pin.
        @param command: {"method": "disable_digital_reporting", "params": [PIN]}
        @return: No return message.
        """
        pin = int(command[0])
        yield from self.core.disable_digital_reporting(pin)

    @asyncio.coroutine
    def enable_analog_reporting(self, command):
        """
        Enable Firmata reporting for an analog pin.
        @param command: {"method": "enable_analog_reporting", "params": [PIN]}
        @return: {"method": "analog_message_reply", "params": [PIN, ANALOG_DATA_VALUE]}
        """
        pin = int(command[0])
        yield from self.core.enable_analog_reporting(pin)

    @asyncio.coroutine
    def enable_digital_reporting(self, command):
        """
        Enable Firmata reporting for a digital pin.

        @param command: {"method": "enable_digital_reporting", "params": [PIN]}
        @return: {"method": "digital_message_reply", "params": [PIN, DIGITAL_DATA_VALUE]}
        """
        pin = int(command[0])
        yield from self.core.enable_digital_reporting(pin)

    @asyncio.coroutine
    def encoder_config(self, command):
        """
        Configure 2 pins for FirmataPlus encoder operation.

        @param command: {"method": "encoder_config", "params": [PIN_A, PIN_B]}
        @return: {"method": "encoder_data_reply", "params": [ENCODER_DATA]}
        """
        pin_a = int(command[0])
        pin_b = int(command[1])
        yield from self.core.encoder_config(pin_a, pin_b, self.encoder_callback)

    @asyncio.coroutine
    def encoder_read(self, command):
        """
        This is a polling method to read the last cached FirmataPlus encoder value.
        Normally not used. See encoder config for the asynchronous report message format.

        @param command: {"method": "encoder_read", "params": [PIN_A]}
        @return: {"method": "encoder_read_reply", "params": [PIN_A, ENCODER_VALUE]}
        """
        pin = int(command[0])
        val = yield from self.core.encoder_read(pin)
        reply = json.dumps({"method": "encoder_read_reply", "params": [pin, val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_analog_latch_data(self, command):
        """
        This method retrieves a latch table entry for an analog pin.

        See constants.py for definition of reply message parameters.

        @param command:  {"method": "get_analog_latch_data", "params": [ANALOG_PIN]}
        @return: {"method": "get_analog_latch_data_reply", "params": [ANALOG_PIN, LATCHED_STATE, THRESHOLD_TYPE,\
         THRESHOLD_TARGET, DATA_VALUE, TIME_STAMP ]}
        """
        pin = int(command[0])
        data_val = yield from self.core.get_analog_latch_data(pin)
        if data_val:
            data_val = data_val[0:-1]
        reply = json.dumps({"method": "get_analog_latch_data_reply", "params": [pin, data_val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_analog_map(self):
        """
        This method retrieves the Firmata analog map.

        Refer to: http://firmata.org/wiki/Protocol#Analog_Mapping_Query to interpret the reply

        The command JSON format is: {"method":"get_analog_map","params":["null"]}
        @return: {"method": "analog_map_reply", "params": [ANALOG_MAP]}
        """
        value = yield from self.core.get_analog_map()
        if value:
            reply = json.dumps({"method": "analog_map_reply", "params": value})
        else:
            reply = json.dumps({"method": "analog_map_reply", "params": "None"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_capability_report(self):
        """
        This method retrieves the Firmata capability report.

        Refer to http://firmata.org/wiki/Protocol#Capability_Query

        The command format is: {"method":"get_capability_report","params":["null"]}

        @return: {"method": "capability_report_reply", "params": [RAW_CAPABILITY_REPORT]}
        """
        value = yield from self.core.get_capability_report()
        asyncio.sleep(.1)
        if value:
            reply = json.dumps({"method": "capability_report_reply", "params": value})
        else:
            reply = json.dumps({"method": "capability_report_reply", "params": "None"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_digital_latch_data(self, command):
        """
        This method retrieves a latch table entry for a digital pin.

        See constants.py for definition of reply message parameters.

        @param command:  {"method": "get_digital_latch_data", "params": [ANALOG_PIN]}
        @return: {"method": "get_digital_latch_data_reply", "params": [DIGITAL_PIN, LATCHED_STATE, THRESHOLD_TYPE,\
         THRESHOLD_TARGET, DATA_VALUE, TIME_STAMP ]}
        """
        pin = int(command[0])
        data_val = yield from self.core.get_digital_latch_data(pin)
        if data_val:
            data_val = data_val[0:-1]
        reply = json.dumps({"method": "get_digital_latch_data_reply", "params": [pin, data_val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_firmware_version(self):
        """
        This method retrieves the Firmata firmware version.

        See: http://firmata.org/wiki/Protocol#Query_Firmware_Name_and_Version


        JSON command: {"method": "get_firmware_version", "params": ["null"]}

        @return: {"method": "firmware_version_reply", "params": [FIRMWARE_VERSION]}
        """
        value = yield from self.core.get_firmware_version()
        if value:
            reply = json.dumps({"method": "firmware_version_reply", "params": value})
        else:
            reply = json.dumps({"method": "firmware_version_reply", "params": "Unknown"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_pinstate_report(self, command):
        """
        This method retrieves a Firmata pin_state report for a pin..

        See: http://firmata.org/wiki/Protocol#Pin_State_Query

        @param command: {"method": "get_pin_state", "params": [PIN]}
        @return: {"method": "get_pin_state_reply", "params": [PIN_NUMBER, PIN_MODE, PIN_STATE]}
        """
        pin = int(command[0])
        value = yield from self.core.get_pin_state(pin)
        if value:
            reply = json.dumps({"method": "pin_state_reply", "params": value})
        else:
            reply = json.dumps({"method": "pin_state_reply", "params": "Unknown"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_protocol_version(self):
        """
        This method retrieves the Firmata protocol version.

        JSON command: {"method": "get_protocol_version", "params": ["null"]}

        @return: {"method": "protocol_version_reply", "params": [PROTOCOL_VERSION]}
        """
        value = yield from self.core.get_protocol_version()
        if value:
            reply = json.dumps({"method": "protocol_version_reply", "params": value})
        else:
            reply = json.dumps({"method": "protocol_version_reply", "params": "Unknown"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def get_pymata_version(self):
        """
         This method retrieves the PyMata release version number.

         JSON command: {"method": "get_pymata_version", "params": ["null"]}

         @return:  {"method": "pymata_version_reply", "params":[PYMATA_VERSION]}
        """
        value = yield from self.core.get_pymata_version()
        if value:
            reply = json.dumps({"method": "pymata_version_reply", "params": value})
        else:
            reply = json.dumps({"method": "pymata_version_reply", "params": "Unknown"})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def i2c_config(self, command):
        """
        This method initializes the I2c and sets the optional read delay (in microseconds).

        It must be called before doing any other i2c operations for a given device.
        @param command: {"method": "i2c_config", "params": [DELAY]}
        @return: No Return message.
        """
        delay = int(command[0])
        yield from self.core.i2c_config(delay)

    @asyncio.coroutine
    def i2c_read_data(self, command):
        """
        This method retrieves the last value read for an i2c device identified by address.
        This is a polling implementation and i2c_read_request and i2c_read_request_reply may be
        a better alternative.
        @param command: {"method": "i2c_read_data", "params": [I2C_ADDRESS ]}
        @return:{"method": "i2c_read_data_reply", "params": i2c_data}
        """
        address = int(command[0])
        i2c_data = yield from self.core.i2c_read_data(address)
        reply = json.dumps({"method": "i2c_read_data_reply", "params": i2c_data})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def i2c_read_request(self, command):
        """
        This method sends an I2C read request to Firmata. It is qualified by a single shot, continuous
        read, or stop reading command.
        Special Note: for the read type supply one of the following string values:

         "0" = I2C_READ

         "1" = I2C_READ | I2C_END_TX_MASK"

         "2" = I2C_READ_CONTINUOUSLY

         "3" = I2C_READ_CONTINUOUSLY | I2C_END_TX_MASK

         "4" = I2C_STOP_READING

        @param command: {"method": "i2c_read_request", "params": [I2C_ADDRESS, I2C_REGISTER,
                NUMBER_OF_BYTES, I2C_READ_TYPE ]}
        @return: {"method": "i2c_read_request_reply", "params": [DATA]}
        """
        device_address = int(command[0])
        register = int(command[1])
        number_of_bytes = int(command[2])

        if command[3] == "0":
            read_type = Constants.I2C_READ_CONTINUOUSLY
        elif command[3] == "1":
            read_type = Constants.I2C_READ
        elif command[3] == "2":
            read_type = Constants.I2C_READ | Constants.I2C_END_TX_MASK
        elif command[3] == "3":
            read_type = Constants.I2C_READ_CONTINUOUSLY | Constants.I2C_END_TX_MASK
        else:    # the default case stop reading valid request or invalid request
            read_type = Constants.I2C_STOP_READING

        yield from self.core.i2c_read_request(device_address, register, number_of_bytes, read_type,
                                              self.i2c_read_request_callback)
        yield from asyncio.sleep(1)

    @asyncio.coroutine
    def i2c_write_request(self, command):
        """
        This method performs an I2C write at a given I2C address,
        @param command: {"method": "i2c_write_request", "params": [I2C_DEVICE_ADDRESS, [DATA_TO_WRITE]]}
        @return:No return message.
        """
        device_address = int(command[0])
        params = command[1]
        params = [int(i) for i in params]
        yield from self.core.i2c_write_request(device_address, params)

    @asyncio.coroutine
    def play_tone(self, command):
        """
        This method controls a piezo device to play a tone. It is a FirmataPlus feature.
        Tone command is TONE_TONE to play, TONE_NO_TONE to stop playing.
        @param command: {"method": "play_tone", "params": [PIN, TONE_COMMAND, FREQUENCY(Hz), DURATION(MS)]}
        @return:No return message.
        """
        pin = int(command[0])
        if command[1] == "TONE_TONE":
            tone_command = Constants.TONE_TONE
        else:
            tone_command = Constants.TONE_NO_TONE
        frequency = int(command[2])
        duration = int(command[3])
        yield from self.core.play_tone(pin, tone_command, frequency, duration)

    @asyncio.coroutine
    def set_analog_latch(self, command):
        """
        This method sets the an analog latch for a given analog pin, providing the threshold type, and
        latching threshold.
        @param command: {"method": "set_analog_latch", "params": [PIN, THRESHOLD_TYPE, THRESHOLD_VALUE]}
        @return:{"method": "analog_latch_data_reply", "params": [PIN, DATA_VALUE_LATCHED, TIMESTAMP_STRING]}
        """
        pin = int(command[0])
        threshold_type = int(command[1])
        threshold_value = int(command[2])
        yield from self.core.set_analog_latch(pin, threshold_type, threshold_value, self.analog_latch_callback)

    @asyncio.coroutine
    def set_digital_latch(self, command):
        """
        This method sets the a digital latch for a given digital pin, the threshold type, and latching threshold.
        @param command:{"method": "set_digital_latch", "params": [PIN, THRESHOLD (0 or 1)]}
        @return:{"method": digital_latch_data_reply", "params": [PIN, DATA_VALUE_LATCHED, TIMESTAMP_STRING]}
        """
        pin = int(command[0])
        threshold_value = int(command[1])
        yield from self.core.set_digital_latch(pin, threshold_value, self.digital_latch_callback)

    @asyncio.coroutine
    def set_pin_mode(self, command):
        """
        This method sets the pin mode for the selected pin. It handles: Input, Analog(Input) PWM, and OUTPUT. Servo
        is handled by servo_config().
        @param command: {"method": "set_pin_mode", "params": [PIN, MODE]}
        @return:No return message.
        """
        pin = int(command[0])
        mode = int(command[1])
        if mode == Constants.INPUT:
            cb = self.digital_callback
        elif mode == Constants.ANALOG:
            cb = self.analog_callback
        else:
            cb = None

        yield from self.core.set_pin_mode(pin, mode, cb)

    def set_sampling_interval(self, command):
        """
        This method sets the Firmata sampling interval in ms.
        @param command:{"method": "set_sampling_interval", "params": [INTERVAL]}
        @return:No return message.
        """
        sample_interval = int(command[0])
        yield from self.core.set_sampling_interval(sample_interval)

    @asyncio.coroutine
    def sonar_config(self, command):
        """
        This method configures 2 pins to support HC-SR04 Ping devices.
        This is a FirmataPlus feature.
        @param command: {"method": "sonar_config", "params": [TRIGGER_PIN, ECHO_PIN, PING_INTERVAL(default=50),
         MAX_DISTANCE(default= 200 cm]}
        @return:{"method": "sonar_data_reply", "params": [DISTANCE_IN_CM]}
        """
        trigger = int(command[0])
        echo = int(command[1])
        interval = int(command[2])
        max_dist = int(command[3])
        yield from self.core.sonar_config(trigger, echo, self.sonar_callback, interval, max_dist)

    @asyncio.coroutine
    def sonar_read(self, command):
        """
        This method retrieves the last sonar data value that was cached.
        This is a polling method. After sonar config, sonar_data_reply messages will be sent automatically.
        @param command: {"method": "sonar_read", "params": [TRIGGER_PIN]}
        @return:{"method": "sonar_read_reply", "params": [TRIGGER_PIN, DATA_VALUE]}
        """
        pin = int(command[0])
        val = yield from self.core.sonar_data_retrieve(pin)

        reply = json.dumps({"method": "sonar_read_reply", "params": [pin, val]})
        self.sendMessage(reply.encode('utf8'))

    @asyncio.coroutine
    def servo_config(self, command):
        """
        This method configures a pin for servo operation. The servo angle is set by using analog_write().
        @param command: {"method": "servo_config", "params": [PIN, MINIMUM_PULSE(ms), MAXIMUM_PULSE(ms)]}
        @return:No message returned.
        """
        pin = int(command[0])
        min_pulse = int(command[1])
        max_pulse = int(command[2])
        yield from self.core.servo_config(pin, min_pulse, max_pulse)

    @asyncio.coroutine
    def stepper_config(self, command):
        """
        This method configures 4 pins for stepper motor operation.
        This is a FirmataPlus feature.
        @param command: {"method": "stepper_config", "params": [STEPS_PER_REVOLUTION, [PIN1, PIN2, PIN3, PIN4]]}
        @return:No message returned.
        """
        steps_per_revs = int(command[0])
        pins = command[1]
        pin1 = int(pins[0])
        pin2 = int(pins[1])
        pin3 = int(pins[2])
        pin4 = int(pins[3])
        yield from self.core.stepper_config(steps_per_revs, [pin1, pin2, pin3, pin4])

    @asyncio.coroutine
    def stepper_step(self, command):
        """
        This method activates a stepper motor motion.
        This is a FirmataPlus feature.
        @param command: {"method": "stepper_step", "params": [SPEED, NUMBER_OF_STEPS]}
        @return:No message returned.
        """
        speed = int(command[0])
        num_steps = int(command[1])
        yield from self.core.stepper_step(speed, num_steps)

    def onClose(self, was_clean, code, reason):
        """
        Websocket management message.
        This message is received when the client closes the connection. A console status message is printed and
        and the interface is shutdown before exiting.
        @param was_clean: Autobahn provided flag
        @param code:Autobahn provided flag
        @param reason:Autobahn provided flag
        @return:Console message is generated.
        """
        print("WebSocket connection closed: {0}".format(reason))
        yield from self.core.shutdown()

    def onConnect(self, request):
        """
        WebSocket management method.
        This method issues a console status message for Websocket connection establishment.
        @param request: Websocket request
        @return: No return value.
        """
        print("Client connecting: {0}".format(request.peer))

    def onMessage(self, payload, is_binary):
        """
        Websocket management method.
        This method receives JSON messages from the Websocket client. All messages are assumed to be text.
        If a binary message is sent, a console status message is generated.
    
        The JSON command is interpreted and translated to a method call to handle the command request.
        @param payload: JSON command
        @param is_binary: True if message is binary. Assumed to always be False
        @return: No value is returned.
        """
        if is_binary:
            print("Binary message received: {0} bytes".format(len(payload)))
            print('Expected text and not binary')
        else:
            cmd_dict = json.loads(payload.decode('utf8'))
            client_cmd = cmd_dict.get("method")

            if client_cmd in self.command_map:
                cmd = self.command_map.get(client_cmd)
                params = cmd_dict.get("params")
                if params[0] != "null":
                    yield from cmd(params)
                else:
                    yield from cmd()

    def onOpen(self):
        """
        WebSocket management method.
        This method issues a console status message for the opening of a Websocket connection. It sends a Firmata
        reset command to the Arduino.
        @return:  No return value.
        """
        print("WebSocket connection open.")
        yield from self.core.send_reset()

    def analog_callback(self, data):
        """
        This method handles the analog message received from pymata_core
        @param data: analog callback message
        @return:{"method": "analog_message_reply", "params": [PIN, DATA_VALUE}
        """
        reply = json.dumps({"method": "analog_message_reply", "params": [data[0], data[1]]})
        self.sendMessage(reply.encode('utf8'))

    def analog_latch_callback(self, data):
        """
        This method handles analog_latch data received from pymata_core
        @param data: analog latch callback message
        @return:{"method": "analog_latch_data_reply", "params": [ANALOG_PIN, VALUE_AT_TRIGGER, TIME_STAMP_STRING]}
        """
        ts = data[2]
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        reply = json.dumps({"method": "analog_latch_data_reply", "params": [data[0], data[1], st]})
        self.sendMessage(reply.encode('utf8'))

    def digital_callback(self, data):
        """
        This method handles the digital message received from pymata_core
        @param data: digital callback message
        @return:{"method": "digital_message_reply", "params": [PIN, DATA_VALUE]}
        """
        reply = json.dumps({"method": "digital_message_reply", "params": [data[0], data[1]]})
        self.sendMessage(reply.encode('utf8'))
        # yield from self.core.sleep(.001)

    def digital_latch_callback(self, data):
        """
        This method handles the digital latch data message received from pymata_core
        @param data: digital latch callback message
        @return:s{"method": "digital_latch_data_reply", "params": [PIN, DATA_VALUE_AT_TRIGGER, TIME_STAMP_STRING]}
        """
        ts = data[2]
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        reply = json.dumps({"method": "digital_latch_data_reply", "params": [data[0], data[1], st]})
        self.sendMessage(reply.encode('utf8'))

    def encoder_callback(self, data):
        """
        This method handles the encoder data message received from pymata_core
        @param data: encoder data callback message
        @return:{"method": "encoder_data_reply", "params": [ENCODER VALUE]}
        """
        reply = json.dumps({"method": "encoder_data_reply", "params": data})
        self.sendMessage(reply.encode('utf8'))

    def i2c_read_request_callback(self, data):
        """
        This method handles the i2c read data message received from pymata_core.
        @param data: i2c read data callback message
        @return:{"method": "i2c_read_request_reply", "params": [DATA_VALUE]}
        """
        reply = json.dumps({"method": "i2c_read_request_reply", "params": data})
        self.sendMessage(reply.encode('utf8'))

    def i2c_read_data_callback(self, data):
        """
        This method handles the i2c cached read data received from pymata_core.
        @param data: i2c read cached data callback message
        @return:{"method": "i2c_read_data_reply", "params": [DATA_VALUE]}
        """
        reply = json.dumps({"method": "i2c_read_data_reply", "params": data})
        self.sendMessage(reply.encode('utf8'))

    def sonar_callback(self, data):
        """
        This method handles sonar data received from pymata_core.
        @param data: sonar data callback message
        @return:{"method": "sonar_data_reply", "params": [DATA_VALUE]}
        """
        reply = json.dumps({"method": "sonar_data_reply", "params": data})

        self.sendMessage(reply.encode('utf8'))


if __name__ == '__main__':

    # factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    ws_string = 'ws://' + PymataIOT.ip_addr + ':' + PymataIOT.ip_port
    print('Websocket server operating on: ' + ws_string)
    factory = WebSocketServerFactory(ws_string, debug=False)
    factory.protocol = PymataIOT

    loop = asyncio.get_event_loop()
    # coro = loop.create_server(factory, '0.0.0.0', 9000)
    coro = loop.create_server(factory, '0.0.0.0', int(PymataIOT.ip_port))
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()