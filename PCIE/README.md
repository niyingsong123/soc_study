# PCIe — PCI Express

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

主机/设备互联学习入口。当前没有本项目协议版本、端口角色或控制器规格。

协议分层与 RTL 分块分别描述；PHY 可作为物理层实例，NBIF/HDP 是否包含在某个 PCIe 子系统中则需框图。

学习配置空间与 BAR、事务请求/completion、posted/non-posted、流控/保序、MSI/MSI-X，再结合 SDMA 理解主机与设备访问。关联：[NBIF](../NBIF/README.md)、[HDP](../HDP/README.md)、[PHY](../PHY/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：分别研究 CPU BAR/MMIO 与 GPU DMA；PCIe、NBIF、HDP 学习顺序不证明串行拓扑。下一项：第 1 轮：端口角色、地址类型及读写基本闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[IO1](sources/IO1-pg213-transactions.md) → [IO2](../HDP/sources/IO2-linux-device-io.md) → [IO3](sources/IO3-linux-dma-api.md) → [IO4](sources/IO4-base-spec-gap.md)。覆盖：BAR/DMA 与请求完成；有限资源、保序与翻译扩展；通知、链路和恢复。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[IO4](sources/IO4-base-spec-gap.md)、[VM10](../UTCL2/sources/VM10-iommu-spec.md)。Base 5.0 官方下载本次要求会员登录，保留规范待补；AMD IOMMU 的 PRI/PPR 完成和溢出规则已补，可联读 IO11，但不能替 PCIe Base 的线协议规则。
