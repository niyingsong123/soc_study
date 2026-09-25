# R9：CHI Protocol Bundle 用户指南：模型接口与 credit 回调

更新日期：2026-09-25。

导读：这是 Arm SoC Designer 仿真组件指南，展示 CHI 通道、模型转换器和回调如何接线；可用于理解模型边界，不能作为 CHI 一致性事务规范。
来源：[Arm DUI 0954C，SoC Designer Plus 9.0.0 AMBA CHI Protocol Bundle User Guide，2016](https://documentation-service.arm.com/static/5ed104c1ca06a95ce53f8869)。
阅读状态：已核对封面及 §6–8 的模型、端口、参数与 API；纠正旧入口可能造成的“CHI 协议规范”误解。

## 资料实际提供什么

组件包括 CHI↔AXI 转换、CHI-to-CHI、stub，以及事务/信号接口之间的适配。参数定义模型接受的数据宽度、protocol variant 和 cluster 配置。例如转换器要求 AXI 宽度不超过所配置 CHI 宽度；这是该组件的限制，不能解释成整个 CHI/AXI 标准的通用组合规则。

REQ、RSP、SNP、DAT 在 API 中分别有发送/接收方法，字段包含 QoS、TgtID、SrcID、TxnID、opcode 和数据标识等。学习价值是看到请求、响应、snoop、data 为不同消息通道，路由目的地与事务匹配身份也不同；具体位宽来自该模型版本，不能用来重建最新 CHI flit。

## credit 与事件接口

驱动事务的 callbacks 和 reverse LCRDV notification 分开，接收方通过相应方法更新 link credit。实现模型时，发送事件、接收事件和 credit 归还都要有时间/接口边界。一个 callback 被调用并不表示完整 coherence transaction 结束，信用只是接收资源许可。

debug/transaction bridge 可提供快速访问或辅助观察，但可能绕过正常周期/协议流；性能统计不能把 debug 路径的行为当作运行时数据路径。stub 脚本能生成事务，也不代表模型自动覆盖合法事务间依赖。

## 如何引用及何时回原文

本资料适用于方案中的“仿真组件怎样建模和连接”，不用于声称某 opcode 的 completion/snoop/ownership 规则。后续若需要事务状态机，应取得明确版本的 IHI0050 等正式规范；本指南未提供足够证据时保留未知。[R12](../../SWITCH/sources/R12-arm-system-architecture.md) 用于系统层概念，[R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md)/[R11](../../SWITCH/sources/R11-ucie11-streaming.md) 用于 D2D 承载对照，均不可把 CHI 名称直接替换成 AMD DF。

正式事务与链路规则已另建 [R23：CHI E.a 原始规范选读](R23-chi-ea-protocol.md)。本篇保留原资料身份，不能因新增规范而把模型/介绍的阅读记录改成规范精读。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
