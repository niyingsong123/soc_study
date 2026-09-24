# CF 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 18 个可复用来源，主笔记归档 1 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 命令身份与端点访问 | [L1](../../SDMA/sources/L1-external-glossary-scope.md) → [L2](../../SDMA/sources/L2-external-shaobo-scope.md) → [IO10](IO10-gfx90-register-control.md) → [MG4](../../SMN/sources/MG4-smn-indirect-access.md) | 第 1 轮：CF 保持 Command Fabric；GRBM/SMN 只是控制访问参照，外部目标接口需本地复查。 |
| 接纳、排序和完成 | [R8](../../SWITCH/sources/R8-axi-ordering-contract.md) → [R7](../../SWITCH/sources/R7-floonoc-paper.md) → [FAB4](../../DF/sources/FAB4-dma-fence-contract.md) → [FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) → [SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) | 第 1–2 轮：credit、接收确认、工作完成及原命令完成逐项找责任者，不把 AXI 默认当 CF 协议。 |
| 共享状态与异常退出 | [MG1](../../SMU/sources/MG1-smu-message-table.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) → [MG8](../../IH/sources/MG8-irq-dispatch-lifecycle.md) | 第 3 轮：控制请求也会等待共享资源；超时、取消和复位后的旧返回必须有退出约定。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [GC3：LLVM AMDGPU 内存模型：等待、缓存维护与一致性域](../../GC/sources/GC3-llvm-memory-model.md) | 解释 acquire/release 为什么需要组合等待与 cache 操作，以及 gfx90a/gfx942 的 agent、L2 和远端内存条件。研究“写完成”“缓存可见”“TLB 失效”之间的区别时应优先读。 | 固定版本公开代码。精读 Memory Model 总论与 GFX90A、GFX942 的结构/一致性说明；未逐行验证全部编译序列表或后端代码，未编译测试。 | [原文](https://github.com/llvm/llvm-project/blob/llvmorg-18.1.7/llvm/docs/AMDGPUUsage.rst) |
| [VM3：GMC v9 的 GPUVM 失效：请求、ACK、hub 与电源状态](../../UTCL2/sources/VM3-gpuvm-invalidation.md) | 详细追踪 GPUVM invalidate 的软件发起与完成观察，包含 VMID/PASID 转换、不同 hub、KIQ 与直接寄存器路径及旧 ACK 风险。适合建立维护事务闭环。 | 固定版本公开代码。精读 `get_invalidate_req`、`use_invalidate_semaphore`、`flush_gpu_tlb`、`flush_gpu_tlb_pasid`、`emit_flush_gpu_tlb`，以及 fault 状态输出定位；其他 GMC 功能未全文研究。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c) |
| [VM11：动态 VMID 的租用、复用与页表更新依赖](../../UTCL2/sources/VM11-vmid-lifetime.md) | 解释为什么 VMID 不能当作永久进程编号，以及驱动如何用 active fence、页表根和 flush 进度防止过早复用。适合连接提交队列、翻译上下文与完成事件。 | 固定版本公开代码。精读 VMID idle/used/reserved/grab、compatible、flush 进度与 active fence 处理；PASID allocator 的全部路径未展开。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c) |
| [FAB4：dma-fence：完成对象、时间线与硬件语义的边界](../../DF/sources/FAB4-dma-fence-contract.md) | 解释 fence 的 context/seqno、signal/error、callback 与 lifetime，帮助区分软件完成对象和硬件 flush/fence 操作；跨模块研究完成语义时必读。 | 固定版本公开代码。已读结构、ops 注释、signal/status/wait、seqno 比较和引用生命周期接口；未把头文件视为所有驱动的硬件完成规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h) |
| [FAB7：AMDGPU fence：ring 完成写回、序号槽位和异常收敛](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) | 把抽象 dma-fence 落到 AMDGPU 的 ring 命令、写回内存、序号表、中断/定时器与回收流程，适合研究数据完成怎样变成软件可等待事件。 | 固定版本公开代码。已读 fence contract、emit/polling、process、fallback、wait 和恢复相关入口；具体 ASIC emit_fence 的硬件指令仍需读相应 ring 实现。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c) |
| [R7：FlooNoC 论文：宽物理网络、AXI 并发流与端点重排](../../SWITCH/sources/R7-floonoc-paper.md) | 说明宽链路 NoC 如何把 AXI 排序放在 NI、用响应存储预约保证可接收，并比较带 ROB 与限制同 ID 目标的两种设计；适合作为 AMD switch 的行业对照。 | 原始论文。已读 §II–VI，重点 NI ordering、physical links、router、集成/物理实现；性能数字不作为 AMD 目标指标。 | [原文](https://arxiv.org/html/2409.17606v1) |
| [R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界](../../SWITCH/sources/R8-axi-ordering-contract.md) | 保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。 | 规范选读。已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。 | [原文](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) |
| [R12：Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层](../../SWITCH/sources/R12-arm-system-architecture.md) | 提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。 | Arm 架构概述。已读系统组件和接口章节，重点第 4 章 AMBA 分类、CHI-C2C、DTI/LTI 与 LPI；不把 Arm 组件名视为 AMD 一一等价模块。 | [原文](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749) |
| [IO1：PG213：TLP 接收、选择性流控与跨接口保序](../../PCIE/sources/IO1-pg213-transactions.md) | 围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。 | 厂商/项目官方资料。已读所列正文；FPGA PCIe4 IP 的接口实例，不是完整 PCIe Base 规范或 AMD GPU PCIe RTL。 | [原文](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation) |
| [IO2：Linux Device I/O：MMIO、Posted write 与访问顺序](../../HDP/sources/IO2-linux-device-io.md) | 解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。 | 厂商/项目官方资料。已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。 | [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成](IO10-gfx90-register-control.md) | 研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。 | 固定版本公开代码。已读 select_se_sh、受 grbm_idx_mutex 保护的选择/恢复模式、kiq_read_clock 的提交/fence/超时/复位分支，以及 ring_emit_hdp_flush；未展开 wait_reg_mem 包字段，文件其余大型执行模块不在本研究范围。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c) |
| [MG1：SMU 公共驱动：mailbox、错误状态与表传输](../../SMU/sources/MG1-smu-message-table.md) | 详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。 | 固定版本公开代码。已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) |
| [MG4：AMD SMN：index/data 访问与错误判定](../../SMN/sources/MG4-smn-indirect-access.md) | 解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。 | 固定版本公开代码。已读 SMN 访问函数及其完整错误语义注释；不是 GPU 所有 SMN 接入路径的统一规格。 | [原文](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c) |
| [MG8：AMDGPU IRQ：来源分派、引用计数与复位恢复](../../IH/sources/MG8-irq-dispatch-lifecycle.md) | 研究 IH 解码后如何路由给 IP/KFD、如何管理中断使能引用，以及 reset 后如何恢复；适合把事件传输连接到实际处理者。 | 固定版本公开代码。已读 handler、来源登记/dispatch、delegate、enable get/put/update 和 reset resume helper；未通读所有 IRQ domain 平台分支。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c) |
| [SD2：SDMA 5.2：doorbell、维护命令、fence 与 trap](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) | 把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。 | 固定版本公开代码。已读 ring get/set_wptr、mem_sync、HDP flush、VM flush、pipeline sync、fence 和 trap handler；未扩写引擎内部 packet 全规格或 FE/BE/TBE 论文。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c) |
| [L1：外部 SDMA 术语表：既有登记与复查入口](../../SDMA/sources/L1-external-glossary-scope.md) | 用于查项目专用 CF/DF、FE/BE/TBE、UTCL1/UTCL2 含义；当前只保存原仓库登记范围，必须在本地可访问外部项目时复查原文。 | 外部入口·未重读。本次无法访问外部项目，未重新读取全文；本笔记仅整理本仓库已有摘要，不是原文详细总结。 | 外部本地路径见笔记 |
| [L2：外部 shaobo 摘要：两条后端路径的待复查接口](../../SDMA/sources/L2-external-shaobo-scope.md) | 原登记涉及 FE 两条后端路径、CF_IF/DF_IF、TBE 内 UTCL1、UTCL2 请求和 MMHUB 写回；适合后续本地核实 SDMA 与 SoC 的连接。 | 外部入口·未重读。本次未取得外部摘要或原始资料全文；仅保留现有来源登记，不补造时序、格式和内部职责。 | 外部本地路径见笔记 |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
