# UTCL1 资料索引与逐篇技术笔记

更新日期：2026-09-25。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 20 个可复用来源，主笔记归档 2 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 客户端身份、命中与 miss | [VM1](../../UTCL2/sources/VM1-gpuvm-address-spaces.md) → [C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md) → [C03](../../UTCL2/sources/C03-utcl2-topology.md) → [VM7](VM7-gem5-vega-tlb.md) | 第 1–2 轮：用本地页图与 gem5 功能模型对照；模型中 ASID/失效简化不能当成目标能力。 |
| 合并、等待与资源释放 | [VM9](VM9-gem5-coalescer.md) → [VM5](../../UTCL2/sources/VM5-mask-paper.md) → [C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 第 2–3 轮：区分合并键、上游请求数和下游翻译数；保留客户端返回与 credit 释放。 |
| 失效与地址空间复用 | [VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md) → [VM11](../../UTCL2/sources/VM11-vmid-lifetime.md) → [VM10](../../UTCL2/sources/VM10-iommu-spec.md) → [IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) | 第 3–4 轮：把 VMID 重用、翻译失效、IOMMU/ATC 分支分别解释，不套统一流水。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [P5：MI200 的翻译、EA credit 与在途请求计数](../../GC/sources/P5-mi200-counters.md) | 提供可操作的观测点：UTCL1 translation/permission miss、UTCL2 busy、EA 按 IO/GMI/DRAM 分类的 credit stall，以及在途请求积分。适合做跨模块性能诊断，但不是目标芯片的计数器规格。 | 厂商/项目官方资料。本次成功读取页面，精读 GRBM、CPF/CPC 的翻译相关项、TCP UTCL1、TCC/EA 及 derived metrics 对应条目和缩写；未逐一研究全部指令/纹理计数，未采样验证。 | [原文](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html) |
| [VM1：GPUVM 的地址空间、VMID、PASID 与 aperture](../../UTCL2/sources/VM1-gpuvm-address-spaces.md) | 建立 GPUVA、页表、动态 VMID、PASID 与系统地址的基本关系；尤其适合防止把 GPUVM 和系统 IOMMU 合并为一个翻译器。 | 固定版本公开代码。精读开头 `DOC: GPUVM` 与 `amdgpu_vm_set_pasid`；页表 BO 搬迁和全部更新实现未系统研读。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c) |
| [VM2：MMHUB 2.x 的地址范围、翻译缓存与 fault 配置](../../HUBS/sources/VM2-mmhub-v2.md) | 按初始化顺序整理 MMHUB 软件可见的服务结构：页表根、aperture、TLB/cache、VM context、失效引擎和 fault。适合构建 hub 控制面；不证明完整内部数据网络。 | 固定版本公开代码。精读 page-table/aperture、TLB/cache、VMID config、invalidation、gart enable/disable 与 fault decode；时钟门控的全部分支未逐项展开。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c) |
| [VM3：GMC v9 的 GPUVM 失效：请求、ACK、hub 与电源状态](../../UTCL2/sources/VM3-gpuvm-invalidation.md) | 详细追踪 GPUVM invalidate 的软件发起与完成观察，包含 VMID/PASID 转换、不同 hub、KIQ 与直接寄存器路径及旧 ACK 风险。适合建立维护事务闭环。 | 固定版本公开代码。精读 `get_invalidate_req`、`use_invalidate_semaphore`、`flush_gpu_tlb`、`flush_gpu_tlb_pasid`、`emit_flush_gpu_tlb`，以及 fault 状态输出定位；其他 GMC 功能未全文研究。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c) |
| [VM5：MASK：把地址翻译需求传递到共享缓存和 DRAM 调度](../../UTCL2/sources/VM5-mask-paper.md) | 解释 token/fill 与两种 cache 旁路、DRAM 三队列预算；保存公式、容量、工作负载筛选、基线与吞吐/公平性结果，适合 UTCL2–EA–UMC 的翻译干扰研究。 | 原始论文。补核 §5–7 的机制、预算式、Table 1 原图和主结果，记录 warp 配置疑点；未复现模拟器或重算全部实验。 | [原文](https://rausavar.github.io/pubs/mask-asplos18.pdf) |
| [VM7：gem5 Vega TLB：查找、回填、属性与模型简化](VM7-gem5-vega-tlb.md) | 提供一套可以沿函数追踪的 TLB 模型，解释命中、miss、回填和返回。尤其记录其 ASID、fault 与失效处理的简化，避免后续 Codex 把模拟器当成完整硬件规格。 | 固定版本公开代码。精读构造、lookup/insert、invalidate/demap、issue/translationReturn、protectionChecks、walkerResponse、cleanup；未运行模型。 | [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/tlb.cc) |
| [VM8：gem5 Vega 页表遍历器的依赖状态与端口重试](../../UTCL2/sources/VM8-gem5-page-walker.md) | 具体解释一个 page walk 如何保存上下文、逐级读 PDE/PTE、等待内存、遇到背压重试并回填。适合建立 walker 与缓存/内存服务之间的接口。 | 固定版本公开代码。精读 startTiming/initState、startWalk/stepWalk、walkStateMachine、sendPackets、recvTimingResp/retry、pageFault；未执行模拟。 | [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/pagetable_walker.cc) |
| [VM9：翻译请求合并：时间窗、在途表与响应展开](VM9-gem5-coalescer.md) | 解释多个同页请求如何共用一次下游翻译，以及如何保留每个请求的 offset、返回端口和统计数量。适合研究 miss 合并与有限资源；明确模型的多地址空间限制。 | 固定版本公开代码。精读 canCoalesce、recvTimingReq、processProbeTLBEvent、updatePhysAddresses、retry、cleanup、stall/unstall；未仿真。 | [原文](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/tlb_coalescer.cc) |
| [VM11：动态 VMID 的租用、复用与页表更新依赖](../../UTCL2/sources/VM11-vmid-lifetime.md) | 解释为什么 VMID 不能当作永久进程编号，以及驱动如何用 active fence、页表根和 flush 进度防止过早复用。适合连接提交队列、翻译上下文与完成事件。 | 固定版本公开代码。精读 VMID idle/used/reserved/grab、compatible、flush 进度与 active fence 处理；PASID allocator 的全部路径未展开。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c) |
| [VM10：AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约](../../UTCL2/sources/VM10-iommu-spec.md) | 用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。 | 规范选读。已取得完整 303 页 PDF；重点核读 §1.3、§2.1–2.2、§2.4.1–2.4.4、§2.4.11、§2.5；本次补核 §2.2.6–2.2.7.1、§2.4.7、§2.6 的 guest/nested 与 PRI/PPR 主线；本笔记不是整本规范的逐字段替代品。 | [原文](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf) |
| [C01：MM_UTCL2 图示与验证环境：从翻译事务到可观测检查点](../../UTCL2/sources/C01-mm-utcl2-testbench.md) | 覆盖 MM_UTCL2 的 APT1/2/3、VML2/ATCL2、fault/retry、两类失效以及验证环境，适合建立请求生命周期和验证检查点；所有容量与字段均须保留该资料版本范围。 | 用户页图·参考设计。49 页的已提交页图均已取得文字阅读或图像核看记录；2026-09-25 补回并直接核看了此前未读取的第 1、4 页。主要技术范围为第 3–5、15–31、33–47、49 页；并非对所有 OCR 字符逐字校勘。图示版本与目标芯片对应关系仍需本地确认。 | [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/tb_mm_utcl2) |
| [C02：UTCL2 结构与使用：页表格式、cache 映射和 BigK 性能反例](../../UTCL2/sources/C02-utcl2-cache-organization.md) | 解释 Group/VML2/Walker/ATC 的分工、PTE cache 的 bank/set/way/tag、表布局粒度与映射粒度的区别，并保存 BigK 增大反而禁止填充的具体案例。 | 用户页图·参考设计。读取 38 页文字并核看结构及第 34–35 页关键条件；本笔记保留原资料案例的配置前提，不把建议寄存器值写成可直接应用的优化命令。 | [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin) |
| [C03：UTCL2 总图：GPUVM、ATC 与 walker 的资源边界](../../UTCL2/sources/C03-utcl2-topology.md) | 从一张总图建立请求入口、VML2 bank、walker、ATCL2 与返回网络的关系，适合快速判断一个 feature 应放在哪个子模块；图中的实例数只属于该图配置。 | 用户页图·参考设计。已直接查看整张高分辨率图并核对主要连接；未据此推导图中没有标明的吞吐、端口时序或协议完成保证。 | [原文](https://github.com/niyingsong123/soc_study/blob/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/utcl2_top/page-001.png) |
| [C04：地址翻译与预取：rdif 扩展、资源竞争和已核算勘误](../../UTCL2/sources/C04-translation-prefetch.md) | 把常见翻译预取思想与资料中 shaobo 的 rdif 方案分开，说明 history table、独立预取缓存、需求请求优先和返回分类；同时记录地址例题和阈值描述中的问题。 | 用户页图·参考设计。读取 26 页文字，直接核看第 18、22、23、25 页；完成第 18 页地址索引的独立逐位核算。未取得 RTL、专利公开号或性能原始测量条件。 | [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D) |
| [C05：MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。 | 用户页图·参考设计。读取 41 页可提取文字，直接核看第 7、18、27、32、33、34、40 页关键图表；图中缺乏的 RTL 时序、RAM 端口数和严格完成定义保持未知。 | [原文](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/HUBS/assets/MMHUB_introduction) |
| [R12：Arm 系统架构入门：数据、翻译、中断与低功耗接口的分层](../../SWITCH/sources/R12-arm-system-architecture.md) | 提供 CHI/AXI、SMMU 翻译接口、GIC 与低功耗控制的系统地图，帮助研究 AMD 模块别名和职责边界；它是入门总览，不是 CHI 事务规范。 | Arm 架构概述。已读系统组件和接口章节，重点第 4 章 AMBA 分类、CHI-C2C、DTI/LTI 与 LPI；不把 Arm 组件名视为 AMD 一一等价模块。 | [原文](https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749) |
| [IO11：PCI ATS/PRI/PASID：能力、额度与 PF/VF 共享](../../PCIE/sources/IO11-ats-pri-pasid.md) | 用于区分 ATS 缓存翻译、PRI 请求资源和 PASID 身份能力，重点是配置依赖、PF/VF 共享及队列深度编码；适合 IOMMU 与 PCIe 联读。 | 固定版本公开代码。已读 ATS、PRI、PASID enable/disable/restore、能力和额度处理；未读完整 PCIe 扩展规范或设备内部状态机。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/pci/ats.c) |
| [L1：外部 SDMA 术语表：既有登记与复查入口](../../SDMA/sources/L1-external-glossary-scope.md) | 用于查项目专用 CF/DF、FE/BE/TBE、UTCL1/UTCL2 含义；当前只保存原仓库登记范围，必须在本地可访问外部项目时复查原文。 | 外部入口·未重读。本次无法访问外部项目，未重新读取全文；本笔记仅整理本仓库已有摘要，不是原文详细总结。 | 外部本地路径见笔记 |
| [L2：外部 shaobo 摘要：两条后端路径的待复查接口](../../SDMA/sources/L2-external-shaobo-scope.md) | 原登记涉及 FE 两条后端路径、CF_IF/DF_IF、TBE 内 UTCL1、UTCL2 请求和 MMHUB 写回；适合后续本地核实 SDMA 与 SoC 的连接。 | 外部入口·未重读。本次未取得外部摘要或原始资料全文；仅保留现有来源登记，不补造时序、格式和内部职责。 | 外部本地路径见笔记 |
| [L3：外部 SDMA 待确认问题：保留 anshi TBE 边界](../../SDMA/sources/L3-external-open-questions.md) | 用于接续未决问题，特别是 anshi TBE 的剩余职责；当前没有原文，禁止用公开驱动或 shaobo 架构把未知项自动填满。 | 外部入口·未重读。本次未读取外部文件；仅整理当前仓库已登记的未知项和后续复查方式。 | 外部本地路径见笔记 |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
