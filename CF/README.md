# CF — Command Fabric

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

全称来自 shaobo SDMA 资料 [L1]。BE 经 CF 接收命令并返回 EOC、异常、cancel、credit 等信息 [L2]。

CF 与 DF 分开管理；CF、SMN、anshi 的 CANE 不自动等同。不同代际须重新核对命名与拓扑。

学习命令路由、端点标识、包格式、背压、返回语义；区分 credit、后端任务完成、原始命令完成。尚无独立 CF 规格。

## 当前规划与研究位置

[多轮研究方案](research-plan.md) · [整体研究顺序](../research-roadmap.md)。已形成 3 轮规划，详细论文轮次均待执行。

上下游场景：命令发起、后端接纳与控制返回；CF 与 DF 数据侧依赖不表示同一网络。下一项：第 1 轮：消息角色与正常任务闭环。

## 资料集与接续

资料入口：[本模块逐篇索引](sources/README.md)；[全局编号与阅读状态](../sources.md)。每篇索引说明讲什么、何时值得读，链接详细技术笔记和原文；跨模块来源只有一份主笔记。

优先阅读：[L1](../SDMA/sources/L1-external-glossary-scope.md) → [L2](../SDMA/sources/L2-external-shaobo-scope.md) → [IO10](sources/IO10-gfx90-register-control.md) → [MG4](../SMN/sources/MG4-smn-indirect-access.md)。覆盖：命令身份与端点访问；接纳、排序和完成；共享状态与异常退出。

后续 Codex 先读本模块上下文和 research-plan.md 的整体架构，再按问题选择笔记。笔记保留版本、机制、重要细节、实际阅读范围及证据边界；精确字段、新版本或未读部分再回原资料。补充资料时同步索引、主笔记与受影响方案，不在上下文复制整份资料集。

本批笔记与索引已建立，详细阅读与笔记完善仍有[待补项](../source-reading-audit.md)；不能以文件数视为深度验收。资料整理不计为新的论文轮次，论文接续在用户明确要求后按上文执行。方法见[研究范本 v1.3](../chip-study-plan.md)。
