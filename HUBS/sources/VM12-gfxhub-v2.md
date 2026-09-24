# VM12：GFXHUB 2.0 与 MMHUB 的编程模型对照

更新日期：2026-09-24。

导读：用另一 hub 的公开实现对照页表根、地址 aperture、翻译 cache、context 与失效入口，帮助区分共享编程概念与真实物理归属。
来源：[gfxhub_v2_0.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c)。新增资料。
阅读状态：精读 setup_vm_pt_regs、init_gart/system_aperture、init_tlb/cache、setup_vmid_config、gart_enable/disable、init 的 hub 寄存器登记；未对全部字段做芯片手册核验。

## 相同框架不代表相同实例

GFXHUB 同样把页表根、VA 范围、system aperture、L1/VM L2 配置、context enable 和 invalidation 拆为函数。寄存器地址在 `amdgpu_vmhub` 中登记，使 GMC 的通用失效代码可按 hub 选用正确 req/ack/距离。抽象层一致可以减少驱动重复，但不能证明 GFXHUB 与 MMHUB 共用一个物理 TLB 或 walker。

对照 [VM2](../../HUBS/sources/VM2-mmhub-v2.md) 时先比较服务对象与寄存器命名，再比较字段条件，不把两个文件相似的初始化序列拼成一条串行数据流。客户端可以属于不同 hub；目标 UTCL2 与 hub 的具体归属仍需对应产品框图。

## 对配置的具体理解

aperture low/high/default、页表根、context 范围共同定义哪些地址走何种路径；使能翻译 cache 不等于数据 cache 一致。fault default/retry 等位影响异常响应，旧 context 应在 disable 时逐项关闭。重新 enable 的正确性还依赖页表和失效准备，不能只置一个 enable 位。

`init` 保存 context、engine 地址步长及 req/ack 等接口位置，这是运行时代码把“语义上的 hub”映射到寄存器的桥梁。进行跨 hub invalidate 时应检查这个表、启用 mask 和实际版本，而非假设所有 hub 的地址和数量相同。

## 后续复用

用于 HUBS 第 1–2 轮的边界与配置图、UTCL2 的多 hub 维护范围，以及 GC 与其他客户的服务分工。该文件未解释 CH，不补写 CH 的内部微架构。需要确定具体某块共享、旁路或实例数时继续核对 [C03](../../UTCL2/sources/C03-utcl2-topology.md)、[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 与目标版本材料。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
