# Headspin API - Python 

## Requirements 

The Headspin API packaged depends on Python 3 and installation of packages in `requirements.txt`

`pip3 install -r requirements.txt`

## Usage

The main API helpers can be imported as follows:

`from hs_api.hs_api import HSApi`

Then the Headspin API object can be initialized with:

`hs_api_call = HSApi(UDID, API_Token)`

Where the UDID is the unique ID of the device and the API_Token is the user's token from the Headspin UI.


## Example Script

Included are three example scripts:

- `example_basic.py` - To demonstrate the Headspin API object and interacting with it.

- `example_appium_ios.py` and `example_appium_android.py` - To record and automate the Youtube app on iOS and Android with Headspin and Appium.

Note: Youtube needs to be manually installed prior to running the examples.

### Repo Structure

1. Example scripts in root folder 

All the scripts of apps are saved here.

2. hs_api

Python 3 helpers to assist with various Headspin functions

### Command

`python3 example_appium_ios.py --udid [udid] --web_driver_url [web_driver_url] --working_dir [path_to_working_dir]`

### Arguments

Some of the key arguments are:

--udid - The UDID of the target device

--web_driver_url - The full web driver URL taken from Headspin UI

--working_dir - A working directory path which should be created before the script is started. Recommend to create in /tmp/


