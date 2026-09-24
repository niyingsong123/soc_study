# MEM7：AM002：串行接收均衡与 CDR

更新日期：2026-09-24。

导读：把链路误码问题分解为信道损耗、均衡与采样相位跟踪，适合 PHY 微架构入门；不提供 HBM 源同步接口或目标芯片的接收器设计。
来源：[AM002 RX CDR](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-CDR)、[RX Equalizer DFE and LPM](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-Equalizer-DFE-and-LPM)、[RX Margin Analysis](https://docs.amd.com/r/en-US/am002-versal-gty-transceivers/RX-Margin-Analysis)（页示 revision 1.3，2023-10-26）。
阅读状态：已读 Versal GTY/GTYP 接收器上述正文；未读全手册、未做眼图/BER 实测。

## 信号路径

接收均衡用于补偿信道高频损耗及码间干扰；CDR 在均衡后的信号上利用边沿和数据采样获取时序信息，控制相位插值器调整采样位置。PLL 提供基础时钟，CDR 继续跟踪接收数据与本地时钟之间的频率/相位偏差，因此 PLL lock 不能直接当作数据采样可靠的充分条件。

数据采样希望位于眼中心，边沿采样提供偏差方向；控制状态更新作用于 phase rotator。方案需要同时考虑信号恢复与时序恢复，不能只为 PHY 画一个“反序列化”方块。

## 均衡能力边界

DFE 依赖已判决符号补偿后游标干扰，不能用它消除前游标；线性均衡则可影响前后游标。选择 DFE/LPM 要结合信道损耗、速率与功耗条件，不能仅以功能更多判定更好。误码由发送器、信道和接收器共同决定，不能看到高 BER 就直接归因为 CDR。

## 观测位置影响眼图含义

Margin Analysis 说明，高损耗下板上接收端眼图可能闭合，而接收均衡后的内部眼仍可打开。GTY/GTYP 的 RX eye scan 用于观察均衡后裕量；因此板级远端眼、内部统计眼和系统 BER 不能当成同一测量。只读到机制介绍，未读取完整扫描设置或把工具输出用作协议合规证书。

## 后续研究如何展开

先定义目标通道、速率及编码，再列模拟均衡、判决、CDR、解串、弹性缓冲与协议训练之间的关系。观察量宜包括锁定状态、误码、系数/相位变化及重训频率；区分训练暂态和稳定态测量。

这些是可迁移的分析步骤。具体 tap 数、收敛条件、眼宽阈值和功耗数据必须来自目标产品材料。[MEM6](../../PHY/sources/MEM6-pcie-equalization.md) 给出 PCIe 训练序列，不能用本页物理解释替代协议完成条件；[MEM5](../../PHY/sources/MEM5-ug586-phy.md) 的 DQS 源同步训练也不应按同一个 CDR 模型解释。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
