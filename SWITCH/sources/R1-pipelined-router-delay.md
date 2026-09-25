# R1：Peh/Dally：流水 router 延迟模型与推测分配

更新日期：2026-09-25。

导读：保存 router 级划分与逻辑努力公式、FO4 对照、8×8 mesh 实验配置及不同 buffer/VC 的结果；适合比较周期、吞吐和 credit 周转，所有数值保留原工艺与工作负载。
来源：[A Delay Model and Speculative Architecture for Pipelined Routers，HPCA 2001](https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf)。
阅读状态：补核 §3–5，包含 PDF 第 5 页公式、第 8 页 Table 1 原图和仿真方法/结果；未重跑综合与仿真。

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

## 延迟模型：怎样从组合模块形成流水级

原文 §4、PDF 第 5 页式 (1) 将不可再分的组合模块延迟记为 `t_i`，该模块处切断流水所需的优先级更新、恢复等开销记为 `h_i`。从模块 a 到 b 的一级需要满足 `Σ(i=a..b)t_i+h_b≤clk`；不能再向右合并时，`Σ(i=a..b+1)t_i+h_(b+1)>clk`，相应向左扩展也超出周期。重点不是“每个方框一拍”，而是只有合法的切断位置才可以形成新一级。拆开仲裁器还必须处理跨拍的请求、grant 与状态更新。

式 (2) 用逻辑努力估计门级路径：`T/τ=Σ(g_i·e_i)+Σp_i`，分别为逻辑努力、电气努力和寄生延迟。本笔记把电气努力改记 e，避免与上一式的切断开销 h 混淆；τ 是该模型的工艺延迟单位，FO4 反相器延迟 `τ4=5τ`。因此下表中的 τ4 不能直接当作当前节点的皮秒数。

Table 1 的代表性式子：物理端口数为 p、每端口 VC 数为 v；wormhole switch allocator 的组合延迟是 `(21.5·log4(p)+14+1/12)τ`，切断开销为 `9τ`；R→v VC allocator 则将对数项换成 `log4(pv)`，同样有 `9τ` 开销。这里对数底数是 4。例如 p=5 时前者加开销后约为 `9.61τ4`，与表中的 9.6 一致。此算例是复核公式，不是重新综合。R→p、R→pv 等不同请求连接结构改变仲裁扇入，不能把这些式子只按模块名称互换。

| Table 1 配置 p=5、w=32、v=2 | 模型，τ4 | Synopsys，τ4 |
| --- | ---: | ---: |
| wormhole switch allocator | 9.6 | 9.9 |
| crossbar | 8.4 | 10.5 |
| R→v VC allocator | 11.8 | 11.0 |
| R→p VC allocator | 13.1 | 13.3 |
| R→pv VC allocator | 16.9 | 15.3 |
| VC switch allocator | 10.9 | 12.0 |

这张表对照的是原文 0.18 μm 实现与近似模型，不是现代 AMD 的实测。原设置 `τ4=90 ps`、`clk=20τ4`；表中工具结果也说明简单模型存在误差。比较流水设计时应同时保留 cycle time 与 cycle 数，否则把更多级的高频设计与低频少级设计按周期直接比较会失真。

## 实验方法和可以带条件引用的结果

§5 使用 Verilog 模型、8×8 mesh、均匀随机目的地、维序路由、credit 流控与固定 5-flit 包。预热 10,000 cycles，随后统计 100,000 个包并排空已采样包。延迟从第一个 flit 生成算到 tail 离开网络，**包括源端等待**；目的端假设立即接收，因此不能据此排除真实 endpoint 背压。

| 每输入总缓冲 | wormhole | 非推测 VC | 推测 VC |
| --- | --- | --- | --- |
| 8 flits | 3 级；零负载 29 cycles；饱和约 40% | 2 VC×4；4 级；36 cycles；约 50% | 2 VC×4；3 级；30 cycles；约 55% |
| 16 flits | 29 cycles；约 50% | 2 VC×8；35 cycles；约 65% | 2 VC×8；29 cycles；约 70% |

百分比是论文该流量模型下的吞吐归一化口径，不能改写成任意工作负载的利用率保证。第二行 70% 对 50% 是相对提高 40%，不是提高 40 个百分点。另一个 4 VC×4 配置中，推测和非推测 VC 都约在 70% 饱和：足够覆盖 credit 往返后，减少一级流水仍可改善延迟，却未必继续提高饱和吞吐。由此应分别研究资源数量、资源周转时间和仲裁关键路径。

本次补核了公式页、Table 1 原图及 §5 文字；未重跑综合/仿真，也未从曲线推造额外精度。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
