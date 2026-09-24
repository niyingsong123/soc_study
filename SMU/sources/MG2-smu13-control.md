# MG2：SMU 13 公共控制：固件就绪、表地址和频率约束

更新日期：2026-09-24。

导读：连接 SMU 初始化、固件接口、频率上下界和事件处理；适合研究管理状态机，避免把设置频率边界等同于即时完成变频。
来源：[Linux v6.12 smu_v13_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0.c)。
阅读状态：已读固件状态/版本、表地址、allowed mask、软硬频率范围、PPT 功耗上限、reset event 和 IRQ 相关段；未通读全部板级/风扇/显示策略。

## 初始化的多个条件

check_fw_status 根据 IP 版本选择 MP1 firmware flags，检查中断已使能状态；该返回值不代表所有管理 feature 已准备好。check_fw_version 分解固件版本并比较 driver interface，所读代码对不匹配记录信息而不一概终止；这种兼容策略不能推广成任意二进制表都可混用。

driver/tool table 的 MC 地址通过高低两条消息发布，高部分失败时不继续低部分。feature allowed mask 也分高低发送。多消息更新可能中途失败，因此方案需要写清恢复/重建和部分更新问题，不能把软件一次函数调用当硬件原子事务。

## 频率控制是什么操作

软/硬上下界接口先判断对应 clock DPM 是否使能，再将逻辑 clock ID 转为 ASIC ID，与频率值打包发消息。未使能 DPM 时某些接口直接成功返回；max 和 min 分开设置，后一步失败不能证明前一步没生效。

这些操作修改约束或策略输入，不是本源给出的完整电压/PLL/训练切换序列。实际频率、平均频率和请求值要另取观测，见 [MG3](../../SMU/sources/MG3-smu13-firmware-abi.md)/[MG9](../../SMU/sources/MG9-thermal-power-observability.md)；UMC/PHY 变频前的排空和重训责任仍需目标文档。

## 功耗上限的能力与状态更新

`set_power_limit` 仅接受 `SMU_DEFAULT_PPT_LIMIT` 类型，否则返回 `EINVAL`；还要求 PPT feature 已使能，否则返回 `EOPNOTSUPP`。通过检查后发送 `SetPptLimit` 消息，失败就退出，成功后才更新软件记录 `current_power_limit`。因此应分别保留“支持该类型”“feature 已使能”“消息返回成功”“软件缓存更新”四个条件。

`current_power_limit` 是软件记录的限制值，不是实测功耗，也不证明固件已经完成某次电压/频率过渡。底层消息 API 在特定上下文可能跳过硬件操作，须结合 [MG1](../../SMU/sources/MG1-smu-message-table.md) 的条件判断解释成功返回。

## 管理事件与恢复

SMU reset complete 的等待接口通过特定 recovery 消息实现。IRQ 分支按 THM、ROM_SMUIO、MP1 等来源区分温度事件和 SMCToHost 通知；MP1 先 ACK，再按上下文处理 AC/DC、节流等，严重温度故障可触发系统关机。不是所有管理事件都能简化成同一个完成 bit。

后续应把策略、执行者、反馈和保护动作分开，记录每项状态由 driver、firmware 还是本地硬件拥有。该代码是 SMU13 公共软件层，不代表所有 AMD 芯片的相同电源拓扑。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
