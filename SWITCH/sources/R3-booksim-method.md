# R3：BookSim 论文：模型边界、两阶段更新与性能实验口径

更新日期：2026-09-24。

导读：说明微架构仿真如何保持真实并行时序、建模 credit 延迟和源端排队，并揭示局部公平与全局公平、年龄优先与吞吐之间的区别。
来源：[A Detailed and Flexible Cycle-Accurate Network-on-Chip Simulator，ISPASS 2013，作者 KAIST 页面](https://icn.kaist.ac.kr/~jjk12/papers/2013ISPASS.pdf)。先前备用 LBNL 链接失效，采用此原作者入口。
阅读状态：通过公开 PDF 核读 §II–IV 及 §V 的 age/RTL validation 相关内容；本次未运行 BookSim，也未声称完成 AMD 模型校准。

## 分清四层模型

拓扑决定连接，路由决定选择路径，流控决定争用时谁可占资源，router 微架构决定 buffer/allocator/crossbar 的组织。traffic manager 又规定注入、包长、流量分布和端点行为。研究一种优化时应明确修改哪层，避免同时改变拓扑、buffer 总量和时钟而把收益只归给仲裁算法。

模型在 flit/周期粒度工作，邻居经 channel 通信，credit 走反向通道。链路宽度应反映为包的 flit 数和序列化代价；internal speedup、crossbar speedup、网络链路速率也是不同参数，speedup 往往需要额外输出 buffering，并非免费提高频率。

## Evaluate/Update 防止仿真“偷看未来”

旧模型逐个执行阶段并立即更新状态时，后执行的 SA 可能看到同拍 VA 已经成功，从而无意消除本应存在的推测失败。BookSim2 将读状态/计算决策与生效更新分开：先 evaluate，产生带时间标记的更新，再统一 update。这样并行硬件逻辑都基于正确周期的状态。

这一原则也适用于 UTCL2 miss/fill、EA 同拍 enqueue/dequeue、credit 返回与发射。模型如果写得可运行却泄露本拍结果，性能会系统性偏乐观。look-ahead 的零延迟近似对确定性路由可能合理，对依赖拥塞的自适应路由必须计入信息陈旧性。

## 实验要包含源端等待与资源归还策略

注入意愿与实际注入不同；饱和后源端排队若被忽略，会低估总延迟。应分别统计 offered load、accepted/injected load、delivered throughput、source queue latency 和 network latency，说明 warm-up、测量、drain 及停止条件。

`wait_for_tail_credit` 决定 VC 是否等前包尾 credit 返回后再分配；其与仅在 tail 发出后释放的策略有不同包间依赖与利用率。策略名相同也要核对实现，见 [R19](../../SWITCH/sources/R19-booksim-buffer-state.md)。局部 RR 公平不保证多跳流的全局公平；age-based 可改善某些 starvation，却也可能改变匹配质量和饱和吞吐，不能仅凭“更公平”断言更快。

## 使用范围

论文用特定 RTL 对照验证模型，证明对应配置的建模可信度，不能代表任意新参数都已与真实芯片一致。后续规划保留可追溯配置、指标定义和定向场景即可；目前不需要先构造大规模仿真平台。[R4](../../SWITCH/sources/R4-garnet-overview.md)–[R6](../../SWITCH/sources/R6-garnet-input-output-credit.md) 提供另一模型的实现对照。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
