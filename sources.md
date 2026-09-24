# 资料来源

基础整理日期：2026-09-23；Switch 第二轮公开研究补充：2026-09-24。公开文档用于解释术语和提供架构参考，不能证明本项目目标芯片的具体实现。初始化时读取本地 Markdown 摘要。C01–C05 留有历史转换与校验记录，但五份 Markdown 正文当前缺失；用户选择只同步现有文件，不补回正文。当前状态见 [项目上下文](project-context.md)，未进行目标芯片 RTL 核验。

## 用户说明

- **U1：** 本次任务给出的模块清单、HUBS（mmhub、CH）与 SDMA（FE、BE、TBE）分组；SDMA 独立项目只读；后续由用户补充新模块资料。
- **U2：** 用户明确纠正模块名称为 GRBM。
- **U3：** 用户明确允许 UTCL1 这类公共模块独立建目录，即使某个实例位于 TBE 内部。
- **U4：** `original_file/` 仅供本地查看，不得上传 GitHub 或其他云端服务。
- **U5：** SOC 项目仅关联 `soc_repo`，取消独立 `sdma_repo` 的附加关联；SDMA 文件继续独立管理。
- **U6：** GitHub 同步只包含当前已有文件，不补回已缺失的五份 Markdown 正文。
- **U7：** 用户说明已建立云端 `niyingsong123/soc_study` 环境，并希望连接该环境；本条不表示本地任务已经切换到云端。
- **U8：** 用户要求以高质量公开资料研究 NoC 与 D2D 的完整微架构，按六轮迭代维护 `switch/`；本次明确授权在云端开始第二轮 Router 专项。具体轮次和执行边界见 [研究进度](switch/RESEARCH_PROGRESS.md)。

- **U9（2026-09-24）：** 用户明确 SWITCH 仅完成两轮，原六轮规划可根据新研究修订；其他模块轮数按需增减。当前先用高质量资料逐模块完成研究与撰写方案，详细内容由后续本地 Codex 展开；各模块规划完成后再评估跨模块研究。U8 的固定六轮安排是当时计划，后续可按本条复核调整。
- **U10（2026-09-24）：** 用户要求始终以整体微架构为基础规划子模块和 feature：先建立结构与工作流程，再分解研究，并把每轮结果整合回整体微架构。
- **U11（2026-09-24）：** 用户明确本项目以 AMD 芯片和 AMD 模块命名为基础。学习前应查找行业别名、通用术语及功能相关名称，扩大高质量资料范围；例如 UTCL2 可以联合 MMU 主题研究。最终方案以 AMD 命名组织。这里记录用户的研究方向，不据此宣称两个模块完全等价；适用边界须在研究中核实。具体执行规则见 [项目上下文](project-context.md)。

- **U12（2026-09-24）：** 用户要求在规划具体子模块、feature 或其他研究内容时，把发现的相关资料链接附在对应内容旁，供后续本地 Codex 学习。具体执行方式见 [研究范本](chip-study-plan.md)的“挂接资料并编排研究轮次”。

- **U13（2026-09-24）：** 用户要求审视当前规划是否遗漏必要内容，以及哪些步骤多余、缺乏意义或会增加云端与本地 Codex 的思考负担。根据该要求整理的精简执行方法见 [研究范本](chip-study-plan.md)；具体取舍是规划方法，不作为目标芯片的技术事实。

- **U14（2026-09-24）：** 用户明确确认最终六步实施计划，授权按计划执行，并要求在真正开展模块规划前将计划保存到 GitHub，作为以后芯片学习可持续维护和更新的范本。已确认版本集中保存于 [chip-study-plan.md](chip-study-plan.md)，当前项目应用与进度另见 [project-context.md](project-context.md)。

## 本地只读参考

下列相对链接指向仓库之外的独立 SDMA 项目，仅在本地对应目录存在时可用，GitHub 仓库中不包含这些文件。

- **L1：[SDMA 术语表](../sdma_repo/docs/context/glossary.md)**：CF/DF、FE/BE/TBE、UTCL1/UTCL2 的本项目语义。配合 [项目上下文](../sdma_repo/docs/project-context.md)。
- **L2：[shaobo 架构摘要](../sdma_repo/docs/context/shaobo.md)**：FE 两条后端路径、CF_IF/DF_IF、TBE 内 UTCL1、UTCL2 请求及 MMHUB 写回。其原始依据为外部项目 S1「dma_utcl1」「Dma_ce」与 S2「子模块划分」等，定位见 [外部原始资料目录](../sdma_repo/docs/sources.md)。
- **L3：[SDMA 待确认问题](../sdma_repo/docs/context/open-questions.md)**：特别保留 anshi TBE 的剩余职责未确定这一边界。

外部目录为 `D:\project\no_preject\sdma_repo`。这里只引用，不复制或修改其文件。L1–L3 是本项目引用编号；外部 S1–S9 的编号保持原义。

## 公开参考

