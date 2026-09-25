# 从请求地址到 HBM bank：跨模块研究方案

版本：v1.1；日期：2026-09-25；范围依据用户 U23、U24，推进方式按 U27 的单模块聚焦规则调整。**本专题已确定为必做主线，当前完成方案，逐地址推导和目标实现核验待执行。** 不增加资料篇数或已完成论文轮次。

本页统一维护跨模块问题、阶段和验收；具体机制仍写回各模块论文，原始资料只维护一份[技术笔记](sources/README.md)。研究以理解和运用为目标，不以取得厂商完整器件数据表为前置。

## 需要回答的主问题

给定请求的地址、长度、类型、身份及当前映射配置，能够解释：实际发生哪些内存事务，各事务为什么去相应 HBM stack、channel、pseudo-channel（PC）、bank group/bank、row/column；每一级是谁选择、谁传递、谁执行，最后怎样把数据、错误与完成对应回原请求。

这里的“不同 HBM”首先分清是不同 stack，还是同 stack 内不同 channel、PC 或 bank。层级关系、数量及 SID/bank group 的含义按所选代际核对，不把 HBM2、HBM3 和某个模拟器组织拼成一套结构。stack、die、控制器实例、PHY 实例和逻辑通道不能按名称假定一一对应。

同时区分两个问题：改变请求起始地址后，目标如何变化；一笔带长度的请求是否跨越映射或传输边界，需要在哪里拆成多个子请求。先标明“请求”是软件操作、SDMA 命令、cache line/sector 访问、fabric 事务，还是 DRAM 命令，避免将不同粒度混算。

## 先建立一条有依据的访问路径

优先选择一个明确产品/配置的本地 HBM 普通读和写，先固定起始接口及其地址空间，再追踪实际访问分支。GC 缓存路径与 SDMA 路径分别建图；cache 命中、旁路、写回以及远端内存另画条件分支。UTCL 的翻译服务与数据传输分开画，不画成所有数据必经 UTCL1→UTCL2→HUB→EA→DF 的统一串联。

目标资料不足时，用明确标注的功能参考模型完成演算，将未知的目标连接与位段保留为待核实。可以用 CDNA 资料理解封装/存储层次，用 PG276 理解控制器实例，用 ATL 研究映射方法；三者分别注明产品与证据用途。此专题保持必做：当前逐模块研究自身职责、资源、局部地址语义及必要接口，保存具体跨模块问题；相关模块的必要详细结论形成后，再集中建立完整路径与统一地址演算。关键接口疑点即时核对，不等待无关模块或可选细节。

## 沿数据通路分配研究责任

下表是问题分工，不是已验证的 RTL 串接图；每条选定路径只保留实际参与的模块。

