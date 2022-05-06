# -*- coding: utf-8 -*-

from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
import time
from hs_api.logger import logger
import hs_api.kpi_names


class HeadSpinAction:
    '''
    Super Class of HeadspinAndroidAction and HeadspinIOSAction
    Define interface
    '''
    def __init__(self, testCase, driver):
        self.testCase = testCase
        self.driver = driver
        try:
            if not self.testCase.use_browser.lower() == "chrome":
                self.get_screen_size()
        except:
            self.get_screen_size()
        
    def find_element_by_class(self, class_name, handle_exception=True):
        '''
        Find first element by class
        '''
        logger.info("find_element_by_class: "+str(class_name))      

    def find_element_by_id(self, id_name, handle_exception=True):
        '''
        Find first element by class
        '''
        logger.info("find_element_by_id: "+str(id_name))          

    def find_element_by_label(self, label, match=False, handle_exception=True):
        '''
        Find element by label
        if match is true, the label is exactly same as label
        if match is false, the label contain the label
        '''
        logger.info("find_element_by_label: "+str(label)+" "+str(match))
    
    def find_elements_by_class(self, class_name, handle_exception=True):
        '''
        Find multiple elements by class 
        '''
        logger.info("find_elements_by_class: "+str(class_name))
        
    def find_elements_by_label(self, label, match=False, handle_exception=True):
        '''
        find multiple elements by label
        '''
        logger.info("find_elements_by_label: "+str(label)+" "+str(match))

    def find_element_by_description(self, label, match=False, handle_exception=True):
        '''
        find multiple element by description
        '''
        logger.info("find_element_by_label: "+str(label)+" "+str(match))

    def click(self, element, match=False, tti_label=None, tti_label_match=False,
        kpi_name=None, delay=False, start_sensitivity=None, end_sensitivity=None, segment_start = None, segment_end = None, element_by='label', find_by='label'):
        
        logger.info("click: ")

        if kpi_name and not tti_label:
            raise Exception('when supplying kpi_name, you need tti_label')
        
        if(element_by == 'label'):
            el = self.find_element_by_label(element, match)
        elif(element_by == 'id'):
            el = self.find_element_by_id(element)
        elif(element_by == 'element'):
            el = element
        elif(element_by == 'description'):
            el = self.find_element_by_description(element)
        else:
            el = None
        
        if(element_by != 'pos' and el is None):
            logger.info("Can't find the specific element")
            return None

        if((tti_label is not None and kpi_name is not None) or delay):
            time.sleep(self.testCase.delta_time)

        start_time = int(round(time.time()*1000))

        if(element_by == 'pos'):
            self.short_click(element['x'], element['y'])
        else:
            el.click()

        if(tti_label is not None and kpi_name is not None):      

            if(find_by == 'label'):
                tti_label_el = self.find_element_by_label(tti_label, tti_label_match)
            elif(find_by == 'id'):
                tti_label_el = self.find_element_by_id(tti_label)            
            elif(find_by == 'description'):
                tti_label_el = self.find_element_by_description(tti_label) 
            elif(find_by == 'time'):
                time.sleep(tti_label)
                tti_label_el = el   
            if(tti_label_el is None):                
                return None
            else:
                self.testCase.kpi_labels[kpi_name] = {}
                self.testCase.kpi_labels[kpi_name]['start'] = start_time
                self.testCase.kpi_labels[kpi_name]['end'] = int(round(time.time() * 1000.0))
                if start_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['start_sensitivity'] = start_sensitivity
                if end_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['end_sensitivity'] = end_sensitivity

                if segment_start is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_start'] = segment_start
                if segment_end is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_end'] = segment_end  
                
        return el

    
    def go_backaction(self, back_opt=0):        
        logger.info("go back action: ")       


    def go_back(self, back_opt=0, tti_label=None, tti_label_match=False, kpi_name=None, delay=False,start_sensitivity=None, end_sensitivity=None, segment_start = None, segment_end = None, find_by='label'):
        
        logger.info("go back ")         

        if((tti_label is not None and kpi_name is not None) or delay):
            time.sleep(self.testCase.delta_time)
        start_time = int(round(time.time()*1000))
        
        self.go_backaction(back_opt)
        if(tti_label is not None and kpi_name is not None):  

            if(find_by == 'label'):
                tti_label_el = self.find_element_by_label(tti_label, tti_label_match)
            elif(find_by == 'id'):
                tti_label_el = self.find_element_by_id(tti_label)            
            elif(find_by == 'description'):
                tti_label_el = self.find_element_by_description(tti_label) 
            elif(find_by == 'time'):
                time.sleep(tti_label)
                tti_label_el = el   
            if(tti_label_el is None):                
                return False
            else:
                self.testCase.kpi_labels[kpi_name] = {}
                self.testCase.kpi_labels[kpi_name]['start'] = start_time
                self.testCase.kpi_labels[kpi_name]['end'] = int(round(time.time() * 1000.0))
                if start_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['start_sensitivity'] = start_sensitivity
                if end_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['end_sensitivity'] = end_sensitivity

                if segment_start is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_start'] = segment_start
                if segment_end is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_end'] = segment_end
           
        return True  
    
    def short_click(self, start_x, start_y):
        '''
        short click
        '''
        logger.info("short click:"+str(start_x)+" "+str(start_y))
        action = TouchAction(self.driver)
        action \
            .press(x=start_x, y=start_y) \
            .wait(ms=100) \
            .release()
        action.perform()
        return self

    def long_click(self, start_x, start_y):
        '''
        long time click
        '''
        logger.info("long click:"+str(start_x)+" "+str(start_y))
        action = TouchAction(self.driver)
        
        action \
            .press(x=start_x, y=start_y) \
            .wait(ms=2000) \
            .release()
        action.perform()
        return self

    def short_short_click(self, start_x, start_y):
        '''
        very short click 
        '''
        logger.info("short click:"+str(start_x)+" "+str(start_y))
        action = TouchAction(self.driver)
        action \
            .press(x=start_x, y=start_y) \
            .release()
        action.perform()
        
    
    def double_click(self, start_x, start_y):
        '''
        double click 
        '''
        logger.info("double click:"+str(start_x)+" "+str(start_y))
        

    def swipe_down(self):
        '''
        swipe to down
        '''
        logger.info("swipe down")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        start_x = width/2
        start_y = height/1.7
        end_x = width/2
        end_y = height/2 
        self.driver.swipe(start_x, start_y, end_x, end_y, duration=200)

    def swipe_down1(self):
        '''
        swipe to down
        '''
        logger.info("swipe down")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        start_x = width/2
        start_y = height-50
        end_x = width/2
        end_y = height/3
        self.driver.swipe(start_x, start_y, end_x, end_y, duration=500)

    def swipe_down_custom(self, start_y_ratio, end_y_ratio):
        '''
        long swipe to down (exit fullscreen on videos)
        
        Keyword arguments:
        start_y_ratio -- ratio of height where to start the swipe
        end_y_ratio -- ratio of height where to end the swipe
        '''
        logger.info("swipe down")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        start_x = width/2
        start_y = start_y_ratio * height
        end_x = width/2
        end_y = end_y_ratio * height
        self.driver.swipe(start_x, start_y, end_x, end_y, duration=500)

    def swipe_up(self):
        '''
        swipe to up
        '''
        logger.info("swipe up")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        start_x = width/2
        start_y = height/1.7
        end_x = width/2
        end_y = height/2
        self.driver.swipe(start_x, end_y, end_x, start_y, duration=200)

    def swipe_left(self):
        '''
        swipe to left
        '''
        logger.info("swipe left")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        
        self.driver.swipe(width-50, height/2, 50, height/2, duration=200)

    def swipe_right(self):
        '''
        swipe to right
        '''
        logger.info("swipe right")
        window_size = self.driver.get_window_size()
        width = window_size["width"]
        height = window_size["height"]
        
        self.driver.swipe(0, height/2, width, height/2, duration=200)

    def hide_key(self):
        '''
        hide keyboard
        '''
        logger.info("hide key")
        self.driver.hide_keyboard()  
        
    def press_key(self, key_value, delay=True):
        '''
        Press key by key_value
        '''
        logger.info("press key "+str(key_value))
        if(delay):
            time.sleep(self.testCase.delta_time)
        self.driver.press_keycode(key_value)


    def get_launch_time(self, label, match=False, start_sensitivity=None, end_sensitivity=None, use_auto_launch=False, segment_start = None, segment_end = None, find_by='label'):
        logger.info("get launch time")
        
        if use_auto_launch:
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['start'] = int(round(time.time() * 1000))
        else:
            
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['start'] = int(round(time.time() * 1000))
            if self.testCase.os == 'iOS' or self.testCase.os == 'tvOS':
                self.driver.execute_script('mobile: terminateApp', {'bundleId': self.testCase.package_name})
                time.sleep(self.testCase.delta_time)
                self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['start'] = int(round(time.time() * 1000))
                self.driver.execute_script('mobile: launchApp', {'bundleId': self.testCase.package_name})
                #
            else:
                self.driver.launch_app()

        if(find_by == 'label'):
            el = self.find_element_by_label(label, match)
        elif(find_by == 'id'):
            el = self.find_element_by_id(label)            
        elif(find_by == 'description'):
            el = self.find_element_by_description(label) 
        
        logger.info('launch app completed')
        # Create buffer for the next action
        self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['end'] = int(round(time.time() * 1000))
        
        if start_sensitivity:
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['start_sensitivity'] = start_sensitivity
        if end_sensitivity:
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['end_sensitivity'] = end_sensitivity
        logger.info(str(segment_start))
        if segment_start is not None:
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['segment_start'] = segment_start
        logger.info(str(segment_end))
        if segment_end is not None:
            self.testCase.kpi_labels[kpi_names.COLD_APP_LAUNCH_TTI]['segment_end'] = segment_end
        return el
    

    def get_warm_launch_time(self, label, match=False):
        '''
        Get warm launch time 
        '''
        logger.info('get warm launch time')
        self.testCase.kpi_labels[kpi_names.WARM_APP_LAUNCH_TTI]['start'] = int(round(time.time() * 1000))
        if self.testCase.os == 'iOS':
            self.driver.execute_script('mobile: launchApp', {'bundleId': 'com.apple.Preferences'})
            self.driver.activate_app(self.package_name)
            
            self.find_tti_element(label, match)
            self.testCase.kpi_labels[kpi_names.WARM_LAUNCH_TIME]['end'] = int(round(time.time() * 1000))
        else:
            self.driver.background_app(-1)
            self.driver.activate_app(self.package_name)
            
            self.testCase.find_tti_element(label, match)
            self.testCase.kpi_labels[kpi_names.WARM_LAUNCH_TIME]['end'] = int(round(time.time() * 1000))
        
        logger.info('warm launch app completed')

    def get_element_rect(self, element):
        logger.info("get element rect")
        rect = {}
        rect['x'] = element.location['x']
        rect['y'] = element.location['y']
        rect['width'] = element.size['width']
        rect['height'] = element.size['height']
        return rect

    def get_screen_size(self):
        # screensize of the device
        screen_size = self.driver.get_window_size()
        self.width = screen_size['width']
        self.height = screen_size['height']
        self.half_width = self.width/2
        self.half_height = self.height/2
        self.top_quarter_height = self.height/4

    def set_new_value(self, element, new_text, match=False, tti_label=None, tti_label_match=False, kpi_name=None,  start_sensitivity=None, end_sensitivity=None, segment_start=None, segment_end=None, element_by='label', find_by='label'):

        logger.info("set new value ")

        if(element_by == 'label'):
            el = self.find_element_by_label(element, match)
        elif(element_by == 'id'):
            el = self.find_element_by_id(element)
        elif(element_by == 'element'):
            el = element
        elif(element_by == 'description'):
            el = self.find_element_by_description(element)
        else:
            el = None

        if(el is None):
            return False
        if kpi_name and not tti_label:
            raise Exception('when supplying kpi_name, you need tti_label')            
                
        start_time = int(round(time.time()*1000))

        #el.click()
        time.sleep(self.testCase.delta_time)


        el.set_value(new_text)

        if(tti_label is not None and kpi_name is not None):
            if(find_by == 'label'):
                tti_label_el = self.find_element_by_label(tti_label, tti_label_match)
            elif(find_by == 'id'):
                tti_label_el = self.find_element_by_id(tti_label)            
            elif(find_by == 'description'):
                tti_label_el = self.find_element_by_description(tti_label) 
            elif(find_by == 'time'):
                time.sleep(tti_label)
                tti_label_el = el   
            if(tti_label_el is None):                
                return False
            else:
                self.testCase.kpi_labels[kpi_name] = {}
                self.testCase.kpi_labels[kpi_name]['start'] = start_time
                self.testCase.kpi_labels[kpi_name]['end'] = int(round(time.time() * 1000.0))
                if start_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['start_sensitivity'] = start_sensitivity
                if end_sensitivity:
                    self.testCase.kpi_labels[kpi_name]['end_sensitivity'] = end_sensitivity

                if segment_start is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_start'] = segment_start
                if segment_end is not None:
                    self.testCase.kpi_labels[kpi_name]['segment_end'] = segment_end
        return True
