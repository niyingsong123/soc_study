# GC 多轮研究与论文规划

方案版本：v1.0；依据 [研究范本 v1.2](../chip-study-plan.md)；日期：2026-09-24。
状态：规划与定向资料阅读完成；下列五轮详细研究均待执行。下一项：第 1 轮，先明确目标代际及 GL2 输入地址和外部接口。
[模块上下文](README.md) · [资料集](../sources.md#gc1) · [整体研究安排](../research-roadmap.md)

## 范围、术语与上下游

本目录仅研究 GL2、GRBM、RLC；GC 是这三个对象的归档入口，不据此补入 CU、CP、图形流水线的内部研究。其他引擎作为请求源或控制端出现在边界图中。

| AMD 名称 | 行业检索入口与关系 | 本次边界 |
| --- | --- | --- |
| GL2 | shared/sliced GPU L2 cache、non-blocking cache；CDNA 文档的 L2/TCC 是相关代际参照 | 数据缓存，不是 UTCL2；GL2/TCC 的名称与分片对应须按芯片确认 |
| GRBM | Graphics Register Bus Manager、indexed register access、broadcast register write、utilization counters | 寄存器选择和观测路径；不是数据 miss 必经级 |
| RLC | RunList Controller、power-management microcontroller、safe mode、clock gating | 名称保留历史语义，公开较新实现重在 GC 电源管理协作，不凭名字推断它是当前队列调度器 |

采用两个互补场景：一笔客户端读请求在 GL2 命中或 miss 后返回；一次控制端选择实例、修改配置并由 RLC 协调安全状态。上游客户端的 VA/PA、VMID、访问属性来自其接口约定；翻译发生在哪个阶段由 [UTCL1](../UTCL1/research-plan.md)/[UTCL2](../UTCL2/research-plan.md) 的接口研究核对，不能默认所有客户端先经过 GL2 再翻译。下游为内存服务接口；gfx115x 的公开材料给出 GL2→GCEA 的关系，不能直接替换成目标芯片 EA/DF 的精确连接。

## 整体微架构骨架

下图是用于分配研究问题的功能骨架；GL2 内部队列划分是待论证的参考分解，不代表已取得目标 RTL。数据分支与控制分支共同构成研究对象。

~~~mermaid
flowchart TD
    IN["客户端数据请求"] --> LOOK["GL2 分片选择与 tag 查询"]
    LOOK -->|命中| DATA["数据阵列与返回"]
    LOOK -->|未命中| MISS["未完成请求跟踪"]
    MISS --> MEM["下游内存接口"]
    MEM --> FILL["回填与替换处理"]
    FILL --> DATA
    DATA --> IN
    CTRL["驱动或控制端"] --> GRBM["GRBM 实例选择与寄存器访问"]
    GRBM --> CFG["GC 配置与状态"]
    CTRL --> RLC["RLC 固件与安全状态"]
    RLC --> CFG
    CFG -.-> LOOK
~~~

数据过程至少解释：请求被哪个分片接收、命中如何返回；miss 如何保留原请求身份、等待下游、回填后唤醒；替换遇到脏数据时如何研究写回与新请求竞争。是否合并同 line miss、采用何种分片散列、原子操作位于何处，均作为研究问题，不提前指定 MSHR 数量或流水级数。

控制过程解释：选择具体实例或广播目标→执行寄存器访问→观测状态→恢复访问选择；需要改变受电源管理影响的状态时，先核对 RLC safe-mode 进入/确认/退出的契约。该过程与正常请求并发时，哪些动作要求静止、排空或保留状态，是后续研究核心。

## 从结构分解研究内容

| 架构位置与优先级 | 需要解释的问题 | 就近资料与阅读目的 |
| --- | --- | --- |
| GL2 分片和数据阵列；核心 | 地址选择、hit/miss、读写路径、替换与脏数据；分片带宽和下游带宽为何不同 | [AMD CDNA 2 白皮书 p.5](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf#page=5) 的分片/排队/原子操作描述，作为 GC1 的 CDNA 参考；[gfx115x GL2](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gl2-cache.html) 的缓存与 GCEA 观测边界，见 P3 |
| miss 跟踪和返回；核心 | 何时接收请求，哪些资源被占用，回填如何关联等待者，反压如何传回客户端 | 同上 [GL2 请求与带宽指标](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gl2-cache.html)；公开指标只支持观察位置，不证明 MSHR 或返回队列实现 |
| 内存语义；核心/条件 | writeback、invalidate、原子操作和访问属性分别影响什么；CPU/GPU 一致性只在什么平台成立 | [GC1 p.5、p.8](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf#page=5)；目标 GCR/flush 行为仍需目标资料，不能由普通 cache 教程推定 |
| GRBM 访问与观测；核心 | 实例/广播选择、选择寄存器的并发保护；busy 指标的统计窗口与分母 | [GC2：gfx_v9_4_3_xcc_select_se_sh](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c#L692-L717)；[P5：MI200 GRBM counters](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html)，用于提出指标口径核对问题 |
| RLC 控制与恢复；核心 | firmware/硬件职责、safe mode、启停/复位、clock-gating 顺序、超时后如何处理 | [GC2：safe mode 与 register-access control](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c#L1364-L1418)、[clock-gating 更新](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c#L2710-L2746)；代码代表该公开 IP 版本的软件接口 |
| 多实例/虚拟化/功耗；条件 | 目标是否有多个 XCC、VF 限制或分区，哪些状态隔离、哪些共享 | [GC2：RLC resume](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c#L1597-L1635) 与 [P2：GC/RLC 职责](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure)；不由代码分支推广到全部 AMD 产品 |

扩展内容为替代缓存组织和更深入的时序/面积优化。只有它们能解释目标瓶颈时再加入，不为凑轮数展开通用 cache 教科书。

## 五轮安排

采用五轮，是因为 GL2 数据通路和 GRBM/RLC 控制通路都需独立解释，又需要一次统一复核；目标资料若表明 RLC 有额外独立协议，可拆分第 4 轮。

| 轮次 | 架构范围与核心问题 | 前置与阅读 | 文档产出和完成条件 |
| --- | --- | --- | --- |
| 1：职责与请求骨架 | 锁定参考代际，列三块职责与接口，解释一个 hit 和一个 miss | 先读本图、P2/GC1；只预读翻译模块输入输出约定 | 在本目录建立技术正文，给出两分支总图、接口表及完整基本流程；读者能判断数据、翻译与控制的区别 |
| 2：GL2 资源与进度 | 分片/tag/data、miss 跟踪、回填、替换/写回、争用和反压 | 第 1 轮；核对 UTCL 接口，读 GC1 p.5 与 P3；目标内部结构不足处另标参考设计 | 补 hit/miss/dirty-eviction 路径和资源生命周期；每种等待均有释放者，能解释同址与不同址请求的并发 |
| 3：GL2 语义与性能 | 访问属性、原子操作、维护操作的完成点；容量、带宽、尾延迟瓶颈 | 第 2 轮；GC1 一致性适用平台与 P3/P5 指标；借用 DF/UTCL 接口约定 | 形成“操作—作用对象—完成条件”表和瓶颈假设；不把缓存清理等同 TLB invalidate，不把下游请求量等同 HBM 实际读量 |
| 4：GRBM/RLC 控制 | 实例选择、访问并发、安全模式、固件边界、启停/恢复和超时 | 第 1 轮职责；GC2 上述函数；参照 SMU 的外部控制契约 | 补一条寄存器访问与一条 safe-mode 流程，指出状态保存者和返回依据；多实例/VF 条件单独说明 |
| 5：统一解释与观测 | 数据流与控制状态相互作用，哪些指标区分源端缺请求、GL2 阻塞、下游拥塞 | 第 2–4 轮与相关接口已有结论；P3/P5 和 GC2 | 整合章节、图与计数器位置，给出最小对照场景；以证据解释瓶颈/异常，模型仅在能区分假设时补做 |

## 未决问题与本地接续

优先确认目标产品/IP 代际、GL2 和 TCC 的名称关系、翻译边界、实际客户端与下游接口；随后核对分片映射、写策略、原子/一致性范围和 RLC 固件可见性。队列深度及逐周期实现放入第 2 或第 4 轮，不影响当前规划交付。

后续 Codex 先读 [README 的资料集入口](README.md#资料集与接续)，再读本文件第 1 轮所列材料。资料主条目集中在根 sources.md 的 P2–P5、GC1–GC2；新增细节写入本目录单一技术正文，回链本方案并更新轮次状态。上游入口关系可先借用 [SDMA 系统接口方案](../SDMA/research-plan.md)；不得因此在 GC 扩展 FE/BE/TBE 或其他 GC 引擎的内部实现。
