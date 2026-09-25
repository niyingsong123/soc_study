# GC — GL2 / GRBM / RLC 的上级归档入口

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

GC（Graphics and Compute）将用户已列出的图形/计算域模块放在同一上级入口，本次不扩展其他 GC 子模块，也不建立 GL2、GRBM、RLC 子目录。

GL2：公开 gfx115x 的 GFX 数据缓存，不同于 UTCL2 [P3]。

GRBM：Graphics Register Bus Manager，按用户纠正的名称管理 [U2、P4]。

RLC：公开 AMDGPU 资料明确列为 GC 内部微控制器 [P2]。

学习 GL2 命中/miss、写回和带宽；GRBM 寄存器访问、实例选择及活动统计；RLC 控制与固件交互。公开归档依据不证明目标芯片直接父实例都叫 GC，也不证明三者相互包含。EA 独立保留，等待目标 GC/EA 框图。关联：[EA](../EA/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：GL2 的缓存侧请求与返回；GRBM/RLC 另走配置和控制支路，实际翻译及下游接口待目标核实。下一项：第 1 轮：确定参考代际、输入地址类型与基本命中/miss 闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[P2](sources/P2-amdgpu-hardware.md) → [GC1](sources/GC1-cdna2-memory.md) → [P3](sources/P3-gl2-metrics.md) → [P5](sources/P5-mi200-counters.md)。覆盖：存储层次与 GL2 请求边界；GRBM/RLC 的选择状态与恢复；可见性与性能解释。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[R23](../SWITCH/sources/R23-chi-ea-protocol.md)。比较缓存状态、所有权、写回责任和 CompAck 的行业语义；SC 不等于主存必定最新。仍仅研究 GL2/GRBM/RLC，目标协议需 AMD 证据。

## HBM 地址映射专题接续（U24）

[专题方案与逐层分工](../HBM/address-interleaving-plan.md) · [本模块具体落点](research-plan.md#u24请求地址到-hbm-bank-的跨模块落点)。从 GL2 的实际输入与下游请求粒度出发，分清 cache slice/set/bank 与 HBM bank；核对 cache 命中、旁路/写回、请求合并拆分及进入内存侧的地址。继续只研究 GL2、GRBM、RLC，源端其他引擎只作接口边界。 先读取现有资料索引，专题例子跨模块共用，实际连接与参数保留证据边界。
