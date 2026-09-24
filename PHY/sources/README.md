# PHY 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 22 个可复用来源，主笔记归档 7 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 内存接口、时钟与校准 | [MEM1](../../UMC/sources/MEM1-pg276-hbm-controller.md) → [MEM4](MEM4-dfi-version-boundary.md) → [MEM5](MEM5-ug586-phy.md) → [MEM15](MEM15-pg150-dqs-gate.md) | 第 1–3 轮：先数字/电气边界，再训练观测和配置；UG586 所读是 LPDDR2，PG150 是另一个实例。 |
| 串行采样和协议训练 | [MEM6](MEM6-pcie-equalization.md) → [MEM7](MEM7-versal-cdr-equalizer.md) | 第 4 轮 PCIe 分支：CDR、均衡、眼图测量位置与协议阶段完成分开，done 必须带当前状态语境。 |
| D2D 与性能裕量 | [R14](R14-ucie-electrical-training.md) → [MEM8](MEM8-ucie-official-qa.md) → [R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md) → [MEM11](../../HBM/sources/MEM11-jedec-scope-gap.md) | 第 4–5 轮：lane/sideband 与协议重试分层；器件电气表未取得时不填写数值裕量或宣称合规。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [GC1：CDNA 2 的分片 L2、内存与互联边界](../../GC/sources/GC1-cdna2-memory.md) | 从 MI200 的公开整体结构理解 GCD 内 L2、内存控制器、HBM 和多种互联的分工。适合建立模块间地图与带宽层级；不提供内部队列或一致性状态机。 | 厂商/项目官方资料。精读打印页 2、5–8 的架构/存储/通信，视觉核对 p.3 Fig.1a；计算指令章节不在本笔记范围。 | [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf) |
| [P1：AMD GDC 2019：CCM、CS、CAKE 与本地/远端访存路径](../../DF/sources/P1-ryzen-fabric-topology.md) | 提供 CS、CAKE 等 AMD 名称的官方出处，并用本地 DRAM、同 die 其他 CCX、远端 die DRAM 三条路径说明一致性端点与传输层的分工；历史性能数字不可外推。 | 厂商/项目官方资料。已读取 PDF 的 cache/NUMA/本地及远端 refill 相关页；软件优化、编译器和核心流水线部分不是本笔记覆盖重点。 | [原文](https://gpuopen.com/gdc-presentations/2019/gdc-2019-s2-amd-ryzen-processor-software-optimization.pdf) |
| [FAB1：CDNA 3 白皮书：XCD/IOD、memory-side cache 与一致性层次](../../DF/sources/FAB1-cdna3-iod-memory.md) | 解释 CDNA 3 把计算侧 L2、IOD 存储侧 cache、HBM 与互联重新分配后的职责，特别区分 snoop filter、cache 数据和 CPU/GPU 统一内存；适合校准模块边界与带宽口径。 | 厂商/项目官方资料。已核读 XCD、memory architecture、IOD/Infinity Cache、HBM 和分区段落，重点印刷第 9–13 页；没有据此补写未公开的 DF 协议状态机。 | [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf) |
| [FAB5：AMDGPU XGMI：hive、节点拓扑、链路信息与 RAS](../../DF/sources/FAB5-xgmi-topology.md) | 从驱动观察 XGMI 多设备拓扑的建立、固件协作、hop/link 信息和错误入口；特别记录 v6.12 中 pstate 切换实际被提前返回禁用，防止把死代码当现行功能。 | 固定版本公开代码。已读 hive 生命周期、add/remove、PSP topology、hop/link 查询、pstate 和 RAS 入口；未获得 XGMI 私有线协议。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c) |
| [R21：ElastiStore：每 VC 槽位与共享弹性缓冲的取舍](../../SWITCH/sources/R21-elastistore.md) | 解释 ready/valid 反压流水为何需要额外吸收空间，以及 ElastiStore 用 V+1 个槽替代 2V 个槽时的结构和明确吞吐例外。 | 原始论文。已读 §II–V 的 elastic protocol、共享辅助槽、控制和 router 集成，以及论文明确列出的最坏阻塞情况。 | [原文](https://gdimitrak.github.io/papers/date14a.pdf) |
| [R10：UCIe 教程：协议层、D2D Adapter、CRC/retry 与状态协商](../../SWITCH/sources/R10-ucie-protocol-adapter.md) | 分清 FDI/RDI 两侧责任、raw/标准 flit 模式的可靠性归属，以及链路初始化/低功耗进入需要的多层握手；用于规划 die-to-die switch 边界。 | 厂商/项目官方资料。已读协议/flit 格式、adapter、初始化和 PM 示例；教程是 2023 版本背景，不代表后续所有 UCIe 修订。 | [原文](https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf) |
| [R11：UCIe 1.1 streaming：可复用可靠性不等于统一上层协议](../../SWITCH/sources/R11-ucie11-streaming.md) | 说明 UCIe 1.1 如何让非 PCIe/CXL 的 streaming payload 复用 adapter CRC/replay，并指出 Raw Mode、flit 格式协商和上层 CHI 打包的边界。 | 厂商/项目官方资料。已读完整正文；这是版本功能说明文章，未提供完整线格式与一致性事务规则。 | [原文](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay) |
| [R14：UCIe 电气教程：forwarded clock、训练、repair 与封装约束](R14-ucie-electrical-training.md) | 解释 UCIe die-to-die 物理层如何依赖封装距离、时钟/数据匹配、训练与 lane repair；用来区分链路可靠性、可用带宽和协议完成。 | 厂商/项目官方资料。已读 PHY architecture、clocking、BER/channel、LTSSM、initialization/repair 与 compliance 相关页；所有速率/距离/封装参数保留 2023 教程版本范围。 | [原文](https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf) |
| [MEM1：PG276：HBM 拓扑、地址映射、重排与错误边界](../../UMC/sources/MEM1-pg276-hbm-controller.md) | 研究请求进入内存控制器后为何排队、如何选 bank/行、何时返回错误。重点是两级重排、共享命令资源、地址映射对调度的影响；适合 UMC 主线与 EA/HBM 联读。 | 厂商/项目官方资料。已读上述章节正文；AMD FPGA HBM2 IP 实例，不是 GPU UMC 规格；未读全指南或运行 IP。 | [原文](https://docs.amd.com/r/en-US/pg276-axi-hbm) |
| [MEM4：DFI 官方资料：控制器与 PHY 的边界及 6.0 变化](MEM4-dfi-version-boundary.md) | 用于确定 controller/PHY 分工、训练所有权与规范版本；尤其修正“DFI 不支持 HBM”的过时概括。公开更新不能代替接口信号规范。 | 规范组织公开介绍。已读公开介绍与发布消息；未取得登录下载的完整 DFI 规范，不填写未核实的信号、时序或 HBM profile。 | [原文](https://ddr-phy.org/) |
| [MEM5：UG586：字节组 PHY 与初始化、校准分工](MEM5-ug586-phy.md) | 研究 DQ/DQS、相位调节、FIFO 和校准逻辑如何组成 PHY；用于从控制器侧跨到物理接口侧，需注意实际读取的是 LPDDR2 章节。 | 厂商/项目官方资料。已读上述路径实际解析到的 7 Series LPDDR2 PHY 架构/初始化说明；未核验全书各 DDR 类型训练顺序或图中全部阶段。 | [原文](https://docs.amd.com/r/en-US/ug586_7Series_MIS) |
| [MEM6：PG239：PCIe PHY 均衡阶段与完成语义](MEM6-pcie-equalization.md) | 解释 Preset Apply、接收适配、发送系数更新的不同阶段，适合 PCIe PHY 与链路状态机联读；重点是请求接受和适配完成的区别。 | 厂商/项目官方资料。已读均衡序列章节；产品规格仅作入口，未读完整 PCIe 规范或实现全部训练流程。 | [原文](https://docs.amd.com/r/en-US/pg239-pcie-phy/Product-Specification) |
| [MEM7：AM002：串行接收均衡与 CDR](MEM7-versal-cdr-equalizer.md) | 把链路误码问题分解为信道损耗、均衡与采样相位跟踪，适合 PHY 微架构入门；不提供 HBM 源同步接口或目标芯片的接收器设计。 | 厂商/项目官方资料。已读 Versal GTY/GTYP 接收器上述正文；未读全手册、未做眼图/BER 实测。 | [原文](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR) |
| [MEM8：UCIe 官方问答：侧带、lane 与链路延迟口径](MEM8-ucie-official-qa.md) | 澄清 UCIe 初代公开介绍中的 lane 模块化、侧带和延迟数字；用于 D2D 接口与 PHY 边界，避免把物理指标当系统事务性能。 | 厂商/项目官方资料。已读问答正文；不是当前最新规范，未据此推定后续版本的 FEC、训练或封装能力。 | [原文](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap) |
| [MEM9：Micron HBM3E：组织、容量与带宽口径](../../HBM/sources/MEM9-micron-hbm3e.md) | 提供 HBM3E 器件组织与产品级指标，用于容量/通道/带宽的数量级检查；不包含完整命令时序或端到端性能保证。 | 厂商/项目官方资料。已读产品说明及 FAQ；部分时间表仍为历史表述，不据此判定当前供货；未取得 datasheet。 | [原文](https://www.micron.com/products/memory/hbm/hbm3e) |
| [MEM11：JESD238：HBM3 正式标准入口与待补范围](../../HBM/sources/MEM11-jedec-scope-gap.md) | 这是完整规范尚未取得的缺口记录；用于判断哪些 HBM3 细节必须回查正式标准，不能作为时序、编码或合规依据。 | 规范全文未取得。未取得全文；不声明已读标准，不推定最新修订字母或具体字段。当前笔记是范围索引和后续补读任务。 | [原文](https://www.jedec.org/standards-documents/docs/jesd238) |
| [MEM13：Ramulator HBM3：层级状态、时序与生成式模型](../../HBM/sources/MEM13-ramulator-hbm3-model.md) | 适合逐项理解 HBM3 模型的共享/独立资源、命令依赖与时序作用范围；可与控制器代码联读，不能替代 JEDEC 标准。 | 固定版本公开代码。已读层级、命令/时序声明、命令总线分类及主要 timing 约束；未运行模型，未与完整 JEDEC 逐条核验。 | [原文](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/dram/impl/HBM3.cpp) |
| [MEM15：PG150：DQS gate 搜索、细调与失败定位](MEM15-pg150-dqs-gate.md) | 详细解释读数据门控如何找到 DQS 起始位置，覆盖粗/细调、重复采样、rank 统一及诊断；适合 PHY 校准专题，不能据此宣称已读所有训练阶段。 | 厂商/项目官方资料。已读 DQS gate 算法正文与失败定位说明；总阶段页图未成功读取，未据目录推定完整训练先后顺序。 | [原文](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Calibration-Stages) |
| [IO4：PCIe Base 5.0：规范入口与待补读范围](../../PCIE/sources/IO4-base-spec-gap.md) | 正式规范全文未取得的缺口记录，指明链路层/事务层哪些细节不能只靠 FPGA 指南推定；无需把它当成已完成的技术精读。 | 规范全文未取得。未取得全文；未声明规范合规阅读，版本以原有 5.0 登记为限，不推定当前最新标准。 | [原文](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0) |
| [MG2：SMU 13 公共控制：固件就绪、表地址和频率约束](../../SMU/sources/MG2-smu13-control.md) | 连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。 | 固定版本公开代码。已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) |
| [MG3：SMU 13.0.0 ABI：DPM 描述、表结构与指标语义](../../SMU/sources/MG3-smu13-firmware-abi.md) | 研究固件接口版本、参数表和 telemetry 的字段差异；重点是 target/pre-DS/post-DS、平均时间常数与累计量，适合设计可信观测表。 | 固定版本公开代码。已读版本、feature 定义、DpmDescriptor、PPTable 组合、DriverSmuConfig、DriverInfo 和 SmuMetrics；未逐字段研究完整板级参数/算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h) |
| [MG9：AMDGPU 温度/功耗接口：单位、策略与同步快照](../../SMU/sources/MG9-thermal-power-observability.md) | 用于设计性能实验的观测表，区分功率上限、实际功率、档位与平均频率；适合 SMU 的反馈路径，不是固件调频算法说明。 | 厂商/项目官方资料。已读 hwmon、performance level、pp_dpm 与 gpu_metrics 段；未执行任何调频、功耗或风扇写操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/thermal.html) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
