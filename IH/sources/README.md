# IH 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 23 个可复用来源，主笔记归档 5 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 事件记录、内存和解码 | [MG7](MG7-ih-core-consumer.md) → [MG6](MG6-ih60-ring-hardware.md) → [MG12](MG12-vega10-ih-comparison.md) | 第 1–2 轮：保留 ring 地址/单位、发布屏障、32 字节格式及不同 ring 的 wptr 来源。 |
| 通知和来源处理 | [IO8](IO8-linux-msi.md) → [MG8](MG8-irq-dispatch-lifecycle.md) → [SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) → [MG2](../../SMU/sources/MG2-smu13-control.md) | 第 2–3 轮：MSI、IV、fence 和业务 handler 是不同层次；可能有多个软件消费者。 |
| 溢出、恢复与吞吐 | [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) → [IO13](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) → [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) | 第 3–4 轮：溢出后的追赶无法恢复丢失 IV；每批 budget 不等于总 handler 有界，TODO idle 不作证据。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [P2：AMDGPU 驱动中的 IP 边界与系统入口](../../GC/sources/P2-amdgpu-hardware.md) | 解释 Linux 如何按 IP 组织 GPU，以及 GMC、GC/RLC、SDMA、SMU、IH 的职责。适合首次建立系统边界；查具体队列或硬件协议时应转入对应代码笔记。 | 厂商/项目官方资料。已精读 GPU Hardware Structure、Graphics and Compute Microcontrollers、Driver Structure、Memory Domains、IB 说明；其余 API 参考未逐项研究。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure) |
| [VM2：MMHUB 2.x 的地址范围、翻译缓存与 fault 配置](../../HUBS/sources/VM2-mmhub-v2.md) | 按初始化顺序整理 MMHUB 软件可见的服务结构：页表根、aperture、TLB/cache、VM context、失效引擎和 fault。适合构建 hub 控制面；不证明完整内部数据网络。 | 固定版本公开代码。精读 page-table/aperture、TLB/cache、VMID config、invalidation、gart enable/disable 与 fault decode；时钟门控的全部分支未逐项展开。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c) |
| [VM10：AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约](../../UTCL2/sources/VM10-iommu-spec.md) | 用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。 | 规范选读。已取得完整 303 页 PDF；重点核读 §1.3、§2.1–2.2、§2.4.1–2.4.4、§2.4.11、§2.5；本笔记不是整本规范的逐字段替代品。 | [原文](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf) |
| [C01：MM_UTCL2 图示与验证环境：从翻译事务到可观测检查点](../../UTCL2/sources/C01-mm-utcl2-testbench.md) | 覆盖 MM_UTCL2 的 APT1/2/3、VML2/ATCL2、fault/retry、两类失效以及验证环境，适合建立请求生命周期和验证检查点；所有容量与字段均须保留该资料版本范围。 | 用户页图·参考设计。读取已提交页图的文字并核看关键图；49 页中第 1、4 页未取得有效图像，本笔记主要依据第 3、5、15–31、33–47、49 页。图示版本与目标芯片对应关系仍需本地确认。 | [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/tb_mm_utcl2) |
| [FAB4：dma-fence：完成对象、时间线与硬件语义的边界](../../DF/sources/FAB4-dma-fence-contract.md) | 解释 fence 的 context/seqno、signal/error、callback 与 lifetime，帮助区分软件完成对象和硬件 flush/fence 操作；跨模块研究完成语义时必读。 | 固定版本公开代码。已读结构、ops 注释、signal/status/wait、seqno 比较和引用生命周期接口；未把头文件视为所有驱动的硬件完成规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h) |
| [FAB7：AMDGPU fence：ring 完成写回、序号槽位和异常收敛](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) | 把抽象 dma-fence 落到 AMDGPU 的 ring 命令、写回内存、序号表、中断/定时器与回收流程，适合研究数据完成怎样变成软件可等待事件。 | 固定版本公开代码。已读 fence contract、emit/polling、process、fallback、wait 和恢复相关入口；具体 ASIC emit_fence 的硬件指令仍需读相应 ring 实现。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c) |
| [R22：Garnet NI：终点背压、tail 保留与协议缓冲依赖](../../SWITCH/sources/R22-garnet-network-interface.md) | 说明网络到达终点后仍可能因协议 MessageBuffer 无空间而持有 tail/VC，并解释 credit、回调和消息交付的关系；用于补齐端到端依赖分析。 | 固定版本公开代码。已读 wakeup、stall queue、flitisizeMessage、VC 选择及发送调度相关路径；消息是模型对象，不将其内存表示当硬件缓存实现。 | [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/NetworkInterface.cc) |
| [R12：Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层](../../SWITCH/sources/R12-arm-system-architecture.md) | 提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。 | Arm 架构概述。已读系统组件和接口章节，重点第 4 章 AMBA 分类、CHI-C2C、DTI/LTI 与 LPI；不把 Arm 组件名视为 AMD 一一等价模块。 | [原文](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749) |
| [MEM3：AMDGPU RAS：错误计数、坏页与恢复策略](../../UMC/sources/MEM3-amdgpu-ras.md) | 从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。 | 厂商/项目官方资料。已读文档正文的支持、控制、计数和坏页接口；未执行注错、复位或 EEPROM 操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) |
| [MEM14：UMC 8.10 驱动：错误分类与地址候选展开](../../UMC/sources/MEM14-umc810-ras-address.md) | 研究错误地址为何不是现成系统物理地址，以及 UE 计数为何可能没有可隔离页面；提供具体寄存器与转换路径，适合 RAS 联读。 | 固定版本公开代码。已读错误计数、通道索引、地址转换、状态清除及固件 ECC 信息分支；未读取目标芯片寄存器，不能推广到其他 UMC 代际。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c) |
| [IO3：Linux DMA API：地址、所有权、同步和 scatter-gather](../../PCIE/sources/IO3-linux-dma-api.md) | 用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。 | 厂商/项目官方资料。已读地址关系、DMA mask、coherent/streaming、方向、map/sync/unmap、scatter-gather 与错误处理段；未验证某硬件平台。 | [原文](https://docs.kernel.org/6.12/core-api/dma-api-howto.html) |
| [IO5：NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口](../../NBIF/sources/IO5-nbio74-host-bridge.md) | 提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。 | 固定版本公开代码。已读所列窗口、doorbell、HDP、IH 函数、无 BIF ring 的 RAS controller 中断路径及公共接口表；未通读 ASPM/RAS 全分支，NBIF 与 NBIO 仅作功能对照。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c) |
| [IO8：Linux MSI：通知写、向量分配与中断并发](IO8-linux-msi.md) | 解释 MSI/MSI-X 为什么是内存写形式的通知、如何与之前的数据写排序，以及多向量如何改变并发；适合 IH 到 CPU 的最后一段路径。 | 厂商/项目官方资料。已读基本原理、排序、向量 API、锁和诊断段；不是完整 PCIe 规范或中断控制器硬件说明。 | [原文](https://docs.kernel.org/6.12/PCI/msi-howto.html) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO12：PCIe AER：严重性、报告权与恢复触发](../../PCIE/sources/IO12-aer-error-path.md) | 区分可纠正、不可纠正非致命与致命错误，并说明固件/OS 谁处理 AER；适合把链路错误连接到恢复策略，不能当作通用 ECC 规范。 | 厂商/项目官方资料。已读 AER 服务、_OSC、错误分类/日志和恢复回调段；未进行注错或实机恢复。 | [原文](https://docs.kernel.org/6.12/PCI/pcieaer-howto.html) |
| [IO13：NBIO 7.9：多 AID doorbell、分区与 replay 计数](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) | 扩展 NBIF 到多实例/分区场景，解释 doorbell 的双层配置和 replay 指标的实际来源；适合与 NBIO 7.4 比较代际差异。 | 固定版本公开代码。已读 SDMA/IH doorbell、aperture、partition 状态、初始化和 replay count；未系统阅读整个 RAS/电源路径。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c) |
| [MG2：SMU 13 公共控制：固件就绪、表地址和频率约束](../../SMU/sources/MG2-smu13-control.md) | 连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。 | 固定版本公开代码。已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) |
| [MG6：IH 6.0：ring 地址、溢出与 doorbell 回收](MG6-ih60-ring-hardware.md) | 从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。 | 固定版本公开代码。已读 ring 控制/地址配置、get_wptr/set_rptr、rearm、self IRQ、软件初始化和 idle/reset 接口；未读目标 RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c) |
| [MG7：IH 公共代码：发布顺序、IV 解码与 checkpoint](MG7-ih-core-consumer.md) | 解释 producer/consumer ring 的内存顺序和 32 字节 IV 格式，覆盖 budget/restart、软件 ring 和 checkpoint；适合写 IH 完成与丢事件边界。 | 固定版本公开代码。已读 ring 分配、写入、处理、Vega10+ 解码及 checkpoint 等待；未把公共格式推广至旧代际。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c) |
| [MG8：AMDGPU IRQ：来源分派、引用计数与复位恢复](MG8-irq-dispatch-lifecycle.md) | 研究 IH 解码后如何路由给 IP/KFD、如何管理中断使能引用，以及 reset 后如何恢复；适合把事件传输连接到实际处理者。 | 固定版本公开代码。已读 handler、来源登记/dispatch、delegate、enable get/put/update 和 reset resume helper；未通读所有 IRQ domain 平台分支。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c) |
| [MG12：Vega10 IH：不同 ring 的 wptr 来源与溢出处理](MG12-vega10-ih-comparison.md) | 通过另一代 IH 检查 ring 数量、writeback、地址和 overflow 差异；适合验证哪些结论可复用，避免只看 IH6.0 就推广所有 GPU。 | 固定版本公开代码。已读软件初始化、wptr/rptr、overflow/rearm 和公共解码绑定；原候选 ih_v5_0.c 路径不适用，实际来源以此文件为准。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/vega10_ih.c) |
| [SD1：AMDGPU SDMA 公共层：实例、固件和 RAS 接口](../../SDMA/sources/SD1-sdma-system-lifecycle.md) | 只研究 SDMA 如何接入 SoC：ring 到实例映射、固件版本条件、ECC 通知和复位责任；不替代外部 SDMA 项目的 FE/BE/TBE 内部资料。 | 固定版本公开代码。已读实例查找、上下文地址条件、固件头/feature 与 RAS 入口；未复制或修改独立 sdma_repo，未研究目标 FE/BE/TBE RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c) |
| [SD2：SDMA 5.2：doorbell、维护命令、fence 与 trap](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) | 把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。 | 固定版本公开代码。已读 ring get/set_wptr、mem_sync、HDP flush、VM flush、pipeline sync、fence 和 trap handler；未扩写引擎内部 packet 全规格或 FE/BE/TBE 论文。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
