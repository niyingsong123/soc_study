# IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成

更新日期：2026-09-25。

导读：研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。
来源：[Linux v6.12 gfx_v9_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c)。
阅读状态：已读实例选择/恢复、KIQ clock 读回、HDP request/done 及 WAIT_REG_MEM helper 的字段和失败路径；不是目标 CF 拓扑证据。

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

## 下层 WAIT_REG_MEM 与失败路径补核

本次继续读取同版 `gfx_v9_0_wait_reg_mem`：它依次发一个 PACKET3_WAIT_REG_MEM 头和六个 payload dword；控制字包含 mem_space、operation、比较函数 3（equal）、engine，后续为 addr0、addr1、reference、mask 和 polling interval。代码只在 memory 模式显式检查 addr0 的 dword 对齐。HDP 调用采用 register 模式、operation=1，传 request/done 两地址、相同 ref/mask 及 interval=0x20。该 interval 是包字段，源码没有在这里换算为纳秒；不能当成软件 sleep 或总体 timeout。

KIQ clock 读取同样展示资源失败细节：持 ring lock 分配 writeback，发 COPY_DATA 与 polling fence，commit 后解锁，再等待。fence 发射失败先 ring_undo；reset 中不继续长等；成功后用 mb() 再拼接两个 32-bit writeback 字。失败返回全一的 64-bit 值，不是合法零时钟值。cleanup 还有 `if (reg_val_offs)` 条件，本次不据此宣称所有资源路径已形式验证，也不将注释提到的 IRQ 限制自动当成该函数具有显式 in_irq 检查。

定向检索 AMD 的 Command Fabric/CF_IF 与相邻控制接口后，仍未找到能将这些公开操作映射到目标 CF 拓扑/packet format 的直接材料。因此 CF 的真实身份和路径继续依赖 [L1](../../SDMA/sources/L1-external-glossary-scope.md)/[L2](../../SDMA/sources/L2-external-shaobo-scope.md) 的本地核对；这里新增的是可追踪机制，不是通过相邻来源替 CF 填写未知 RTL。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
