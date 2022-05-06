import time
from hs_api.logger import logger
from hs_api import HSApi



def manage_network(self):
    self.connection_status = self.hs_api_call.get_connection_type()
    print (self.connection_status)
    
    if self.connection_status:
        if self.connection_type not in self.connection_status :
            print ("attempting to change to wifi")
            if 'WIFI' in self.connection_type:
                self.hs_api_call.run_adb_command("su -c svc wifi enable")
                self.hs_api_call.run_adb_command("su -c svc data disable")
                print("changing to WIFI")
                self.connection_status = "WIFI"
            else:
                self.hs_api_call.run_adb_command("su -c svc wifi disable")
                self.hs_api_call.run_adb_command("su -c svc data enable")
                print("changing to MOBILE")
                self.connection_status = "MOBILE"
            time.sleep (3)
    else:
        if 'WIFI' in self.connection_type:
            self.hs_api_call.run_adb_command("su -c svc wifi enable")
            self.hs_api_call.run_adb_command("su -c svc data disable")
            print("changing to WIFI")
            self.connection_status = "WIFI"
        else:
            self.hs_api_call.run_adb_command("su -c svc wifi disable")
            self.hs_api_call.run_adb_command("su -c svc data enable")
            print("changing to MOBILE")
            self.connection_status = "MOBILE"
        time.sleep (3)
