# IO11：PCI ATS/PRI/PASID：能力、额度与 PF/VF 共享

更新日期：2026-09-24。

导读：用于区分 ATS 缓存翻译、PRI 请求资源和 PASID 身份能力，重点是配置依赖、PF/VF 共享及队列深度编码；适合 IOMMU 与 PCIe 联读。
来源：[Linux v6.12 drivers/pci/ats.c](https://github.com/torvalds/linux/blob/v6.12/drivers/pci/ats.c)。
阅读状态：已读 ATS、PRI、PASID enable/disable/restore、能力和额度处理；未读完整 PCIe 扩展规范或设备内部状态机。

## 能力存在不等于可以使用

ATS 是否可用同时检查能力项及设备信任条件。STU/page shift 有最小要求，VF 与 PF 的相关配置必须一致；恢复函数也只有在软件记录为 enabled 时才重写状态。枚举到 capability 只是第一步，不能直接认为功能正在参与翻译。

ATS invalidation queue depth 的硬件编码零代表最大 32，而本 API 返回零可表示 VF 共享队列。必须区分寄存器编码、解码后的容量和共享关系；将返回零解释成“不支持任何 invalidate”会错误建模背压。

## PRI 额度和状态

PRI enable 要在 stopped 状态下进行，申请 outstanding 数被硬件 max 限制，再写入 allocation。VF 不独立实现该能力，而共享 PF 配置；复位前要求先 disable。额度、使能和停止是不同状态，不能认为把 enable 清零就自动完成全部在途请求的收尾。

PASID enable 检查路径能力及所请求 EXEC/PRIV feature 是否支持，VF 共享 PF 的配置；最大 PASID 数由能力字段解码。身份数量与同时在途翻译数、TLB 项数是不同资源。

## 对翻译主线的价值

研究 GPUVM 与 IOMMU 时分别记录设备身份、PASID、缓存翻译、失效队列和缺页请求；不要用 UTCL2=MMU 的功能类比把它们合并。[VM10](../../UTCL2/sources/VM10-iommu-spec.md)/[VM4](../../UTCL2/sources/VM4-amd-iommu-commands.md) 解释 AMD IOMMU 一侧，[C03](../../UTCL2/sources/C03-utcl2-topology.md) 给本地参考的分路径结构。此文件证明软件配置逻辑，不证明目标 UTCL2 实现 ATS/PRI 的每一种模式。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
