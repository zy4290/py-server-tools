# py-server-tools

## 前提
在一台服务器上
使用Nginx作为反向代理
两组后端服务，每组后端服务至少两个容器，一主一备

## 目标
实现容器状态监控和重启，升级不中断服务和异常回滚

## 组件
### conf/config.json
全局配置文件，包含Nginx和后端服务的重要配置参数，配置示例如下:
```
{
    "project-name": "test",
    "nginx": {
        "nginx-home": "/usr/local/nginx",
        "nginx-reload-cmd": "nginx -s reload",
        "upstream-conf-path": "/etc/nginx/conf.d/upstream.conf",
        "upstream": {
            "upstream-name": "jetty",
            "keepalive": 1,
            "node-group": {
                "group1": {
                    "nodes": {
                        "jetty1": {
                            "health-check-url": "http://127.0.0.1:8080/",
                            "upstream-url": "127.0.0.1:8080",
                            "start-cmd": "/opt/jettygroup/jetty1/bin/jetty.sh start",
                            "stop-cmd": "/opt/jettygroup/jetty1/bin/jetty.sh stop",
                            "backup": false
                        },
                        "jetty1-backup": {
                            "health-check-url": "http://127.0.0.1:8082/",
                            "upstream-url": "127.0.0.1:8082",
                            "start-cmd": "/opt/jettygroup/jetty1-backup/bin/jetty.sh start",
                            "stop-cmd": "/opt/jettygroup/jetty1-backup/bin/jetty.sh stop",
                            "backup": true
                        }
                    },
                    "default-group": "primary"
                },
                "group2": {
                    "nodes": {
                        "jetty2": {
                            "health-check-url": "http://127.0.0.1:8081/",
                            "upstream-url": "127.0.0.1:8081",
                            "start-cmd": "/opt/jettygroup/jetty2/bin/jetty.sh start",
                            "stop-cmd": "/opt/jettygroup/jetty2/bin/jetty.sh stop",
                            "backup": false
                        },
                        "jetty2-backup": {
                            "health-check-url": "http://127.0.0.1:8083/",
                            "upstream-url": "127.0.0.1:8083",
                            "start-cmd": "/opt/jettygroup/jetty2-backup/bin/jetty.sh start",
                            "stop-cmd": "/opt/jettygroup/jetty2-backup/bin/jetty.sh stop",
                            "backup": true
                        }
                    },
                    "default-group": "standby"
                }
            }
        }
    }
}
```
### runtime
runtime由脚本根据全局配置文件(config.json)和运行时环境生成，包括：
* node-group-status.json
node-group-status.json记录当前后端服务组的状态(primary/standby)和关联服务节点名称，由primary-upstream-switch.py生成和编辑，内容示例如下：
```
{
    "standby": {
        "group-name": "lsip2",
        "nodes": [
            "jetty2-backup",
            "jetty2"
        ]
    },
    "primary": {
        "group-name": "lsip1",
        "nodes": [
            "jetty1-backup",
            "jetty1"
        ]
    }
}
```
* node-health-status.json
node-health-status.json记录服务节点的状态信息('n/a'/running/dead)和健康数据，由nodes-health-check.py生成和编辑，内容示例如下：
```
{
    "jetty1-backup": {
        "status": "dead",
        "health-check-url": "http://127.0.0.1:8082/",
        "last-response-time": 0.01,
        "reboot-count": 0,
        "last-response-code": 502,
        "fail-count": 16,
        "last-check-time": "2016-05-17 14:24:56"
    },
    "jetty2": {
        "status": "dead",
        "health-check-url": "http://127.0.0.1:8081/",
        "last-response-time": 0.0,
        "reboot-count": 0,
        "last-response-code": 502,
        "fail-count": 21,
        "last-check-time": "2016-05-17 14:24:56"
    },
    "jetty2-backup": {
        "status": "dead",
        "health-check-url": "http://127.0.0.1:8083/",
        "last-response-time": 0.0,
        "reboot-count": 0,
        "last-response-code": 502,
        "fail-count": 21,
        "last-check-time": "2016-05-17 14:24:56"
    },
    "jetty1": {
        "status": "dead",
        "health-check-url": "http://127.0.0.1:8080/",
        "last-response-time": 0.0,
        "reboot-count": 0,
        "last-response-code": 502,
        "fail-count": 16,
        "last-check-time": "2016-05-17 14:24:56"
    }
}
```
### python script
* nginx-upstream-edit.py
根据primary组的节点生成Nginx的upstream配置项
* nodes-health-check.py
遍历health-check-url配置，更新节点状态信息与健康信息
* primary-nodes-startup.py
启动primary组服务节点
* standby-nodes-shutdown.py
停止standby组服务节点
* primary-upstream-switch.py
切换node-group-status.json的primary和standby服务节点