- **P1：[AMD Ryzen Processor Software Optimization，GDC 2019](https://gpuopen.com/gdc-presentations/2019/gdc-2019-s2-amd-ryzen-processor-software-optimization.pdf)**，2019-03-20，第 21 页：SDF、CS、CAKE、UMC 的参考架构与术语。适用 Ryzen 示例；只支持 DF 相关主题的初步归档，不能确定 shaobo/anshi 的 RTL 父级。
- **P2：[Linux AMDGPU Core Driver Infrastructure — GPU Hardware Structure](https://docs.kernel.org/gpu/amdgpu/driver-core.html#gpu-hardware-structure)**：GC 包含 RLC、IH 和 SMU 基本职责、内存 hub 的架构差异。在线文档查询日期 2026-09-23，未固定内核提交。
- **P3：[AMD ROCm Compute Profiler — GL2 cache](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.1/conceptual/rdna/gl2-cache.html)**：gfx115x 的 GL2 与 GCEA 访问路径，不能直接推广到所有 GPU。
- **P4：[AMD ROCm Compute Profiler — Graphics Register Bus Manager](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.1/conceptual/rdna/grbm.html)**：GRBM 名称、图形/计算活动统计主题。
- **P5：[AMD ROCm 6.0.0 — MI200 performance counters and metrics](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html)**，2024-01-16：EA、UTCL1、UTCL2、GRBM、HBM 缩写与计数器参考。同页 CS 指 Compute Shader，说明缩写必须结合上下文，不能直接替换 DF 语境的 Coherent Slave。

## P6：Switch 公开研究资料组

登记日期：2026-09-24。完整来源条目、版本和引用关系在 [详细微架构稿](switch/switch_detailed_guide.md)第 37、48 章，使用该文内部的 R1–R21 编号，不覆盖本页的 L/P/C 编号。第一轮完整稿另存 [v2.0 历史原稿](switch/switch_detailed_guide_v2.0.md)。

第二轮实际重点阅读与对照如下；只声明阅读所列章节和源码，不声明完成全部文献或规范的合规核验。

| 对应编号 | 来源与版本 | 本轮阅读定位及用途 |
|---|---|---|
| R1 | Peh/Dally，2001，[Router 延迟与推测架构论文](https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf) | VC/推测流水、credit turnaround；用于空间闭环和失败路径 |
| R2 | Mullins/West/Moore，ISCA 2004，[低延迟 VC Router](https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf) | Router 结构与控制路径；不采用其工艺数字作为本项目参数 |
| R5 | gem5 tag `v24.1.0.1`，[SwitchAllocator.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc) | `arbitrate_inports/outports`、成功路径和指针更新；blob `e31733d42e1d2a84f5afc86050a8209367983aa1` |
| R18 | Nick McKeown，IEEE/ACM ToN 7(2)，1999，[iSLIP 原论文](https://www.cs.cmu.edu/~dga/15-744/S07/papers/islip-ton.pdf) | 第 III、VI、IX 节，第一迭代指针更新与 matching；原场景是固定 cell 输入排队交换机 |
| R19 | BookSim2 commit `28f43299f1706a3160ffac721ca461d74eb6e618`，[buffer_state.cpp](https://github.com/booksim/booksim2/blob/28f43299f1706a3160ffac721ca461d74eb6e618/src/buffer_state.cpp) | 私有/共享容量、SendingFlit/ProcessCredit/TakeBuffer；blob `228d91d0ab1a221cf6ced0461e650959eecce0f8` |
| R20 | Yuval Tamir、Gregory L. Frazier，ISCA 1988，[High-Performance Multi-Queue Buffers for VLSI Communication Switches](https://web.cs.ucla.edu/~tamir/papers/isca88.pdf) | 第 III 节、buffer organisation 与 timing；用于共享数据/指针/free pool 的实现对照 |
| R21 | I. Seitanidis、A. Psarras、G. Dimitrakopoulos、C. Nicopoulos，DATE 2014，[ElastiStore](https://gdimitrak.github.io/papers/date14a.pdf) | 第 II–IV 节与 Fig.1–5，弹性 VC、共享辅助槽和反压；未合入本轮 mesh 模型 |

本轮代码是原创教学模型，不是以上实现的重命名副本；模型运行结果登记在 [round2_results.json](switch/examples/round2_results.json)，验证范围见 [研究进度](switch/RESEARCH_PROGRESS.md)。公开资料不证明目标芯片 SWITCH 属于 DF、连接 CAKE 或采用某一协议。

## 新资料登记方式

新增资料记录：来源编号、文件链接、产品/代际、版本/日期、覆盖模块、章节定位及未决问题。不同版本保留差异，不覆盖已有引用依据。尚未收到的资料不登记为已读来源。

## C01–C05：历史转换登记与当前状态

原件统一平铺保存在本地 `original_file/`，保留原文件名与字节内容，禁止上传。表中的 Markdown 路径只用于标识缺失正文，不作为可点击入口。页数来自历史登记；版本以原文为准，不凭文件名推定适用产品。

| 编号 | 原件名称（仅本地） | 原 Markdown 路径与当前状态 | 页数 | GitHub 与本地可读资源 |
| --- | --- | --- | --- | --- |
| C01 | `tb_mm_utcl2.pptx` | `UTCL2/tb_mm_utcl2.md`（缺失） | 49 | [现有图像](UTCL2/assets/tb_mm_utcl2/) |
| C02 | `UTCL2 结构和使用简介 by Wang Junmin.pptx` | `UTCL2/UTCL2 结构和使用简介 by Wang Junmin.md`（缺失） | 38 | [现有图像](UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin/) |
| C03 | `utcl2_top.pdf` | `UTCL2/utcl2_top.md`（缺失） | 1 | [现有图像](UTCL2/assets/utcl2_top/) |
| C04 | `UTCL2地址翻译及预取技术介绍.pdf` | `UTCL2/UTCL2地址翻译及预取技术介绍.md`（缺失） | 26 | [现有图像](UTCL2/assets/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D/) |
| C05 | `MMHUB_introduction.pptx` | `HUBS/MMHUB_introduction.md`（缺失） | 41 | [现有图像](HUBS/assets/MMHUB_introduction/) |

[历史转换报告](conversion-report.md) · [历史 SHA-256 清单](source-manifest.json)。这些记录保留当时的结果，不能作为五份正文当前存在的证明。C01 第 6 页引用的 `code_coverage_improve.xlsx` 未提供；当前仅保留该附件缺失的记录。
