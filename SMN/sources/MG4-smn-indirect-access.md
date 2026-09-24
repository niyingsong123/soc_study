# MG4：AMD SMN：index/data 访问与错误判定

更新日期：2026-09-24。

导读：解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。
来源：[Linux v6.12 arch/x86/kernel/amd_nb.c](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c)，amd_smn_read/write 与公共内部函数。
阅读状态：已读 SMN 访问函数及其完整错误语义注释；不是 GPU 所有 SMN 接入路径的统一规格。

## 访问序列

先检查 node 是否存在、获得对应 root PCI device，持 smn_mutex 后写 config offset 0x60 选择 SMN 地址，再在 0x64 读写数据。锁必须覆盖两步，否则另一个线程可以在选择和数据访问之间替换地址。node 选择与内部 register address 是两层身份。

这一实现是 host 通过 PCI 配置窗口访问 SMN 的实例。不能据此声称 SMN 只能这样访问，也不能把 0x60/0x64 当成所有 GPU 的固定寄存器接口。

## 成功的层次

PCI 层错误可返回 errno，全 1 等可能错误响应会被额外识别；但合法零与 Read-as-Zero 无法由通用函数区分。写后读回也不能统一比较相等，因为 W1C、写忽略、保留位等有各自语义。调用者必须按具体寄存器判断目标效果。

因此返回成功只覆盖该访问路径知道的错误，不代表内部受控硬件已执行完毕。连续读零不能直接证明目标空闲；复位/低功耗造成不可达时尤其需要确认寄存器定义。

## 微架构研究落点

SMN 先研究入口、地址空间、目标选择、共享访问资源、响应和错误，再扩到可能的多 die 路由、背压与电源域。后几项在本文件没有证据。[IO10](../../CF/sources/IO10-gfx90-register-control.md) 的 GRBM index 锁提供另一种控制访问模式，[MG10](../../SMN/sources/MG10-atl-system-identity.md) 说明系统身份字段为何依代际变化，二者都不应改名成 SMN 的内部模块。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
