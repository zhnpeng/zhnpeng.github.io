---
layout: post
title: zmq broker 并发问题
tags: [zmq, router, borker, concurrent]
datetime: 2020-5-3 9:34
---

{{ page.title }}
================

## 概述
zmq是一个异步消息队列库，使用方便，我们用了broker pattern，用于异步任务系统，但是由于这个模式是reactor模式，单线程每次处理一次请求并且响应，导致当并发量大或者单词请求耗时长时，broker节点会成为瓶颈。

## ZeroMQ broker pattern
<img src="/assets/img/zmq-broker-pattern.png" />

## 当前框架

* 客户端所以请求经过broker节点，broker节点负责代理请求到后端worker
* worker节点发送heartbeat到broker，broker负责识别worker状态和管理worker
* worker进程异步调度任务，worker可互相调用（需通过broker）
* 任务行为分为create,query,result,stop

结构和流程：
<img src="/assets/img/zmq-broker-issue-1.png" />
如上图所示，merge需要发起多个stat统计任务，并且poll该任务完成之后做合并，我们遇到的场景是这个统计返回的数据量会比较大，比如30-100M，这种情况下，当任务完成，client请求获取result数据的时候，io耗时比较长，比如30M耗时1.x秒，多个这样的请求，就会堵塞。
另外还有一个问题是并发问题，如果并发很大，client请求在队列中，长时间不响应也会超时（比如10s超时)。

## 改进

使用connection per thread pattern进行改进，由于我们的场景是result请求io耗时太长导致的，所以只把这个模式应用于result请求，其他的create,query请求依然用reactor模式。

结构和流程：
<img src="/assets/img/zmq-broker-issue-2.png" />
如上图所示

* client 需要将result请求分发到result_router
* router负责处理create,query请求，worker heartbeat，并且把worker状态通过pub/sub模式publish到result_router
* result_router只代理result请求，使用connection per thread模式

## 高并发改进

如果真的是并发问题，可以考虑使用多个broker来处理create和query等，对于非耗时长的操作，reactor的性能应该是比connection per thread模式高。

类似于：
<img src="/assets/img/zmq-cross-connected-workers.png" />
