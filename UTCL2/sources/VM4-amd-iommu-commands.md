# VM4：AMD IOMMU 驱动的多级翻译缓存失效与完成等待

更新日期：2026-09-24。

导读：说明为什么更新系统映射后可能需要同时处理 IOMMU 内部缓存和 ATS 设备 IOTLB，并追踪 command queue 与 completion wait。适合与本地 GPUVM invalidate 对比。
来源：[drivers/iommu/amd/iommu.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/iommu/amd/iommu.c)。
阅读状态：精读 command 构造、range 编码、queue/completion、device/domain flush 相关函数；中断重映射与全部 IOMMU 模式未通读。

## 两类缓存拥有者

`build_inv_iommu_pages` 按 domain、地址范围及条件 PASID/GN 构造 IOMMU 内部失效，并设置 PDE 位以覆盖中间翻译缓存。`build_inv_iotlb_pages` 则带设备标识、ATS queue depth 等信息，面向设备侧 IOTLB。两种命令针对不同状态拥有者；清掉前者不保证后者不再使用旧翻译。

domain flush 先按 IOMMU/页表模式安排内部失效，再遍历属于该 domain 且启用 ATS 的设备，排队设备 IOTLB 失效。未启用 ATS 的设备不会凭空多出设备 ATC 路径。Device Table Entry 更新还涉及设备 alias，不能只按一个 PCI requester 数字理解所有关联。

## 范围和队列不是简单调用参数

`build_inv_address` 对单页做页对齐；多页范围根据首尾最高不同位编码覆盖范围并设置 size 位，跨出可编码范围时扩大到全范围。这说明硬件失效实际覆盖区域可能比软件修改区域更大，不能把 byte length 原样当成逐字节精确比较。

命令通过 ring buffer 入队并发布 tail。入队成功只表示控制命令交付给 IOMMU 的队列，不等于远端设备已完成。`need_sync` 记录是否还需同步；completion wait 使用递增值，让硬件向指定 semaphore 内存写入这个值，软件等待相同值，从而区分不同批次的完成。

## 一个映射更新的阶段划分

页表/设备表更新可见 → 构造有关失效命令 → 向相关 IOMMU 队列提交 → 向启用 ATS 的设备发起 IOTLB 维护 → 排入 completion wait 并等待 → 才能根据上层 API 契约继续。具体 hard/soft fence、读写 drain 和协议完成条件必须由 IOMMU/ATS 规范限定，不能只靠这个调用顺序补出。

`amd_iommu_domain_flush_pages` 的注释明确将完成等待与 IOMMU TLB、设备 IOTLB 完成联系起来；NpCache/vIOMMU 分支还会考虑非自然对齐范围的代价。因此不同平台模式不能直接共用同一失效成本假设。

## 跨模块复用

[VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md) 是 GPUVM/hub 内的维护，本文是系统侧 IOMMU 和设备 IOTLB 的协调；[IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) 解释 ATS/PASID/PRI 的能力配置。讨论 heavy/light、NACK 或在途请求 drain 时继续查 [VM10](../../UTCL2/sources/VM10-iommu-spec.md)，不把 Linux 函数名当作全部协议语义。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
