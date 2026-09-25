# 资料集与来源

更新日期：2026-09-25。当前 **103 篇独立来源笔记、19 个模块资料索引**。99 篇有正文、相关章节/函数、页图或官方介绍的阅读记录，其中 MEM11、MEM16 是公开规范转录的局部选读，原版图表待核；IO4 与 L1–L3 共 4 篇仍未取得本次可读正文。这些计数不是深度完成率，也不表示 99 本资料均全文精读。

本次补足 R1/VM5 定量条件、R8/VM10 协议细节、R13 原证明和 C01 缺页，新增 R23 CHI 正式规范与 MEM16 DFI 5.1 选读，更新 PHY 总阶段及 RSMU 直接证据。逐项结果及真实剩余项见[资料任务检查与补齐记录](source-reading-audit.md)。

原有 41 是上一阶段新增的 GC/VM/FAB/MEM/IO/MG 主条目数量，并非当时全项目所有历史资料。此次覆盖这些条目、旧 P/C/R/L 来源并补充新资料；P6 是分组，R17 与 IO3 同源，只保留一篇主笔记，不重复充数。一个编号可包含同一指南的多个章节，或一个机制必需的紧密关联代码文件；原文入口在笔记中逐一列出。

模块索引告诉你“这篇讲什么、何时读”；逐篇笔记保存技术细节、限制和位置；研究方案保存微架构问题及轮次。先读模块上下文/结构，再查索引和相关笔记，按需回原文。[维护范本 v1.4](chip-study-plan.md) · [项目上下文](project-context.md) · [研究路线图](research-roadmap.md)。

**使用状态：** 已完成笔记/索引建设及本次可访问范围的补读；原版规范、器件手册、外部 SDMA 与目标 CF 证据仍有具体缺口，不用来源数替代技术验收。

## 按模块查阅资料集

| 模块索引 | 主笔记数 | 含跨模块复用来源数 | 主线内容 |
| --- | --- | --- | --- |
| [GC](GC/sources/README.md) | 8 | 26 | 存储层次与 GL2 请求边界；GRBM/RLC 的选择状态与恢复；可见性与性能解释 |
| [UTCL1](UTCL1/sources/README.md) | 2 | 20 | 客户端身份、命中与 miss；合并、等待与资源释放；失效与地址空间复用 |
| [UTCL2](UTCL2/sources/README.md) | 11 | 30 | 整体结构、页表层级与回填；并发、fault、失效和外部翻译；预取、观测与纠错 |
| [HUBS](HUBS/sources/README.md) | 3 | 29 | Hub 集成及翻译服务边界；数据/地址交接与共享资源；失效、故障和通知 |
| [EA](EA/sources/README.md) | 2 | 30 | 请求接入与下游服务；共享存储、bank/group 与资格；返回、维护与性能解释 |
| [DF](DF/sources/README.md) | 8 | 43 | 本地/远端目标与身份；地址归属、hash 与 XGMI；事务完成、流控和恢复 |
| [SWITCH](SWITCH/sources/README.md) | 21 | 34 | 既有 Router 两轮的证据复查；NI、排序和协议映射；D2D 交接、进展与评估 |
| [UMC](UMC/sources/README.md) | 5 | 31 | 请求、映射与命令调度；PHY 交接与刷新/低功耗；错误、地址隔离与观测 |
| [PHY](PHY/sources/README.md) | 8 | 23 | 内存接口、时钟与校准；串行采样和协议训练；D2D 与性能裕量 |
| [HBM](HBM/sources/README.md) | 4 | 18 | 器件组织与数量级；命令、时序和维护；保护域与持续性能 |
| [PCIE](PCIE/sources/README.md) | 6 | 20 | BAR/DMA 与请求完成；有限资源、保序与翻译扩展；通知、链路和恢复 |
| [NBIF](NBIF/sources/README.md) | 2 | 21 | 窗口、目标和实例；主机交付与维护连接；事件、分区与异常 |
| [HDP](HDP/sources/README.md) | 4 | 17 | 历史职责与现代接口；维护与可见性闭环；低功耗、RAS 和代际差异 |
| [CF](CF/sources/README.md) | 1 | 18 | 命令身份与端点访问；接纳、排序和完成；共享状态与异常退出 |
| [SMU](SMU/sources/README.md) | 4 | 25 | 管理请求和共享表；策略约束与反馈；错误、事件和恢复 |
| [SMN](SMN/sources/README.md) | 2 | 13 | 管理访问入口与选择状态；端点与相邻接口；完成、低功耗和恢复 |
| [RSMU](RSMU/sources/README.md) | 2 | 11 | 模块身份与直接寄存器证据；端点访问及错误状态；可访问性与恢复责任 |
| [IH](IH/sources/README.md) | 5 | 23 | 事件记录、内存和解码；通知和来源处理；溢出、恢复与吞吐 |
| [SDMA](SDMA/sources/README.md) | 5 | 27 | 目标接口与外部范围；系统提交、寻址与维护；完成、事件和恢复 |

主笔记数合计 103；复用来源数不能相加。所有来源保留原编号；固定 tag/commit 和具体章节/函数见各笔记。

## 用户说明

- **U1：** 本次任务给出的模块清单、HUBS（mmhub、CH）与 SDMA（FE、BE、TBE）分组；SDMA 独立项目只读；后续由用户补充新模块资料。
- **U2：** 用户明确纠正模块名称为 GRBM。
- **U3：** 用户明确允许 UTCL1 这类公共模块独立建目录，即使某个实例位于 TBE 内部。
- **U4：** `original_file/` 仅供本地查看，不得上传 GitHub 或其他云端服务。
- **U5：** SOC 项目仅关联 `soc_repo`，取消独立 `sdma_repo` 的附加关联；SDMA 文件继续独立管理。
- **U6：** GitHub 同步只包含当前已有文件，不补回已缺失的五份 Markdown 正文。
- **U7：** 用户说明已建立云端 `niyingsong123/soc_study` 环境，并希望连接该环境；本条不表示本地任务已经切换到云端。
- **U8：** 用户要求以高质量公开资料研究 NoC 与 D2D 的完整微架构，按六轮迭代维护 `switch/`；本次明确授权在云端开始第二轮 Router 专项。具体轮次和执行边界见 [研究进度](switch/RESEARCH_PROGRESS.md)。

