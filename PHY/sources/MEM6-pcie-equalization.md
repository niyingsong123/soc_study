# MEM6：PG239：PCIe PHY 均衡阶段与完成语义

更新日期：2026-09-24。

导读：解释 Preset Apply、接收适配、发送系数更新的不同阶段，适合 PCIe PHY 与链路状态机联读；重点是请求接受和适配完成的区别。
来源：[PG239 Product Specification](https://docs.amd.com/r/en-US/pg239-pcie-phy/Product-Specification)、[Equalization Sequences](https://docs.amd.com/r/en-US/pg239-pcie-phy/Equalization-Sequences)，v1.0，2024-12-18。
阅读状态：已读均衡序列章节；产品规格仅作入口，未读完整 PCIe 规范或实现全部训练流程。

## 状态与方向

Preset Apply 位于相关电气空闲和新速率切换的规定窗口，见 Recovery.Speed/Polling.Compliance 场景。它是应用预设，不是完整 RX 适配。RX adaptation 对上游方向出现在 Phase 2、对下游方向出现在 Phase 3；TX adaptation 在互补阶段参与系数协商。

RX 流程分 New Proposal 和 Adaptation；`rxeq_done=1` 时仍需结合 `adapt_done` 判断到底是新提议阶段结束还是适配结束。单独看到 done 就把链路标成可用会丢掉状态语境。TX 侧也有系数 Apply/Query 等不同操作，操作完成与最终链路进入正常传输不是同一事件。

## 对方案的用法

先建立 PHY 与上层训练控制器的状态契约，再研究 preset、系数、接收判定和失败恢复。表格应列出当前阶段、发起方向、参数所有者、done 的限定含义、失败后的动作。训练占用时间应与稳定态链路吞吐分开统计。

这份资料的价值是公开接口例子；不能据此给 AMD GPU PCIe PHY 填入相同状态编码，也不能把 PCIe 的阶段号套到 UCIe/HBM。[MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md) 解释均衡/CDR 的信号基础，[R14](../../PHY/sources/R14-ucie-electrical-training.md) 与 [MEM8](../../PHY/sources/MEM8-ucie-official-qa.md) 属于 D2D 的另一种链路背景。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
