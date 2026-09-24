# HBM — High Bandwidth Memory

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

高带宽内存主题 [P5]，不是 SoC 内存控制器的内部逻辑；为理解整个系统保留独立目录。

与 UMC、PHY 分开管理，实际 stack/channel 和控制器实例对应关系待确认。

学习 stack、channel、pseudo-channel、bank、容量与带宽、访问粒度和刷新。目标产品的代际、数量和接口参数等待资料。关联：[UMC](../UMC/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：UMC 经 PHY 发令，器件处理并返回；逻辑 channel/bank 与物理 stack 分开。下一项：第 1 轮：选择明确代际、建立逻辑与物理两种视图。

## 资料集与接续

资料集入口：[本模块来源主条目](../sources.md#mem9)；[资料集总入口](../sources.md)。覆盖本方案使用的公开材料与既有来源；建议阅读顺序：MEM1 → MEM9/MEM10 → MEM11 候选规范。内容简介、版本及已读范围集中维护在资料集中。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
