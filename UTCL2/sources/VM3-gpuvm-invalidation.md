# VM3：GMC v9 的 GPUVM 失效：请求、ACK、hub 与电源状态

更新日期：2026-09-24。

导读：详细追踪 GPUVM invalidate 的软件发起与完成观察，包含 VMID/PASID 转换、不同 hub、KIQ 与直接寄存器路径及旧 ACK 风险。适合建立维护事务闭环。
来源：[gmc_v9_0.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c)。
阅读状态：精读 `get_invalidate_req`、`use_invalidate_semaphore`、`flush_gpu_tlb`、`flush_gpu_tlb_pasid`、`emit_flush_gpu_tlb`，以及 fault 状态输出定位；其他 GMC 功能未全文研究。

## 一个请求包含哪些选择

`get_invalidate_req` 组合 VMID 位图、FLUSH_TYPE、L1 PTE、L2 PTE 和多个 PDE cache 的失效使能；清 protection fault status/address 的字段设为 0。它把“哪个上下文”“清哪些翻译缓存”“用什么类型”分开编码。

FLUSH_TYPE 在这里由调用者传入；这个文件不能单独定义目标设计的 legacy/light/heavy 语义，更不能证明某个类型必然等待所有业务数据到达 DRAM。要写这种结论必须追溯对应 IP 规范。

## 从提交到确认

直接路径选择对应 hub 的 invalidate engine，持有软件锁；必要时读取 semaphore 直到取得，随后写请求，轮询 ACK 中该 VMID 的位，最后释放 semaphore 和锁。驱动使用 engine 17 的路径只是具体软件分配，ring 命令路径使用自己的 `vm_inv_eng`。

特定旧 GFXHUB 版本在写请求后执行 dummy read，避免快速 GRBM 接口下把前一轮尚未清除的 ACK 当作新 ACK。这个例子说明“ACK 已经为 1”必须关联到当前命令的生命周期；不能只看电平而忽略旧状态。

semaphore 的注释指出 power-gating 可能丢失 invalidate acknowledge 状态，因此需要阻止这段期间进入相关 gated 状态。是否启用它有 GC 版本、hub、VF 和 APU 条件，并非所有路径统一要求。

## 命令队列路径与 PASID

KIQ 等已准备好时可使用 firmware register write/wait helper，服务 SR-IOV/GFXOFF 等条件；早期初始化仍需直接路径。`emit_flush_gpu_tlb` 将页表根高低位、失效请求、等待 ACK 和 semaphore 操作写入 ring。软件完成“生成命令”不等于 GPU 已执行到等待点。

PASID 路径先读取 ATC VMID→PASID 映射，匹配有效项，然后按 `all_hub` 遍历启用 hub 或只处理指定 GFXHUB。PASID 本身不是直接作为本函数 VMID 位图写入的编号，匹配范围也不自动覆盖所有系统 IOMMU/设备 ATC。

## 失败、跨模块和复用

semaphore/ACK 超时被记录为错误，但部分函数返回 void，不能仅凭调用返回判定成功。后续 CF/SDMA 的完成链必须区分命令已发、GPUVM ACK 已观察、数据 cache 维护已完成、软件 fence 已通知四个事件。

与 [VM4](../../UTCL2/sources/VM4-amd-iommu-commands.md) 的 IOMMU command completion、[GC3](../../GC/sources/GC3-llvm-memory-model.md) 的 cache 可见性、[FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) 的 fence 组合研究时，先保留各自完成范围。本文不证明它们可任意互相替代，也不证明 reset 后旧请求自动消失。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
