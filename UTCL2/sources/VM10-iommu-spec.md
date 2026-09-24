# VM10：AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约

更新日期：2026-09-24。

导读：用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。
来源：[AMD 文档 48882 rev.3.09，2023-10，实际读取的 AMD 原文镜像](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf)；[AMD 原入口](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/specifications/48882_IOMMU.pdf)本次返回 404。镜像只作为原文取得渠道，不作为文档作者。
阅读状态：已取得完整 303 页 PDF；重点核读 §1.3、§2.1–2.2、§2.4.1–2.4.4、§2.4.11、§2.5；本笔记不是整本规范的逐字段替代品。

## 微架构位置与术语

系统 IOMMU 从设备身份查 Device Table，再按 domain / PASID 和相应模式完成地址翻译与保护。支持 ATS 的设备可把翻译缓存在自己的 IOTLB/ATC 中。因此至少有页表内存、IOMMU 的设备/页目录/页翻译缓存、设备端 ATC 三类状态。UTCL2 的 VML2 与 ATCL2 可以借这套分工理解，但 GPUVM 的 VMID、IOMMU DomainID、PASID、PCIe DeviceID 不是同一个编号，也不能把规范中的系统 IOMMU 等同于整个 UTCL2。

嵌套翻译还要分 GVA、GPA、SPA：失效命令的 GN 控制地址解释及作用域。规范 §2.4.3 明确，GN=0 的 nested 失效可能要求清掉域内全部 guest 翻译；不能只凭 VA 数值相等决定命中失效。PDE 位还决定是否涉及中间页目录缓存，修改上层表项后只清最终 PTE 缓存可能不够。

## 命令、资源和完成点

命令缓冲区是软件生产、IOMMU 消费的环；取走命令不等于执行完成。实现允许并行处理独立命令，必须另外满足规范列出的依赖：先前 Device Table 失效要先于相关 IOMMU page/interrupt-table 失效；设备 IOTLB 失效又要等待先前 Device Table 和 IOMMU page 失效。否则设备可能刚清掉旧映射，又从仍旧的上游缓存重新取得它。

`INVALIDATE_DEVTAB_ENTRY` 不代替 domain 翻译失效。更新页表通常先发 `INVALIDATE_IOMMU_PAGES`，再对有远端缓存的设备发 `INVALIDATE_IOTLB_PAGES`。后者的 DeviceID 是目标功能，QueueID 则是共享失效队列的流控身份；多个 VF 可共用一个队列，按 VF 各自限制 outstanding 仍可能把物理队列压满。Maxpend 必须结合设备能力，不能取任意固定值。

远端命令的 Type 在本版本中可表示标准 ATS 失效、只失效地址范围而不 flush 依赖事务、以及失效该范围并 flush 全部 outstanding 事务。增强类型有能力位条件；其设备传输机制并非本规范完整定义。不要把它与本项目图示的 VM flush-type 数字直接一一对应。

`COMPLETION_WAIT` 等待自前一 Completion Wait 以来较老命令完成；其 `f` 位进一步限制后续命令是否可以提前启动。`s` 可在系统内存写入完成值，`i` 可产生完成中断；两者可同时启用。完成写要求一致性语义，并有通道与属性限制。它不是任意请求后面的通用“全系统清空”指令，效果依赖前面的失效命令及其作用域。

§2.4.11 把完成约束延伸到依赖旧翻译的在途 DMA：匹配的读要收到响应；已翻译的写要推进到规定的 host-bridge 边界，并按通道/多流条件使用 Fence、Flush，等待相应 Flush response。由此，页面回收流程是“页表撤销 → 适当缓存失效 → 等待其完成”，不能在清掉一个 valid 位后立即复用物理页。此结论有规范前提；非 flush 增强类型不能被不加区分地套入强完成结论。

## 错误与前进性

非法命令或 command hardware error 可停止命令处理，而翻译等其他活动仍可能继续。恢复需观察 CmdBufRun，禁用后修正环与指针，再重新启用。命令超时应区分命令未取、远端队列无 credit、设备未回 completion 和事件通路故障。

事件日志也是有容量的环；满时有 overflow 状态，部分硬件事件还依靠 MMIO 状态寄存器报告。不能以“没有日志记录”推出“没有异常”，也不能将 IH 消费事件当作旧 DMA 已全部退出的证据。

## 可复用研究问题

为每种失效建立矩阵：触发者、身份键、地址范围、PTE/PDE/ATC 对象、在途翻译的处理、读写 drain 条件、确认接收者、超时恢复。与 [VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md)、[VM4](../../UTCL2/sources/VM4-amd-iommu-commands.md) 的软件实现，[C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md)/[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 的 GPU 图示，[IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) 的 ATS/PRI/PASID 能力管理一起使用。精确的虚拟化、PRI、interrupt-remapping 位域仍需回到相应规范章节，不由本笔记推测。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
