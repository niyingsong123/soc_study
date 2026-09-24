# MG5：RSMU 寄存器线索与 UMC 6.1 访问模式

更新日期：2026-09-24。

导读：这是 RSMU 最直接的公开接口证据：UMC index mode 及错误采集前后的状态切换。适合建立职责边界，不能据少量寄存器推定完整 RAS 控制器。
来源：[rsmu_0_0_2_offset.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h)、[sh_mask.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h)、[umc_v6_1.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c)，Linux v6.12。
阅读状态：已读两个短寄存器头及 UMC index enable/disable/state、RAS count 调用序列；不声明读到 RSMU 完整功能规格。

## 直接证据

公开头给出 RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU，含 WREN、INSTANCE、MODE_EN 字段。UMC 6.1 代码通过 PCIe 间接访问读改写 MODE_EN，并提供查询当前状态的函数。这能确认一个 UMC 寄存器访问模式控制接口，不能单独确定 WREN 全部行为或 RSMU 内部实现。

错误计数路径保存原 index mode，必要时关闭，按 UMC/channel 遍历采集，随后恢复原模式。ARCTURUS 分支还暂时禁止 DF C-state，结束后重新允许；失败仅记录告警的分支也应注意，不能声称访问可达性已严格保证。

## 三种责任不要混合

RSMU 接口的访问模式、UMC 的 ECC 检测/状态、SMU/驱动的电源与恢复策略是不同证据层。文件位于 rsmu/、函数涉及 RAS，并不能推出 RSMU 就是“Reliability SMU”。本地参考 C05 有 remote SMU 的名称线索，仍需确认与目标模块和公开寄存器是否同一含义。

## 接续研究

以“谁通过什么入口访问哪个 UMC 实例，访问前后需保留什么状态”建立第一版结构。再查是否有远程命令、权限、地址路由和响应通道证据；没有就保持未知，不先画大型 RAS 管理器。[MG11](../../RSMU/sources/MG11-umc67-ras-comparison.md)/[MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) 提供 UMC 错误处理对照，但不应自动归属于 RSMU 内部。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
