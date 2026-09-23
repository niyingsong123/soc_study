# UTCL1 — 一级地址翻译缓存

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

公共模块独立学习，同时记录各实例的实际归属，这是用户明确要求的管理方式 [U3]。公开 AMD 术语为 Unified Translation Cache - Level 1 [P5]。

本地资料确认：shaobo SDMA → TBE → dma_utcl1；dma_utcl1 与 copy engine 同级，未命中时向 UTCL2 请求 [L2「地址翻译与限制」，回指外部 S1]。其他客户端的实例与数量待确认。L1/L2 是翻译层级，不代表 UTCL1 被 UTCL2 包含。

学习 VA/PA、命中/miss、VMID、权限、异常及 invalidation。具体 TBE 实现继续查 [SDMA 外部入口](../SDMA/README.md)；此处维护公共概念与实例索引。关联：[UTCL2](../UTCL2/README.md)。
