---
layout: post
title: Python Profile function
tags: python,profile
datetime: 2017-5-8 15:04
---

{{ page.title }}
================

## 概述
<a href="https://docs.python.org/3/library/profile.html">The Python Profiler</a>
基于lsprof的用c语言实现的库,开销小,统计函数的调用时间和次数.

# Code
{% hightlight python %}
import cProfile, pstats
import re

def fib(n):
    if n==1 or n==2:
        return 1
    return fib(n-1)+fib(n-2)
   
def profile(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        try:
            pr.enable()
            return func(*args, **kwargs)
        finally:
            pr.disable()
            ps = pstats.Stats(pr)
            ps.sort_stats('time', 'cumulative').print_stats()
    return wrapper

@profile
def foo():
    fib(30)

foo()
{% endhighlight %}

# 输出
{% highlight shell %}
832040
         1664081 function calls (3 primitive calls) in 0.466 seconds

   Ordered by: internal time, cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
1664079/1    0.466    0.000    0.466    0.466 ./test.py:43(fib)
        1    0.000    0.000    0.466    0.466 ./test.py:108(foo)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
{% endhighlight %}
其中，输出每列的具体解释如下：<br/>

ncalls：表示函数调用的次数；<br/>

tottime：表示指定函数的总的运行时间，除掉函数中调用子函数的运行时间；<br/>

percall：（第一个percall）等于 tottime/ncalls；<br/>

cumtime：表示该函数及其所有子函数的调用运行的时间，即函数开始调用到返回的时间；<br/>

percall：（第二个percall）即函数运行一次的平均时间，等于 cumtime/ncalls；<br/>

filename:lineno(function)：每个函数调用的具体信息；<br/>

