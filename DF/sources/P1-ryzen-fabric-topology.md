# P1：AMD GDC 2019：CCM、CS、CAKE 与本地/远端访存路径

更新日期：2026-09-24。

导读：提供 CS、CAKE 等 AMD 名称的官方出处，并用本地 DRAM、同 die 其他 CCX、远端 die DRAM 三条路径说明一致性端点与传输层的分工；历史性能数字不可外推。
来源：[AMD Ryzen Processor Software Optimization，GDC 2019](https://gpuopen.com/gdc-presentations/2019/gdc-2019-s2-amd-ryzen-processor-software-optimization.pdf)，重点第 20–23 页。
阅读状态：已读取 PDF 的 cache/NUMA/本地及远端 refill 相关页；软件优化、编译器和核心流水线部分不是本笔记覆盖重点。

## 官方命名与边界

第 21 页解释 CCM 为 Cache-Coherent Master，CS 为 Coherent Slave，CAKE 为 Coherent AMD socKet Extender，UMC 为 Unified Memory Controller；IFOP/IFIS 分别表示封装内/插座间 SerDes。这里的 CS 属于一致性存储侧角色，不能与计数器文档中的其他 CS 缩写混用；CAKE 是扩展一致性连接的端点，不能仅凭名字等同于任意 packet switch。

CPU CCX 经 CCM 接入 SDF transport layer；本地内存经 CS、UMC 到 DDR4；离开 die 的连接经 CAKE 与 SerDes。于是必须区分事务的一致性语义、transport 的路由/流控、物理链路传输和 DRAM 调度。一个模块可以参与多个层面，但图中分块不能被一句“Infinity Fabric 搬运数据”抹平。

## 三条路径与定位价值

本地 DRAM refill 路径在本 die 的存储端结束；来自另一 CCX 的 line 可能通过一致性路径取得，不一定访问 DRAM；远端 DRAM 路径额外跨越两端 CAKE 和 die 间链路。地址在远端内存、数据被远端 cache 持有、当前请求由哪个 master 发出，是不同维度。

第 20 页介绍该代 L3 与 L2 victim、tag 副本和 probe filtering 的关系，说明“数据 cache”和“用于判断是否需要 snoop 的目录信息”不能混为同一份数据。该 CPU 结构只能作为理解一致性端点的参考，不能直接替代 GPU GL2 或 MI300 IOD 的结构。

资料中的 near/far 延迟和带宽有处理器、DDR4-3200、BIOS/系统等测试条件，而且不同平台页的 die-to-die 数字不同。保留其定性结论：距离和经过的服务点会影响延迟/带宽；不把 2019 年测试值写入当前目标参数表。

## 后续使用

DF 论文先列 master、home/memory-side、外连端点与 transport，再研究路由、credit、ordering、snoop/response；SWITCH 研究 transport 内部资源，PHY 研究链路，UMC 研究命令服务。跨模块链路必须标清哪些结构由本资料直接证明、哪些仅是研究模型。新一代 GPU 的 memory-side cache 与 XCD/IOD 拆分见 [FAB1](../../DF/sources/FAB1-cdna3-iod-memory.md)，软件可见的 interleave 与 hash 见 [FAB2](../../DF/sources/FAB2-df36-registers-counters.md)/[FAB3](../../DF/sources/FAB3-atl-address-core.md)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
