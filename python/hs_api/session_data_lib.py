# -*- coding: utf-8 -*-
import json
import traceback
import hs_api.kpi_names as kpi_names
import re
import datetime
import multiprocessing
from hs_api.hs_api import HSApi
import os
import time
from hs_api.logger import logger
import hs_api.failure_handling  as failure_case


def run_record_session_info(self):
    '''
    Save KPI and Description to session
    '''
    logger.info('run_record_session_info')

    # if self.status != "Pass":
    #     print ("call failure case")
    #     failure_case.failure_retry(self)
        
    sni_datas = {'data': []}
    # # if need run sni analysis
    # if(hasattr(self, "sni_analysis")) and self.status == "Pass":
    #     run_sni_analysis(self, sni_datas)

    run_add_annotation_data(self)
    
    run_add_session_data(self)
    
                #str(self.session_id)+"/waterfall")
    logger.info("https://ui-dev.headspin.io/sessions/" +
                str(self.session_id)+"/waterfall")


def filter_sni_server(server_name, package_name):

    filter_strs = ['ads', 'google', 'report',
                   'analytics', 'img', 'measurement',
                   "fcache.veoh.com"]

    for filter_str in filter_strs:
        if(server_name.find(filter_str) != -1):
            return False

    return True


def run_sni_analysis(self, sni_datas):
    time.sleep(20)
    pcap_file = self.hs_api_call.get_pcap(self.session_id, self.working_dir)
    ssl_file = self.hs_api_call.get_sslkeylog(
        self.session_id, self.working_dir)
    json_file = os.path.join(self.working_dir, self.session_id + '.json')

    tls_datas = get_tls_handshake(json_file, pcap_file, ssl_file)
    '''
    har_file = self.hs_api_call.get_har(self.session_id, self.working_dir)

    filter_entries = filter_contentType_from_har(har_file, self.sni_analysis)

    tls_videos = []
    for tls_data in tls_datas:
        for filter_entry in filter_entries:
            if(tls_data['ip_dst'] == filter_entry['serverIPAddress']):
                tls_videos.append(tls_data)
                break

    if(len(tls_videos) == 0):
        tls_videos = tls_datas
    
    sni_servers = []

    for tls_data in tls_videos:
        if filter_sni_server(tls_data['server_name'], self.package_name):
            sni_servers.append(tls_data)
    '''
    sni_final_servers = get_network_speed(
        self.session_id, self.working_dir,  tls_datas, self.min_down_size)
    logger.info("final servers")
    logger.info(json.dumps(sni_final_servers, indent=2))
    server_field = 'server_name'
    sni_datas['data'].append(
        {"key": 'SNI_SERVERS', "value": ', '.join([sni_server[server_field] for sni_server in sni_final_servers])})
    sni_datas['data'].append(
        {"key": 'Download', "value": ', '.join([f"{sni_server['download_size']:.2f}KB" for sni_server in sni_final_servers])})
    try:
        down_max = max([sni_server['download_speed']
                        for sni_server in sni_final_servers])
    except:
        down_max = 0

    har_file = os.path.join(self.working_dir, self.session_id + '.har')
    ssl_file = os.path.join(self.working_dir, self.session_id + '.sslkeylog.txt')
    json_file = os.path.join(self.working_dir, self.session_id + '.json')
    pcap_file = os.path.join(self.working_dir, self.session_id + '.pcap')
    conv_file = os.path.join(self.working_dir, self.session_id + '.conv.txt')
    print (down_max)
    #exit the script if download speed is 0
    if int(down_max) == 0:
        try:
            os.remove(har_file)
            os.remove(ssl_file)
            os.remove(json_file)
            os.remove(pcap_file)
            os.remove(conv_file)
        except Exception as e:
            print(e)
        failure_case.failure_retry(self)
         
    sni_datas['data'].append(
        {"key": 'Download_speed', "value": f"{down_max:.2f}KBps"})
    
    # Remove the processing files
    try:
        os.remove(har_file)
        os.remove(ssl_file)
        os.remove(json_file)
        os.remove(pcap_file)
        os.remove(conv_file)
    except Exception as e:
        print(e)


