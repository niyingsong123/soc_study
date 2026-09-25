# SDMA 系统接口接续方案

方案版本：v1.1；依据 [研究范本 v1.4](../chip-study-plan.md)；日期：2026-09-24。
状态：本仓库系统接口规划完成；下列三轮接口整理待执行。FE/BE/TBE 详细研究的进度由外部项目独立记录，本文件不替它报告完成。
[模块上下文及外部入口](README.md) · [资料集](../sources.md) · [整体安排](../research-roadmap.md)

## 逐篇笔记与本方案的研究落点

先查[模块资料索引](sources/README.md)了解每篇讲什么，再读对应详细笔记；笔记内保留原文链接、版本、阅读位置、机制及重要限制。本次仅补资料与修订规划，下面的论文轮次完成状态不变。

| 微架构位置 | 对应轮次 | 可直接复用的技术笔记 | 本次补充的研究重点 |
| --- | --- | --- | --- |
| 目标接口与外部范围 | 接口第 1 轮 | [L1](sources/L1-external-glossary-scope.md)、[L2](sources/L2-external-shaobo-scope.md)、[L3](sources/L3-external-open-questions.md)、[P2](../GC/sources/P2-amdgpu-hardware.md) | 外部材料本次未读，沿原入口复查 FE/BE/TBE；不复制另一套内部规格。 |
| 系统提交、寻址与维护 | 接口第 1–2 轮 | [SD1](sources/SD1-sdma-system-lifecycle.md)、[SD2](sources/SD2-sdma52-completion-maintenance.md)、[IO3](../PCIE/sources/IO3-linux-dma-api.md)、[VM3](../UTCL2/sources/VM3-gpuvm-invalidation.md)、[IO5](../NBIF/sources/IO5-nbio74-host-bridge.md)、[IO13](../NBIF/sources/IO13-nbio79-partition-doorbell.md) | 区分实例、doorbell、DMA 地址、GCR/HDP/TLB 维护和相关资源。 |
| 完成、事件和恢复 | 接口第 2–3 轮 | [FAB7](../DF/sources/FAB7-amdgpu-fence-lifecycle.md)、[MG7](../IH/sources/MG7-ih-core-consumer.md)、[MG8](../IH/sources/MG8-irq-dispatch-lifecycle.md)、[MEM3](../UMC/sources/MEM3-amdgpu-ras.md) | 用 fence/IV 路径定义 SoC 契约，公开驱动不等于 shaobo/anshi 的内部实现。 |


## 范围与微架构入口

本仓库把 SDMA 作为代表性请求源，用它提出翻译、数据传输、命令完成与中断的接口问题；内部微架构继续在独立 sdma_repo 管理。System DMA、DMA engine、copy engine 是公开研究入口，但它们不能证明 shaobo/anshi FE、BE、TBE 的具体分工。

