# IO9：Linux PCI 恢复：隔离、诊断、复位与恢复 I/O

更新日期：2026-09-24。

导读：提供错误后跨驱动协作的状态机，重点是 MMIO 恢复不等于 DMA 可重启；用于系统恢复主线及超时/复位规划。
来源：[Linux 6.12 PCI Error Recovery](https://docs.kernel.org/6.12/PCI/pci-error-recovery.html)。
阅读状态：已读通用回调、状态/返回码、恢复阶段及中断限制；部分内容明确为平台特例或提案，未当成所有 Linux 平台事实。

## 故障后的协作边界

平台可隔离受影响设备以阻止继续破坏系统；驱动收到 error_detected 后停止依赖不可访问寄存器的轮询并处理新请求。所有受影响功能共同反馈 CAN_RECOVER、NEED_RESET 或 DISCONNECT，平台据此决定下一步，不能只看某个函数已经成功。

mmio_enabled 允许早期诊断/配置，通常还不允许正常 DMA；slot_reset 后要恢复设备状态，但正常 I/O 应等待协调后的 resume。链路复位、slot 复位和永久故障是不同分支，具体范围由平台能力决定。

## 完成与失败处理

原先在途请求可能失去完成事件，不能一律重发带副作用命令。设计应分别决定取消、返回错误、重建或有条件重试，并处理 tag、队列和映射资源。永久故障时拒绝新 I/O、取消未完成操作，是与暂时暂停不同的终态。

隔离到恢复期间中断既不能保证停止，也不能保证正常送达；handler 必须考虑无效设备状态。不能把一次中断缺失当成工作尚未完成，也不能因中断到来就继续普通 MMIO。

## 跨模块研究使用

把 PCIe link、NBIF aperture、HDP 状态、IH ring、DMA 队列及 SMU 管理通道分别列出恢复条件，标明谁拥有每项状态。上述是系统分析任务，文档没有证明它们在目标芯片上共享同一复位域。[IO12](../../PCIE/sources/IO12-aer-error-path.md) 连接 AER 严重性，[MG1](../../SMU/sources/MG1-smu-message-table.md) 连接固件管理超时，避免将恢复写成一个 reset 按钮。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
