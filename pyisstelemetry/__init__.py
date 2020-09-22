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


from . import lightstreamer as ls
import pkg_resources

TM_FILE = pkg_resources.resource_filename('pyisstelemetry', 'tm.list')

class TelemetryStream():
    """
    A class for establishing and handling inbound TM from the International Space
    Station.
    """
    def __init__(self,opcodes=None):
        self.telemetry_history = []
        if opcodes != None:
            self.opcodes = opcodes
        else:
            self.opcodes = self.read_tm_list()
        self.connect_via_lightstream()
        self.subscribe()

    def read_tm_list(self):
        with open(TM_FILE) as f:
            lines = [line.rstrip() for line in f]
        return lines

    def get_tm(self):
        """Returns a list of ISS telemetry."""
        return self.telemetry_history
        
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
        fields=["Value","TimeStamp","Status","Symbol"])
    
    @staticmethod
    def _merge_two_dicts(x, y):
        z = x.copy()
        z.update(y)
        return z

    def on_item_update(self,item_update):
        """Subscription listener"""
        item_metadata = {
            'name':item_update['name'],
            'pos':item_update['pos'],
        }
        entry = self._merge_two_dicts(item_metadata,item_update['values'])
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
