#! /usr/bin/env python
import json
import sys

try:
    with open('runtime/node-group-status.json', 'r') as node_group_status_file:
        node_group_status = json.load(node_group_status_file)
except Exception as e:
    with open('conf/config.json') as config_file:
        config = json.load(config_file)
    node_group = config['nginx']['upstream']['node-group']
    node_group_status = {'primary': {}, 'standby': {}}
    for group_name, group_info in node_group.items():
        node_group_status[group_info['default-group']] = {
            'group-name': group_name,
            'nodes': group_info['nodes'].keys()
        }
    with open('runtime/node-group-status.json', 'w') as node_group_status_file:
        node_group_status_file.write(json.dumps(node_group_status, indent=4))
    sys.exit()

switched_node_group_status = {}
switched_node_group_status['primary'], switched_node_group_status[
    'standby'] = node_group_status['standby'], node_group_status['primary']

with open('runtime/node-group-status.json', 'w') as node_group_status_file:
    node_group_status_file.write(
        json.dumps(switched_node_group_status, indent=4))
