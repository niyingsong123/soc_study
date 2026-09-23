# SMU — System Management Unit

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

公开 AMDGPU 资料将其描述为系统功耗管理控制器，涉及时钟、电压、温度和复位等管理 [P2]。目标芯片具体职责及固件接口待资料。

管理其他模块不等于包含它们；SMN 网络与 RSMU 的层级分别待确认，当前不纳入 SMU 子目录。

学习软件请求、硬件状态反馈、频率/电压协调、idle、时钟门控与复位。关联：[SMN](../SMN/README.md)、[RSMU](../RSMU/README.md)。
