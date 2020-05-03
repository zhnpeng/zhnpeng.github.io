---
layout: post
title: uwsgi load balance
tags: [uwsgi, multiple processes, load balance]
datetime: 2019-11-1 8:59
---

{{ page.title }}
================

## 概述

Django web服务在处理高频率的请求时发现，uwsgi起了8进程，数据请求延时严重，并且只有2进程cpu占用超过80%，其他进程很闲。于是使用uwsgitop工具查看请求分发情况，发现请求分发非常集中，导致虽然uwsgi配了8进程，但是实际只有2进程在处理请求，再加上python的GIL，多线程的情况下，同时只有一个线程占用cpu，对于cpu密集型任务，其他线程都在等待，导致请求处理延时，甚至在nginx排队积压，严重影响前端响应时间。

## uwsgi multiple processes not banlanced

首先uwsgi配置如下：
```
[secstats]
socket = 127.0.0.1:23081
pythonpath = .
module = wsgi
processes = 8
threads = 20
enable-threads = true
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)
master = true
close-on-exec = true
lazy-apps=true
pypy-home = /opt/bpc/usr/pypy2
pypy-wsgi = wsgi
```

通过uwsgitop工具（下图），可以看出uwsgi实例多进程模式下，request分配非常集中，多进程空闲
<img src="/assets/img/uwsgitool.png" />

## uwsgi 官方load balance方案fastrouter
uwsgi 官方load balance方案是fastrouter
起一个实例专门做load balance的fasterrouter，然后真正的服务实例subcribe上去
请求过程拓扑是  client <——> nginx <——> fasterrouter <—- (load-balance)——> [secstats1, secstats2]
uwsgi配置如下：
```
[fastrouter]
plugins = fastrouter
master = true
shared-socket = 127.0.0.1:23080
fastrouter-subscription-server = 127.0.0.1:23081
fastrouter = =0
vacuum = true
stats = /tmp/fastrouter.sock
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)

[secstats1]
socket = 127.0.0.1:23082
subscribe2 = server=127.0.0.1:23081,key=domain
subscribe2 = server=127.0.0.1:23081,key=
pythonpath = .
module = wsgi
processes = 4
threads = 20
enable-threads = true
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)
master = true
close-on-exec = true
lazy-apps=true
pypy-home = /opt/bpc/usr/pypy2
pypy-wsgi = wsgi

[secstats2]
socket = 127.0.0.1:23083
subscribe2 = server=127.0.0.1:23081,key=172.16.13.188
subscribe2 = server=127.0.0.1:23081,key=
subscribe2 = server=127.0.0.1:23081,key=127.0.0.1
pythonpath = .
module = wsgi
processes = 4
threads = 20
enable-threads = true
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)
master = true
close-on-exec = true
lazy-apps=true
pypy-home = /opt/bpc/usr/pypy2
pypy-wsgi = wsgi
```
nginx配置:
```
location /secstats/ {
     include        uwsgi_params;
     uwsgi_pass     127.0.0.1:23080;
     uwsgi_read_timeout 1800;
}
```
如上配置，如果需要做load balance，需要配置一个新的实例，然后subscribe2 127.0.0.1:23081，key也需要一致，这样fastrouter在分发请求的时候，就可以在subscribe到同一个key的实例间做load balance。
由于一个uwsgi实例的多进程的请求很不平均，集中在2-3个进程，所以实例进程数配置processes=4就差不多可以了。

## 直接使用nginx load balanec
由于uwsgi也没法在单个实例里做load balance，所以也可以直接使用nginx的load-balance，在多个uwsgi实例间做负载均衡。
拓扑 client <——> nginx <——(load-banlance)——> [secstats1, secstats2]
nginx配置如下：
```
upstream servicegroup {
    secstats 127.0.0.1:23082
    secstats 127.0.0.1:23083
}

Server {
    Location /secstats/ {
        include        uwsgi_params;
        uwsgi_pass     servicegroup;
        uwsgi_read_timeout 1800;
    }
}
```

uwsgi配置如下（不需要配fastrouter）：
```
[server1]
socket = 127.0.0.1:23082
pythonpath = .
module = wsgi
processes = 4
threads = 20
enable-threads = true
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)
master = true
close-on-exec = true
lazy-apps=true
pypy-home = /opt/bpc/usr/pypy2
pypy-wsgi = wsgi


[server2]
socket = 127.0.0.1:23083
pythonpath = .
module = wsgi
processes = 4
threads = 20
enable-threads = true
log-format = %(addr) [%(ltime)] "%(method) %(uri)" %(status) %(size) %(micros)
master = true
close-on-exec = true
lazy-apps=true
pypy-home = /opt/bpc/usr/pypy2
pypy-wsgi = wsgi
```