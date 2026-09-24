# PCIe — PCI Express

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

主机/设备互联学习入口。当前没有本项目协议版本、端口角色或控制器规格。

协议分层与 RTL 分块分别描述；PHY 可作为物理层实例，NBIF/HDP 是否包含在某个 PCIe 子系统中则需框图。

学习配置空间与 BAR、事务请求/completion、posted/non-posted、流控/保序、MSI/MSI-X，再结合 SDMA 理解主机与设备访问。关联：[NBIF](../NBIF/README.md)、[HDP](../HDP/README.md)、[PHY](../PHY/README.md)。

## 资料集与接续

资料集入口：[资料集与来源总入口](../sources.md)。按本模块主题查看来源简介、相关研究问题和实际阅读定位；条目随后续阅读补充。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
