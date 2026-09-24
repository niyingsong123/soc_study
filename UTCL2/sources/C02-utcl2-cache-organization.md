# C02：UTCL2 结构与使用：页表格式、cache 映射和 BigK 性能反例

更新日期：2026-09-24。

导读：解释 Group/VML2/Walker/ATC 的分工、PTE cache 的 bank/set/way/tag、表布局粒度与映射粒度的区别，并保存 BigK 增大反而禁止填充的具体案例。
来源：[仓库既有“UTCL2 结构和使用简介 by Wang Junmin”页图](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin)。HYGON 标识的用户资料；不是所有 AMD 产品通用参数。
阅读状态：读取 38 页文字并核看结构及第 34–35 页关键条件；本笔记保留原资料案例的配置前提，不把建议寄存器值写成可直接应用的优化命令。

## 先把三个“粒度”分开

第 3–7、25–29 页强调，软件生成表，硬件按寄存器和表项格式遍历。`PAGE_TABLE_BLOCK_SIZE` 参与页表布局；PDE0 中的 block-fragment 字段影响下一级表深度；PTE fragment 描述最终映射覆盖。它们共同影响寻址，但不是可以互换的三个页大小设置。一个表内可能重复填入描述同一较大映射的条目；内容覆盖大，不代表用于管理这些条目的 cache 自动扩大 tag 范围。

通常的四级、每级 9-bit 索引图只是特例。起始深度、虚拟区间和 block size 改变后，最高级有效索引宽度及最后一级表深度可能不同。计算表项物理地址应先明确地址单位，再做“该级基址 + 索引×8”；把 4K 页号直接当字节地址会同时破坏 tag 和 walker 请求地址。

## 四部分微架构

Group 聚合客户端、做 APT1/2/3 决策、保留来源身份并仲裁返回；VML2 查询 PTE cache 和检查表项；Walker 为 miss 遍历 PDE/PTE，并管理取表与填充；ATC 面向另一个翻译服务域，与 ATHUB 通信。第 12–16 页中入口 FIFO、返程 FIFO、credit 和 per-request 状态都显式存在。因此性能可分别受入口冲突、cache bank、walker 状态、外部取表、返回仲裁约束，不能把所有等待都计为“TLB miss latency”。

资料的 GC/MMHUB QoS 配置存在差异，例如 non-RT/soft-RT 在 BigK cache 中是否区分；应按实例归属研究，不能把相近模块名当成同配置复用。

## PTE cache：空间容量与并行度不是一回事

第 17–24 页按 bank → set → way/tag 解释读取。line 含 8 个 PTE，line 的管理范围与 `Cache_Fragment_Size+3` 有关；set hash 可混入地址片段与 VMID，bank 由另组选定位决定；同一 set 内采用该资料所述的 2-way LRU，并描述读写同 set 时的更新优先关系。

在资料配置中，bank 选择位通常放在 line 覆盖范围以上，即建议的 bank shift 与 BigK+3 相配。否则同一逻辑 line 的映射关系可能失去预期。bank 的价值是并行处理不同 bank 的请求，增加 bank 数不会自动消除多个客户端同时访问同一 bank 的冲突。评估必须看短时间窗口的 bank 分布、set 冲突和有效 fill，而不只看总 entry 数。

Walker 的 PDE cache 又用取表地址及属性标识条目，与 VML2 的虚拟地址/上下文组织不同。中间表命中减少取表流量，不能等同于最终 PTE 命中，也不能把不同级的 hit count 相加当 TLB hit rate。

## 保存一个容易被“扩大页”直觉误导的案例

第 30–35 页给定四级表、block size=0、PDE0-as-PTE、最终 fragment=9。BigK=6 时，VML2 line 管理范围为 2^(12+6+3)=2 MiB；其后端 PDE0 line 的内容可描述更大空间。部分地址仍进入 walker，而特定 debug 设置会影响 PDE-as-PTE 的缓存命中处理。

把 BigK 提到 9 后，名义 VML2 line 范围成为 16 MiB，性能却可能更差。第 34 页给出的本实现填充条件为 `Type×9 + PAGE_TABLE_BLOCK_SIZE >= BigK+3`。案例 Type=1、block size=0，只有 BigK≤6 满足；BigK=9 时结果仍可返回 UTCL1，却不填入 VML2。于是“翻译正确”与“缓存有效工作”完全可以分离。

这是特定实现的填充条件，不能提升成所有 MMU 必须遵守的通用包含性定理。也不能从名义覆盖容量直接推实际有效容量：hash、way 冲突、工作集、上下文、PDE-as-PTE、填充许可和 debug 配置都影响结果。

## 方案建议的边界与复用

第 37–38 页讨论改变表层级、block size、BigK、禁用 PDE-as-PTE 或调整 debug 控制；这些建议都依赖驱动页表生成与硬件格式匹配，有地址翻译错误风险，不能直接作为生产调参操作。后续应比较相同地址轨迹下的 VML2 lookup/hit/fill、各级 PDE hit、walker 取表数、bank 冲突和总完成延迟，并说明性能改善由哪一资源变化带来。

可复用到 [C04](../../UTCL2/sources/C04-translation-prefetch.md) 的预取研究：先排除配置导致不 fill，再评价预取收益。可复用到 [VM5](../../UTCL2/sources/VM5-mask-paper.md) 的共享翻译研究：总容量、可用并行度、有效插入率、隔离公平性应分别讨论。精确 hash 和容量应回查目标版本图表/RTL，勿把本资料与 [C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md) 的不同 cache 参数合并。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
