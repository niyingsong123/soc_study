# R7：FlooNoC 论文：宽物理网络、AXI 并发流与端点重排

更新日期：2026-09-25。

导读：说明宽链路 NoC 如何把 AXI 排序放在 NI、用响应存储预约保证可接收，并比较带 ROB 与限制同 ID 目标的两种设计；适合作为 AMD switch 的行业对照。
来源：[FlooNoC，arXiv:2409.17606v1](https://arxiv.org/html/2409.17606v1)，2024-09-26。
阅读状态：已读 §II–VI，重点 NI ordering、physical links、router、集成/物理实现；性能数字不作为 AMD 目标指标。

## 端点承担事务语义

AXI 同一 TxnID 的响应需保持规定顺序，而不同目标有不同延迟。带 ROB 的 NI 在请求被接受、注入 NoC 之前分配响应空间与 robIDx，维护 reorder table；响应到达时若可按序交付可直接旁路，否则写对应 ROB。只有响应真正交给 AXI 后才移除相应记录。

这使“网络能继续路由”与“端点一定能接响应”相连。按请求数预留固定一个槽仍可能不足以接长 burst，实际空间单位与响应大小必须对齐。论文还通过同 ID 首响应和确定性同目标路径等条件减少不必要预留；这些优化有顺序假设，不能无条件沿用。

无 ROB 方案则按 TxnID 保存 outstanding 计数和目标，旧请求未完成前限制同 ID 切换目的地。它用注入限制换响应存储，代价是可能阻塞可并行事务；若软件/上游能用不同 TxnID 区分独立流，可降低这一代价。

## 通道组织与 router 简化

论文采用窄 request/response 与宽 data 物理链接，header 与 payload 并行传输，减少宽数据被额外 head/tail flit 稀释的效率损失。请求/响应分开承担隔离；router 不处理完整 AXI transaction 排序，采用小输入缓冲和可选输出缓冲以适应布线时序。

W burst 等需要防止跨事务交织，可使用按 flit 标识的 wormhole 锁定。这里“单 flit 装下一个 beat”不等于整个 burst 单拍结束；packet/beat/burst 的单位应分开。

## CF round 1 reuse check (2026-09-25)

Revisited the original v1 HTML, especially III-A1/A2 and III-B, while drafting CF. Reconfirmed the NI ordering alternatives and the role of separate request/response paths. No new performance experiment or source figure review was performed. CF uses this as a public comparison, not as target topology or a general deadlock proof.

## 性能与可移植性

宽线降低序列化和高频需求，但占用 routing metal、buffer/repeater 与宏块周边资源。论文在具体 SoC 与工艺布局中评价，不支持“现代 NoC 都应弃用 VC”的普遍结论。AMD 的一致性消息类别、die-to-die 宽度限制和 PHY 可靠性可能需要不同组织。

后续方案应比较重排存储、ID 限制、独立物理网络和 VC 方案的面积/并发/死锁依赖，不只比较 wire width。代码版本 [R15](../../SWITCH/sources/R15-floonoc-router-code.md) 已演进出新功能，不能将其每一分支当成本文 2024 实验实现。

## 第三轮复用时的边界

本次回查原论文 §III-A、§III-A1/2，确认 response 空间预约、reorder table 移除及同 ID 目标限制的职责。论文以确定性路由和同目标响应顺序作为优化条件；迁移到多 VC、不同 target issue 或 response scheduler 后，必须重新证明完整路径上的顺序，不能只保留“XY”这个名称。

R0 第三轮采用更保守的单 domain 单笔在途，其他 domain 有限并发，并为每笔读预约完整 response slot。该 slot 是返回落点，不包含同 ID 多笔按 sequence 提交的 ROB。FlooNoC 的 RoB-less 表示省去重排结构，不等于整个 NI、网络或消费者完全无 buffer；本文也不直接套用论文首响应免预约的优化。比较落点见[NI ordering](../../switch/switch_detailed_guide.md#65-ordering先把需要保持的顺序定义清楚)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
