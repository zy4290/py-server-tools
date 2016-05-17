#! /usr/bin/env python
import json
import sys
import os

with open('conf/config.json', 'r') as config_file:
    config = json.load(config_file)

with open('runtime/node-group-status.json', 'r') as group_staus_file:
    node_group_status = json.load(group_staus_file)

standby = node_group_status['standby']
standby_group_name = standby['group-name']
standby_nodes_list = standby['nodes']
standby_nodes_info = config['nginx'][
    'upstream']['node-group'][standby_group_name]['nodes']

with open('runtime/node-health-status.json', 'r') as health_staus_file:
    node_health_status = json.load(health_staus_file)

print(standby_nodes_list)

for standby_node in standby_nodes_list:
    os.system(standby_nodes_info[standby_node]['stop-cmd'])
