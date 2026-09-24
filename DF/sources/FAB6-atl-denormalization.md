# FAB6：AMD ATL denormalize：非二次幂通道与 hash 的逆向重建

更新日期：2026-09-24。

导读：解释 3/5 倍通道模式为何不能靠插入几位 channel ID 还原 PA，以及 DF4.5 如何枚举丢失位和余数，再用正向映射与 CS 身份校验候选地址。
来源：[Linux v6.12 AMD ATL denormalize.c](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/denormalize.c)。
阅读状态：已读模式分派、DF4/DF4.5 非二次幂路径及 candidate verification；大量具体位段仅在本版本代码中有效，本笔记不逐个复制。

## 为什么 normalized address 丢了信息

interleave 将一个系统物理地址拆成目标通道/CS 与通道内部地址。二次幂方案常可理解为抽出若干位；3、5、6、10、12、24 等模式还涉及除法、余数与 hash。归一化后某些位以及除法余数不再保留，只给 normalized address 无法唯一反解。

算法需要来源 coherent station、map 的目标 fabric ID、channel 模式和 hash controls。与 [FAB3](../../DF/sources/FAB3-atl-address-core.md) 一样，它不是页表 MMU，也不能由公式名推测硬件在请求关键路径上做了相同的软件枚举。

## DF4.5 路径的重建办法

初始化按 1K/2K 与 NPS/channel 模式确定直接保留的地址位、被除的高位、mod_value、需枚举的位数与 rehash_vector。对每个可能余数及丢失位组合构建候选 denormalized address，恢复 base/MMIO hole 后重算相应 hash 位。

候选需通过两个检查：计算出的 logical coherent-station fabric ID 等于来源目标；去除 base/hole 后再 normalize，应还原输入地址。仅满足地址相等而目标 CS 不符仍不合法。代码还定义多候选时的选择方式，不能自行删去这一步或假设一定只有一个候选。

hash 位可结合不同高地址位和开关，例如 64K、2M、1G、1T。改变 map 或 hash 开关会改变相同 normalized address 的解释。部分中间运算用带 base/hole 的 SPA，另一些用不带它们的地址，必须保留函数间的语义边界。

## 可复用的研究方法

地址映射方案必须同时给正向与逆向不变量：`decode(encode(address, config), source, config)` 能否回到原地址，以及是否回到原目标。设计校验场景应覆盖非二次幂通道、MMIO hole 边界、map limit、hash 开关和未知配置；不必在规划阶段写出全部位公式。

本资料增加了 DF/UMC/RAS 的研究精度：需要保留 source 实例和配置快照，不能只存一个“错误地址”。精确目标公式应使用对应 revision 的路径，不能把 DF4.5 的位段应用于 GPU DF3.6。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
