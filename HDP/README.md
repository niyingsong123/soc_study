# HDP

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

以主机数据访问为学习主题保留入口；本项目全称、职责边界与父级等待规格确认。

与 PCIe、NBIF、内存侧的关系待确认，不先画为嵌套关系。

学习问题：主机访问设备内存经过哪里，窗口、缓冲、flush 和可见性由谁负责，与 SDMA 如何配合。这些是阅读方向，不是已实现功能清单。关联：[PCIe](../PCIE/README.md)、[NBIF](../NBIF/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：主机窗口到内存侧的数据与维护路径；flush/invalidate 的完成范围分别核实。下一项：第 1 轮：目标代际、地址语义及读写闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[IO7](sources/IO7-bkdg-hdp-history.md) → [IO5](../NBIF/sources/IO5-nbio74-host-bridge.md) → [IO6](sources/IO6-hdp40-maintenance.md)。覆盖：历史职责与现代接口；维护与可见性闭环；低功耗、RAS 和代际差异。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本批笔记与索引已建立，详细阅读与笔记完善仍有[待补项](../source-reading-audit.md)；不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
