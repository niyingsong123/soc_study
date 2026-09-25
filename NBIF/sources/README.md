# NBIF 资料索引与逐篇技术笔记

更新日期：2026-09-25。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 21 个可复用来源，主笔记归档 2 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 窗口、目标和实例 | [IO5](IO5-nbio74-host-bridge.md) → [IO13](IO13-nbio79-partition-doorbell.md) → [IO3](../../PCIE/sources/IO3-linux-dma-api.md) | 第 1–2 轮：NBIO 是功能参照；framebuffer、doorbell、self-ring 与实例/AID 映射分开。 |
| 主机交付与维护连接 | [IO1](../../PCIE/sources/IO1-pg213-transactions.md) → [IO2](../../HDP/sources/IO2-linux-device-io.md) → [IO6](../../HDP/sources/IO6-hdp40-maintenance.md) → [IO14](../../HDP/sources/IO14-hdp60-power-sequence.md) | 第 2–3 轮：HDP remap 的寄存器位置不证明 HDP 数据存储归属，posted write 不等于目标完成。 |
| 事件、分区与异常 | [MG6](../../IH/sources/MG6-ih60-ring-hardware.md) → [IO8](../../IH/sources/IO8-linux-msi.md) → [IO9](../../PCIE/sources/IO9-pci-error-recovery.md) → [IO12](../../PCIE/sources/IO12-aer-error-path.md) | 第 3–4 轮：ring 地址/权限、replay 指标、故障隔离与恢复分别找证据。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [C05：MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。 | 用户页图·参考设计。读取 41 页可提取文字，直接核看第 7、18、27、32、33、34、40 页关键图表；图中缺乏的 RTL 时序、RAM 端口数和严格完成定义保持未知。 | 原图已移出仓库 |
| [R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界](../../SWITCH/sources/R8-axi-ordering-contract.md) | 保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。 | 规范选读。已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion，并补核 A3.4 burst/error 与 A7.2 exclusive；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。 | [原文](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) |
| [IO1：PG213：TLP 接收、选择性流控与跨接口保序](../../PCIE/sources/IO1-pg213-transactions.md) | 围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。 | 厂商/项目官方资料。已读所列正文；FPGA PCIe4 IP 的接口实例，不是完整 PCIe Base 规范或 AMD GPU PCIe RTL。 | [原文](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation) |
| [IO2：Linux Device I/O：MMIO、Posted write 与访问顺序](../../HDP/sources/IO2-linux-device-io.md) | 解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。 | 厂商/项目官方资料。已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。 | [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) |
| [IO3：Linux DMA API：地址、所有权、同步和 scatter-gather](../../PCIE/sources/IO3-linux-dma-api.md) | 用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。 | 厂商/项目官方资料。已读地址关系、DMA mask、coherent/streaming、方向、map/sync/unmap、scatter-gather 与错误处理段；未验证某硬件平台。 | [原文](https://docs.kernel.org/6.12/core-api/dma-api-howto.html) |
| [IO4：PCIe Base 5.0：规范入口与待补读范围](../../PCIE/sources/IO4-base-spec-gap.md) | 正式规范全文未取得的缺口记录，指明链路层/事务层哪些细节不能只靠 FPGA 指南推定；无需把它当成已完成的技术精读。 | 规范全文未取得。未取得全文；未声明规范合规阅读，版本以原有 5.0 登记为限，不推定当前最新标准。 | [原文](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0) |
| [IO5：NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口](IO5-nbio74-host-bridge.md) | 提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。 | 固定版本公开代码。已读所列窗口、doorbell、HDP、IH 函数、无 BIF ring 的 RAS controller 中断路径及公共接口表；未通读 ASPM/RAS 全分支，NBIF 与 NBIO 仅作功能对照。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c) |
| [IO6：HDP 4.0 驱动：flush、invalidate 与 RAS 代际差异](../../HDP/sources/IO6-hdp40-maintenance.md) | 研究 HDP 维护命令怎样由 CPU 或 ring 发起、哪些 IP 跳过 invalidate，以及计数清除为何有读清/写清区别；用于准确写完成与恢复边界。 | 固定版本公开代码。已读 flush/invalidate、RAS query/reset、初始化及相关代际判断；没有目标硬件测试。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c) |
| [IO7：AMD 15h BKDG：HDP 历史职责与 UMA 窗口](../../HDP/sources/IO7-bkdg-hdp-history.md) | HDP 全称和 host framebuffer 地址转换的 AMD 原厂历史依据；适合确认命名与窗口概念，不能作为现代 GPU 容量/拓扑参数。 | 厂商/项目官方资料。已读上述 GMC、framebuffer、HDP 正文及配置表；未研读整本寄存器手册。 | [原文](https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/50742_15h_Models_60h-6Fh_BKDG.pdf) |
| [IO8：Linux MSI：通知写、向量分配与中断并发](../../IH/sources/IO8-linux-msi.md) | 解释 MSI/MSI-X 为什么是内存写形式的通知、如何与之前的数据写排序，以及多向量如何改变并发；适合 IH 到 CPU 的最后一段路径。 | 厂商/项目官方资料。已读基本原理、排序、向量 API、锁和诊断段；不是完整 PCIe 规范或中断控制器硬件说明。 | [原文](https://docs.kernel.org/6.12/PCI/msi-howto.html) |
| [IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](../../PCIE/sources/IO9-pci-error-recovery.md) | 提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。 | 厂商/项目官方资料。已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。 | [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) |
| [IO10：GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成](../../CF/sources/IO10-gfx90-register-control.md) | 研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。 | 固定版本公开代码。已读实例选择/恢复、KIQ clock 读回、HDP request/done 及 WAIT_REG_MEM helper 的字段和失败路径；不是目标 CF 拓扑证据。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c) |
| [IO11：PCI ATS/PRI/PASID：能力、额度与 PF/VF 共享](../../PCIE/sources/IO11-ats-pri-pasid.md) | 用于区分 ATS 缓存翻译、PRI 请求资源和 PASID 身份能力，重点是配置依赖、PF/VF 共享及队列深度编码；适合 IOMMU 与 PCIe 联读。 | 固定版本公开代码。已读 ATS、PRI、PASID enable/disable/restore、能力和额度处理；未读完整 PCIe 扩展规范或设备内部状态机。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/pci/ats.c) |
| [IO12：PCIe AER：严重性、报告权与恢复触发](../../PCIE/sources/IO12-aer-error-path.md) | 区分可纠正、不可纠正非致命与致命错误，并说明固件/OS 谁处理 AER；适合把链路错误连接到恢复策略，不能当作通用 ECC 规范。 | 厂商/项目官方资料。已读 AER 服务、_OSC、错误分类/日志和恢复回调段；未进行注错或实机恢复。 | [原文](https://docs.kernel.org/6.12/PCI/pcieaer-howto.html) |
| [IO13：NBIO 7.9：多 AID doorbell、分区与 replay 计数](IO13-nbio79-partition-doorbell.md) | 扩展 NBIF 到多实例/分区场景，解释 doorbell 的双层配置和 replay 指标的实际来源；适合与 NBIO 7.4 比较代际差异。 | 固定版本公开代码。已读 SDMA/IH doorbell、aperture、partition 状态、初始化和 replay count；未系统阅读整个 RAS/电源路径。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c) |
| [IO14：HDP 6.0：维护提交与时钟/存储低功耗切换](../../HDP/sources/IO14-hdp60-power-sequence.md) | 研究 HDP power/clock 配置的顺序约束和代际地址差异，适合把低功耗放回可访问性与状态保持主线；不能据此推导 SRAM retention 细节。 | 固定版本公开代码。已读完整短文件的 flush、clock-gating 更新及查询；未取得目标电源状态机/电气规范。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c) |
| [MG5：RSMU 寄存器线索与 UMC 6.1 访问模式](../../RSMU/sources/MG5-rsmu-umc-index.md) | 用 AMD 作者提交确认 remote SMU 名称及寄存器接口/错误/复位职责，配合 UMC index-mode 保存恢复与 BOWEN 参考位置；目标实例/内部实现仍未知。 | 固定版本公开代码。已读 AMD 原始提交 245219a、两份 v0.0.2 头及 Linux v6.12 UMC index/RAS 调用；不声明取得完整 RSMU 规格。 | [原文](https://github.com/torvalds/linux/commit/245219a66085332a30e4653db3542ea5654ff762) |
| [MG6：IH 6.0：ring 地址、溢出与 doorbell 回收](../../IH/sources/MG6-ih60-ring-hardware.md) | 从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。 | 固定版本公开代码。已读 ring 控制/地址配置、get_wptr/set_rptr、rearm、self IRQ、软件初始化和 idle/reset 接口；未读目标 RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c) |
| [MG12：Vega10 IH：不同 ring 的 wptr 来源与溢出处理](../../IH/sources/MG12-vega10-ih-comparison.md) | 通过另一代 IH 检查 ring 数量、writeback、地址和 overflow 差异；适合验证哪些结论可复用，避免只看 IH6.0 就推广所有 GPU。 | 固定版本公开代码。已读软件初始化、wptr/rptr、overflow/rearm 和公共解码绑定；原候选 ih_v5_0.c 路径不适用，实际来源以此文件为准。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/vega10_ih.c) |
| [SD1：AMDGPU SDMA 公共层：实例、固件和 RAS 接口](../../SDMA/sources/SD1-sdma-system-lifecycle.md) | 只研究 SDMA 如何接入 SoC：ring 到实例映射、固件版本条件、ECC 通知和复位责任；不替代外部 SDMA 项目的 FE/BE/TBE 内部资料。 | 固定版本公开代码。已读实例查找、上下文地址条件、固件头/feature 与 RAS 入口；未复制或修改独立 sdma_repo，未研究目标 FE/BE/TBE RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c) |
| [SD2：SDMA 5.2：doorbell、维护命令、fence 与 trap](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) | 把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。 | 固定版本公开代码。已读 ring get/set_wptr、mem_sync、HDP flush、VM flush、pipeline sync、fence 和 trap handler；未扩写引擎内部 packet 全规格或 FE/BE/TBE 论文。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
