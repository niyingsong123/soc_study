# MEM15：PG150：DQS gate 搜索、细调与失败定位

更新日期：2026-09-25。

导读：解释 DQS gate 搜索、重复采样、跨 rank 收敛，并补 2022 原图的整体训练分支与灰色未实现项；适合建立 PHY 阶段、配置和业务放行的关系。
来源：[Calibration Stages](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Calibration-Stages)、[Debugging DQS Gate Calibration Failures](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Debugging-DQS-Gate-Calibration-Failures)、[Determine the Failing Calibration Stage](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Determine-the-Failing-Calibration-Stage)，PG150 v1.4，2025-12-03。
阅读状态：已读 2025-12-03 网页的 DQS gate 算法与失败定位；本次另取得官方 2022-04-20 完整 PDF，直接核看第 593 页 Figure 38-5 总阶段图。两版日期分开记录，未声称 2025 总图已经核实。

## 门控要解决什么

XIPHY 用 DQS 捕获读数据并送入内部 FIFO，必须先确定何时打开门，避免空闲/前导区域被当成有效数据。训练发出单次读，通过采样状态确定 DQS 第一上升沿相对内部时钟的位置；按 byte 配置整数周期延迟，并用粗、细延迟作亚周期调整。

搜索从预计返回位置之前开始。预计值包含 PHY、PCB 和器件读延迟，不能只取 CAS latency。DDR3 空闲区域可能呈不确定采样，训练对一个位置重复 20 次采样，把不一致结果记为不确定；还检查整个边沿模式，并用 MPR 数据验证以减少耦合噪声造成的假匹配。独立随机采样的概率估算不覆盖相关噪声。

## 粗调、细调与跨 rank

算法先查粗相位模式，失败后调整整周期窗口重试；若起点太晚则向前移动。遍历仍不成功时再改变细相位起点，避免固定采样相位与占空比畸变组合造成漏检。找到边界后细扫不确定区并取中点。

每个 rank 可独立训练，但正常运行还要求同 byte 的整周期控制值能跨 rank 统一，差异由粗相位补偿；找不到公共设置则报错。因此“每个 rank 单独成功”未必保证最终公共配置成功。

## 诊断与研究复用

工具可定位失败阶段及 byte/nibble/bit，并区分尚未完成、算法失败和具体训练参数。方案应保留阶段、窗口边界、重复采样稳定性、公共配置约束及最终状态；不要只记录一个 calibration_done。

本项目可用这一实例说明校准如何从观测值生成运行配置，以及为何训练结束前不能放行普通流量。具体 tap 数/分辨率、模式和调试接口属于 FPGA IP，不能直接移植至 AMD GPU HBM PHY。串行链路的均衡/CDR 另见 [MEM6](../../PHY/sources/MEM6-pcie-equalization.md)/[MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md)。

## 补读整体训练流程：2022 版 Figure 38-5

来源：[AMD/Xilinx 官方 PG150 v1.4 PDF](https://www.xilinx.com/support/documents/ip_documentation/ultrascale_memory_ip/v1_4/pg150-ultrascale-memory-ip.pdf)，本次实际返回的封面日期为 **2022-04-20**，732 页；以下依据第 593 页 Calibration Stages 图，不能因为 v1.4 相同就当成 2025 网页的同一修订。

| 阶段组 | 图示依赖及分支 | 微架构上要理解什么 |
| --- | --- | --- |
| 起始 | System Reset→XIPHY BISC→XSDB Setup→DDR3/4 Initialization | PHY 内部自校准、调试配置与 DRAM 初始化各有责任，尚不能发普通流量 |
| 每 rank 基础定位 | DQS Gate→Write Leveling | 先确定读采样门控，再建立写 DQS 与器件时钟关系；不等同于读写数据眼已经居中 |
| 读路径初校 | rank 0 的 Read Per-bit Deskew、Read DBI Deskew，再到 Read DQS Centering Simple | bit 间偏斜与 byte 级公共 DQS 位置是不同参数；rank 分支决定哪些配置重复训练 |
| 写路径初校 | rank 0 的 Write DQS-DQ Deskew、Write DM/DBI Deskew、Write DQS-DQ Simple、Write DM/DBI Simple | 数据、掩码/DBI 与 strobe 的调整分别记录；不能以一个 tap 值概括整个写路径 |
| 后续训练 | Read DQS Centering DBI→Write Latency→Read DQS Centering Complex；rank 0 还走 Write DQS-DQ Complex | 从简单模式推进到更复杂数据模式及延迟对齐；分支和检查点必须保留 |
| rank 收敛 | Read DQS Centering Multirank Adjustment；未做完全部 rank 时回到 DQS Gate | 单 rank 成功还要处理公共配置及跨 rank 可兼容范围 |
| 结束 | Multi Rank Checks and Adjustments→Enable VT Tracking→Done | 多 rank 检查和运行期电压/温度跟踪接续在校准之后；Done 是完整流程的结果 |

图里的 **Read VREF Calibration (DDR4)** 和 **Write VREF Calibration (DDR4)** 是深灰项，图注明此版本不可用，不能根据方框存在就宣称该版本执行这些阶段。图中穿插的 Sanity Checks 也不是最终 Done 的同义词：其中 Check 5 只在非首 rank、Check 6 在所有 rank 执行。具体跳转应按原图分支，不应把所有方框拉成无条件直线。

这一补充使本笔记从单个 gate 搜索例子延伸到“训练阶段、状态保存、rank 共享参数、最终放行”框架。用作 PHY 第 3 轮的结构参考时，需分别记录当前阶段、被测 rank/byte/bit、失败/重试原因、产出的配置寄存器，以及成功后由谁允许普通流量。HBM 的训练集合及顺序仍须从对应 HBM PHY 原文确定，不能复制 DDR3/4 算法。

2025 网页总图本次仍未获得可核看的图像；历史总图已补读，不将两版一致性这一小项标成已证实。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
