from hs_api.hs_api import HSApi
from hs_api.logger import logger
from hs_api import kpi_names, label_categories
import json
import time

def get_default_caps(self):
    '''
    General Capture Settings
    '''
    desired_caps = {}
    desired_caps["platformName"] = self.os
    desired_caps["deviceName"] = self.udid
    desired_caps["udid"] = self.udid
    desired_caps["automationName"] = self.automationName
    if self.no_reset:
        desired_caps['noReset'] = self.no_reset

    desired_caps["newCommandTimeout"] = 30000
    # Make sure we don't lose login
    '''
    desired_caps['autoGrantPermissions'] = True
    desired_caps['disableWindowAnimation']= True
    desired_caps['unlockType'] = "pin"
    desired_caps['unlockKey'] = "1234"

    if self.no_reset:
        desired_caps['noReset'] = self.no_reset
    try:
        desired_caps['autoLaunch'] = self.use_auto_launch
    except:
        logger.info('use auto launch default')
    try:
        if self.use_control_lock:
            desired_caps['headspin:controlLock'] = True
    except:
        logger.debug(traceback.format_exc())
        logger.debug('No control lock')
        
    '''

    if self.video_capture_only and self.use_capture:
        desired_caps['headspin:capture.video'] = True
        desired_caps['headspin:capture.network'] = False
    elif self.use_capture:
        desired_caps['headspin:capture.video'] = True
        desired_caps['headspin:capture.network'] = True

    return desired_caps


def init_android_caps(self):
    '''
    android device Capture Init
    '''
    self.os = "Android"
    self.automationName = "UiAutomator2"
    self.desired_caps = get_default_caps(self)

    if hasattr(self, 'use_browser'):
        self.desired_caps["browserName"] = self.use_browser
        self.desired_caps['headspin:autoDownloadChromedriver'] = True

        #self.desired_caps['headspin:controlLock'] = True
    else:
        self.desired_caps["appPackage"] = self.package_name
        self.desired_caps["appActivity"] = self.activity_name
    logger.info(json.dumps(self.desired_caps, indent=2))


def init_ios_caps(self):
    '''
    iOS device Capture Init
    '''
    self.os = 'iOS'
    self.automationName = 'XCUITest'
    self.desired_caps = get_default_caps(self)

    if hasattr(self, 'use_browser'):
        self.desired_caps["browserName"] = self.use_browser

    else:
        self.desired_caps['bundleId'] = self.package_name
    logger.info(json.dumps(self.desired_caps, indent=2))


def init_tvos_caps(self):
    '''
    tv device Capture Init
    '''
    self.os = 'tvOS'
    self.automationName = 'XCUITest'
    self.desired_caps = {}

    self.desired_caps['bundleId'] = self.package_name
    self.desired_caps["platformName"] = self.os
    self.desired_caps["deviceName"] = "Apple TV"

    self.desired_caps["udid"] = self.udid
    self.desired_caps["automationName"] = self.automationName
    self.desired_caps['headspin:appiumVersion'] = '1.17.0'

    #self.desired_caps['headspin:controlLock'] = True
    if self.video_capture_only and self.use_capture:
        self.desired_caps['headspin:capture.video'] = True
        self.desired_caps['headspin:capture.network'] = False
    elif self.use_capture:
        self.desired_caps['headspin.capture'] = True
    logger.info(json.dumps(self.desired_caps, indent=2))


def init_general_timing(self):
    '''
    Init KPI, Action Labels
    '''
    logger.info("Init general Timing")
    self.reference = int(round(time.time() * 1000))

    # initialising variables
    self.status = "Fail_launch"
    self.pass_count = 0
    self.fail_count = 0
    self.app_version = None

    self.video_play_duration = 300
    # KPI Labels
    self.kpi_labels = {}
    self.kpi_labels[kpi_names.LAUNCH_TIME_TTI] = {}
    self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['start'] = None
    self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['end'] = None
    
    self.videoplay_label = {}
    self.videoplay_label['video_play'] = {}
    self.videoplay_label['video_play']['start'] = None
    self.videoplay_label['video_play']['end'] = None
    
    self.delta_time = 0

    self.sni_analysis_start = None
    self.sni_analysis_end = None

    self.hs_api_call = HSApi(self.udid, self.access_token)
    # Check iOS vs. Android

    if hasattr(self, 'package_name'):
        logger.info("getting app Version")
        if self.os == 'iOS':
            self.app_version = self.hs_api_call.get_ios_installed_version(
                self.package_name)
        elif self.os == 'Android':
            self.app_version = self.hs_api_call.get_android_installed_version(
                self.package_name)
        logger.info(f"App Version:{self.app_version}")
    self.ACTION_LABEL_CATEGORY = label_categories.APPIUM_ACTION_LABEL_CATEGORY
    self.HS_TIMING_CATEGORY = label_categories.HS_TIMING
