# VM8：gem5 Vega 页表遍历器的依赖状态与端口重试

更新日期：2026-09-24。

导读：具体解释一个 page walk 如何保存上下文、逐级读 PDE/PTE、等待内存、遇到背压重试并回填。适合建立 walker 与缓存/内存服务之间的接口。
来源：[pagetable_walker.cc，gem5 v24.1.0.1](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/pagetable_walker.cc)。新增资料。
阅读状态：精读 startTiming/initState、startWalk/stepWalk、walkStateMachine、sendPackets、recvTimingResp/retry、pageFault；未执行模拟。

## 每次 walk 必須保存什么

`startTiming` 为请求创建 WalkerState，保存原翻译 packet、访问 mode、根地址和当前 VA；每次读取 8-byte 表项，初始化从该模型的 PDE2 开始。不同 walk 各自保留状态，页表级间有数据依赖：上一层返回给出下一层地址，不能把四级 walk 当作四个无关访存同时发出。

状态依次解释 PDE2、PDE1、PDE0、PTE，某些 PDE 可作为叶子提前结束，fragment/block-fragment 影响最终页大小与下一层索引。模型对 blockFragmentSize 有特定取值断言，因此这不是支持所有 AMD 页表组合的通用解码器。最终必须同时形成对齐页面基址和页大小，供上游重建每个客户的 offset。

## 下游拥塞怎样反馈

发请求前为 packet 压入指向 WalkerState 的 sender state。下游 `sendTimingReq` 返回 false 时，撤回刚压入的临时状态，保留未发送 packet，并置 retrying；不会把失败发送当作已接受。收到 retry 回调后重新发送。收到响应后根据 sender state 找到正确 walk，解析本层表项，再产生下一次读。

因此同时存在两种等待：请求尚未被端口接受，以及请求已被接受、正在等待响应。二者在资源释放、重试和性能计数上不同。研究 UMC/NoC 反压时，这个区分尤其有用。

## 结束与异常

有效叶子结束依赖链，形成 entry 并通知 TLB；中间表项的属性还影响下一次表项读取是否 uncacheable。无效或相应执行保护条件会生成 page-fault 对象。软件模型里的错误对象、TLB 层的 fatal 分支，以及真实 GPU 的可恢复 fault 通知并不是同一个机制。

Functional 模式直接访问内存推进遍历，Timing 模式通过时延、端口接纳和响应事件推进。不能用 functional 正确翻译测试证明 timing 反压、并发容量或吞吐正确。

## 跨模块复用

UTCL2→GC/内存的页表读取应携带正确地址域和访问属性；返回还要关联 walk 身份。页表缓存、调度优先级、在途失效和取消机制不由本例完整实现，分别联读 [VM5](../../UTCL2/sources/VM5-mask-paper.md)、[C03](../../UTCL2/sources/C03-utcl2-topology.md)、[VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md)。如果只需复述依赖流程与 retry，本笔记可直接使用；实现精确字段时回读该版本代码。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
