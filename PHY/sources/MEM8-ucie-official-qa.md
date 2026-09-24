# MEM8：UCIe 官方问答：侧带、lane 与链路延迟口径

更新日期：2026-09-24。

导读：澄清 UCIe 初代公开介绍中的 lane 模块化、侧带和延迟数字；用于 D2D 接口与 PHY 边界，避免把物理指标当系统事务性能。
来源：[Introduction to UCIe Webinar Q&A Recap](https://www.uciexpress.org/post/introduction-to-ucie-webinar-q-a-recap)，UCIe 1.0 背景的官方说明。
阅读状态：已读问答正文；不是当前最新规范，未据此推定后续版本的 FEC、训练或封装能力。

## 侧带和 lane 不是普通流量通道的别名

侧带支持训练、管理、调试和固件相关活动，设计意图与主数据通道不同。物理 lane 与逻辑 lane 存在映射，可涉及 reversal 和冗余替代。高级封装示例按一组 lane 提供 spare，具体数量应按规范/封装版本核实，不能把 spare 当成持续可用的额外 payload 带宽。

模块化宽度选择兼顾时钟偏斜、布线与面积开销；问答讨论 x16 等组织不等于任意缩成 x1 都保持相同效率。举例 4 Gbit/s×16 lanes=64 Gbit/s=8 GB/s 是单方向原始速率，尚未扣编码、协议和空闲开销。

## 延迟必须标出端点

问答的物理延迟目标以 FDI 与 bump 等边界定义，不能当作远端读返回延迟。完整事务还可能经过 adapter、协议队列、retry/retrain、远端目标服务和响应路径。对确定性要求高的研究，应说明哪些延迟有界、哪些受排队或恢复影响。

## 复用边界

用于 SWITCH D2D 章节时，将主数据发送、侧带状态、链路训练、重试和事务完成分别画出。无 FEC 等说法只限该材料的版本背景；正式设计须查匹配版本规范。与 [R10](../../SWITCH/sources/R10-ucie-protocol-adapter.md)/[R11](../../SWITCH/sources/R11-ucie11-streaming.md) 的协议层材料和 [R14](../../PHY/sources/R14-ucie-electrical-training.md) 的电气训练教程联读，可建立层次，但仍不能证明 AMD Infinity Fabric 采用 UCIe。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
