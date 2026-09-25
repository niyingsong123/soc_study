# R22：Garnet NI：终点背压、tail 保留与协议缓冲依赖

更新日期：2026-09-24。

导读：说明网络到达终点后仍可能因协议 MessageBuffer 无空间而持有 tail/VC，并解释 credit、回调和消息交付的关系；用于补齐端到端依赖分析。
来源：[gem5 v24.1.0.1 NetworkInterface.cc](https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/NetworkInterface.cc)。
阅读状态：已读 wakeup、stall queue、flitisizeMessage、VC 选择及发送调度相关路径；消息是模型对象，不将其内存表示当硬件缓存实现。

## 两侧接口与注入

NI 一侧接协议 MessageBuffer，另一侧接 flit 和 credit 链路。注入时需要可用 VC，再把消息按 link width 拆成 flit 并维护 vnet/route/入队时间。多目的消息的展开、ordered vnet 检查和端口选择影响实际注入；协议消息 ready 不意味着本周期全部注入网络。

## 终点消费是独立资源

普通非 tail flit 到达后可返回槽 credit；tail/head-tail 到达时，只有相应 protocol buffer 有空间、且本周期 ejection 条件允许，才能 enqueue 消息并返还带 free signal 的 credit。若无空间，tail 放入 stall queue，保持相关 VC 占用并登记 dequeue callback。

下游协议消费者取走消息后，callback 安排 NI 重查，解除 stall 并归还 credit。于是 router 路由已结束与 packet 真正被协议层接收之间仍有可持续等待。endpoint 若又等待网络资源生成/发出另一消息，就可能闭合协议级资源依赖。

## 完成与统计的边界

模型删除非 tail flit 对象不表示硬件 payload 丢失，消息对象承载其数据语义；不能把软件对象释放位置当实际 SRAM 释放。tail 统计在成功交付/解除 stall 时完成，端点等待会进入相关延迟口径。

一周期可能产生多个待发 credit，代码另安排后续 wakeup，说明信用生成与链路实际送出不同步。注入 VC 空闲、ejection free signal 和消息消费者完成也不可合并。

## 后续复用

SWITCH 的 deadlock 方案必须纳入 NI、reorder/response buffer、协议 consumer；仅证明 router channel graph 无环不够。与 [R16](../../SWITCH/sources/R16-remote-control-deadlock.md) 的边界整包吸收、[R7](../../SWITCH/sources/R7-floonoc-paper.md) 的响应预约、[FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) 的软件完成一起建立多层资源图。此文件不含 AMD IH/DF 协议，只提供一个可核对的机制案例。

第三轮复用此处已保存的固定版本阅读记录，没有重新运行 gem5。本文 R0 另行选择有限 target record：在完整 packet 被其真实存储接管后可释放 Local VC，record 则保持到 response 注入完成。与 Garnet 的差别是协议消费者何时已有可接管空间；不能把 tail 到达本身当成一切资源都可释放。此项是项目参考设计比较，不是对 Garnet 源码的新实现结论；具体流程见[目标 NI](../../switch/switch_detailed_guide.md#66-目标-ni从最后一跳接管到目标真正执行)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
