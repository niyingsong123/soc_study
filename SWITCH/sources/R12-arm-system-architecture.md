# R12：Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层

更新日期：2026-09-24。

导读：提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。
来源：[Learn the architecture – Arm System Architectures，110303_0100_01_en，2025-05-19](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749)。
阅读状态：已读系统组件和接口章节，重点第 4 章 AMBA 分类、CHI-C2C、DTI/LTI 与 LPI；不把 Arm 组件名视为 AMD 一一等价模块。

## 用系统功能拆开搜索范围

一致性数据互联、非一致性/IO 数据、设备翻译、中断分发、寄存器控制和低功耗协调各有不同协议。CHI 面向 coherent interconnect，AXI 面向另一类高性能接入，APB/AHB 服务于不同复杂度和用途。资料还区分芯片内部 CHI 与 CHI-C2C 的 packetization/transport 边界，说明外连适配是独立设计问题。

这有助于 AMD 命名研究：UTCL2 可搜索 MMU/TLB/page walker/ATC；IH 可参考 interrupt controller 的事件与交付区分；SMU 可参考 power-management control interface。但不能据此断言 UTCL2 就是完整 SMMU、IH 就是 GIC 或 CF 就是 APB。

## 翻译不是全部通过数据端口隐式完成

DTI 支持查询并缓存翻译，DTI-ATS 面向带 ATS 的 PCIe root port，DTI-TBU 用于 SMMU 内部组件；LTI 则用于较短距离、无缓存的简化翻译查询。这些接口展示了 translation service 可以与数据传输分离，而缓存的存在会引入额外失效与生命周期责任。

这种分层可用于理解 [C03](../../UTCL2/sources/C03-utcl2-topology.md)/[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 的翻译 sideband，但协议名、身份键和完成语义仍必须以 AMD/目标资料为准。不能把 Arm 的 translation-buffer 分工硬套成 UTCL1/2 的数量或拓扑。

## 管理接口与资料限度

LPI 的 Q/P channel 面向时钟和电源协调；它提示研究 power-down 时要考虑请求停止、状态接受和资源 drain，而非只研究一个 clock-enable 位。具体握手状态、拒绝/恢复和时序需读对应规范；本入门资料不能证明任一 AMD SMU 实现。

该资料适合规划第一轮建立系统地图和扩展检索词；到了具体 feature 论证，应转入 [R8](../../SWITCH/sources/R8-axi-ordering-contract.md)、[VM10](../../UTCL2/sources/VM10-iommu-spec.md)、[MG1](../../SMU/sources/MG1-smu-message-table.md) 等更直接来源。避免用总览文章替代 transaction FSM、寄存器规范或 RTL 证据。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
