# HBM — High Bandwidth Memory

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

高带宽内存主题 [P5]，不是 SoC 内存控制器的内部逻辑；为理解整个系统保留独立目录。

与 UMC、PHY 分开管理，实际 stack/channel 和控制器实例对应关系待确认。

学习 stack、channel、pseudo-channel、bank、容量与带宽、访问粒度和刷新。目标产品的代际、数量和接口参数等待资料。关联：[UMC](../UMC/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：UMC 经 PHY 发令，器件处理并返回；逻辑 channel/bank 与物理 stack 分开。下一项：第 1 轮：选择明确代际、建立逻辑与物理两种视图。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MEM9](sources/MEM9-micron-hbm3e.md) → [MEM10](sources/MEM10-samsung-hbm3.md) → [MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md)。覆盖：器件组织与数量级；命令、时序和维护；保护域与持续性能。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本次资料扩充完成，不计为新的论文轮次；论文的下一项仍按上文实际进度执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
