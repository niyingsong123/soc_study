# 资料任务检查与补齐记录

更新日期：2026-09-25。按用户“按检查报告补齐”的要求执行；基线为 [1f09693](https://github.com/niyingsong123/soc_study/commit/1f096936670b0f3ade91493265939c87985aa469)，[2026-09-24 历史检查原文](https://github.com/niyingsong123/soc_study/blob/1f096936670b0f3ade91493265939c87985aa469/source-reading-audit.md)保留在 Git 历史中。

## 用户后续调整的验收范围（U23）

用户于 2026-09-25 明确：HBM 器件数据表不是重点，目标是理解并运用典型接口行为，尤其 PHY、CS、UMC 的职责与协作。因此 MEM9/MEM10 所缺厂商 datasheet 改为按需参考，不再计入当前必补任务；保留实际未取得的记录。规范选读仍按接口研究问题推进，详见 [当前范围](project-context.md#hbm-接口研究范围)。下表中的历史访问事实不因范围调整而变成已读。

## 当前结论

**已补齐本次能够直接读取的主要机制、公式/实验、缺页与 CHI 正式协议资料，并同步笔记、索引、上下文和受影响方案；整体资料任务仍有明确的访问及原版核验缺口，不能称为全部精读完成。**

原来 101 篇笔记，本次更新 19 篇既有笔记，新增 R23（正式 CHI E.a）和 MEM16（DFI 5.1 转录选读），共 **103 篇主笔记、19 个模块逐篇索引**。新增条目不是重复复制；同一来源仍只维护一份主笔记，其他模块链接复用。

按实际阅读记录，99 篇有正文/相关章节/函数/页图或官方介绍阅读记录；其中 MEM11/MEM16 仅规范转录的局部正文选读，原版图表未核。IO4、L1–L3 共 4 篇没有本次可读正文。**99/103 不是完成率**：正文选读、产品介绍和整本原文的深度不可相加当成统一精读。

## 对上一份检查报告逐项处理的结果

| 检查项 | 本次实际补充 | 当前状态与接续 |
| --- | --- | --- |
| [R1：Router 延迟模型](SWITCH/sources/R1-pipelined-router-delay.md) | 流水级合法切分条件、逻辑努力/FO4、参数表对照、公式算例；mesh、流量、预热/采样、延迟口径和 buffer/VC 比较 | 报告指出的定量与设定缺口已补。未重跑仿真，原结果不外推到 AMD |
| [VM5：MASK](UTCL2/sources/VM5-mask-paper.md) | token/epoch/阈值、旁路 cache、DRAM 预算式/队列、Table 1、工作负载筛选、基线、指标和主要结果 | 报告指出的机制/实验缺口已补。记录原表 warp 配置疑点；吞吐与公平性分别核对指标，均以所述 SharedTLB 主基线引用 |
| [R8：AXI](SWITCH/sources/R8-axi-ordering-contract.md) | burst 长度/4 KB/非对齐地址/WRAP、禁止提前结束、读写错误收尾；exclusive 的 ID/对齐/容量限制及不支持 slave 仍执行写的例外 | 与当前 NI/bridge 相关的缺口已补。无关 ACE/AXI5 扩展不机械扩写 |
| [VM10：IOMMU](UTCL2/sources/VM10-iommu-spec.md) | guest/nested 控制、GCR3/PASID、嵌套 walk、PPR log/组身份、COMPLETE_PPR_REQUEST、溢出保护及模式组合限制 | 所列虚拟化/PRI 主线已补，仍为明确章节选读，不声称 303 页逐字段精读 |
| [R13：Dally/Seitz](SWITCH/sources/R13-channel-dependency-scope.md) | 取得 17 页扫描正文并 OCR；核原图定义、定理、证明及 VC 构造；保存七项前提、两个证明方向、ring/torus 和其他拓扑思路 | 原“仅摘要”缺口已关闭。纠正旧流程将无文字层误判为 PDF 未取得；未宣称目标 SoC 已获无死锁证明 |
| [C01：缺第 1、4 页](UTCL2/sources/C01-mm-utcl2-testbench.md) | 从已提交资源读回两页并直接核图；第 4 页 BOWEN 双 MMHUB、lane/client 扩张、UTCL1 sideband、SMN→rsmu 位置 | 缺页已关闭。删除线建议不当定案，HYGON 参考设计与 AMD 目标继续分开 |
| [MEM15：训练总阶段](PHY/sources/MEM15-pg150-dqs-gate.md) | 官方 2022-04-20 PG150 p.593 Figure 38-5；阶段先后、rank 分支、sanity checks、灰色未实现项和最终 VT tracking | 历史总图与依赖已补；2025-12-03 网页总图仍未取得，不能宣称两版完全一致 |
| [R9](SWITCH/sources/R9-chi-model-user-guide.md)/[R12](SWITCH/sources/R12-arm-system-architecture.md)：缺正式 CHI | 新增 [R23](SWITCH/sources/R23-chi-ea-protocol.md)，从 Arm 官方完整 E.a PDF 选读事务/ID/完成/重试/一致性状态/链路 credit 与停启 | 正式协议来源缺口已关闭到所列范围；R9/R12 保持模型/介绍身份，不伪装成规范 |
| [MEM4：DFI](PHY/sources/MEM4-dfi-version-boundary.md) | 核实官方下载到登录页；新增 [MEM16](PHY/sources/MEM16-dfi51-interface.md) 的 5.1 原文转录选读，整理 boot、写对齐、读有效期、控制权交接 | 局部推进；5.1 原版波形及 6.0 HBM profile 未取得，不能把旧版接口当 HBM 新规范 |
| [MEM11：JESD238](HBM/sources/MEM11-jedec-scope-gap.md) | 找到 JESD238A 2023-01 原文转录，补 PC 共享/独立资源、行列命令接口、group timing 与 CK/DQS 边界 | 从纯入口推进到局部正文选读；完整原版图表/命令/维护/ECC 仍须补核，不再标为“完全没读正文”，也不标为全部完成 |
| [MEM9](HBM/sources/MEM9-micron-hbm3e.md)/[MEM10](HBM/sources/MEM10-samsung-hbm3.md)：datasheet | 检查 Micron catalog/文档入口；Samsung 官方说明 datasheet 按请求提供；保存实际访问结果与需要匹配的料号/版本 | 器件数据表仍未取得；按 U23 已转为可选参考，不计当前必补项。产品页总结不扩成命令、时序或 ODECC 规格 |
| [IO4：PCIe Base 5.0](PCIE/sources/IO4-base-spec-gap.md) | 沿官方入口核实下载文档 13005 跳到 PCI-SIG 会员登录 | 未关闭：当前无合法会话可读正文；无需重做已读 PG213/Linux/IOMMU 周边资料 |
| [MG5：RSMU](RSMU/sources/MG5-rsmu-umc-index.md) | AMD 作者原始提交确认 remote SMU 名称及寄存器接口/错误/复位职责；保留字段编码、UMC mode 操作与 C01 参考位置 | 名称/公开职责证据已补；目标内部结构、实例和 SMU 层级仍未知，研究首轮已改为目标映射 |
| [CF / IO10](CF/sources/IO10-gfx90-register-control.md) | 下钻 WAIT_REG_MEM helper 和 KIQ 失败清理；定向检索 Command Fabric/CF_IF 后仍未得到目标拓扑证据 | 可读机制已加深；目标 CF 直接资料缺口未关闭，不用 GRBM/SMN/KIQ 替代 |
| [L1](SDMA/sources/L1-external-glossary-scope.md)、[L2](SDMA/sources/L2-external-shaobo-scope.md)、[L3](SDMA/sources/L3-external-open-questions.md) | 确认外部 Windows 项目未挂载；三篇各补本地只读接续和回写范围 | 三项均未重读。保留外部项目只读、原件不上云，不编造 shaobo/anshi 细节 |
| 索引、上下文、方案 | 19 个逐篇索引按主笔记同步导读/范围，19 个 README 更新入口提醒；14 个受影响方案补具体落点，RSMU 名称旧判断已修正；范本升级 v1.4 | 组织与交接已完成；新证据不会增加任何论文完成轮次 |

## 剩余项：具备条件后从哪里继续

| 条件/资料 | 下一步要补的实际内容 | 更新位置 |
| --- | --- | --- |
| 可访问 PCI-SIG Base 5.0 原文 | 与目标研究有关的 TLP 顺序/credit/completion、Data Link retry、恢复；固定修订号 | IO4，然后更新 PCIe/SWITCH 相关方案 |
| 可访问官方 DFI 原版，尤其目标 HBM profile | 5.1 选读的波形/比例映射核验；6.0 HBM 的接口与状态规则另按版本整理 | MEM16、MEM4；PHY/UMC |
| 与典型行为有关的 JESD238A 或目标接口规范章节 | 按问题核对命令约束、刷新/训练与外部错误行为；先用符号和明确代际的公开例子建立模型，精确 checker 所需原版图表另行核验 | MEM11、MEM16；HBM/UMC/PHY |
| 可选：具体 HBM 料号 datasheet | 仅在确需器件数值、电气或专属机制时查阅；当前不追索，不阻塞主线。未来使用时再核料号、speed bin 与修订 | MEM9/MEM10；保留背景笔记 |
| PG150 2025 图像可读 | 与已核 2022 Fig.38-5 比较阶段/灰色项/分支；无需重写 gate 搜索说明 | MEM15 |
| 本地可访问独立 SDMA 项目 | 只读 glossary、shaobo、open-questions，核对原定义、读写/CF_IF/DF_IF 与最新未决项，只回写 SoC 接口结论 | L1–L3；需要时修正 CF/UTCL1/UTCL2/HUBS |
| 目标芯片顶层、IP 版本及接口资料 | CF 真实结构；RSMU 公开证据的目标映射；其他同名模块的实例归属 | 对应模块现有笔记/方案，不另起重复台账 |

上述必要规范/目标证据的限制不阻塞使用已有公开参考规划，但限制相应的目标实现或规范图表结论；可选器件资料已按 U23 从当前必补范围移出。本次没有自动联系厂商、注册账号、修改外部项目或上传原始资料；也不把访问失败泛化为该资料永远不可得。

## 复核范围和验证记录

技术复核集中在检查报告列明的缺项：本次回读了新增公式/参数/结果的原文，直接核看关键页图，对 CHI、AXI、IOMMU 和代码只标实际所读章节/函数。R2/R7、R9/R12、MEM12 等已有相关范围说明继续保留，不因文件短就判不合格，也不因已有文件就宣称全原文已验收。

2026-09-25 补齐提交 7fd0d17 的检查记录（不是后续范围调整的变更计数）：103 篇主笔记的编号唯一、导读和来源/阅读状态齐全，19 个模块的逐篇索引与主笔记一致，资料入口和方案入口存在；2,613 个仓库内相对路径引用均能定位到文件。工作基线的 168 个 Markdown 文件已逐一核对 GitHub blob 哈希。本次共变更 82 个 Markdown 文件，其中新增 2 篇主笔记，没有上传原始资料或缓存文件。

验证边界：6 个指向外部本地项目的链接保留为待本地核验；本次未全量验证标题锚点或外部网址实时可达性，也未对其余原有笔记重新逐段核对全部外部原文。上述检查证明索引与文件结构一致，不能替代每份资料的技术正确性验收。

SWITCH 仍仅第 1–2 轮完成，第 3–6 轮、其他模块正式论文与完整跨模块专题不属于本次补齐交付。小写 switch/RESEARCH_PROGRESS.md 仅更新资料接续提示，原模型、测试结果和论文轮次均保持原进度；本次没有新增硬件/仿真实验。

## U24 对下一步研究的要求

HBM 数据表转为可选不等于 bank 划分和 interleave 可省略。用户已确定 [从请求地址到 HBM bank](HBM/address-interleaving-plan.md) 为核心专题，需沿实际数据通路查明各层地址、目标选择、拆分与返回关联。本次新增的是研究方案和模块接续提醒，逐地址推导、目标位图与模型验证尚未完成，不计作资料精读或论文完成。
