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

本次资料扩充完成，不计为新的论文轮次；论文的下一项仍按上文实际进度执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
