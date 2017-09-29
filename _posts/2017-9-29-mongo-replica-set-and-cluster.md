---
layout: post
title: Mongo复制集和集群
tags: DB, mongo, replica set, cluster, mongos, shard, config server
datetime: 2017-9-29 16:42
---

{{ page.title }}
================
### 概述
<a href="https://docs.mongodb.com/manual/sharding/index.html">Mongo集群官方介绍</a>

### 什么时候考虑用Shard Cluster?
<p>
当你考虑使用 Sharded cluster 时，通常是要解决如下2个问题<br/>
1. 存储容量受单机限制，即磁盘资源遭遇瓶颈。<br/>
2. 读写能力受单机限制（读能力也可以在复制集里加 secondary 节点来扩展），可能是 CPU、内存或者网卡等资源遭遇瓶颈，导致读写能力无法扩展。<br/>
如果你没有遇到上述问题，使用 MongoDB 复制集就足够了，管理维护上比 Sharded cluster 要简单很多。
</p>

### Mongo集群框架图
<img src="/assets/img/mongo-cluster-framework.png" />
<p>
集群之后通过mongos读写数据，整个分片读写过程对client端来说是透明的。非集群情况mongo client直接访问mongod读写数据。
</p>
<p>
<strong>replica set是复制集</strong>，比如Shard replica set就是由多个mongod组成的分片服务器集合，除了mongos之外，configs server和shard都可以配成复制集（HA）
也可以不配使用复制集，直接把一个mongod添加到集群分片合集中(sh.addShard(‘host:port’))
</p>
<p>
Mongos，Config Server和Shard都是mongod进程，Mongos负责Router和load balance，Config Servers负责保存集群配置信息。Shard负责存储数据。
</p>

# 关于Shard Key
<p>
Shard Key分为2种，range Key和hashed key<br/>
collection的shard key需要建立索引，要么是独立索引，要么是复合索引的前缀（如果没有建索引，会在设置成shard key时被强制建立索引）
</p>

### Mongo Cluster 配置
<a href="https://docs.mongodb.com/manual/tutorial/deploy-sharded-cluster-ranged-sharding/">官方文档以range key为例</a>

# sharding配置是以collection为对象的
<p>
所以如果某个collection没有设置分片，那就会存放在primary chunk里。
设置了分片的collection会根据shard key分别读写到对应的chunk中。
<a href="https://docs.mongodb.com/manual/reference/command/">pymongo command和mongo runCommand()的一样。</a>
</p>
<p>
如果collection是在运行时创建的，需要在创建的时候调用命令（mongo shell）<br/>
sh.enableSharding(“database name”)，用来允许数据库分片 <br/>
sh.shardCollectioin(‘db name.collection name’, {key: directory or ‘hashed’})，设置collection的分片key
其他相关命令<br/>
sh.addShard(‘replica set name/host:port’)，添加shard数据库（集合）<br/>
sh.status()，查看cluster的库和集合的状态。<br/>
如下图：
<img src="/assets/img/mongo-sh-status.png" />
蓝色框表示3个shards（都不是复制集而是单独mongod server）
</p>

