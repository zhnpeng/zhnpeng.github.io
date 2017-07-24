---
layout: post
title: 解决Javascript内存泄露问题
tags: javascript,memory leak,内存泄露
datetime: 2017-7-24 10:18
---

{{ page.title }}
================

## javascript 内存回收
javascript内存大概也是周期性找到没有被使用的内存,然后将其回收.每个内存都会有引用计数来标示该对象,如果引用计数清零,说明内存可以被回收,
然后通过标记清除告诉内存回收器适时回收内存.

## 调试内存泄露
调试内存泄露一般要到解析器/VM里调,对于js来说就是browser.
chrome的devtools提供了调试工具,主要由三种,Take Heap Snapshot,Record Allocation Profile和Record Allocation Timeline.
调试工具默认可能没有functioin call stack,需要在devtools的settings里勾选Record heap allocation stack traces
<img src="/assets/img/js-memory-leak-1.png" />

## 调试过程
使用Record Allocation Timeline可以记录整个时间段内存泄露情况,
如下图蓝色的柱子代表内存没有被回收,灰色的柱子是被回收调的内存.
<img src="/assets/img/js-memory-leak-2.png" />

选择某个时间段,可以看到这个时间段的内存使用情况,并且在Allocation Stack页签下看到function call stack.
<img src="/assets/img/js-memory-leak-3.png" />
在function call stack中inspect就可以看到那段代码引起的内存泄露.

## 修复后
修复后再使用Record Allocation Timeline功能抓取内存,可以看到之前泄露的内存已经在列表中消失,如下图.
<img src="/assets/img/js-memory-leak-4.png" />