| 位置与关联轮次 | 必须查清的微架构问题 | 现有资料入口与使用边界 |
| --- | --- | --- |
| 源端：GC/GL2 第 1–2 轮、SDMA 接口第 1–2 轮 | 输入地址/长度/byte mask；合并、拆分、cache line/sector 与写回粒度；GL2 slice/bank 选择是否与下游目标选择使用不同函数；哪些访问根本不下达 HBM | [GC1](../GC/sources/GC1-cdna2-memory.md)、[FAB1](../DF/sources/FAB1-cdna3-iod-memory.md)、[SD1](../SDMA/sources/SD1-sdma-system-lifecycle.md)、[SD2](../SDMA/sources/SD2-sdma52-completion-maintenance.md)。SDMA 目标内部只在外部项目只读核对；不扩大 GC 引擎研究范围 |
| UTCL1/UTCL2 基础轮次、HUBS 第 1–3 轮 | 此段是 VA、GPA、SPA、FB 地址还是窗口内偏移？何处做翻译、aperture 判定或 base 处理？跨页后是否仍物理连续？翻译结果与请求属性如何交接 | [VM1](../UTCL2/sources/VM1-gpuvm-address-spaces.md)、[VM2](../HUBS/sources/VM2-mmhub-v2.md)、[C03](../UTCL2/sources/C03-utcl2-topology.md)。页表翻译不是 HBM interleave；C03 是参考设计而非目标 GPU 证明 |
| EA 第 1–3 轮、HUBS 第 2–3 轮 | 地址/目标 ID、命令和写数据如何保持配对；内部 bank/group、队列分区与仲裁资源对应什么？目标选择结果如何影响反压和并发 | [C05](../HUBS/sources/C05-mmhub-dagb-ea.md)、[VM6](../EA/sources/VM6-gcea-metrics.md)。EA 内部存储 bank 或指标中的 bank 不能未经核对就等同 HBM bank |
| DF/CS 第 1–3 轮 | system/local/remote 目标、地址窗口与内存分区；stack/channel/CS 选择究竟在哪个模块；交织粒度、hash/XOR、非二次幂通道及配置来源；交给下游的是完整地址还是 normalized/local address | [FAB1](../DF/sources/FAB1-cdna3-iod-memory.md)、[FAB2](../DF/sources/FAB2-df36-registers-counters.md)、[FAB3](../DF/sources/FAB3-atl-address-core.md)、[FAB6](../DF/sources/FAB6-atl-denormalization.md)、[P1](../DF/sources/P1-ryzen-fabric-topology.md)。ATL 是 RAS 软件逆向解码，不能把软件算法顺序画成 GPU 硬件流水 |
| SWITCH 第 3 轮；跨 die 时联读第 4 轮 | NI 接收地址还是目标 ID；地址路由、端点选择与 router 下一跳选择如何分开；包拆分是否改变内存事务边界；返回 ID、重排与资源预留如何处理 | [R8](../SWITCH/sources/R8-axi-ordering-contract.md)、[R23](../SWITCH/sources/R23-chi-ea-protocol.md)。协议仅作行业参考；NoC 路由选择不等于重新分配物理存储位置 |
| UMC 第 1–3 轮 | 上游已去掉/编码了哪些选择位；余下地址怎样解到 channel/PC、适用的 SID/BG/bank、row/column/burst offset；映射与读写队列、开放行、命令可发性如何相连；跨边界子请求归谁管理 | [MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md)、[MEM12](../UMC/sources/MEM12-ramulator-hbm-controller.md)、[MEM13](sources/MEM13-ramulator-hbm3-model.md)。映射与调度分开解释，再研究二者的性能耦合 |
| PHY 第 1–3 轮、HBM 第 1–3 轮 | 逻辑目标怎样对应实际 PHY/channel/PC 接口；命令地址、写数据、读数据有效期如何对齐；bank 行状态、共享命令资源、刷新与训练就绪如何约束服务 | [MEM11](sources/MEM11-jedec-scope-gap.md)、[MEM13](sources/MEM13-ramulator-hbm3-model.md)、[MEM16](../PHY/sources/MEM16-dfi51-interface.md)、[MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md)。区分逻辑映射、信号适配及物理 lane 映射，不能预设 PHY 重新做系统地址 hash |
| 反向数据/完成；各模块对应返回轮次 | parent/child ID、字节范围和错误如何保留；多个目标乱序返回后何处重组、何处受保序约束；写缓冲接收、写命令发出和上游完成分别何时发生；阻塞时哪些资源仍占用 | [R8](../SWITCH/sources/R8-axi-ordering-contract.md)、[FAB4](../DF/sources/FAB4-dma-fence-contract.md)、[MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md)。不把链路完成、HBM 命令执行和软件 fence 视为一个事件 |

若选主机访问，再接入 PCIe/NBIF/HDP 分支；若选跨 die 目标，再补 CAKE/相关链路。SMN/SMU/RSMU 仅在确有映射、分区、训练或配置证据时接入控制平面，不能为“全通路”把所有模块硬串进去。

## 地址映射必须分层记录

独立模块阶段先保存本模块的输入地址空间、配置、变换/选择、输出目标及返回关联，并标明外部假设；只读取完成本模块所需的相邻契约。进入集中跨模块阶段后，再以同一配置和请求统一下表，核对各模块结果能否衔接，避免把互不兼容的例子拼在一起：

| 层/执行模块 | 输入地址空间、地址及请求长度 | 配置与映射函数 | 输出目标 ID、局部地址及子请求范围 | 返回关联与依据 |
| --- | --- | --- | --- | --- |
| 每个实际转换或选择点各一行 | 同时记单位、已完成的翻译和属性 | 位抽取、XOR、取模或其他已证实函数；记录 base、粒度、目标集合、配置版本 | 明确哪些位保留、移除或编码；映射到哪个逻辑/物理资源 | parent/child 身份与原请求 byte offset；原文/代码位置或教学假设 |

需要分别解释：页表映射；适用的缓存 slice/set/bank 映射；系统/封装内存目标与交织；控制器内的 DRAM 地址解码。源端数据布局/tiling swizzle 仅在相关请求用到时说明，不能与 fabric hash 混为一个函数。访问同一 bank 的不同 row 和访问不同 bank，最终导致的命令依赖也必须区分。

交织不是每次发请求临时挑一个空闲 HBM。研究固定配置下的存储归属与排队/路由策略各自能改变什么；如讨论分区或映射变化，另核其生效条件、旧在途事务和数据布局的一致性，不能假定热改配置自动正确。

