# HBM — High Bandwidth Memory

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

高带宽内存主题 [P5]，不是 SoC 内存控制器的内部逻辑；为理解整个系统保留独立目录。

与 UMC、PHY 分开管理，实际 stack/channel 和控制器实例对应关系待确认。

学习 stack、channel、pseudo-channel、bank、容量与带宽、访问粒度和刷新。目标产品的代际、数量和接口参数等待资料。关联：[UMC](../UMC/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：UMC 经 PHY 发令，器件处理并返回；逻辑 channel/bank 与物理 stack 分开。下一项：第 1 轮：选择明确代际的接口参考，建立逻辑资源图与读写闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md) → [MEM13](sources/MEM13-ramulator-hbm3-model.md) → [MEM11](sources/MEM11-jedec-scope-gap.md)。覆盖：接口层级与共享资源、命令约束、维护恢复及持续性能；MEM9/MEM10 仅作按需数量级参考。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[MEM11](sources/MEM11-jedec-scope-gap.md)、[MEM9](sources/MEM9-micron-hbm3e.md)、[MEM10](sources/MEM10-samsung-hbm3.md)。MEM11 已从纯入口推进到 JESD238A 正文转录选读，支持 PC、共享命令与 CK/DQS 的架构分解；相关规范图表按研究问题继续核验；具体料号 datasheet 未取得，但按 U23 不再列为必补项。

## 当前研究重点（U23，2026-09-25）

以可见接口行为为中心：逻辑层级及共享资源、命令与数据、行冲突、刷新及恢复、错误边界。器件内部只保留解释这些行为所需的内容，厂商数据表降为可选背景。 统一范围与运用标准见 [项目上下文](../project-context.md#hbm-接口研究范围)。缺少厂商器件数据表不阻塞主线；实际未读状态仍保留。
