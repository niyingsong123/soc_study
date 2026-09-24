# MG10：AMD ATL system.c：Fabric 身份字段与版本发现

更新日期：2026-09-24。

导读：解释 socket/die/node/component ID 的代际解码和未知版本处理；适合控制寻址与错误地址定位的前置研究，不能用固定移位套所有芯片。
来源：[Linux v6.12 drivers/ras/amd/atl/system.c](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/system.c)。
阅读状态：已读 node ID 构造、DF2/3/3.5/4 mask/shift、版本发现及系统配置采集；这是 CPU DF/ATL 软件上下文，不是 GPU SMN 路由表。

## 身份解码依赖系统配置

socket_id 与 die_id 分别移位、掩码后组合成 node_id；若配置不支持某身份位而调用者给出非零值，函数返回错误。分步运算还避免越界移位。身份不是按目录编号或 die 数量简单拼接。

不同 DF 代际从不同字段取得 component/node/socket/die 的 mask 和 shift，DF4 有特定 quirk；部分字段还要统一移到 node_id 所在位置。研究地址映射时须先保留这些系统参数，再讨论 interleave/normalized address。

## 版本发现与缺口

较新系统从 FabricBlockInstanceCount 中读取版本，较老 read-as-zero 走 legacy 识别；此固定版本拒绝未明确支持的 major revision，而不是用最近一代格式猜测。系统配置还包括 coherent station map 数和 DRAM hole 等。

版本识别失败和部分辅助字段读取告警有不同错误策略，不能把一个总入口成功等同于所有硬件信息都经过同级验证。

## 复用方式

与 [FAB3](../../DF/sources/FAB3-atl-address-core.md)/[FAB6](../../DF/sources/FAB6-atl-denormalization.md) 联读，可把“先发现系统组织，再做地址反解”的依赖写入 DF/UMC 方案；与 [MG4](../../SMN/sources/MG4-smn-indirect-access.md) 联读可提醒 SMN 访问的 node 参数也有平台语境。本源不说明目标 GPU 的 SMN 包格式或 RSMU 拓扑，行业术语互通应保留这条边界。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
