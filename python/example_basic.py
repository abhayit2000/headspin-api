import json
from time import sleep
from hs_api.hs_api import HSApi

API_Token = 'YOUR_API_TOKEN'

UDID = 'YOUR_DEVICE_ID'

hs_api_call = HSApi(UDID, API_Token)

# Get device list
hs_api_call.init_device_details()
print(json.dumps(hs_api_call.devices, indent=4))

# Start session capture
### Ensure phone is engaged by Headspin first ###
session_id = hs_api_call.start_session_capture()

### Perform actions here ###
sleep(10)

# Stop session capture
hs_api_call.stop_session_capture(session_id)

# Add session data
sample_data = {"session_id": session_id, "test_name": "Test", "data":[{"key":"bundle_id","value":"com.example.android"}] }
hs_api_call.add_session_data(session_id)