已有原始资料可直接提供两个定位点：[PG276 地址映射章](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Address-Map-and-Protocol-Considerations)分别列出 stack、目标 AXI 端口与 HBM 地址，并给出一笔 AXI 访问变成两个不同 bank group 命令的例子。后续演算可先复现该实例，再与目标 GPU 对照；不能将其具体位号移植为 GPU 规格。缓存分片、目标 channel/stack 与 bank-group interleave 因而应分别立题，而不只写一个“地址 hash”小节。

## 四个推进阶段与具体产出

以下四阶段在相关模块形成必要的独立详细结论后集中推进；此前先完成各模块既有轮次中的本地职责与必要接口研究，记录专题依赖问题。对齐所选场景所需的核心基础即可，不要求全部模块或可选细节完结；四阶段不机械增加每个模块的轮数。

| 阶段 | 要完成的工作 | 完成条件 |
| --- | --- | --- |
| A：资源与路径 | 固定一个参考产品/配置和请求类别；画 stack/channel/PC/BG/bank/row/column 资源图及正反向模块图；列清翻译服务、cache 命中和远端分支 | 每个术语有作用域，每条边有证据或明确参考假设；未知目标拓扑不妨碍先做参考演算 |
| B：逐级地址演算 | 固定配置，写目标选择与局部地址公式；为连续、跨 stripe、跨 row、固定 stride 等地址填写统一追踪表；对 hash 和非二次幂只展开适用实现 | 从入口地址可以算到实际逻辑资源；解释各位/运算的用途，没有重复交织、丢失位或混用地址空间。目标实例未知时交付明确标注的教学映射，不冒充真实位图 |
| C：拆分、执行与返回 | 追踪一笔跨边界大请求，以及同长度、不同起始地址的请求；列子请求覆盖范围、byte mask、队列、命令、返回和释放条件；联入反压/刷新/错误 | 子请求覆盖正确且无意外重叠；读数据能按原字节位置恢复；完成/错误与资源生命周期闭环。atomic 或不可拆事务另核协议，不能沿用普通 memcpy 的拆分假设 |
| D：应用与校验 | 用地址序列解释行局部性、bank 并行、共享总线争用、热点与有效带宽；在地址公式已固定时按需写一个小型 trace/decode 脚本并对照原例 | 能指出瓶颈发生在哪层；将配置、源地址、各层选择与结果一起保存。脚本是功能/映射校验，未建时序模型不得据其宣称芯片带宽或延迟 |

## 演算场景与检查重点

至少覆盖以下有区分度的场景，数值来自固定公开实例或明确的教学假设：

1. 单个可服务粒度与连续地址：哪些地址只改变 column/offset，何时切 bank、PC、channel 或 stack？没有真实位图时先建立符号边界。
2. 相同长度、不同起始地址：分别构造同 bank 同 row、同 bank 不同 row、不同 bank，以及不同 channel/stack 的情况，比较资源和命令依赖。
3. 一笔跨边界请求：分别跨映射 stripe、cache line/burst 和页面；逐层核拆分责任，不能把三个边界假设为同一个大小。跨页必须重新考虑翻译结果的物理连续性。
4. 固定 stride 与热点：追踪实际目标分布；对比纯位选与已证实 hash，解释何时看似连续/规则的流量仍聚集，不能只根据总请求数宣称负载均匀。
5. 多目标乱序返回与下游暂停：让一个目标被刷新或反压，检查其他目标能否进展、返回空间如何保留、父请求何时可完成。并发能力须落到真实资源或教学模型的声明中。
6. 条件场景：非二次幂通道、分区/屏蔽实例、远端 HBM，以及 RAS 逆向定位，仅在所选配置适用时展开。用 [FAB3/FAB6](../DF/sources/README.md) 检查“局部地址 + 来源实例 + 配置”的反解条件，不能假设单独局部地址总能唯一反解。

## 本地 Codex 接续与状态

当前先按[路线图](../research-roadmap.md)及用户指定任务聚焦单个模块，保存本模块所需的资源/地址/返回结论和具体依赖问题，必要接口疑点立即核实。相关模块核心基础具备后再集中执行 A–D：先统一资源与路径，再固定有证据的映射做演算。无需等待厂商 datasheet、无关模块论文或可选细节。优先复用本页所链笔记，再针对缺失的地址位、粒度、实例对应及返回契约回原文。每个阶段把结论写回责任模块的同一论文，专题只维护整体路径、地址追踪例子、跨模块差异与状态，避免复制整套资料总结。

当前未确认：目标 GPU 精确地址位/hash、stack/channel/CS/UMC/PHY 实例对应、各请求类别的真实拆分位置与响应合同。**本方案没有声称这些目标细节已经查明，亦未运行地址模型。** 厂商数据表继续按需参考；bank 划分、地址交织和完整数据通路则明确属于核心必做内容。
