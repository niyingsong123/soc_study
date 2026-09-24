# EA — Efficiency Arbiter

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

MI200 文档使用 Efficiency Arbiter [P5]；gfx115x 文档另有 GCEA（Graphics Core Efficiency Arbiter），GL2 流量通过其继续访问内存系统 [P3]。

这些公开名称不证明本项目 EA 与某个 GCEA 实例相同。当前保留独立入口，具体宿主待确认。

学习多客户端仲裁、优先级、公平性、有效带宽、背压和返回路由。待补充框图与端口，确认和 GL2/HUBS/DF 的关系。关联：[GC](../GC/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：以 gfx115x GL2/GCEA 为公开参照；目标 EA 的客户端和内存侧接口待核实。下一项：第 1 轮：接纳、下发与返回三种完成边界。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[P3](../GC/sources/P3-gl2-metrics.md) → [P5](../GC/sources/P5-mi200-counters.md) → [VM6](sources/VM6-gcea-metrics.md) → [C05](../HUBS/sources/C05-mmhub-dagb-ea.md)。覆盖：请求接入与下游服务；共享存储、bank/group 与资格；返回、维护与性能解释。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本次资料扩充完成，不计为新的论文轮次；论文的下一项仍按上文实际进度执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
