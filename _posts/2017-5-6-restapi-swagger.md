---
layout: post
title: restapi swagger
tags: restapi,swagger,文档,自动,gencode
datetime: 2017-5-6 19:16
---

{{ page.title }}
================

# 概述
<a href="http://swagger.io/">Swagger</a> is a powerful open source framework backed by a large ecosystem of tools that helps you design, build, document, and consume your RESTful APIs.

# RestAPI 文档化
Swagger UI
以Django为例：<a href="https://github.com/marcgibbons/django-rest-swagger">django-rest-swagger 点进去参考安装和使用方法</a>
django-rest-swagger配合django-rest-framework:
继承django-rest-framework的ViewSet
在处理函数中写YAML语言的schema，用来定义请求参数的类型和名称。
例如：
{% highlight YAML %}
"""
create a search for transaction dataset.
---

parameters:
    - name: body
      # pytype指集成rest_framework.Serializer的复杂类型的serializer
      pytype: TransParamSerializer
      paramType: body
"""
{% endhighlight %}
或者：
{% highlight YAML %}
"""
create a search for transaction dataset.
---

parameters:
    - name: body
"""
preview a search for transaction dataset.
---

request_serializer: TransPreviewParamSerializer
parameters:
    - name: id
      type: string
      paramType: query
    - name: type
      type: integer
      paramType: query
    - name: index
      type: integer
      required: false
      paramType: query
"""
{% endhighlight %}

# 生成client code
<a href="https://github.com/swagger-api/swagger-codegen">swagger-codegen</a>

## 下载codegen客户端：
wget http://central.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.2/swagger-codegen-cli-2.2.2.jar -O swagger-codegen-cli.jar

## 生成client代码generate code:
<p>
generate之前需要把restapi docs server跑起来，比如路径http://host/restapi/api-docs<br/>
java -jar swagger-codegen-cli.jar generate -i "https://host/restapi/api-docs" -l python -o output_dir<br/>
-i 输入，restapi服务的URL，必须是running server<br/>
-l 指定code的语言<br/>
-o api输出的目录<br/>
</p>
<p>
最后输出的目录结构：
{% highlight shell %}
|-OutputDir
   |- apis
       |- XXX_api.py
   |- models
       |- XXX_serializer.py
 api_client.py
{% endhighlight %}
api目录用来存放api类(APIClass)，具体请求类<br/>
> apis/XXX_api.py
models目录存放serializers<br/>
> models/XXX_serializer.py
api_client.py是Api Client Class。<br/>
</p>

## client的使用方法：
<p>
api = XXX_APIClass(APIClient) 实例化APIClass对象，然后调用api.method()，请求对应的restapi。<br/>
method名称是自动生成的，生成规则是：又ViewSet类名和方法决定，比如ITProductViewSet.list，得到it_product_list。<br/>
api.it_product_list()就会向restapi服务端发送请求，获取数据。
</p>
