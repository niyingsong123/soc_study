# HBM 资料索引与逐篇技术笔记

更新日期：2026-09-24。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 18 个可复用来源，主笔记归档 4 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 器件组织与数量级 | [MEM9](MEM9-micron-hbm3e.md) → [MEM10](MEM10-samsung-hbm3.md) → [MEM1](../../UMC/sources/MEM1-pg276-hbm-controller.md) | 第 1 轮：区分 stack 层数、channel/PC、容量和原始带宽；修正 GB/Gb，保留厂商测试条件。 |
| 命令、时序和维护 | [MEM13](MEM13-ramulator-hbm3-model.md) → [MEM12](../../UMC/sources/MEM12-ramulator-hbm-controller.md) → [MEM2](../../UMC/sources/MEM2-ramulator2-paper.md) → [MEM11](MEM11-jedec-scope-gap.md) | 第 2–3 轮：用模型理解层级约束，完整 JEDEC 未读时不能以模型命令表声称标准合规。 |
| 保护域与持续性能 | [MEM1](../../UMC/sources/MEM1-pg276-hbm-controller.md) → [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) → [MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) → [MG11](../../RSMU/sources/MG11-umc67-ras-comparison.md) | 第 3–4 轮：ODECC、parity、UMC ECC、poison 和页面隔离不是同一个保证；采样窗口可能有间隙。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [P5：MI200 的翻译、EA credit 与在途请求计数](../../GC/sources/P5-mi200-counters.md) | 提供可操作的观测点：UTCL1 translation/permission miss、UTCL2 busy、EA 按 IO/GMI/DRAM 分类的 credit stall，以及在途请求积分。适合做跨模块性能诊断，但不是目标芯片的计数器规格。 | 厂商/项目官方资料。本次成功读取页面，精读 GRBM、CPF/CPC 的翻译相关项、TCP UTCL1、TCC/EA 及 derived metrics 对应条目和缩写；未逐一研究全部指令/纹理计数，未采样验证。 | [原文](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html) |
| [GC1：CDNA 2 的分片 L2、内存与互联边界](../../GC/sources/GC1-cdna2-memory.md) | 从 MI200 的公开整体结构理解 GCD 内 L2、内存控制器、HBM 和多种互联的分工。适合建立模块间地图与带宽层级；不提供内部队列或一致性状态机。 | 厂商/项目官方资料。精读打印页 2、5–8 的架构/存储/通信，视觉核对 p.3 Fig.1a；计算指令章节不在本笔记范围。 | [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-business-docs/white-papers/amd-cdna2-white-paper.pdf) |
| [FAB1：CDNA 3 白皮书：XCD/IOD、memory-side cache 与一致性层次](../../DF/sources/FAB1-cdna3-iod-memory.md) | 解释 CDNA 3 把计算侧 L2、IOD 存储侧 cache、HBM 与互联重新分配后的职责，特别区分 snoop filter、cache 数据和 CPU/GPU 统一内存；适合校准模块边界与带宽口径。 | 厂商/项目官方资料。已核读 XCD、memory architecture、IOD/Infinity Cache、HBM 和分区段落，重点印刷第 9–13 页；没有据此补写未公开的 DF 协议状态机。 | [原文](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf) |
| [FAB2：Linux DF 3.6：通道编码、hash、实例访问与性能计数器](../../DF/sources/FAB2-df36-registers-counters.md) | 从 AMDGPU 的 DF 3.6 回调识别软件能观察的配置与计数器生命周期，特别说明寄存器编码不等于实际通道数、计数器零值也可能来自未支持或重装失败。 | 固定版本公开代码。已读 channel/hash、broadcast、clock gating、PMC 分配/启动/读回/停止及 poison-query 相关函数；本文件是软件编程视图，不是 DF RTL。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c) |
| [FAB3：AMD ATL：从 UMC 归一化地址恢复系统物理地址](../../DF/sources/FAB3-atl-address-core.md) | 展示 RAS 地址解码必须结合 socket/die/CS、DRAM map、interleave/hash、base 与 MMIO hole；用于避免把 UMC 错误地址直接解释成系统 PA。 | 固定版本公开代码。已读完整文件，重点 norm_to_sys_addr、base/hole 处理及初始化/decoder 注册。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c) |
| [FAB5：AMDGPU XGMI：hive、节点拓扑、链路信息与 RAS](../../DF/sources/FAB5-xgmi-topology.md) | 从驱动观察 XGMI 多设备拓扑的建立、固件协作、hop/link 信息和错误入口；特别记录 v6.12 中 pstate 切换实际被提前返回禁用，防止把死代码当现行功能。 | 固定版本公开代码。已读 hive 生命周期、add/remove、PSP topology、hop/link 查询、pstate 和 RAS 入口；未获得 XGMI 私有线协议。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c) |
| [FAB6：AMD ATL denormalize：非二次幂通道与 hash 的逆向重建](../../DF/sources/FAB6-atl-denormalization.md) | 解释 3/5 倍通道模式为何不能靠插入几位 channel ID 还原 PA，以及 DF4.5 如何枚举丢失位和余数，再用正向映射与 CS 身份校验候选地址。 | 固定版本公开代码。已读模式分派、DF4/DF4.5 非二次幂路径及 candidate verification；大量具体位段仅在本版本代码中有效，本笔记不逐个复制。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/denormalize.c) |
| [MEM1：PG276：HBM 拓扑、地址映射、重排与错误边界](../../UMC/sources/MEM1-pg276-hbm-controller.md) | 研究请求进入内存控制器后为何排队、如何选 bank/行、何时返回错误。重点是两级重排、共享命令资源、地址映射对调度的影响；适合 UMC 主线与 EA/HBM 联读。 | 厂商/项目官方资料。已读上述章节正文；AMD FPGA HBM2 IP 实例，不是 GPU UMC 规格；未读全指南或运行 IP。 | [原文](https://docs.amd.com/r/en-US/pg276-axi-hbm) |
| [MEM2：Ramulator 2.0：控制器、DRAM 模型与验证边界](../../UMC/sources/MEM2-ramulator2-paper.md) | 解释如何把请求调度、命令前置条件、时序状态和维护策略拆开建模；适合搭建 UMC 教学模型与理解验证覆盖，不是 AMD UMC 实现说明。 | 原始论文。已读架构、DRAM 表达方式及 III 节验证/实验正文；未复现实验；当前源码另见 MEM12/MEM13，不能与论文当成同一版本。 | [原文](https://arxiv.org/html/2308.11030v2) |
| [MEM3：AMDGPU RAS：错误计数、坏页与恢复策略](../../UMC/sources/MEM3-amdgpu-ras.md) | 从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。 | 厂商/项目官方资料。已读文档正文的支持、控制、计数和坏页接口；未执行注错、复位或 EEPROM 操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) |
| [MEM4：DFI 官方资料：控制器与 PHY 的边界及 6.0 变化](../../PHY/sources/MEM4-dfi-version-boundary.md) | 用于确定 controller/PHY 分工、训练所有权与规范版本；尤其修正“DFI 不支持 HBM”的过时概括。公开更新不能代替接口信号规范。 | 规范组织公开介绍。已读公开介绍与发布消息；未取得登录下载的完整 DFI 规范，不填写未核实的信号、时序或 HBM profile。 | [原文](https://ddr-phy.org/) |
| [MEM9：Micron HBM3E：组织、容量与带宽口径](MEM9-micron-hbm3e.md) | 提供 HBM3E 器件组织与产品级指标，用于容量/通道/带宽的数量级检查；不包含完整命令时序或端到端性能保证。 | 厂商/项目官方资料。已读产品说明及 FAQ；部分时间表仍为历史表述，不据此判定当前供货；未取得 datasheet。 | [原文](https://www.micron.com/products/memory/hbm/hbm3e) |
| [MEM10：Samsung HBM3：产品指标与 ODECC 表述边界](MEM10-samsung-hbm3.md) | 用于与 HBM3E 对照容量和原始带宽，并识别器件内部 ECC 宣传与系统 RAS 的区别；不提供可实现的 ECC 编码或命令规范。 | 厂商/项目官方资料。已读速度、容量、功耗和可靠性正文；正式 datasheet 需另行取得，当前未读。 | [原文](https://semiconductor.samsung.com/dram/hbm/hbm3/) |
| [MEM11：JESD238：HBM3 正式标准入口与待补范围](MEM11-jedec-scope-gap.md) | 这是完整规范尚未取得的缺口记录；用于判断哪些 HBM3 细节必须回查正式标准，不能作为时序、编码或合规依据。 | 规范全文未取得。未取得全文；不声明已读标准，不推定最新修订字母或具体字段。当前笔记是范围索引和后续补读任务。 | [原文](https://www.jedec.org/standards-documents/docs/jesd238) |
| [MEM12：Ramulator 当前 HBM 控制器：双命令槽与 FRFCFS](../../UMC/sources/MEM12-ramulator-hbm-controller.md) | 研究请求如何变成可发出的列/行命令，以及优先级、激活缓冲和共享命令总线怎样约束吞吐；提供代码级 UMC 对照实例。 | 固定版本公开代码。已读所列文件的队列选择、时钟推进、slot eligibility、发命令和调度比较函数；未运行仿真，未通读所有插件/完成回调实现。 | [原文](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/impl/hbm34_controller.cpp) |
| [MEM13：Ramulator HBM3：层级状态、时序与生成式模型](MEM13-ramulator-hbm3-model.md) | 适合逐项理解 HBM3 模型的共享/独立资源、命令依赖与时序作用范围；可与控制器代码联读，不能替代 JEDEC 标准。 | 固定版本公开代码。已读层级、命令/时序声明、命令总线分类及主要 timing 约束；未运行模型，未与完整 JEDEC 逐条核验。 | [原文](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/dram/impl/HBM3.cpp) |
| [MEM14：UMC 8.10 驱动：错误分类与地址候选展开](../../UMC/sources/MEM14-umc810-ras-address.md) | 研究错误地址为何不是现成系统物理地址，以及 UE 计数为何可能没有可隔离页面；提供具体寄存器与转换路径，适合 RAS 联读。 | 固定版本公开代码。已读错误计数、通道索引、地址转换、状态清除及固件 ECC 信息分支；未读取目标芯片寄存器，不能推广到其他 UMC 代际。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c) |
| [MG11：UMC 6.7：错误地址展开与 poison 模式的代际对照](../../RSMU/sources/MG11-umc67-ras-comparison.md) | 补充 RSMU 相邻的 UMC RAS 路径，解释 hash/列位模糊如何扩大隔离候选，及 poison 查询如何依赖寄存器；用于对照 UMC 8.10。 | 固定版本公开代码。已读地址转换、直接/固件错误地址路径及 poison 查询；这不是 RSMU 内部实现证据。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c) |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
