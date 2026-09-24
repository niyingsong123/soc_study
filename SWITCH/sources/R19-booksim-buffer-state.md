# R19：BookSim BufferState：共享池、保留槽与 tail-credit 释放

更新日期：2026-09-24。

导读：区分总容量、per-VC 占用、共享池、保留槽和 VC ownership，并解释不同 buffer policy 与 tail-credit 配置怎样改变可发送条件。
来源：[BookSim buffer_state.cpp，固定提交 28f4329](https://github.com/booksim/booksim2/blob/28f43299f1706a3160ffac721ca461d74eb6e618/src/buffer_state.cpp)。
阅读状态：已读 BufferPolicy 构造、private/shared/limited 分支和 SendingFlit/ProcessCredit/TakeBuffer；feedback policy 的全部调参不作为本笔记已验证算法。

## 数据结构表达的是发送端的下游资源视图

BufferState 维护总 occupancy、每 VC occupancy、in_use_by、tail_sent，另由 policy 判断某 VC 是否可取得槽位。TakeBuffer 分配 VC ownership，SendingFlit 占用容量，ProcessCredit 释放容量；这些事件不能只用一个“buffer empty”布尔量替代。

Private policy 固定容量；shared policy 包含 private 部分与共享部分，空闲总量不意味着每 VC 无限制可用。limited/dynamic-limited 再对单 VC 持有量施加限制，以防一个流占满共享资源。真正可用量取决于保留槽、私有剩余和共享剩余，需按 policy 解释。

## 保留与归还的细节

共享策略中某些已经分配、暂时无数据的 VC 会保留槽位；后续 flit 可消耗预留，而不是再次从共享池扣。tail 时还需回收剩余 reservation。若只跟踪数据 occupancy，可能把仍被承诺给旧包的空间再次分出去。

`wait_for_tail_credit` 开启时，VC ownership 等 tail 已发送且其 occupancy 归零后才释放；关闭时可在 tail 发出后释放 ownership，而 credit 仍继续返回并修正容量。两者不是同一个 free 事件，不可任意跨策略比较。

代码对总/局部 underflow、overflow、已占 VC 再分配和异常 credit 都有检查。研究模型应维持同类不变量，并明确 reset 时是重置统计还是实际销毁 outstanding 状态。

## 复用与限制

本实现适合为 [C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 共享 command/data pool 建立概念对照，但它不是 AMD EA 的 list-manager RTL。后续要分别列物理存储、逻辑队列、reservation、ownership 和归还事件，再研究动态限额是否改善公平/利用率。源码统计能验证模型内部守恒，不能证明硬件 RAM 端口和访问时序足够。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
