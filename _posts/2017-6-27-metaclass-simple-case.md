---
layout: post
title: python metaclass
tags: python,metaclass,orm,simple
datetime: 2017-6-27 22:38
---

{{ page.title }}
================

### 概述
metaclass在很多语言里都有，能够动态改变类的行为。

### 例子：简单模拟了一下Django ORM Model
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
print m.age, m.nam

"""
Output:
[<class '__main__.BaseModel'>, 'MyModel', (), {'__module__': '__main__', 'age': <__main__.Field object at 0x7f2083b4f150>, 'name': <__main__.Field object at 0x7f2083bb5e90>}]
<__main__.Field object at 0x7f2083b4f150> <__main__.Field object at 0x7f2083bb5e90>
100 aaa
"""
{% endhighlight %}

# Tips
{% highlight python %}
def __init__(self, *args, **kwargs):
    for field, field_obj in fields.items():
        cleaned_data = field_obj.validate(kwargs.get(field, None))
        setattr(self, field, cleaned_data)
attrs['__init__'] = __init__
{% endhighlight %}
这段代码重载了类的构造函数<code>__init__</code>，在构造的时候会调用<code>Field.validate</code>方法，并且把对象的属性赋值为validated之后的cleaned_data。<br/>
所以在调用<code>print MyModel.age</code>打印的是Field Object，而MyModel()对象输出的是100。

### 例子：metaclass hook 实现 mixin
{% highlight python %}
# -*- coding: utf-8 -*-
import six
from collections import OrderedDict

class MetaClass(type):
    
    @classmethod
    def _get_hook_funcs(cls, bases, attrs):
        fields = [(field_name, attrs.pop(field_name))
                  for field_name, obj in list(attrs.items())
                  if field_name.startswith("_do_")]

        for base in reversed(bases): #遵循多重继承顺序
            if hasattr(base, '_hook_funcs'):
                fields += list(base._hook_funcs.items())
        # 返回OrderedDict，因此是重名覆盖
        return OrderedDict(fields)
    
    def __new__(cls, name, bases, attrs):
        attrs['_hook_funcs'] = cls._get_hook_funcs(bases, attrs)
        return super(MetaClass, cls).__new__(cls, name, bases, attrs)
    
class MetaClassAll(type):
    
    @classmethod
    def _get_hook_funcs(cls, bases, attrs):
        fields = []
        for name, _ in attrs.items():
            if name.startswith("_do_"):
                fields.append(attrs.pop(name))

        for base in reversed(bases):
            if hasattr(base, '_hook_funcs'):
                fields += base._hook_funcs
        # 返回list，重名不覆盖
        return fields
    
    def __new__(cls, name, bases, attrs):
        attrs['_hook_funcs'] = cls._get_hook_funcs(bases, attrs)
        return super(MetaClassAll, cls).__new__(cls, name, bases, attrs)


class Mixin1(object):
    __metaclass__ = MetaClass
    
    def _do_mixin1(self):
        print "foo from Minxin1"
    
class Mixin2(object):
    __metaclass__ = MetaClass
    
    def _do_mixin2(self):
        print "foo from Minxin2"

class KlassBase(object):
    __metaclass__ = MetaClass

    def foo(self):
        if getattr(self, "_hook_funcs", None):
            for name, func in self._hook_funcs.items():
                func(self)
    
    def _do_print1(self):
        self.print1()
    
    def print1(self):
        print "print 1 from KlassBase"
    
class MyKlass(KlassBase, Mixin1, Mixin2):
    
    def print1(self):
        print "print 1 form KlassA"

MyKlass().foo()

"""
Output:
foo from Minxin2
foo from Minxin1
print 1 form KlassA
"""
{% endhighlight %}
# Tips:
metaclass通过收集当前类和基类的所有_do_开头的属性，放到当前类的_hook_funcs属性中，在基类调用钩子里的函数。<br/>
MetaClass的_hook_funcs是OrderedDict，因此同名hook函数覆盖.MetaClassAll使用list存储所以hook functions，因此不覆盖。