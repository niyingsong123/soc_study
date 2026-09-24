# MG6：IH 6.0：ring 地址、溢出与 doorbell 回收

更新日期：2026-09-24。

导读：从硬件可见配置解释 IH ring 的地址空间、wptr 发布、溢出和 rptr 回收，适合建立事件传输主线；特别标出占位函数不能证明 idle。
来源：[Linux v6.12 ih_v6_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/ih_v6_0.c)。
阅读状态：已读 ring 控制/地址配置、get_wptr/set_rptr、rearm、self IRQ、软件初始化和 idle/reset 接口；未读目标 RTL。

## Ring 地址与入口

软件初始化按固件装载路径选择 bus address 或 GPU 地址，不能把所有 IH DMA 都视为绕过 GPU 地址体系。ring 配置包括 MC_SPACE、VMID、snoop/relaxed ordering、wptr writeback 及容量；base 的移位编码与 host 指针单位不同。

ring0 支持相应 writeback 配置，ring1 对 overflow/full drain 的设置不同；非 APU 才创建所读额外硬件 ring。VF 某些控制写通过 PSP 间接编程，失败可返回超时，说明寄存器访问权限也是初始化依赖。

## 溢出不是无损重试

先读 wptr shadow，发现 overflow 再读硬件寄存器确认；确认后把 rptr 移到 `(wptr+32)&mask` 从尚未覆盖处继续处理。已经覆盖的 IV 无法由这段代码恢复。清 overflow 位后立即撤销 clear，以便检测下一次溢出。

set_rptr 可更新 shadow 并敲 doorbell，或写寄存器；VF 有有限次 rearm/rewrite，检查硬件 rptr 是否追上软件。这里重写的是消费者位置通知，不是重放原业务事务。

## 中断风暴与 self IRQ 阈值

初始化将 GC/MMHUB UTCL2 page fault 设为支持 MSI storm 控制的来源，并配置 delay 字段，以减少连续 page fault 造成的频繁 ISR；离散 GPU 的部分来源可重定向至 ring1。这里调整的是事件通知与消费节奏，不是修复 fault 的机制。

`force_update_wptr_for_self_int` 的 threshold 编码范围为 0–15，对应 `2^threshold`；timeout 编码范围为 0–20，对应 `2^timeout × 1024 / socclk_freq` 的时间关系，计算时频率与时间单位必须一致。它设置 self IV 的强制更新超时/使能，并给启用的 ring1 设置中断阈值；初始化调用使用 threshold=0、timeout=8。VF 经 PSP 写寄存器失败时会返回错误，不能仅凭期望配置宣称阈值生效。

研究时需把 IV 写入 ring、wptr 发布、self IRQ 通知和软件消费分别放入资源/状态表。合并通知不能据此推出无事件丢失保证，环容量与最慢消费者仍需另行评估。

## 多 ring 与完成

self IRQ 可携带 ring1 的 wptr，更新 shadow 后安排 work；事件本身也能用于通知另一个事件队列。[MG7](../../IH/sources/MG7-ih-core-consumer.md) 再负责按 wptr 读取 IV、分派和回收，[IO8](../../IH/sources/IO8-linux-msi.md) 解释 CPU 侧 MSI。

特别注意 is_idle 返回 true、wait_for_idle 返回超时、soft_reset 返回零的函数带 TODO；不能以这些返回值声称硬件已排空或完成复位。论文需列实际可观察状态，避免让软件占位实现变成架构结论。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
