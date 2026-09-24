# SWITCH — 芯片互联

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

对应用户提出的“芯片互联（switch）”。**学习范围现已明确为片内 NoC 与封装内 die-to-die；但目标芯片的实际 SWITCH 拓扑、协议和 RTL 归属仍未确认。** 不把公开参考设计直接当作 shaobo/anshi 或某代 AMD 的实现。

暂独立管理；是否属于 DF、如何连接 CAKE、使用哪类 PHY，仍需目标协议与拓扑资料确认。关联：[DF](../DF/README.md)、[PHY](../PHY/README.md)。

## 已有公开技术研究

用户指定的研究正文保存在小写 `switch/`；本大写目录继续作为 SoC 模块入口。当前不合并、移动或重命名两个目录。

- [完整微架构研究稿](../switch/switch_detailed_guide.md)：系统、包格式、NI、Router、D2D、延迟和 SDMA；第二轮核心为第 38—49 章。
- [六问简化版](../switch/switch_quick_guide.md)：为什么需要、功能、上下游/流向、关键参数、SDMA 关联及软硬件协同。
- [研究轮次与执行证据](../switch/RESEARCH_PROGRESS.md)：第一、二轮完成，第三至第六轮待研究。
- [第二轮有限缓冲模型](../switch/examples/router_round2.py)与[实际测试报告](../switch/examples/round2_results.json)：教学模型，不是 RTL 或协议合规验证。

第一轮完整原稿以[历史快照](../switch/switch_detailed_guide_v2.0.md)保留。当前稿将其主线重整并加入第二轮下钻内容；历史稿不再作为另一套并行设计维护。

更新日期：2026-09-24。学习内容覆盖端口、路由、VC/VN、VA/SA、credit、buffer、失败路径、死锁依赖、ordering 与完成点；实际目标模块是否具备这些功能仍由目标资料决定。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。本次已复核后续方案；实际研究第 1、2 轮已完成，第 3–6 轮待执行。

上下游场景：从客户端/DF 事务需求研究 NI、Router、D2D 的输运责任，协议与目标拓扑待核实。下一项：修订后的第 3 轮：NI 事务契约、排序与协议映射。

## 资料集与接续

资料集入口：[本模块来源主条目](../sources.md#p6switch-公开研究资料组)；[资料集总入口](../sources.md)。覆盖本方案使用的公开材料与既有来源；建议阅读顺序：P6 中既有 R1–R21 → 本次补充阅读 → 按需 FAB1。内容简介、版本及已读范围集中维护在资料集中。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
