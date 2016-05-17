#! /usr/bin/env python
import socket
import json
import time
import urllib2

# set global timeout
socket.setdefaulttimeout(30)

# read nodes status
try:
    with open('runtime/node-health-status.json', 'r') as health_staus_file:
        node_health_status = json.load(health_staus_file)
        # update health check url
        with open('conf/config.json', 'r') as config_file:
            config = json.load(config_file)
        for group_name, group_info in config['nginx']['upstream'][
                'node-group'].items():
            for node_name in sorted(group_info['nodes'].keys()):
                node_health_status[node_name][
                    'health-check-url'] = group_info['nodes'][node_name][
                    'health-check-url']
except Exception:
    # file not exist, create it
    with open('conf/config.json', 'r') as config_file:
        config = json.load(config_file)
    node_health_status = {}
    for group_name, group_info in config['nginx']['upstream'][
            'node-group'].items():
        for node_name in sorted(group_info['nodes'].keys()):
            node_health_status[node_name] = {
                'health-check-url': group_info['nodes'][node_name][
                    'health-check-url'],
                'status': 'n/a',
                'last-response-code': 'n/a',
                'last-response-time': 0,
                'fail-count': 0,
                'reboot-count': 0,
                'last-check-time': time.strftime('%Y-%m-%d %H:%M:%S')}
    # write into file
    with open('runtime/node-health-status.json', 'w') as new_health_staus_file:
        new_health_staus_file.write(json.dumps(node_health_status, indent=4))

# process according to status
for node_name in node_health_status.keys():
    node = node_health_status[node_name]
    status = node_health_status[node_name]['status']
    url = node_health_status[node_name]['health-check-url']

    response = None
    ret_code = 502
    begin_time = time.time()
    end_time = None
    try:
        response = urllib2.urlopen(url)
    except Exception as e:
        if hasattr(e, 'code'):
            ret_code = e.code
    finally:
        end_time = time.time()
        if response:
            ret_code = response.code
            response.close()

        node['last-response-time'] = round((end_time - begin_time), 3)
        node['last-check-time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        node['last-response-code'] = ret_code

        if ret_code == 200:
            node['status'] = 'running'
            node['fail-count'] = 0
            node['reboot-count'] = 0
        elif node['status'] == 'running' or node['status'] == 'n/a':
            node['status'] = 'error'

        if node['status'] == 'error':
            node['fail-count'] = node['fail-count'] + 1
            if node['fail-count'] == 5:
                node['status'] = 'dead'
        elif node['status'] == 'dead':
            node['fail-count'] = node['fail-count'] + 1

# print(json.dumps(node_health_status, indent=4))
with open('runtime/node-health-status.json', 'w') as new_health_staus_file:
    new_health_staus_file.write(json.dumps(node_health_status, indent=4))
