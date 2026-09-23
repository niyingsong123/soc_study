# PCIe — PCI Express

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

主机/设备互联学习入口。当前没有本项目协议版本、端口角色或控制器规格。

协议分层与 RTL 分块分别描述；PHY 可作为物理层实例，NBIF/HDP 是否包含在某个 PCIe 子系统中则需框图。

学习配置空间与 BAR、事务请求/completion、posted/non-posted、流控/保序、MSI/MSI-X，再结合 SDMA 理解主机与设备访问。关联：[NBIF](../NBIF/README.md)、[HDP](../HDP/README.md)、[PHY](../PHY/README.md)。
