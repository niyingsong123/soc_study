# FAB4：dma-fence：完成对象、时间线与硬件语义的边界

更新日期：2026-09-24。

导读：解释 fence 的 context/seqno、signal/error、callback 与 lifetime，帮助区分软件完成对象和硬件 flush/fence 操作；跨模块研究完成语义时必读。
来源：[Linux v6.12 include/linux/dma-fence.h](https://github.com/torvalds/linux/blob/v6.12/include/linux/dma-fence.h)。
阅读状态：已读结构、ops 注释、signal/status/wait、seqno 比较和引用生命周期接口；未把头文件视为所有驱动的硬件完成规范。

## 一个 fence 记录什么

dma_fence 是软件同步原语，包含 context、seqno、flags、错误、锁、引用计数和回调/时间戳生命周期。seqno 只有在适当的同一时间线上才可比较；不同 ring/context 的较大数值不表示全系统执行得更晚。32-bit 与 64-bit seqno 也有不同的比较处理，不能用普通无符号大小比较替代其 API。

signal 是一个不可逆的完成通知，error 可说明以错误结束；signaled 不等于成功。回调的安装可能与 signal 并发，引用要保护对象直到消费者结束使用。signal 后 callback list、timestamp、RCU 复用同一 union 存储，直接绕过 API 读取容易误解生命周期。

## signaling、等待与硬件动作不同

`enable_signaling` 可按需启用中断或插入命令，以支持硬件→软件通知；某些实现始终启用。`signaled` 回调可作为查询快路径，wait/callback 则供消费者使用。这些接口定义通知与对象管理，不会自动生成目标硬件所需的 cache writeback、HDP flush、TLB invalidate 或 PCIe posted-write drain。

因此写技术论文时，必须同时写生产者保证：它在发出完成值之前等待了哪些工作、刷新了哪些 cache、错误怎样表示。消费者等待 dma_fence 只是取得该保证，不能扩大其 scope。强制 signal 用于异常恢复时，尤其不能写成数据已正确落地。

## 用于跨模块研究

为每个完成点记录“哪个 ring/context、seqno、相关 buffer、成功/错误、硬件写回位置、通知方式、等待方”。将任务完成、协议 completion、link ACK、credit return 分开：它们可能发生在不同层级，互不自动替代。AMD 的具体实现见 [FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md)，SDMA 的接口边界见 [SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md)，CPU/DMA 内存规则见 [IO3](../../PCIE/sources/IO3-linux-dma-api.md)。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
