import sys

def failure_retry(self):
    if self.script_retry:
        print("working on failure handling")
        print (("https://ui-dev.headspin.io/sessions/" +str(self.session_id)+"/waterfall"))
        sys.exit(1)
