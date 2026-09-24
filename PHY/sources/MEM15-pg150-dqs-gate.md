# MEM15：PG150：DQS gate 搜索、细调与失败定位

更新日期：2026-09-24。

导读：详细解释读数据门控如何找到 DQS 起始位置，覆盖粗/细调、重复采样、rank 统一及诊断；适合 PHY 校准专题，不能据此宣称已读所有训练阶段。
来源：[Calibration Stages](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Calibration-Stages)、[Debugging DQS Gate Calibration Failures](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Debugging-DQS-Gate-Calibration-Failures)、[Determine the Failing Calibration Stage](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Determine-the-Failing-Calibration-Stage)，PG150 v1.4，2025-12-03。
阅读状态：已读 DQS gate 算法正文与失败定位说明；总阶段页图未成功读取，未据目录推定完整训练先后顺序。

## 门控要解决什么

XIPHY 用 DQS 捕获读数据并送入内部 FIFO，必须先确定何时打开门，避免空闲/前导区域被当成有效数据。训练发出单次读，通过采样状态确定 DQS 第一上升沿相对内部时钟的位置；按 byte 配置整数周期延迟，并用粗、细延迟作亚周期调整。

搜索从预计返回位置之前开始。预计值包含 PHY、PCB 和器件读延迟，不能只取 CAS latency。DDR3 空闲区域可能呈不确定采样，训练对一个位置重复 20 次采样，把不一致结果记为不确定；还检查整个边沿模式，并用 MPR 数据验证以减少耦合噪声造成的假匹配。独立随机采样的概率估算不覆盖相关噪声。

## 粗调、细调与跨 rank

算法先查粗相位模式，失败后调整整周期窗口重试；若起点太晚则向前移动。遍历仍不成功时再改变细相位起点，避免固定采样相位与占空比畸变组合造成漏检。找到边界后细扫不确定区并取中点。

每个 rank 可独立训练，但正常运行还要求同 byte 的整周期控制值能跨 rank 统一，差异由粗相位补偿；找不到公共设置则报错。因此“每个 rank 单独成功”未必保证最终公共配置成功。

## 诊断与研究复用

工具可定位失败阶段及 byte/nibble/bit，并区分尚未完成、算法失败和具体训练参数。方案应保留阶段、窗口边界、重复采样稳定性、公共配置约束及最终状态；不要只记录一个 calibration_done。

本项目可用这一实例说明校准如何从观测值生成运行配置，以及为何训练结束前不能放行普通流量。具体 tap 数/分辨率、模式和调试接口属于 FPGA IP，不能直接移植至 AMD GPU HBM PHY。串行链路的均衡/CDR 另见 [MEM6](../../PHY/sources/MEM6-pcie-equalization.md)/[MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
