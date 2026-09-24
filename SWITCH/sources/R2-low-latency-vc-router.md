# R2：Mullins 等：look-ahead、预计算仲裁与单周期 router

更新日期：2026-09-24。

导读：解释低延迟 router 如何把控制从数据关键路径移开，以及空闲后多个新请求到达时为何需要冲突检测/撤销；用于约束低延迟方案的真实前提。
来源：[Low-Latency Virtual-Channel Routers for On-Chip Networks，ISCA 2004](https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf)。
阅读状态：已读 §2–5，重点 look-ahead、speculation、precomputing arbitration 及 safe/unsafe environment。

## 关键不是把所有方框挤进一拍

look-ahead routing 在上游计算下一 router 的路由，当前 router 接收时就能参与分配；当前节点可同时为下一跳计算新路由。它转移了计算位置，不是消除了依赖。若路由依赖实时拥塞，上游可见信息有传播延迟，不能假定全网状态瞬时共享。

推测 VA/SA 让 head 更快，但非推测请求优先、下游 credit 和分配成功条件仍必须满足。数据 bypass 也要有合法仲裁和缓冲回退；不能理解成输入未获授权就绕过队列直接输出。

## 预计算 grant enable 的安全条件

论文将部分仲裁决定提前一周期计算，寄存 grant-enable，再与当前请求相乘得到 grant。若上一拍仍有请求，下一拍候选通常可预测；若原来无请求，则分两类环境：每拍至多一个新请求时，可同时预使能多个候选而不会冲突；可能同时来多个请求时，全部使能会出现多个 grant，必须检测并 abort，或采用预测/提示等受限方案。

这个区分依赖具体仲裁层：一个输入端每拍只到一个 head，与多个输入同时竞争某输出完全不同。后者不能照搬前者的安全性。撤销必须覆盖本次操作的全部副作用，包括缓冲、credit、VC 归属和优先级更新；恢复后继续竞争，不得丢请求。

## 成本、比较与复用

预计算减少当前组合路径，但增加预计算状态、无请求特例与恢复控制。论文 FO4/cycle 和吞吐结果有给定结构及工艺模型，不能当通用 AMD 时序目标。低负载少冲突和高负载已有排队时的行为不同，极端同拍突发是必须保留的研究场景。

后续可把每个 SA 层标为可预知请求集、可能新增请求集、冲突检测时点和最终 commit 点。与 [R1](../../SWITCH/sources/R1-pipelined-router-delay.md) 的依赖图及 [R5](../../SWITCH/sources/R5-garnet-switch-allocator.md) 的实际发送条件比较。是否采用该技术由目标时序/面积需求决定，不必把 speculation 强制列为所有模块的必选 feature。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
