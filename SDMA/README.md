# SDMA — 独立项目只读入口

[项目入口](../README.md) · [模块关系](../module-map.md) · [资料集与来源](../sources.md)

**详细研究在 `D:\project\no_preject\sdma_repo` 管理，本项目只读参考，不修改其任何内容。** 此目录只维护入口及系统关系，不复制原始资料，不建立 FE、BE、TBE 子目录。

FE（Front End）、BE（Back End）、TBE（Tile Back End）属于 SDMA 研究范围 [L1、L2]。shaobo BE 路径由 FE 拆分并翻译；TBE 可接收原始任务自行拆分/翻译，内部 dma_utcl1 与 copy engine 同级。L1 miss 请求 UTCL2，写回涉及 MMHUB [L2]。

公共 UTCL1 独立建目录 [U3]，实例归属仍为 TBE。CF 命令接口与 DF 数据接口分开理解。anshi TBE 剩余职责未确定，不以 N/A 推断已删除 [L3/Q01]。后续这里只补充有资料依据的跨模块联系，内部实现继续在外部项目维护。

## 外部入口

独立 `sdma_repo` 已取消与 SOC 项目的附加关联。以下链接仅在本地对应目录存在时可用；本 GitHub 仓库不包含这些外部文件，详细研究仍在独立项目维护。

- [项目首页](../../sdma_repo/README.md)
- [项目上下文](../../sdma_repo/docs/project-context.md)
- [shaobo 架构](../../sdma_repo/docs/context/shaobo.md)
- [anshi 架构](../../sdma_repo/docs/context/anshi.md)
- [资料目录](../../sdma_repo/docs/sources.md)
- [未决问题](../../sdma_repo/docs/context/open-questions.md)

## 资料集与接续

资料集入口：[资料集与来源总入口](../sources.md)。用于本仓库的 SDMA 系统联系与只读来源，详细研究仍在外部项目。

后续 Codex 先读本入口及已有方案/整体架构，再浏览相关资料简介，按需阅读原文。这里保留位置与阅读顺序，简介在资料集中维护；若后续建立或移动模块资料集，同步更新本节和总索引。具体方法见 [研究范本](../chip-study-plan.md)。
