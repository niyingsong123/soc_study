# GC4：RLC 公共层：软件状态、保存区与硬件回调

更新日期：2026-09-24。

导读：补足 GC2 的上层：safe-mode 的软件标志如何维护、保存恢复数据由谁分配。适合判断驱动状态与硬件状态是否被错误等同。
来源：[amdgpu_rlc.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c)。新增资料。
阅读状态：精读 `amdgpu_gfx_rlc_enter_safe_mode`、`exit_safe_mode`、`init_sr` 及相邻资源管理；未通读全部固件版本解析。

## 公共层与 IP 实现的分工

enter 首先检查该 XCC 的 `in_safe_mode`，避免重复进入；随后检查相关 gating 支持条件和 RLC 是否启用，再调用 IP 的 `set_safe_mode` 并置软件标志。exit 对称检查状态、调用 `unset_safe_mode` 并清标志。实际寄存器协议由函数表背后的 IP 代码提供，公共层不能独立说明某代硬件的握手。

这里的软件状态有幂等用途，但没有自动提供全程硬件验证。如果底层回调未上报超时，公共层仍可能设置状态；[GC2](../../GC/sources/GC2-gfx943-rlc-grbm.md) 的 void 回调就是需要注意的例子。研究时应分列“请求状态”“已观察到的 ACK”“软件 bookkeeping”，不要都叫完成。

## 保存恢复资源

`init_sr` 用 dword 数乘 4 得到保存区字节数，创建可由 GPU 访问的 BO，并保存 CPU 指针与 GPU 地址，再把寄存器列表复制到该区。CPU 访问地址和 GPU 使用地址不是同一地址空间；该资源还有分配失败、释放和生命周期问题。

这些数据准备使 RLC 能使用保存恢复信息，但函数本身不证明固件已经执行一次完整 save/restore，也不提供被保存寄存器的全部语义。写论文时应把“描述/缓冲区准备”放在控制前置，把“硬件执行及确认”放在另一阶段。

## 跨模块使用

与 SMU 的 [MG1](../../SMU/sources/MG1-smu-message-table.md) 共享表比较，可学习 CPU 准备数据、设备地址发布、固件消费之间的接口责任；与 [MG4](../../SMN/sources/MG4-smn-indirect-access.md) 的 selector 锁比较，可检查控制状态是否跨调用共享。只有需要固件表格式、完整恢复顺序或实际错误传播时才需继续回读更深代码。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
