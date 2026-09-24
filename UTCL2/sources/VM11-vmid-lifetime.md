# VM11：动态 VMID 的租用、复用与页表更新依赖

更新日期：2026-09-24。

导读：解释为什么 VMID 不能当作永久进程编号，以及驱动如何用 active fence、页表根和 flush 进度防止过早复用。适合连接提交队列、翻译上下文与完成事件。
来源：[amdgpu_ids.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c)，blob `92d27d32de41ba138757c8c7f0b3f5c168a96fd6`。新增资料；文件名不是 `amdgpu_vmid.c`。
阅读状态：精读 VMID idle/used/reserved/grab、compatible、flush 进度与 active fence 处理；PASID allocator 的全部路径未展开。

## 上下文槽与软件地址空间

每个 vmhub 有自己的 VMID manager 和锁。VMID 保存 owner、页表根地址、已刷新更新序号、last_flush 和 active 依赖。它是可复用的硬件上下文槽；job 同时记录 VMID 与 VM 的 PASID，不能用其中任一个替代所有身份维度。

已有 VMID 只有 owner 与作业配置兼容才可能复用。若页表更新序号比已刷新的新、last_flush 缺失，或另一 fence context 的 flush 尚未完成，则需要维护或依赖等待。`concurrent_flush` 会影响能否在这些条件下复用，不能把策略简化成“相同进程直接复用”。

## 接纳、等待和完成

grab 先找 idle 候选，再尝试复用已分配槽；没有可直接使用的槽时返回需等待的 fence，而不是静默覆盖仍活动的映射。成功后把当前 job 的 finished fence 登记为该 VMID 的使用者，更新 owner、根地址和其他配置；需要失效时设置 job 的 `vm_needs_flush`。

标记 needs_flush 是提交前的决策，不等于硬件已完成 flush；后者还要经过 [VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md) 的命令与 ACK 及相应 fence 记录。`flushed_updates` 的软件 bookkeeping 也必须结合实际完成依赖读取，不能只比较一个数字。

reserved VMID/gang 路径还要等待 gang 组装条件，代码注释指出提前使用会有死锁风险。它说明“预留资源”也需要系统级进入条件；不能简单认为 reserved 就永远无等待。

## 跨模块用途

CF/SDMA 负责的作业完成如何释放翻译槽、页表更新如何排序到后续任务、hub 的上下文是否独立，都可用这份资料提出精确问题。这里仍是驱动资源协议；VFID 的硬件切换、pipe drain、mid-command preemption 不能由 VMID manager 单独证明。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
