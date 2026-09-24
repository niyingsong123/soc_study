# UTCL1 — 一级地址翻译缓存

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

公共模块独立学习，同时记录各实例的实际归属，这是用户明确要求的管理方式 [U3]。公开 AMD 术语为 Unified Translation Cache - Level 1 [P5]。

本地资料确认：shaobo SDMA → TBE → dma_utcl1；dma_utcl1 与 copy engine 同级，未命中时向 UTCL2 请求 [L2「地址翻译与限制」，回指外部 S1]。其他客户端的实例与数量待确认。L1/L2 是翻译层级，不代表 UTCL1 被 UTCL2 包含。

学习 VA/PA、命中/miss、VMID、权限、异常及 invalidation。具体 TBE 实现继续查 [SDMA 外部入口](../SDMA/README.md)；此处维护公共概念与实例索引。关联：[UTCL2](../UTCL2/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：客户端翻译请求到 UTCL2 服务；翻译返回与业务数据返回分开。下一项：第 1 轮：客户端身份、地址及命中/未命中接口。

## 资料集与接续

资料集入口：[本模块来源主条目](../sources.md#vm1)；[资料集总入口](../sources.md)。覆盖本方案使用的公开材料与既有来源；建议阅读顺序：VM1/VM5 → VM2/VM3。内容简介、版本及已读范围集中维护在资料集中。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