### Aggregate 在集群中的行为
<a href="https://docs.mongodb.com/manual/core/aggregation-pipeline-sharded-collections/#aggregation-pipeline-sharded-collection">
Aggregation Pipeline and Sharded Collections
</a>
<p>
如果pipeline开头的$match条件是指向一个确定的shard key的话，那整个aggregate pipeline只会在匹配的shard上执行，然后直接结果返回给mongos，不需要primary shard做merge，否则需要primary shard（或者一个随机shard）做merge，然后再返回给mongos。
</p>
<p>
对集群来说，如果aggregate操作是需要merge的话，会有splitPipeline，splitPipeline会分成2部分，第一部分是shardsPart，第二部分是mergerPart，shardsPart就是shard执行的pipeline，mergerPart就是做merge的pipeline，为了减轻primary shard的负荷，如果没有参数指明一定要primary shard做merge，就随机一个shard来merge
</p>
<p>
在执行db.collections.aggregate()方法中加入参数explain就可以返回pipeline的分裂结果。
</p>
比如<br/>
{% highlight python %}
db.getCollection('stat_cap1_1h_x').aggregate(
    [
        { $match: { t : { $gte: 1506481000, $lt: 1506499201 }  } },
        { $project: { ts: "$t", trans_type: "$n", _1m: 1, _id: 0 } },
        { $unwind: "$_1m" },
        { $match: { _1m: { $ne: null } } },
        { $project: { ts: { $add: [ "$ts", "$_1m.t" ] }, trans_type: 1, duration: "$_1m.u", resp_count: "$_1m.p" } },
        { $match: { ts: { $gte: 1506481000, $lt: 1506499201 } } },
        { $group: { _id: { trans_type: "$trans_type" }, _raw_duration: { $avg: "$duration" }, resp_count: { $sum: "$resp_count" } } } ,
    ],
    { explain: true }
)
{% endhighlight %}
输出<br/>
{% highlight json %}
{
    "needsPrimaryShardMerger" : false,
    "splitPipeline" : {
        "shardsPart" : [
            {
                "$match" : {
                    "t" : {
                        "$gte" : 1506481000.0,
                        "$lt" : 1506499201.0
                    }
                }
            },
            {
                "$project" : {
                    "_id" : false,
                    "ts" : "$t",
                    "trans_type" : "$n",
                    "_1m" : true
                }
            },
            {
                "$unwind" : {
                    "path" : "$_1m"
                }
            },
            {
                "$match" : {
                    "_1m" : {
                        "$ne" : null
                    }
                }
            },
            {
                "$project" : {
                    "ts" : {
                        "$add" : [
                            "$ts",
                            "$_1m.t"
                        ]
                    },
                    "trans_type" : true,
                    "duration" : "$_1m.u",
                    "resp_count" : "$_1m.p"
                }
            },
            {
                "$match" : {
                    "ts" : {
                        "$gte" : 1506481000.0,
                        "$lt" : 1506499201.0
                    }
                }
            },
            {
                "$group" : {
                    "_id" : {
                        "trans_type" : "$trans_type"
                    },
                    "_raw_duration" : {
                        "$avg" : "$duration"
                    },
                    "resp_count" : {
                        "$sum" : "$resp_count"
                    }
                }
            }
        ],
        "mergerPart" : [
            {
                "$group" : {
                    "_id" : "$$ROOT._id",
                    "_raw_duration" : {
                        "$avg" : "$$ROOT._raw_duration"
                    },
                    "resp_count" : {
                        "$sum" : "$$ROOT.resp_count"
                    },
                    "$doingMerge" : true
                }
            }
        ]
    },
    "shards" : {
        "SS185" : {
            "host" : "172.16.13.185:27018",
            "stages" : [
                {
                    "$cursor" : {
                        "query" : {
                            "t" : {
                                "$gte" : 1506481000.0,
                                "$lt" : 1506499201.0
                            }
                        },
                        "fields" : {
                            "_1m" : 1,
                            "n" : 1,
                            "t" : 1,
                            "_id" : 0
                        },
                        "queryPlanner" : {
                            "plannerVersion" : 1,
                            "namespace" : "bpc_data_app1_1m_201709.stat_cap1_1h_x",
                            "indexFilterSet" : false,
                            "parsedQuery" : {
                                "$and" : [
                                    {
                                        "t" : {
                                            "$lt" : 1506499201.0
                                        }
                                    },
                                    {
                                        "t" : {
                                            "$gte" : 1506481000.0
                                        }
                                    }
                                ]
                            },
                            "winningPlan" : {
                                "stage" : "CACHED_PLAN",
                                "inputStage" : {
                                    "stage" : "SHARDING_FILTER",
                                    "inputStage" : {
                                        "stage" : "FETCH",
                                        "filter" : {
                                            "t" : {
                                                "$lt" : 1506499201.0
                                            }
                                        },
                                        "inputStage" : {
                                            "stage" : "IXSCAN",
                                            "keyPattern" : {
                                                "t" : -1,
                                                "g" : 1
                                            },
                                            "indexName" : "t_-1_g_1",
                                            "isMultiKey" : true,
                                            "isUnique" : false,
                                            "isSparse" : false,
                                            "isPartial" : false,
                                            "indexVersion" : 1,
                                            "direction" : "forward",
                                            "indexBounds" : {
                                                "t" : [
                                                    "[inf.0, 1506481000.0]"
                                                ],
                                                "g" : [
                                                    "[MinKey, MaxKey]"
                                                ]
                                            }
                                        }
                                    }
                                }
                            },
                            "rejectedPlans" : []
                        }
                    }
                },
                {
                    "$project" : {
                        "_id" : false,
                        "ts" : "$t",
                        "trans_type" : "$n",
                        "_1m" : true
                    }
                },
                {
                    "$unwind" : {
                        "path" : "$_1m"
                    }
                },
                {
                    "$match" : {
                        "_1m" : {
                            "$ne" : null
                        }
                    }
                },
                {
                    "$project" : {
                        "ts" : {
                            "$add" : [
                                "$ts",
                                "$_1m.t"
                            ]
                        },
                        "trans_type" : true,
                        "duration" : "$_1m.u",
                        "resp_count" : "$_1m.p"
                    }
                },
                {
                    "$match" : {
                        "ts" : {
                            "$gte" : 1506481000.0,
                            "$lt" : 1506499201.0
                        }
                    }
                },
                {
                    "$group" : {
                        "_id" : {
                            "trans_type" : "$trans_type"
                        },
                        "_raw_duration" : {
                            "$avg" : "$duration"
                        },
                        "resp_count" : {
                            "$sum" : "$resp_count"
                        }
                    }
                }
            ]
        },
        "SS187" : {
            "host" : "172.16.13.187:27018",
            "stages" : [
                {
                    "$cursor" : {
                        "query" : {
                            "t" : {
                                "$gte" : 1506481000.0,
                                "$lt" : 1506499201.0
                            }
                        },
                        "fields" : {
                            "_1m" : 1,
                            "n" : 1,
                            "t" : 1,
                            "_id" : 0
                        },
                        "queryPlanner" : {
                            "plannerVersion" : 1,
                            "namespace" : "bpc_data_app1_1m_201709.stat_cap1_1h_x",
                            "indexFilterSet" : false,
                            "parsedQuery" : {
                                "$and" : [
                                    {
                                        "t" : {
                                            "$lt" : 1506499201.0
                                        }
                                    },
                                    {
                                        "t" : {
                                            "$gte" : 1506481000.0
                                        }
                                    }
                                ]
                            },
                            "winningPlan" : {
                                "stage" : "CACHED_PLAN",
                                "inputStage" : {
                                    "stage" : "SHARDING_FILTER",
                                    "inputStage" : {
                                        "stage" : "FETCH",
                                        "filter" : {
                                            "t" : {
                                                "$lt" : 1506499201.0
                                            }
                                        },
                                        "inputStage" : {
                                            "stage" : "IXSCAN",
                                            "keyPattern" : {
                                                "t" : -1,
                                                "g" : 1
                                            },
                                            "indexName" : "t_-1_g_1",
                                            "isMultiKey" : true,
                                            "isUnique" : false,
                                            "isSparse" : false,
                                            "isPartial" : false,
                                            "indexVersion" : 1,
                                            "direction" : "forward",
                                            "indexBounds" : {
                                                "t" : [
                                                    "[inf.0, 1506481000.0]"
                                                ],
                                                "g" : [
                                                    "[MinKey, MaxKey]"
                                                ]
                                            }
                                        }
                                    }
                                }
                            },
                            "rejectedPlans" : []
                        }
                    }
                },
                {
                    "$project" : {
                        "_id" : false,
                        "ts" : "$t",
                        "trans_type" : "$n",
                        "_1m" : true
                    }
                },
                {
                    "$unwind" : {
                        "path" : "$_1m"
                    }
                },
                {
                    "$match" : {
                        "_1m" : {
                            "$ne" : null
                        }
                    }
                },
                {
                    "$project" : {
                        "ts" : {
                            "$add" : [
                                "$ts",
                                "$_1m.t"
                            ]
                        },
                        "trans_type" : true,
                        "duration" : "$_1m.u",
                        "resp_count" : "$_1m.p"
                    }
                },
                {
                    "$match" : {
                        "ts" : {
                            "$gte" : 1506481000.0,
                            "$lt" : 1506499201.0
                        }
                    }
                },
                {
                    "$group" : {
                        "_id" : {
                            "trans_type" : "$trans_type"
                        },
                        "_raw_duration" : {
                            "$avg" : "$duration"
                        },
                        "resp_count" : {
                            "$sum" : "$resp_count"
                        }
                    }
                }
            ]
        }
    },
    "ok" : 1.0
}
{% endhighlight %}
在一个shard里的情况
{% highlight python %}
db.getCollection('stat_cap1_1h_x').aggregate(
    [
        { $match: { _id : { $eq: 1506337200} } },
        { $project: { ts: "$t", trans_type: "$n", _1m: 1, _id: 0 } },
        { $unwind: "$_1m" },
        { $match: { _1m: { $ne: null } } },
        { $project: { ts: { $add: [ "$ts", "$_1m.t" ] }, trans_type: 1, duration: "$_1m.u", resp_count: "$_1m.p" } },
        { $match: { ts: { $gte: 1506481000, $lt: 1506499201 } } },
        { $group: { _id: { trans_type: "$trans_type" }, _raw_duration: { $avg: "$duration" }, resp_count: { $sum: "$resp_count" } } } ,
    ],
    { explain: true })
{% endhighlight %}
输出
{% highlight json %}
{
    "splitPipeline" : null,
    "shards" : {
        "SS185" : {
            "host" : "172.16.13.185:27018",
            "stages" : [
                {
                    "$cursor" : {
                        "query" : {
                            "_id" : {
                                "$eq" : 1506337200.0
                            }
                        },
                        "fields" : {
                            "_1m" : 1,
                            "n" : 1,
                            "t" : 1,
                            "_id" : 0
                        },
                        "queryPlanner" : {
                            "plannerVersion" : 1,
                            "namespace" : "bpc_data_app1_1m_201709.stat_cap1_1h_x",
                            "indexFilterSet" : false,
                            "parsedQuery" : {
                                "_id" : {
                                    "$eq" : 1506337200.0
                                }
                            },
                            "winningPlan" : {
                                "stage" : "CACHED_PLAN",
                                "inputStage" : {
                                    "stage" : "FETCH",
                                    "inputStage" : {
                                        "stage" : "SHARDING_FILTER",
                                        "inputStage" : {
                                            "stage" : "IXSCAN",
                                            "keyPattern" : {
                                                "_id" : 1
                                            },
                                            "indexName" : "_id_",
                                            "isMultiKey" : false,
                                            "isUnique" : true,
                                            "isSparse" : false,
                                            "isPartial" : false,
                                            "indexVersion" : 1,
                                            "direction" : "forward",
                                            "indexBounds" : {
                                                "_id" : [
                                                    "[1506337200.0, 1506337200.0]"
                                                ]
                                            }
                                        }
                                    }
                                }
                            },
                            "rejectedPlans" : []
                        }
                    }
                },
                {
                    "$project" : {
                        "_id" : false,
                        "ts" : "$t",
                        "trans_type" : "$n",
                        "_1m" : true
                    }
                },
                {
                    "$unwind" : {
                        "path" : "$_1m"
                    }
                },
                {
                    "$match" : {
                        "_1m" : {
                            "$ne" : null
                        }
                    }
                },
                {
                    "$project" : {
                        "ts" : {
                            "$add" : [
                                "$ts",
                                "$_1m.t"
                            ]
                        },
                        "trans_type" : true,
                        "duration" : "$_1m.u",
                        "resp_count" : "$_1m.p"
                    }
                },
                {
                    "$match" : {
                        "ts" : {
                            "$gte" : 1506481000.0,
                            "$lt" : 1506499201.0
                        }
                    }
                },
                {
                    "$group" : {
                        "_id" : {
                            "trans_type" : "$trans_type"
                        },
                        "_raw_duration" : {
                            "$avg" : "$duration"
                        },
                        "resp_count" : {
                            "$sum" : "$resp_count"
                        }
                    }
                }
            ]
        }
    },
    "ok" : 1.0
}
{% endhighlight %}

### 一些tips
<p>
要换shard_key，没有自动更换的命令，需要：<br/>
<ol>
<li>把collection的数据导出，mongoexport db.collection to file.dat</li>
<li>drop掉集合，drop collection</li>
<li>重新建集合，设置需要的索引</li>
<li>配置集合分片，shardCollection(‘db.collection’, {new_key: ‘hashed’})</li>
<li>导入之前导出的数据，mongoimport to db.collection from file.dat</li>
</ol>
以上需要连接mongos操作
</p>
<p>
如果要更换shard set某个成员，需要重启cluster里的全部服务，包括mongos，config server和shard。
否则执行和shard相关命令时会报错说replica set name different from old name之类的错误。
</p>
