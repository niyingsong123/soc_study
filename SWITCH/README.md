# SWITCH — 芯片互联

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

对应用户提出的“芯片互联（switch）”。**学习范围现已明确为片内 NoC 与封装内 die-to-die；但目标芯片的实际 SWITCH 拓扑、协议和 RTL 归属仍未确认。** 不把公开参考设计直接当作 shaobo/anshi 或某代 AMD 的实现。

暂独立管理；是否属于 DF、如何连接 CAKE、使用哪类 PHY，仍需目标协议与拓扑资料确认。关联：[DF](../DF/README.md)、[PHY](../PHY/README.md)。

## 已有公开技术研究

用户指定的研究正文保存在小写 `switch/`；本大写目录继续作为 SoC 模块入口。当前不合并、移动或重命名两个目录。

- [完整微架构研究稿](../switch/switch_detailed_guide.md)：v2.3 在既有主线中深化 NI transaction contract、AW/W、有限并发和 response/retire，并联动架构、读写过程及证据边界；旧章节映射见附录 B。
- [六问简化版](../switch/switch_quick_guide.md)：为什么需要、功能、上下游/流向、关键参数、SDMA 关联及软硬件协同。
- [研究轮次与执行证据](../switch/RESEARCH_PROGRESS.md)：第 1–3 轮完成，第 4–6 轮待研究；第三轮的文档级推演与算术检查见[核查记录](round3-review.md)。
- [第二轮有限缓冲模型](../switch/examples/router_round2.py)与[实际测试报告](../switch/examples/round2_results.json)：教学模型，不是 RTL 或协议合规验证。

第一轮完整原稿以[历史快照](../switch/switch_detailed_guide_v2.0.md)保留。v2.2 将前两轮合并为 17 节及两份附录，v2.3 在同一结构中整合第三轮；历史稿不再作为另一套并行设计维护。

更新日期：2026-09-25。学习内容覆盖端口、路由、VC/VN、VA/SA、credit、buffer、失败路径、死锁依赖、ordering 与完成点；实际目标模块是否具备这些功能仍由目标资料决定。

## 当前规划与研究位置

[多轮研究方案 v2.1](research-plan.md) · [整体研究顺序](../research-roadmap.md)。2026-09-25 的 U32 重拟总计六轮，U35 已实施第三轮 NI transaction contract；实际第 1–3 轮完成。后续依次为第 4 轮片内 progress/恢复、第 5 轮 D2D、第 6 轮性能与模块收尾，均待执行。

上下游场景：从客户端/DF 事务需求研究 NI、Router、D2D 的输运责任，协议与目标拓扑待核实。v2.3 延续[详细文档写作方法](../chip-study-plan.md#详细文档写作方法)，第三轮已明确参考 NI 的 admission、outstanding、ordering、目标交接和 response/retire；常用英文术语按 U31 保留。第 4 轮应将这些有限资源与 Router、消费者组合分析，并深化 drain/reset，不能重新把 NI 普通过程当作待写基础。完整系统复审仍在跨模块阶段，本模块必需的接口不延后。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

当前第 4 轮优先阅读：[R13](sources/R13-channel-dependency-scope.md) → [R19](sources/R19-booksim-buffer-state.md) → [R22](sources/R22-garnet-network-interface.md)，以 v2.3 第 6 节为资源和接口起点，必要时回查 R8。第三轮的 R8/R7/R22 结论已保存；第 5 轮读 R10/R11/R16，第 6 轮复用 R3/R1/R7。各轮具体章节和条件性比较见[选读表](sources/README.md#按微架构问题选读)，无需从头重读全部来源。

后续 Codex 先读本模块上下文、详细稿第 3–6 节及 research-plan.md，建立上下游接口与完整事务图景，再按问题选择笔记；不要求先通读下列全部来源。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行资料审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。第三轮完成依据正文与明确的核查成果；资料数量未增加，既有 Router 模型未改动或重跑。方法见[当前研究范本](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[R1](sources/R1-pipelined-router-delay.md)、[R8](sources/R8-axi-ordering-contract.md)、[R13](sources/R13-channel-dependency-scope.md)、[R23](sources/R23-chi-ea-protocol.md)。模型公式/实验条件、burst 与错误收尾、CDG 前提、CHI 事务/两类 credit 和链路收敛已补。协议依赖与路由依赖分别分析；R9/R12 不再承担正式 CHI 规则来源。

## HBM 地址映射专题接续（U24）

[专题方案与逐层分工](../HBM/address-interleaving-plan.md) · [本模块具体落点](research-plan.md#u24请求地址到-hbm-bank-的跨模块落点)。将地址/目标 ID 进入 NI、下一跳路由、包拆分和返回重排分开；明确谁已经决定 HBM 归属，谁只负责输运。网络分包不自动等于内存子请求拆分，协议完成也不等于 DRAM 写完成。 先读取现有资料索引，聚焦 SWITCH 的接口与输运责任并保存依赖问题；必要接口疑点立即核实，相关模块基础具备后再统一全路径例子，实际连接与参数保留证据边界。
