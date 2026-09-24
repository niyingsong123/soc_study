# UMC — 内存控制器

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

公开 AMD 资料使用 Unified Memory Controller [P1]。研究上游内存请求如何转化为存储器侧操作；目标设计的命名与边界待确认。

UMC 与 HBM 是控制器和存储器的关系，HBM 不归为 UMC 内部逻辑；PHY 在内存子系统中的父级需要集成图。

学习地址到通道/bank 的映射、调度、读写切换、刷新、时序与 ECC/RAS。具体支持项、位宽、频率和数量待资料。关联：[HBM](../HBM/README.md)、[PHY](../PHY/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：上游内存请求到命令、内存 PHY 和 HBM；先预读 HBM 最小命令/层级知识。下一项：第 1 轮：上游地址/请求与下游命令/返回约定。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MEM1](sources/MEM1-pg276-hbm-controller.md) → [MEM2](sources/MEM2-ramulator2-paper.md) → [MEM12](sources/MEM12-ramulator-hbm-controller.md) → [MEM13](../HBM/sources/MEM13-ramulator-hbm3-model.md)。覆盖：请求、映射与命令调度；PHY 交接与刷新/低功耗；错误、地址隔离与观测。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本批笔记与索引已建立，详细阅读与笔记完善仍有[待补项](../source-reading-audit.md)；不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
