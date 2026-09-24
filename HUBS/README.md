# HUBS — MMHUB / CH

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

按用户给出的 HUBS（mmhub、CH）分组统一管理，不建立子目录。这是学习分组，不证明存在名为 HUBS 的 RTL 父实例 [U1]。

MMHUB：本地 shaobo TBE 摘要明确写回经过它 [L2]。CH：本地未决问题提及其 compression_mode 属性，但不足以定义全称和职责 [L3/Q06]；不自动等同于 GCHUB。

UTCL1/UTCL2 公共主题独立管理，各实例是否属于某 hub 需框图。公开资料显示 hub 连接会随代际变化 [P2]。学习客户端接入、翻译、访问属性、缓存/一致性、路由和错误处理。关联：[UTCL1](../UTCL1/README.md)、[UTCL2](../UTCL2/README.md)。

## 资料现状

历史转换记录对应的 Markdown 正文目前缺失，用户已选择只同步现有文件，不补回正文。页面预览和嵌入图像仍保留在 `assets/`；下表提供当前可读入口。原始 PPTX/PDF 仅保存在本地 `original_file/`，不得上传 GitHub。

| 来源 | 原 Markdown 文件与当前状态 | 页数 | 现有图像 |
| --- | --- | --- | --- |
| C05 | `MMHUB_introduction.md`（缺失） | 41 | [全部图像](assets/MMHUB_introduction/) · [第一页](assets/MMHUB_introduction/slide-001.png) |

页面图片保留原资料的视觉内容，本次上下文整理不新增目标芯片的架构结论。来源原名及证据边界见 [资料登记](../sources.md)。

[项目上下文](../project-context.md) · [历史转换报告](../conversion-report.md) · [历史来源与哈希清单](../source-manifest.json)

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 5 轮规划，详细论文轮次均待执行。

上下游场景：MMHUB 客户端与内存服务的交接；CH 先核实职责，不推定串接或包含。下一项：第 1 轮：一个 MMHUB 访问的上下游及地址约定。

## 资料集与接续

资料集入口：[本模块来源主条目](../sources.md#vm1)；[资料集总入口](../sources.md)。覆盖本方案使用的公开材料与既有来源；建议阅读顺序：P2/VM1 → VM2/VM3。内容简介、版本及已读范围集中维护在资料集中。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
