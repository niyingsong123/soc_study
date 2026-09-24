# R18：iSLIP：VOQ、Request/Grant/Accept 与指针更新

更新日期：2026-09-24。

导读：解释交叉开关的两侧匹配、RR 指针为何必须与接受结果关联，以及多轮匹配的第一轮更新规则；用于区分单输出仲裁与多输入多输出分配。
来源：[The iSLIP Scheduling Algorithm for Input-Queued Switches，IEEE/ACM TON 1999](https://www.cs.cmu.edu/~dga/15-744/S07/papers/islip-ton.pdf)。
阅读状态：已读单轮/多轮算法、RRM 同步问题、公平性与均匀流量结果；不把定长 cell、特定到达模型的吞吐保证扩大到任意 NoC 流量。

## 问题是匹配而非单独选一个请求

每个输入按输出建立 VOQ，避免一个拥塞目的地的队头阻塞其他目的地。一次 slot 中每输入和每输出最多参与一个连接，故输出各自 grant 之后，仍需输入 accept 来消除一个输入被多个输出选中的冲突。VOQ 解决队头隔离，matching 决定如何使用 crossbar，两者不可互相替代。

Request 报告有待发 cell 的输入→输出候选；每输出按自身 RR grant；每输入从收到的 grants 按另一 RR accept。匹配只会在双方最终接受后成立。maximal matching 表示不能再直接加边，不等于全局 maximum matching。

## 状态更新是算法的重要部分

简单 RRM 若每次 grant 都移动输出指针，即使未被 accept，多个输出可能保持同步反复选择同一输入，浪费可用并发。iSLIP 的输出 grant pointer 只在 grant 被接受时前移，让未服务候选继续有机会。多轮版本还限制相关输出指针更新在第一轮成功接受时发生；后续轮用于填补剩余未匹配输入/输出，不应任意改写规则。

移植到带 backpressure 的 RTL 时还要定义最终 transfer：accept 后如果链路不 ready，能否把它计作服务？论文 slot 模型和持续 valid/ready 模型不完全相同，需把状态提交点写清。

## 性能主张的条件

文中均匀 i.i.d. 到达下的高吞吐结果不表示所有不均匀、相关 burst、变长包、信用限制和 QoS 权重下都满速。更多迭代改善匹配但占组合时间/流水周期。局部连接不饥饿也不能自动升级成多跳网络每个应用流的时延上界。

本资料适合 SWITCH 的 allocator 对比，EA 仅在确实有多侧匹配结构时使用。[R5](../../SWITCH/sources/R5-garnet-switch-allocator.md) 的两级 separable allocator 不等于完整 iSLIP；[EA1](../../EA/sources/EA1-rr-arbiter.md) 的 RR tree 更只是一个仲裁器。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
