# IO8：Linux MSI：通知写、向量分配与中断并发

更新日期：2026-09-24。

导读：解释 MSI/MSI-X 为什么是内存写形式的通知、如何与之前的数据写排序，以及多向量如何改变并发；适合 IH 到 CPU 的最后一段路径。
来源：[Linux 6.12 MSI Driver Guide](https://docs.kernel.org/6.12/PCI/msi-howto.html)。
阅读状态：已读基本原理、排序、向量 API、锁和诊断段；不是完整 PCIe 规范或中断控制器硬件说明。

## 通知和数据的关系

MSI 是设备向特定地址发出的写，引起 CPU 中断。在文档所述 PCI 事务顺序条件下，通知写不能越过此前数据写；这避免传统引脚中断可能先于数据到达的情形。这个保证应限定在相应事务路径和排序条件，不能无条件扩成所有 GPU cache 数据已对所有代理可见。

中断仍只是事件通知；软件要读取 ring/status 才知道发生了什么，streaming DMA 的同步职责也仍存在，见 [IO3](../../PCIE/sources/IO3-linux-dma-api.md)。IH 产生的一条 IV 和 CPU 收到的一次 MSI 未必一一对应，合并、预算和 ring 排空另见 [MG7](../../IH/sources/MG7-ih-core-consumer.md)。

## 向量资源与并发

MSI-X 可独立配置较多向量；MSI 数目受更严格数量和布局限制。驱动申请 min/max，必须使用实际分配的数量并处理不足；支持多队列不代表一定能分到每队列一个向量。MSI 与 MSI-X 不能同时开启。

单向量不会自重入的经验不能用于多向量共享锁。另一向量中断可能在持有同一锁时到来，形成递归等待；锁与关中断范围必须按并发路径设计。向量亲和性影响软件分摊，不直接改变设备内部事件仲裁。

## 研究落点

记录事件产生、IV 入 ring、wptr 发布、MSI 写、CPU handler、rptr 回收等不同事件。用 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md) 的 dummy read 配置解释平台顺序辅助，用 [MG6](../../IH/sources/MG6-ih60-ring-hardware.md)/[MG12](../../IH/sources/MG12-vega10-ih-comparison.md) 比较 IV 格式及溢出处理。文档数字只描述机制上限，不是目标芯片配置。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
