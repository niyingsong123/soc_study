# UTCL2 多轮研究与论文方案

依据范本：v1.4；方案版本：v1.1；日期：2026-09-24。**状态：规划完成，六轮详细研究均待执行。** 下一步确认服务边界与地址空间模型。本方案只建立研究基础，公开软件接口与研究模型不代表 shaobo/anshi 实现。

接续：[模块上下文](README.md) → 本页 → [资料集 VM1–VM5](../sources.md#vm1) → 具体原文。每轮维护资料集的阅读范围，在本页记录真实进度，详细内容逐步合入后续创建的本目录 `technical-paper.md`。C01–C04 缺失转换正文不恢复；本次已读现有页图并形成逐篇笔记，未访问本地原件。页图中的参考结构及目标映射仍须分开。

## 逐篇笔记与本方案的研究落点

先查[模块资料索引](sources/README.md)了解每篇讲什么，再读对应详细笔记；笔记内保留原文链接、版本、阅读位置、机制及重要限制。本次仅补资料与修订规划，下面的论文轮次完成状态不变。

| 微架构位置 | 对应轮次 | 可直接复用的技术笔记 | 本次补充的研究重点 |
| --- | --- | --- | --- |
| 整体结构、页表层级与回填 | 第 1–2 轮 | [C03](sources/C03-utcl2-topology.md)、[C02](sources/C02-utcl2-cache-organization.md)、[C01](sources/C01-mm-utcl2-testbench.md)、[VM1](sources/VM1-gpuvm-address-spaces.md)、[VM8](sources/VM8-gem5-page-walker.md) | 区分页图中的 GPUVM/ATC 分路；BigK 回填条件按特定结构理解，不推广成 MMU 定理。 |
| 并发、fault、失效和外部翻译 | 第 3–5 轮 | [VM5](sources/VM5-mask-paper.md)、[VM3](sources/VM3-gpuvm-invalidation.md)、[VM11](sources/VM11-vmid-lifetime.md)、[VM10](sources/VM10-iommu-spec.md)、[IO11](../PCIE/sources/IO11-ats-pri-pasid.md)、[VM2](../HUBS/sources/VM2-mmhub-v2.md) | 分别记录客户端请求、PTW 读、已翻译业务事务；系统失效完成与本地完成分开。 |
| 预取、观测与纠错 | 第 6 轮 | [C04](sources/C04-translation-prefetch.md)、[P5](../GC/sources/P5-mi200-counters.md)、[VM7](../UTCL1/sources/VM7-gem5-vega-tlb.md)、[VM9](../UTCL1/sources/VM9-gem5-coalescer.md) | 围绕预取对象、反馈、配额和失效展开；C04 地址例子有逐位纠错，先读笔记再复用。 |


## 对象、术语与上下游

沿用 AMD Unified Translation Cache – Level 2 [P5]；联合检索 shared TLB、GPU MMU、page-table walker、page-walk cache、GPUVM、ATC、IOMMU、ATS。这里 MMU/GPUVM 是更广的功能体系，PTW 是遍历功能，ATC/IOMMU 属于可能相关的系统翻译路径，均不能直接等同 UTCL2。

上游是需要共享翻译服务的 UTCL1/客户端；shaobo TBE 的 UTCL1 miss 向 UTCL2 请求，是仓库既有摘要支持的部分关系 [L2]。先复用 [UTCL1](../UTCL1/research-plan.md)的请求身份、返回和失效约定，再研究服务端。下游包含“取得页表/其他翻译服务”以及“向客户端返回结果”两类接口；页表遍历单元的位置、访存经过哪个 hub、是否经过 GL2 都待目标证据确认。后续 [HUBS](../HUBS/research-plan.md)接续 hub 集成，不以目录顺序推断包含。

**必须保持两个分离：** GL2 缓存业务数据，UTCL2 研究翻译信息；GPUVM 处理 GPU 地址空间，系统 IOMMU 处理系统侧 I/O 翻译与保护。系统内存访问是否还需 IOMMU、是否启用 ATS/ATC、地址处于 GPUVA/IOVA/系统 PA 的哪一层，应逐场景说明。[VM1 GPUVM 段](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c)与 [VM4 AMD IOMMU 驱动](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c)提供不同软件边界；二者代码名称不构成硬件等价证明。 技术笔记：[VM1](sources/VM1-gpuvm-address-spaces.md)、[VM4](sources/VM4-amd-iommu-commands.md)。

## 整体功能微架构与请求闭环

图为**公开参考支持的研究骨架**，只表示功能依赖。页表服务刻意画在边界之外，后续取得框图才判断是否在 UTCL2 本体；PTE/PDE 保存结构也不预设为若干固定物理 cache。

```mermaid
flowchart TD
    U[UTCL1 与其他客户端] --> A[请求接入与上下文选择]
    A --> T[翻译与中间结果查询]
    T -->|可用结果| R[权限属性与响应]
    T -->|缺少信息| M[未完成请求与服务调度]
    M --> W[页表或外部翻译服务]
    W -->|结果或错误| F[结果关联与回填控制]
    F --> R
    F --> T
    R --> U
    V[失效与上下文管理] -.-> T
    V -.-> M
    V -.-> F
```

主闭环采用一个 GPUVM 翻译 miss：客户端提交地址和身份 → 选择地址空间与上下文 → 查找可用的最终或中间翻译信息 → 缺失部分向页表服务请求 → 关联返回、检查访问权限和页表状态 → 决定回填并返回翻译/错误 → 上游继续或处理失败。遍历产生的读请求另有 outstanding，与客户端原始业务读写分开记录；每一类都需说明等待位置和完成条件。

第二条闭环是页表更新：更新数据可见 → 发起相应失效 → 各参与者处理条目及在途状态 → 完成确认 → 允许依赖新映射的访问。这里的箭头是研究所需的顺序问题，具体屏障、ACK 与排空责任待协议确认；不能把 ACK 自动解释为所有业务写入已到 DRAM。

## 重点与阅读位置

| 架构位置 / 优先级 | 需要回答的问题 | 资料直链与定位 |
| --- | --- | --- |
| 接入与上下文 / 核心 | VMID/PASID/地址空间如何关联？哪些属性参与隔离，哪些只影响目标路由？ | [VM1](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c)，`DOC: GPUVM`；[VM3](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c)，VMID/PASID flush 路径  技术笔记：[VM1](sources/VM1-gpuvm-address-spaces.md)、[VM3](sources/VM3-gpuvm-invalidation.md)。 |
| 查询与遍历服务 / 核心 | final translation、PDE/PTE 缓存、PTW 各解决什么？未命中由谁补齐？ | [VM2](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c)，`init_cache_regs`；[VM5](https://rausavar.github.io/pubs/mask-asplos18.pdf)，第 3 节，比较 TLB 与 walk cache  技术笔记：[VM2](../HUBS/sources/VM2-mmhub-v2.md)、[VM5](sources/VM5-mask-paper.md)。 |
| 共享并发 / 核心 | 客户端公平性、同页合并条件、请求追踪、服务反压和返回拥塞如何影响吞吐？ | [VM5](https://rausavar.github.io/pubs/mask-asplos18.pdf)，第 4 节，研究干扰与阻塞；算法只作对照  技术笔记：[VM5](sources/VM5-mask-paper.md)。 |
| 权限与 fault / 核心 | 无映射、权限失败、遍历读失败、可重试事件如何区分并通知原请求？ | [VM2](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c)，`print_l2_protection_fault_status`、`setup_vmid_config`  技术笔记：[VM2](../HUBS/sources/VM2-mmhub-v2.md)。 |
| 失效 / 核心 | 清哪些层级、如何防旧回填、哪个 outstanding 需等待、谁返回完成？ | [VM2](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c)，`get_invalidate_req`；[VM3](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c)，`flush_gpu_tlb`  技术笔记：[VM2](../HUBS/sources/VM2-mmhub-v2.md)、[VM3](sources/VM3-gpuvm-invalidation.md)。 |
| 系统翻译 / 条件 | IOMMU 缓存失效与设备 ATC 失效有哪些不同参与者？目标场景支持哪条路径？ | [VM4](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c)，`build_inv_iommu_pages`、`device_flush_iotlb`、`domain_flush_complete`  技术笔记：[VM4](sources/VM4-amd-iommu-commands.md)。 |
| 预取与优化 / 条件或扩展 | 预取对象是 PTE/PDE、翻译结果还是数据？跨页权限、fault、资源配额和失效如何约束？ | [VM5](https://rausavar.github.io/pubs/mask-asplos18.pdf)，第 4 节支持干扰分析，**不证明 AMD 预取算法**；已读 C04 参考预取机制，目标对应仍待查  技术笔记：[VM5](sources/VM5-mask-paper.md)。 |

## 六轮研究安排

### 第一轮：整体边界与地址空间

- **前置与范围：** UTCL1 基础接口；选择 GPUVM 的一个本地内存场景、一个系统内存条件分支。先明确谁持有地址、谁解释身份、谁产生数据请求。
- **阅读：** VM1 `DOC: GPUVM`，VM2 `setup_vm_pt_regs` / `setup_vmid_config`；VM4 仅用于识别系统侧边界。
- **产出：** 论文总图、术语关系及请求字段的功能分类；标注 unknown 的物理归属。
- **完成条件：** 能走通一次请求，并能区分翻译返回、数据返回和地址空间转换，避免把所有访问画成固定串行链。

### 第二轮：翻译层级与 miss 服务

- **前置与范围：** 第一轮上下文确定后，研究最终条目、中间页表信息、页大小及页表服务；PTW 内外归属未知时采用服务边界。
- **阅读：** C03 双服务路径；C02 的 PDE/PTE cache、BigK 回填限制和页大小；C01 的验证环境；VM8 的 walker 状态；VM2 `init_cache_regs`、VM5 第 3 节。
- **产出：** 命中层级与缺失信息的路径图、遍历依赖和返回关联；说明 translation cache 与缓存页表数据的 data cache 差异。
- **完成条件：** 对“中间信息命中但叶级缺失”能解释剩余工作及错误出口；不复制研究论文的级数或容量为目标参数。

### 第三轮：并发、共享资源与故障处理

- **前置与范围：** 已知正常 miss 生命周期，再研究多客户端竞争、下游阻塞、权限与遍历异常。
- **阅读：** VM5 第 4 节；VM2 fault 状态解码与 retry 相关配置。
- **产出：** outstanding 类型和资源释放表、错误分类、可重试/终止流程；如存在同页合并，明确不同上下文不能错误合并。
- **完成条件：** 任一已接收请求均有可说明的完成或异常出口，fault 不被误写成普通 cache miss，回压不丢失上下文。

### 第四轮：invalidation 与在途事务

- **前置与范围：** 已掌握在途状态，再研究更新可见性、失效范围、旧回填竞争和完成确认。
- **阅读：** VM2 `get_invalidate_req`，VM3 `flush_gpu_tlb`、`flush_gpu_tlb_pasid`、`emit_flush_gpu_tlb`。
- **产出：** 页表更新到重新使用的时序、参与者/条目/在途状态/完成条件表；legacy/light/heavy 名称只有在目标协议证实后才写入语义表。
- **完成条件：** 分清翻译查询、PTW 读、已翻译业务事务三类 outstanding；说明哪些必须等待及依据。驱动的 FLUSH_TYPE 数值不能替代硬件协议证明。

### 第五轮：系统 IOMMU 与 ATS 条件分支

- **前置与范围：** 第四轮失效基础完成，先核实目标系统是否启用相关能力；不支持时缩为边界说明，与第四轮合并。
- **阅读：** VM4 两类 invalidate 构造、`__domain_flush_pages` 与 `domain_flush_complete`；补读 VM10 的 AMD IOMMU 48882 rev3.09 选读笔记与 IO11 的 ATS/PRI/PASID 代码；完整 PCIe 扩展规范仍待取得。
- **产出：** GPUVM、系统 IOMMU、设备 ATC 的参与者图，地址与身份转换表，外部失效和本地失效的责任差异。
- **完成条件：** 不把 GPUVM TLB、ATC 与 IOMMU cache 当作同一缓存；没有协议原文支持时不确定 NACK、heavy 排空或自动续跑细节。

### 第六轮：预取、性能与全文收敛

- **前置与范围：** 基础正确性闭环后，判断预取是否适用；分析命中率、服务延迟、并发度与下游干扰，优化只在已存在的资源上讨论。
- **阅读：** VM5 第 4、5.3 节作干扰研究；补读 C04 的 miss 采样、预取对象、控制状态及地址算例纠错；该参考机制与目标芯片的对应仍待确认。
- **产出：** 条件机制取舍、瓶颈诊断、需要验证的代表性序列；回写整体图和边界，移除无证据的具体实现断言。
- **完成条件：** 每个优化能对应性能问题且保留权限/失效/fault 约束；最终论文的正常与异常流程一致，不以功能列表代替微架构。

## 页图版本与计算纠错

C01–C04 提供用户参考设计的更具体结构，不能统一假设为同一 AMD 产品。C01/C05 对 VM 类型的 UTCL1/ATCL1 标签存在差异；C02 的 BigK 回填条件有特定 cache 组织前提；C04 的连续地址示例已重新核算 PDE/PTE 索引，阈值定义仍有不明确处。以上差异在对应笔记保留，后续不得抄入目标论文而丢掉条件。

## 优先未知项与下一步

先确定目标代际、UTCL2 所属域、请求/响应契约、PTW 归属和地址空间模型；这些影响第一、二轮。失效完成语义在第四轮优先核实；预取算法和精确容量留后。公开 MMHUB 2.1.x 源码注明无 ATCL2 [VM2]，说明系统翻译能力确有版本边界，不能因此反推 shaobo/anshi。

本地 Codex 从第一轮开始，在 `technical-paper.md` 建立有来源的结构和两类地址场景。本页六轮是复杂度选择，允许证据到来后合并或拆分；任何调整均不增加已完成轮次数。

## 2026-09-25 资料补齐对本方案的影响

第 1–2 轮、第 3–5 轮优先复用 [C01](sources/C01-mm-utcl2-testbench.md)、[VM5](sources/VM5-mask-paper.md)、[VM10](sources/VM10-iommu-spec.md)。C01 第 4 页补出 lane/client 扩张及内部 UTCL1 sideband；MASK 补定量控制与基线；IOMMU 补 nested walk、PPR 身份/队列/完成。按结构定位资源，保留 C01/C05 版本差异。 本次仅更新依据和研究落点，不把任何待执行论文轮次改为完成。

## U24：请求地址到 HBM bank 的跨模块落点

接入轮次：基础路径及页表相关轮次。给出本次访问的翻译链、输出地址空间和属性，界定 GPUVM/IOMMU 分支；向后续 interleave 研究交接明确的地址语义。翻译服务与业务数据路径分别画图。

执行 [跨模块专题方案](../HBM/address-interleaving-plan.md)，将本模块的输入地址、配置/映射、输出目标与局部地址、子请求范围、返回关联填入同一组例子，结论写回本模块论文。先做资源/路径，再做映射、拆分返回和应用；不等所有模块论文完成，不将本次规划更新计为已完成研究轮次。
