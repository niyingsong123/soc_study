# VM10：AMD IOMMU 3.09：翻译、远端 ATC 与失效完成契约

更新日期：2026-09-25。

导读：用规范区分 IOMMU 内部缓存、设备 ATC、页表更新与在途 DMA；重点解释失效命令的依赖、Completion Wait、QueueID 流控和安全回收页面的条件。
来源：[AMD 文档 48882 rev.3.09，2023-10，实际读取的 AMD 原文镜像](https://kib.kiev.ua/x86docs/AMD/IOMMU/48882-3.09.pdf)；[AMD 原入口](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/specifications/48882_IOMMU.pdf)本次返回 404。镜像只作为原文取得渠道，不作为文档作者。
阅读状态：已取得完整 303 页 PDF；重点核读 §1.3、§2.1–2.2、§2.4.1–2.4.4、§2.4.11、§2.5；本次补核 §2.2.6–2.2.7.1、§2.4.7、§2.6 的 guest/nested 与 PRI/PPR 主线；本笔记不是整本规范的逐字段替代品。

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

为每种失效建立矩阵：触发者、身份键、地址范围、PTE/PDE/ATC 对象、在途翻译的处理、读写 drain 条件、确认接收者、超时恢复。与 [VM3](../../UTCL2/sources/VM3-gpuvm-invalidation.md)、[VM4](../../UTCL2/sources/VM4-amd-iommu-commands.md) 的软件实现，[C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md)/[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 的 GPU 图示，[IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) 的 ATS/PRI/PASID 能力管理一起使用。虚拟化与 PRI/PPR 的相关细节补在下文；interrupt-remapping 全部位域仍按实际研究范围另查。

## §2.2.6–2.2.7：PASID、GCR3 与嵌套 walk

Guest translation 同时受实现能力 GTSup/GLXSup、全局 GTEn 与 DTE 的 GV/GLX 控制；带 PASID 并不自动开启两级翻译。DeviceID 选 DTE，PASID 查 GCR3 表，GCR3 再给 guest 页表根；guest 表项里的 GPA 还可能需要 nested host 表翻成 SPA。DTE 的 GCR3 root 可按 GCR3TRPMode 解释为 SPA 或 GPA，后者要求相应能力位，不能默认所有表根都在同一种物理空间。

一层 GCR3 表的 4 KB 页按 PASID[8:0] 索引，高位在该模式中被忽略；软件必须使 PASID 分配与支持的表深匹配，不能只按 TLP 的字段宽度推导可独立寻址的进程数。改写 GCR3 表**不会自动清 IOMMU TLB**，仍需执行相应失效。NX、U/S 的检查取决于支持位及控制设置，并且上级 guest 表项的禁止权限不能被叶子放宽。

| 配置方向 | 主要控制关系 | 研究含义 |
| --- | --- | --- |
| 关闭翻译 | DTE[V]=0 | upstream 不作翻译/访问检查；ATS/PRI 请求失败，不能把它当正常 ATS 直通模式 |
| nested only | V=1、GV=0 | GPA→SPA；可按能力启用 ATS/PRI |
| guest only | V=1、GV=1、Mode=0 | GVA→GPA，nested 为直通，GPA=SPA；仍需 guest 支持及全局使能 |
| guest+nested | V=1、GV=1，并配置两套表 | GVA→SPA；中间 guest 页表读取也消耗 nested 翻译资源 |

§2.2.6.8 Figure 40 展示了上述“walk 中还有 walk”：图画出五层 guest、四层 nested 的 4 KB 示例，包含取 guest 表项及最终 GPA 转 SPA 共 29 个编号访问步骤；这不是任何请求必定发出 29 次 DRAM 读。cache hit、大页、skip-level 会缩短路径，且 GCR3 查表等资源还要按场景另算。相邻说明文字仍写“四层”，与本版图中 GL5 不一致，保留版本内差异，不能由此编出统一固定层数。UTCL2 研究应按 cache 类别和层级列资源占用，避免把所有 miss 都折成一笔固定延迟。

## §2.6：PRI 如何成为软件可处理的 PPR

ATS 查询已有映射，PRI 请求软件服务页面，二者不是同一个失败重试信号。支持 PPR 的 IOMMU 将 PRI 转成系统内存中的 **128-bit PPR 环记录**，软件通过推进 head 表示取走记录，处理完再发 COMPLETE_PPR_REQUEST；“消费日志槽”与“完成页面服务”是两个事件。

PPR log 基址按 4 KB 对齐，容量为 4 KB 的倍数，最大 32768 项/512 KB；head=tail 表示空，保留一个空槽判满。基础模式溢出设置 PprOverflow、丢弃新请求并停止记录；软件需腾空间或调整缓冲后按规定重启。不能从没看到一条 PPR 推断设备没发请求，也不能把关闭 PPRLogEn 当作完成在途页面请求；停止单个设备发 PRI 还需控制设备自身。

PAGE_SERVICE_REQUEST 记录保存 DeviceID、PASID、GN、页地址、权限和 PPRtag。GN=1 时地址为 GVA 且 PASID 有效；GN=0 时地址为 GPA，软件忽略 PASID。地址低 12 位不记录，按 4 KB 页定位。PPRtag[9] 是 PRI L 位，低 9 位是 Page Request Group index；日志中的每个 page 请求与最终 group 响应不能简单一一等同。

## §2.4.7：完成响应的关联字段

COMPLETE_PPR_REQUEST 要求 PPRSup，否则是非法命令。软件填回原 DeviceID、group index、适用的 PASID/GN 与响应码；CompletionTag[15:12] 为 PRI response code，[11:9] 必须为零，[8:0] 为原 group index。IOMMU **不校验软件填的 CompletionTag 是否正确**，所以这个字段必须与保留的请求身份关联，不能用新分配的任意 tag 代替。

GVA 服务用 GN=1，响应带 PASID prefix；GPA 服务用 GN=0，忽略 PASID、不带该 prefix。操作序列应拆成“身份校验/页面服务→所需页表及缓存维护→group 响应→设备后续访问”，不能把 PPR completion 当旧 DMA 的强 drain，也不能假定硬件已经替软件补页或恢复全部 fault。

## 溢出保护具有能力和组合限制

§2.6.1/2.6.4 的 dual log 支持等级区分无双缓冲、有双缓冲无自动切换、以及支持 autoswap；启用不支持的 autoswap 是错误。auto-response、early-overflow warning 和 always-on 是另外的机制，不能默认与所有模式任意叠加。

启用自动响应且达到限制时，对 L=1 的组结尾请求产生响应，其他 L=0 请求可以被丢弃；默认自动响应码为 successful，可由软件配置。这个 successful **不证明缺失的页面已经被处理**，它是已配置的溢出应对行为。auto-response 与 early warning 在本版都不适用于 autoswap 模式；always-on 还要求先启用 auto-response。软件动态搬迁/调整 log 时规范建议使用 always-on，但这不是无限缓冲或无丢失保证。

后续微架构研究可据此区分四类容量：设备 pending PRI groups、IOMMU PPR log、软件未完成服务队列、命令完成队列。分别记录满时动作和恢复责任，才能连接 [IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) 的设备能力管理与 IH 的通知路径。以上补核不包括 interrupt-remapping/SEV-SNP 全部字段，也不证明目标 GPU 的 ATCL2 与该系统 IOMMU 具有同样内部实现。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
