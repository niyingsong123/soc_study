# 资料集与来源

基础整理日期：2026-09-23；Switch 第二轮公开研究补充：2026-09-24。公开文档用于解释术语和提供架构参考，不能证明本项目目标芯片的具体实现。初始化时读取本地 Markdown 摘要。C01–C05 留有历史转换与校验记录，但五份 Markdown 正文当前缺失；用户选择只同步现有文件，不补回正文。当前状态见 [项目上下文](project-context.md)，未进行目标芯片 RTL 核验。

本页兼作资料集总入口，复用既有来源编号与分类。后续阅读时为相关资料补充简短内容介绍、链接、对应研究主题和实际阅读范围；模块资料较多时可链接该模块的资料集。条目以实际读到的部分为准，未读资料标为待查；不因建立资料集而把历史登记改记为已读。维护方式见 [研究范本](chip-study-plan.md)。

## 按模块查阅资料集

本次新增来源是支持规划的定向阅读，详细轮次尚未执行。来源摘要集中在本页；模块 README 与方案直接引用，不额外复制书目。完整规范未取得或仅阅读官网简介的条目已明确标为候选/局部阅读。

| 研究主题 | 主条目入口 | 主要内容 |
| --- | --- | --- |
| GC：GL2、GRBM、RLC | [GC1–GC2](#gc1)，复用 P2–P5 | AMD 存储结构与公开寄存器/固件控制接口 |
| UTCL1、UTCL2、HUBS、EA | [VM1–VM6](#vm1)，复用 P2/P3/P5 | GPUVM、MMHUB、失效、IOMMU、翻译研究及 GCEA 观察 |
| DF、CF | [FAB1–FAB4](#fab1)，复用 P1/P6 | AMD 互联、地址归属、公开驱动与完成语义参照 |
| SWITCH | [P6 与已有 R1–R21](#p6switch-公开研究资料组)，补充 FAB1 | NI、Router、D2D、进展与后续性能研究 |
| UMC、PHY、HBM | [MEM1–MEM11](#mem1)，复用 MG5 | 控制器/器件/PHY 参考与标准、训练、RAS 边界 |
| PCIe、NBIF、HDP | [IO1–IO10](#io1) | 事务与地址、主机窗口、HDP 维护、通知与恢复 |
| SMU、SMN、RSMU、IH | [MG1–MG8](#mg1) | 管理请求、间接访问、RSMU 接口线索、事件 ring |
| SDMA 系统接口 | 本页 L1–L3、P2 及相邻模块主条目 | 仅复用已有摘要与公开系统边界，内部正文在外部项目 |

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

## 本地只读参考

下列相对链接指向仓库之外的独立 SDMA 项目，仅在本地对应目录存在时可用，GitHub 仓库中不包含这些文件。

- **L1：[SDMA 术语表](../sdma_repo/docs/context/glossary.md)**：CF/DF、FE/BE/TBE、UTCL1/UTCL2 的本项目语义。配合 [项目上下文](../sdma_repo/docs/project-context.md)。
- **L2：[shaobo 架构摘要](../sdma_repo/docs/context/shaobo.md)**：FE 两条后端路径、CF_IF/DF_IF、TBE 内 UTCL1、UTCL2 请求及 MMHUB 写回。其原始依据为外部项目 S1「dma_utcl1」「Dma_ce」与 S2「子模块划分」等，定位见 [外部原始资料目录](../sdma_repo/docs/sources.md)。
- **L3：[SDMA 待确认问题](../sdma_repo/docs/context/open-questions.md)**：特别保留 anshi TBE 的剩余职责未确定这一边界。

外部目录为 `D:\project\no_preject\sdma_repo`。这里只引用，不复制或修改其文件。L1–L3 是本项目引用编号；外部 S1–S9 的编号保持原义。

## 公开参考

- **P1：[AMD Ryzen Processor Software Optimization，GDC 2019](https://gpuopen.com/gdc-presentations/2019/gdc-2019-s2-amd-ryzen-processor-software-optimization.pdf)**，2019-03-20，第 21 页：SDF、CS、CAKE、UMC 的参考架构与术语。适用 Ryzen 示例；只支持 DF 相关主题的初步归档，不能确定 shaobo/anshi 的 RTL 父级。 本次规划复读打印页 21–23 的术语和 local/remote refill 抽取文字：用于辨认 CCM、SDF transport、CS、CAKE、UMC 的参考职责，不复制 CPU 产品的参数或拓扑到目标 GPU。
- **P2：[Linux AMDGPU Core Driver Infrastructure — GPU Hardware Structure](https://docs.kernel.org/gpu/amdgpu/driver-core.html#gpu-hardware-structure)**：GC 包含 RLC、IH 和 SMU 基本职责、内存 hub 的架构差异。在线文档查询日期 2026-09-23，未固定内核提交。 本次定向阅读同一文档的在线 hub/client 连接说明，以及 [Linux 6.12 固定版本](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure)开头的 GMC、IH、SMU、SDMA、GC/RLC 职责。前者随在线版本变化，后者可固定复查；没有全文研读或目标 RTL 核验。
- **P3：[AMD ROCm Compute Profiler — GL2 cache](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.1/conceptual/rdna/gl2-cache.html)**：gfx115x 的 GL2 与 GCEA 访问路径，不能直接推广到所有 GPU。 本次原链接读取未成功，实际已读 [docs-7.14.0 / Profiler 3.7.0 的同名页](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gl2-cache.html)中 GL2 cache、performance、request statistics、bandwidth。适用 RDNA3.5/gfx115x；资料提供 GL2/GCEA 的观察边界及命中/请求/带宽口径，指出 EA 方向请求可能由系统级 cache 服务，不能以 DRAM 命名推定每次访问实际到 DRAM。目标队列和算法仍无直接证据。
- **P4：[AMD ROCm Compute Profiler — Graphics Register Bus Manager](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.1/conceptual/rdna/grbm.html)**：GRBM 名称、图形/计算活动统计主题。
- **P5：[AMD ROCm 6.0.0 — MI200 performance counters and metrics](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html)**，2024-01-16：EA、UTCL1、UTCL2、GRBM、HBM 缩写与计数器参考。同页 CS 指 Compute Shader，说明缩写必须结合上下文，不能直接替换 DF 语境的 Coherent Slave。 本次沿用既有术语登记；页面入口/搜索结果可见，但具体 UTCL 章节定位遇到访问限流，未增加完整阅读或计数器核验声明，后续使用具体事件时须复查。

## P6：Switch 公开研究资料组

登记日期：2026-09-24。完整来源条目、版本和引用关系在 [详细微架构稿](switch/switch_detailed_guide.md)第 37、48 章，使用该文内部的 R1–R21 编号，不覆盖本页的 L/P/C 编号。第一轮完整稿另存 [v2.0 历史原稿](switch/switch_detailed_guide_v2.0.md)。

第二轮实际重点阅读与对照如下；只声明阅读所列章节和源码，不声明完成全部文献或规范的合规核验。

| 对应编号 | 来源与版本 | 本轮阅读定位及用途 |
|---|---|---|
| R1 | Peh/Dally，2001，[Router 延迟与推测架构论文](https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf) | VC/推测流水、credit turnaround；用于空间闭环和失败路径 |
| R2 | Mullins/West/Moore，ISCA 2004，[低延迟 VC Router](https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf) | Router 结构与控制路径；不采用其工艺数字作为本项目参数 |
| R5 | gem5 tag `v24.1.0.1`，[SwitchAllocator.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc) | `arbitrate_inports/outports`、成功路径和指针更新；blob `e31733d42e1d2a84f5afc86050a8209367983aa1` |
| R18 | Nick McKeown，IEEE/ACM ToN 7(2)，1999，[iSLIP 原论文](https://www.cs.cmu.edu/~dga/15-744/S07/papers/islip-ton.pdf) | 第 III、VI、IX 节，第一迭代指针更新与 matching；原场景是固定 cell 输入排队交换机 |
| R19 | BookSim2 commit `28f43299f1706a3160ffac721ca461d74eb6e618`，[buffer_state.cpp](https://github.com/booksim/booksim2/blob/28f43299f1706a3160ffac721ca461d74eb6e618/src/buffer_state.cpp) | 私有/共享容量、SendingFlit/ProcessCredit/TakeBuffer；blob `228d91d0ab1a221cf6ced0461e650959eecce0f8` |
| R20 | Yuval Tamir、Gregory L. Frazier，ISCA 1988，[High-Performance Multi-Queue Buffers for VLSI Communication Switches](https://web.cs.ucla.edu/~tamir/papers/isca88.pdf) | 第 III 节、buffer organisation 与 timing；用于共享数据/指针/free pool 的实现对照 |
| R21 | I. Seitanidis、A. Psarras、G. Dimitrakopoulos、C. Nicopoulos，DATE 2014，[ElastiStore](https://gdimitrak.github.io/papers/date14a.pdf) | 第 II–IV 节与 Fig.1–5，弹性 VC、共享辅助槽和反压；未合入本轮 mesh 模型 |

本轮代码是原创教学模型，不是以上实现的重命名副本；模型运行结果登记在 [round2_results.json](switch/examples/round2_results.json)，验证范围见 [研究进度](switch/RESEARCH_PROGRESS.md)。公开资料不证明目标芯片 SWITCH 属于 DF、连接 CAKE 或采用某一协议。

## 规划阶段对既有 SWITCH 来源的补充阅读

阅读日期：2026-09-24。下列条目仍沿用 P6/R 编号；它们补充资料简介与本次定位，不表示完成 SWITCH 新一轮研究。

| 原编号与直达入口 | 主要内容、研究用途和本次阅读范围 |
| --- | --- |
| [R7：FlooNoC v1](https://arxiv.org/html/2409.17606v1) | 提供 NI 端点排序与 NoC 组织的公开实现研究。已读 III-A 的 ROB/限制注入取舍、III-C 及 IV-A 开头；IV–V 完整实验/物理实现细节留第 5 轮，不据其参数推定 AMD 实现。 |
| [R8：AXI IHI0022H](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf) | 用于 NI 请求/响应契约与保序研究，CF 仅借鉴规则写法。已读 A3.3、A5.2 相关返回排序及 A6.1–A6.6 的抽取段落；未核验全规范合规，AMD 目标采用的协议待确认。 |
| [R10：UCIe Hot Chips 2023 Protocol 教程](https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf) | 解释分层、Raw/格式职责、链路状态和初始化。已读打印页 27、34、36–45 的相关文字；它是当时模式的教程，不能替代匹配版本正式规范。 |
| [R11：UCIe 1.1 Streaming 官方说明](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay) | 用于识别 Streaming/Raw 与差错处理的版本变化；本次复读其背景说明，精确模式和字段留待正式规范，原创 LRP-64 不因此成为 UCIe 实现。 |
| [R16：Modular SoC 原论文 v1](https://arxiv.org/pdf/1910.04882v1) | 讨论跨 chiplet 引入的资源等待与模块化进展问题。已读引言和第 2 节；Remote Control 全算法/证明未重做，也不作为本仓库 PRE/POST 教学设计的证明。 |

## GC：缓存与控制：本次规划来源

### GC1

- 原名与链接：[Introducing AMD CDNA 2 Architecture](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf)；本次读取官网 17 页白皮书，2026-09-24。
- 主要内容：介绍 MI200 的 GCD、分片 L2、内存接口和多种主机/加速器互联配置。第 5 页将 L2 排队、仲裁、原子操作及特定平台的一致性放在系统存储层次中说明。
- 研究用途：GC 的 L2 结构/下游带宽与 DF/SWITCH 的互联边界；目标 shaobo/anshi 参数不能直接套用。CDNA L2/TCC 与本目录 GL2 按功能对照，不能默认名称和实现一一对应。
- 实际阅读：正文 p.2、p.4–5 的结构/存储说明，以及 p.5–8 的通信与一致性段落；未逐页完整研读计算单元或矩阵指令章节。读过的文本能支持定向规划，不作为队列/协议完整实现规格。

### GC2

- 原名与链接：[Linux v6.12 — gfx_v9_4_3.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c)，Git blob c100845409f7948cd060c2e44d978aec8bf35997。
- 主要内容：GC 9.4.3 驱动呈现 GRBM 的实例/广播选择、RLC 寄存器访问控制、safe-mode 握手，以及启停、复位、恢复与 clock-gating 的软件编程序列。
- 研究用途：GRBM 和 RLC 的控制微架构边界、共享选择状态、固件/驱动职责、控制完成和超时；代码不是 RLC 固件或目标 RTL。
- 实际阅读：gfx_v9_4_3_xcc_select_se_sh；is_rlc_enabled、xcc_set/unset_safe_mode、init_rlcg_reg_access_ctrl；xcc_rlc_stop/reset/start/resume 和 rlc_resume；xcc_update_gfx_clock_gating（约 L692–717、1364–1440、1488–1550、1597–1635、2710–2762）。其他部分未完整阅读。

## 翻译、hub 与仲裁：本次规划来源

### VM1

- **原名与链接：** Linux `drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c`，[v6.12 固定 tag](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c)，blob `6005280f5f38f07c0b5c5f583f1b4e273ac117e9`。
- **主要内容：** 开头 GPUVM 说明从软件接口介绍 GPU 地址空间、VMID/页表、访问权限和 VMID 0 的特殊 aperture；系统地址在有 IOMMU 时可处于 IOVA 语境。它帮助区分 GPU 翻译体系与系统 IOMMU，但不是 UTCL1/UTCL2 RTL 规格。
- **适用版本与阅读：** Linux v6.12 AMDGPU；已读 `DOC: GPUVM` 全段及 `amdgpu_vm_set_pasid`，其余实现未系统研究。注释内 VMID 数量和页表级数不得推广为所有 AMD 芯片参数。
- **用途与未知：** UTCL1/UTCL2 第一轮地址空间、权限与请求身份；HUBS aperture 边界。目标 UTCL2 的 PTW 位置、缓存组织、接口字段仍待查。

### VM2

- **原名与链接：** Linux `drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c`，[v6.12 固定 tag](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c)，blob `a0cc8e218ca1ea2c10349e48205d82f3ef490b06`。
- **主要内容：** 通过 MMHUB client ID、aperture/上下文配置、TLB/cache 初始化、失效请求和保护故障状态暴露公开软件可见的功能。代码按 IP 版本选择 client 表，且注明 MMHUB 2.1.x 无 ATCL2，说明 hub 的翻译组成必须按代际核对。
- **适用版本与阅读：** Linux v6.12 中此文件所列 MMHUB 2.0.x/2.1.x，不能反推所有 hub。已读 client ID 表、`get_invalidate_req`、`print_l2_protection_fault_status`、`setup_vm_pt_regs`、`init_gart_aperture_regs`、`init_system_aperture_regs`、`init_tlb_regs`、`init_cache_regs`、`setup_vmid_config`、`program_invalidation`、`set_fault_enable_default`、clock-gating/light-sleep 相关段。
- **用途与未知：** UTCL1/UTCL2 的权限与失效研究入口，HUBS 的集成边界与错误归因。寄存器名称不证明内部队列、PTW 物理归属或 heavy/light 的事务排空语义；不提供 CH 定义。

### VM3

- **原名与链接：** Linux `drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`，[v6.12 固定 tag](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c)，blob `7a45f3fdc73410c8a3c2ef84a6d759dc82a3e13c`。
- **主要内容：** 展示 GPU TLB 失效的软件发起、按 VMID/PASID 与 hub 选择、请求/ACK 等待，以及特定配置下与门控相关的 semaphore 处理。可据此研究失效的发起方、目标与完成接口，不能从软件等待推出所有业务事务的硬件完成点。
- **适用版本与阅读：** Linux v6.12，此源文件管理的 GMC v9 相关配置；已读 `gmc_v9_0_flush_gpu_tlb`、`gmc_v9_0_flush_gpu_tlb_pasid`、`gmc_v9_0_emit_flush_gpu_tlb`，并浏览附近 VMID/PASID 和 Vega10 PTE/PDE 注释。未读取完整 IP 规格。
- **用途与未知：** UTCL1 第三轮、UTCL2 第四轮、HUBS 第四轮的接口对齐。FLUSH_TYPE 的协议含义、在途旧回填、light/heavy/NACK 规则仍需适用芯片原始协议证据。

### VM4

- **原名与链接：** Linux `drivers/iommu/amd/iommu.c`，[v6.12 固定 tag](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c)，blob `8364cd6fa47d016311c7d79ed218adfea90fcbb6`。
- **主要内容：** AMD IOMMU 驱动分别构造 IOMMU 页翻译缓存和设备 IOTLB 的失效命令，并在启用 ATS 的设备上安排设备侧失效；完成等待路径用于保证相关失效命令完成。它明确系统侧多参与者边界，不能替代 GPUVM 或 UTCL2 的硬件协议。
- **适用版本与阅读：** Linux v6.12 AMD IOMMU；已读 `build_inv_iommu_pages`、`build_inv_iotlb_pages`、`device_flush_iotlb`、`__domain_flush_pages`、`amd_iommu_domain_flush_pages` 的常规路径、`iommu_completion_wait`、`domain_flush_complete`。未系统研究整个驱动或 PPR 状态机。
- **用途与未知：** UTCL2 第五轮区分 GPUVM、IOMMU 和 ATC/设备 IOTLB；是否适用于目标系统需先核对。AMD 48882 IOMMU 规范检索到了入口，但本次打开原 PDF/API 失败，不能记为已读；ATS 协议的 NACK、排空与续跑细节待原始规范。

### VM5

- **原名与链接：** Rachata Ausavarungnirun et al., *MASK: Redesigning the GPU Memory Hierarchy to Support Multi-Application Concurrency*, ASPLOS 2018，[作者提供的 PDF](https://rausavar.github.io/pubs/mask-asplos18.pdf)，[DOI](https://doi.org/10.1145/3173162.3173169)。
- **主要内容：** 以研究模型比较 GPU TLB/页表缓存路径，讨论翻译等待与共享资源干扰，并提出跨翻译和数据层次的优化。适合作为建立问题和比较设计的资料，不能当成 AMD 已实现的结构。
- **适用版本与阅读：** 2018 原论文，实验模型基于 NVIDIA Maxwell/GPGPU-Sim/Mosaic；已读第 3 节和 Fig.2、第 4.1 节及第 4 节部分干扰分析、第 5.1 节、第 5.3 节开头、第 6 节方法开头。其余优化细节和实验未完整评审。
- **用途与未知：** UTCL1 miss/等待、UTCL2 translation cache 与 walk cache 的区分及共享干扰、EA 条件性的翻译/业务竞争问题。其条目数、算法、页表级数、保守排空做法和性能数值都不转为目标参数；目标预取机制无直接证据。

### VM6

- **原名与链接：** AMD *Graphics Core Efficiency Arbiter (GCEA)*，[ROCm Compute Profiler 3.7.0，docs-7.14.0](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gcea.html)。
- **主要内容：** 从性能观察角度描述 GL2 下游 GCEA 阶段，组织 DRAM 读写、SARB 和返回接口指标，提供忙、停顿、饥饿和请求/返回量等分析入口。页面分组用于性能解释，不证明 GCEA 的 RTL 层级或仲裁算法。
- **适用版本与阅读：** 正文注明 RDNA3.5/gfx115x；已读 GCEA 说明、DRAM read interface、DRAM write interface、System arbiter、Return interface、Memory chart。
- **用途与未知：** EA 的输入/下发/返回闭环、反压与性能诊断；与 P3 共用 GL2/GCEA 分界。目标 EA 是否同一实例、客户端、队列、QoS、算法及一致性职责均待查。

## DF、SWITCH 与命令支路：本次规划来源

### FAB1

- 原名：[AMD CDNA 3 Architecture white paper](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf)。2026-09-24 官网取得的 28 页版本，含 MI325X；不能标成未经核对的原始 2023 版本。
- 简介：解释 XCD/IOD 的功能分工、L2 与内存侧 Infinity Cache、片内与跨封装互联，以及 MI300A/MI300X 的不同内存与连接组织。用于把 DF 研究置于真实 AMD 产品结构中，明确缓存一致性职责与输运职责不能仅靠名称合并。
- 适用性：公开 CDNA 3 产品参考，不能证明 shaobo/anshi 的 CS、CAKE 或 SWITCH RTL 归属；也不能据此声称 AMD D2D 采用 UCIe。
- 实际阅读：Introduction、Chiplet Architecture Repartitioning；打印页 9–14 “Memory”及 Fig.6–8；打印页 15–18 “Communication and Scaling”及 Fig.9–10 的抽取文字。没有把正文外的图形细节当作已目视核验。
- 用途：DF 第 1、3、4 轮；SWITCH 目标协议/层级边界。与其他模块引用同一白皮书时合并主条目。

### FAB2

- 原名：[Linux v6.12 — drivers/gpu/drm/amd/amdgpu/df_v3_6.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c)；Git blob `483a441b46aa1051f78820296095b0a1368b2bc2`。
- 简介：驱动侧展示 DF 地址 hash/通道配置查询、间接配置访问、时钟门控及 perfmon 的读写组织。可据此提出地址映射和观测点问题，但寄存器访问序列不是在线 DF 事务实现。
- 适用性：固定 Linux tag；代码有 Arcturus/Aldebaran 条件分支，不自动适用于全部 AMD GPU。
- 实际阅读：`df_v3_6_query_hashes`、`df_v3_6_get_fb_channel_number`、`df_v3_6_get_hbm_channel_number`、`df_v3_6_get_fica/set_fica`、`df_v3_6_perfmon_rreg/wreg`；计数器配置/读取的函数入口已核对，未逐项核验目标性能事件编码。
- 用途：DF 地址归属、配置边界与性能观测规划。

### FAB3

- 原名：[Linux v6.12 — drivers/ras/amd/atl/core.c](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c)；Git blob `4197e10993acaaa0a5097c7f21796ccde418020c`。
- 简介：AMD Address Translation Library 将 RAS 报告相关的 normalized address 转为 system address，调用节点/映射选择、反交织/hash 与 base/hole 处理。它提醒 DF 地址归属变换和 MMU 的虚实地址翻译是不同研究层次。
- 适用性：该版本针对可匹配的 AMD Zen/SMCA 系统；不能拿软件反解函数的调用次序画成 GPU 硬件流水级。
- 实际阅读：完整 `core.c`，重点 `norm_to_sys_addr`、`get_base_addr`、`add_base_and_hole`、`late_hole_remove`、`addr_over_limit` 和初始化适用条件；被调用的其他源文件尚未逐一展开。
- 用途：DF 第 2 轮地址空间边界及目标资料核对。

### FAB4

- 原名：[Linux v6.12 — include/linux/dma-fence.h](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h)；Git blob `e06bad467f55ef1befdad569f0a8a37875def383`。
- 简介：软件 fence 通过 context/seqno 表达同一执行上下文中的同步对象，区分未完成、成功完成和带错误终结。用于为 CF 的“谁看到什么完成”提问，避免把所有完成信号等同成功。
- 适用性：Linux 软件同步机制参考；不是 CF 协议，不证明 EOC、cancel 与 fence 对应。
- 实际阅读：`struct dma_fence` 字段说明、`dma_fence_ops` 的 signaling 注释、`dma_fence_is_later`、`dma_fence_get_status_locked`、`dma_fence_set_error`；未核验具体 GPU fence 发出/中断链路。
- 用途：CF 第 3 轮软件可见终结与错误传播的边界。

## 内存控制、PHY 与 HBM：本次规划来源

### MEM1

- 原名与入口：[AMD AXI High Bandwidth Memory Controller LogiCORE IP Product Guide (PG276)](https://docs.amd.com/r/en-US/pg276-axi-hbm)，v1.0，页面发布日期 2025-12-17。
- 简介：说明 AMD FPGA HBM IP 的用户端口、地址映射、重排与内存命令、刷新和数据保护，以及 PHY-only 与时钟接口。它提供可具体研究的控制器实例；GPU UMC 的协议、队列深度、实例数和功能支持不得由此推定。
- 实际阅读：相关章节已读——[HBM Topology](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Topology)、[HBM Address Map and Protocol Considerations](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Address-Map-and-Protocol-Considerations)、[HBM Reordering Options](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Reordering-Options)、[Reorder, Refresh, and Power Savings Options Tab](https://docs.amd.com/r/en-US/pg276-axi-hbm/Reorder-Refresh-and-Power-Savings-Options-Tab)、[Data Path Error Protection](https://docs.amd.com/r/en-US/pg276-axi-hbm/Data-Path-Error-Protection)、[Clocking](https://docs.amd.com/r/en-US/pg276-axi-hbm/Clocking)、[PHY Only Mode](https://docs.amd.com/r/en-US/pg276-axi-hbm/PHY-Only-Mode)。正文阅读，不声明全书和所有图中波形已核验。
- 用途与限制：UMC 的事务到命令路径、PHY 边界、HBM2 拓扑与共享资源。Topology 段落存在 Gb/GB/Mb/MB 混写，容量须交叉核对 Address Map 表与具体料号，不直接复制。PHY-only 称接口为 DFI，未在已读部分明确版本，需与 MEM4 的标准覆盖范围核对。

### MEM2

- 原名与链接：[Ramulator 2.0: A Modern, Modular, and Extensible DRAM Simulator](https://arxiv.org/html/2308.11030v2)，Luo 等，arXiv:2308.11030v2，2023-11-29。
- 简介：通过地址映射、控制器、调度器、刷新管理器和独立 DRAM 行为模型划分可替换组件，解释请求如何转为受状态与时序限制的命令。适合检查研究骨架是否遗漏维护请求及完成反馈。
- 实际阅读：第 II-A、II-A1、II-B 节及文字中的 Fig.1–2、Listing 1–3 说明已读；本次未运行模拟器、未读取其源码，也未核验论文性能数据。
- 用途与限制：UMC 逻辑拆分与 HBM 命令约束表达；是研究模拟器架构，不是 AMD RTL。若后续需要实验，另选固定 tag/commit、校验目标内存模型并更新本条，不直接引用移动分支的结果。

### MEM3

- 原名与链接：[AMDGPU RAS Support — Linux Kernel 6.12 documentation](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html)。
- 简介：说明 AMDGPU 按 IP 暴露 RAS 能力、错误计数、注入和 VRAM 坏页管理的驱动接口。它帮助区分硬件检测、驱动恢复与系统页隔离，不能反推 UMC ECC 编码电路。
- 实际阅读：RAS debugfs/sysfs Control and Error Injection、Error Count、EEPROM、VRAM Bad Pages、Reboot Behavior 各节已读；未执行注入、复位或系统操作。
- 用途：UMC RAS 第 4 轮的观测与恢复闭环；与 MG5 的特定 UMC 版本源码交叉引用，支持情况以 ASIC 为准。

### MEM4

- 原名与链接：[DDR PHY Interface (DFI) Group — About DFI / DFI News](https://ddr-phy.org/)。
- 简介：标准组织说明 DFI 定义 MC-PHY 的信号、时序和功能，且不限定系统侧或存储器侧接口。2018 年 5.0 公告介绍 PHY-independent training；2026 年 6.0 公告声明首次正式支持 HBM，说明检索 DFI 时必须区分版本和厂商扩展。
- 实际阅读：About DFI、2018-05-02 DFI 5.0 公告及 2026-05-26 DFI 6.0 公告全文已读；**DFI 5.x/6.0 规范全文未获取、未读**。
- 用途与限制：PHY 接口责任、训练所有权、规范版本核对。AMD 参与 DFI 不证明目标 GPU UMC 使用某版本；MEM1 的 DFI 命名须结合对应产品接口手册确认。

### MEM5

- 原名与链接：[Zynq 7000 SoC and 7 Series Devices Memory Interface Solutions User Guide (UG586)](https://docs.amd.com/r/en-US/ug586_7Series_MIS)，v4.2，2024-11-13。
- 简介：所读 LPDDR2 PHY 章节展示慢速控制域到 I/O 的 FIFO、字节组时钟、相位调整及采样路径；初始化章节说明训练完成后才允许控制器进入正常访问。用于建立“数据路径与校准共同组成 PHY”的具体认识。
- 实际阅读：[Overall PHY Architecture](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Overall-PHY-Architecture)、[Memory Initialization and Calibration Sequence](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Memory-Initialization-and-Calibration-Sequence) 正文已读；本次直链解析落到 **LPDDR2** 章节，不将其标为 DDR3/HBM 训练细节。各 calibration 子步骤全文未逐项阅读。
- 用途与限制：PHY 功能骨架、初始化门控、时钟域和读写采样研究。PHASER/FPGA 原语及具体训练序列只属于该参考，不复制成 AMD GPU HBM PHY 实现。

### MEM6

- 原名与链接：[PCI Express PHY LogiCORE IP Product Guide (PG239)](https://docs.amd.com/r/en-US/pg239-pcie-phy/Product-Specification)，v1.0，2024-12-18。
- 简介：所读部分说明该 FPGA PCIe PHY 使用 GTY/GTH 收发器，并给出速率变化及 TX/RX 均衡的控制交互。可用于追问 MAC/LTSSM 与 PHY 谁发起、谁执行、谁报告完成。
- 实际阅读：Product Specification 与 [Equalization Sequences](https://docs.amd.com/r/en-US/pg239-pcie-phy/Equalization-Sequences) 的 Preset Apply、RX Adapt、TX Adapt 正文已读；图中完整波形与其余接口表尚未逐项核验。
- 用途与限制：PHY 的 PCIe 分支；不是 AMD GPU PCIe PHY 的实例级证明，也不能推广到所有 PCIe 代际。

### MEM7

- 原名与链接：[Versal Adaptive SoC GTY and GTYP Transceivers Architecture Manual (AM002)](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR)，rev.1.3，2023-10-26。
- 简介：RX CDR 解释接收采样相位如何跟踪串行数据；RX Equalizer 解释接收均衡针对信道损耗和码间干扰的作用。适合把电气信道、均衡、采样和数字接收路径连起来理解。
- 实际阅读：[RX CDR](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR)、[RX Equalizer (DFE and LPM)](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-Equalizer-DFE-and-LPM) 正文已读；没有晶体管级、电路仿真或完整手册阅读。
- 用途与限制：相应串行 PHY 的采样和均衡基础；不对宽并行 HBM 接口强套 CDR/DFE，不将 GTY 当成目标 GPU 实现。

### MEM8

- 原名与链接：[UCIe Consortium — Introduction to UCIe Webinar: Q&A Recap](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap)，UCIe 1.0 语境。
- 简介：Physical Questions 说明 mainband、sideband、逻辑与物理 lane 映射及封装约束；Miscellaneous 提醒链路延迟目标不等于端到端事务延迟。用于形成 D2D PHY 与适配器责任边界的问题。
- 实际阅读：Physical Questions 与 Miscellaneous 中 latency、clock receiver、repair 问答已读；未凭此声明 UCIe 规范全文阅读或合规。
- 用途与限制：PHY 的 D2D 比较支路。UCIe 是行业参考，不能将 AMD Infinity Fabric、CAKE 或本项目 SWITCH 直接命名为 UCIe。

### MEM9

- 原名与链接：[Micron HBM3E](https://www.micron.com/products/memory/hbm/hbm3e)，动态官方产品页，查询 2026-09-24。
- 简介：FAQ 给出 Micron HBM3E 的 stack 容量、接口总宽度及 channel/pseudo-channel 组织，可用于检查 HBM2 参考参数是否被误用到后续代际。产品性能比较为厂商口径，不作为目标芯片或应用实测结果。
- 实际阅读：Frequently asked questions 的组织、容量、带宽及 HBM2/HBM3E 差异条目已读；页面所链 Product Brief 请求被拒绝，**未获取完整数据手册或其时序/命令表**。
- 用途：HBM 代际选择、容量/带宽口径及具体料号数据手册待查入口。

### MEM10

- 原名与链接：[Samsung HBM3](https://semiconductor.samsung.com/dram/hbm/hbm3/)，动态官方产品页，查询 2026-09-24。
- 简介：产品页展示 HBM3 堆叠与 ODECC 的产品级信息，并明确更详细规格需索取数据手册。用于提示器件内部纠错与控制器端 ECC 不能混为一个保护域，不据营销描述确定纠错码字或完整故障覆盖。
- 实际阅读：Stack the chips in your favor、Level up to high reliability、数据手册可索取说明已读；**数据手册正文未取得**。
- 用途：HBM RAS 研究问题及来源边界；具体位数、保护范围和错误上报协议均留待器件手册核验。

### MEM11

- 原名与入口：[JEDEC JESD238 — High Bandwidth Memory (HBM3)](https://www.jedec.org/standards-documents/docs/jesd238)。
- 状态：规范候选待查；本次官方页面访问失败，**未读标准全文，不填写未经核验的章节号或参数**。
- 用途：目标采用 HBM3 时，后续本地 Codex 从合法可用版本核验器件组织、命令、时序、初始化、刷新与 RAS。若目标为 HBM2/2E，改选相应 JESD235 修订版及具体料号；不以厂商概述代替规范。

## PCIe、NBIF 与 HDP：本次规划来源

### IO1

- 名称与入口：[AMD UltraScale+ Devices Integrated Block for PCI Express Product Guide，PG213 v1.3](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation)。在线页面版本 v1.3，读取日期 2026-09-24；页面是持续更新入口，后续应按目标控制器版本复核。
- 内容简介：已读 Completer Request Interface Operation、[Completer Memory Read Operation](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Memory-Read-Operation)、[Completer Memory Write Operation](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Memory-Write-Operation)、[Selective Flow Control for Non-Posted Requests](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Selective-Flow-Control-for-Non-Posted-Requests)、[Maintaining Transaction Order](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Maintaining-Transaction-Order) 正文。分别说明请求描述符与数据、读返回拆分、写字节使能、NP 请求的局部信用控制，以及发送流水中的顺序约束。
- 研究用途：PCIe 接收/发送与内部事务适配、posted/non-posted/completion、反压和保序；提供可工作的公开端点接口例子。
- 阅读状态与限制：上述正文相关部分已读，Tag Management 页面未成功取得正文，留待下一轮；图示信号逐拍时序未核验。这里的 AXI4-Stream、CQ/CC/RQ/RC 和具体信用数是该 FPGA IP 的实现接口，不是 PCI-SIG 全规范，也不能套成目标 AMD GPU 的端口名或容量。

### IO2

- 名称与链接：[Linux 6.12 — Bus-Independent Device Accesses](https://docs.kernel.org/6.12/driver-api/device-io.html)。
- 内容简介：描述 MMIO accessors、`ioremap`/`ioremap_wc` 的访问性质，以及 posted write 可能尚未到设备的语义；说明需要时通过合适的读操作约束 posted write 完成。CPU 侧顺序、总线写入到达和设备内部操作完成应分别分析。
- 阅读状态：相关章节已读，定位 Accessing the device、Differences between I/O access functions、Device memory mapping modes；非相关架构和 API 列表未逐项研读。
- 研究用途：PCIe BAR/MMIO 与普通内存访问区别，NBIF doorbell 前的发布次序，HDP flush 与 MMIO readback 的边界；通用 Linux 语义，不决定目标芯片缓存一致性实现。

### IO3

- 名称与链接：[Linux 6.12 — Dynamic DMA mapping Guide](https://docs.kernel.org/6.12/core-api/dma-api-howto.html)。
- 内容简介：开篇区分 CPU 虚拟、CPU 物理和设备 bus/DMA 地址，并用 host bridge 与 IOMMU 解释它们为何不能一概相等；`dma_map_single` 得到设备可用 DMA 地址。用于把 CPU 访问设备 BAR 与设备主动访问主存分成两条路径。
- 阅读状态：CPU and DMA addresses 相关正文及图的文本说明已读，后续 DMA ownership/sync API 全部细节未研究。
- 研究用途：PCIe requester/completer 角色、NBIF 地址窗口与系统 IOMMU 边界；ATS/PASID/PRI 仍需专门规范和目标支持证据，本条不能证明这些能力存在。

### IO4

- 名称与链接：[PCI-SIG — PCI Express Base Specification Revision 5.0, Version 1.0](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0)。
- 内容简介：官方登记页说明 Base Specification 的范围及 2019-05-28 发布信息；可作为取得合法规范全文的入口。
- 阅读状态：只读登记页，**规范正文未取得、未阅读，候选资料**。后续通过已有合法访问渠道获取目标版本，再定位 Transaction Layer、Data Link Layer、Configuration、Error Handling；当前不编造章节号，不以登记页支持协议细节。
- 研究用途：PCIe 后续规范核验；选 5.0 作为传统 non-FLIT 研究候选不表示本项目目标端口已确认为 Gen5，也不将 PG213 当作替代规范。

### IO5

- 名称与链接：[Linux v6.12 — nbio_v7_4.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c)；配套 [amdgpu_nbio.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_nbio.h)。
- 内容简介：公开 NBIO 驱动包含 doorbell aperture/range、framebuffer 访问使能、HDP flush remap/REQ/DONE、IH 控制、NBIF RAS 事件和 ASPM 等配置入口。文件中同时出现 NBIO 软件归档和 NBIF 硬件寄存器/中断标识，证明需要联合检索，不能据此证明二者在所有芯片中完全等价。
- 阅读状态：相关函数已读：`nbio_v7_4_mc_access_enable`、`sdma_doorbell_range`、`enable_doorbell_aperture`、`ih_control`、`remap_hdp_registers`、`get_hdp_flush_req_offset`/`get_hdp_flush_done_offset`、`set_reg_remap`、`program_aspm`、`handle_ras_controller_intr_no_bifring`，以及 header 的 `amdgpu_nbio_funcs`。保留各函数完整的 `nbio_v7_4_` 前缀检索。
- 研究用途：NBIF 研究候选功能与公开软件证据；HDP 控制关系；不能还原内部完整数据路径、队列规模、NBIF 父级或 shaobo/anshi 实例。`v7_4` 文件仍含多个 IP/产品分支，应逐分支引用。

### IO6

- 名称与链接：[Linux v6.12 — hdp_v4_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c)。
- 内容简介：HDP 驱动分别实现 flush 与 read-cache invalidate、non-surface base 初始化、时钟/内存低功耗和 RAS 计数。invalidate 对指定 4.4.x 版本直接返回，说明仅凭函数名不能假设所有 HDP 代际具有同一种缓存维护操作。
- 阅读状态：相关函数已读：`hdp_v4_0_flush_hdp`、`invalidate_hdp`、`init_registers`、`query_ras_error_count`、`reset_ras_error_count`、`update_clock_gating`。`init_registers` 的 VF 跳过分支和 HDP 4.2.1 的 `HDP_MMHUB_CNTL` 设置均已见；它们是软件配置事实，不能确定目标 HDP/MMHUB 的完整拓扑。
- 研究用途：HDP 维护状态、主机 aperture 地址基础、代际差异和错误恢复研究；驱动调用发出与硬件处理完成需另查协议，不自行解释为已排空全部 GPU 缓存。

### IO7

- 名称与链接：[AMD BKDG for Family 15h Models 60h–6Fh，50742 Rev 3.05，2016-05-21](https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/50742_15h_Models_60h-6Fh_BKDG.pdf)。
- 内容简介：第 2.14.2.2 节 Host Data Path Guidelines 将 HDP 与 host 对 framebuffer 的地址转换联系起来，并给出该旧 APU 的窗口配置语境。用于确认 AMD 公开历史名称和 aperture 研究入口。
- 阅读状态：已读第 2.14.1–2.14.2.2 节相关段落，纸面第 169–170 页（PDF 索引 168–169），未研究完整手册或寄存器表。
- 研究用途与限制：HDP 全称和历史职能的原厂证据；旧 UMA APU 的容量上限、GMC 组织和访问路径不适用于未确认的目标 GPU，不能与新 NBIO/HDP 文件拼成一个真实芯片。

### IO8

- 名称与链接：[Linux 6.12 — The MSI Driver Guide HOWTO](https://docs.kernel.org/6.12/PCI/msi-howto.html)。
- 内容简介：MSI 是设备向特殊地址写入以触发主机中断，文档比较传统引脚中断与 MSI 的数据写入顺序，并说明 MSI/MSI-X 的配置和向量管理。
- 阅读状态：第 4.2、4.3、4.4.2 节相关部分已读；未以此核验目标芯片 MSI-X 表位置或能力。
- 研究用途：PCIe 请求闭环中的通知阶段，与 IH 事件汇聚和 ring 消费区分；中断顺序结论仅在文档讨论的 PCI ordering 前提下使用，不能替代任意缓存域的维护。

### IO9

- 名称与链接：[Linux 6.12 — PCI Error Recovery](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html)。
- 内容简介：给出平台与设备驱动在错误通知、停止新 I/O、恢复 MMIO、link/slot reset 和 resume 之间的协作。恢复过程具有平台差异，驱动恢复回调不是 PCIe 链路重放协议。
- 阅读状态：第 7.1 节及 STEP 0–4 相关正文已读；具体平台实现未研究。
- 研究用途：PCIe/NBIF 异常闭环，区分链路可纠错重放、事务失败和软件恢复，不把 Linux 回调直接画成目标硬件状态机。

### IO10

- 名称与链接：[Linux v6.12 — gfx_v9_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c)。
- 内容简介：`gfx_v9_0_ring_emit_hdp_flush` 按引擎选择 mask，使用 NBIO 提供的 HDP request/done 寄存器构造等待；它给出 HDP 维护命令从请求到等待完成的公开调用例子。
- 阅读状态：只读该函数及相关 ring funcs 中的 `emit_hdp_flush` 绑定，未研究该大文件的其他执行单元和命令处理器；相关的 `gfx_v9_0_wait_reg_mem` 具体包字段留待后续。
- 研究用途：NBIF/HDP 控制闭环及完成条件的来源追踪。这里只借调用点研究接口，不扩展本项目 GC 的既定模块范围，不认为所有 flush 路径都会使用相同等待机制。

## 管理与事件支路：本次规划来源

### MG1

**Linux v6.12 — AMDGPU SMU common interfaces / smu_cmn.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c)。

简介：实现软件到 SMU 的消息映射、参数提交、状态轮询和错误返回，也实现共享内存表格传输。消息互斥与固件状态检查可用于解释请求接口，表格传输前后的 HDP 操作提供 CPU/GPU 可见性的具体入口，不能据此推导固件内部调度。

版本/适用：Linux v6.12，AMDGPU swsmu common 层，实际路径受 ASIC/能力配置约束。  
阅读状态：相关函数已读；定位 `__smu_cmn_send_msg`、`__smu_cmn_reg2errno`、`__smu_cmn_ras_filter_msg`、`smu_cmn_send_smc_msg_with_param`、`smu_cmn_wait_for_response`、`smu_cmn_update_table`。未逐一研究所有芯片的消息映射。  
研究用途：SMU 第 1–2 轮 mailbox、共享状态、超时/拒绝以及表格传输；HDP 接口可以复用此条。

### MG2

**Linux v6.12 — AMDGPU SMU 13.0 / smu_v13_0.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c)。

简介：提供 SMU 13.0 系列的固件接口版本检查、频率范围与功率约束调用，以及 thermal、AC/DC 和 SMU-to-host 事件处理。源码可区分软件请求、固件接口与源端 ACK/re-enable；它没有公开完整 DVFS 控制算法。

版本/适用：Linux v6.12，SMU 13.0 common 实现；产品差异由分支和调用方决定，不能假定同一文件所有功能用于同一 ASIC。  
阅读状态：相关函数已读；定位 `check_fw_version`、`set_power_limit`、`set_soft_freq_limited_range`、`set_hard_freq_limited_range`、`enable_thermal_alert`、`set_irq_state`、`irq_process`、`ack_ac_dc_interrupt`、`register_irq_handler`。初始化/恢复全调用链尚未完整追踪。  
研究用途：SMU 约束—执行—反馈和保护事件；IH 源端处理责任的条件化例子，不据此证明 SMU 13.0 与某个 IH 版本必然同片。

### MG3

**Linux v6.12 — SMU 13.0.0 driver/firmware interface / smu13_driver_if_v13_0_0.h**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h)。

简介：定义该接口版本的功率策略表与遥测结构，包括功率/电流/温度限制、时钟、活动、能量和 throttling 等可见字段。字段与注释有助于辨认控制输入和反馈输出，不能单靠表布局恢复整个控制器的内部算法。

版本/适用：Linux v6.12 携带的 SMU 13.0.0 ABI，头文件标注 `PPTABLE_VERSION 0x2B`，不推广其他 SMU 版本。  
阅读状态：部分章节已读；定位 PPTable_t 的 Feature Control、Infrastructure Limits、Throttler settings，以及 SmuMetrics_t / SmuMetricsExternal_t；其余表格和具体单位转换未全面研究。  
研究用途：SMU 第 2–3 轮共享表、约束与遥测、版本适用性。

### MG4

**Linux v6.12 — AMD northbridge SMN access / arch/x86/kernel/amd_nb.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c)。

简介：通过节点选择和 PCI 配置 index/data 窗口完成 SMN 读写，使用软件互斥保护一组间接访问。代码注释解释 SMN 访问失败检测的边界，包括 PCI error response、读零及写副作用，说明“访问返回”与“端点语义正确”需要分别判断。

版本/适用：Linux v6.12，AMD x86 CPU 平台访问帮助函数；不能直接用来确定目标 GPU 的寄存器地址、SMN 拓扑或硬件并发能力。  
阅读状态：相关函数与注释已读；定位 smn_mutex、`__amd_smn_rw`、`amd_smn_read`、`amd_smn_write` 及函数前的错误/读回注释；未通读其他 northbridge 功能。  
研究用途：SMN 第 1–2 轮入口与状态、返回语义；第 3–4 轮的硬件网络/超时机制仍需目标资料。

### MG5

**Linux v6.12 — RSMU UMC index-mode register definitions and UMC v6.1 callers**  
链接：[rsmu_0_0_2_offset.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h)、[rsmu_0_0_2_sh_mask.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h)、[umc_v6_1.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c)。

简介：两个小型寄存器头与调用代码共同给出 RSMU 命名的 UMC index-mode 接口证据。UMC RAS 路径保存原 mode、必要时关闭它、访问各 UMC/通道后恢复，并有 Arcturus 特定 DF C-state 条件；这些只证明该访问模式与调用关系，不证明 RSMU 全称、完整微架构、SMU 包含关系或 UMC 内存数据经过 RSMU。

版本/适用：Linux v6.12；RSMU 0.0.2 寄存器符号含 NBIF_VG20_GPU，调用者为 UMC v6.1 实现，具体 ASIC 分支分别辨认。  
阅读状态：两个头文件全文已读；umc_v6_1.c 已读 `enable_umc_index_mode`、`disable_umc_index_mode`、`get_umc_index_mode_state`、`clear_error_count`、`query_ras_error_count`、`query_ras_error_address`、`err_cnt_init` 中模式处理及外围调用顺序；未完整研究 ECC 地址解码算法。  
研究用途：RSMU 三轮的身份/接口线索与条件化架构；UMC RAS 管理访问约定；SMN 间接访问状态的对比例子。三个紧密关联的接口文件在本条统一登记，跨模块不另建重复条目。

### MG6

**Linux v6.12 — AMDGPU IH v6.0 / ih_v6_0.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c)。

简介：配置 IH ring、指针写回、doorbell 与主机通知，并提供 overflow 检测、RPTR 恢复及第二 ring 的 self-interrupt 处理。初始化还可见事件 storm/flood 控制和特定 ring 分流，是研究通知节奏与事件存储差别的入口，不提供完整入口 RTL 仲裁结构。

版本/适用：Linux v6.12，IH v6.0 实现；ring/VF/固件加载条件分别核对，不用其参数代表全代际。  
阅读状态：相关函数已读；定位 `enable_ring`、`get_wptr`、`set_rptr`、`irq_rearm`、`self_irq`、`irq_init`、`irq_disable`、`toggle_ring_interrupts` 与 `force_update_wptr_for_self_int`。未系统检查所有 IP revision 和虚拟化组合。  
研究用途：IH 第 2–4 轮 ring、overflow、storm、self interrupt、生命周期。

### MG7

**Linux v6.12 — AMDGPU IH common ring / amdgpu_ih.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c)。

简介：负责 IH ring 内存分配、指针 shadow、软件消费循环和公共 IV 解码。代码显示 DMA coherent 与 GTT 路径的区别，以及读写指针与 ring 数据的顺序要求；公共解码中的身份字段须按实际源及 IP 适用。

版本/适用：Linux v6.12，AMDGPU common 层；decode_iv_helper 注释对应 Vega10 及之后的格式，不能自动套给旧代际。  
阅读状态：相关函数已读；定位 `amdgpu_ih_ring_init`、`amdgpu_ih_process`、`amdgpu_ih_decode_iv_helper`；检查了 checkpoint/write-ring 附近的读取定位，未完整研究这些辅助路径。  
研究用途：IH 第 1–2 轮 IV 信息、DMA/内存归属、WPTR/RPTR 与可见性。

### MG8

**Linux v6.12 — AMDGPU IRQ setup and dispatch / amdgpu_irq.c**  
链接：[原文件](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c)。

简介：设置主机 IRQ、驱动 handler 和后台 work，并将 IV 分发给对应 client/source 回调或相关处理者。它有助于区分中断记录、主机 IRQ 资源以及源端业务处理，回调被调用不等于业务事件必已消除。

版本/适用：Linux v6.12，AMDGPU 通用分发；MSI/MSI-X/INTx、legacy client、VF 等路径按条件解释。  
阅读状态：相关部分已读；定位 `amdgpu_irq_init`、`amdgpu_irq_handler`、`amdgpu_irq_dispatch`、ih1/ih2/soft work handlers；未逐一研究所有源模块回调。  
研究用途：IH 第 1、3–4 轮主机通知、分发、后台处理与异常边界；SMU 源端回调复用 MG2。

## 新资料登记方式

新增资料沿用来源编号和链接，并根据实际阅读补充 1–3 句主要内容简介、关联模块/研究问题及阅读状态；产品/代际、版本/日期、章节或代码定位和重要限制按需记录。相同资料更新原条目，不重复登记；不同版本保留影响研究的差异。尚未收到或未读的资料标为待查，不登记为已读来源。

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
