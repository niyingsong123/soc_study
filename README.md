# SoC 模块学习项目

本项目从模块职责、接口和协作路径入手，逐步建立对整个 SoC 的理解。当前按用户列出的模块初始化；原写法已统一更正为 **GRBM**。

## 阅读入口

- [芯片学习与微架构研究计划](chip-study-plan.md)：用户确认的长期维护范本，包含六步流程、按上下游推进的研究顺序、模块方案结构、资料集与引用、完成条件和更新方式。
- [项目上下文](project-context.md)：当前 AMD 项目范围、研究顺序、SWITCH 进度、资料现状与后续问题。
- [模块关系与完整映射](module-map.md)：包含关系、接口关系、归档位置及待确认项。
- [资料集与来源](sources.md)：本地 SDMA 只读参考与公开架构资料的总入口；现有 101 篇来源笔记与 19 个模块索引，每篇附内容导读、细节、版本和实际阅读范围。
- [SDMA 外部项目入口](SDMA/README.md)：FE、BE、TBE 的详细研究继续在独立项目维护。

## 当前研究规划

已完成各模块的多轮规划及资料索引，逐篇笔记为阶段性成果：[研究路线图和全部方案](research-roadmap.md)。18 个模块按 3–6 轮安排，SDMA 另有仅限系统接口的接续方案；详细论文由后续本地 Codex 逐轮补充。SWITCH 实际仍为前两轮完成，后四轮方案已复核。本批资料扩充与方案修订已保存，但详细阅读与笔记完善尚未全部完成；6 篇缺原文正文总结，其他笔记也有局部阅读/深度缺口。接续先查[资料任务检查与待补项](source-reading-audit.md)，再读模块索引和相关笔记。

## 顶层目录

当前建立 19 个学习目录，各模块 `sources/` 保存逐篇资料笔记并由 README 索引；不预建芯片子模块目录。专属子模块合并到父级；UTCL1 这类公共模块按用户要求保留独立目录，并注明实例归属；缺少本项目层级证据的模块暂保留独立入口。**这是学习资料的组织方式，不是已验证的芯片 RTL 顶层图。**

| 目录 | 管理范围 |
| --- | --- |
| [DF](DF/README.md) | Data Fabric；CS、CAKE 暂按 DF 相关子模块归档 |
| [CF](CF/README.md) | Command Fabric，当前名称来自 shaobo 资料 |
| [SMN](SMN/README.md) | 系统管理网络主题 |
| [UTCL1](UTCL1/README.md) | 分布式一级地址翻译缓存主题；具体实例归属于使用它的模块 |
| [UTCL2](UTCL2/README.md) | 二级地址翻译缓存主题；本项目物理归属待确认 |
| [EA](EA/README.md) | Efficiency Arbiter；具体实例归属待确认 |
| [NBIF](NBIF/README.md) | NBIF 接口模块，边界与命名待资料确认 |
| [SWITCH](SWITCH/README.md) | 用户所说的芯片互联 switch；拓扑与协议待确认 |
| [UMC](UMC/README.md) | 内存控制器 |
| [HBM](HBM/README.md) | 高带宽内存及其与控制器、PHY 的接口 |
| [PCIE](PCIE/README.md) | PCI Express 接口主题 |
| [HDP](HDP/README.md) | 主机数据访问主题 |
| [PHY](PHY/README.md) | 物理层主题；区分内存、PCIe、芯片互联等不同实例 |
| [HUBS](HUBS/README.md) | MMHUB、CH，按用户给出的分组管理 |
| [SDMA](SDMA/README.md) | FE、BE、TBE；只提供独立项目链接及系统关系 |
| [GC](GC/README.md) | GL2、GRBM、RLC 的图形/计算上级归档入口 |
| [IH](IH/README.md) | 中断汇聚与处理 |
| [RSMU](RSMU/README.md) | 名称、职责及与 SMU 的关系待确认 |
| [SMU](SMU/README.md) | 系统管理、功耗与时钟等主题 |

`GC` 是为表示上级关系补充的归档名称，不额外展开其他图形计算模块。UTCL1/UTCL2 保留独立学习入口并不意味着它们在硬件上都是 SoC 顶层实例。CS、CAKE、GL2、GRBM、RLC、MMHUB、CH、FE、BE、TBE 不再分别建目录。

## 学习方法

每个主题逐步回答：负责什么、接收谁的请求、向谁发请求、如何完成、异常如何上报、关键参数与代际差异是什么。系统路径可用 SDMA 发起的一次搬运作为实例，沿地址翻译、互联、内存和中断路径理解。各路径的准确连接以目标芯片资料为准。

多轮论文研究统一采用 [芯片学习与微架构研究计划](chip-study-plan.md)。本项目已按代表性数据／请求路径和控制事件依赖形成 [模块方案及接续顺序](research-roadmap.md)。当前先处理资料补读与笔记完善；用户明确开始正式论文后，默认从 GC 第 1 轮开展详细研究；先借用相邻模块的最小接口基础，保持先上游、后下游的主线。SWITCH 已完成的两轮继续复用，其后续安排以 [修订方案](SWITCH/research-plan.md) 为准。项目范围与实际进度见 [项目上下文](project-context.md)。

后续收到新资料时，在对应顶层目录归档并补充来源；需要新增模块或改变父子关系时，同步更新映射表。整理日期：2026-09-23。


## 原始文件与 Markdown

UTCL2、HUBS 保留了五份资料的 223 个图像资源（含 155 页完整页面预览），但五份转换后的 Markdown 正文目前在本地和 GitHub 均缺失。用户已选择只同步当前已有文件，不补回正文。可从 [UTCL2](UTCL2/README.md) 与 [HUBS](HUBS/README.md) 入口查看现有页面图片；本次已依据这些已提交页图整理 C01–C05 技术笔记，未恢复转换正文；`assets/` 和 `sources/` 分别是图像与笔记目录，不是芯片子模块目录。

`original_file/` 中的文件仅供本地查看，不得上传 GitHub（包括私有仓库）或其他云端服务；已通过 `.gitignore` 排除。云端环境中无法打开指向这些本地原件的链接。

[历史转换报告](conversion-report.md) · [历史来源与哈希清单](source-manifest.json)。这些记录描述当时的转换结果，当前资料可用性以 [项目上下文](project-context.md) 和 [来源登记](sources.md) 为准。

GitHub 仓库：[niyingsong123/soc_study](https://github.com/niyingsong123/soc_study)。本地项目只关联 `soc_repo`；独立的 `sdma_repo` 继续在另一个项目管理。
