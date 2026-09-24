# R10：UCIe 教程：协议层、D2D Adapter、CRC/retry 与状态协商

更新日期：2026-09-24。

导读：分清 FDI/RDI 两侧责任、raw/标准 flit 模式的可靠性归属，以及链路初始化/低功耗进入需要的多层握手；用于规划 die-to-die switch 边界。
来源：[UCIe Protocol，Hot Chips 2023 官方教程](https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf)，页码沿完整教程编号 25 起。
阅读状态：已读协议/flit 格式、adapter、初始化和 PM 示例；教程是 2023 版本背景，不代表后续所有 UCIe 修订。

## 三层责任

协议层提供 PCIe/CXL 或 streaming 事务语义；D2D Adapter 按协商模式承担 mux、flit framing、CRC/retry、链路状态和参数协商；PHY 承担 training、lane repair/reversal、scrambling 和物理传输。FDI 在协议层与 adapter 之间，RDI 在 adapter 与 PHY 之间。AMD 私有互联可以借这套分层分析，但没有证据证明它实际使用同一协议。

Raw 模式可让 adapter 不解释有效负载并旁路部分可靠性功能；不同标准 flit 格式由 adapter 添加 header/CRC，并改变协议层需要承担的校验/重放职责。不能说“只要使用 UCIe 就一定由 adapter 做所有 retry”，也不能把 flit mode 与电气层 FEC 混成一件事。

## buffer 与带宽的研究含义

协议 payload、flit header/CRC 和链路传输字节不同，实际效率需按协商格式计算。某些 flow-control 信息走独立的注入/插入通路而非普通 retry buffer；分析资源环路时不能假设所有控制消息都被同一数据 FIFO 承载。

发送后为重放保留的数据与远端接收 buffer 是两类资源。link ACK、retry 存储释放、远端协议接收和最终内存完成应分别定义。故障时重发必须避免上层重复提交；仅说明 CRC 能检测错误不足以完成可靠性方案。

## 初始化和电源状态

教程顺序为两端各自 reset、sideband 建立、training 参数交换与 mainband 训练/repair、协议参数协商，之后才开始 flit 传输。不能把 PHY active 直接解释为协议层已可接业务。

CXL PM 示例先让协议虚拟链路状态握手，再确认 retry buffer 为空，随后 adapter 经 sideband 协商，最后 PHY 进入低功耗。此顺序揭示有状态资源必须收敛；“无新请求”并不保证缓存/重放/返回均为空。精确的超时、重训练、错误恢复须查目标版本规范。

后续 die-to-die 研究以封装适配、buffer 预约、可靠性、状态协商和完成点组织；[R14](../../PHY/sources/R14-ucie-electrical-training.md) 负责物理层，[R11](../../SWITCH/sources/R11-ucie11-streaming.md) 专门解释 streaming 模式的版本变化。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
