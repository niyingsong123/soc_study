# IO13：NBIO 7.9：多 AID doorbell、分区与 replay 计数

更新日期：2026-09-24。

导读：扩展 NBIF 到多实例/分区场景，解释 doorbell 的双层配置和 replay 指标的实际来源；适合与 NBIO 7.4 比较代际差异。
来源：[Linux v6.12 nbio_v7_9.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c)。
阅读状态：已读 SDMA/IH doorbell、aperture、partition 状态、初始化和 replay count；未系统阅读整个 RAS/电源路径。

## 目标身份不再只是 instance

SDMA 配置先取得逻辑/硬件实例映射和 aid_id，再按每 AID 实例数选择入口。写 doorbell range 的同时，还要配置 S2A 路径的 enable/range 等控制。IH 也有两类控制寄存器；仅改变 CPU 侧 offset 不一定完成内部路由配置。

与 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) 相比，7.9 的 SDMA use_doorbell=false 分支直接返回，不能从 7.4 的 size=0 行为推定其停用流程。状态清除可能由其他路径负责，需进一步查调用关系。

## 分区、初始化和观察量

compute partition 读取模式字段；memory partition 读取 NPS bitset 后用 ffs 返回模式位置，并可返回支持能力。原始 bitmask 与 API 整数不是同一编码。初始化根据 xcc_mask/aid_mask 设置 doorbell fence 和相关模式，表明不可见/未启用实例会影响控制可达性。

replay count 实际取 received/generated NAK 两个 16 位部分之和，APU 分支返回零。这是代码定义的观测值，不能无条件当作独立事务重发总数或 BER；还需确认计数器溢出、复位和采样间隔。

## 研究落点

为每条 host 控制路径列“软件实例→硬件实例→AID→range→目标”，并区分能力、配置、当前状态和统计。[FAB1](../../DF/sources/FAB1-cdna3-iod-memory.md) 提供多 die 系统背景但不能证明每个 NBIO 寄存器对应的物理布线。clock-gating 等空函数也只说明本驱动接口未操作，不证明硬件没有相关能力。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