现存 [模块映射图](../module-map.md#从已知-sdma-路径建立整体认识) 与 [README 摘要](README.md) 构成接口骨架：shaobo FE 分发到 BE/TBE，TBE 内 dma_utcl1 miss 请求 UTCL2，TBE 写回涉及 MMHUB，BE 通过 DF 数据接口工作。CF 命令接口与 DF 数据接口分别理解。这些是仓库已保存的 L1/L2 摘要；本轮未读取外部原件。

| 场景中的接口位置 | 本仓库需要形成的约定 | 资料入口及边界 |
| --- | --- | --- |
| 上游命令与后端任务 | 谁提交、谁拆分，原始命令与后端任务怎样对应 | [SDMA 现有摘要](README.md)、[CF 入口](../CF/README.md)；仅保留现存说明，字段/精确握手待原文 |
| 地址与身份 | 源/目的各用什么地址空间，谁请求翻译，如何返回权限或故障 | [UTCL1 方案](../UTCL1/research-plan.md)、[UTCL2 方案](../UTCL2/research-plan.md)；[P2 GPUVM](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#amdgpu-virtual-memory) 仅作公开基础  技术笔记：[P2](../GC/sources/P2-amdgpu-hardware.md)。 |
| 数据服务 | 读请求与写请求怎样关联，返回数据/接收容量/完成是什么 | [DF 方案](../DF/research-plan.md)、[HUBS 方案](../HUBS/research-plan.md)；是否缓存、经过哪些端点以资料确认 |
| 完成、错误及软件可见性 | credit、EOC、写入可见、fence、IH 通知是否同一完成点 | [CF 摘要](../CF/README.md)、[IH 方案](../IH/research-plan.md)；[P2 SDMA/IH 职责](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure)  技术笔记：[P2](../GC/sources/P2-amdgpu-hardware.md)。 |

代表性工作过程采用一次内存搬运：任务被接收→分别解决源和目的地址/权限→发起读、承接返回数据并发起写→根据实际接口定义确认完成→必要时通知软件。这里是需要补齐的事务说明框架，不宣称目标流水线必须按这些阶段完全串行；读写重叠与拆分策略由外部 SDMA 研究负责。

## 三轮系统接口安排

| 轮次 | 核心范围 | 前置与阅读 | 产出和完成条件 |
| --- | --- | --- | --- |
| 1：确认源端约定 | 仅整理请求类别、身份、地址/属性、输入输出与命令完成层级 | 先读本 README、根 module-map 的已知路径；本地可用时只读外部项目上下文与对应来源 | 在本目录补系统接口表；每项标明已知/待核实且有来源，外部内部研究不复制；可作为其他模块规划前置 |
| 2：补齐翻译和数据服务 | 分别跟踪源/目的翻译、请求接收、数据返回、反压与错误 | UTCL1/UTCL2、HUBS、DF 的基本接口结论；按各方案就近资料回读 | 形成一条正常搬运与一条 fault/阻塞场景的跨接口说明；不把翻译完成、数据完成与原始命令完成混为一谈 |
| 3：复核完成与恢复 | 核对取消、维护操作、故障通知、fence/IH 以及不可继续时的责任端 | 第 2 轮，CF/IH 及内存侧相关详细研究已形成；外部 SDMA 对应接口可读 | 更新系统关系和未决项；每种完成有明确可见性/作用域，不编造目标 cancel 或 invalidation 协议 |

本方案的三轮是 SoC 接口整理，不能计为外部 SDMA 的新研究轮次，也不能提前算作 SWITCH 最终系统复审完成。若本地外部资料仍不可读，保留具体接口问题并沿已有公开约定继续其他模块，不恢复缺失原件或扩大云端访问范围。

## 下一步与资料集

下一步只做第 1 轮源端约定，足够启动相邻模块规划。先查看 [资料集中的 L1–L3 登记及 P2](../sources.md)，然后通过 [本地外部入口](README.md#外部入口) 按需回原文；云端不声称已读取这些外部路径。接口结论在本目录维护，资料简介集中在 sources.md，详细 SDMA 规格继续由独立项目作为唯一维护处。

## 2026-09-25 资料补齐对本方案的影响

接口第 1–3 轮优先复用 [L1](sources/L1-external-glossary-scope.md)、[L2](sources/L2-external-shaobo-scope.md)、[L3](sources/L3-external-open-questions.md)。三项外部资料本次未挂载，已记录本地只读接续方式与回写范围。公开 SD1/SD2 及 C01 新页只作对照，不能替代目标原文。 本次仅更新依据和研究落点，不把任何待执行论文轮次改为完成。

## U24：请求地址到 HBM bank 的跨模块落点

接入轮次：接口第 1–2 轮。记录搬运命令与源/目的访问的粒度、地址类型、子请求范围和返回/完成关联；将跨页与跨 interleave 边界分开核对。内部拆分实现只在外部项目只读研究，本仓库仅回写系统接口结论。

执行 [跨模块专题方案](../HBM/address-interleaving-plan.md)，将本模块的输入地址、配置/映射、输出目标与局部地址、子请求范围、返回关联填入同一组例子，结论写回本模块论文。先做资源/路径，再做映射、拆分返回和应用；不等所有模块论文完成，不将本次规划更新计为已完成研究轮次。