- **U9（2026-09-24）：** 用户明确 SWITCH 仅完成两轮，原六轮规划可根据新研究修订；其他模块轮数按需增减。当前先用高质量资料逐模块完成研究与撰写方案，详细内容由后续本地 Codex 展开；各模块规划完成后再评估跨模块研究。U8 的固定六轮安排是当时计划，后续可按本条复核调整。
- **U10（2026-09-24）：** 用户要求始终以整体微架构为基础规划子模块和 feature：先建立结构与工作流程，再分解研究，并把每轮结果整合回整体微架构。
- **U11（2026-09-24）：** 用户明确本项目以 AMD 芯片和 AMD 模块命名为基础。学习前应查找行业别名、通用术语及功能相关名称，扩大高质量资料范围；例如 UTCL2 可以联合 MMU 主题研究。最终方案以 AMD 命名组织。这里记录用户的研究方向，不据此宣称两个模块完全等价；适用边界须在研究中核实。具体执行规则见 [项目上下文](project-context.md)。

- **U12（2026-09-24）：** 用户要求在规划具体子模块、feature 或其他研究内容时，把发现的相关资料链接附在对应内容旁，供后续本地 Codex 学习。具体执行方式见 [研究范本](chip-study-plan.md)的“挂接资料并编排研究轮次”。

- **U13（2026-09-24）：** 用户要求审视当前规划是否遗漏必要内容，以及哪些步骤多余、缺乏意义或会增加云端与本地 Codex 的思考负担。根据该要求整理的精简执行方法见 [研究范本](chip-study-plan.md)；具体取舍是规划方法，不作为目标芯片的技术事实。

- **U14（2026-09-24）：** 用户明确确认最终六步实施计划，授权按计划执行，并要求在真正开展模块规划前将计划保存到 GitHub，作为以后芯片学习可持续维护和更新的范本。已确认版本集中保存于 [chip-study-plan.md](chip-study-plan.md)，当前项目应用与进度另见 [project-context.md](project-context.md)。

- **U15（2026-09-24）：** 用户要求阅读各种资料时维护资料集，简单介绍每份资料主要讲的内容并附链接，帮助在大量阅读后保持清晰、方便后续接续；据此重新整理计划并更新长期维护范本。方法更新记录于 [chip-study-plan.md](chip-study-plan.md) v1.1。

- **U16（2026-09-24）：** 用户补充要求提醒后续 Codex 资料集的存在，可在模块上下文中保存资料内容或位置，由助手选择。当前采用在模块上下文/README 中保存资料集入口、覆盖范围和阅读顺序，简介留在资料集，避免重复占用上下文。

- **U17（2026-09-24）：** 用户建议按数据上下游的逻辑研究模块，先研究上游，再研究下游，并要求将这一原则更新到长期维护范本。具体执行方式见 [chip-study-plan.md](chip-study-plan.md) v1.2；研究顺序须结合代表性场景与有依据的微架构路径确定。

- **U18（2026-09-24）：** 用户确认按已维护的计划正式实施。本次完成各模块的研究与论文规划、资料集及接续入口；详细论文留给后续本地 Codex，实际轮次单独记录。

- **U19（2026-09-24）：** 用户要求在既有 41 个规划主条目基础上继续扩充各模块资料，为每份新旧资料分别整理核心内容与重要细节，文档统一存入模块下的资料子目录，并更新上下文和入口。
- **U20（2026-09-24）：** 用户强调笔记应足够详细，减少后续 Codex 反复阅读原资料，并支持未来多次跨模块复用；已授权实施所有既有及新增来源的整理。
- **U21（2026-09-24）：** 用户要求每篇资料都有索引，说明大致内容，帮助 Codex 判断是否值得阅读；后续明确要求继续实施。当前采用模块 sources/README.md 的逐篇导读与唯一主笔记。


- **U22（2026-09-25）：** 用户要求按资料任务检查报告补齐未完成工作；本次执行正文补读、笔记加深、证据纠正及索引/上下文同步。访问受限项保留可执行的本地接续范围，不冒充完成。

## 本地只读参考

外部目录为 `D:\project\no_preject\sdma_repo`，仅引用，不复制或修改。L1–L3 是本项目编号，外部 S1–S9 编号保持原义。本次没有访问外部全文，详情见以下范围笔记。
### L1

[外部 SDMA 术语表：既有登记与复查入口](SDMA/sources/L1-external-glossary-scope.md) · 外部本地路径见笔记 · 外部入口·未重读

用于查项目专用 CF/DF、FE/BE/TBE、UTCL1/UTCL2 含义；当前只保存原仓库登记范围，必须在本地可访问外部项目时复查原文。

### L2

[外部 shaobo 摘要：两条后端路径的待复查接口](SDMA/sources/L2-external-shaobo-scope.md) · 外部本地路径见笔记 · 外部入口·未重读

原登记涉及 FE 两条后端路径、CF_IF/DF_IF、TBE 内 UTCL1、UTCL2 请求和 MMHUB 写回；适合后续本地核实 SDMA 与 SoC 的连接。

### L3

[外部 SDMA 待确认问题：保留 anshi TBE 边界](SDMA/sources/L3-external-open-questions.md) · 外部本地路径见笔记 · 外部入口·未重读

用于接续未决问题，特别是 anshi TBE 的剩余职责；当前没有原文，禁止用公开驱动或 shaobo 架构把未知项自动填满。

## 公开参考

### P1

