# UTCL1 — 一级地址翻译缓存

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

公共模块独立学习，同时记录各实例的实际归属，这是用户明确要求的管理方式 [U3]。公开 AMD 术语为 Unified Translation Cache - Level 1 [P5]。

本地资料确认：shaobo SDMA → TBE → dma_utcl1；dma_utcl1 与 copy engine 同级，未命中时向 UTCL2 请求 [L2「地址翻译与限制」，回指外部 S1]。其他客户端的实例与数量待确认。L1/L2 是翻译层级，不代表 UTCL1 被 UTCL2 包含。

学习 VA/PA、命中/miss、VMID、权限、异常及 invalidation。具体 TBE 实现继续查 [SDMA 外部入口](../SDMA/README.md)；此处维护公共概念与实例索引。关联：[UTCL2](../UTCL2/README.md)。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 4 轮规划，详细论文轮次均待执行。

上下游场景：客户端翻译请求到 UTCL2 服务；翻译返回与业务数据返回分开。下一项：第 1 轮：客户端身份、地址及命中/未命中接口。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[VM1](../UTCL2/sources/VM1-gpuvm-address-spaces.md) → [C01](../UTCL2/sources/C01-mm-utcl2-testbench.md) → [C03](../UTCL2/sources/C03-utcl2-topology.md) → [VM7](sources/VM7-gem5-vega-tlb.md)。覆盖：客户端身份、命中与 miss；合并、等待与资源释放；失效与地址空间复用。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本批笔记与索引已建立，详细阅读与笔记完善仍有[待补项](../source-reading-audit.md)；不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
