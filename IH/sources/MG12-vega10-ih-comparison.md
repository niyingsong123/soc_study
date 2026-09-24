# MG12：Vega10 IH：不同 ring 的 wptr 来源与溢出处理

更新日期：2026-09-24。

导读：通过另一代 IH 检查 ring 数量、writeback、地址和 overflow 差异；适合验证哪些结论可复用，避免只看 IH6.0 就推广所有 GPU。
来源：[Linux v6.12 vega10_ih.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/vega10_ih.c)。
阅读状态：已读软件初始化、wptr/rptr、overflow/rearm 和公共解码绑定；原候选 ih_v5_0.c 路径不适用，实际来源以此文件为准。

## Ring 的差异

主 ring 和 software ring 可从内存 shadow 取 wptr，其他硬件 ring 走寄存器读取并检查 overflow；software ring 没有对应硬件寄存器，set_rptr 直接返回。非 APU 配置还创建 ih1/ih2，额外 ring 用 PAGE_SIZE，不能认为所有 ring 大小和通知方式相同。

该版初始化采用 bus address；[MG6](../../IH/sources/MG6-ih60-ring-hardware.md) IH6.0 会根据固件装载路径选择地址空间。两代共享部分公共函数，不表示所有初始化条件都相同。

## 溢出和回收

overflow 处理二次核对寄存器，丢弃已覆盖范围并从 wptr 后一个 IV 位置继续；clear 位先置再撤销。此动作恢复解析进度，无法追回丢失事件。VF 的 doorbell rearm 采用有限重写检查，改善消费者位置通知，不是业务数据重传。

绑定公共 Vega10+ 解码器，每条 IV 32 字节，字段解释见 [MG7](../../IH/sources/MG7-ih-core-consumer.md)。比较时应把硬件生成、wptr 取得、ring 消费和中断使能分别对照，避免因格式相同便认为整条事件链相同。

## 后续使用

研究计划可以以一代为主、另一代作差异检查：哪些状态在驱动持有，哪些由硬件返回，哪些为 TODO/空操作。不能将两个版本的 ring 数和地址模式合并为目标配置；目标 IH 容量、溢出策略和重通知保证仍需本地材料确认。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
