# FAB7：AMDGPU fence：ring 完成写回、序号槽位和异常收敛

更新日期：2026-09-24。

导读：把抽象 dma-fence 落到 AMDGPU 的 ring 命令、写回内存、序号表、中断/定时器与回收流程，适合研究数据完成怎样变成软件可等待事件。
来源：[Linux v6.12 amdgpu_fence.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_fence.c)。
阅读状态：已读 fence contract、emit/polling、process、fallback、wait 和恢复相关入口；具体 ASIC emit_fence 的硬件指令仍需读相应 ring 实现。

## 硬件事件与软件对象

文件开头约定：写 fence 时，相关 ring 应已不再使用关联 buffer，并满足相关 GPU cache 刷新要求。这是生产者协议前提；本文件的通用 emit 不独自实现所有刷新，实际动作委托 `amdgpu_ring_emit_fence()` 和 ASIC 回调。

emit 增加该 ring 的 sync_seq，建立 context/seqno 对象，向 ring 发出 fence 写命令，再把对象放入按 mask 索引的槽位。槽位环会复用，所以若旧对象尚存需先等待并释放；空间复用受到完成进度约束。重提交 job 还需重新关联序号，不能用旧序号判断新执行已完成。

## 通知不等于每个中断一项工作

硬件写回序号后，`amdgpu_fence_process()` 读取并推进 last_seq，遍历这段区间的槽位并 signal 对应对象。一次检查可能完成多项 fence；没有新 seq 则不重复通知。中断只是触发检查的一种方式，fallback timer 可在中断未及时到达时再检查。

因此 IH 记录数量、fence signal 数量和硬件任务数不必相等。性能研究应分别记录硬件完成写回时间、驱动观察时间和等待者唤醒时间，不能把调度/中断延迟全算成 DF 数据路径延迟。

## 生命周期和错误

引用、RCU 槽位和锁保护对象直到消费者不再使用；ring 的 runtime-PM 引用也与未完成工作有关。恢复时的错误完成/强制 signal 用于解除等待，不可当成结果正确写入的证据。消费者应同时检查 status/error，而不是只看 signaled 位。

适合后续维护一张完成关系表：数据操作 → ASIC cache/ordering 动作 → fence 写回 → 通知/轮询 → dma_fence → buffer 复用。与 [FAB4](../../DF/sources/FAB4-dma-fence-contract.md)、[IO3](../../PCIE/sources/IO3-linux-dma-api.md)、[SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) 一起阅读。本文件不足以证明 PCIe posted writes、XGMI link ACK 或 UTCL2 invalidate 与任务 fence 的先后关系，必须追相应命令序列。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
