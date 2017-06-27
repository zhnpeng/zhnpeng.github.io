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


class BaseField(object):

    __default = None

    def __init__(self, *args, **kwargs):
        self.__value = kwargs.get('default', self.__default)

    def validate(self, value):
        raise NotImplemented


class IntegerField(BaseField):

    def validate(self, value):
        # raise directly if exception occur
        self.__value = int(value)
        # simply return clean value after validate
        return self.__value


class CharField(BaseField):

    def validate(self, value):
        self.__value = str(value)
        return self.__value


class BaseModel(type):

    def __new__(mcls, name, bases, attrs):
        print [mcls, name, bases, attrs]
        fields = {}
        for attrname, attr in attrs.items():
            if isinstance(attr, BaseField):
                fields[attrname] = attr

        def __init__(self, *args, **kwargs):
            for field, field_obj in fields.items():
                cleaned_data = field_obj.validate(kwargs.get(field, None))
                setattr(self, field, cleaned_data)
        attrs['__init__'] = __init__
        return type(name, (object,), attrs)


class MyModel(six.with_metaclass(BaseModel)):

    age = IntegerField(default=0)
    name = CharField(default='')


m = MyModel(age='a100', name='aaa')
print MyModel.age, MyModel.name
print m.age, m.name

"""
Output:
[<class '__main__.BaseModel'>, 'MyModel', (), {'__module__': '__main__', 'age': <__main__.Field object at 0x7f2083b4f150>, 'name': <__main__.Field object at 0x7f2083bb5e90>}]
<__main__.Field object at 0x7f2083b4f150> <__main__.Field object at 0x7f2083bb5e90>
100 aaa
"""
{% endhighlight %}

## 结尾
使用metaclass来实现这种功能我想到的好处有：<br/>
1. 使用接口非常简单。<br/>
2. 封装了很多功能，像我上面的简单例子，把Field的validate行为封装成统一调用。<br/>
还有其他的网上说的好处，就像使用django ORM Model一样，当然djang ORM复杂很多。<br/>
虽然号称99%的情况用不到metaclass，但是metaclass还是需要学习的。
