# MG11：UMC 6.7：错误地址展开与 poison 模式的代际对照

更新日期：2026-09-24。

导读：补充 RSMU 相邻的 UMC RAS 路径，解释 hash/列位模糊如何扩大隔离候选，及 poison 查询如何依赖寄存器；用于对照 UMC 8.10。
来源：[Linux v6.12 umc_v6_7.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c)。
阅读状态：已读地址转换、直接/固件错误地址路径及 poison 查询；这不是 RSMU 内部实现证据。

## 地址不是直接 PA

转换先用错误 channel address、channel index 合成 8 KB block、256 B block 与块内 offset，再应用 channel hash。随后清除特定列位，遍历 C4/C3/C2 的组合，并对每个候选翻转 R14 再生成记录。这是本代际地址模糊的展开，不是“一次 UE 对应一个精确页面”。

输出记录数量不等于独立故障数量，也不保证最终所有候选都是不同软件页；页面粒度、去重和隔离结果要交给后续处理分析。不能把候选 PA 的变换泛化到任意 HBM 组织。

## 有效性与访问途径

所读地址分支检查 Val 与 UECC，没有采用 [MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) UMC 8.10 中同样的 AddrV 条件。直接寄存器读取后清除状态，固件 ECC 表分支则从已采集信息取地址。相同函数意图并不意味着完全相同的有效位语义。

poison 查询读取 instance0/channel0 的 UCFatalEn 并取反，以这个位置代表相应模式；UMC 8.10 因 host 不可访问而强制返回 true，含义明显不同。由此可见 API bool 可能是读取结果，也可能是驱动假设，必须追溯实现。

## 用于规划

RSMU 研究仅把这条路径作为受访问对象/系统 RAS 邻接材料。检测、状态采集、地址反解、隔离、poison 传播和恢复各有责任，不应全部归给 RSMU。[MG5](../../RSMU/sources/MG5-rsmu-umc-index.md) 才是直接命名寄存器线索；[MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) 是软件坏页状态。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
