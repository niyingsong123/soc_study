# RSMU

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

保留 AMD RSMU 名称。AMD 作者的原始提交将其展开为 remote SMU，并说明寄存器接口、错误处理、复位生成等职责，见 [MG5](sources/MG5-rsmu-umc-index.md)。目标内部结构、实例及与 SMU 的包含关系仍待核实，暂独立管理。

首先核对目标与公开 v0.0.2 IP 的对应，再研究接口和状态；C01 的 BOWEN 图给出每组 MMHUB 的 SMN→rsmu 参考连接，不推广成 AMD 统一拓扑。

待补充框图、寄存器或微架构资料，确认和 SMU、SMN 及其他模块的接口。关联：[SMU](../SMU/README.md)、[SMN](../SMN/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 3 轮规划，详细论文轮次均待执行。

上下游场景：已确认公开 remote SMU 名称/职责和 UMC index-mode 调用；目标微架构、实例与 SMU 关系待资料。下一项：第 1 轮：目标身份与接口定位，再决定后两轮范围。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MG5](sources/MG5-rsmu-umc-index.md) → [C05](../HUBS/sources/C05-mmhub-dagb-ea.md)。覆盖：模块身份与直接寄存器证据；端点访问及错误状态；可访问性与恢复责任。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[MG5](sources/MG5-rsmu-umc-index.md)、[C01](../UTCL2/sources/C01-mm-utcl2-testbench.md)。从 AMD 作者说明确认 remote SMU 名称/职责，再结合公开 index-mode 与 BOWEN 参考连接；第一轮不再重复猜全称，重点改为目标映射和状态归属。
