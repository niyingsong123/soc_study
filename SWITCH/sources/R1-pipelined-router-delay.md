# R1：Peh/Dally：流水 router 延迟模型与推测分配

更新日期：2026-09-24。

导读：说明 router pipeline、VC 分配、switch 分配和 credit 往返如何共同决定零负载延迟与吞吐，适合审查“每跳一拍”和“增加 VC 必然更快”等简化假设。
来源：[A Delay Model and Speculative Architecture for Pipelined Routers，HPCA 2001](https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf)。
阅读状态：已读架构、模块依赖、延迟模型和实验结论，重点 §3–5；工艺延迟与论文结果只属于原实验配置。

## 基础结构与依赖

论文把 route compute、input buffer、VC allocation、switch allocation、crossbar 与 credit control 放入具体流水结构。VC 分配通常为包保留下一跳虚通道；switch 分配按 flit 竞争物理传输机会。包获得 VC 不代表每一拍都能通过 crossbar，也不代表下游总有空槽。

head 要完成路由与资源建立，body/tail 可继承已保存的 route/outVC，因此三类 flit 的关键路径不同。输入 VC 可以共享一个 crossbar 输入端口；多个 VC 同时 ready 仍要先竞争这个物理资源。只将 VC 数量乘上链路带宽会高估吞吐。

## 推测到底省掉哪段串行等待

常规流程先 VA 成功再做 SA；推测方案并行请求 VC 和 switch，假定 VA 会成功。只有两者均成功且其他发送条件成立才允许真正传输。失败时，已分出的 crossbar 机会可能浪费。论文优先保障非推测请求，避免推测请求妨碍已经获得资源的包；这不是任意 speculation 策略都无吞吐代价的证明。

研究实现时必须写出可回滚状态：推测 SA 成功但 VA 失败，是否曾扣 credit、弹出输入 FIFO、更新 RR 或分配 outVC？这些动作必须以最终有效传输为准，或者有完整恢复规则。不能只删除流水图中的 VA 方框。

## credit 路径必须显式建模

可用空槽信息经 credit 链路返回，在途 credit 使发送端看到的是延迟后的资源状态。需要的 buffering 与带宽×往返时间相关，还受到归还时点和处理流水影响；简单容量估算只可作为下界/初算，不是所有流控策略的精确公式。

论文通过逻辑/电气努力等方法估计各单元延迟，再按时钟周期切分流水，而不是把每个模块固定视为一拍。扩大 radix/VC 数会改变 allocator 和 crossbar 代价，不能同时免费获得更多资源与相同 cycle time。

## 如何用于当前方案

SWITCH 第 3–4 轮应以“资源依赖 → 时序可达性 → 推测/旁路 → 正确性检查”组织。比较方案时同时报告时钟周期、head latency、steady-state 吞吐、credit round-trip 和 buffer 配置。论文中的百分比增益不能直接作为 AMD switch 预测值。[R2](../../SWITCH/sources/R2-low-latency-vc-router.md) 进一步讨论预计算仲裁，[R3](../../SWITCH/sources/R3-booksim-method.md) 说明仿真如何避免意外看见本拍尚未生效的结果。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
