# R14：UCIe 电气教程：forwarded clock、训练、repair 与封装约束

更新日期：2026-09-24。

导读：解释 UCIe die-to-die 物理层如何依赖封装距离、时钟/数据匹配、训练与 lane repair；用来区分链路可靠性、可用带宽和协议完成。
来源：[Electrical, Form-Factor, and Compliance，Hot Chips 2023 UCIe 官方教程](https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf)，完整教程页码 52 起。
阅读状态：已读 PHY architecture、clocking、BER/channel、LTSSM、initialization/repair 与 compliance 相关页；所有速率/距离/封装参数保留 2023 教程版本范围。

## 与长距离 SerDes 的结构区别

教程给出单向 NRZ、单端数据和差分 forwarded clock，强调 clock/data 路径匹配。advanced 与 standard package 在基本模块宽度、bump pitch、reach、终端与冗余能力上不同；不能把 x64/x16 当所有 die-to-die 接口的统一配置。

接收端采样质量由数据/时钟差分 jitter、skew、Vref、信道损耗和供电共同影响。clock forwarding 降低某些时钟恢复成本，却没有消除相位校准和 tracking。TX/RX 电压兼容又属于跨工艺可靠性，不是数字协议握手能解决的问题。

## 训练、维护和状态层次

sideband 先初始化，mainband 再做参数交换、clock/valid/data 检查及 repair/reversal，随后以目标速度训练。LTSSM 区分 active、低功耗、retrain 和 train-error；降速/降宽或使用备用 lane 会改变可用带宽与延迟，不能在故障恢复后仍按原峰值计算。

clock gating 受 valid、前后导时序和协商的 free-running 模式影响；track 通路支持背景相位维护。上层暂停数据不等于能立即关闭所有时钟。具体 state timeout、lane map 和重训练后的丢包/重放边界需要与 adapter 配合，见 [R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md)。

## BER 与系统可靠性

教程按数据率/封装讨论 BER 目标，并将 CRC/retry 与系统 FIT 联系起来。BER 是原始链路错误概率尺度，CRC 检出、retry 成功、不可纠正错误和上层事务失败是不同指标。不能把一次 retry 等同于一次应用数据错误，也不能只报告低 BER 就忽略重放容量与延迟尾部。

## 后续规划

PHY 研究按“controller/adapter 接口 → 数字训练/状态 → AFE/时钟 → 封装通道 → 观测/恢复”展开。与 [MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md) 的 CDR/均衡对照时解释各自链路类型；不能把 FPGA GT、UCIe 和 HBM PHY 合并成一个训练流程。精确电气 compliance 需要目标版本规范及测量条件，本教程不提供 AMD 私有 PHY 实现细节。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
