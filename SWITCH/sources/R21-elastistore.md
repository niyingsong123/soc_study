# R21：ElastiStore：每 VC 槽位与共享弹性缓冲的取舍

更新日期：2026-09-24。

导读：解释 ready/valid 反压流水为何需要额外吸收空间，以及 ElastiStore 用 V+1 个槽替代 2V 个槽时的结构和明确吞吐例外。
来源：[ElastiStore: An Elastic Buffer Architecture for Network-on-Chip Routers，DATE 2014](https://gdimitrak.github.io/papers/date14a.pdf)。
阅读状态：已读 §II–V 的 elastic protocol、共享辅助槽、控制和 router 集成，以及论文明确列出的最坏阻塞情况。

## 普通 elastic buffer 的容量原因

valid/ready 同时成立才发生一次 transfer。反压经过寄存阶段逐拍向上游传播，在停止信息到达之前仍可能有一份已允许发送的数据到来，因此传统两槽 EB 存一份被堵数据和一份额外吸收数据。该需求由实际 ready 延迟决定，不能把所有寄存切分都压成一个无条件单槽。

多 VC 需要独立 valid/ready 和资格状态，发送仲裁选择有数据且下游可接的 VC。只有一个 physical datapath，因此每拍最多一 VC 传数据；多个 ready 可同时为真，不等于多份数据同时传输。

## ElastiStore 的共享辅助槽

基准为每 VC 两槽，共 2V；改进为每 VC 一槽，加一个由各 VC 动态共享的辅助槽，共 V+1。多个活跃 VC 分摊物理链路时，通常每 VC 只需较低发送频率；单个独占流可借辅助槽保持连续吞吐。

论文明确有例外：除一个 VC 外其余都被堵，且辅助槽被堵塞 VC 占用时，唯一活跃 VC 实际只有一槽，吞吐可降至 50%，而每 VC 两槽方案可维持满速。不能只引用摘要中的性能接近就删掉这个条件。共享节省的是 V−1 个槽，不保证任何流量下无代价。

## 实现与使用范围

控制维护各 VC 的 EMPTY/HALF/FULL 类状态及共享辅助槽归属，组合 mux、寄存使能、ready 计算和输出仲裁协同。可用触发器或 latch 实现，但时钟相位/透明窗口与时序约束不同，不能仅凭容量相同互换。

本资料适合比较 router/link pipeline 的面积、隔离和吞吐；与 [R19](../../SWITCH/sources/R19-booksim-buffer-state.md) 的大型共享池不是同一机制。PHY/CDC 研究可借它理解缓冲吸收，但 EB 本身不是跨异步时钟域的完整安全方案。后续应保留全堵/单活跃 VC、反压传播和共享槽释放场景。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
