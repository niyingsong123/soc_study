# 资料来源

整理日期：2026-09-23。公开文档用于解释术语和提供架构参考，不能证明本项目目标芯片的具体实现。初始化时读取本地 Markdown 摘要。C01–C05 留有历史转换与校验记录，但五份 Markdown 正文当前缺失；用户选择只同步现有文件，不补回正文。当前状态见 [项目上下文](project-context.md)，未进行新的 RTL 核验。

## 用户说明

- **U1：** 本次任务给出的模块清单、HUBS（mmhub、CH）与 SDMA（FE、BE、TBE）分组；SDMA 独立项目只读；后续由用户补充新模块资料。
- **U2：** 用户明确纠正模块名称为 GRBM。
- **U3：** 用户明确允许 UTCL1 这类公共模块独立建目录，即使某个实例位于 TBE 内部。
- **U4：** `original_file/` 仅供本地查看，不得上传 GitHub 或其他云端服务。
- **U5：** SOC 项目仅关联 `soc_repo`，取消独立 `sdma_repo` 的附加关联；SDMA 文件继续独立管理。
- **U6：** GitHub 同步只包含当前已有文件，不补回已缺失的五份 Markdown 正文。
- **U7：** 用户说明已建立云端 `niyingsong123/soc_study` 环境，并希望连接该环境；本条不表示本地任务已经切换到云端。

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

## 新资料登记方式

新增资料记录：来源编号、文件链接、产品/代际、版本/日期、覆盖模块、章节定位及未决问题。不同版本保留差异，不覆盖已有引用依据。尚未收到的资料不登记为已读来源。

## C01–C05：历史转换登记与当前状态

原件统一平铺保存在本地 `original_file/`，保留原文件名与字节内容，禁止上传。表中的 Markdown 路径只用于标识缺失正文，不作为可点击入口。页数来自历史转换登记；版本以原文为准，不凭文件名推定适用产品。

| 编号 | 原件名称（仅本地） | 原 Markdown 路径与当前状态 | 页数 | GitHub 与本地可读资源 |
| --- | --- | --- | --- | --- |
| C01 | `tb_mm_utcl2.pptx` | `UTCL2/tb_mm_utcl2.md`（缺失） | 49 | [现有图像](UTCL2/assets/tb_mm_utcl2/) |
| C02 | `UTCL2 结构和使用简介 by Wang Junmin.pptx` | `UTCL2/UTCL2 结构和使用简介 by Wang Junmin.md`（缺失） | 38 | [现有图像](UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin/) |
| C03 | `utcl2_top.pdf` | `UTCL2/utcl2_top.md`（缺失） | 1 | [现有图像](UTCL2/assets/utcl2_top/) |
| C04 | `UTCL2地址翻译及预取技术介绍.pdf` | `UTCL2/UTCL2地址翻译及预取技术介绍.md`（缺失） | 26 | [现有图像](UTCL2/assets/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D/) |
| C05 | `MMHUB_introduction.pptx` | `HUBS/MMHUB_introduction.md`（缺失） | 41 | [现有图像](HUBS/assets/MMHUB_introduction/) |

[历史转换报告](conversion-report.md) · [历史 SHA-256 清单](source-manifest.json)。这些记录保留当时的结果，不能作为五份正文当前存在的证明。C01 第 6 页引用的 `code_coverage_improve.xlsx` 未提供；当前仅保留该附件缺失的记录。
