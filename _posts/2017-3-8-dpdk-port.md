---
layout: post
title: DPDK 网卡接口
tags: DPDK,port,driver
datetime: 2017-3-8 14:53
---

{{ page.title }}
================
<a href="http://dpdk.org"><strong>DPDK</strong></a>
DPDK is a set of libraries and drivers for fast packet processing. It was designed to run on any processors. The first supported CPU was Intel x86 and it is now extended to IBM POWER and ARM. It runs mostly in Linux userland. A FreeBSD port is available for a subset of DPDK features.

# dpdk tool devbind.py

dpdk-devbind.py
用来绑定网卡驱动的工具

查看接口信息

> dpdk-devbind.py —status
> 0000:02:01.0 '82545EM Gigabit Ethernet Controller (Copper)' if=eth0 drv=e1000 unused=vfio-pci
> 0000:02:06.0 '82545EM Gigabit Ethernet Controller (Copper)' if=eth1 drv=e1000 unused=vfio-pci

0000:02:06.0 表示ID, drv=e1000 表示驱动, if=eth1 表示interface name

把id为000:02:06.0的设备(eth1)绑定到e1000驱动。

> dpdk-devbind.py -b igb_uio e1000 0000:02:06.0

解绑驱动

> dpdk-devbind.py -u dev_id


# 网卡接口/Port
dpdk programs只能识别dpdk驱动的网卡，所以需要先将网卡绑定dpdk驱动( igb_uio，vfio-pci，uio_pci_generic）这3种驱动都是用户态驱动，而不是内核态驱动。

虚拟机下vfio无法绑定网卡，原因未知。

# 手动insesrt igb_uio驱动
加载linux kernel的uio_pci_generic和uio模块

> modprobe uio_pci_generic
> modprobe uio

insert dpdk的igb_uio模块到kernel

> insmod $RTE_DPDK/build/kmod/igb_uio.ko

# 绑定网卡
使用dpdk tools dpdk-devbind.py可以查看网卡状态和绑定/解绑网卡驱动。

> dpdk-devbind.py -b <driver> <dev_id>

igb_uio driver目录
> /sys/bus/pci/drivers/igb_uio

绑定之后dpdk的接口就可以按照序号(0,1,2,..）取到网卡（dpdk的port）

比如：

> Network devices using DPDK-compatible driver
> "============================================"
> 0000:02:06.0 '82545EM Gigabit Ethernet Controller (Copper)' drv=igb_uio unused=uio_pci_generic

port 0 就是 0000:02:06.0这个设备，igb_uio没有eth0这种interface name