# HDP 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 17 个可复用来源，主笔记归档 4 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 历史职责与现代接口 | [IO7](IO7-bkdg-hdp-history.md) → [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) → [IO6](IO6-hdp40-maintenance.md) | 第 1–2 轮：旧 UMA APU 只用于命名/窗口概念，不能套用其容量上限。 |
| 维护与可见性闭环 | [IO2](IO2-linux-device-io.md) → [IO3](../../PCIE/sources/IO3-linux-dma-api.md) → [IO10](../../CF/sources/IO10-gfx90-register-control.md) → [SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) → [MG1](../../SMU/sources/MG1-smu-message-table.md) → [FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) | 第 2–3 轮：CPU copy、HDP flush/invalidate、按请求者匹配的 request/done、ring fence 和 SMU 表传输按实际完成范围连接。 |
| 低功耗、RAS 和代际差异 | [IO14](IO14-hdp60-power-sequence.md) → [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) | 第 3–4 轮：读清/写清、VF 分支、时钟 override 与状态保持分别核对，不靠 callback 返回值猜硬件。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [GC3：LLVM AMDGPU 内存模型：等待、缓存维护与一致性域](../../GC/sources/GC3-llvm-memory-model.md) | 解释 acquire/release 为什么需要组合等待与 cache 操作，以及 gfx90a/gfx942 的 agent、L2 和远端内存条件。研究“写完成”“缓存可见”“TLB 失效”之间的区别时应优先读。 | 固定版本公开代码。精读 Memory Model 总论与 GFX90A、GFX942 的结构/一致性说明；未逐行验证全部编译序列表或后端代码，未编译测试。 | [原文](https://github.com/llvm/llvm-project/blob/llvmorg-18.1.7/llvm/docs/AMDGPUUsage.rst) |
| [VM2：MMHUB 2.x 的地址范围、翻译缓存与 fault 配置](../../HUBS/sources/VM2-mmhub-v2.md) | 按初始化顺序整理 MMHUB 软件可见的服务结构：页表根、aperture、TLB/cache、VM context、失效引擎和 fault。适合构建 hub 控制面；不证明完整内部数据网络。 | 固定版本公开代码。精读 page-table/aperture、TLB/cache、VMID config、invalidation、gart enable/disable 与 fault decode；时钟门控的全部分支未逐项展开。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c) |
| [FAB4：dma-fence：完成对象、时间线与硬件语义的边界](../../DF/sources/FAB4-dma-fence-contract.md) | 解释 fence 的 context/seqno、signal/error、callback 与 lifetime，帮助区分软件完成对象和硬件 flush/fence 操作；跨模块研究完成语义时必读。 | 固定版本公开代码。已读结构、ops 注释、signal/status/wait、seqno 比较和引用生命周期接口；未把头文件视为所有驱动的硬件完成规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h) |
| [FAB7：AMDGPU fence：ring 完成写回、序号槽位和异常收敛](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) | 把抽象 dma-fence 落到 AMDGPU 的 ring 命令、写回内存、序号表、中断/定时器与回收流程，适合研究数据完成怎样变成软件可等待事件。 | 固定版本公开代码。已读 fence contract、emit/polling、process、fallback、wait 和恢复相关入口；具体 ASIC emit_fence 的硬件指令仍需读相应 ring 实现。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c) |
| [R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界](../../SWITCH/sources/R8-axi-ordering-contract.md) | 保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。 | 规范选读。已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。 | [原文](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) |
| [MEM3：AMDGPU RAS：错误计数、坏页与恢复策略](../../UMC/sources/MEM3-amdgpu-ras.md) | 从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。 | 厂商/项目官方资料。已读文档正文的支持、控制、计数和坏页接口；未执行注错、复位或 EEPROM 操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) |
| [IO1：PG213：TLP 接收、选择性流控与跨接口保序](../../PCIE/sources/IO1-pg213-transactions.md) | 围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。 | 厂商/项目官方资料。已读所列正文；FPGA PCIe4 IP 的接口实例，不是完整 PCIe Base 规范或 AMD GPU PCIe RTL。 | [原文](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation) |
| [IO2：Linux Device I/O：MMIO、Posted write 与访问顺序](IO2-linux-device-io.md) | 解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。 | 厂商/项目官方资料。已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。 | [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) |
| [IO3：Linux DMA API：地址、所有权、同步和 scatter-gather](../../PCIE/sources/IO3-linux-dma-api.md) | 用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。 | 厂商/项目官方资料。已读地址关系、DMA mask、coherent/streaming、方向、map/sync/unmap、scatter-gather 与错误处理段；未验证某硬件平台。 | [原文](https://docs.kernel.org/6.12/core-api/dma-api-howto.html) |
| [IO5：NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口](../../NBIF/sources/IO5-nbio74-host-bridge.md) | 提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。 | 固定版本公开代码。已读所列窗口、doorbell、HDP、IH 函数、无 BIF ring 的 RAS controller 中断路径及公共接口表；未通读 ASPM/RAS 全分支，NBIF 与 NBIO 仅作功能对照。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c) |
| [IO6：HDP 4.0 驱动：flush、invalidate 与 RAS 代际差异](IO6-hdp40-maintenance.md) | 研究 HDP 维护命令怎样由 CPU 或 ring 发起、哪些 IP 跳过 invalidate，以及计数清除为何有读清/写清区别；用于准确写完成与恢复边界。 | 固定版本公开代码。已读 flush/invalidate、RAS query/reset、初始化及相关代际判断；没有目标硬件测试。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c) |
| [IO7：AMD 15h BKDG：HDP 历史职责与 UMA 窗口](IO7-bkdg-hdp-history.md) | HDP 全称和 host framebuffer 地址转换的 AMD 原厂历史依据；适合确认命名与窗口概念，不能作为现代 GPU 容量/拓扑参数。 | 厂商/项目官方资料。已读上述 GMC、framebuffer、HDP 正文及配置表；未研读整本寄存器手册。 | [原文](https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/50742_15h_Models_60h-6Fh_BKDG.pdf) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成](../../CF/sources/IO10-gfx90-register-control.md) | 研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。 | 固定版本公开代码。已读 select_se_sh、受 grbm_idx_mutex 保护的选择/恢复模式、kiq_read_clock 的提交/fence/超时/复位分支，以及 ring_emit_hdp_flush；未展开 wait_reg_mem 包字段，文件其余大型执行模块不在本研究范围。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c) |
| [IO14：HDP 6.0：维护提交与时钟/存储低功耗切换](IO14-hdp60-power-sequence.md) | 研究 HDP power/clock 配置的顺序约束和代际地址差异，适合把低功耗放回可访问性与状态保持主线；不能据此推导 SRAM retention 细节。 | 固定版本公开代码。已读完整短文件的 flush、clock-gating 更新及查询；未取得目标电源状态机/电气规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c) |
| [MG1：SMU 公共驱动：mailbox、错误状态与表传输](../../SMU/sources/MG1-smu-message-table.md) | 详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。 | 固定版本公开代码。已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) |
| [SD2：SDMA 5.2：doorbell、维护命令、fence 与 trap](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) | 把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。 | 固定版本公开代码。已读 ring get/set_wptr、mem_sync、HDP flush、VM flush、pipeline sync、fence 和 trap handler；未扩写引擎内部 packet 全规格或 FE/BE/TBE 论文。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
