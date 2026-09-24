# GC — GL2 / GRBM / RLC 的上级归档入口

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

GC（Graphics and Compute）将用户已列出的图形/计算域模块放在同一上级入口，本次不扩展其他 GC 子模块，也不建立 GL2、GRBM、RLC 子目录。

GL2：公开 gfx115x 的 GFX 数据缓存，不同于 UTCL2 [P3]。

GRBM：Graphics Register Bus Manager，按用户纠正的名称管理 [U2、P4]。

RLC：公开 AMDGPU 资料明确列为 GC 内部微控制器 [P2]。

学习 GL2 命中/miss、写回和带宽；GRBM 寄存器访问、实例选择及活动统计；RLC 控制与固件交互。公开归档依据不证明目标芯片直接父实例都叫 GC，也不证明三者相互包含。EA 独立保留，等待目标 GC/EA 框图。关联：[EA](../EA/README.md)。

## 资料集与接续

资料集入口：[资料集与来源总入口](../sources.md)。按本模块主题查看来源简介、相关研究问题和实际阅读定位；条目随后续阅读补充。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
