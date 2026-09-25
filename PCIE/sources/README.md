# PCIE 资料索引与逐篇技术笔记

更新日期：2026-09-25。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 20 个可复用来源，主笔记归档 6 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| BAR/DMA 与请求完成 | [IO1](IO1-pg213-transactions.md) → [IO2](../../HDP/sources/IO2-linux-device-io.md) → [IO3](IO3-linux-dma-api.md) → [IO4](IO4-base-spec-gap.md) | 第 1–2 轮：区分地址域、descriptor/payload/byte enable、Split Completion 与在途身份。 |
| 有限资源、保序与翻译扩展 | [IO1](IO1-pg213-transactions.md) → [IO11](IO11-ats-pri-pasid.md) → [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) → [IO13](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) | 第 3–4 轮：CQ NP credit 与链路 credit 分池；ATS/PRI/PASID 的能力、额度和 PF/VF 共享分别核对。 |
| 通知、链路和恢复 | [IO8](../../IH/sources/IO8-linux-msi.md) → [IO9](IO9-pci-error-recovery.md) → [IO12](IO12-aer-error-path.md) → [MEM6](../../PHY/sources/MEM6-pcie-equalization.md) → [MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md) | 第 4–5 轮：MSI 排序、AER 严重性、早期 MMIO 与正常 DMA 恢复有不同完成条件。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [VM1：GPUVM 的地址空间、VMID、PASID 与 aperture](../../UTCL2/sources/VM1-gpuvm-address-spaces.md) | 建立 GPUVA、页表、动态 VMID、PASID 与系统地址的基本关系；尤其适合防止把 GPUVM 和系统 IOMMU 合并为一个翻译器。 | 固定版本公开代码。精读开头 `DOC: GPUVM` 与 `amdgpu_vm_set_pasid`；页表 BO 搬迁和全部更新实现未系统研读。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c) |
| [VM4：AMD IOMMU 驱动的多级翻译缓存失效与完成等待](../../UTCL2/sources/VM4-amd-iommu-commands.md) | 说明为什么更新系统映射后可能需要同时处理 IOMMU 内部缓存和 ATS 设备 IOTLB，并追踪 command queue 与 completion wait。适合与本地 GPUVM invalidate 对比。 | 固定版本公开代码。精读 command 构造、range 编码、queue/completion、device/domain flush 相关函数；中断重映射与全部 IOMMU 模式未通读。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c) |
| [VM10：AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约](../../UTCL2/sources/VM10-iommu-spec.md) | 用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。 | 规范选读。已取得完整 303 页 PDF；重点核读 §1.3、§2.1–2.2、§2.4.1–2.4.4、§2.4.11、§2.5；本次补核 §2.2.6–2.2.7.1、§2.4.7、§2.6 的 guest/nested 与 PRI/PPR 主线；本笔记不是整本规范的逐字段替代品。 | [原文](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf) |
| [C05：MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。 | 用户页图·参考设计。读取 41 页可提取文字，直接核看第 7、18、27、32、33、34、40 页关键图表；图中缺乏的 RTL 时序、RAM 端口数和严格完成定义保持未知。 | 原图已移出仓库 |
| [R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界](../../SWITCH/sources/R8-axi-ordering-contract.md) | 保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。 | 规范选读。已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion，并补核 A3.4 burst/error 与 A7.2 exclusive；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。 | [原文](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) |
| [MEM6：PG239：PCIe PHY 均衡阶段与完成语义](../../PHY/sources/MEM6-pcie-equalization.md) | 解释 Preset Apply、接收适配、发送系数更新的不同阶段，适合 PCIe PHY 与链路状态机联读；重点是请求接受和适配完成的区别。 | 厂商/项目官方资料。已读均衡序列章节；产品规格仅作入口，未读完整 PCIe 规范或实现全部训练流程。 | [原文](https://docs.amd.com/r/en-US/pg239-pcie-phy/Product-Specification) |
| [MEM7：AM002：串行接收均衡与 CDR](../../PHY/sources/MEM7-versal-cdr-equalizer.md) | 把链路误码问题分解为信道损耗、均衡与采样相位跟踪，适合 PHY 微架构入门；不提供 HBM 源同步接口或目标芯片的接收器设计。 | 厂商/项目官方资料。已读 Versal GTY/GTYP 接收器上述正文；未读全手册、未做眼图/BER 实测。 | [原文](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR) |
| [IO1：PG213：TLP 接收、选择性流控与跨接口保序](IO1-pg213-transactions.md) | 围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。 | 厂商/项目官方资料。已读所列正文；FPGA PCIe4 IP 的接口实例，不是完整 PCIe Base 规范或 AMD GPU PCIe RTL。 | [原文](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation) |
| [IO2：Linux Device I/O：MMIO、Posted write 与访问顺序](../../HDP/sources/IO2-linux-device-io.md) | 解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。 | 厂商/项目官方资料。已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。 | [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) |
| [IO3：Linux DMA API：地址、所有权、同步和 scatter-gather](IO3-linux-dma-api.md) | 用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。 | 厂商/项目官方资料。已读地址关系、DMA mask、coherent/streaming、方向、map/sync/unmap、scatter-gather 与错误处理段；未验证某硬件平台。 | [原文](https://docs.kernel.org/6.12/core-api/dma-api-howto.html) |
| [IO4：PCIe Base 5.0：规范入口与待补读范围](IO4-base-spec-gap.md) | 正式规范全文未取得的缺口记录，指明链路层/事务层哪些细节不能只靠 FPGA 指南推定；无需把它当成已完成的技术精读。 | 规范全文未取得。未取得全文；未声明规范合规阅读，版本以原有 5.0 登记为限，不推定当前最新标准。 | [原文](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0) |
| [IO5：NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口](../../NBIF/sources/IO5-nbio74-host-bridge.md) | 提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。 | 固定版本公开代码。已读所列窗口、doorbell、HDP、IH 函数、无 BIF ring 的 RAS controller 中断路径及公共接口表；未通读 ASPM/RAS 全分支，NBIF 与 NBIO 仅作功能对照。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c) |
| [IO8：Linux MSI：通知写、向量分配与中断并发](../../IH/sources/IO8-linux-msi.md) | 解释 MSI/MSI-X 为什么是内存写形式的通知、如何与之前的数据写排序，以及多向量如何改变并发；适合 IH 到 CPU 的最后一段路径。 | 厂商/项目官方资料。已读基本原理、排序、向量 API、锁和诊断段；不是完整 PCIe 规范或中断控制器硬件说明。 | [原文](https://docs.kernel.org/6.12/PCI/msi-howto.html) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO11：PCI ATS/PRI/PASID：能力、额度与 PF/VF 共享](IO11-ats-pri-pasid.md) | 用于区分 ATS 缓存翻译、PRI 请求资源和 PASID 身份能力，重点是配置依赖、PF/VF 共享及队列深度编码；适合 IOMMU 与 PCIe 联读。 | 固定版本公开代码。已读 ATS、PRI、PASID enable/disable/restore、能力和额度处理；未读完整 PCIe 扩展规范或设备内部状态机。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/pci/ats.c) |
| [IO12：PCIe AER：严重性、报告权与恢复触发](IO12-aer-error-path.md) | 区分可纠正、不可纠正非致命与致命错误，并说明固件/OS 谁处理 AER；适合把链路错误连接到恢复策略，不能当作通用 ECC 规范。 | 厂商/项目官方资料。已读 AER 服务、_OSC、错误分类/日志和恢复回调段；未进行注错或实机恢复。 | [原文](https://docs.kernel.org/6.12/PCI/pcieaer-howto.html) |
| [IO13：NBIO 7.9：多 AID doorbell、分区与 replay 计数](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) | 扩展 NBIF 到多实例/分区场景，解释 doorbell 的双层配置和 replay 指标的实际来源；适合与 NBIO 7.4 比较代际差异。 | 固定版本公开代码。已读 SDMA/IH doorbell、aperture、partition 状态、初始化和 replay count；未系统阅读整个 RAS/电源路径。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c) |
| [MG6：IH 6.0：ring 地址、溢出与 doorbell 回收](../../IH/sources/MG6-ih60-ring-hardware.md) | 从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。 | 固定版本公开代码。已读 ring 控制/地址配置、get_wptr/set_rptr、rearm、self IRQ、软件初始化和 idle/reset 接口；未读目标 RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c) |
| [MG7：IH 公共代码：发布顺序、IV 解码与 checkpoint](../../IH/sources/MG7-ih-core-consumer.md) | 解释 producer/consumer ring 的内存顺序和 32 字节 IV 格式，覆盖 budget/restart、软件 ring 和 checkpoint；适合写 IH 完成与丢事件边界。 | 固定版本公开代码。已读 ring 分配、写入、处理、Vega10+ 解码及 checkpoint 等待；未把公共格式推广至旧代际。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c) |
| [MG12：Vega10 IH：不同 ring 的 wptr 来源与溢出处理](../../IH/sources/MG12-vega10-ih-comparison.md) | 通过另一代 IH 检查 ring 数量、writeback、地址和 overflow 差异；适合验证哪些结论可复用，避免只看 IH6.0 就推广所有 GPU。 | 固定版本公开代码。已读软件初始化、wptr/rptr、overflow/rearm 和公共解码绑定；原候选 ih_v5_0.c 路径不适用，实际来源以此文件为准。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/vega10_ih.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
