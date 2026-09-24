# VM2：MMHUB 2.x 的地址范围、翻译缓存与 fault 配置

更新日期：2026-09-24。

导读：按初始化顺序整理 MMHUB 软件可见的服务结构：页表根、aperture、TLB/cache、VM context、失效引擎和 fault。适合构建 hub 控制面；不证明完整内部数据网络。
来源：[mmhub_v2_0.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c)。
阅读状态：精读 page-table/aperture、TLB/cache、VMID config、invalidation、gart enable/disable 与 fault decode；时钟门控的全部分支未逐项展开。

## 初始化揭示的功能分工

`gart_enable` 依次设置 GART 页表根及有效范围、系统 aperture、L1 TLB、VM L2 cache，启用 system domain，关闭不使用的 identity aperture，设置用户 VM context，最后配置失效引擎范围。顺序为控制前置提供线索，不意味着一次数据请求依次通过这些寄存器块。

页表根分高低寄存器按 VMID 寻址；GART start/end 按页粒度编码，system aperture 又有自己的地址单位。研究字段时必须带上移位和单位，不能把两个寄存器中的同一整数当成相同字节地址。默认页使用经过转换的 scratch 地址，用于特定错误/缺省行为；不能把它视作正常映射修复。

## 缓存与上下文

`init_tlb_regs` 设置 L1 TLB enable、system access、advanced driver model、MTYPE 等。`init_cache_regs` 设置 MMVM L2、PDE/PTE 相关策略及失效位；这里的 L2 是翻译体系的 cache，不能当成 GL2 数据缓存。

`translate_further` 影响 BANK_SELECT 和 big-fragment 配置，说明组织/页大小选择存在条件，但单个寄存器值不能推出完整 bank 数量与 hash。VF 无权设置的一部分寄存器由 PF 配置，研究虚拟化时应记录谁拥有状态，而不是让 VF 重复整个初始化。

用户 context 配置页表深度、block size、最大页范围和多种保护行为。`RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` 与 `noretry` 相关；代码注释将 no-retry XNACK 与抑制 fault storm 联系起来。由此可知“出现 fault 后继续重试”是条件行为，不能默认对所有访问开放。

## 失效与错误返回

失效请求选择 VMID，并设置 L1 PTE、L2 PTE、PDE0/1/2 等对象；fault 地址状态清除是另一字段，未被本函数自动开启。18 个引擎的范围编程是此版本的事实，不推广成目标 UTCL2 的所有接口数量。

fault status 带 CID、RW、walker error、permission、mapping 和 more-faults 等维度。CID 名称还取决于 MMHUB 2.0/2.1 的具体版本和读写方向。仅看到相同 CID 数字，不能跨版本认定相同客户；more-faults 提醒单条报告可能不能表达整个故障集合。

## 与其他资料的关系

[VM12](../../HUBS/sources/VM12-gfxhub-v2.md) 提供同版本 GFXHUB 控制面的对照；[VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md) 提供运行时 invalidate 的请求—ACK；[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 提供仓库原有 MMHUB 教学页面。它们需要先核对产品再对应。CH 的完整身份和与 MMHUB 的连线仍不能由此确定。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
