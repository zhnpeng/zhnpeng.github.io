---
layout: post
title: metaclass简单应用
tags: python,metaclass,orm,simple
datetime: 2017-6-27 22:38
---

{{ page.title }}
================

### 概述
metaclass在很多语言里都有，能够动态改变类的行为，号称99%的情况不需要用到，今天简单模拟了一下Django ORM Model。<br/>
Model 可以以下面的形式定义Field:
{% highlight python %}
from django.db import models


class Resource(models.Model):

    name = models.CharField(max_length=128, unique=True)
    host = models.GenericIPAddressField()
    description = models.TextField(blank=True)
{% endhighlight %}
在Resource Model对象使用：
{% highlight python %}
resource_obj = Resource(name='guset', host='127.0.0.1')
print Resource.name
# Output: <CharField object>
print resource_obj.name
# Output: guest
{% endhighlight %}

## 模拟代码：
{% highlight python %}
import six


class Field(object):

    __default = None

    def __init__(self, *args, **kwargs):
        self._default = kwargs.get('default', self.__default)

    @property
    def default(self):
        return self._default


class BaseModel(type):

    def __new__(mcls, name, bases, attrs):
        print [mcls, name, bases, attrs]
        fields = {}
        for attrname, attr in attrs.items():
            if isinstance(attr, Field):
                fields[attrname] = attr.default
                
        def __init__(self, *args, **kwargs):
            for field, default_value in fields.items():
                setattr(self, field, kwargs.get(field, default_value))
        attrs['__init__'] = __init__
        return type(name, (object,), attrs)


class MyModel(six.with_metaclass(BaseModel)):

    age = Field(default=0)
    name = Field(default='')


m = MyModel(age=100, name='aaa')
print MyModel.age, MyModel.name
print m.age, m.name

"""
Output:
[<class '__main__.BaseModel'>, 'MyModel', (), {'__module__': '__main__', 'age': <__main__.Field object at 0x7f2083b4f150>, 'name': <__main__.Field object at 0x7f2083bb5e90>}]
<__main__.Field object at 0x7f2083b4f150> <__main__.Field object at 0x7f2083bb5e90>
100 aaa
"""
{% endhighlight %}
