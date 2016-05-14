#! /usr/bin/env python
import json
import sys
import os

with open('conf/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('runtime/node-group-status.json', 'r') as group_staus_file:
    node_group_status = json.load(group_staus_file)

primary = node_group_status['primary']
primary_group_name = primary['group-name']
primary_nodes_list = primary['nodes']
primary_nodes_info = config['nginx'][
    'upstream']['node-group'][primary_group_name]['nodes']

with open('runtime/node-health-status.json', 'r') as health_staus_file:
    node_health_status = json.load(health_staus_file)

error_nodes_list = []
for node_name in primary_nodes_list:
    if node_health_status[node_name]['status'] == 'dead' or \
            node_health_status[node_name]['status'] == 'n/a':
        error_nodes_list.append(node_name)

# print(error_nodes_list)

for error_node in error_nodes_list:
    os.system(primary_nodes_info[error_node]['stop-cmd'])
    os.system(primary_nodes_info[error_node]['start-cmd'])
