#! /usr/bin/env python
import json
import sys
import logging

# load configuration
with open('conf/config.json', 'r') as config_file:
    config = json.load(config_file)

# acquire primary node group
try:
    with open('runtime/node-group-status.json', 'r') as group_staus_file:
        node_group_status = json.load(group_staus_file)
except Exception:
    logging.error('fail to acquire node group status, abort.')
    sys.exit()

primary = node_group_status['primary']

# acquire upstream node status
try:
    with open('runtime/node-health-status.json', 'r') as health_staus_file:
        node_health_status = json.load(health_staus_file)
except Exception:
    logging.error('fail to acquire node group status, abort.')
    sys.exit(-1)

primary_grou_name = primary['group-name']
alive_primary = []
for node in primary['nodes']:
    if node in node_health_status and \
            node_health_status[node]['status'] != 'dead':
        alive_primary.append(node)

if len(alive_primary) == 0:
    logging.error('primary list of nodes alive is empty, abort.')
    sys.exit(-1)

# re-generate upstream content
upstream_config = config['nginx']['upstream']
nodes_config = config['nginx']['upstream'][primary_grou_name]['nodes']
upstream_content = 'upstream ' + \
    upstream_config['upstream-name'] + '\n{\n'
for alive_node in alive_primary:
    upstream_content += '\tserver ' + \
        config['nginx']['upstream'][primary_grou_name][
            'nodes'][alive_node]['upstream-url'] + ';\n'

# keepalive configuration
if 'keepalive' in upstream_config:
    upstream_content += '\n\t' + 'keepalive ' + \
        str(config['nginx']['upstream']['keepalive']) + ';\n}\n\n'
else:
    upstream_content = upstream_content[:-1] + '\n}\n'

# print(upstream_content)
# write to upstream confs
try:
    with open(config['nginx']['upstream-conf-path'], 'w') as upstream_config_file:
        upstream_config_file.write(upstream_content)
except Exception:
    print('fail to open %s, abort.' % config['nginx']['upstream-conf-path'])
    sys.exit(-1)

sys.exit(1)
