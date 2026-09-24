# MEM14：UMC 8.10 驱动：错误分类与地址候选展开

更新日期：2026-09-24。

导读：研究错误地址为何不是现成系统物理地址，以及 UE 计数为何可能没有可隔离页面；提供具体寄存器与转换路径，适合 RAS 联读。
来源：[Linux v6.12 umc_v8_10.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c)。
阅读状态：已读错误计数、通道索引、地址转换、状态清除及固件 ECC 信息分支；未读取目标芯片寄存器，不能推广到其他 UMC 代际。

## 计数与地址有效性不同

直接寄存器路径将 Val 与 CECC 组合判断 CE；UE 分类还可由 Deferred、UECC、PCC、UC、TCC 等条件触发。这里只按一次状态检查累加，并不自动等于硬件发生事件的精确次数。

地址转换要求 Val、AddrV、UECC 同时满足。故计入 UE 的状态未必进入错误地址处理。没有地址缓冲时可以清除状态后返回，状态为零则直接退出；研究采集时必须注意读取、清除和保存记录的顺序。

## Normalized address 到系统地址

代码按 node/UMC/channel 定位寄存器，另用通道索引表获得地址映射所需 channel index。先依据 AddrLsb 去掉无效低位，再清除特定列位并枚举 C6/C5 的四种可能；每种 normalized address 通过 swizzle 映射得到候选系统物理地址，生成错误记录。

这说明原始错误状态可能只能定位一个地址集合，页面隔离不能假设一条错误只对应一个确定 byte。通道数对应不同列位选择；无法识别的通道组织返回错误，而不是继续给出看似合法的 PA。具体宏和映射只适用于此代际。

## 访问路径与不可见状态

另一分支从 RAS 上下文中的固件 ECC 信息表读 CE count、MCA status/address，再调用同样地址转换。这与 host 直接读寄存器不是同一种采集路径。`query_ras_poison_mode` 因 host 无法访问相应控制寄存器而强制返回 true；不能把这个软件返回值解释为实际读到了 poison 配置。

## 复用要点

UMC/RSMU/SMU/IH 联合研究应保存：错误来源、有效位、位置粒度、地址转换规则、候选数量、状态清除点、隔离是否成功。[MEM3](../../UMC/sources/MEM3-amdgpu-ras.md) 的 R/P/F 状态是后续处置结果，不能与这里的错误地址有效性合并。[MG11](../../RSMU/sources/MG11-umc67-ras-comparison.md) 可用于比较另一 UMC 代际，避免用一个函数概括整个 AMD RAS。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
