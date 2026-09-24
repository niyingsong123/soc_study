# IO3：Linux DMA API：地址、所有权、同步和 scatter-gather

更新日期：2026-09-24。

导读：用于判断设备应使用哪种地址、何时 CPU/设备可以碰缓冲区、为何 coherent 仍需排序。原 SWITCH R17 与本条是同一资料，复用此笔记。
来源：[Linux 6.12 DMA API HOWTO](https://docs.kernel.org/6.12/core-api/dma-api-howto.html)；兼容来源编号 R17。
阅读状态：已读地址关系、DMA mask、coherent/streaming、方向、map/sync/unmap、scatter-gather 与错误处理段；未验证某硬件平台。

## 三种地址与两类映射

CPU 虚拟地址经 CPU 页表得到 CPU 物理地址；设备发出的是 DMA/bus address，可能经 IOMMU 才到相同 RAM。`dma_addr_t` 不是 CPU 指针，也不能默认等于物理地址。映射 API 同时处理平台寻址限制；设置 streaming mask 与 coherent mask 时须检查返回值。

coherent 内存允许双方观察更新而不显式做通常的 cache 同步，但不免除内存顺序：descriptor 的地址/长度必须在 valid 标志之前发布。streaming 映射强调设备访问方向和所有权转换，CPU 再读取或修改前要按 API 同步，重新交回设备前也要完成相应操作。

DMA_TO_DEVICE 是内存到设备，DMA_FROM_DEVICE 是设备到内存；方向应从数据流解释，不能从 CPU 发起命令的方向猜测。精确方向还影响权限检查与平台优化。

## 映射资源与完成

每个成功 map 要有对应 unmap；解除映射前应确保 DMA 活动已结束。映射失败不可把返回地址继续交给硬件。共享 cache line 的不当布局可能使 CPU 和设备修改互相覆盖，哪怕它们修改不同字段。

保持同一 streaming 映射并多次复用时，CPU/设备之间通过 sync_for_cpu/sync_for_device 转移访问阶段；这与是否发出了完成中断是两个条件。中断可能告知设备操作结束，却不能替代特定平台要求的 cache 同步。

## Scatter-gather 的两个计数

dma_map_sg 可以合并相邻项，返回给硬件使用的 segment 数 count，可能小于输入 nents。编程硬件时遍历 count 并使用 sg_dma_address/len；unmap 和 sync 时传入原始 nents。把两种计数混用会破坏映射管理。

## 连接微架构

对 SDMA/PCIe/IH 的每条缓冲区路径，记录 CPU 地址、DMA 地址、映射生命周期、所有权、发布顺序、完成证据和解除映射时点。[IO8](../../IH/sources/IO8-linux-msi.md) 说明 MSI 的传输排序，[MG7](../../IH/sources/MG7-ih-core-consumer.md) 说明 IH ring 的内存读取屏障，[VM10](../../UTCL2/sources/VM10-iommu-spec.md) 提供 AMD IOMMU 背景。此 API 不证明目标 SDMA FE/BE/TBE 的内部地址字段。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
