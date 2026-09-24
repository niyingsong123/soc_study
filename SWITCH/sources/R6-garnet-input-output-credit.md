# R6：Garnet Input/OutputUnit：VC 状态与 credit 往返

更新日期：2026-09-24。

导读：配对追踪接收 flit、保存路由、流水等待、输入释放和下游 free-credit 返回，避免把 buffer 空槽与 packet 的 VC ownership 混为一个状态。
来源：[gem5 v24.1.0.1 InputUnit.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/InputUnit.cc)；同版本 [OutputUnit.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/OutputUnit.cc) 为同一资源生命周期的配套阅读，不单独虚增来源条目。
阅读状态：已读输入 wakeup、increment_credit，以及输出 VC 选择、credit wakeup 和链路发射函数。

## 输入侧保存包状态

接收到 head/head-tail 时，输入 VC 必须 idle，随后 active 并计算/保存 outport；body/tail 必须属于 active VC，继承已有路由。flit 放入输入 VC 后，模型按 router pipeline 配置将其标为当前或若干周期后可参与 SA，同时安排未来 wakeup。

这里的额外 pipeline 主要表现为可参与 SA 的时间戳等待，不能假定每延迟一拍都自动增加一个独立硬件吞吐级。head 的 route 存在 VC 状态中，flit 内 outport/outVC 则在 SA 胜出后更新；看单个 flit 字段可能误判状态尚未建立。

## credit 和 ownership 的双状态

输入被 SA 消费后，`increment_credit()` 产生 credit 并安排下一周期发送。普通 flit 仅返槽，tail 带 free signal。发送端 OutputUnit 保存下一跳各 VC 的 credit 与 active/idle 状态：收到 credit 增计数，只有 free signal 才标 idle。

因此一个 VC 可以有空槽但仍属于当前 packet；仅有 credit 不允许另一个 head 抢占 ownership。反过来，本地释放输入并不意味着上游立即知道，credit 还在链路中。吞吐估算需要计入该往返，不应只看 queue 深度。

## 统计与模型边界

InputUnit 在插入时同时增加预期 buffer read/write 活动，注释依据是每次写入以后读一次；它不是逐拍测量真实 SRAM 端口翻转。functional read/write 又是仿真访问机制，不代表正常时间模型的网络数据流。

可复用的守恒关系是“可用 credit + 已占/在途资源 = 配置容量”，但具体每项的计数边界须由实现定义。与 [R19](../../SWITCH/sources/R19-booksim-buffer-state.md) 的共享池比较时，还要区分全局空闲与 per-VC 保留容量。终点何时归还 tail/free credit 见 [R22](../../SWITCH/sources/R22-garnet-network-interface.md)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
