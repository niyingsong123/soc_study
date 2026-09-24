# R16：Remote Control：独立无死锁 chiplet 组合后的环路风险

更新日期：2026-09-24。

导读：解释多个内部无死锁网络连接后仍可能互相阻塞，以及出口整包缓冲预约如何切断跨 chiplet 依赖；用于规划 die-to-die 组合正确性。
来源：[Remote Control: A Simple Deadlock Avoidance Scheme for Modular System on Chip，arXiv:1910.04882v1](https://arxiv.org/pdf/1910.04882)。
阅读状态：已读动机、边界环路、RC buffer/注入控制和证明思路；未将仿真收益或缓冲规模移植为 AMD 参数。

## 组合为什么会产生新依赖

源 chiplet 的出站 packet 可占住内部 VC 并等待 interposer；来自另一 chiplet 的入站 packet 又可能被这些 VC 阻塞，最终形成跨边界循环。分别证明每个 chiplet 和 interposer 无死锁，不能覆盖新增连接和边界缓冲形成的资源边。

需要区分本地消费流与出站流，检查 tail 是否仍滞留在源网内；仅在边界给 head 一个空槽并不能保证整个 wormhole packet 从内部网络退出。

## RC 的核心契约

论文在边界 router 设置能容纳完整出站 packet 的 rc_buffer；源节点在注入出站包之前，先确保该边界缓冲有相应空间。这样即使外网暂时堵住，出站 packet 仍可完整进入边界缓冲，释放源 chiplet 的 VC，避免它永久阻塞入站/本地消费路径。

预约必须覆盖整包大小并受独立计数/控制管理；多个源不能同时把同一容量当可用。资格获得、包实际进入、buffer 被外网消费和 credit 返回是不同事件。多出口、可变包长、取消/复位都要求维持这一守恒关系。

## 证明前提和范围

该方法依赖各子网自身无死锁、目的地消费可前进，以及预约/边界控制不引入新环。它不是只要加一个 FIFO 就能解决所有协议死锁：响应生成、重放、ROB、功耗唤醒和管理通道仍可能增加资源依赖。

后续 SWITCH 第 5 轮应画包含端点/边界的依赖图，说明整包吸收点或其他断环机制，而不是仅检查 router XY turns。与 [R13](../../SWITCH/sources/R13-channel-dependency-scope.md) 的 CDG 原理、[R22](../../SWITCH/sources/R22-garnet-network-interface.md) 的终点 tail stall 和 [R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md) 的 D2D replay 缓冲联合使用。RC 只是可比较的一种行业方案，不预设目标 AMD 一定采用。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
