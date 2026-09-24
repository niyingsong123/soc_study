# SMN 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 13 个可复用来源，主笔记归档 2 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 管理访问入口与选择状态 | [MG4](MG4-smn-indirect-access.md) → [MG10](MG10-atl-system-identity.md) | 第 1–2 轮：node 与 register address 分层；index/data 锁覆盖两步，Read-as-Zero 需要调用者解释。 |
| 端点与相邻接口 | [MG5](../../RSMU/sources/MG5-rsmu-umc-index.md) → [MG1](../../SMU/sources/MG1-smu-message-table.md) → [IO10](../../CF/sources/IO10-gfx90-register-control.md) | 第 2–3 轮：寄存器写效果、mailbox 执行和广播选择不同，未知物理网络先保持边界。 |
| 完成、低功耗和恢复 | [IO2](../../HDP/sources/IO2-linux-device-io.md) → [MG2](../../SMU/sources/MG2-smu13-control.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) | 第 3–4 轮：不以读回相等作为所有寄存器的通用成功规则，不把控制网常开当既定事实。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [GC2：GC 9.4.3 的 GRBM 选址与 RLC 控制闭环](../../GC/sources/GC2-gfx943-rlc-grbm.md) | 从驱动调用看实例选择、广播、safe-mode、RLC 启停和门控顺序。适合恢复控制路径的状态与握手；不等同 RLC 固件或硬件内部算法。 | 固定版本公开代码。精读 `xcc_select_se_sh`、safe-mode、`init_rlcg_reg_access_ctrl`、`wait_for_rlc_serdes`、RLC stop/reset/start/resume、`xcc_update_gfx_clock_gating`；其余引擎不扩展研究。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c) |
| [GC4：RLC 公共层：软件状态、保存区与硬件回调](../../GC/sources/GC4-rlc-common.md) | 补足 GC2 的上层：safe-mode 的软件标志如何维护、保存恢复数据由谁分配。适合判断驱动状态与硬件状态是否被错误等同。 | 固定版本公开代码。精读 `amdgpu_gfx_rlc_enter_safe_mode`、`exit_safe_mode`、`init_sr` 及相邻资源管理；未通读全部固件版本解析。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c) |
| [FAB2：Linux DF 3.6：通道编码、hash、实例访问与性能计数器](../../DF/sources/FAB2-df36-registers-counters.md) | 从 AMDGPU 的 DF 3.6 回调识别软件能观察的配置与计数器生命周期，特别说明寄存器编码不等于实际通道数、计数器零值也可能来自未支持或重装失败。 | 固定版本公开代码。已读 channel/hash、broadcast、clock gating、PMC 分配/启动/读回/停止及 poison-query 相关函数；本文件是软件编程视图，不是 DF RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c) |
| [FAB3：AMD ATL：从 UMC 归一化地址恢复系统物理地址](../../DF/sources/FAB3-atl-address-core.md) | 展示 RAS 地址解码必须结合 socket/die/CS、DRAM map、interleave/hash、base 与 MMIO hole；用于避免把 UMC 错误地址直接解释成系统 PA。 | 固定版本公开代码。已读完整文件，重点 norm_to_sys_addr、base/hole 处理及初始化/decoder 注册。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c) |
| [FAB6：AMD ATL denormalize：非二次幂通道与 hash 的逆向重建](../../DF/sources/FAB6-atl-denormalization.md) | 解释 3/5 倍通道模式为何不能靠插入几位 channel ID 还原 PA，以及 DF4.5 如何枚举丢失位和余数，再用正向映射与 CS 身份校验候选地址。 | 固定版本公开代码。已读模式分派、DF4/DF4.5 非二次幂路径及 candidate verification；大量具体位段仅在本版本代码中有效，本笔记不逐个复制。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/denormalize.c) |
| [IO2：Linux Device I/O：MMIO、Posted write 与访问顺序](../../HDP/sources/IO2-linux-device-io.md) | 解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。 | 厂商/项目官方资料。已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。 | [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成](../../CF/sources/IO10-gfx90-register-control.md) | 研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。 | 固定版本公开代码。已读 select_se_sh、受 grbm_idx_mutex 保护的选择/恢复模式、kiq_read_clock 的提交/fence/超时/复位分支，以及 ring_emit_hdp_flush；未展开 wait_reg_mem 包字段，文件其余大型执行模块不在本研究范围。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c) |
| [MG1：SMU 公共驱动：mailbox、错误状态与表传输](../../SMU/sources/MG1-smu-message-table.md) | 详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。 | 固定版本公开代码。已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) |
| [MG2：SMU 13 公共控制：固件就绪、表地址和频率约束](../../SMU/sources/MG2-smu13-control.md) | 连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。 | 固定版本公开代码。已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) |
| [MG4：AMD SMN：index/data 访问与错误判定](MG4-smn-indirect-access.md) | 解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。 | 固定版本公开代码。已读 SMN 访问函数及其完整错误语义注释；不是 GPU 所有 SMN 接入路径的统一规格。 | [原文](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c) |
| [MG5：RSMU 寄存器线索与 UMC 6.1 访问模式](../../RSMU/sources/MG5-rsmu-umc-index.md) | 这是 RSMU 最直接的公开接口证据：UMC index mode 及错误采集前后的状态切换。适合建立职责边界，不能据少量寄存器推定完整 RAS 控制器。 | 固定版本公开代码。已读两个短寄存器头及 UMC index enable/disable/state、RAS count 调用序列；不声明读到 RSMU 完整功能规格。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h) |
| [MG10：AMD ATL system.c：Fabric 身份字段与版本发现](MG10-atl-system-identity.md) | 解释 socket/die/node/component ID 的代际解码和未知版本处理；适合控制寻址与错误地址定位的前置研究，不能用固定移位套所有芯片。 | 固定版本公开代码。已读 node ID 构造、DF2/3/3.5/4 mask/shift、版本发现及系统配置采集；这是 CPU DF/ATL 软件上下文，不是 GPU SMN 路由表。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/system.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
