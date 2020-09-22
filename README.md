# py-iss-telemetry
Python library for establishing a telemetry stream with the International Space Station.

This module allows public International Space Station Telemetry 
values to be streamed into a list of dictionaries using Python. 
A websocket is established with NASA's ISSLIVE Lightstreamer server.

DISCLAIMER: The creator of this module is in no way affiliated with
Lightstreamer Srl., NASA or any ISS partners.

## Installation

To install, simply run:
	pip install py-iss-telemetry

	
## Usage

Example:

    import pyisstelemetry

    To create a telemetry stream do

        stream = pyisstelemetry.TelemetryStream()
    
    To get the current telemetry values do

        values = stream.get_tm()
    
    To end the session do

        stream.disconnect()
