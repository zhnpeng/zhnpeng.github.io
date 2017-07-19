---
layout: post
title: Python线程安全的对象
tags: python,theading,thread-safe
datetime: 2017-7-19 22:43
---

{{ page.title }}
================

### 概述
多线程安全的对象。
threading.local

{% highlight python %}
import threading

# 线程安全
l = threading.local()

def func(*args):
    l.x = args[0]
    # id(l) 所有线程是相等的，是用一个对象。
    print id(l)
    # id(l.x) 这个对象的地址都是不同的。
    print id(l.x)
   
ts = []
for x in xrange(4):
    ts.append(threading.Thread(target=func, args=(x,)))
for t in ts:
    t.join()
{% endhighlight %}
l的地址是一样的，但是l.x的地址是不一样的说明l.__setattr__和__getattr__是特殊的。<br/>
实现类似于
{% highlight python %}
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class Local(object):
    __slots__ = ('__storage__', '__ident_func__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)
        
    def __getattr__(self, name):
        try:
            # 在这里我们返回调用了self.__ident_func__()，也就是当前的唯一ID
            # 来作为__storage__的key
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}
{% endhighlight %}
<p>
get_ident会取得每个线程号，而且线程号都是唯一的，因此sotrage[ident]就实现了线程隔离。
</p>
