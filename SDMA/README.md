# SDMA — 独立项目只读入口

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

**详细研究在 `D:\project\no_preject\sdma_repo` 管理，本项目只读参考，不修改其任何内容。** 此目录只维护入口及系统关系，不复制原始资料，不建立 FE、BE、TBE 子目录。

FE（Front End）、BE（Back End）、TBE（Tile Back End）属于 SDMA 研究范围 [L1、L2]。shaobo BE 路径由 FE 拆分并翻译；TBE 可接收原始任务自行拆分/翻译，内部 dma_utcl1 与 copy engine 同级。L1 miss 请求 UTCL2，写回涉及 MMHUB [L2]。

公共 UTCL1 独立建目录 [U3]，实例归属仍为 TBE。CF 命令接口与 DF 数据接口分开理解。anshi TBE 剩余职责未确定，不以 N/A 推断已删除 [L3/Q01]。后续这里只补充有资料依据的跨模块联系，内部实现继续在外部项目维护。

## 外部入口

独立 `sdma_repo` 已取消与 SOC 项目的附加关联。以下链接仅在本地对应目录存在时可用；本 GitHub 仓库不包含这些外部文件，详细研究仍在独立项目维护。

- [项目首页](../../sdma_repo/README.md)
- [项目上下文](../../sdma_repo/docs/project-context.md)
- [shaobo 架构](../../sdma_repo/docs/context/shaobo.md)
- [anshi 架构](../../sdma_repo/docs/context/anshi.md)
- [资料目录](../../sdma_repo/docs/sources.md)
- [未决问题](../../sdma_repo/docs/context/open-questions.md)

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。本次形成三轮系统接口接续方案；接口整理待执行，外部详细研究的实际进度由独立项目记录。

上下游场景：只作为源端与 SoC 接口上下文；内部 FE/BE/TBE 研究仍在独立项目。下一项：第 1 轮系统接口整理：浏览既有摘要、明确请求与完成约定。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[L1](sources/L1-external-glossary-scope.md) → [L2](sources/L2-external-shaobo-scope.md) → [L3](sources/L3-external-open-questions.md) → [P2](../GC/sources/P2-amdgpu-hardware.md)。覆盖：目标接口与外部范围；系统提交、寻址与维护；完成、事件和恢复。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[L1](sources/L1-external-glossary-scope.md)、[L2](sources/L2-external-shaobo-scope.md)、[L3](sources/L3-external-open-questions.md)。三项外部资料本次未挂载，已记录本地只读接续方式与回写范围。公开 SD1/SD2 及 C01 新页只作对照，不能替代目标原文。

## HBM 地址映射专题接续（U24）

[专题方案与逐层分工](../HBM/address-interleaving-plan.md) · [本模块具体落点](research-plan.md#u24请求地址到-hbm-bank-的跨模块落点)。记录搬运命令与源/目的访问的粒度、地址类型、子请求范围和返回/完成关联；将跨页与跨 interleave 边界分开核对。内部拆分实现只在外部项目只读研究，本仓库仅回写系统接口结论。 先读取现有资料索引，专题例子跨模块共用，实际连接与参数保留证据边界。
