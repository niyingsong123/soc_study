# PHY — 物理层

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

PHY 是一类物理接口模块的统称，可保留公共入口；不同接口实例可能分属不同子系统。

后续按资料区分 HBM PHY、PCIe PHY 和芯片互联 PHY 的实例、父级与版本，目前不预建子目录。

学习数字控制器/物理接口边界、时钟、训练/校准、lane、时序和错误检测。SerDes、均衡等只用于相应串行链路，不套用到所有 PHY。关联：[UMC](../UMC/README.md)、[PCIe](../PCIE/README.md)、[SWITCH](../SWITCH/README.md)。
