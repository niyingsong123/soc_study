# DF — Data Fabric

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

本地 SDMA 资料区分 CF 命令接口与 DF 数据路径 [L1、L2]。本目录研究数据请求的路由、流控与返回。

CS、CAKE 暂合并在本目录，不另建子目录：CS 暂按 Coherent Slave 理解；CAKE 在 AMD 公开资料中为 Coherent AMD socKet Extender。两者属于公开 DF 相关架构的参考主题 [P1]，目标芯片的直接父级尚待确认。注意 P5 中 CS 指 Compute Shader，不能跨语境混用。

学习请求/响应、地址路由、仲裁、credit、保序、一致性与跨 die 访问。待补充 DF/CS/CAKE 框图、协议和地址映射；SWITCH、UMC、PHY 不据连线归为 DF 子模块。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：从客户端数据事务理解目标选择、本地/远端及内存侧责任；CS/CAKE 核对代际。下一项：第 1 轮：入口地址和本地读写闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[P1](sources/P1-ryzen-fabric-topology.md) → [FAB1](sources/FAB1-cdna3-iod-memory.md) → [FAB2](sources/FAB2-df36-registers-counters.md) → [MG10](../SMN/sources/MG10-atl-system-identity.md)。覆盖：本地/远端目标与身份；地址归属、hash 与 XGMI；事务完成、流控和恢复。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[R23](../SWITCH/sources/R23-chi-ea-protocol.md)、[R13](../SWITCH/sources/R13-channel-dependency-scope.md)。正式 CHI 选读提供事务身份、观察顺序、重试资源和链路 credit 的行业参照；将 home/coherence 责任与输运分开，不将其直接映射为 AMD DF。

## 当前研究重点（U23，2026-09-25）

CS 仍在本目录研究。重点解释内存目标选择、适用的一致性/顺序、返回关联与完成责任，并与 UMC 的请求/响应约定接上；不把 CS 预设为 DRAM 命令调度器。 统一范围与运用标准见 [项目上下文](../project-context.md#hbm-接口研究范围)。缺少厂商器件数据表不阻塞主线；实际未读状态仍保留。
