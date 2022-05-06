# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import unittest
import traceback
from appium import webdriver
import threading
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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

class YoutubeAndroid(unittest.TestCase):
    use_capture = True
    video_capture_only = False # Network capture cause problems
    
    test_name = "Youtube Android"
    package_name = 'com.google.android.youtube'
    activity_name = "com.google.android.youtube.app.honeycomb.Shell$HomeActivity"
    
    segment_time_step = 300
    default_elemnt_timeout = 30

    use_auto_launch = True
    no_reset = True
    debug = True
    sni_analysis = 'video'
    
    def init_vars(self):
        '''
        Init Test Case 
        '''
        logger.info("Init Vars for test...")
        args_helper.init_args(self, __file__)        
        cap_lib.init_android_caps(self)
        cap_lib.init_general_timing(self)
        self.KPI_LABEL_CATEGORY = label_categories.SHOPPING_LABEL_KPI
        
    def setUp(self):
        '''
        Before Test Start
        '''
        logger.info("")
        logger.info("Setting up the test case...")
        self.init_vars()    
        print(self.desired_caps)
        self.driver = webdriver.Remote(self.web_driver_url, self.desired_caps)
        self.session_id = self.driver.session_id
        logger.info(str(self.session_id))
        self.headspin_action = HeadSpinAndroidAction(self, self.driver)
        self.kpi_labels[kpi_names.VIDEO_PLAY_TTI] = {}
        self.status = "Fail"
        self.video_play_duration=300
        
    def test_youtube(self):
        '''
        Automation Test 
        '''
        logger.info("Testing case...")

        self.driver.implicitly_wait(self.default_elemnt_timeout)

        #self.video_start_time = int(round(time.time()*1000))
        # Click on Video
        #self.headspin_action.click('com.google.android.youtube:id/title', element_by='id')
        
        #search
        search_btn = self.driver.find_element_by_android_uiautomator('new UiSelector().description("Search")')
        search_btn.click()
        
        search_edit = self.driver.find_element_by_id('com.google.android.youtube:id/search_edit_text')
        search_edit.click()
        search_edit.set_value("Naruto")
        self.driver.press_keycode(66)
        
        time.sleep(5)
        try:
            self.driver.find_elements_by_android_uiautomator('new UiSelector().descriptionContains("play video")')[1].click()
        except:
            self.driver.find_elements_by_id('com.google.android.youtube:id/title')[1].click()
        logger.info("Play clicked")
        time.sleep(2)
        try:
            self.driver.find_element_by_id('com.google.android.youtube:id/skip_ad_button_text').click()
        except:
            pass
        
        self.video_start_time = int(round(time.time()*1000))
        self.kpi_labels[kpi_names.VIDEO_PLAY_TTI]['start'] = self.video_start_time
        
        self.driver.find_element_by_id('com.google.android.youtube:id/player_view')
        self.status = "Pass"
        self.kpi_labels[kpi_names.VIDEO_PLAY_TTI]['end']=  int(round(time.time()*1000))
        time.sleep(self.video_play_duration)

            
        self.headspin_action.go_back() # Exit Full_Screen
        self.headspin_action.go_back() # Go back to Home Page
        
        
    def tearDown(self):
        '''
        End Test 
        '''
        time.sleep(5)
        logger.info("Test case ended")
        
        # logger.info(self.driver.page_source)
        
        try:
            self.driver.quit()
            logger.info('driver quit')
        except:
            logger.info('session terminated already')

        if self.session_id and self.use_capture:
            session_data_lib.run_record_session_info(self)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(YoutubeAndroid)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
