#! /usr/bin/env python
import sys

# usage tip
if(len(sys.argv) != 2):
    print("""usage:
    python nginx-access-log-analysis.py [nginx_log_path]""")
    sys.exit()

# stat viriables
line_count = 0
post_req_count = 0
post_req_len = 0
get_req_count = 0
get_req_len = 0
get_304_count = 0
get_304_len = 0
file_access_stat = {}
error_analysis_count = 0

# log file process by lines
with open(sys.argv[1], 'r') as access_log:
    for line in access_log:
        try:
            words = line.split(' ')
            if words[5][1:] == 'POST':
                post_req_count += 1
                post_req_len += int(words[9])
            elif words[5][1:] == 'GET':
                get_req_count += 1
                get_req_len += int(words[9])
                res_ext_name = words[6].split('/')[-1:][0]
                dot_loc = res_ext_name.rfind('.')
                qm_loc = res_ext_name.rfind('?')
                if qm_loc == -1:
                    res_ext_name = res_ext_name[dot_loc:]
                else:
                    res_ext_name = res_ext_name[dot_loc:qm_loc]
                if res_ext_name not in file_access_stat:
                    file_access_stat[res_ext_name] = [1, get_req_len]
                else:
                    file_access_stat[res_ext_name] = [file_access_stat[
                        res_ext_name][0] + 1, file_access_stat[
                        res_ext_name][1] + int(words[9])]
                if words[8] == '304':
                    get_304_count += 1
                    get_304_len += int(words[9])
            line_count += 1
        except Exception:
            error_analysis_count += 1

# stat result output
if(error_analysis_count > 0):
    print("Warning: %d lines analysis failed." % error_analysis_count)
print("-request stat-")
print("total request count: %d" % line_count)
print("POST count: %d" % post_req_count)
print("POST length: %d bytes" % post_req_len)
print("POST average length: %d bytes" % int(post_req_len/post_req_count))
print("GET count: %d" % get_req_count)
print("GET length: %d bytes" % get_req_len)
print("GET average length: %d bytes" % int(get_req_len/get_req_count))
print("GET 304 ratio: %.2f%%" % (get_304_count*100/get_req_count))
#print("GET 304 length: %d bytes" % get_304_len)
print
print("-file stat-")
for k, v in file_access_stat.items():
    if k.find('.') != -1 and v[0] > 10:
        print("file: %5s access count: %5d length: %10.2f KB" %
              (k, v[0], v[1]/8/1024))
