# NBIF

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

保留用户提供的名称；尚无本项目规格，不自动改名 NBIO，也不强行展开缩写。

与 PCIe、HDP 的接口和父子层级待确认，当前独立管理。

学习问题：主机侧与 SoC 内部如何对接，是否承担地址窗口、doorbell、路由、流控或虚拟化。上述是阅读问题，不是已确认功能。关联：[PCIe](../PCIE/README.md)、[HDP](../HDP/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：主机窗口、目标交付及维护协作；NBIO 是相关资料入口，目标覆盖关系待查。下一项：第 1 轮：目标名称、端口与窗口职责。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[IO5](sources/IO5-nbio74-host-bridge.md) → [IO13](sources/IO13-nbio79-partition-doorbell.md) → [IO3](../PCIE/sources/IO3-linux-dma-api.md)。覆盖：窗口、目标和实例；主机交付与维护连接；事件、分区与异常。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本次资料扩充完成，不计为新的论文轮次；论文的下一项仍按上文实际进度执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
