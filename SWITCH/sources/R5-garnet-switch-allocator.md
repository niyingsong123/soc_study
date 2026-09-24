# R5：Garnet SwitchAllocator：两级选择、发送资格与最终提交

更新日期：2026-09-24。

导读：逐步说明 SA-I/SA-II 怎样选择 flit、何时分配 outVC、扣 credit、弹出输入及更新 RR；重点是有请求与允许发送之间的差别。
来源：[gem5 v24.1.0.1 SwitchAllocator.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc)。
阅读状态：已读 wakeup、arbitrate_inports/outports、send_allowed、vc_allocate 与 wakeup scheduling。

## 决策顺序

SA-I 在每个输入端口的 VC 中按 RR 查找一个可发送候选；SA-II 在每个输出端口对各输入提交的候选再做 RR。第一阶段每输入只能提交一个候选，因此即使另一个 VC 指向空闲输出，也可能在本拍未参与第二阶段。这种 separable 分配不等于全局最大匹配。

该版本把空闲 outVC 分配并入 SA 胜出处理，没有独立 VA 流水级。比较 [R1](../../SWITCH/sources/R1-pipelined-router-delay.md) 的传统流水时必须说明差异，而不是按旧阶段名字强行解释代码。

## send_allowed 的三类条件

head 尚无 outVC 时，目标 vnet 至少要有空闲 VC；模型假定空闲 VC 至少有一个 buffer slot。body/tail 已有 outVC 时需要其 credit。ordered vnet 还检查同输入、同 vnet、同输出是否有更早进入且已 ready 的 VC；有则不能越过。该规则不是全系统所有 ID 的强排序，只适用于代码定义的范围。

最终胜出才读出 flit、更新 outport/outVC、扣下一跳 credit、推进 ST 并交给 crossbar。随后返还上游输入槽 credit；tail/head-tail 还把本输入 VC 设 idle，并附 free signal。RR 指针在实际 grant 处更新，未完成发送的请求不能被错误当成已服务。

## 资源与完成语义

下游 outVC 空闲、下游 buffer 有空、当前输入被弹出、上游观察到 credit、远端应用接收 packet 是不同事件。此代码只负责 router 内传输；credit 链路有传播时间，具体见 [R6](../../SWITCH/sources/R6-garnet-input-output-credit.md)。研究 QoS 应记录候选被哪条条件过滤、在哪一级输掉，而不是只有一项“arbiter stall”。

可用于 EA 仲裁的思考方法，但不能代表 [C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 的 bank/group/list-manager 结构。后续可用空闲输出遗漏、ordered vnet 老请求阻塞、tail credit 延迟等定向例子解释吞吐及公平性边界。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
