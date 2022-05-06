import os
import json
import argparse
from hs_api.logger import logger
import time
import datetime
from hs_api.hs_api import HSApi


def init_args(self, file_path):
    '''
    Init Args from Command Line Arges
    '''
    args, parser = get_args()
    load_args(self, args)
    if not self.udid or not self.web_driver_url:
        print_help(parser, os.path.basename(file_path))

def get_args():
    '''
    Parser parameter from Command Line
    '''
    parser = argparse.ArgumentParser()
    

    parser.add_argument('--use_network_capture', '--use_network_capture', dest='use_network_capture',
                        action='store_true',
                        default=False,
                        required=False,
                        help='use_network_capture')

    parser.add_argument('--use_local_pbox', '--use_local_pbox', dest='use_local_pbox',
                        action='store_true',
                        default=False,
                        required=False,
                        help='use_local_pbox')

    parser.add_argument('--open_remote_control', '--open_remote_control', dest='open_remote_control',
                        action='store_true',
                        default=False,
                        required=False,
                        help='open_remote_control')

    parser.add_argument('--open_session_url', '--open_session_url', dest='open_session_url',
                        action='store_true',
                        default=False,
                        required=False,
                        help='open_session_url')

    parser.add_argument('--debug', '--debug', dest='debug',
                        action='store_true',
                        default=False,
                        required=False,
                        help='debug')

    # Vars
    parser.add_argument('--udid', '--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="udid")
    ## udid2
    parser.add_argument('--udid2', '--udid2', dest='udid2',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="udid2")
    parser.add_argument('--web_driver_url', '--web_driver_url', dest='web_driver_url',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="web_driver_url")    

    #web url 2
    parser.add_argument('--web_driver_url2', '--web_driver_url2', dest='web_driver_url2',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="web_driver_url2") 
    parser.add_argument('--env', '--env', dest='env',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="env")    

    parser.add_argument('--env_file', '--env_file', dest='env_file',
                        type=str, nargs='?',
                        default=False,
                        required=False,
                        help="env_file")

    parser.add_argument('--user_flow_id', '--user_flow_id', dest='user_flow_id',
                        type=str, nargs='?',
                        default=False,
                        required=False,
                        help="user_flow_id")

    parser.add_argument('--access_token', '--access_token', dest='access_token',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="access_token")

    parser.add_argument('--code_version', '--code_version', dest='code_version',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="code_version")

    parser.add_argument('--working_dir', '--working_dir', dest='working_dir',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="working_dir")
    
    parser.add_argument('--recipient_num', '--recipient_num', dest='recipient_num',
                        type=str, nargs='?',
                        default=None,
                        required=False,
                        help="recipient_num")

    parser.add_argument('--script_retry', '--script_retry', dest='script_retry',
                        action='store_true',
                        default=False,
                        required=False,
                        help='script_retry')

    

    args = parser.parse_args()
    return args, parser


def print_help(parser, file_location):
    '''
    Print Help Message how to use it.
    '''
    example_args_with_env = []
    example_args_with_env.append('--env_file <env_file>')
    logger.info('Example Args with Env: python ' + file_location + ' ' + ' '.join(example_args_with_env))
    parser.print_help()
    example_args = []
    
    example_args.append('--udid <udid>')
    example_args.append('--web_driver_url https://<host:port>/v0/<access_token>/wd/hub')
    logger.info('Example Args: python ' + file_location + ' ' + ' '.join(example_args))
    example_args = []

    example_args.append('--access_token <access_token>')
    example_args.append('--use_network_capture')
    example_args.append('--udid <udid>')
    logger.info('Example Args: python ' + file_location + ' ' + ' '.join(example_args))


    example_args.append('--access_token <access_token>')
    example_args.append('--udid <udid>')
    logger.info('Example Args: python ' + file_location + ' ' + ' '.join(example_args))

    raise Exception('invalid Args')

def load_args(self, args):
    '''
    Set Args to Test
    '''
    self.script_retry = args.script_retry
    self.use_local_pbox = args.use_local_pbox
    self.udid = args.udid
    ##udid 2
    self.udid2 = args.udid2
    self.web_driver_url = args.web_driver_url
    #web url 2
    self.web_driver_url2 = args.web_driver_url2
    self.env = args.env
    if args.use_network_capture:
        self.use_capture = True
        self.video_capture_only = False
    self.open_session_url = args.open_session_url
    self.open_remote_control = args.open_remote_control
    self.access_token = args.access_token
    self.code_version = args.code_version
    self.debug = args.debug
    self.working_dir = args.working_dir
    self.recipient_num = args.recipient_num
    self.send_time = None
    if self.web_driver_url:
        self.access_token = self.web_driver_url.split('/')[-3]
    
    if not self.web_driver_url and self.access_token:
        hs_api = HSApi(self.udid, self.access_token, self.env)
        payload = hs_api.get_automation_config()
        self.web_driver_url = payload['driver_url']
