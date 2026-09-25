# PHY — 物理层

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

PHY 是一类物理接口模块的统称，可保留公共入口；不同接口实例可能分属不同子系统。

后续按资料区分 HBM PHY、PCIe PHY 和芯片互联 PHY 的实例、父级与版本，目前不预建子目录。

学习数字控制器/物理接口边界、时钟、训练/校准、lane、时序和错误检测。SerDes、均衡等只用于相应串行链路，不套用到所有 PHY。关联：[UMC](../UMC/README.md)、[PCIe](../PCIE/README.md)、[SWITCH](../SWITCH/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：先接续 UMC 的内存 PHY，再按 PCIe/D2D 各自协议安排分支；实例不等同。下一项：第 1 轮：内存 PHY 两侧接口、时钟与训练所有权。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[MEM1](../UMC/sources/MEM1-pg276-hbm-controller.md) → [MEM4](sources/MEM4-dfi-version-boundary.md) → [MEM5](sources/MEM5-ug586-phy.md) → [MEM15](sources/MEM15-pg150-dqs-gate.md)。覆盖：内存接口、时钟与校准；串行采样和协议训练；D2D 与性能裕量。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[MEM16](sources/MEM16-dfi51-interface.md)、[MEM15](sources/MEM15-pg150-dqs-gate.md)。DFI 5.1 转录补启动与数据有效期；2022 PG150 原图补完整阶段、rank 分支和灰色未实现项。2025 图与 DFI 6.0 HBM profile 仍待原版，不合并年代；器件精确时序按 U23 仅在需要时查阅。

## 当前研究重点（U23，2026-09-25）

HBM 主线重点解释命令/写数据对齐、读采样与有效期、初始化/训练就绪、停流与恢复。电气机制保留必要解释，料号级 AC/DC 数值与封装预算按需展开。 统一范围与运用标准见 [项目上下文](../project-context.md#hbm-接口研究范围)。缺少厂商器件数据表不阻塞主线；实际未读状态仍保留。

## HBM 地址映射专题接续（U24）

[专题方案与逐层分工](../HBM/address-interleaving-plan.md) · [本模块具体落点](research-plan.md#u24请求地址到-hbm-bank-的跨模块落点)。将 UMC 的逻辑目标、命令地址及数据映射到实际 PHY/channel/PC 接口，核对对齐、读有效及返回关联；区分逻辑地址映射、物理 lane 对应和时序适配，不预设 PHY 重新选择 HBM stack 或重做系统 hash。 先读取现有资料索引，专题例子跨模块共用，实际连接与参数保留证据边界。
