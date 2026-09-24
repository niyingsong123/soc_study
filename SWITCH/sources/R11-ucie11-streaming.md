# R11：UCIe 1.1 streaming：可复用可靠性不等于统一上层协议

更新日期：2026-09-24。

导读：说明 UCIe 1.1 如何让非 PCIe/CXL 的 streaming payload 复用 adapter CRC/replay，并指出 Raw Mode、flit 格式协商和上层 CHI 打包的边界。
来源：[UCIe 官方：UCIe 1.1 Provides Streaming Protocol Solution for Error Detection and Replay，2023-08-28](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay)。
阅读状态：已读完整正文；这是版本功能说明文章，未提供完整线格式与一致性事务规则。

## 版本变化的意义

文章对照 1.0 的 Raw streaming：它绕过许多 UCIe 功能，可靠性需实现者自行处理。1.1 的 streaming flit 允许把其他协议消息放入已有 flit 类型兼容的 payload，复用 D2D adapter 插入 header/CRC、检测和 replay 的逻辑。研究中必须先说清使用哪种模式，不能把 Raw 与 streaming flit 混称为同一可靠性方案。

## 仍需上层解决的问题

初始化会协商 flit 类型，文章给出特定格式 236 或 250 字节 payload。它们是格式有效负载，不是 lane 宽度，也不是一个 coherence transaction 恒定大小。上层仍要定义如何打包、跨 flit、恢复消息边界、处理多类 channel 和满足 ordering。

CHI 可以使用可靠 streaming 承载，但 UCIe 本身不定义 CHI cache ownership。文章对 CHI 标准化打包的表述处于 2023 年时间点，不能当作所有后来规范功能的完整描述。多个设备都支持 UCIe PHY，也不自动证明它们的任意私有 streaming payload 互通。

## 用于后续规划

将“物理可连接、flit 格式兼容、可靠传输、上层语义兼容”列为四个独立层次。研究实现时关注 adapter 的 retry buffer、上层 backpressure、控制消息是否可前进，以及重放对上层是否透明。文章无法回答精确序号窗口、重放深度和错误上报，不能据此编造数值。结合 [R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md)/[R14](../../PHY/sources/R14-ucie-electrical-training.md) 使用，AMD 目标是否采用 UCIe 仍是待证项。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
