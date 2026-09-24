# MG7：IH 公共代码：发布顺序、IV 解码与 checkpoint

更新日期：2026-09-24。

导读：解释 producer/consumer ring 的内存顺序和 32 字节 IV 格式，覆盖 budget/restart、软件 ring 和 checkpoint；适合写 IH 完成与丢事件边界。
来源：[Linux v6.12 amdgpu_ih.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c)。
阅读状态：已读 ring 分配、写入、处理、Vega10+ 解码及 checkpoint 等待；未把公共格式推广至旧代际。

## 地址、容量与单位

ring 大小按 2 的幂对齐，ptr_mask 用于回绕。bus-address 分支用 dma_alloc_coherent，并在尾部放 rptr/wptr shadow；另一分支用 GTT BO 和独立 writeback 槽。CPU 指针、gpu_addr 与 shadow 地址分别保存，不能只画一个 ring base。

公共解码的 rptr/wptr 单位是字节，数组访问转为 Dword；一次读取 8 Dword，推进 32 字节。字段包含 client/src/ring、VMID 及来源、时间戳及来源、PASID、node 和 4 个源数据字。字段意义要结合 client，不能把 src_data 固定理解为地址。

## 发布与消费顺序

软件写 ring 先写 IV，wmb 后发布 wptr；消费者先取 wptr，再 rmb 后读 IV。coherent 分配不消除这类排序需求。软件写路径在检测到回绕碰到 rptr 时不发布新 wptr，但数据写已发生，不能仅由该判断声称拥有完整无覆盖保护。

处理循环有每批 IV 计数，发布 rptr 并唤醒等待者后再次读 wptr，如仍有数据便 restart。因此批量上限不是整个 handler 必然有界的总工作量；高持续输入仍需研究服务预算和公平性。

## Checkpoint 的保证范围

checkpoint 取当时 wptr 前一项时间戳，等待 processed timestamp 经过该点或 ring 已空，并有可中断超时。它证明的是相应 IV 消费进度，不自动证明所有由 handler 触发的异步工作完成，也不覆盖此前已溢出丢失的事件。

后续研究分别记录业务完成、IV 生成、ring 可见、dispatch、异步处置和 checkpoint。[MG8](../../IH/sources/MG8-irq-dispatch-lifecycle.md) 解释分派，[MG6](../../IH/sources/MG6-ih60-ring-hardware.md)/[MG12](../../IH/sources/MG12-vega10-ih-comparison.md) 解释硬件入口差异。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
