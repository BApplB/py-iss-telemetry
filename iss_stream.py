import lightstreamer as ls
import tm_list


class TelemetryStream():
    """
    A class for establishing and handling inbound TM from the International Space
    Station.
    """
    def __init__(self,opcodes=tm_list.opcodes):
        self.telemetry_history = []
        self.opcodes = opcodes
        self.connect_via_lightstream()
        self.subscribe()

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
    
    def on_item_update(self,item_update):
        """Subscription listener"""
        self.telemetry_history.append(item_update)

    
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
