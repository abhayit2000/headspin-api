# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import unittest
import traceback
from appium import webdriver
from selenium.webdriver.common.keys import Keys
import threading
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from appium.webdriver.common.touch_action import TouchAction

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#Add libs, root Path
script_path = os.path.dirname(os.path.abspath(__file__))
automation_path = os.path.dirname(os.path.dirname(script_path))
libs_path = os.path.join(automation_path, 'hs_api')
root_path = os.path.dirname(automation_path)


sys.path.append(script_path)
sys.path.append(automation_path)
sys.path.append(libs_path)

from hs_api import session_data_lib, label_categories, kpi_names, args_helper, cap_lib
from hs_api.logger import logger
from hs_api.headspin_ios_action import HeadSpinIOSAction

class YoutubeIOS(unittest.TestCase):
    use_capture = True
    video_capture_only = False # Network capture cause problems
    
    test_name = "Youtube iOS"
    package_name = 'com.google.ios.youtube'
    
    segment_time_step = 300
    default_elemnt_timeout = 30

    use_auto_launch = False
    no_reset = True
    debug = True
    sni_analysis = 'video'
    
    def init_vars(self):
        '''
        Init Test Case 
        '''
        logger.info("Init Vars for test...")
        args_helper.init_args(self, __file__)        
        cap_lib.init_ios_caps(self)
        cap_lib.init_general_timing(self)
        self.desired_caps['bundleId'] = self.package_name
        self.KPI_LABEL_CATEGORY = label_categories.MEDIA_APP_KPI
        self.desired_caps['autoLaunch'] = self.use_auto_launch
        
    def setUp(self):
        '''
        Before Test Start
        '''
        logger.info("")
        logger.info("Setting up the test case...")
        self.init_vars()    
        
        # self.desired_caps['headspin:controlLock'] = True
        self.video_play_duration = 60
        self.driver = webdriver.Remote(self.web_driver_url, self.desired_caps)
        self.session_id = self.driver.session_id
        logger.info(str(self.session_id))
        self.headspin_action = HeadSpinIOSAction(self, self.driver)
        self.kpi_labels = {}
        self.kpi_labels[kpi_names.LAUNCH_TIME_TTI] = {'start': None, 'end': None}
        self.kpi_labels[kpi_names.VIDEO_START_TIME] = {'start': None, 'end': None}
        self.videoplay_label = {}
        self.videoplay_label['video_play'] = {'start': None, 'end': None}

    def get_video_start_time(self,session_id):
        capture_timestamp = self.hs_api_call.get_capture_timestamp(
            session_id)
        video_start_timestamp = capture_timestamp['capture-started'] * 1000
        return video_start_timestamp

    def test_youtube(self):
        '''
        Automation Test.
        '''
        logger.info("Testing case...")
        try:
            self.driver.execute_script('mobile: terminateApp', {'bundleId': self.package_name})
        except:
            pass
        self.driver.implicitly_wait(self.default_elemnt_timeout)
        time.sleep(5)
        logger.info("Launching App")
        self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['start'] = int(round(time.time()*1000))
        self.driver.activate_app(self.package_name)
        self.driver.find_element_by_class_name("XCUIElementTypeCell")
        time.sleep(3)
        self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['end'] = int(round(time.time()*1000))
        self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['segment_start'] = 0
        self.kpi_labels[kpi_names.LAUNCH_TIME_TTI]['segment_end'] = 3

        time.sleep(5)
        search_icon = self.driver.find_element_by_accessibility_id('id.ui.navigation.search.button')
        search_icon.click()
        
        search_box = self.driver.find_element_by_accessibility_id("id.navigation.search.text_field")
        search_box.send_keys("bloomberg live")
        
        search_button = self.driver.find_element_by_name("Search")
        search_button.click()
        
        time.sleep(5)
        video_thumbnail = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeOther' and name BEGINSWITH 'LIVE, Bloomberg Global'")
        self.videoplay_label['video_play']['start'] = int(round(time.time()*1000))
        video_thumbnail.click()
        self.kpi_labels[kpi_names.VIDEO_START_TIME]['start'] = int(round(time.time()*1000))
        self.vid_start = int(round(time.time()*1000))
        time.sleep(1)
        progress = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeOther' and value contains 'hours' or value contains 'seconds'")
        value = progress.get_attribute("value")
        print(value)
        # while True:
        #     try:
        #         progress = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeOther' and value contains '1 seconds'")
        #     except:
        #         break
        # time.sleep(2)
        while True:
            self.driver.implicitly_wait(0.1)
            try:
                progress = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeOther' and value contains 'econds'")
                break
            except:
                progress = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeOther' and value contains 'hours'")
                break
        self.kpi_labels[kpi_names.VIDEO_START_TIME]['end'] = int(round(time.time()*1000))
        self.driver.implicitly_wait(self.default_elemnt_timeout)
        self.vid_end = int(round(time.time()*1000))
        self.kpi_labels[kpi_names.VIDEO_START_TIME]['start_sensitivity'] = 0.99
        self.kpi_labels[kpi_names.VIDEO_START_TIME]['end_sensitivity'] = 0.55
        self.driver.implicitly_wait(25)
        try:
            self.driver.find_element_by_accessibility_id('ad.skip.button').click()
            logger.info("ad skipped")
        except:
            try:
                self.driver.find_element_by_accessibility_id('id.player.scrubber.slider')
            except:
                try:
                    self.driver.find_element_by_accessibility_id('ad.skip.button').click()
                    logger.info("ad skipped")
                except:
                    pass
        
        screen_size = self.driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
                
        time.sleep(self.video_play_duration)
        self.headspin_action.click({'x':(width * 0.502), 'y':(height * 0.188)}, element_by='pos')
        ## Tap on the Video Centre
        
        back_button = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeButton' and name=='id.ui.generic.button'")
        back_button.click()
        
        close_button = self.driver.find_element_by_ios_predicate("type=='XCUIElementTypeButton' and name=='id.player.close.button'")
        close_button.click()
        self.videoplay_label['video_play']['end'] = int(round(time.time()*1000))
        
        home_button = self.driver.find_element_by_accessibility_id('id.ui.pivotbar.FEwhat_to_watch.button')
        home_button.click()
        
        self.status = "Pass"
        
    
    def tearDown(self):
        '''
        End Test 
        '''
        time.sleep(5)
        logger.info("Test case ended")
        try:
            self.driver.close_app("com.google.ios.youtube")
        except:
            pass

        session_start = self.get_video_start_time(self.session_id)
        print("video start :", self.vid_start - session_start,"\n Video start :", self.vid_start - session_start, "\n Video end :",self.vid_end - session_start )
        
        try:
            self.driver.quit()
            logger.info('driver quit')
        except:
            logger.info('session terminated already')

        if self.session_id and self.use_capture:
            session_data_lib.run_record_session_info(self)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(YoutubeIOS)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
    time.sleep(10)
