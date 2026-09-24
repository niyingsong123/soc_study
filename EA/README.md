# EA — Efficiency Arbiter

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

MI200 文档使用 Efficiency Arbiter [P5]；gfx115x 文档另有 GCEA（Graphics Core Efficiency Arbiter），GL2 流量通过其继续访问内存系统 [P3]。

这些公开名称不证明本项目 EA 与某个 GCEA 实例相同。当前保留独立入口，具体宿主待确认。

学习多客户端仲裁、优先级、公平性、有效带宽、背压和返回路由。待补充框图与端口，确认和 GL2/HUBS/DF 的关系。关联：[GC](../GC/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：以 gfx115x GL2/GCEA 为公开参照；目标 EA 的客户端和内存侧接口待核实。下一项：第 1 轮：接纳、下发与返回三种完成边界。

## 资料集与接续

资料集入口：[本模块来源主条目](../sources.md#vm6)；[资料集总入口](../sources.md)。覆盖本方案使用的公开材料与既有来源；建议阅读顺序：P3/VM6 → 按需 VM5/P5。内容简介、版本及已读范围集中维护在资料集中。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
