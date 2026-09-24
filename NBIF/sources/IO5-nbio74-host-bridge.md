# IO5：NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口

更新日期：2026-09-24。

导读：提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。
来源：[Linux v6.12 nbio_v7_4.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c)、[amdgpu_nbio.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h)。
阅读状态：已读所列窗口、doorbell、HDP、IH 函数、无 BIF ring 的 RAS controller 中断路径及公共接口表；未通读 ASPM/RAS 全分支，NBIF 与 NBIO 仅作功能对照。

## 分开的访问入口

`mc_access_enable` 控制 framebuffer 读写入口，doorbell aperture 则控制通知窗口。self-ring aperture 配置基址与模式；SDMA 和 IH 分别配置 doorbell offset/size。能访问 framebuffer 不代表 doorbell 路由已正确配置，反之亦然。

SDMA 实例寄存器地址不是简单连续数组，超过前两个实例有偏移，ALDEBARAN 的特定实例还需额外调整。这说明“instance id→寄存器地址→目标引擎”必须留有代际映射，不能按名字后缀直接推导物理位置。关闭某 range 通常通过 size=0，在不同代际可能不同。

## HDP 和 IH 的连接

NBIO 为 HDP memory/register flush 提供 remap 入口和 flush request/done 寄存器偏移；实际 HDP 行为由 [IO6](../../HDP/sources/IO6-hdp40-maintenance.md) 配合解释。不要因寄存器位于 NBIO 就把 HDP SRAM 归入 NBIF。

IH 配置设置 dummy read 地址及是否由 MSI 模式控制 dummy read，并配置 ring 请求 snoop 属性。注释把非缓存存储位置与 nonsnoop 联系起来，但具体代码选择必须单独看，不能从注释范例断言当前 ring 在 VRAM。

## 无 BIF ring 时的 RAS 出口

`handle_ras_controller_intr_no_bifring` 先读取 doorbell interrupt 状态；ALDEBARAN 使用不同寄存器。BIF ring 未启用时，驱动需显式写清 RAS controller 中断状态。有 RAS 上下文、计数采集未被禁用且管理对象存在时，再查询错误数并累计 CE/UE。硬件状态清除、软件累计和通知消费者不是一个动作。

该分支注释明确这是 NBIF RAS error 的专用 controller interrupt，不是全局 sync flood 中断；随后设置 FED 状态并请求 GPU reset。由此可研究“来源检测→清状态→可选计数采集→保护/恢复”的依赖，但不能将该分支推广为所有 NBIF 中断的处理规则。

## 后续研究问题

先列 host BAR/aperture、framebuffer data、doorbell、register access、interrupt notification 五类入口，再逐一标地址译码、目标、权限、背压和完成语义。doorbell 写只是通知提交位置，实际引擎完成要看 fence/事件。

[IO13](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) 的多 AID NBIO 7.9 是有价值的对照，不应把两代字段合并为一个目标实现。公共函数表说明软件支持哪些操作，不能证明内部 crossbar、队列数或完整功能父级。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
