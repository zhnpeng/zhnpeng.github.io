---
layout: post
title: cookies，会话和跨域
tags: cookies,session,跨域请求,csr
datetime: 2017-6-8 21:13
---

{{ page.title }}
================

### Cookies
<img src="/assets/img/set-cookies.png" />
<p>
(a) 用户第一次访问 Web 站点，Web 服务器对用户一无所知。<br/>
(b) Web 服务器希望这个用户下次访问该站点时，可以识别出它来。所以通过 Set-Cookie（或 Set-Cookie2）向客户端回送一个独有的 cookie。上图中，服务器会将一个表示 id="34294" 的 cookie 返回给用户。服务器可以用这个数字来查找服务器为其访问者累积的数据库信息。cookie 并不仅限于保存 ID 号。很多 Web 服务器都会将信息以名值对的形式直接保存在 cookie 中。<br/>
(c) 浏览器接收到 Web 服务器的响应，会将 Set-Cookie（或 Set-Cookie2）首部中的 cookie 内容保存在本地。将来用户再次访问同一站点时，浏览器会将 cookie 的内容取出，并通过 Cookie 请求首部将其传回去，以此来标识自己的身份。<br/>
</p>

# cookies参数和数据结构
<ul>
<li>
domain表示的是cookie所在的域，默认为请求的地址，如网址为www.test.com/test/test.aspx，那么domain默认为www.test.com。而跨域访问，如域A为t1.test.com，域B为t2.test.com，那么在域A生产一个令域A和域B都能访问的cookie就要将该cookie的domain设置为.test.com；如果要在域A生产一个令域A不能访问而域B能访问的cookie就要将该cookie的domain设置为t2.test.com。
</li>
<li>
path表示cookie所在的目录，asp.net默认为/，就是根目录。在同一个服务器上有目录如下：/test/,/test/cd/,/test/dd/，现设一个cookie1的path为/test/，cookie2的path为/test/cd/，那么test下的所有页面都可以访问到cookie1，而/test/和/test/dd/的子页面不能访问cookie2。这是因为cookie能让其path路径下的页面访问。
</li>
<li>
浏览器会将domain和path都相同的cookie保存在一个文件里，cookie间用*隔开。
</li>
<li>
含值键值对的cookie：以前一直用的是nam=value单键值对的cookie，一说到含多个子键值对的就蒙了。现在总算弄清楚了。含多个子键值对的cookie格式是name=key1=value1&key2=value2。可以理解为单键值对的值保存一个自定义的多键值字符串，其中的键值对分割符为&，当然可以自定义一个分隔符，但用asp.net获取时是以&为分割符。
</li>

比如google的cookies:
<img src="/assets/img/cookies-sample.png" />

### 跨域请求（设认证信息存储在cookies中）
<p>
当一个资源从与该资源本身所在的服务器的域或端口不同的域或不同的端口请求一个资源时，资源会发起一个跨域 HTTP 请求。
</p>
<p>
比如，站点 http://domain-a.com 的某 HTML 页面通过 <img> 的 src 请求 http://domain-b.com/image.jpg。网络上的许多页面都会加载来自不同域的CSS样式表，图像和脚本等资源。
</p>
<p>
出于安全考虑，浏览器会限制从脚本内发起的跨域HTTP请求。例如，XMLHttpRequest 和 Fetch 遵循<a src="https://developer.mozilla.org/zh-CN/docs/Web/Security/Same-origin_policy">同源策略</a>。因此，使用 XMLHttpRequest或 Fetch 的Web应用程序只能将HTTP请求发送到其自己的域。为了改进Web应用程序，开发人员要求浏览器厂商允许跨域请求。% highlight javascript %}
</p>

## 解决跨域请求访问问题
# 1.CORS（跨域资源共享）
在<strong>服务器端</strong>配置CORS参数，允许跨域访问的origin url白名单。

# 2.反向代理（服务端）
<p>
反向代理（Reverse Proxy）方式是指以代理服务器来接受Internet上的连接请求，然后将请求转发给内部网络上的服务器；并将从服务器上得到的结果返回给Internet上请求连接的客户端，此时代理服务器对外就表现为一个服务器。
</p>
<p>
反向代理服务器对于客户端而言它就像是原始服务器，并且客户端不需要进行任何特别的设置。客户端向反向代理 的命名空间(name-space)中的内容发送普通请求，接着反向代理将判断向何处(原始服务器)转交请求，并将获得的内容返回给客户端，就像这些内容 原本就是它自己的一样。
</p>
<p>
load balance通过反向代理来做。
</p>

# 3.jsonp（客户端+服务端）
a) jsonp是利用get方法一般都是没有跨域请求限制这一点来做的，比如domain.com可以<script src="www.google.com/some/script.js" />来引入别的domain的js/img或者css资源。所以jsonp只支持http get方法.<br/>
b) jsonp要求在ajax请求中url?后加入key为callback，value为callback_function的参数。<br/>
c) 服务端返回的数据需要把json数据包装到callback_function里边。<br/>
比如:<br/>
服务器返回的数据是{ trans_count: 1000 }，那序列化返回给客户端的数据就是"callback_function({trans_count: 1000}"<br/>
最后客户端获取到数据之后就直接调用预先在客户端定义好的函数callback_function()处理{trans_count: 1000}。<br/>
{% highlight javascript %}
    $.ajax({
        url:"http://crossdomain.com/services.php",
        dataType:'jsonp',
        data:'',
        jsonp:'callback',
        success:function(result) {
            for(var i in result) {
                alert(i+":"+result[i]);//循环输出a:1,b:2,etc.
            }
        },
        timeout:3000
    });
{% endhighlight %}
<p>
jsonp来获取domainA的session_id，然后客户端用callback_function set cookie把，session_id设置到domainB的cookies里，
那跨域访问（Ajax/request）的时候，cookie就带着session_id信息，如果domainB和domainA使用同一个session系统，就能获取用户信息。
或者把用户名存放在cookie里。
</P>
