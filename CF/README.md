# CF — Command Fabric

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

全称来自 shaobo SDMA 资料 [L1]。BE 经 CF 接收命令并返回 EOC、异常、cancel、credit 等信息 [L2]。

CF 与 DF 分开管理；CF、SMN、anshi 的 CANE 不自动等同。不同代际须重新核对命名与拓扑。

学习命令路由、端点标识、包格式、背压、返回语义；区分 credit、后端任务完成、原始命令完成。尚无独立 CF 规格。
