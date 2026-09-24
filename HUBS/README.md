# HUBS — MMHUB / CH

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

按用户给出的 HUBS（mmhub、CH）分组统一管理，不另建 MMHUB/CH 子模块目录；`sources/` 用于资料笔记。这是学习分组，不证明存在名为 HUBS 的 RTL 父实例 [U1]。

MMHUB：本地 shaobo TBE 摘要明确写回经过它 [L2]。CH：本地未决问题提及其 compression_mode 属性，但不足以定义全称和职责 [L3/Q06]；不自动等同于 GCHUB。

UTCL1/UTCL2 公共主题独立管理，各实例是否属于某 hub 需框图。公开资料显示 hub 连接会随代际变化 [P2]。学习客户端接入、翻译、访问属性、缓存/一致性、路由和错误处理。关联：[UTCL1](../UTCL1/README.md)、[UTCL2](../UTCL2/README.md)。

## 资料现状

历史转换记录对应的 Markdown 正文目前缺失，用户已选择只同步现有文件，不补回正文。页面预览和嵌入图像仍保留在 `assets/`；下表提供当前可读入口。原始 PPTX/PDF 仅保存在本地 `original_file/`，不得上传 GitHub。

| 来源 | 原 Markdown 文件与当前状态 | 页数 | 现有图像 |
| --- | --- | --- | --- |
| C05 | `MMHUB_introduction.md`（缺失） | 41 | [全部图像](assets/MMHUB_introduction/) · [第一页](assets/MMHUB_introduction/slide-001.png) |

页面图像已用于本次技术阅读，逐篇机制和阅读范围见 [sources/README.md](sources/README.md)。本次未访问原件、未恢复缺失转换正文；用户参考设计不等于 AMD 官方或目标芯片已确认实现，版本冲突及算例纠错保留在笔记中。

[项目上下文](../project-context.md) · [历史转换报告](../conversion-report.md) · [历史来源与哈希清单](../source-manifest.json)

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：MMHUB 客户端与内存服务的交接；CH 先核实职责，不推定串接或包含。下一项：第 1 轮：一个 MMHUB 访问的上下游及地址约定。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[P2](../GC/sources/P2-amdgpu-hardware.md) → [C03](../UTCL2/sources/C03-utcl2-topology.md) → [C05](sources/C05-mmhub-dagb-ea.md) → [VM2](sources/VM2-mmhub-v2.md) → [VM12](sources/VM12-gfxhub-v2.md)。覆盖：Hub 集成及翻译服务边界；数据/地址交接与共享资源；失效、故障和通知。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本批笔记与索引已建立，详细阅读与笔记完善仍有[待补项](../source-reading-audit.md)；不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
