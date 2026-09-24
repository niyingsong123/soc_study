# L3：外部 SDMA 待确认问题：保留 anshi TBE 边界

更新日期：2026-09-24。

导读：用于接续未决问题，特别是 anshi TBE 的剩余职责；当前没有原文，禁止用公开驱动或 shaobo 架构把未知项自动填满。
来源：外部只读项目 `D:\project\no_preject\sdma_repo\docs\context\open-questions.md`；历史登记见[全局资料集](../../sources.md#本地只读参考)。
阅读状态：本次未读取外部文件；仅整理当前仓库已登记的未知项和后续复查方式。

## 已知的未知

原登记特别要求保留 anshi TBE 剩余职责未确定这一边界。当前可确认的是存在待确认项，而非这些职责的内容；不能把另一个芯片的 TBE 或 AMD 公共 SDMA driver 直接当作答案。

## 后续接续

本地 Codex 应先读该问题集，检查问题是否已有更新证据、哪些会改变 SoC 模块接口或研究顺序。每项使用“当前疑问、已有依据、需要哪类证据、影响哪条工作流”的简短记录；只保留影响微架构判断的问题，避免无限扩展清单。

若当前任务只完善 SoC 方案，可将未决接口写成假设并标明适用条件，继续完成不依赖该答案的模块。若必须给出目标时序或职责归属，则需取得本地资料；这份范围笔记不能当作已完成详细技术总结。

与 [L1](../../SDMA/sources/L1-external-glossary-scope.md)/[L2](../../SDMA/sources/L2-external-shaobo-scope.md) 一起保留外部项目入口，公开 [SD1](../../SDMA/sources/SD1-sdma-system-lifecycle.md)/[SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) 只提供独立的系统层对照。所有后续核实继续遵守外部项目只读与原始文件不上传的边界。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
