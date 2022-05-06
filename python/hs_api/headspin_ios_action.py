# -*- coding: utf-8 -*-

from hs_api.headspin_action import HeadSpinAction
import time


from hs_api.logger import logger

class HeadSpinIOSAction(HeadSpinAction):

    def __init__(self, testCase, driver):
        super().__init__(testCase, driver)

    def find_element_by_class(self, class_name, handle_exception=True):
        
        super().find_element_by_class(class_name)        

        if handle_exception:
            try:
                el = self.driver.find_element_by_ios_predicate("type == '"+class_name+"'")
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_ios_predicate("type == '"+class_name+"'")
        
    def find_element_by_label(self, label, match=False, handle_exception=True):
        
        super().find_element_by_label(label, match)

        uiStr = ''
        if(match is True):
            uiStr = "label == '"+label+"' or name == '"+label+"'" + "or value == '"+label+"'"
        else:
            uiStr = "label contains '"+label+"' or name contains '"+label+"'" + "or value contains '"+label+"'"
       
        if handle_exception:
            try:
                el = self.driver.find_element_by_ios_predicate(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_ios_predicate(uiStr)
        
    def find_elements_by_class(self, class_name, handle_exception=True):
        
        super().find_elements_by_class(class_name)
                  
        if handle_exception:
            try:
                el = self.driver.find_elements_by_ios_predicate("type == '"+class_name+"'") 
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_elements_by_ios_predicate("type == '"+class_name+"'") 
    
    def find_element_by_description(self, label, match=False, handle_exception=True):
        '''
        find multiple element by description
        '''
        super().find_element_by_description(label, match)

    def find_elements_by_label(self, label, match=False, handle_exception=True):
        
        super().find_elements_by_label(label,match)
        
        uiStr = ''
        if(match is True):
            uiStr = "label == '"+label+"' or name == '"+label+"'" + "or value == '"+label+"'"
        else:
            uiStr = "label contains '"+label+"' or name contains '"+label+"'" + "or value contains '"+label+"'"

        if handle_exception:
            try:
                el = self.driver.find_elements_by_ios_predicate(uiStr)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_elements_by_ios_predicate(uiStr)


    def find_element_by_id(self, id_name, handle_exception=True):
        if handle_exception:
            try:
                el = self.driver.find_element_by_id(id_name)
            except:
                el = None
            finally:
                return el
        else:
            return self.driver.find_element_by_id(id_name)


    def go_backaction(self, back_opt=0):        
        self.driver.back()

    def double_click(self, start_x, start_y):
        '''
        double click 
        '''
        logger.info("double click:"+str(start_x)+" "+str(start_y))
        args = {}
        args["x"] = start_x
        args["y"] = start_y
        self.driver.execute_script("mobile: doubleTap", args)
        return self        
        
        
    
