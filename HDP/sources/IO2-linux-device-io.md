# IO2：Linux Device I/O：MMIO、Posted write 与访问顺序

更新日期：2026-09-24。

导读：解释 CPU 寄存器访问与设备真正收到写入之间的差异，覆盖 MMIO 映射属性、读回和 relaxed accessor；适合主机控制路径与 HDP 完成语义。
来源：[Linux 6.12 Device I/O](https://docs.kernel.org/6.12/driver-api/device-io.html)。
阅读状态：已读 MMIO accessor、posted write、映射类型及 ordering 相关正文；未穷尽平台特有实现。

## 地址和访问方式

`ioremap` 返回 `__iomem` token，便携驱动须通过 readl/writel 等访问，不能把它当普通 RAM 指针解引用。CPU 物理 MMIO 地址、设备 BAR 地址和映射后的 CPU 虚拟 token 是不同对象，地址变换另见 [IO3](../../PCIE/sources/IO3-linux-dma-api.md)。

普通寄存器映射限制投机、合并、重复等行为；WC 映射允许更强优化，适用于可承受这些行为的区域。带读写副作用的寄存器不能仅为性能改成普通可缓存内存。64 位寄存器在部分平台通过两个 32 位操作访问，先后半字顺序由设备定义，不能默认原子。

## 顺序与完成分开

MMIO accessor 约束 CPU/编译器观察的访问顺序，但 PCI memory write 可以 posted：写指令退休时设备可能尚未收到。需要确认特定写已到达时，可按文档采用同设备的合适读回；设备复位期间则须考虑可安全失败的读路径。spinlock 只约束软件互斥，不能自动排空 posted write。

relaxed accessor 减弱与 DMA 等访问之间的序列化，在确知不依赖 DMA 完成的路径上才有合适语义。不能把“读出了寄存器值”普遍解释为所有设备内存写都已可见。`ioremap_np` 也不能为 PCI BAR 强行制造非 posted 的 memory write。

## 对 HDP/CF 研究的启发

明确区分写缓冲排空、设备寄存器副作用生效、HDP flush、cache invalidate、页表失效与命令 fence。它们可以先后依赖，但不是同义词。为每种完成定义观察者、作用范围和确认方式，再连接 [IO6](../../HDP/sources/IO6-hdp40-maintenance.md) 的实际驱动分支。

本资料提供 OS 契约，不能证明 AMD 内部具体桥接器的缓存组织或 CF 拓扑。后续可用“CPU 写 descriptor→发布 valid→敲 doorbell→设备工作→状态/中断”逐步标注所需顺序，而不把单个 barrier 当成整条链路的万能完成标志。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
