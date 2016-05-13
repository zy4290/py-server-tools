#! /usr/bin/env python
import sys

# usage tip
with open('conf/config.json', 'r') as config:
    for line in config:
        print(line)
