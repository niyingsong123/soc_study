# MG8：AMDGPU IRQ：来源分派、引用计数与复位恢复

更新日期：2026-09-24。

导读：研究 IH 解码后如何路由给 IP/KFD、如何管理中断使能引用，以及 reset 后如何恢复；适合把事件传输连接到实际处理者。
来源：[Linux v6.12 amdgpu_irq.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_irq.c)。
阅读状态：已读 handler、来源登记/dispatch、delegate、enable get/put/update 和 reset resume helper；未通读所有 IRQ domain 平台分支。

## 分派身份

来源用 client_id 与 src_id 两级表登记，检查范围、回调及重复登记。dispatch 先解码 IV，再按身份查找处理函数；旧 SoC 不支持时间戳时初始化为零。因此“有时间戳字段”不代表每代都提供有效硬件时间。

部分 legacy/ISP 分支进入 IRQ domain；一般来源调用其 process，返回值影响是否继续送 KFD。未被标记 handled 的事件还可能交给 amdkfd，不能假定每条 IV 恰好一个软件消费者。异常 client/src 也需要保留诊断，而不是默默映射到默认模块。

## 使能是共享状态

get/put 对某个 source/type 维护引用计数，在首次启用或最后一次释放时调用硬件 set。update 在持 irq lock 后重新判断 enabled 状态，避免并发把刚启用的源又关闭。计数不是在途 IV 数，mask 也不代表此前 ring 中事件已清空。

reset resume helper 可恢复 MSI-X，并遍历所有已登记 source/type 重新应用期望状态。软件保留的 desired state 与复位后硬件寄存器实际状态存在一段差异，恢复顺序应与 ring 准备好相协调。

## 接续研究

IH 主线需覆盖生产、传输、分派和处理完成，不能在“CPU 收到 IRQ”结束。SDMA trap 可能推进 fence，温度事件可能触发管理工作，故 handler 返回和上层动作完成不同。[SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md)/[MG2](../../SMU/sources/MG2-smu13-control.md) 给出相邻来源实例；本文件不证明目标硬件中断仲裁算法。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
