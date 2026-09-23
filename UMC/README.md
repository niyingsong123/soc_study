# UMC — 内存控制器

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

公开 AMD 资料使用 Unified Memory Controller [P1]。研究上游内存请求如何转化为存储器侧操作；目标设计的命名与边界待确认。

UMC 与 HBM 是控制器和存储器的关系，HBM 不归为 UMC 内部逻辑；PHY 在内存子系统中的父级需要集成图。

学习地址到通道/bank 的映射、调度、读写切换、刷新、时序与 ECC/RAS。具体支持项、位宽、频率和数量待资料。关联：[HBM](../HBM/README.md)、[PHY](../PHY/README.md)。
