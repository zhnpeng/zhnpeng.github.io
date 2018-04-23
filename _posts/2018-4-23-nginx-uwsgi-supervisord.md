---
layout: post
title: nginx-uwsgi-supervisord
tags: nginx,uwsgi,supervisor,supervisord,django
datetime: 2018-4-23 13:58
---

{{ page.title }}
================
因为每次新建Python web project都需要搭建这些东西，也很难记住，所以每次都搜索，索性在这里记录一下，web端使用Django。

# 安装
nginx 使用操作系统包管理器安装，比如:apt-get,yum<br/>
uwsgi和supervisord 使用pip安装就可以

# uwsgi配置与运行

## 配置
配置实例
{% highlight bash %}
[uwsgi]
# ln -s $project /etc/project
chdir           = /etc/megas/web
# uwsgi.py的目录
wsgi-file       = /etc/megas/web/web/wsgi.py
master          = true
# 进程数
workers         = 1
# socket文件位置，和nginx通讯的文件
socket      	= /var/megas/web.sock
# socket文件的权限，需要保证nginx有权限,666不是一个好的用法
chmod-socket    = 666
pidfile         = /var/megas/megas_web.pid
vacuum          = true
{% endhighlight %}

uwsgi.py示例(Django)
{% highlight python %}
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

application = get_wsgi_application()
{% endhighlight %}

## 运行
配置完之后，执行 <code>uwsgi --ini uwsgi.ini</code>运行
如果没有保存，说明配置正确。

# supervisord

## 配置
安装完supervisord之后，调用<code>echo_supervisord_conf > /etc/supervisord.conf</code>
把sample配置文件写到supervisord得默认配置文件/etc/supervisord.conf中
<code>vi /etc/supervisord.conf</code>
文件末尾有
{% highlight bash %}
[include]
files = relative/path/*.ini
{% endhighlight %}
把自己项目的ini include进去,比如<code>files=path/*.ini</code>

supervisord配置示例(path/web.ini)
{% highlight bash %}
[program:web]
command = /usr/bin/uwsgi --ini /etc/megas/web/uwsgi.ini
autostart = true
autorestart = true

redirect_stderr = true
stdout_logfile = /var/log/web.log
stopsignal = QUIT
{% endhighlight %}

## 运行
执行supervisord运行，没有报错，说明配置正确。
执行<code>supervisorctl</code>可以看到进程正在运行。
重启所以进程<code>supervisorctl reload</code>

# nginx
{% highlight bash %}
location / {
    include uwsgi_params;
    uwsgi_pass unix:/var/megas/web.sock;
    uwsgi_read_timeout 2;
}
{% endhighlight %}
配置/的路由的uwsgi_pass到uwsgi进程的sock，注意需要有权限。

# 最后
访问http://host/看有没有问题
