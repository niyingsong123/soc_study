# FAB3：AMD ATL：从 UMC 归一化地址恢复系统物理地址

更新日期：2026-09-24。

导读：展示 RAS 地址解码必须结合 socket/die/CS、DRAM map、interleave/hash、base 与 MMIO hole；用于避免把 UMC 错误地址直接解释成系统 PA。
来源：[Linux v6.12 AMD ATL core.c](https://github.com/torvalds/linux/blob/v6.12/drivers/ras/amd/atl/core.c)。
阅读状态：已读完整文件，重点 norm_to_sys_addr、base/hole 处理及初始化/decoder 注册。

## 输入不是独立的一串地址位

`norm_to_sys_addr()` 输入 socket_id、die_id、coh_st_inst_id 和 normalized address。它先建立地址上下文、确认节点并取得地址 map，再 denormalize、dehash、补 base/hole，最后检查 DRAM limit。由此可见，归一化地址只有与来源控制器和映射配置结合才有系统意义。

这种翻译属于存储地址映射/错误解码，不是 UTCL2 的 VA→PA 页表翻译。把两者都搜索为 address translation 是合理的资料拓展，但最终方案必须分清服务对象、状态来源和使用时机。

## 顺序与版本是算法的一部分

base 加法与 legacy MMIO hole 的恢复不是固定放在同一位置。`late_hole_remove()` 为 DF3.5、DF4 和特定六通道模式选择不同顺序；dehash 前后的地址含义因此不同。单独复制一个 XOR 公式而不记录输入是 normalized、带 base 还是带 hole，会产生看似合理却错误的 PA。

limit 检查把寄存器中的边界单位转换成实际地址范围。未知 DF、map 取得失败或超范围均返回错误；调用者必须识别错误返回，不能把其无符号表现形式当合法高地址。

初始化还按 CPU 家族/型号选择 legacy FICAA/FICAD 间接访问方式，再注册 UMC MCA decoder。寄存器访问层与地址数学层是分开的，方便后续将 SMN/DF 配置、UMC RAS 和系统页面处理串起来。

## 可以据此提出的检查

错误记录需同时保存来源实例、原始 normalized address、有效位/错误类型、DF revision 和映射快照。映射改变、harvest、重启后再解析旧记录，可能使用错误上下文。后续只研究可重用接口与证据链，不在没有目标配置时输出一个所谓通用 PA 公式。

非二次幂通道的逆向映射见 [FAB6](../../DF/sources/FAB6-atl-denormalization.md)；系统发现见 [MG10](../../SMN/sources/MG10-atl-system-identity.md)；UMC 记录有效性见 [MEM14](../../UMC/sources/MEM14-umc810-ras-address.md)/[MG11](../../RSMU/sources/MG11-umc67-ras-comparison.md)。本文件不能证明数据请求的硬件 critical path 正是这些软件函数的执行顺序。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
