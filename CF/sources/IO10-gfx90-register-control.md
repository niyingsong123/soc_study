# IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成

更新日期：2026-09-24。

导读：研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。
来源：[Linux v6.12 gfx_v9_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c)。
阅读状态：已读 select_se_sh、受 grbm_idx_mutex 保护的选择/恢复模式、kiq_read_clock 的提交/fence/超时/复位分支，以及 ring_emit_hdp_flush；未展开 wait_reg_mem 包字段，文件其余大型执行模块不在本研究范围。

## 目标选择本身也是状态

GRBM_GFX_INDEX 分别设置 instance、SE、SH 索引或广播位。调用方持有 grbm_idx_mutex 后选择实例、访问寄存器，再恢复广播并释放锁；关键不只是某个单次读写原子，而是“选择→访问→恢复”这一序列不可被另一使用者穿插。

广播写与单实例读的含义不同，不能把广播看成普通地址多了一个值。错误/超时分支仍要恢复选择状态并解锁，否则后续访问可能悄悄落到错误实例。[GC2](../../GC/sources/GC2-gfx943-rlc-grbm.md) 提供另一代 XCC 语境对照。

## 异步读回路径

kiq_read_clock 分配 writeback 位置，在 ring 中发起寄存器到内存的读回及 polling fence，再提交、释放 ring lock、等待 fence，最后用内存屏障后读取 writeback。资源分配、命令提交、fence 完成、数据读取和释放是不同步骤。

代码对 GPU reset 情形退出长期等待，以免恢复流程反被等待读寄存器的线程阻塞；失败还需撤销或释放相应资源。这提供“控制路径也可能参与进展循环”的具体例子，而非只在大数据 NoC 中研究死锁。

## HDP request/done 与请求者匹配

`ring_emit_hdp_flush` 从 NBIO 接口取得 request/done 寄存器偏移和各请求者的 reference/mask。compute ring 的 ME 1 以 CP2 基准左移 pipe，ME 2 以 CP6 基准左移 pipe，其他 ME 直接返回；非 compute ring 使用 CP0 基准。compute 与非 compute 路径还分别选择不同的 register/memory engine 参数。

函数把 request 地址、done 地址、相同 reference/mask 和 `0x20` 轮询参数交给 `gfx_v9_0_wait_reg_mem`，在 ring 中发出维护及等待操作。这不是 CPU 当场轮询的路径，也不能把一个请求者的 done 当成所有引擎、GL2/TLB 和系统缓存同时完成。精确包编码仍需回读下层 helper。与 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) 的 NBIO remap、[IO6](../../HDP/sources/IO6-hdp40-maintenance.md) 的 HDP 操作、[SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) 的 SDMA 维护路径联读，可保留“发起者身份→维护请求→对应完成→后继命令”的系统接口闭环。

## 应用于 CF 的方式

保持本项目 CF=Command Fabric，使用 register/control bus、CSR fabric、indirect access 等术语扩大搜索。先确定发起者、目标身份、共享选择状态、返回路径、锁/资源和失效退出，再决定是否需要研究仲裁/QoS。此代码不能说明命令实际经过哪个硬件 fabric，也不能把 KIQ、SMN 或 GRBM 直接改名为 CF。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