[AMD GDC 2019：CCM、CS、CAKE 与本地/远端访存路径](DF/sources/P1-ryzen-fabric-topology.md) · [原文](https://gpuopen.com/gdc-presentations/2019/gdc-2019-s2-amd-ryzen-processor-software-optimization.pdf) · 厂商/项目官方资料

提供 CS、CAKE 等 AMD 名称的官方出处，并用本地 DRAM、同 die 其他 CCX、远端 die DRAM 三条路径说明一致性端点与传输层的分工；历史性能数字不可外推。

### P2

[AMDGPU 驱动中的 IP 边界与系统入口](GC/sources/P2-amdgpu-hardware.md) · [原文](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure) · 厂商/项目官方资料

解释 Linux 如何按 IP 组织 GPU，以及 GMC、GC/RLC、SDMA、SMU、IH 的职责。适合首次建立系统边界；查具体队列或硬件协议时应转入对应代码笔记。

### P3

[gfx115x GL2 的访问边界与计数口径](GC/sources/P3-gl2-metrics.md) · [原文](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gl2-cache.html) · 厂商/项目官方资料

把 GL2 命中、客户请求和向 GCEA 下发的流量分开，适合建立缓存到仲裁器的观测模型。它提供计数语义，不提供 GL2 队列深度或替换算法。

### P4

[GRBM 活动计数与利用率解释](GC/sources/P4-grbm-utilization.md) · [原文](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/grbm.html) · 厂商/项目官方资料

说明 GRBM 提供哪些粗粒度忙碌度观测，以及为什么 GPU Busy、GL2C Busy 不能直接证明吞吐或瓶颈。研究 GRBM 寄存器选址和 RLC 协同时应联读 GC2。

### P5

[MI200 的翻译、EA credit 与在途请求计数](GC/sources/P5-mi200-counters.md) · [原文](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html) · 厂商/项目官方资料

提供可操作的观测点：UTCL1 translation/permission miss、UTCL2 busy、EA 按 IO/GMI/DRAM 分类的 credit stall，以及在途请求积分。适合做跨模块性能诊断，但不是目标芯片的计数器规格。

## P6：Switch 公开研究资料组

R1–R22 保留 SWITCH 原有编号体系并补 R22。第 1、2 轮事实与模型执行结果见[真实研究进度](switch/RESEARCH_PROGRESS.md)；旧引用关系可在[详细稿](switch/switch_detailed_guide.md)及 Git 历史复查。本次扩充来源笔记，不执行第 3–6 轮。R9 是 CHI 模型用户指南，R12 是 Arm 架构介绍，均不能替代正式 CHI 规范。

### R1

[Peh/Dally：流水 router 延迟模型与推测分配](SWITCH/sources/R1-pipelined-router-delay.md) · [原文](https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf) · 原始论文

保存 router 级划分与逻辑努力公式、FO4 对照、8×8 mesh 实验配置及不同 buffer/VC 的结果；适合比较周期、吞吐和 credit 周转，所有数值保留原工艺与工作负载。

### R2

[Mullins 等：look-ahead、预计算仲裁与单周期 router](SWITCH/sources/R2-low-latency-vc-router.md) · [原文](https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf) · 原始论文

解释低延迟 router 如何把控制从数据关键路径移开，以及空闲后多个新请求到达时为何需要冲突检测/撤销；用于约束低延迟方案的真实前提。

### R3

[BookSim 论文：模型边界、两阶段更新与性能实验口径](SWITCH/sources/R3-booksim-method.md) · [原文](https://icn.kaist.ac.kr/~jjk12/papers/2013ISPASS.pdf) · 原始论文

说明微架构仿真如何保持真实并行时序、建模 credit 延迟和源端排队，并揭示局部公平与全局公平、年龄优先与吞吐之间的区别。

### R4

[Garnet 2.0：NI、router、vnet 与流水模型总览](SWITCH/sources/R4-garnet-overview.md) · [原文](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/) · 厂商/项目官方资料

建立 gem5 网络模型的组件与参数语义，区分协议 vnet、物理链路、VC 和端点缓冲；适合阅读具体 allocator/credit 代码前使用。

### R5

[Garnet SwitchAllocator：两级选择、发送资格与最终提交](SWITCH/sources/R5-garnet-switch-allocator.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc) · 固定版本公开代码

逐步说明 SA-I/SA-II 怎样选择 flit、何时分配 outVC、扣 credit、弹出输入及更新 RR；重点是有请求与允许发送之间的差别。

### R6

[Garnet Input/OutputUnit：VC 状态与 credit 往返](SWITCH/sources/R6-garnet-input-output-credit.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/InputUnit.cc) · 固定版本公开代码

配对追踪接收 flit、保存路由、流水等待、输入释放和下游 free-credit 返回，避免把 buffer 空槽与 packet 的 VC ownership 混为一个状态。

### R7

[FlooNoC 论文：宽物理网络、AXI 并发流与端点重排](SWITCH/sources/R7-floonoc-paper.md) · [原文](https://arxiv.org/html/2409.17606v1) · 原始论文

说明宽链路 NoC 如何把 AXI 排序放在 NI、用响应存储预约保证可接收，并比较带 ROB 与限制同 ID 目标的两种设计；适合作为 AMD switch 的行业对照。

### R8

[AMBA AXI：握手、独立通道、ID 顺序与完成边界](SWITCH/sources/R8-axi-ordering-contract.md) · [原文](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) · 规范选读

保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。

### R9

[CHI Protocol Bundle 用户指南：模型接口与 credit 回调](SWITCH/sources/R9-chi-model-user-guide.md) · [原文](https://documentation-service.arm.com/static/5ed104c1ca06a95ce53f8869) · CHI 模型用户指南

这是 Arm SoC Designer 仿真组件指南，展示 CHI 通道、模型转换器和回调如何接线；可用于理解模型边界，不能作为 CHI 一致性事务规范。

### R10

[UCIe 教程：协议层、D2D Adapter、CRC/retry 与状态协商](SWITCH/sources/R10-ucie-protocol-adapter.md) · [原文](https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf) · 厂商/项目官方资料

分清 FDI/RDI 两侧责任、raw/标准 flit 模式的可靠性归属，以及链路初始化/低功耗进入需要的多层握手；用于规划 die-to-die switch 边界。

### R11

[UCIe 1.1 streaming：可复用可靠性不等于统一上层协议](SWITCH/sources/R11-ucie11-streaming.md) · [原文](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay) · 厂商/项目官方资料

说明 UCIe 1.1 如何让非 PCIe/CXL 的 streaming payload 复用 adapter CRC/replay，并指出 Raw Mode、flit 格式协商和上层 CHI 打包的边界。

### R12

[Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层](SWITCH/sources/R12-arm-system-architecture.md) · [原文](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749) · Arm 架构概述

提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。

### R13

[Dally/Seitz：CDG 定理的前提、证明与虚通道构造](SWITCH/sources/R13-channel-dependency-scope.md) · [原文](https://authors.library.caltech.edu/records/fd0yr-br438) · 原始论文正文选读

解释确定性 wormhole 路由为何需要检查 channel dependency graph，保存定理假设、双向证明要点、环网/torus 的 VC 断环构造和系统应用边界；适合 SWITCH 的路由、VC 与死锁研究。

### R14

[UCIe 电气教程：forwarded clock、训练、repair 与封装约束](PHY/sources/R14-ucie-electrical-training.md) · [原文](https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf) · 厂商/项目官方资料

解释 UCIe die-to-die 物理层如何依赖封装距离、时钟/数据匹配、训练与 lane repair；用来区分链路可靠性、可用带宽和协议完成。

### R15

[FlooNoC router RTL：参数化队列、路由裁剪与握手边界](SWITCH/sources/R15-floonoc-router-code.md) · [原文](https://github.com/pulp-platform/FlooNoC/blob/c58f1bf13baeda147b4e87e961683d389db090a1/hw/floo_router.sv) · 固定版本公开代码

从固定版本 RTL 识别输入 FIFO、route select、输出仲裁、可选输出 FIFO 和 VC/物理通道复用，并记录代码较原论文的新能力和端点握手约束。

### R16

[Remote Control：独立无死锁 chiplet 组合后的环路风险](SWITCH/sources/R16-remote-control-deadlock.md) · [原文](https://arxiv.org/pdf/1910.04882) · 原始论文

解释多个内部无死锁网络连接后仍可能互相阻塞，以及出口整包缓冲预约如何切断跨 chiplet 依赖；用于规划 die-to-die 组合正确性。

### R17

与 [IO3](PCIE/sources/IO3-linux-dma-api.md) 同源：Linux DMA API，研究地址、所有权与可见性。保留旧编号，详细笔记只维护一份。

### R18

[iSLIP：VOQ、Request/Grant/Accept 与指针更新](SWITCH/sources/R18-islip-matching.md) · [原文](https://www.cs.cmu.edu/~dga/15-744/S07/papers/islip-ton.pdf) · 原始论文

解释交叉开关的两侧匹配、RR 指针为何必须与接受结果关联，以及多轮匹配的第一轮更新规则；用于区分单输出仲裁与多输入多输出分配。

### R19

[BookSim BufferState：共享池、保留槽与 tail-credit 释放](SWITCH/sources/R19-booksim-buffer-state.md) · [原文](https://github.com/booksim/booksim2/blob/28f43299f1706a3160ffac721ca461d74eb6e618/src/buffer_state.cpp) · 固定版本公开代码

区分总容量、per-VC 占用、共享池、保留槽和 VC ownership，并解释不同 buffer policy 与 tail-credit 配置怎样改变可发送条件。

### R20

[Tamir/Frazier：动态多队列缓冲与共享存储实现](SWITCH/sources/R20-damq-buffer.md) · [原文](https://web.cs.ucla.edu/~tamir/papers/isca88.pdf) · 原始论文

解释 DAMQ 怎样用每目的队列与共享 free list 同时减少 HOL 和静态分区浪费，保留指针阵列、头尾、分块分配和 cut-through 的关键实现条件。

### R21

[ElastiStore：每 VC 槽位与共享弹性缓冲的取舍](SWITCH/sources/R21-elastistore.md) · [原文](https://gdimitrak.github.io/papers/date14a.pdf) · 原始论文

解释 ready/valid 反压流水为何需要额外吸收空间，以及 ElastiStore 用 V+1 个槽替代 2V 个槽时的结构和明确吞吐例外。

### R22

[Garnet NI：终点背压、tail 保留与协议缓冲依赖](SWITCH/sources/R22-garnet-network-interface.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/NetworkInterface.cc) · 固定版本公开代码

说明网络到达终点后仍可能因协议 MessageBuffer 无空间而持有 tail/VC，并解释 credit、回调和消息交付的关系；用于补齐端到端依赖分析。

### R23

[CHI E.a 原始规范：事务资源、顺序、重试与链路 credit](SWITCH/sources/R23-chi-ea-protocol.md) · [原文](https://documentation-service.arm.com/static/6087f99b5e70d934bc69f1f0) · 正式规范选读

从 CHI 正式规范解释 RN/HN/SN、四类通道、TxnID/DBID 生命周期、完成与可见性、P-Credit/L-Credit 以及链路低功耗收敛；适合 SWITCH/DF/GC 的行业协议对照，不是 AMD fabric 实现说明。

## 规划阶段对既有 SWITCH 来源的补充阅读

上一阶段定向阅读与本次更深阅读的历史由 Git 保存；当前实际阅读范围以 R 系列逐篇笔记为准。规范版本、论文与当前代码差异、摘要范围及性能例外均已纳入笔记。

## GC：缓存与控制

### GC1

[CDNA 2 的分片 L2、内存与互联边界](GC/sources/GC1-cdna2-memory.md) · [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf) · 厂商/项目官方资料

从 MI200 的公开整体结构理解 GCD 内 L2、内存控制器、HBM 和多种互联的分工。适合建立模块间地图与带宽层级；不提供内部队列或一致性状态机。

### GC2

[GC 9.4.3 的 GRBM 选址与 RLC 控制闭环](GC/sources/GC2-gfx943-rlc-grbm.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c) · 固定版本公开代码

从驱动调用看实例选择、广播、safe-mode、RLC 启停和门控顺序。适合恢复控制路径的状态与握手；不等同 RLC 固件或硬件内部算法。

### GC3

[LLVM AMDGPU 内存模型：等待、缓存维护与一致性域](GC/sources/GC3-llvm-memory-model.md) · [原文](https://github.com/llvm/llvm-project/blob/llvmorg-18.1.7/llvm/docs/AMDGPUUsage.rst) · 固定版本公开代码

解释 acquire/release 为什么需要组合等待与 cache 操作，以及 gfx90a/gfx942 的 agent、L2 和远端内存条件。研究“写完成”“缓存可见”“TLB 失效”之间的区别时应优先读。

### GC4

[RLC 公共层：软件状态、保存区与硬件回调](GC/sources/GC4-rlc-common.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_rlc.c) · 固定版本公开代码

补足 GC2 的上层：safe-mode 的软件标志如何维护、保存恢复数据由谁分配。适合判断驱动状态与硬件状态是否被错误等同。

## 翻译、hub 与仲裁

### VM1

[GPUVM 的地址空间、VMID、PASID 与 aperture](UTCL2/sources/VM1-gpuvm-address-spaces.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c) · 固定版本公开代码

建立 GPUVA、页表、动态 VMID、PASID 与系统地址的基本关系；尤其适合防止把 GPUVM 和系统 IOMMU 合并为一个翻译器。

### VM2

[MMHUB 2.x 的地址范围、翻译缓存与 fault 配置](HUBS/sources/VM2-mmhub-v2.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c) · 固定版本公开代码

按初始化顺序整理 MMHUB 软件可见的服务结构：页表根、aperture、TLB/cache、VM context、失效引擎和 fault。适合构建 hub 控制面；不证明完整内部数据网络。

### VM3

[GMC v9 的 GPUVM 失效：请求、ACK、hub 与电源状态](UTCL2/sources/VM3-gpuvm-invalidation.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c) · 固定版本公开代码

详细追踪 GPUVM invalidate 的软件发起与完成观察，包含 VMID/PASID 转换、不同 hub、KIQ 与直接寄存器路径及旧 ACK 风险。适合建立维护事务闭环。

### VM4

[AMD IOMMU 驱动的多级翻译缓存失效与完成等待](UTCL2/sources/VM4-amd-iommu-commands.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c) · 固定版本公开代码

说明为什么更新系统映射后可能需要同时处理 IOMMU 内部缓存和 ATS 设备 IOTLB，并追踪 command queue 与 completion wait。适合与本地 GPUVM invalidate 对比。

### VM5

[MASK：把地址翻译需求传递到共享缓存和 DRAM 调度](UTCL2/sources/VM5-mask-paper.md) · [原文](https://rausavar.github.io/pubs/mask-asplos18.pdf) · 原始论文

解释 token/fill 与两种 cache 旁路、DRAM 三队列预算；保存公式、容量、工作负载筛选、基线与吞吐/公平性结果，适合 UTCL2–EA–UMC 的翻译干扰研究。

### VM6

[GCEA 的接纳、停顿、目标与返回观测](EA/sources/VM6-gcea-metrics.md) · [原文](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gcea.html) · 厂商/项目官方资料

按 read/write、SARB 和 return 三个边界整理 gfx115x 的 GCEA 指标，帮助判断请求缺乏、下游背压和返回受阻的区别。

### VM7

[gem5 Vega TLB：查找、回填、属性与模型简化](UTCL1/sources/VM7-gem5-vega-tlb.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/tlb.cc) · 固定版本公开代码

提供一套可以沿函数追踪的 TLB 模型，解释命中、miss、回填和返回。尤其记录其 ASID、fault 与失效处理的简化，避免后续 Codex 把模拟器当成完整硬件规格。

### VM8

[gem5 Vega 页表遍历器的依赖状态与端口重试](UTCL2/sources/VM8-gem5-page-walker.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/pagetable_walker.cc) · 固定版本公开代码

具体解释一个 page walk 如何保存上下文、逐级读 PDE/PTE、等待内存、遇到背压重试并回填。适合建立 walker 与缓存/内存服务之间的接口。

### VM9

[翻译请求合并：时间窗、在途表与响应展开](UTCL1/sources/VM9-gem5-coalescer.md) · [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/tlb_coalescer.cc) · 固定版本公开代码

解释多个同页请求如何共用一次下游翻译，以及如何保留每个请求的 offset、返回端口和统计数量。适合研究 miss 合并与有限资源；明确模型的多地址空间限制。

### VM10

[AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约](UTCL2/sources/VM10-iommu-spec.md) · [原文](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf) · 规范选读

用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。

### VM11

[动态 VMID 的租用、复用与页表更新依赖](UTCL2/sources/VM11-vmid-lifetime.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c) · 固定版本公开代码

解释为什么 VMID 不能当作永久进程编号，以及驱动如何用 active fence、页表根和 flush 进度防止过早复用。适合连接提交队列、翻译上下文与完成事件。

### VM12

[GFXHUB 2.0 与 MMHUB 的编程模型对照](HUBS/sources/VM12-gfxhub-v2.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c) · 固定版本公开代码

用另一 hub 的公开实现对照页表根、地址 aperture、翻译 cache、context 与失效入口，帮助区分共享编程概念与真实物理归属。

### EA1

[轮转仲裁 RTL：成功传输、背压锁定与公平性](EA/sources/EA1-rr-arbiter.md) · [原文](https://github.com/pulp-platform/common_cells/blob/e73baaec2ca665cd80c3c384e9258e35242b829c/src/cc_rr_arb_tree.sv) · 固定版本公开代码

提供能追踪到状态更新的仲裁器参考，解释选中、grant、真正交付和优先级轮转的区别。适合补足 EA 方案中的可实现机制，但不代表 AMD EA 采用本设计。

## Fabric、地址与完成

### FAB1

[CDNA 3 白皮书：XCD/IOD、memory-side cache 与一致性层次](DF/sources/FAB1-cdna3-iod-memory.md) · [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf) · 厂商/项目官方资料

解释 CDNA 3 把计算侧 L2、IOD 存储侧 cache、HBM 与互联重新分配后的职责，特别区分 snoop filter、cache 数据和 CPU/GPU 统一内存；适合校准模块边界与带宽口径。

### FAB2

[Linux DF 3.6：通道编码、hash、实例访问与性能计数器](DF/sources/FAB2-df36-registers-counters.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c) · 固定版本公开代码

从 AMDGPU 的 DF 3.6 回调识别软件能观察的配置与计数器生命周期，特别说明寄存器编码不等于实际通道数、计数器零值也可能来自未支持或重装失败。

### FAB3

[AMD ATL：从 UMC 归一化地址恢复系统物理地址](DF/sources/FAB3-atl-address-core.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c) · 固定版本公开代码

展示 RAS 地址解码必须结合 socket/die/CS、DRAM map、interleave/hash、base 与 MMIO hole；用于避免把 UMC 错误地址直接解释成系统 PA。

### FAB4

[dma-fence：完成对象、时间线与硬件语义的边界](DF/sources/FAB4-dma-fence-contract.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h) · 固定版本公开代码

解释 fence 的 context/seqno、signal/error、callback 与 lifetime，帮助区分软件完成对象和硬件 flush/fence 操作；跨模块研究完成语义时必读。

### FAB5

[AMDGPU XGMI：hive、节点拓扑、链路信息与 RAS](DF/sources/FAB5-xgmi-topology.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c) · 固定版本公开代码

从驱动观察 XGMI 多设备拓扑的建立、固件协作、hop/link 信息和错误入口；特别记录 v6.12 中 pstate 切换实际被提前返回禁用，防止把死代码当现行功能。

### FAB6

[AMD ATL denormalize：非二次幂通道与 hash 的逆向重建](DF/sources/FAB6-atl-denormalization.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/denormalize.c) · 固定版本公开代码

解释 3/5 倍通道模式为何不能靠插入几位 channel ID 还原 PA，以及 DF4.5 如何枚举丢失位和余数，再用正向映射与 CS 身份校验候选地址。

### FAB7

[AMDGPU fence：ring 完成写回、序号槽位和异常收敛](DF/sources/FAB7-amdgpu-fence-lifecycle.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c) · 固定版本公开代码

把抽象 dma-fence 落到 AMDGPU 的 ring 命令、写回内存、序号表、中断/定时器与回收流程，适合研究数据完成怎样变成软件可等待事件。

## 控制器、PHY 与 HBM

### MEM1

[PG276：HBM 拓扑、地址映射、重排与错误边界](UMC/sources/MEM1-pg276-hbm-controller.md) · [原文](https://docs.amd.com/r/en-US/pg276-axi-hbm) · 厂商/项目官方资料

研究请求进入内存控制器后为何排队、如何选 bank/行、何时返回错误。重点是两级重排、共享命令资源、地址映射对调度的影响；适合 UMC 主线与 EA/HBM 联读。

### MEM2

[Ramulator 2.0：控制器、DRAM 模型与验证边界](UMC/sources/MEM2-ramulator2-paper.md) · [原文](https://arxiv.org/html/2308.11030v2) · 原始论文

解释如何把请求调度、命令前置条件、时序状态和维护策略拆开建模；适合搭建 UMC 教学模型与理解验证覆盖，不是 AMD UMC 实现说明。

### MEM3

[AMDGPU RAS：错误计数、坏页与恢复策略](UMC/sources/MEM3-amdgpu-ras.md) · [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) · 厂商/项目官方资料

从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。

### MEM4

[DFI 官方资料：控制器与 PHY 的边界及 6.0 变化](PHY/sources/MEM4-dfi-version-boundary.md) · [原文](https://ddr-phy.org/) · 规范组织公开介绍

用于确定 controller/PHY 分工、训练所有权与规范版本；尤其修正“DFI 不支持 HBM”的过时概括。公开更新不能代替接口信号规范。

### MEM5

[UG586：字节组 PHY 与初始化、校准分工](PHY/sources/MEM5-ug586-phy.md) · [原文](https://docs.amd.com/r/en-US/ug586_7Series_MIS) · 厂商/项目官方资料

研究 DQ/DQS、相位调节、FIFO 和校准逻辑如何组成 PHY；用于从控制器侧跨到物理接口侧，需注意实际读取的是 LPDDR2 章节。

### MEM6

[PG239：PCIe PHY 均衡阶段与完成语义](PHY/sources/MEM6-pcie-equalization.md) · [原文](https://docs.amd.com/r/en-US/pg239-pcie-phy/Product-Specification) · 厂商/项目官方资料

解释 Preset Apply、接收适配、发送系数更新的不同阶段，适合 PCIe PHY 与链路状态机联读；重点是请求接受和适配完成的区别。

### MEM7

[AM002：串行接收均衡与 CDR](PHY/sources/MEM7-versal-cdr-equalizer.md) · [原文](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR) · 厂商/项目官方资料

把链路误码问题分解为信道损耗、均衡与采样相位跟踪，适合 PHY 微架构入门；不提供 HBM 源同步接口或目标芯片的接收器设计。

### MEM8

[UCIe 官方问答：侧带、lane 与链路延迟口径](PHY/sources/MEM8-ucie-official-qa.md) · [原文](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap) · 厂商/项目官方资料

澄清 UCIe 初代公开介绍中的 lane 模块化、侧带和延迟数字；用于 D2D 接口与 PHY 边界，避免把物理指标当系统事务性能。

### MEM9

[Micron HBM3E：组织、容量与带宽口径](HBM/sources/MEM9-micron-hbm3e.md) · [原文](https://www.micron.com/products/memory/hbm/hbm3e) · 厂商/项目官方资料

提供 HBM3E 器件组织与产品级指标，用于容量/通道/带宽的数量级检查；不包含完整命令时序或端到端性能保证。

### MEM10

[Samsung HBM3：产品指标与 ODECC 表述边界](HBM/sources/MEM10-samsung-hbm3.md) · [原文](https://semiconductor.samsung.com/dram/hbm/hbm3/) · 厂商/项目官方资料

用于与 HBM3E 对照容量和原始带宽，并识别器件内部 ECC 宣传与系统 RAS 的区别；不提供可实现的 ECC 编码或命令规范。

### MEM11

[JESD238A：伪通道共享、命令与时钟边界选读](HBM/sources/MEM11-jedec-scope-gap.md) · [原文](https://studylib.net/doc/28550091/jesd238a-hbm3) · 规范正文转录选读·原版图表待核

从 JESD238A 的公开正文转录整理 PC 的独立与共享资源、行列命令接口及 CK/DQS 关系；可用于 HBM/UMC 的架构骨架，精确时序图和编码仍需原版核验。

### MEM12

[Ramulator 当前 HBM 控制器：双命令槽与 FRFCFS](UMC/sources/MEM12-ramulator-hbm-controller.md) · [原文](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/impl/hbm34_controller.cpp) · 固定版本公开代码

研究请求如何变成可发出的列/行命令，以及优先级、激活缓冲和共享命令总线怎样约束吞吐；提供代码级 UMC 对照实例。

### MEM13

[Ramulator HBM3：层级状态、时序与生成式模型](HBM/sources/MEM13-ramulator-hbm3-model.md) · [原文](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/dram/impl/HBM3.cpp) · 固定版本公开代码

适合逐项理解 HBM3 模型的共享/独立资源、命令依赖与时序作用范围；可与控制器代码联读，不能替代 JEDEC 标准。

### MEM14

[UMC 8.10 驱动：错误分类与地址候选展开](UMC/sources/MEM14-umc810-ras-address.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c) · 固定版本公开代码

研究错误地址为何不是现成系统物理地址，以及 UE 计数为何可能没有可隔离页面；提供具体寄存器与转换路径，适合 RAS 联读。

### MEM15

[PG150：DQS gate 搜索、细调与失败定位](PHY/sources/MEM15-pg150-dqs-gate.md) · [原文](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Calibration-Stages) · 厂商/项目官方资料

解释 DQS gate 搜索、重复采样、跨 rank 收敛，并补 2022 原图的整体训练分支与灰色未实现项；适合建立 PHY 阶段、配置和业务放行的关系。

### MEM16

[DFI 5.1：启动、训练交接与读写有效期选读](PHY/sources/MEM16-dfi51-interface.md) · [原文](https://studylib.net/doc/27487094/ddr-phy-interface-specification-v5-1) · 规范正文转录选读·原版图表待核

补足 DFI 官网介绍之外的接口机制：启动完成代表什么、PHY 如何取得训练控制、写命令与数据怎样对齐、读返回为什么不能假定固定连续延迟。适合 UMC/PHY 边界研究，不覆盖 DFI 6.0 HBM profile。

## 主机与控制接口

### IO1

[PG213：TLP 接收、选择性流控与跨接口保序](PCIE/sources/IO1-pg213-transactions.md) · [原文](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation) · 厂商/项目官方资料

围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。

### IO2

[Linux Device I/O：MMIO、Posted write 与访问顺序](HDP/sources/IO2-linux-device-io.md) · [原文](https://docs.kernel.org/6.12/driver-api/device-io.html) · 厂商/项目官方资料

解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。

### IO3

[Linux DMA API：地址、所有权、同步和 scatter-gather](PCIE/sources/IO3-linux-dma-api.md) · [原文](https://docs.kernel.org/6.12/core-api/dma-api-howto.html) · 厂商/项目官方资料

用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。

### IO4

[PCIe Base 5.0：规范入口与待补读范围](PCIE/sources/IO4-base-spec-gap.md) · [原文](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0) · 规范全文未取得

正式规范全文未取得的缺口记录，指明链路层/事务层哪些细节不能只靠 FPGA 指南推定；无需把它当成已完成的技术精读。

### IO5

[NBIO 7.4：主机窗口、doorbell 与 HDP/IH 接口](NBIF/sources/IO5-nbio74-host-bridge.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c) · 固定版本公开代码

提供 NBIF 可对应的公开 NBIO 软件接口，重点是 framebuffer 访问开关、doorbell 译码范围、HDP remap 和 IH 配置；适合建立主机桥边界。

### IO6

[HDP 4.0 驱动：flush、invalidate 与 RAS 代际差异](HDP/sources/IO6-hdp40-maintenance.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c) · 固定版本公开代码

研究 HDP 维护命令怎样由 CPU 或 ring 发起、哪些 IP 跳过 invalidate，以及计数清除为何有读清/写清区别；用于准确写完成与恢复边界。

### IO7

[AMD 15h BKDG：HDP 历史职责与 UMA 窗口](HDP/sources/IO7-bkdg-hdp-history.md) · [原文](https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/50742_15h_Models_60h-6Fh_BKDG.pdf) · 厂商/项目官方资料

HDP 全称和 host framebuffer 地址转换的 AMD 原厂历史依据；适合确认命名与窗口概念，不能作为现代 GPU 容量/拓扑参数。

### IO8

[Linux MSI：通知写、向量分配与中断并发](IH/sources/IO8-linux-msi.md) · [原文](https://docs.kernel.org/6.12/PCI/msi-howto.html) · 厂商/项目官方资料

解释 MSI/MSI-X 为什么是内存写形式的通知、如何与之前的数据写排序，以及多向量如何改变并发；适合 IH 到 CPU 的最后一段路径。

### IO9

[Linux PCI 恢复：隔离、诊断、复位与恢复 I/O](PCIE/sources/IO9-pci-error-recovery.md) · [原文](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html) · 厂商/项目官方资料

提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。

### IO10

[GC 9.0 驱动：实例选择、异步寄存器访问与 HDP 完成](CF/sources/IO10-gfx90-register-control.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c) · 固定版本公开代码

研究 GRBM 共享选择状态、异步读回，以及 ring 按引擎/pipe 发起 HDP request/done 等待；适合控制事务与维护完成联读，不扩展 CU/CP 内部或推定真实 CF 拓扑。

### IO11

[PCI ATS/PRI/PASID：能力、额度与 PF/VF 共享](PCIE/sources/IO11-ats-pri-pasid.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/pci/ats.c) · 固定版本公开代码

用于区分 ATS 缓存翻译、PRI 请求资源和 PASID 身份能力，重点是配置依赖、PF/VF 共享及队列深度编码；适合 IOMMU 与 PCIe 联读。

### IO12

[PCIe AER：严重性、报告权与恢复触发](PCIE/sources/IO12-aer-error-path.md) · [原文](https://docs.kernel.org/6.12/PCI/pcieaer-howto.html) · 厂商/项目官方资料

区分可纠正、不可纠正非致命与致命错误，并说明固件/OS 谁处理 AER；适合把链路错误连接到恢复策略，不能当作通用 ECC 规范。

### IO13

[NBIO 7.9：多 AID doorbell、分区与 replay 计数](NBIF/sources/IO13-nbio79-partition-doorbell.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c) · 固定版本公开代码

扩展 NBIF 到多实例/分区场景，解释 doorbell 的双层配置和 replay 指标的实际来源；适合与 NBIO 7.4 比较代际差异。

### IO14

[HDP 6.0：维护提交与时钟/存储低功耗切换](HDP/sources/IO14-hdp60-power-sequence.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c) · 固定版本公开代码

研究 HDP power/clock 配置的顺序约束和代际地址差异，适合把低功耗放回可访问性与状态保持主线；不能据此推导 SRAM retention 细节。

## 管理与事件

### MG1

[SMU 公共驱动：mailbox、错误状态与表传输](SMU/sources/MG1-smu-message-table.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) · 固定版本公开代码

详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。

### MG2

[SMU 13 公共控制：固件就绪、表地址和频率约束](SMU/sources/MG2-smu13-control.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) · 固定版本公开代码

连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。

### MG3

[SMU 13.0.0 ABI：DPM 描述、表结构与指标语义](SMU/sources/MG3-smu13-firmware-abi.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h) · 固定版本公开代码

研究固件接口版本、参数表和 telemetry 的字段差异；重点是 target/pre-DS/post-DS、平均时间常数与累计量，适合设计可信观测表。

### MG4

[AMD SMN：index/data 访问与错误判定](SMN/sources/MG4-smn-indirect-access.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c) · 固定版本公开代码

解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。

### MG5

[RSMU 寄存器线索与 UMC 6.1 访问模式](RSMU/sources/MG5-rsmu-umc-index.md) · [原文](https://github.com/torvalds/linux/commit/245219a66085332a30e4653db3542ea5654ff762) · 固定版本公开代码

用 AMD 作者提交确认 remote SMU 名称及寄存器接口/错误/复位职责，配合 UMC index-mode 保存恢复与 BOWEN 参考位置；目标实例/内部实现仍未知。

### MG6

[IH 6.0：ring 地址、溢出与 doorbell 回收](IH/sources/MG6-ih60-ring-hardware.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c) · 固定版本公开代码

从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。

### MG7

[IH 公共代码：发布顺序、IV 解码与 checkpoint](IH/sources/MG7-ih-core-consumer.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c) · 固定版本公开代码

解释 producer/consumer ring 的内存顺序和 32 字节 IV 格式，覆盖 budget/restart、软件 ring 和 checkpoint；适合写 IH 完成与丢事件边界。

### MG8

[AMDGPU IRQ：来源分派、引用计数与复位恢复](IH/sources/MG8-irq-dispatch-lifecycle.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c) · 固定版本公开代码

研究 IH 解码后如何路由给 IP/KFD、如何管理中断使能引用，以及 reset 后如何恢复；适合把事件传输连接到实际处理者。

### MG9

[AMDGPU 温度/功耗接口：单位、策略与同步快照](SMU/sources/MG9-thermal-power-observability.md) · [原文](https://docs.kernel.org/6.12/gpu/amdgpu/thermal.html) · 厂商/项目官方资料

用于设计性能实验的观测表，区分功率上限、实际功率、档位与平均频率；适合 SMU 的反馈路径，不是固件调频算法说明。

### MG10

[AMD ATL system.c：Fabric 身份字段与版本发现](SMN/sources/MG10-atl-system-identity.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/system.c) · 固定版本公开代码

解释 socket/die/node/component ID 的代际解码和未知版本处理；适合控制寻址与错误地址定位的前置研究，不能用固定移位套所有芯片。

### MG11

[UMC 6.7：错误地址展开与 poison 模式的代际对照](RSMU/sources/MG11-umc67-ras-comparison.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c) · 固定版本公开代码

补充 RSMU 相邻的 UMC RAS 路径，解释 hash/列位模糊如何扩大隔离候选，及 poison 查询如何依赖寄存器；用于对照 UMC 8.10。

### MG12

[Vega10 IH：不同 ring 的 wptr 来源与溢出处理](IH/sources/MG12-vega10-ih-comparison.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/vega10_ih.c) · 固定版本公开代码

通过另一代 IH 检查 ring 数量、writeback、地址和 overflow 差异；适合验证哪些结论可复用，避免只看 IH6.0 就推广所有 GPU。

## SDMA 公开系统接口

### SD1

[AMDGPU SDMA 公共层：实例、固件和 RAS 接口](SDMA/sources/SD1-sdma-system-lifecycle.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c) · 固定版本公开代码

只研究 SDMA 如何接入 SoC：ring 到实例映射、固件版本条件、ECC 通知和复位责任；不替代外部 SDMA 项目的 FE/BE/TBE 内部资料。

### SD2

[SDMA 5.2：doorbell、维护命令、fence 与 trap](SDMA/sources/SD2-sdma52-completion-maintenance.md) · [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c) · 固定版本公开代码

把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。

## 新资料登记方式

每个来源维护一个稳定编号、一篇主笔记及模块索引导读。笔记记录来源/版本、实际阅读位置、机制与关键细节、状态/资源和完成语义、适用边界及可复用问题；缺失全文据实记录。共享资料通过链接复用，紧密关联文件说明组合范围；不以链接或文件数量替代技术深度。见[范本](chip-study-plan.md)。

## C01–C05：历史转换登记与当前状态

原件统一平铺保存在本地 `original_file/`，保留原文件名与字节内容，禁止上传。表中的 Markdown 路径只用于标识缺失正文，不作为可点击入口。页数来自历史登记；版本以原文为准，不凭文件名推定适用产品。

| 编号 | 原件名称（仅本地） | 原 Markdown 路径与当前状态 | 页数 | GitHub 与本地可读资源 |
| --- | --- | --- | --- | --- |
| C01 | `tb_mm_utcl2.pptx` | `UTCL2/tb_mm_utcl2.md`（缺失） | 49 | [现有图像](UTCL2/assets/tb_mm_utcl2/) |
| C02 | `UTCL2 结构和使用简介 by Wang Junmin.pptx` | `UTCL2/UTCL2 结构和使用简介 by Wang Junmin.md`（缺失） | 38 | [现有图像](UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin/) |
| C03 | `utcl2_top.pdf` | `UTCL2/utcl2_top.md`（缺失） | 1 | [现有图像](UTCL2/assets/utcl2_top/) |
| C04 | `UTCL2地址翻译及预取技术介绍.pdf` | `UTCL2/UTCL2地址翻译及预取技术介绍.md`（缺失） | 26 | [现有图像](UTCL2/assets/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D/) |
| C05 | `MMHUB_introduction.pptx` | `HUBS/MMHUB_introduction.md`（缺失） | 41 | [现有图像](HUBS/assets/MMHUB_introduction/) |

[历史转换报告](conversion-report.md) · [历史 SHA-256 清单](source-manifest.json)。这些记录保留当时的结果，不能作为五份正文当前存在的证明。C01 第 6 页引用的 `code_coverage_improve.xlsx` 未提供；当前仅保留该附件缺失的记录。

### 本次页图阅读与技术笔记

本次使用仓库已提交的页面图像进行文字阅读，并直接核看关键结构/表格；没有访问或上传 original_file/，没有恢复缺失的转换正文。C01 第 1、4 页本次未取得有效图像，其余读取范围见笔记。部分页带 HYGON 标识，统一作为用户参考设计，与 AMD 官方或目标 shaobo/anshi 证据区分。C04 地址算例存在错误，已在笔记保留原问题和独立核算；C01/C05 的 VM 类型标签差异没有强行统一。

### C01

[MM_UTCL2 图示与验证环境：从翻译事务到可观测检查点](UTCL2/sources/C01-mm-utcl2-testbench.md) · [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/tb_mm_utcl2) · 用户页图·参考设计

覆盖 MM_UTCL2 的 APT1/2/3、VML2/ATCL2、fault/retry、两类失效以及验证环境，适合建立请求生命周期和验证检查点；所有容量与字段均须保留该资料版本范围。

### C02

[UTCL2 结构与使用：页表格式、cache 映射和 BigK 性能反例](UTCL2/sources/C02-utcl2-cache-organization.md) · [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin) · 用户页图·参考设计

解释 Group/VML2/Walker/ATC 的分工、PTE cache 的 bank/set/way/tag、表布局粒度与映射粒度的区别，并保存 BigK 增大反而禁止填充的具体案例。

### C03

[UTCL2 总图：GPUVM、ATC 与 walker 的资源边界](UTCL2/sources/C03-utcl2-topology.md) · [原文](https://github.com/niyingsong123/soc_study/blob/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/utcl2_top/page-001.png) · 用户页图·参考设计

从一张总图建立请求入口、VML2 bank、walker、ATCL2 与返回网络的关系，适合快速判断一个 feature 应放在哪个子模块；图中的实例数只属于该图配置。

### C04

[地址翻译与预取：rdif 扩展、资源竞争和已核算勘误](UTCL2/sources/C04-translation-prefetch.md) · [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D) · 用户页图·参考设计

把常见翻译预取思想与资料中 shaobo 的 rdif 方案分开，说明 history table、独立预取缓存、需求请求优先和返回分类；同时记录地址例题和阈值描述中的问题。

### C05

[MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界](HUBS/sources/C05-mmhub-dagb-ea.md) · [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/HUBS/assets/MMHUB_introduction) · 用户页图·参考设计

连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。

