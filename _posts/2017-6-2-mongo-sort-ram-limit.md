---
layout: post
title: Mongo sort ram limit
tags: Mongo,sort,ram,query,find,aggregate
datetime: 2017-6-2 9:59
---

{{ page.title }}
================

## 概述
<p>
Mongo sort操作是在内存里sort数据，默认会有最大内存限制.
find/query的sort默认是32MB,aggregate的$sort默认是100MB，当sort条目数据量超过之后就会报错.
</p>
{% highlight javascript %}
Error: error: {
    "waitedMS" : NumberLong(0),
    "ok" : 0,
    "errmsg" : "Executor error during find command: OperationFailed: Sort operation used more than the maximum 33554432 bytes of RAM. Add an index, or specify a smaller limit.",
    "code" : 96
}
{% endhighlight %}

## 解决方法:

# 增大内存ram limit
db.adminCommand({setParameter: 1, internalQueryExecMaxBlockingSortBytes: 100000000})

# 使用limit限制数据集数量
<a href="https://docs.mongodb.com/manual/reference/operator/aggregation/sort/#sort-operator-and-memory">aggregation sort operator and memory</a>
<p>
Mongo 2.4以后，内存只会保存limit数量n的top n的条目，应该是sort过程中把末尾元素替换掉。<br />
2.4版本以前，mongo会把所有item放到内存在sort，然后做limit,因此这个方法只适用于Mongo 2.4以后的版本.
</p>

# 建立索引
对于query操作，可以通过<strong>db.connection.createIndex({key: 1})</strong>的方式建立索引。

# 使用aggregate代替query
<p>
使用ggregate时加上allowDiskUse:true参数（因为aggregate document有16MB的内存限制），允许aggregate时当内存超过限制时使用Disk Storage。<br/>
如果是query/find操作，可以转换成aggregate操作。aggregate的$sort内存限制默认是100MB，而query sort是32MB。<br/>
比如<strong>db.connection.aggregate([{$sort: {duration: 1}}], {allowDiskUse: true})</strong>
</p>
简单性能比对：

1.count
> db.getCollection('transtrack_20170601T153539F929136R119').find({}).count()

> 81601

2.set memory limit to 100MB
> db.adminCommand({setParameter: 1, internalQueryExecMaxBlockingSortBytes: 100000000})

3.sort use memory only
> db.getCollection('transtrack_20170601T153539F929136R119').find({}).sort({duration:1})

> cost: 0.4s-0.7s

5.use aggregate and allowDiskUse
> db.getCollection('transtrack_20170601T153539F929136R119').aggregate([{$sort: {duration: 1}}], {allowDiskUse: true})

> cost 1s-1.5s

80000数据,sort的字段没有index,默认document limit情况下，aggregate+allowDiskUse性能比memory limit范围内的query sort慢了一倍多。