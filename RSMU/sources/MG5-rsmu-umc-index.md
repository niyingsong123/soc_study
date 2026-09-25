# MG5：RSMU 寄存器线索与 UMC 6.1 访问模式

更新日期：2026-09-25。

导读：用 AMD 作者提交确认 remote SMU 名称及寄存器接口/错误/复位职责，配合 UMC index-mode 保存恢复与 BOWEN 参考位置；目标实例/内部实现仍未知。
来源：[rsmu_0_0_2_offset.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_offset.h)、[sh_mask.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/include/asic_reg/rsmu/rsmu_0_0_2_sh_mask.h)、[umc_v6_1.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c)，Linux v6.12。
阅读状态：已读 AMD 原始提交 245219a、两份 v0.0.2 头及 Linux v6.12 UMC index/RAS 调用；不声明取得完整 RSMU 规格。

## 直接证据

公开头给出 RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU，含 WREN、INSTANCE、MODE_EN 字段。UMC 6.1 代码通过 PCIe 间接访问读改写 MODE_EN，并提供查询当前状态的函数。这能确认一个 UMC 寄存器访问模式控制接口，不能单独确定 WREN 全部行为或 RSMU 内部实现。

错误计数路径保存原 index mode，必要时关闭，按 UMC/channel 遍历采集，随后恢复原模式。ARCTURUS 分支还暂时禁止 DF C-state，结束后重新允许；失败仅记录告警的分支也应注意，不能声称访问可达性已严格保证。

## 三种责任不要混合

RSMU 接口的访问模式、UMC 的 ECC 检测/状态、SMU/驱动的电源与恢复策略是不同证据层。文件位于 rsmu/、函数涉及 RAS，并不能推出 RSMU 就是“Reliability SMU”。AMD 原始提交明确使用 remote SMU，见下节；仍需确认目标芯片的具体实例和接口，不能只凭同名映射所有代际。

## 接续研究

以“谁通过什么入口访问哪个 UMC 实例，访问前后需保留什么状态”建立第一版结构。再查是否有远程命令、权限、地址路由和响应通道证据；没有就保持未知，不先画大型 RAS 管理器。[MG11](../../RSMU/sources/MG11-umc67-ras-comparison.md)/[MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) 提供 UMC 错误处理对照，但不应自动归属于 RSMU 内部。

## AMD 作者的名称与职责证据

补充原始来源：[Linux 提交 245219a](https://github.com/torvalds/linux/commit/245219a66085332a30e4653db3542ea5654ff762)，作者 Hawking Zhang，2019-07-24，2019-07-31 合入。已核读完整提交说明和两个新增头文件。作者将 rsmu 展开为 **remote smu**，并列出 IP 寄存器接口、错误处理、复位生成等职责。这比根据缩写猜测可靠，后续可以使用 remote SMU 扩大检索；但该简短说明没有给内部数据通路、指令集、mailbox 或处理器实现。

| 公开 v0.0.2 编码 | 可以确认的事实 | 不能据此推导 |
| --- | --- | --- |
| offset `0x0d91`、BASE_IDX=0 | 符号 `RSMU_UMC_INDEX_REGISTER_NBIF_VG20_GPU` 的寄存器索引定义 | 不能脱离访问宏直接当 CPU 字节地址 |
| WREN：shift 0、mask `0x0000ffff` | 16-bit 字段的编码范围 | 每一位的写入动作/广播语义 |
| INSTANCE：shift 16、mask `0x000f0000` | 4-bit 实例选择字段的编码 | 目标实际具有 16 个实例 |
| MODE_EN：shift 31、mask `0x80000000` | 驱动切换的模式位位置 | 模式内完整译码与并发协议 |

因此第一版微架构骨架可由“管理访问入口→IP 寄存器接口/选择状态→端点寄存器”展开，同时将错误和复位列为作者确认的职责方向；每项具体队列、时序、权限和响应仍需要对应版本证据。

[C01 第 4 页](../../UTCL2/sources/C01-mm-utcl2-testbench.md) 的 BOWEN 参考图中，SMN 分别接入两组 MMHUB 的 rsmu，旁边还有 PCTL 与 rdft。这支持参考设计的连接位置，不是 AMD 目标的实例表。将这一页、AMD 提交说明、UMC 驱动调用分三层记录：名称/职责、参考拓扑、可观察访问序列，不能拼成已经确认的单一芯片实现。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
