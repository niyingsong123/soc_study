# R4：Garnet 2.0：NI、router、vnet 与流水模型总览

更新日期：2026-09-24。

导读：建立 gem5 网络模型的组件与参数语义，区分协议 vnet、物理链路、VC 和端点缓冲；适合阅读具体 allocator/credit 代码前使用。
来源：[gem5 官方 Garnet 2.0 文档](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)。网页随项目更新；本资料集代码对照固定 v24.1.0.1。
阅读状态：已读配置、组件、routing、router pipeline 与 flow-control 内容；文中旧 garnet2.0 路径与固定版本 garnet 路径存在命名差异。

## 系统中的位置

Ruby coherence controller 通过 MessageBuffer 连接 NetworkInterface；NI 把协议消息转换成 flit，router 仲裁并向链路发出，反向 CreditLink 传送容量与 VC 释放信息。网络收包与 coherence controller 消费消息有独立缓冲边界，端点背压属于完整性能/死锁分析的一部分。

vnet 是协议消息类别，VC 是承载它的队列/资源，物理链路按时间复用传 flit。增加 vnet 不等于增加物理带宽，增加 VC 也不能替代协议依赖分离。具体 mapping 由模型配置及 coherence 协议决定。

## 默认值只是示例模型

文档描述默认一周期 router，也可在拓扑中增加 router delay。不同消息按控制/数据映射成不同 flit 数，宽度改变会影响序列化；不能把一个 message 计作恒定一拍。链路 delay 与 router pipeline 独立，跨 die 建模还需补适配、序列化、CDC 和可靠性，不能只加一个 hop。

默认表驱动最短路径可用 link weight 表达偏好，另有 XY/custom 路由入口。权重定义路径选择，不是物理带宽或电气距离。自定义算法是否无死锁必须单独论证。

## 阅读代码时的检查表

先用 [R6](../../SWITCH/sources/R6-garnet-input-output-credit.md) 追 head 建立 route 与 VC 状态，再用 [R5](../../SWITCH/sources/R5-garnet-switch-allocator.md) 看发送资格与 SA 两级选择，最后用 [R22](../../SWITCH/sources/R22-garnet-network-interface.md) 看 NI 的 tail stall。检查统计口径：模型中的 buffer read 活动可能按预期访问记账，不等于可直接映射到硅上某个 perf event。

本资料提供模型骨架而非 AMD 实现事实。方案中引用它时应写“用于研究/仿真对照”，不能写“AMD router 默认一周期”。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
