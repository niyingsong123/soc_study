# GC1：CDNA 2 的分片 L2、内存与互联边界

更新日期：2026-09-24。

导读：从 MI200 的公开整体结构理解 GCD 内 L2、内存控制器、HBM 和多种互联的分工。适合建立模块间地图与带宽层级；不提供内部队列或一致性状态机。
来源：[Introducing AMD CDNA 2 Architecture](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf)，17 页版本。
阅读状态：精读打印页 2、5–8 的架构/存储/通信，视觉核对 p.3 Fig.1a；计算指令章节不在本笔记范围。

## 空间结构和数据路径

MI250/MI250X 封装包含两个 GCD，MI210 为单 GCD 产品。一个 GCD 的 L2 由多个 slice 构成并供该 GCD 的资源共享；白皮书把每个 slice 与 memory controller 对应起来。p.3 同时画出计算阵列、L2/controllers、memory controller、memory PHY、Infinity Fabric 及外部接口：这足以区分缓存、控制器和 PHY，却不足以确认其间全部内部网络和队列。

p.5 的公开配置为每 GCD 8MB、32 个 slice、16 路组相联，每 slice 128B/clock 的 L2 读带宽。它也明确提到对分布式 L2 的排队和仲裁进行了增强，但没有给出算法。容量和聚合带宽需要始终携带“每 GCD/每封装”的范围。

L2 一侧提供命中后可反复复用的带宽，HBM 一侧提供填充与写回所需带宽；两者峰值不同并非矛盾。根据公开数值，32×128B 是每 GCD 每周期的理论聚合读出宽度；实际性能还取决于分片均衡、频率、命中、资源竞争和协议开销。该式只是量纲检查，不是实测吞吐。

## 原子与一致性的职责

部分 FP64 原子操作在 L2 附近执行，说明缓存研究必须包括读改写的串行化与原子可见性，不能只画 read miss/refill。白皮书没有提供原子队列、热点处理或 retry 协议。

CPU–GPU cache coherence 是特定优化 EPYC 平台和连接配置的能力。文中提及 GPU directory 跟踪与 CPU 共享的内存，并允许 CPU cache GPU memory。不能将这一能力推广到任何 PCIe 主机连接；p.8 明确讨论主机接口在不同连接对象下的 coherent IF 与普通 PCIe 非一致通信模式。

## 跨 die 和主机连接

资料区分封装内 GCD 间连接、封装间 GPU P2P、支持一致性的 host link、下游 PCIe root-complex 连接。讨论“带宽”前应先选定哪一种接口、单向或双向、单链路或聚合。一个物理/封装拓扑中存在多种路径，并不意味着每个内存请求依次穿过它们。

## 如何复用

GC 用它确定分布式缓存与原子研究位置；DF/SWITCH 用它区分目标归属和传输服务；UMC/HBM/PHY 用它区分缓存带宽、控制器与引脚带宽。精确缓存策略转 [GC3](../../GC/sources/GC3-llvm-memory-model.md)，CDNA 3 的 XCD/IOD 差异转 [FAB1](../../DF/sources/FAB1-cdna3-iod-memory.md)。目标 shaobo/anshi 的参数、真实 SWITCH 归属及协议仍待确认。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
