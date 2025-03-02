"""py-iss-telemetry

This module allows public International Space Station Telemetry 
values to be streamed into a list of dictionaries using Python. 
A websocket is established with NASA's ISSLIVE Lightstreamer server.

DISCLAIMER: The creator of this module is in no way affiliated with
Lightstreamer Srl., NASA or any ISS partners.

Example:
    To create a telemetry stream do

        stream = pyisstelemetry.TelemetryStream()
    
    To get the current telemetry values do

        values = stream.get_tm()
    
    To end the session do

        stream.disconnect()

"""

__author__ = "Ben Appleby"
__email__ = "ben.appleby@sky.com"
__copyright__ = "Copyright 2020, Ben Appleby"
__credits__ = ["Ben Appleby", "Lightstreamer Srl."]

__version__ = "1.0.0"
__status__ = "Stable"

#Copyright 2020 Benjamin Appleby <ben.appleby@sky.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import math
import copy
import json
import os.path
from . import lightstreamer as ls

MODULES_DICT_PATH = os.path.join(os.path.dirname(__file__), 'module_dictionary.json')

with open(MODULES_DICT_PATH, "r") as modules_dict:
    MODULES_DICT = json.load(modules_dict)

class TelemetryStream():
    """
    A class for establishing and handling inbound TM from the International Space
    Station.
    """
    def __init__(self, opcodes=None):
        self.telemetry_lock = False
        self.telemetry_history = []
        self.telemetry_cache = []
        self.QTRN = {
          "0": None,
          "1": None,
          "2": None,
          "3": None
        }
        if opcodes != None:
            self.opcodes = opcodes
        else:
            self.opcodes = self.read_modules_dicts()
        self.connect_via_lightstream()
        self.subscribe()

    def read_modules_dicts(self):
        opcodes_list = [module["Public_PUI"] for module in MODULES_DICT]
        return opcodes_list

    def get_tm(self):
        """Returns a list of ISS telemetry."""
        return self.telemetry_history

    def reset_tm(self):
        self.telemetry_lock = True
        self.telemetry_history = []
        self.telemetry_lock = False

    def dump_tm(self):
        self.telemetry_lock = True
        dumped_data = self.telemetry_history.copy()
        self.telemetry_history = []
        self.telemetry_lock = False
        return dumped_data

    def connect_via_lightstream(self):
        """Creates a connection to ISSLIVE via lighstream."""
        print("Starting connection")
        self.lightstreamer_client = ls.LSClient("http://push.lightstreamer.com", "ISSLIVE")
        try:
            self.lightstreamer_client.connect()
        except Exception as e:
            print("Unable to connect to Lightstreamer Server")
            print(e)
        return self.lightstreamer_client

    def make_lightstream_subscription(self):
        """Creates a subscription to inbound TM from lightstream."""
        print("Creating subscription")
        return ls.Subscription(
        mode="MERGE",
        items=self.opcodes,
        fields=["TimeStamp", "Value", "Status.Class", "Status.Indicator", "Status.Color", "CalibratedData"])
        #fields=["Value","TimeStamp","Status","Symbol"])

    @staticmethod
    def calculate_attitude(Q0, Q1, Q2, Q3):    
        # Initialize attitude angles
        yaw = 0.0
        pitch = 0.0
        roll = 0.0

        # Calculate intermediate values
        c12 = 2 * (Q1 * Q2 + Q0 * Q3)
        c11 = Q0 * Q0 + Q1 * Q1 - Q2 * Q2 - Q3 * Q3
        c13 = 2 * (Q1 * Q3 - Q0 * Q2)
        c23 = 2 * (Q2 * Q3 + Q0 * Q1)
        c33 = Q0 * Q0 - Q1 * Q1 - Q2 * Q2 + Q3 * Q3
        c22 = Q0 * Q0 - Q1 * Q1 + Q2 * Q2 - Q3 * Q3
        c21 = 2 * (Q1 * Q2 - Q0 * Q3)
        mag_c13 = abs(c13)  # All c's should be in radians

        # Calculate yaw, pitch, and roll based on magnitude of c13
        if mag_c13 < 1:
            yaw = math.atan2(c12, c11)
            pitch = math.atan2(-c13, math.sqrt(1.0 - (c13 * c13)))
            roll = math.atan2(c23, c33)
        elif mag_c13 == 1:
            yaw = math.atan2(-c21, c22)
            pitch = math.asin(-c13)
            roll = 0.0

        # Convert angles to degrees
        yaw = yaw * 180 / math.pi
        pitch = pitch * 180 / math.pi
        roll = roll * 180 / math.pi

        return yaw, pitch, roll

    @staticmethod
    def _merge_two_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    def on_item_update(self, item_update):
        """Subscription listener"""
        item = {
            'name': item_update['name'],
            'pos': item_update['pos'],
            'values': item_update['values']
        }

        if item['name'] == 'USLAB000018':
            self.QTRN['0'] = float(item['values']['Value'])
        elif item['name'] == 'USLAB000019':
            self.QTRN['1'] = float(item['values']['Value'])
        elif item['name'] == 'USLAB000020':
            self.QTRN['2'] = float(item['values']['Value'])
        elif item['name'] == 'USLAB000021':
            self.QTRN['3'] = float(item['values']['Value'])

        matching_metadata = next((metadata for metadata in MODULES_DICT if metadata["Public_PUI"] == item['name']), None)
    
        if matching_metadata:
            item_metadata = self._merge_two_dicts(item, matching_metadata)
        else:
            # If no matching metadata, create a new metadata with keys set to None
            default_metadata = {key: None for key in MODULES_DICT[0].keys()}
            item_metadata = self._merge_two_dicts(item, default_metadata)

        self.add_telemetry_history(item_metadata, item['values'])

        # Calculate yaw, pitch, and roll values if all quaternion values are present
        if all(q is not None for q in self.QTRN.values()):
            Q0, Q1, Q2, Q3 = self.QTRN['0'], self.QTRN['1'], self.QTRN['2'], self.QTRN['3']

            yaw_value, pitch_value, roll_value = self.calculate_attitude(Q0, Q1, Q2, Q3)

            ypr_values = {
                'USLAB000YAW': yaw_value,
                'USLAB000PIT': pitch_value,
                'USLAB000ROL': roll_value,
            }

            # Generate item updates for yaw, pitch, and roll
            # Use _merge_two_dicts to update 'Value' while keeping other values
            for item_name, new_value in ypr_values.items():
                if new_value is not None:
                    item['name'] = item_name
                    item['values']['Value'] = new_value
                    matching_metadata = next((metadata for metadata in MODULES_DICT if metadata["Public_PUI"] == item['name']), None)
                    item_metadata = self._merge_two_dicts(item, matching_metadata)
                    self.add_telemetry_history(item_metadata, item['values'])
    
            # Reset quaternion values
            for key in self.QTRN:
                self.QTRN[key] = None

    def add_telemetry_history(self, metadata, update):
        entry = self._merge_two_dicts(metadata, update)
        if self.telemetry_lock:
            self.telemetry_cache.append(entry)
        else:
            if self.telemetry_cache:
                self.telemetry_history = copy.deepcopy(self.telemetry_cache)
                self.telemetry_cache = []
            self.telemetry_history.append(entry)

    def addlistener(self,subscription):
        """Adds a listener to the lightstream."""
        subscription.addlistener(self.on_item_update)
        print("Listening to ISS Telemetry...")

    def subscribe(self):
        """Abstracted subscribe function."""
        self.subscription=self.make_lightstream_subscription()
        self.addlistener(self.subscription)
        self.subkey=self.lightstreamer_client.subscribe(self.subscription)

    def unsubscribe(self):
        """Unsubscribe from lightstream."""
        self.lightstreamer_client.unsubscribe(self.sub_key)

    def disconnect(self):
        """Disconnect from lightstream."""
        self.lightstreamer_client.disconnect()
        print("Stream Disconnected")
