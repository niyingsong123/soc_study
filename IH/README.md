# IH — Interrupt Handler

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

公开 AMDGPU 资料将 IH 描述为汇聚各 IP 中断并写入 ring buffer 的模块 [P2]。目标芯片格式与传递方式仍待规格。

各模块向 IH 上报事件是接口关系，不表示被 IH 包含。

学习事件来源、队列写入、软件通知、溢出/丢失处理，以及完成和异常事件的区别。待补充事件格式与驱动流程。关联：[SDMA](../SDMA/README.md)。
