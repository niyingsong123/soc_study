# MG1：SMU 公共驱动：mailbox、错误状态与表传输

更新日期：2026-09-24。

导读：详细追踪管理命令如何串行提交、等待响应和搬运数据表；适合 SMU 控制路径，尤其用于区分发送成功、固件执行成功和状态实际改变。
来源：[Linux v6.12 smu_cmn.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c)。
阅读状态：已读 mailbox send/poll/response、ASIC 编号映射、VF 过滤及 update_table；未读 SMU 固件内部算法。

## 共享 mailbox 的事务

底层发送按 response 清零、写参数、写 message 的次序进行。同步接口持有 message_lock，先处理旧响应/固件状态，再发送并等待新响应，最后读取可选返回参数。参数寄存器可同时用于输入和输出，因此访问必须属于同一事务；软件通用消息编号还需经过 ASIC 映射。

without_waiting 只保证成功走过发送路径，不保证本条命令已经执行；它还会检查此前状态，不能理解成无条件覆盖 mailbox。poll 等待 response 非零，有有限超时。none、命令失败、未知命令、前置条件不满足、固件忙等状态有不同含义，不宜统一当成硬件挂死。

## 返回零未必发生了硬件操作

no_hw_access 会直接成功返回；VF 不允许的消息映射到特定错误后也可被上层转换为成功并丢弃。同步接口即使得到错误，也可能读取参数寄存器帮助诊断，不能不检查返回码就把该值当结果。固件 hang 状态会限制后续发送。

这要求后续论文分别定义：API 接受、寄存器发布、固件接收、执行响应、目标效果观察。某次响应 OK 是否意味着时钟已稳定或远端动作全部完成，仍需对应命令语义，不能由公共发送函数推断。

## 数据表传输不是只有一条消息

driver→SMU 先复制到共享 driver table，再做 HDP flush，随后发 TransferTableDram2Smu；SMU→driver 则在消息返回后 invalidate HDP 再复制数据。table ID 经映射，argument 的部分位与 ID 打包。共享表地址由另一初始化路径发布，见 [MG2](../../SMU/sources/MG2-smu13-control.md)。

这是一条管理流量依赖数据可见性的实际代码路径：CPU copy、HDP 维护、mailbox、固件访问不是相互独立的动作。[IO6](../../HDP/sources/IO6-hdp40-maintenance.md) 对维护完成的限制仍适用，应查对应调用契约，不把一个通用函数扩成全系统一致性保证。

## 研究落点

将 SMU 分解为 host 接口、命令序列化、固件状态、共享表和受控对象，再研究 DPM/RAS 等 feature。重点保留超时后资源/状态、错误可重试性、VF/PF 权限和复位恢复。代码不证明 RSMU 是 SMU 的某固定子单元，也不证明 mailbox 物理链路一定经过项目 CF。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
