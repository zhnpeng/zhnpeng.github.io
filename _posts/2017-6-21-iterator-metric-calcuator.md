---
layout: post
title: Python实现指标运算
tags: generator,python,metric,calculator
datetime: 2017-6-21 14:07
---

{{ page.title }}
================

### 概述
指标运算,包含嵌套的运算,实现了diff,sum,limit,sort.<br/>

流程: 函数表达式解析 -> 运行解析后的表达式 -> 出运算结果 <br/>

# 包括组件:
1. 基于pyparsing的nested function call grammar.支持表达式和python的args和kwargs,参数类型只支持string和float
2. 运算函数,所有运算函数接收iterator进行迭代运算,kwargs作为辅助参数.
3. 运行函数,负责根据pyparsing解析出来的词法结构来调度运行具体的运算函数(递归调度),还有负责准备参数


### sample code
{% highlight python %}
# -*- utf-8 -*-
from pyparsing import (
    Group,
    Literal,
    Word,
    ZeroOrMore,
    alphas,
    alphanums,
    Combine,
    nums,
    Forward,
    ParseResults
)


"""
gramner to represent a simple nested function call
function call only support identifier and float number, other datastructs such as array not support yet.
"""
# suppress means ignore this literal when parse expression
lparen = Literal("(").suppress()
rparen = Literal(")").suppress()
comma = Literal(",").suppress()
assign = Literal('=').suppress()


identifier = Word(alphas, alphanums + "_")
number  = Word(nums+'.').setParseAction(lambda t: float(t[0]))
# kwarg in python
kwidentifier = Group(identifier + assign + ( number | identifier )).setParseAction(lambda t: {t[0][0]: t[0][1]})
functor = identifier

# allow expression to be used recursively
expression = Forward()

arg =  number | expression | kwidentifier | identifier
args = arg + ZeroOrMore(comma + arg)

expression << Group(functor + Group(lparen + args + rparen))
#print  expression.parseString("func_f(func_g(garg1, garg2), func_h(harg1, harg2), farg3, limit=30.54)")
"""
end of pyparsing grammer, now we get expression to parse string.
"""

""" context store variable, for execute to get """
a = [i for i in map(lambda x: x+3, xrange(10))]
b = [i for i in map(lambda x: x+2, xrange(10))]
c = [i for i in map(lambda x: x+1, xrange(10))]

# use to store variable
context = {
    'a': a,
    'b': b,
    'c': c
}


""" define calculator functions """

""" function manager """
class func_manager(object):

    funcs = {}

    @classmethod
    def reg(cls, func_class):
        cls.funcs[func_class.__name__] = func_class

    @classmethod
    def get(cls, name):
        return cls.funcs.get(name, lambda x:x)

""" functions defination """
# diff
# a diff b: each item in a substract each one in b
@func_manager.reg
class diff_func(object):

    def __init__(self, iterator):
        self.__it = iterator

    def __call__(self):
        for item in self.__it:
            yield reduce(lambda x,y=0: x-y, item)

# test
# print [i for i in diff_func(zip(a,b,c))()]
# print [i for i in diff_func(zip(diff_func(zip(a, b))(), c))()]

# limit
@func_manager.reg
class limit_func(object):

    def __init__(self, iterator, limit=-1):
        self.__it = iterator
        self.__limit = int(limit)

    def __call__(self):
        if self.__limit > -1:
            for i in xrange(self.__limit):
                yield next(self.__it)
        else:
            yield next(self.__it)

# test
# print [i for i in limit_func(iter(a), 5)()]

# sort
@func_manager.reg
class sort_func(object):

    def __init__(self, iterator, asc=1):
        self.__it = iterator
        self.__asc = int(asc)

    def __call__(self):
        items = sorted(self.__it, reverse=(not self.__asc))
        for i in items:
            yield i

# test
# print [i for i in sort_func(limit_func(diff_func(iter(zip(a,b,c)))(), 5)())()]

# sum
@func_manager.reg
class sum_func(object):

    def __init__(self, iterator):
        self.__it = iterator

    def __call__(self):
        yield sum(self.__it)


""" execute expression parsed by pyparsing """
def execute(ep):
    # Group(func, Group(arg1, arg2, ...))
    func_name = ep[0]
    func_args = ep[1]
    args = []
    kwargs = {}
    # prepare arg and kwargs
    for arg in func_args:
        if isinstance(arg, ParseResults):
            # recusive execute if is another cal_func
            args.append(execute(arg))
        elif isinstance(arg, dict):
            kwargs.update(arg)
        else:
            real_arg = context.get(arg)
            args.append(real_arg)
    arg = args[0]
    if len(args)>1:
        # if more than one args, convert them to iterator with zip
        arg =  iter(zip(*args))
    return func_manager.get(func_name)(arg, **kwargs)()

""" Test """
def test():
    print "context %r" %  context

    exp = 'diff_func(diff_func(a,b),c)'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == map(lambda x: x[0]-x[1]-x[2], zip(a,b,c))

    exp = 'sum_func(a)'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == [sum(a)]

    exp = 'limit_func(diff_func(diff_func(a,b),c),limit=5)'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == [0,-1,-2,-3,-4]

    exp = 'sum_func(limit_func(diff_func(diff_func(a,b),c),limit=5))'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == [-10]

    exp = 'sort_func(a, asc=0)'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == sorted(a, reverse=1)

    exp = 'sort_func(limit_func(diff_func(diff_func(a,b),c),limit=5),asc=1)'
    print exp
    exp_parsed = expression.parseString(exp)
    ret = [i for i in execute(exp_parsed[0])]
    print ret
    assert ret == [0,-1,-2,-3,-4][::-1]

test()

"""
ontext {'a': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'c': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'b': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}
diff_func(diff_func(a,b),c)
[0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
sum_func(a)
[75]
limit_func(diff_func(diff_func(a,b),c),limit=5)
[0, -1, -2, -3, -4]
sum_func(limit_func(diff_func(diff_func(a,b),c),limit=5))
[-10]
sort_func(a, asc=0)
[12, 11, 10, 9, 8, 7, 6, 5, 4, 3]
sort_func(limit_func(diff_func(diff_func(a,b),c),limit=5),asc=1)
[-4, -3, -2, -1, 0]
"""
{% endhighlight %}
