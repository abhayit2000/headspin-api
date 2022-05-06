# -*- coding: utf-8 -*-

from hs_api.headspin_action import HeadSpinAction
import time

from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from selenium.webdriver.common.action_chains import ActionChains
from hs_api.logger import logger


class HeadSpinAndroidAction(HeadSpinAction):

    def __init__(self, testCase , driver):
        super().__init__(testCase, driver)

    def find_element_by_class(self, class_name, handle_exception=True):
        
        super().find_element_by_class(class_name)        

        uiStr = 'new UiSelector().'       
        uiStr = uiStr+'className'       
        uiStr = uiStr+'("'+class_name+'")'
        if handle_exception:
            try:
                el = self.driver.find_element_by_android_uiautomator(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_android_uiautomator(uiStr) 
    
    def find_element_by_id(self, id_name, handle_exception=True):
        super().find_element_by_id(id_name,handle_exception)
        if handle_exception:
            try:
                el = self.driver.find_element_by_id(id_name)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_id(id_name) 

    def find_element_by_label(self, label, match=False, handle_exception=True):
        
        super().find_element_by_label(label, match)
        uiStr = 'new UiSelector().'
        
        if(match is True):
            uiStr = uiStr+'textMatches'
        else:
            uiStr = uiStr+'textContains'
        
        uiStr = uiStr+'("'+label+'")'

        
        
        if handle_exception:
            try:
                el = self.driver.find_element_by_android_uiautomator(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_android_uiautomator(uiStr)        
        
    def find_element_by_description(self, label, match=False, handle_exception=True):
        super().find_element_by_description(label, match)
        uiStr = 'new UiSelector().'
        
        
        uiStr = uiStr+'description'        
        uiStr = uiStr+'("'+label+'")'

        
        
        if handle_exception:
            try:
                el = self.driver.find_element_by_android_uiautomator(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_android_uiautomator(uiStr)


    def find_elements_by_class(self, class_name, handle_exception=True):
        
        super().find_elements_by_class(class_name)
        uiStr = 'new UiSelector().'       
        uiStr = uiStr+'className'       
        uiStr = uiStr+'("'+class_name+'")'
        if handle_exception:
            try:
                el = self.driver.find_elements_by_android_uiautomator(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_elements_by_android_uiautomator(uiStr)
        

    def find_elements_by_label(self, label, match=False, handle_exception=True):
        
        super().find_elements_by_label(label, match)
        uiStr = 'new UiSelector().'
        
        if(match is True):
            uiStr = uiStr+'textMatches'
        else:
            uiStr = uiStr+'textContains'
        
        uiStr = uiStr+'("'+label+'")'

        if handle_exception:
            try:
                el = self.driver.find_elements_by_android_uiautomator(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_elements_by_android_uiautomator(uiStr)

    def go_backaction(self, back_opt=0):
        self.driver.keyevent(4)
        
    def double_click(self, element):
        '''
        double click 
        '''
        logger.info("double click")
        actions = TouchAction(self.driver)
        rect = self.get_element_rect(element)
        actions.tap(element, x=rect['width']/2, y=rect['height']/2, count=2)    
        actions.perform()
       
    




    
