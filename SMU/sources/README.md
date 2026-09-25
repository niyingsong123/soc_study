# SMU 资料索引与逐篇技术笔记

更新日期：2026-09-25。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 25 个可复用来源，主笔记归档 4 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 管理请求和共享表 | [MG1](MG1-smu-message-table.md) → [MG2](MG2-smu13-control.md) → [MG3](MG3-smu13-firmware-abi.md) | 第 1–2 轮：message/response、ASIC 映射、锁、ABI 与数据可见性放在同一闭环。 |
| 策略约束与反馈 | [MG9](MG9-thermal-power-observability.md) → [IO14](../../HDP/sources/IO14-hdp60-power-sequence.md) → [MEM4](../../PHY/sources/MEM4-dfi-version-boundary.md) → [FAB5](../../DF/sources/FAB5-xgmi-topology.md) | 第 2–3 轮：请求频率、实际频率和平均值区分；本地低功耗序列不能自动当 SMU 完整算法。 |
| 错误、事件和恢复 | [MG5](../../RSMU/sources/MG5-rsmu-umc-index.md) → [MG6](../../IH/sources/MG6-ih60-ring-hardware.md) → [MG8](../../IH/sources/MG8-irq-dispatch-lifecycle.md) → [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) | 第 3–4 轮：管理访问、检测、通知和保护策略各自有状态；API 成功可能是条件跳过。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [P2：AMDGPU 驱动中的 IP 边界与系统入口](../../GC/sources/P2-amdgpu-hardware.md) | 解释 Linux 如何按 IP 组织 GPU，以及 GMC、GC/RLC、SDMA、SMU、IH 的职责。适合首次建立系统边界；查具体队列或硬件协议时应转入对应代码笔记。 | 厂商/项目官方资料。已精读 GPU Hardware Structure、Graphics and Compute Microcontrollers、Driver Structure、Memory Domains、IB 说明；其余 API 参考未逐项研究。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure) |
| [P4：GRBM 活动计数与利用率解释](../../GC/sources/P4-grbm-utilization.md) | 说明 GRBM 提供哪些粗粒度忙碌度观测，以及为什么 GPU Busy、GL2C Busy 不能直接证明吞吐或瓶颈。研究 GRBM 寄存器选址和 RLC 协同时应联读 GC2。 | 厂商/项目官方资料。正文全部已读；未实测采样，也未逐一核验面板代码。旧索引的 7.14.1 不作为本次实际阅读版本。 | [原文](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/grbm.html) |
| [GC2：GC 9.4.3 的 GRBM 选址与 RLC 控制闭环](../../GC/sources/GC2-gfx943-rlc-grbm.md) | 从驱动调用看实例选择、广播、safe-mode、RLC 启停和门控顺序。适合恢复控制路径的状态与握手；不等同 RLC 固件或硬件内部算法。 | 固定版本公开代码。精读 `xcc_select_se_sh`、safe-mode、`init_rlcg_reg_access_ctrl`、`wait_for_rlc_serdes`、RLC stop/reset/start/resume、`xcc_update_gfx_clock_gating`；其余引擎不扩展研究。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c) |
| [GC4：RLC 公共层：软件状态、保存区与硬件回调](../../GC/sources/GC4-rlc-common.md) | 补足 GC2 的上层：safe-mode 的软件标志如何维护、保存恢复数据由谁分配。适合判断驱动状态与硬件状态是否被错误等同。 | 固定版本公开代码。精读 `amdgpu_gfx_rlc_enter_safe_mode`、`exit_safe_mode`、`init_sr` 及相邻资源管理；未通读全部固件版本解析。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c) |
| [VM3：GMC v9 的 GPUVM 失效：请求、ACK、hub 与电源状态](../../UTCL2/sources/VM3-gpuvm-invalidation.md) | 详细追踪 GPUVM invalidate 的软件发起与完成观察，包含 VMID/PASID 转换、不同 hub、KIQ 与直接寄存器路径及旧 ACK 风险。适合建立维护事务闭环。 | 固定版本公开代码。精读 `get_invalidate_req`、`use_invalidate_semaphore`、`flush_gpu_tlb`、`flush_gpu_tlb_pasid`、`emit_flush_gpu_tlb`，以及 fault 状态输出定位；其他 GMC 功能未全文研究。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c) |
| [FAB2：Linux DF 3.6：通道编码、hash、实例访问与性能计数器](../../DF/sources/FAB2-df36-registers-counters.md) | 从 AMDGPU 的 DF 3.6 回调识别软件能观察的配置与计数器生命周期，特别说明寄存器编码不等于实际通道数、计数器零值也可能来自未支持或重装失败。 | 固定版本公开代码。已读 channel/hash、broadcast、clock gating、PMC 分配/启动/读回/停止及 poison-query 相关函数；本文件是软件编程视图，不是 DF RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c) |
| [FAB5：AMDGPU XGMI：hive、节点拓扑、链路信息与 RAS](../../DF/sources/FAB5-xgmi-topology.md) | 从驱动观察 XGMI 多设备拓扑的建立、固件协作、hop/link 信息和错误入口；特别记录 v6.12 中 pstate 切换实际被提前返回禁用，防止把死代码当现行功能。 | 固定版本公开代码。已读 hive 生命周期、add/remove、PSP topology、hop/link 查询、pstate 和 RAS 入口；未获得 XGMI 私有线协议。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c) |
| [R10：UCIe 教程：协议层、D2D Adapter、CRC/retry 与状态协商](../../SWITCH/sources/R10-ucie-protocol-adapter.md) | 分清 FDI/RDI 两侧责任、raw/标准 flit 模式的可靠性归属，以及链路初始化/低功耗进入需要的多层握手；用于规划 die-to-die switch 边界。 | 厂商/项目官方资料。已读协议/flit 格式、adapter、初始化和 PM 示例；教程是 2023 版本背景，不代表后续所有 UCIe 修订。 | [原文](https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf) |
| [R12：Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层](../../SWITCH/sources/R12-arm-system-architecture.md) | 提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。 | Arm 架构概述。已读系统组件和接口章节，重点第 4 章 AMBA 分类、CHI-C2C、DTI/LTI 与 LPI；不把 Arm 组件名视为 AMD 一一等价模块。 | [原文](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749) |
| [R14：UCIe 电气教程：forwarded clock、训练、repair 与封装约束](../../PHY/sources/R14-ucie-electrical-training.md) | 解释 UCIe die-to-die 物理层如何依赖封装距离、时钟/数据匹配、训练与 lane repair；用来区分链路可靠性、可用带宽和协议完成。 | 厂商/项目官方资料。已读 PHY architecture、clocking、BER/channel、LTSSM、initialization/repair 与 compliance 相关页；所有速率/距离/封装参数保留 2023 教程版本范围。 | [原文](https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf) |
| [MEM3：AMDGPU RAS：错误计数、坏页与恢复策略](../../UMC/sources/MEM3-amdgpu-ras.md) | 从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。 | 厂商/项目官方资料。已读文档正文的支持、控制、计数和坏页接口；未执行注错、复位或 EEPROM 操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) |
| [MEM4：DFI 官方资料：控制器与 PHY 的边界及 6.0 变化](../../PHY/sources/MEM4-dfi-version-boundary.md) | 用于确定 controller/PHY 分工、训练所有权与规范版本；尤其修正“DFI 不支持 HBM”的过时概括。公开更新不能代替接口信号规范。 | 规范组织公开介绍。已读公开介绍与发布消息；未取得登录下载的完整 DFI 规范，不填写未核实的信号、时序或 HBM profile。 | [原文](https://ddr-phy.org/) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO12：PCIe AER：严重性、报告权与恢复触发](../../PCIE/sources/IO12-aer-error-path.md) | 区分可纠正、不可纠正非致命与致命错误，并说明固件/OS 谁处理 AER；适合把链路错误连接到恢复策略，不能当作通用 ECC 规范。 | 厂商/项目官方资料。已读 AER 服务、_OSC、错误分类/日志和恢复回调段；未进行注错或实机恢复。 | [原文](https://docs.kernel.org/6.12/PCI/pcieaer-howto.html) |
| [IO14：HDP 6.0：维护提交与时钟/存储低功耗切换](../../HDP/sources/IO14-hdp60-power-sequence.md) | 研究 HDP power/clock 配置的顺序约束和代际地址差异，适合把低功耗放回可访问性与状态保持主线；不能据此推导 SRAM retention 细节。 | 固定版本公开代码。已读完整短文件的 flush、clock-gating 更新及查询；未取得目标电源状态机/电气规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c) |
| [MG1：SMU 公共驱动：mailbox、错误状态与表传输](MG1-smu-message-table.md) | 详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。 | 固定版本公开代码。已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) |
| [MG2：SMU 13 公共控制：固件就绪、表地址和频率约束](MG2-smu13-control.md) | 连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。 | 固定版本公开代码。已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) |
| [MG3：SMU 13.0.0 ABI：DPM 描述、表结构与指标语义](MG3-smu13-firmware-abi.md) | 研究固件接口版本、参数表和 telemetry 的字段差异；重点是 target/pre-DS/post-DS、平均时间常数与累计量，适合设计可信观测表。 | 固定版本公开代码。已读版本、feature 定义、DpmDescriptor、PPTable 组合、DriverSmuConfig、DriverInfo 和 SmuMetrics；未逐字段研究完整板级参数/算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h) |
| [MG4：AMD SMN：index/data 访问与错误判定](../../SMN/sources/MG4-smn-indirect-access.md) | 解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。 | 固定版本公开代码。已读 SMN 访问函数及其完整错误语义注释；不是 GPU 所有 SMN 接入路径的统一规格。 | [原文](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c) |
| [MG5：RSMU 寄存器线索与 UMC 6.1 访问模式](../../RSMU/sources/MG5-rsmu-umc-index.md) | 用 AMD 作者提交确认 remote SMU 名称及寄存器接口/错误/复位职责，配合 UMC index-mode 保存恢复与 BOWEN 参考位置；目标实例/内部实现仍未知。 | 固定版本公开代码。已读 AMD 原始提交 245219a、两份 v0.0.2 头及 Linux v6.12 UMC index/RAS 调用；不声明取得完整 RSMU 规格。 | [原文](https://github.com/torvalds/linux/commit/245219a66085332a30e4653db3542ea5654ff762) |
| [MG6：IH 6.0：ring 地址、溢出与 doorbell 回收](../../IH/sources/MG6-ih60-ring-hardware.md) | 从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。 | 固定版本公开代码。已读 ring 控制/地址配置、get_wptr/set_rptr、rearm、self IRQ、软件初始化和 idle/reset 接口；未读目标 RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c) |
| [MG8：AMDGPU IRQ：来源分派、引用计数与复位恢复](../../IH/sources/MG8-irq-dispatch-lifecycle.md) | 研究 IH 解码后如何路由给 IP/KFD、如何管理中断使能引用，以及 reset 后如何恢复；适合把事件传输连接到实际处理者。 | 固定版本公开代码。已读 handler、来源登记/dispatch、delegate、enable get/put/update 和 reset resume helper；未通读所有 IRQ domain 平台分支。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c) |
| [MG9：AMDGPU 温度/功耗接口：单位、策略与同步快照](MG9-thermal-power-observability.md) | 用于设计性能实验的观测表，区分功率上限、实际功率、档位与平均频率；适合 SMU 的反馈路径，不是固件调频算法说明。 | 厂商/项目官方资料。已读 hwmon、performance level、pp_dpm 与 gpu_metrics 段；未执行任何调频、功耗或风扇写操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/thermal.html) |
| [MG11：UMC 6.7：错误地址展开与 poison 模式的代际对照](../../RSMU/sources/MG11-umc67-ras-comparison.md) | 补充 RSMU 相邻的 UMC RAS 路径，解释 hash/列位模糊如何扩大隔离候选，及 poison 查询如何依赖寄存器；用于对照 UMC 8.10。 | 固定版本公开代码。已读地址转换、直接/固件错误地址路径及 poison 查询；这不是 RSMU 内部实现证据。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c) |
| [SD1：AMDGPU SDMA 公共层：实例、固件和 RAS 接口](../../SDMA/sources/SD1-sdma-system-lifecycle.md) | 只研究 SDMA 如何接入 SoC：ring 到实例映射、固件版本条件、ECC 通知和复位责任；不替代外部 SDMA 项目的 FE/BE/TBE 内部资料。 | 固定版本公开代码。已读实例查找、上下文地址条件、固件头/feature 与 RAS 入口；未复制或修改独立 sdma_repo，未研究目标 FE/BE/TBE RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
