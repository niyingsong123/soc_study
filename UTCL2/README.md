# UTCL2 — 二级地址翻译缓存

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

公开术语为 Unified Translation Cache - Level 2 [P5]。本地资料确认 shaobo TBE 的 UTCL1 miss 会请求 UTCL2 [L2]。

作为公共翻译主题独立管理。本项目 UTCL2 的 hub 归属尚待框图确认；不包含所有 UTCL1，也不同于 GL2 数据缓存。

学习客户端共享、翻译 miss、权限/异常和 invalidation。谁负责页表遍历、遍历单元是否在 UTCL2 内，均需目标设计资料。关联：[UTCL1](../UTCL1/README.md)、[HUBS](../HUBS/README.md)。

## 资料现状

历史转换记录对应的 Markdown 正文仍缺失，不自行补回。2026-09-25 按用户要求将本模块 `assets/` 的页面预览和嵌入图像移出版本管理，并要求清理其 Git 历史；该目录已加入 Git 忽略，后续不得重新上传。下表记录历史页数与当前可用性。原始 PPTX/PDF 仅限本地 `original_file/`，不得上传 GitHub。

| 来源 | 原 Markdown 文件与当前状态 | 页数 | 图像状态 |
| --- | --- | --- | --- |
| C01 | `tb_mm_utcl2.md`（缺失） | 49 | 原图已移出仓库 |
| C02 | `UTCL2 结构和使用简介 by Wang Junmin.md`（缺失） | 38 | 原图已移出仓库 |
| C03 | `utcl2_top.md`（缺失） | 1 | 原图已移出仓库 |
| C04 | `UTCL2地址翻译及预取技术介绍.md`（缺失） | 26 | 原图已移出仓库 |

页面图像曾用于此前技术阅读，当前不再由仓库提供；逐篇机制和阅读范围见 [sources/README.md](sources/README.md)。本次未访问原件、未恢复缺失转换正文；用户参考设计不等于 AMD 官方或目标芯片已确认实现，版本冲突及算例纠错保留在笔记中。

[项目上下文](../project-context.md) · [历史转换报告](../conversion-report.md) · [历史来源与哈希清单](../source-manifest.json)

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 6 轮规划，详细论文轮次均待执行。

上下游场景：承接 UTCL1/客户端的共享翻译服务，页表服务与系统 IOMMU 分支分别核实。下一项：第 1 轮：GPUVM 地址空间及服务边界。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[C03](sources/C03-utcl2-topology.md) → [C02](sources/C02-utcl2-cache-organization.md) → [C01](sources/C01-mm-utcl2-testbench.md) → [VM1](sources/VM1-gpuvm-address-spaces.md) → [VM8](sources/VM8-gem5-page-walker.md)。覆盖：整体结构、页表层级与回填；并发、fault、失效和外部翻译；预取、观测与纠错。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

资料笔记与索引已建立；2026-09-25 已执行一轮审计补齐，先查[逐项结果与剩余受限项](../source-reading-audit.md)，再读本模块索引。不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.4](../chip-study-plan.md)。

本次补读入口（2026-09-25）：[C01](sources/C01-mm-utcl2-testbench.md)、[VM5](sources/VM5-mask-paper.md)、[VM10](sources/VM10-iommu-spec.md)。C01 第 4 页补出 lane/client 扩张及内部 UTCL1 sideband；MASK 补定量控制与基线；IOMMU 补 nested walk、PPR 身份/队列/完成。按结构定位资源，保留 C01/C05 版本差异。

## HBM 地址映射专题接续（U24）

[专题方案与逐层分工](../HBM/address-interleaving-plan.md) · [本模块具体落点](research-plan.md#u24请求地址到-hbm-bank-的跨模块落点)。给出本次访问的翻译链、输出地址空间和属性，界定 GPUVM/IOMMU 分支；向后续 interleave 研究交接明确的地址语义。翻译服务与业务数据路径分别画图。 先读取现有资料索引，专题例子跨模块共用，实际连接与参数保留证据边界。
