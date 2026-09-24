# DF — Data Fabric

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

本地 SDMA 资料区分 CF 命令接口与 DF 数据路径 [L1、L2]。本目录研究数据请求的路由、流控与返回。

CS、CAKE 暂合并在本目录，不另建子目录：CS 暂按 Coherent Slave 理解；CAKE 在 AMD 公开资料中为 Coherent AMD socKet Extender。两者属于公开 DF 相关架构的参考主题 [P1]，目标芯片的直接父级尚待确认。注意 P5 中 CS 指 Compute Shader，不能跨语境混用。

学习请求/响应、地址路由、仲裁、credit、保序、一致性与跨 die 访问。待补充 DF/CS/CAKE 框图、协议和地址映射；SWITCH、UMC、PHY 不据连线归为 DF 子模块。

## 资料集与接续

资料集入口：[资料集与来源总入口](../sources.md)。按本模块主题查看来源简介、相关研究问题和实际阅读定位；条目随后续阅读补充。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
