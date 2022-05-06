import os
import json
import requests
import traceback
import shutil
import time
from bs4 import BeautifulSoup
from hs_api.logger import logger

# Chunk size for streaming file downloads
DEFAULT_CHUNK_SIZE = 16 * 1024  # 16 KB


class HSApi(object):

    # API for getting all devices and its details present in  an org
    #device_list_url = "https://api-dev.headspin.io/v0/devices"
    # device_list_url = "https://api-dev.headspin.io/v0/devices"
    # get_auto_config = "https://api-dev.headspin.io/v0/devices/automation-config"
    # url_root = 'https://api-dev.headspin.io/v0/'
    # API for getting all devices and its details present in  an org

    def __init__(self, UDID, access_token):
        logger.info(UDID)
        logger.info(access_token)
        self.UDID = UDID
        self.access_token = access_token
        self.auth_header = {
            'Authorization': 'Bearer {}'.format(self.access_token)}

        self.url_root = 'https://api-dev.headspin.io/v0/'
        
        if self.UDID:
            self.init_device_details()


    def init_device_details(self):
        # Get the deivce details
        response = requests.get(
            '{}devices'.format(self.url_root),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        self.devices = result['devices']

        is_desired_device = False
        for device in self.devices:
            self.device_os = device['device_type']
            if self.device_os == "android" and device['serial'] == self.UDID:
                is_desired_device = True
            if self.device_os == "ios" and device['device_id'] == self.UDID:
                is_desired_device = True

            if is_desired_device:
                self.device_details = device
                self.device_hostname = device['hostname']
                self.device_address = "{}@{}".format(
                    self.UDID, self.device_hostname)
                self.device_os = device['device_type']
                break
        self.debug = False
        self.default_timeout = 60

    def get_automation_config(self):
        response = requests.get(
            '{}devices/automation-config'.format(self.url_root),
            headers=self.auth_header,
        )
        response.raise_for_status()
        appium_config = response.json()
        payload = {}
        payload['driver_url'] = appium_config[self.device_address]['driver_url'].replace(
            '{api_token}', self.access_token)
        payload['capabilities'] = appium_config[self.device_address]['capabilities']
        return payload

    # Adb devices
    def get_android_device_list(self):
        request_url = '{}devices/{}'.format(self.url_root, self.UDID)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        data = response.json()
        return data

    # List of ios devices
    def get_ios_device_list(self):
        request_url = "{}idevice/{}/installer/list?json".format(
            self.url_root, self.UDID)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        data = response.json()
        return data

    # Install app
    def install_apk(self, filename):
        data = open(filename, 'rb').read()
        request_url = '{}adb/{}/install'.format(
            self.url_root, self.UDID)
        response = requests.post(
            request_url, data=data, headers=self.auth_header, verify=False)
        response.raise_for_status()
        logger.info(response.text)

    # Install app for iOS
    def install_ipa(self, filename):
        data = open(filename, 'rb').read()
        request_url = '{}idevice/{}/installer/install'.format(
            self.url_root, self.UDID)
        response = requests.post(
            request_url, data=data, headers=self.auth_header, verify=False)
        response.raise_for_status()
        logger.info(response.text)

    # uninstall app Androd
    def uninstall_app_android(self, package_name):
        request_url = "{}adb/{}/uninstall?package={}".format(
            self.url_root, self.UDID, package_name)
        response = requests.post(
            url=request_url,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

    # uninstall ios app
    def uninstall_app_ios(self, bundle_id):
        request_url = "{}idevice/{}/installer/uninstall?appid={}".format(
            self.url_root, self.UDID, bundle_id)
        response = requests.post(
            url=request_url,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

    # adb Commands
    def run_adb_command(self, commmand_to_run):
        api_endpoint = "{}adb/{}/shell".format(
            self.url_root, self.UDID)
        response = requests.post(
            url=api_endpoint,
            data=commmand_to_run,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        stdout = result['stdout'].encode('utf-8').strip()
        return stdout

    # Pull file from android device
    def pull_file_android(self, source, destination):
        api_endpoint = "{}adb/{}/pull?remote={}".format(
            self.url_root, self.UDID, source)
        response = requests.get(
            url=api_endpoint,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        with open(destination, 'wb') as f:
            f.write(response.content)

    # Adb screenshot
    def get_adb_screenshot(self, filename):
        api_endpoint = "{}adb/{}/screenshot".format(
            self.url_root, self.UDID)
        response = requests.get(
            url=api_endpoint,
            headers=self.auth_header,
            stream=True,
            verify=False
        )
        response.raise_for_status()
        logger.info("Status code %s", response.status_code)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(DEFAULT_CHUNK_SIZE):
                f.write(chunk)

    # iOS screenshot
    def get_ios_screenshot(self, filename):
        api_endpoint = "{}idevice/{}/screenshot".format(
            self.url_root, self.UDID)
        response = requests.get(
            url=api_endpoint,
            headers=self.auth_header,
            stream=True,
            verify=False
        )
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(DEFAULT_CHUNK_SIZE):
                f.write(chunk)

    # iOS device info
    def get_idevice_info(self):
        request_url = "{}idevice/{}/info?json".format(
            self.url_root, self.UDID)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        data = response.json()
        logger.info(data)
        return data

    # iOS get list of all apps installed
    def get_app_list_ios(self):
        request_url = "{}idevice/{}/installer/list?json".format(
            self.url_root, self.UDID)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        try:
            data = response.json()
            return data
        except Exception:
            logger.exception("Couldnt fetch the app list.")

    # Dismiss pop up ios
    def dismiss_ios_popup(self):
        api_endpoint = "{}idevice/{}/poptap".format(
            self.url_root, self.UDID)
        response = requests.post(
            url=api_endpoint,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        logger.info(result)

    # iOS device restart
    def restart_ios_device(self):
        api_endpoint = "{}idevice/{}/diagnostics/restart".format(
            self.url_root, self.UDID)
        response = requests.post(
            url=api_endpoint,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        logger.info(result)

    # --- Platform APIs --- #
    def start_session_capture(self):
        api_endpoint = "{}sessions".format(self.url_root)
        payload = {
            "session_type": "capture",
            "device_address": self.device_address
        }
        response = requests.post(
            url=api_endpoint,
            data=json.dumps(payload),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        logger.info(result)
        session_id = result['session_id']
        return session_id

    def stop_session_capture(self, session_id):
        api_endpoint = "{}sessions/{}".format(
            self.url_root, session_id)
        payload = {"active": False}
        response = requests.patch(
            url=api_endpoint,
            data=json.dumps(payload),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        logger.info(result)

    def add_session_tags(self, session_id, **kwargs):
        # followed by any number of tags , syntax:<tag_key="tag_value">. eg: type1="test_session",type2="test_session"
        # Function call example:
        # hs_class.add_session_tags("3da744a6-c269-11e9-b708-0641978974b8",type="test_session")

        api_endpoint = "{}sessions/tags/{}".format(
            self.url_root, session_id)
        payload = []
        for key, value in kwargs.items():
            payload.append({str(key), str(value)})
        response = requests.post(
            url=api_endpoint,
            json=payload,
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

    # Add data to existing session
    def add_session_data(self, session_data):
        # Expecting the input dictionary as the argument
        # Sample
        # {"session_id": "<session_id>", "test_name": "<test_name>", "data":[{"key":"bundle_id","value":"com.example.android"}] }
        api_endpoint = "{}perftests/upload".format(self.url_root)
        response = requests.post(
            api_endpoint,
            headers=self.auth_header,
            json=session_data,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)
        return self.parse_response(response)

    # Get Session timestamps
    def get_session_timestamps(self, session_id):
        # Expecting session_id as the argument
        api_endpoint = "{}sessions/{}/timestamps".format(
            self.url_root, session_id)
        response = requests.get(
            api_endpoint, headers=self.auth_header, verify=False)
        response.raise_for_status()
        try:
            data = response.json()
            return data
        except Exception:
            logger.exception("Couldnt get session_timestamps")

    # Add a label to a session
    def add_session_label(self, session_id, label_data):
        # Expecting session_id and label_data dictionary as the argument
        # Sample label_data
        """
        {
            "name": "a helpful name",
            "category": "an optional category for the label",
            "start_time": "10.5",
            "end_time": "1:20.1",
            "data": {"optional": "data"},
            "pinned": true
        }
        ts_start and ts_end is avaliable instead of start_time and end_time as well
        """
        api_endpoint = "{}sessions/{}/label/add".format(
            self.url_root, session_id)
        response = requests.post(
            api_endpoint,
            headers=self.auth_header,
            json=label_data,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

    # Get Label
    def get_session_label(self, label_id):
        request_url = "{}sessions/label/{}".format(
            self.url_root, label_id)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        data = response.json()
        return data

    # Run Visual Page Load
    def run_visual_pageloadtime(self, session_id, payload):
        api_endpoint = "{}sessions/analysis/pageloadtime/{}".format(
            self.url_root, session_id)
        response = requests.post(
            api_endpoint,
            headers=self.auth_header,
            json=payload,
            verify=False
        )
        response.raise_for_status()
        try:
            data = response.json()
            return data
        except Exception:
            logger.exception("Couldnt run_visual_pageloadtime")
    # --- Audio APIs --- #

    def prepare_and_inject(self, audio_id_to_inject):
        # defining the api-endpoint
        prepare_api_endpoint = "{}audio/prepare".format(self.url_root)

        # Prepare
        payload = {
            'hostname': self.device_hostname,
            'audio_ids': [audio_id_to_inject],
        }

        # sending post request for prepare
        response = requests.post(
            url=prepare_api_endpoint,
            data=json.dumps(payload),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

        logger.info("Inject")
        inject_api_endpoint = "{}audio/inject/start".format(self.url_root)
        payload = {
            'device_address': self.device_address,
            'audio_id': audio_id_to_inject
        }
        response = requests.post(
            url=inject_api_endpoint,
            data=json.dumps(payload),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        logger.info(response.text)

    # Capture audio
    def capture_audio(self, duration, tag=None):
        api_endpoint = "{}audio/capture/start".format(self.url_root)
        payload = {
            'device_address': self.device_address,
            'max_duration': str(duration),
            'tag': tag
        }
        response = requests.post(
            url=api_endpoint,
            data=json.dumps(payload),
            headers=self.auth_header,
            verify=False
        )
        response.raise_for_status()
        result = response.json()
        logger.info(result)
        audio_id = result['audio_id']
        logger.info(audio_id)
        return audio_id

    def download_captured_audio(self, audio_id_to_download, file_name):
        download_audio_url = "{}audio/{}/download?channels=mono".format(
            self.url_root, audio_id_to_download)
        output_file_name = "{}.wav".format(file_name)
        logger.info("Downloading")
        response = requests.get(
            url=download_audio_url,
            headers=self.auth_header,
            stream=True,
            verify=False
        )
        response.raise_for_status()
        with open(output_file_name, 'wb') as f:
            for chunk in response.iter_content(DEFAULT_CHUNK_SIZE):
                f.write(chunk)
        logger.info("Downloaded to {}".format(output_file_name))

    def parse_response(self, response, session_id=None, check_error=False):
        '''
        Parse Response Data to object
        '''

        try:
            if response.ok:
                try:
                    return response.json()
                except:
                    return response.text
            else:
                logger.info('status_code: ' + str(response.status_code))
                if check_error:
                    logger.info(traceback.print_exc())
                    raise Exception('Error occurred')
        except:
            logger.info(traceback.print_exc())
            if check_error:
                raise Exception('Error occurred')

    # Sessions
    def get_sessions(self, count=500):
        '''
        Get Session
        '''
        request_url = self.url_root + \
            'sessions?include_all=true&num_sessions=' + str(count)
        if self.debug:
            logger.info('get request_url '+str(request_url))
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_session_tag(self, session_id):
        '''
        Get Session Tag for session_id
        '''
        request_url = self.url_root + 'sessions/tags/' + session_id
        if self.debug:
            logger.info('get request_url '+str(request_url))
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_mar_csv(self, session_id):
        '''
        Get Session CSV
        '''
        request_url = self.url_root + 'sessions/' + session_id + '.csv'
        if self.debug:
            logger.info('get request_url '+request_url)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return response.content

    # Performnce Test
    def get_user_flows(self):
        '''
        Get Session Flows
        '''
        request_url = self.url_root + 'perftests'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        response_payload = self.parse_response(response)
        if response_payload:
            user_flow_list = response_payload['perf_tests']
            return user_flow_list
        else:
            raise Exception('No User Flow Found')

    def sync_replica_db(self, user_flow_id):
        '''
        DB sysnc
        '''
        request_url = self.url_root + 'perftests/' + user_flow_id + '/dbsync'
        response = requests.post(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_user_flow_dbinfo(self, user_flow_id):
        '''
        Get User Flow in dbinfo
        '''
        request_url = self.url_root + 'perftests/' + user_flow_id + '/dbinfo'
        if self.debug:
            logger.info('get request_url '+request_url)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def attach_session_to_user_flow(self, session_id, test_name, status=None):
        '''
        Attach session_id to user flow
        '''
        request_url = self.url_root + 'perftests/upload'
        data_payload = {}
        data_payload['test_name'] = test_name
        data_payload['session_id'] = session_id
        if status:
            data_payload['status'] = status
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_annotations(self, session_id, check_error=False):
        '''
        Get annotations for session_id
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/list'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response, session_id=session_id, check_error=check_error)

    def get_video(self, session_id, working_dir):
        '''
        Get Video for session_id
        '''
        request_url = self.url_root + 'sessions/' + session_id + '.mp4'
        response = requests.get(request_url, stream=True, verify=False)
        response.raise_for_status()
        out_filename = os.path.join(working_dir, session_id + '.mp4')
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        return out_filename

    def get_label(self, label_id):
        '''
        Get Label in for label_id
        '''
        request_url = self.url_root + 'sessions/label/' + label_id
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_label_start_jpeg(self, label_id, working_dir):
        '''
        Get Capture Jpeg for label start label_id save to working_dir
        '''
        out_filename = os.path.join(working_dir, label_id + '_start.jpg')
        request_url = self.url_root + 'sessions/label/' + label_id + '/keyframe/start'
        if self.debug:
            logger.info('request_url '+request_url)
        response = requests.get(request_url, stream=True,
                                headers=self.auth_header, verify=False)
        response.raise_for_status()
        if self.debug:
            logger.info('response.status_code '+str(response.status_code))
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        return out_filename

    def get_label_end_jpeg(self, label_id, working_dir):
        '''
        Get Capture Jpeg for label end label_id save to working_dir
        '''
        out_filename = os.path.join(working_dir, label_id + '_end.jpg')
        if os.path.exists(out_filename):
            if self.debug:
                logger.info(out_filename+' exists')
            return out_filename
        request_url = self.url_root + 'sessions/label/' + label_id + '/keyframe/end'
        if self.debug:
            logger.info('request_url '+request_url)
        response = requests.get(request_url, stream=True,
                                headers=self.auth_header, verify=False)
        response.raise_for_status()
        if self.debug:
            logger.info('response.status_code '+str(response.status_code))
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        return out_filename

    def add_annotation(self, session_id, data_payload):
        '''
        add annotations to session_id
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def add_label(self, session_id, name, category, start_time, end_time, data=None):
        '''
        add annotations to session_id with name, category, start_time, end_time
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        data_payload = {}
        data_payload['name'] = name
        data_payload['category'] = category
        data_payload['start_time'] = str(start_time)
        data_payload['end_time'] = str(end_time)
        data_payload['data'] = data
        data_payload['pinned'] = False
        logger.info("calling add label api")
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        logger.info('add_label response.status_code ' +
                    str(response.status_code))
        response.raise_for_status()
        return self.parse_response(response)
    
    def add_special_label(self, session_id, name, category, type, start_time, end_time, data=None):
        '''
        add labels meant for any headspin functional analysis like, video analysis, page_load change analysis etc
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/label/add'
        data_payload = {}
        data_payload['name'] = name
        data_payload['category'] = category
        data_payload['label_type'] = type
        data_payload['start_time'] = str(start_time)
        data_payload['end_time'] = str(end_time)
        data_payload['data'] = data
        data_payload['pinned'] = False
        print(data_payload)
        logger.info("calling add label api")
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        logger.info('add_special label response.status_code ' +
                    str(response.status_code))
        response.raise_for_status()
        return self.parse_response(response)

    def get_session_and_and_description(self, session_id):
        '''
        Get session description for session_id
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/description'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def update_session_name_and_description(self, session_id, name, description):
        '''
        Update session_name and description
        '''
        request_url = self.url_root + 'sessions/' + session_id + '/description'
        data_payload = {}
        data_payload['name'] = name
        data_payload['description'] = description

        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def copy_annotation(self, session_id, label_id, match_score_threshold=None):
        '''
        copy to session_id, label_id
        '''
        request_url = self.url_root + 'sessions/' + \
            session_id + '/label/' + label_id + '/copy'

        response = None
        if match_score_threshold:
            data_payload = {}
            data_payload['match_score_threshold'] = match_score_threshold

            response = requests.post(
                request_url, headers=self.auth_header, json=data_payload, verify=False)
        else:
            response = requests.post(
                request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def delete_annotation(self, label_id):
        request_url = self.url_root + 'sessions/label/' + label_id
        response = requests.delete(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_devices(self):
        request_url = self.url_root + 'devices'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_hostname(self):
        devices = self.get_devices()
        for device in devices['devices']:
            if device['device_type'] == 'android':
                if self.UDID == str(device['serial']):
                    return device['hostname']
            else:
                if self.UDID == str(device['device_id']):
                    return device['hostname']

    def get_os_type(self):
        devices = self.get_devices()

        for device in devices['devices']:
            if device['device_type'] == 'android':
                if self.UDID == str(device['serial']):
                    return "Android"
            else:
                if self.UDID == str(device['device_id']):
                    return "iOS"

    def get_ios_installed_apps(self):
        # https://ui-dev.headspin.io/docs/idevice-api
        request_url = self.url_root + 'idevice/' + self.UDID + '/installer/list?json'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_ios_installed_version(self, bundle_id):

        app_list = self.get_ios_installed_apps()
        try:
            for app in app_list['data']:

                if bundle_id == app['CFBundleIdentifier']:
                    return app['CFBundleVersion']
        except:
            logger.info(traceback.print_exc())

    def run_adb_shell(self, data):

        request_url = self.url_root + 'adb/' + self.UDID + '/shell'

        response = requests.post(
            request_url, headers=self.auth_header, data=data, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_android_installed_apps(self):
        # https://ui-dev.headspin.io/docs/adb-api
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        response = requests.post(
            request_url, headers=self.auth_header, data='pm list packages', verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_android_installed_version(self, app_package):
        # https://stackoverflow.com/questions/11942762/get-application-version-name-using-adb
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        response = requests.post(request_url, headers=self.auth_header,
                                 data='dumpsys package ' + app_package + ' | grep version', verify=False)
        response.raise_for_status()
        result = self.parse_response(response)
        result_list = result['stdout'].split('\n')
        if len(result_list) > 1 and 'versionName=' in result_list[1]:
            return result_list[1].replace(' ', '').replace('versionName=', '')

    def get_android_current_activity(self):
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        response = requests.post(request_url, headers=self.auth_header,
                                 data="dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'", verify=False)
        response.raise_for_status()
        result = self.parse_response(response)
        logger.info(result)
        return result['stdout']

    def get_current_adb_xml(self):
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        dump_response = requests.post(
            request_url, headers=self.auth_header, data='uiautomator dump', verify=False)
        dump_response.raise_for_status()
        dump_result = self.parse_response(dump_response)
        if not dump_result['summary'] == 'ok':
            logger.info('dump_result'+dump_result)
            logger.info('error')
        else:
            logger.info(dump_result)
        get_xml_response = requests.post(
            request_url, headers=self.auth_header, data='cat /sdcard/window_dump.xml', verify=False)
        get_xml_response.raise_for_status()
        get_xml_result = self.parse_response(get_xml_response)
        if not get_xml_result['summary'] == 'ok':
            logger.info('get_xml_result'+get_xml_result)
            logger.info('error')
        else:
            soup = BeautifulSoup(get_xml_result['stdout'], "lxml")
            prettyXML = soup.prettify()
            return prettyXML

    def get_apk_paths(self, apk_name):
        # Get Path
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        dump_response = requests.post(
            request_url, headers=self.auth_header, data='pm path ' + apk_name, verify=False)
        dump_response.raise_for_status()
        dump_result = self.parse_response(dump_response)
        logger.info('pm path ' + apk_name)
        remote_paths = dump_result['stdout']
        path_list = remote_paths.split('\n')
        filepath_list = []
        logger.info('found '+len(path_list)+'files')
        for path in path_list:
            filepath = path.replace('package:', '')
            if filepath:
                logger.info(filepath)
                filepath_list.append(filepath)
        return filepath_list

    def upload_file_to_device(self, remote_path, input_filename):
        request_url = self.url_root + 'adb/' + self.UDID + '/push'
        request_url += '?remote=' + remote_path
        if self.debug:
            logger.info('request_url')
            logger.info(request_url)
        response = requests.post(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()

    def pull_path_from_device(self, remote_path, output_filename):
        # PULL
        request_url = self.url_root + 'adb/' + self.UDID + '/pull'
        request_url += '?remote=' + remote_path
        if self.debug:
            logger.info('request_url')
            logger.info(request_url)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        if self.debug:
            logger.info('pull_path_from_device ' + remote_path)
        with open(output_filename, 'wb') as apk_output:
            apk_output.write(response.content)
        return output_filename

    def pull_apk_from_device(self, apk_name, working_dir):
        remote_paths = self.get_apk_paths(apk_name)
        file_list = []
        for remote_path in remote_paths:
            output_file = os.path.join(
                working_dir, os.path.basename(remote_path) + '.apk')
            output_file = self.pull_path_from_device(remote_path, output_file)
            file_list.append(output_file)
        return file_list

    def instrument_apk(self, input_apk, output_apk, add_other_parameters=False):
        """
            curl -X POST -L https://<access_token>@kddi-api.tysheadspin.test/v0/apps/apk/instrument?instr=NetworkSecurity
                --data-binary @"<input_apk_path>" -o <output_apk_path>
        """
        data = None
        with open(input_apk, 'rb') as apk_file_open:
            data = apk_file_open.read()
        request_url = self.url_root + 'apps/apk/instrument?instr=NetworkSecurity'
        if add_other_parameters:
            request_url += '&instr=OkHttp3CertPinner'
            request_url += '&instr=CertificateExceptionCheck'
            request_url += '&instr=HardwareAccelerated'
        logger.info(request_url)
        response = requests.post(
            request_url, headers=self.auth_header, data=data, verify=False)
        response.raise_for_status()
        with open(output_apk, 'wb') as apk_output:
            apk_output.write(response.content)
        return output_apk

    def get_all_process(self):
        # Get Path
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        dump_response = requests.post(
            request_url, headers=self.auth_header, data='ps -A', verify=False)
        dump_response.raise_for_status()
        dump_result = self.parse_response(dump_response)

        all_process_response = dump_result['stdout']
        all_process_response_list = all_process_response.split('\n')
        first_row = all_process_response_list[0]
        cols_with_spaces = first_row.split(' ')
        header_cols = []
        for col in cols_with_spaces:
            if col:
                header_cols.append(col)
        logger.info(header_cols)
        rows = []
        for process_string in all_process_response_list[1:]:

            cols_with_spaces = process_string.split(' ')
            cols = []
            for col in cols_with_spaces:
                if col:
                    cols.append(col)
            row_info = {}
            # skipping cases when the process has a space
            if not len(cols) == len(header_cols):
                continue
            for col_index in range(len(cols)):

                row_info[header_cols[col_index]] = cols[col_index]
            if '.' not in row_info['NAME']:
                continue
            rows.append(row_info)

        return rows

    def get_device_automation_config(self):
        request_url = self.url_root + 'devices/automation-config'
        if self.debug:
            logger.info(request_url)
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def get_pageloadtime(self, session_id, name, start_time, end_time, start_sensitivity=None, end_sensitivity=None):
        request_url = self.url_root + 'sessions/analysis/pageloadtime/'+session_id
        data_payload = {}
        region_times = []
        start_end = {}
        start_end['start_time'] = str(start_time/1000)
        start_end['end_time'] = str(end_time/1000)
        start_end['name'] = name
        region_times.append(start_end)
        data_payload['regions'] = region_times
        if(start_sensitivity is not None):
            data_payload['start_sensitivity'] = start_sensitivity
        if(end_sensitivity is not None):
            data_payload['end_sensitivity'] = end_sensitivity

        logger.info("get_pageloadtime")
        logger.info(data_payload)
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        response.raise_for_status()
        logger.info('get_pageloadtime status  '+str(response.status_code))
        results = self.parse_response(response)
        return results

    def get_capture_timestamp(self, session_id):
        request_url = self.url_root + 'sessions/' + session_id+'/timestamps'
        response = requests.get(
            request_url, headers=self.auth_header, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def create_screenfreezing_tag(self, session_id):
        request_url = self.url_root+'sessions/tags/'+session_id
        data_payload = []
        tags = {}
        tags['analysis'] = 'screenfreezing'
        data_payload.append(tags)
        response = requests.post(request_url, headers=self.auth_header,
                                 json=data_payload, timeout=self.default_timeout, verify=False)
        response.raise_for_status()
        return response.ok

    def get_screen_freezing_issues(self, session_id, start_time, end_time):
        request_url = self.url_root + 'sessions/analysis/screenfreezing'

        data_payload = {}
        data_payload['session_id'] = session_id
        region_times = []

        start_end = {}
        start_end['start_time'] = start_time
        start_end['end_time'] = end_time
        region_times.append(start_end)
        data_payload['regions'] = region_times
        response = requests.post(
            request_url, headers=self.auth_header, json=data_payload, verify=False)
        response.raise_for_status()
        return self.parse_response(response)

    def add_custome_measurements(self, session_id, measurements_data):

        request_url = self.url_root + 'perftests/upload'

        data_payload = {}
        data_payload['session_id'] = session_id
        datas = []

        for key, value in measurements_data.items():
            data_item = {}
            data_item['key'] = key
            data_item['value'] = value
            datas.append(data_item)

        data_payload['data'] = datas
        response = requests.post(request_url, headers=self.auth_header,
                                 json=data_payload, timeout=self.default_timeout, verify=False)
        response.raise_for_status()
        return response.ok

    def get_pcap(self, session_id, working_dir):
        '''
        Get PCAP for session_id
        '''
        logger.info(session_id)
        logger.info(working_dir)
        out_filename = os.path.join(working_dir, session_id + '.pcap')
        logger.info(out_filename)
        if os.path.isfile(out_filename):
            return out_filename
        request_url = self.url_root + 'sessions/' + session_id + '.pcap'
        response = requests.get(request_url, stream=True, verify=False)
        response.raise_for_status()
        logger.info("Downloading pcap file...")
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        logger.info("Downloaded pcap file")
        return out_filename

    def get_sslkeylog(self, session_id, working_dir):
        '''
        Get SSL Key Log for session_id
        '''
        out_filename = os.path.join(working_dir, session_id + '.sslkeylog.txt')
        if os.path.isfile(out_filename):
            return out_filename

        logger.info("Downloading SSL Key Log...")
        request_url = self.url_root + 'sessions/' + session_id + '.sslkeylog.txt'
        response = requests.get(request_url, stream=True, verify=False)
        response.raise_for_status()
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        logger.info("Downloaded SSL Key Log")
        return out_filename

    def get_har(self, session_id, working_dir):
        '''
        Get har for session_id
        '''

        out_filename = os.path.join(working_dir, session_id + '.har')
        if os.path.isfile(out_filename):
            return out_filename
        request_url = self.url_root + 'sessions/' + session_id + '.har'
        response = requests.get(request_url, stream=True, verify=False)
        response.raise_for_status()
        logger.info("Downloading har file...")
        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        logger.info("Downloaded har file")
        return out_filename

    def get_har_file(self, session_id, working_dir):
        '''
        Get session har file for network analysis 
        '''
        out_filename = os.path.join(working_dir, session_id + '.har')
        if os.path.isfile(out_filename):
            return out_filename

        request_url = self.url_root + 'sessions/' + session_id + '.har'
        response = requests.get(request_url, stream=True, verify=False)
        response.raise_for_status()

        with open(out_filename, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        return out_filename

    # Save Datas list to replica to session_id and test_name with json
    def save_perform_data(self, session_id, test_name, data, key_name):

        logger.info("Saving Perform Data...")

        perform_datas = {}
        perform_datas['session_id'] = session_id
        perform_datas['test_name'] = test_name
        perform_data = []
        perform_data.append({
            'key': key_name,
            'value': data
        })

        perform_datas['data'] = perform_data
        try:
            self.add_session_data(perform_datas)
            logger.info("Saved Perform Data")

        except Exception as e:
            logger.error('Failed : ' + str(e))

    def db_sync_test(self, test_name):
        try:
            user_flows = self.get_user_flows()
            for user_flow in user_flows:
                if(user_flow['name'] == test_name):
                    sync_result = self.sync_replica_db(
                        user_flow['perf_test_id'])
                    logger.info(sync_result)
                    logger.info("DB Sync Success")
                    return

        except Exception as e:
            logger.error('Failed : ' + str(e))

    def get_all_running_app(self):
        request_url = self.url_root + 'adb/' + self.UDID + '/shell'
        response = requests.post(
            request_url, headers=self.auth_header, data="ps | grep apps | awk '{print $9}'", verify=False)
        response.raise_for_status()
        return self.parse_response(response)
