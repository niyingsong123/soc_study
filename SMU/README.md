# SMU — System Management Unit

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

公开 AMDGPU 资料将其描述为系统功耗管理控制器，涉及时钟、电压、温度和复位等管理 [P2]。目标芯片具体职责及固件接口待资料。

管理其他模块不等于包含它们；SMN 网络与 RSMU 的层级分别待确认，当前不纳入 SMU 子目录。

学习软件请求、硬件状态反馈、频率/电压协调、idle、时钟门控与复位。关联：[SMN](../SMN/README.md)、[RSMU](../RSMU/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：管理请求、固件/共享表、约束执行和反馈；不预设所有请求经 SMN。下一项：第 1 轮：一个 mailbox 请求与反馈。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MG1](sources/MG1-smu-message-table.md) → [MG2](sources/MG2-smu13-control.md) → [MG3](sources/MG3-smu13-firmware-abi.md)。覆盖：管理请求和共享表；策略约束与反馈；错误、事件和恢复。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。
