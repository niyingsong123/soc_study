# RSMU 资料索引与逐篇技术笔记

更新日期：2026-09-25。先读模块整体微架构与当前问题，再用下表判断需要哪篇笔记；笔记保留机制、条件、状态/接口、版本和待核实边界，精确字段或新版本问题再回原文。

本模块列出 11 个可复用来源，主笔记归档 2 篇。跨模块来源链接到唯一主笔记，计数不能跨模块直接相加。资料阅读不计为论文轮次完成。

[模块上下文](../README.md) · [研究方案](../research-plan.md) · [全局来源编号](../../sources.md) · [研究范本](../../chip-study-plan.md)

## 按微架构问题选读

| 研究位置 | 推荐顺序 | 重点与适用轮次 |
| --- | --- | --- |
| 模块身份与直接寄存器证据 | [MG5](MG5-rsmu-umc-index.md) → [C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 第 1 轮：MG5 的 AMD 作者命名证据和 C01/C05 参考位置与公开 RSMU index register 分别记载，目标映射仍未知。 |
| 端点访问及错误状态 | [MG11](MG11-umc67-ras-comparison.md) → [MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) → [MG4](../../SMN/sources/MG4-smn-indirect-access.md) | 条件第 2 轮：UMC RAS 路径是邻接资料，不能自动归入 RSMU；地址候选与 poison 查询有代际差异。 |
| 可访问性与恢复责任 | [MG2](../../SMU/sources/MG2-smu13-control.md) → [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) → [MG10](../../SMN/sources/MG10-atl-system-identity.md) | 条件第 3 轮：结合原 mode 恢复、DF C-state 和身份配置，资料不足时不扩大为完整管理处理器。 |

## 每篇资料讲什么

| 编号与技术笔记 | 核心内容与何时值得读 | 资料性质及实际阅读范围 | 原文入口 |
| --- | --- | --- | --- |
| [C05：MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界](../../HUBS/sources/C05-mmhub-dagb-ea.md) | 连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。 | 用户页图·参考设计。读取 41 页可提取文字，直接核看第 7、18、27、32、33、34、40 页关键图表；图中缺乏的 RTL 时序、RAM 端口数和严格完成定义保持未知。 | 原图已移出仓库 |
| [FAB3：AMD ATL：从 UMC 归一化地址恢复系统物理地址](../../DF/sources/FAB3-atl-address-core.md) | 展示 RAS 地址解码必须结合 socket/die/CS、DRAM map、interleave/hash、base 与 MMIO hole；用于避免把 UMC 错误地址直接解释成系统 PA。 | 固定版本公开代码。已读完整文件，重点 norm_to_sys_addr、base/hole 处理及初始化/decoder 注册。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c) |
| [MEM3：AMDGPU RAS：错误计数、坏页与恢复策略](../../UMC/sources/MEM3-amdgpu-ras.md) | 从软件侧梳理 CE/UE、坏页状态和恢复动作，适合连接 UMC 检测、IH 通知及页面隔离；不能用软件状态替代硬件错误定位。 | 厂商/项目官方资料。已读文档正文的支持、控制、计数和坏页接口；未执行注错、复位或 EEPROM 操作。 | [原文](https://docs.kernel.org/6.12/gpu/amdgpu/ras.html) |
| [MEM14：UMC 8.10 驱动：错误分类与地址候选展开](../../UMC/sources/MEM14-umc810-ras-address.md) | 研究错误地址为何不是现成系统物理地址，以及 UE 计数为何可能没有可隔离页面；提供具体寄存器与转换路径，适合 RAS 联读。 | 固定版本公开代码。已读错误计数、通道索引、地址转换、状态清除及固件 ECC 信息分支；未读取目标芯片寄存器，不能推广到其他 UMC 代际。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c) |
| [MG1：SMU 公共驱动：mailbox、错误状态与表传输](../../SMU/sources/MG1-smu-message-table.md) | 详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。 | 固定版本公开代码。已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c) |
| [MG2：SMU 13 公共控制：固件就绪、表地址和频率约束](../../SMU/sources/MG2-smu13-control.md) | 连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。 | 固定版本公开代码。已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c) |
| [MG4：AMD SMN：index/data 访问与错误判定](../../SMN/sources/MG4-smn-indirect-access.md) | 解释 SMN 软件访问的地址选择、互斥与返回值局限；适合控制网络的访问契约研究，不足以给出 SMN 路由器或包格式。 | 固定版本公开代码。已读 SMN 访问函数及其完整错误语义注释；不是 GPU 所有 SMN 接入路径的统一规格。 | [原文](https://github.com/torvalds/linux/blob/v6.12/arch/x86/kernel/amd_nb.c) |
| [MG5：RSMU 寄存器线索与 UMC 6.1 访问模式](MG5-rsmu-umc-index.md) | 用 AMD 作者提交确认 remote SMU 名称及寄存器接口/错误/复位职责，配合 UMC index-mode 保存恢复与 BOWEN 参考位置；目标实例/内部实现仍未知。 | 固定版本公开代码。已读 AMD 原始提交 245219a、两份 v0.0.2 头及 Linux v6.12 UMC index/RAS 调用；不声明取得完整 RSMU 规格。 | [原文](https://github.com/torvalds/linux/commit/245219a66085332a30e4653db3542ea5654ff762) |
| [MG10：AMD ATL system.c：Fabric 身份字段与版本发现](../../SMN/sources/MG10-atl-system-identity.md) | 解释 socket/die/node/component ID 的代际解码和未知版本处理；适合控制寻址与错误地址定位的前置研究，不能用固定移位套所有芯片。 | 固定版本公开代码。已读 node ID 构造、DF2/3/3.5/4 mask/shift、版本发现及系统配置采集；这是 CPU DF/ATL 软件上下文，不是 GPU SMN 路由表。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/system.c) |
| [MG11：UMC 6.7：错误地址展开与 poison 模式的代际对照](MG11-umc67-ras-comparison.md) | 补充 RSMU 相邻的 UMC RAS 路径，解释 hash/列位模糊如何扩大隔离候选，及 poison 查询如何依赖寄存器；用于对照 UMC 8.10。 | 固定版本公开代码。已读地址转换、直接/固件错误地址路径及 poison 查询；这不是 RSMU 内部实现证据。 | [原文](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c) |

| [C01：MM_UTCL2 图示与验证环境：从翻译事务到可观测检查点](../../UTCL2/sources/C01-mm-utcl2-testbench.md) | 覆盖 MM_UTCL2 的 APT1/2/3、VML2/ATCL2、fault/retry、两类失效以及验证环境，适合建立请求生命周期和验证检查点；所有容量与字段均须保留该资料版本范围。 | 用户页图·参考设计。49 页的已提交页图均已取得文字阅读或图像核看记录；2026-09-25 补回并直接核看了此前未读取的第 1、4 页。主要技术范围为第 3–5、15–31、33–47、49 页；并非对所有 OCR 字符逐字校勘。图示版本与目标芯片对应关系仍需本地确认。 | 原图已移出仓库 |

## 使用与维护

先复用笔记中已核实的解释与定位；只看摘要或未取得全文的条目不能支持精确机制。更新来源时补原笔记，并同步本索引的导读、状态及受影响方案；不在上下文复制全文。
AMD 名称是归档基础，行业类比仅扩大资料范围。保留产品/代际、规范/论文/模型/代码/用户参考的区别；代码空函数、模拟器简化和资料中的疑似笔误必须一并带入后续引用。
用户参考页图不等于 AMD 官方材料或目标芯片已确认规格；外部 SDMA 和原始文件继续遵守项目边界。
