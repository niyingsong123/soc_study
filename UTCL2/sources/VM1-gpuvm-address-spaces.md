# VM1：GPUVM 的地址空间、VMID、PASID 与 aperture

更新日期：2026-09-24。

导读：建立 GPUVA、页表、动态 VMID、PASID 与系统地址的基本关系；尤其适合防止把 GPUVM 和系统 IOMMU 合并为一个翻译器。
来源：[amdgpu_vm.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c)，blob `6005280f5f38f07c0b5c5f583f1b4e273ac117e9`。
阅读状态：精读开头 `DOC: GPUVM` 与 `amdgpu_vm_set_pasid`；页表 BO 搬迁和全部更新实现未系统研读。

## 对象、身份和地址

GPUVM 是 GPU 提供的 MMU 功能总称。与单一全局 GART 相比，它允许多个页表同时处于活动状态。一个页表可以混合 VRAM 页和系统页，系统页还区分 snooped/unsnooped 属性。不能因为地址已经经过 GPUVM，就认为它一定指向本地显存，或者已经完成系统 IOMMU 的所有翻译。

VMID 是活动硬件地址空间上下文的标识，命令缓冲提交时由内核动态分配并告诉引擎。进程拥有的长期地址空间与暂时分配的 VMID 是不同对象。PASID 是另一个身份维度；`set_pasid` 用 xarray 维护 PASID 到软件 VM 对象的关联，先移除旧关联，再建立新关联。该函数没有直接完成所有硬件 PASID/VMID 寄存器编程。

原注释写出某些 ASIC 支持的活动 VM 数和页表级数，必须保留历史/家族语境，不能当作未来所有 UTCL2 的固定参数。动态重用的真正条件见 [VM11](../../UTCL2/sources/VM11-vmid-lifetime.md)。

## VMID 0 的特殊性

VMID 0 除页表管理的 aperture 外，还有直达 VRAM 和 legacy AGP 等 aperture。AGP 路径可转发到 system physical address；系统存在 IOMMU 时也可能处于 IOVA 语境。因此“VMID 0 不用页表”是过度简化，“物理 GPU 地址等于 CPU 物理地址”同样不成立。

需要把范围匹配、偏移转换和页表遍历作为可选路径画出，由地址范围及上下文决定；不能画成所有访问无条件经过同一 walker。各 aperture 的实际编程与默认页处理见 [VM2](../../HUBS/sources/VM2-mmhub-v2.md)。

## 权限和异常

GPUVM 页表带 RWX 及其他属性，无效页面访问产生 GPU page fault。翻译成功除了得到地址，还需要保留权限、缓存和系统/本地属性。只记录 VA→PA 会遗漏后续访存选择所依赖的信息。

本资料没有说明每种 fault 都可恢复、自动 retry，或由同一中断源报告。fault 通知、页表修复、TLB 失效和原请求重发应拆开研究。与 [VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md)、[MG7](../../IH/sources/MG7-ih-core-consumer.md) 配合，才能说明软件如何观察和响应。

## 复用边界

可以据此建立 UTCL1/UTCL2 的输入身份与输出属性问题，但无法推出目标 UTCL2 缓存组织、walker 位置、VMID 全 F 的专用语义或 light/heavy 定义。要回答这些项目特定问题，优先看 [C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md)–[C04](../../UTCL2/sources/C04-translation-prefetch.md) 的适用范围及正式规范，不能用本注释补出隐藏机制。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
