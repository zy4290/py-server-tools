#! /usr/bin/env python
import json
try:
    with open('runtime/node-group-status.json', 'r') as node_group_status_file:
        node_group_status = json.load(node_group_status_file)
        print(json.dumps(node_group_status))
except Exception as e:
    print(e)
