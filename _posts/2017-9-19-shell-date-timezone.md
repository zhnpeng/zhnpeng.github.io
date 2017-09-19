---
layout: post
title: linux shell date
tags: linux,shell, date, timezone, locale
datetime: 2017-9-19 11:50
---

{{ page.title }}
================

## 概述
用shell命令获取给定时区的今天凌晨的时间戳

<% highlight Bash shell scripts %>
# 取得纽约时区的日期（年-月-日）
today='TZ="America/New_York" date +%Y-%m-%d'
# "${today} 00:00" 的格式是 年-月-日 时：分
# +%s 参数是取时间戳
tsToday=$(TZ="America/New_York" date -d "${today} 00:00" +%s)
echo ${tsToday}
<% endhighlight %>