def dict_raise_on_duplicates(ordered_pairs):
    """Convert duplicate keys to JSON array."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            if type(d[k]) is list:
                d[k].append(v)
            else:
                d[k] = [d[k], v]
        else:
            d[k] = v
    return d


def get_tls_handshake(json_file, pcap_file, ssl_file):
    logger.info("Processing tls handshake...")
    # convert pcap file to json file
    if not os.path.isfile(json_file):
        command = ' '.join(['tshark', '-2', '-o', 'ssl.keylog_file:"' +
                            ssl_file+'"', '-r', pcap_file, '-R "tls.handshake or ssl.handshake or dns"', '-T json >', json_file])
        logger.info('running: {}'.format(command))
        os.system(command)

    with open(json_file, encoding="ISO-8859-1") as json_file_content:
        pcap_datas = json.load(json_file_content)

    logger.info("pcap convert to json and read it")

    results = []
    for pcap_data in pcap_datas:

        protocol = pcap_data['_source']['layers']['frame']["frame.protocols"]

        if(protocol.find('dns') != -1):
            # dns process
            ip_src = pcap_data['_source']['layers']['ip']['ip.src']
            try:
                dns_answers_count = int(
                    pcap_data['_source']['layers']['dns']['dns.count.answers'])
                if(dns_answers_count > 0):
                    dns_answers = pcap_data['_source']['layers']['dns']['Answers']
                    for key, value in dns_answers.items():
                        if (value['dns.resp.type'] == '1'):
                            ip_dst = value['dns.a']
                            server_name = value['dns.resp.name']
                            if(server_name != '' and ip_dst not in [server['ip_dst'] for server in results]):
                                result = {}
                                result['ip_src'] = ip_src
                                result['ip_dst'] = ip_dst
                                result['server_name'] = server_name
                                result['download_size'] = 0
                                result['download_speed'] = 0
                                result['duration'] = 0
                                print(result)
                                results.append(result)
            except:
                continue
        else:
            ip_src = pcap_data['_source']['layers']['ip']['ip.src']
            ip_dst = pcap_data['_source']['layers']['ip']['ip.dst']

            server_name = ''
            if(protocol.find('ssl') != -1):
                try:
                    handshake = pcap_data['_source']['layers']['ssl']['ssl.record']['ssl.handshake']
                    if("ssl.handshake.type" in handshake.keys()):
                        if(handshake['ssl.handshake.type'] != '1'):
                            continue
                        for key, value in handshake.items():
                            if(key.find('Extension: server_name') != -1):
                                server_name = value['Server Name Indication extension']['ssl.handshake.extensions_server_name']
                                break

                except:
                    continue
            elif(protocol.find('tls') != -1):
                try:
                    handshake = pcap_data['_source']['layers']['tls']['tls.record']['tls.handshake']
                    # print(handshake)
                    if("tls.handshake.type" in handshake.keys()):
                        if(handshake['tls.handshake.type'] != '1'):
                            continue

                        for key, value in handshake.items():
                            if(key.find('Extension: server_name') != -1):
                                server_name = value['Server Name Indication extension']['tls.handshake.extensions_server_name']
                                break
                except:
                    continue
            else:
                continue

            if(server_name != '' and ip_dst not in [server['ip_dst'] for server in results]):
                result = {}
                result['ip_src'] = ip_src
                result['ip_dst'] = ip_dst
                result['server_name'] = server_name
                result['download_size'] = 0
                result['download_speed'] = 0
                result['duration'] = 0

                results.append(result)

    logger.info("Processed tls handshake")

    return results


def get_quic_handshake(json_file, pcap_file, ssl_file):
    logger.info("Processing quic handshake...")
    # convert pcap file to json file
    if not os.path.isfile(json_file):
        command = ' '.join(['tshark', '-2', '-o', 'ssl.keylog_file:"' +
                            ssl_file+'"', '-r', pcap_file, '-R "tls.handshake or ssl.handshake"', '-T json >', json_file])
        logger.info('running: {}'.format(command))
        os.system(command)

    with open(json_file, encoding="ISO-8859-1") as json_file_content:
        pcap_datas = json.load(
            json_file_content, object_pairs_hook=dict_raise_on_duplicates)

    results = []
    for pcap_data in pcap_datas:

        protocol = pcap_data['_source']['layers']['frame']["frame.protocols"]

        if(protocol.find('dns') != -1):
            # dns process
            ip_src = pcap_data['_source']['layers']['ip']['ip.src']
            dns_answers_count = int(
                pcap_data['_source']['layers']['dns']['dns.count.answers'])
            if(dns_answers_count > 0):
                dns_answers = pcap_data['_source']['layers']['dns']['Answers']
                for key, value in dns_answers.items():
                    if (value['dns.resp.type'] == '1'):
                        ip_dst = value['dns.a']
                        server_name = value['dns.resp.name']
                        if(server_name != '' and ip_dst not in [server['ip_dst'] for server in results]):
                            result = {}
                            result['ip_src'] = ip_src
                            result['ip_dst'] = ip_dst
                            result['server_name'] = server_name
                            result['download_size'] = 0
                            result['download_speed'] = 0
                            result['duration'] = 0
                            results.append(result)

        else:
            ip_src = pcap_data['_source']['layers']['ip']['ip.src']
            ip_dst = pcap_data['_source']['layers']['ip']['ip.dst']

            server_name = ''
            if(protocol.find('ssl') != -1):
                handshake = pcap_data['_source']['layers']['ssl']['ssl.record']['ssl.handshake']
                if("ssl.handshake.type" in handshake.keys()):
                    if(handshake['ssl.handshake.type'] != '1'):
                        continue
                    for key, value in handshake.items():
                        if(key.find('Extension: server_name') != -1):
                            server_name = value['Server Name Indication extension']['ssl.handshake.extensions_server_name']
                            break
            elif(protocol.find('tls') != -1):
                try:
                    handshake = pcap_data['_source']['layers']['tls']['tls.record']['tls.handshake']
                    # print(handshake)
                    if("tls.handshake.type" in handshake.keys()):
                        if(handshake['tls.handshake.type'] != '1'):
                            continue

                        for key, value in handshake.items():
                            if(key.find('Extension: server_name') != -1):
                                server_name = value['Server Name Indication extension']['tls.handshake.extensions_server_name']
                                break
                except:
                    pass
            else:
                continue

            if(server_name != '' and ip_dst not in [server['ip_dst'] for server in results]):
                result = {}
                result['ip_src'] = ip_src
                result['ip_dst'] = ip_dst
                result['server_name'] = server_name
                result['download_size'] = 0
                result['download_speed'] = 0
                result['duration'] = 0
                print(result)
                results.append(result)

    logger.info("Processed quic handshake")

    return results


video_mime = ['video/mp2t',
              'video/mp4',
              'application/octet-stream',
              'application/vnd.apple.mpegurl',
              'video/x-flv',
              'application/x-mpegURL',
              'video/3gpp',
              'video/quicktime',
              'video/x-msvideo',
              'video/x-ms-wmv',
              'video/mpeg',
              'video/ogg',
              'video/webm'
              ]


def filter_contentType_from_har(har_file, mime_type):
    logger.info("processing har file filter")
    # logger.info(har_file)

    with open(har_file) as json_file_content:
        har_datas = json.load(json_file_content)

    if(mime_type == 'video'):
        mime_types = video_mime

    # logger.info(json.dumps(mime_types, indent=2))
    filters_entries = []

    for entry in har_datas['log']['entries']:
        if entry['response']['content']['mimeType'] in mime_types:
            filters_entries.append(entry)

    logger.info("processed har file filter")
    # logger.info(json.dumps(filters_entries, indent=2))
    return filters_entries


def get_down_size(size_string):
    down_value = re.split(r'MB|kB|bytes', size_string)
    down_value = int(down_value[0].replace(',', ''))
    if(size_string.find('MB') != -1):
        return down_value*1024
    if(size_string.find('kB') != -1):
        return down_value
    return down_value/1024


def get_network_speed(session_id, working_dir, sni_servers, min_down_size):
    logger.info("get network speed start")
    logger.info(json.dumps(sni_servers, indent=2))
    conv_file = os.path.join(working_dir, session_id + '.conv.txt')
    pcap_file = os.path.join(working_dir, session_id + '.pcap')
    conv_type = '-zconv,ipv4'
    if not os.path.isfile(conv_file):
        command = ' '.join(['tshark',  '-r', pcap_file,
                            '-Q', conv_type, '>', conv_file])
        os.system(command)

    with open(conv_file) as conv_file_content:
        Lines = conv_file_content.readlines()
    for line_nu in range(5, len(Lines)-1):
        conv_info = re.split(r'\s+', Lines[line_nu].strip())

        down_size_str = conv_info[8]
        down_kbytes = get_down_size(down_size_str)
        duration = float(conv_info[10])

        for sni_server in sni_servers:
            logger.info("sni ip: "+sni_server['ip_dst'])
            if (sni_server['ip_dst'] == conv_info[2] or sni_server['ip_dst'] == conv_info[0]):
                sni_server['download_size'] += down_kbytes
                sni_server['duration'] += duration
                sni_server['download_speed'] = sni_server['download_size'] / \
                    sni_server['duration']
    logger.info("get network speed end")
    return [server for server in sni_servers if server['download_size'] > min_down_size]


def run_add_session_data(self):
    '''
    Save KPI Label info to description
    '''
    logger.info("run add session data")

    session_data = get_general_session_data(self)
    
    logger.info('session_data')
    logger.info(session_data)
    try:
        description_string = ""
        for data in session_data['data']:
            description_string += data['key'] + \
                " : " + str(data['value']) + "\n"
            self.hs_api_call.update_session_name_and_description(
                self.session_id, self.test_name, description_string)
    except Exception as e:
        print(e)

    if not self.debug:
        result = self.hs_api_call.add_session_data(session_data)
        logger.info('result')
        logger.info(result)


def get_general_session_data(self):
    '''
    General Session Data, include phone os, phone version ....
    '''
    session_status = None
    if self.status != "Pass":
        session_status = "Failed"
    else:
        session_status = "Passed"

    session_data = {}
    session_data['session_id'] = self.session_id
    session_data['test_name'] = self.test_name
    session_data['status'] = session_status
    session_data['data'] = []
    # app info
    session_data['data'].append(
        {"key": kpi_names.BUNDLE_ID, "value": self.package_name})
    session_data['data'].append({"key": 'status', "value": self.status})

    session_data = add_kpi_data_from_labels(self, session_data)

    if self.app_version:
        session_data['data'].append(
            {"key": kpi_names.APP_VERSIONS, "value": self.app_version})

    if self.code_version:
        session_data['data'].append(
            {"key": kpi_names.CODE_VERSION, "value": self.code_version})
    
    try:
        session_link ={}
        session_link['key'] = "reciever_session_id"
        link = str(self.session_id2)
        session_link['value'] = link
        session_data['data'].append(session_link)

    except:
        pass
    
    #Add the video start and end time to session_data
    for videoplay_label_key in self.videoplay_label.keys():
        start_time = self.videoplay_label[videoplay_label_key]['start']
        end_time = self.videoplay_label[videoplay_label_key]['end']
        if start_time and end_time:
            video_data_start = {}
            video_data_start['key'] = videoplay_label_key + "_start"
            video_data_start['value'] = start_time - self.video_start_timestamp
            session_data['data'].append(video_data_start)
            
            video_data_end = {}
            video_data_end['key'] = videoplay_label_key + "_end"
            video_data_end['value'] = end_time - self.video_start_timestamp
            session_data['data'].append(video_data_end)
            
            
    ##adding start and end time for message sent . For whtsapp and snapchat in optus
    if self.send_time:
        message_sent_kpi = {}
        message_sent_kpi['key'] = "message_sent_time"
        message_sent_kpi['value'] = self.send_time
        session_data['data'].append(message_sent_kpi)
        session_link ={}
        session_link['key'] = "reciever_session_id"
        link = str(self.session_id2)
        session_link['value'] = link
        session_data['data'].append(session_link)
    ######
    logger.info(json.dumps(session_data, indent=2))
    return session_data


def get_video_start_timestamp(self):
    logger.info('get_video_start_timestamp')
    wait_until_capture_complete = True
    if wait_until_capture_complete:
        while True:
            capture_timestamp = self.hs_api_call.get_capture_timestamp(
                self.session_id)
            logger.info(capture_timestamp)
            self.video_start_timestamp = capture_timestamp['capture-started'] * 1000
            if 'capture-complete' in capture_timestamp:
                break
            time.sleep(1)
    else:
        capture_timestamp = self.hs_api_call.get_capture_timestamp(
            self.session_id)
        self.video_start_timestamp = capture_timestamp['capture-started'] * 1000


def run_add_annotation_data(self):
    '''
    Add annotation from kpi_labels
    '''
    logger.info("run add annotation to session")
    get_video_start_timestamp(self)
    if self.env == "optus":
        add_page_load_request_labels(self, self.kpi_labels)
    else:
        add_kpi_labels(self, self.kpi_labels, self.KPI_LABEL_CATEGORY)


def add_kpi_data_from_labels(self, session_data):
    '''
    Merge kpi labels and interval time
    '''
    for label_key in self.kpi_labels.keys():
        if self.kpi_labels[label_key] and 'start' in self.kpi_labels[label_key] and 'end' in self.kpi_labels[label_key]:
            data = {}
            data['key'] = label_key
            start_time = self.kpi_labels[label_key]['start']
            end_time = self.kpi_labels[label_key]['end']
            if start_time and end_time:
                data['value'] = end_time - start_time
                session_data['data'].append(data)
                
                #Add the start and end time to the replica
                kpi_start = {}
                kpi_start['key'] = label_key + "_start"
                kpi_start['value'] = start_time
                session_data['data'].append(kpi_start)
                
                kpi_end = {}
                kpi_end['key'] = label_key + "_end"
                kpi_end['value'] =  end_time
                session_data['data'].append(kpi_end)
                
    return session_data


def get_screenchange_list_divide(self, label_key, label_start_time, label_end_time, start_sensitivity=None, end_sensitivity=None):
    """
        Given a visual page load of the region
        If there are start and end, there is only 1 region in the middle that might have more screen changes.
        If start and end are the same we are done
    """
    screen_change_list = []
    sn = 0
    sn_limit = 10

    segment_time_step = 100
    try:
        segment_time_step = self.segment_time_step
    except AttributeError:
        pass

    for i in range(0, 1):
        pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), label_start_time, label_end_time,
                                                     start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
        logger.info(pageload)
        try:
            if 'error_msg' not in pageload['page_load_regions'][0]:
                break
        except:
            time.sleep(5)

    if 'page_load_regions' in pageload.keys() and 'error_msg' not in pageload['page_load_regions'][0]:
        while True:
            screen_change_list.append(
                pageload['page_load_regions'][0]['start_time'])
            screen_change_list.append(
                pageload['page_load_regions'][0]['end_time'])
            sn += 1
            if sn_limit < sn:
                break
            new_label_start_time = float(
                pageload['page_load_regions'][0]['start_time']) + segment_time_step
            new_label_end_time = float(
                pageload['page_load_regions'][0]['end_time']) - segment_time_step
            if new_label_start_time > new_label_end_time:
                break
            logger.debug('new_label_start_time:' + str(new_label_start_time))
            logger.debug('new_label_end_time:' + str(new_label_end_time))
            pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(
                sn), new_label_start_time, new_label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
            logger.debug(pageload)
            if 'page_load_regions' not in pageload.keys() or 'error_msg' in pageload['page_load_regions'][0]:
                logger.debug(pageload)
                break
    else:
        logger.debug(pageload)

    screen_change_list = sorted(list(set(screen_change_list)))
    logger.info(label_key + str(screen_change_list))
    print(label_key + ' ' + str(screen_change_list))
    return screen_change_list

#Add the label for page load request to be considered for post pocessing of the page load api
def add_page_load_request_labels(self, labels):
    data = None
    logger.info("add_kpi_labels")
    print(labels)
    for label_key in labels.keys():
        label = labels[label_key]
        logger.info(label)
        if 'start' in label.keys() and label['start'] and 'end' in label.keys() and label['end']:
            label_start_time = label['start'] - \
                self.video_start_timestamp - self.delta_time * 1000
            if(label_start_time < 0):
                label_start_time = 0.0
            label_end_time = label['end'] - self.video_start_timestamp
            logger.info("Page load Request " + str(label_key) +
                        " "+str(label_start_time)+" "+str(label_end_time))
            
            if 'start_sensitivity' in label.keys() or 'end_sensitivity' in label.keys():
                data = {}
                if 'start_sensitivity' in label.keys():
                    data['start_sensitivity'] = label['start_sensitivity']
                if 'end_sensitivity' in label.keys():
                    data['end_sensitivity'] = label['end_sensitivity']   
            self.hs_api_call.add_special_label(
                self.session_id, label_key, None ,'page-load-request', (label_start_time)/1000, (label_end_time)/1000, data)

      
        
        

def add_kpi_labels(self, labels, label_category):
    '''
        Find all the screen change using different increments
        From the screen changes, pick the desired region
        1. Make sure we can produce the regions that we want to work with 100%
        2. Pick the regions in the code to be inserted for labels kpi

        If there is segment_start and segment_end, find all the candidate regions, and use segment_start and segment_end to pick
        segment_start
        segment_end
        0 => Pick the first segment from the start
        1 => Pick the second segmenet from the start
        -1 => Pick the last segment from the end
        -2 => Pick the second to last segmene from the end
    '''
    logger.info("add_kpi_labels")
    print(labels)
    for label_key in labels.keys():
        label = labels[label_key]
        logger.info(label)
        if 'start' in label.keys() and label['start'] and 'end' in label.keys() and label['end']:
            label_start_time = label['start'] - \
                self.video_start_timestamp - self.delta_time * 1000
            if(label_start_time < 0):
                label_start_time = 0.0
            label_end_time = label['end'] - self.video_start_timestamp
            logger.info("Add Desired Region " + str(label_key) +
                        " "+str(label_start_time)+" "+str(label_end_time))
            self.hs_api_call.add_label(
                self.session_id, label_key, 'desired region', (label_start_time)/1000, (label_end_time)/1000)

            start_sensitivity = None
            end_sensitivity = None
            if 'start_sensitivity' in label:
                start_sensitivity = label['start_sensitivity']
            if 'end_sensitivity' in label:
                end_sensitivity = label['end_sensitivity']

            new_label_start_time = None
            new_label_end_time = None

            if 'segment_start' in labels[label_key] and 'segment_end' in labels[label_key]:
                # Get candidate screen change list, example [2960, 4360, 8040, 9480, 9960, 11560, 13560, 13800, 17720, 18040]
                screen_change_list = get_screenchange_list_divide(
                    self, label_key, label_start_time, label_end_time, start_sensitivity, end_sensitivity)
                if screen_change_list:
                    new_label_start_time = float(
                        screen_change_list[labels[label_key]['segment_start']])
                    new_label_end_time = float(
                        screen_change_list[labels[label_key]['segment_end']])
            else:
                if label['start'] and label['end']:
                    for i in range(0, 1):
                        pageload = self.hs_api_call.get_pageloadtime(
                            self.session_id, label_key, label_start_time, label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity)
                        logger.info(pageload)
                        try:
                            if 'error_msg' not in pageload['page_load_regions'][0]:
                                break
                        except:
                            time.sleep(5)
                    if 'page_load_regions' in pageload.keys() and 'error_msg' not in pageload['page_load_regions'][0]:
                        new_label_start_time = float(
                            pageload['page_load_regions'][0]['start_time'])
                        new_label_end_time = float(
                            pageload['page_load_regions'][0]['end_time'])
            if new_label_start_time and new_label_end_time:
                self.kpi_labels[label_key]['start'] = new_label_start_time
                self.kpi_labels[label_key]['end'] = new_label_end_time
                self.hs_api_call.add_label(self.session_id, label_key, label_category, (
                    new_label_start_time)/1000, (new_label_end_time)/1000)
        # else:
        #     raise Exception('Label not found for:' + str(label_key) + ' ' + label_category)
