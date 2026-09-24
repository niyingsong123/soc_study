# MEM1：PG276：HBM 拓扑、地址映射、重排与错误边界

更新日期：2026-09-24。

导读：研究请求进入内存控制器后为何排队、如何选 bank/行、何时返回错误。重点是两级重排、共享命令资源、地址映射对调度的影响；适合 UMC 主线与 EA/HBM 联读。
来源：[PG276](https://docs.amd.com/r/en-US/pg276-axi-hbm)，v1.0，页面日期 2025-12-17；[拓扑](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Topology)、[地址映射](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Address-Map-and-Protocol-Considerations)、[重排](https://docs.amd.com/r/en-US/pg276-axi-hbm/HBM-Reordering-Options)、[数据错误保护](https://docs.amd.com/r/en-US/pg276-axi-hbm/Data-Path-Error-Protection)、[时钟](https://docs.amd.com/r/en-US/pg276-axi-hbm/Clocking)、[PHY-only](https://docs.amd.com/r/en-US/pg276-axi-hbm/PHY-Only-Mode)、[刷新与节能选项](https://docs.amd.com/r/en-US/pg276-axi-hbm/Reorder-Refresh-and-Power-Savings-Options-Tab)、[原始吞吐](https://docs.amd.com/r/en-US/pg276-axi-hbm/Raw-Throughput-Evaluation)、[Activity Monitor](https://docs.amd.com/r/en-US/pg276-axi-hbm/Activity-Monitor)。
阅读状态：已读上述章节正文；AMD FPGA HBM2 IP 实例，不是 GPU UMC 规格；未读全指南或运行 IP。

## 请求路径与共享资源

一颗 HBM2 stack 有 1024 位数据接口，分为 8 个 128 位 channel，每个 channel 再有两个 64 位 pseudo-channel。PC 有各自的数据访问活动，但共享 command/address/control，故不能把两个 PC 建模为完全独立的 DRAM 控制器。bank 内只能维持一个打开的行；行命中、省去 PRE/ACT 的收益，必须与 bank-group 时序和读写方向切换共同讨论。

拓扑页存在 GB/Gb 单位混用，容量应结合地址映射页交叉检查：4 GB stack 对应每 channel 4 Gb、每 PC 2 Gb（256 MiB）；8 GB stack 对应每 channel 8 Gb、每 PC 4 Gb（512 MiB）。这些是本页配置的容量关系，不是所有 HBM 的固定组织。burst 为 4、数据双沿传输；一次命令的数据量须从 PC 宽度和 burst 算出，不能直接等同主机 AXI burst。

## 地址映射改变调度机会

默认映射采用 Row/Bank/Column 组织并把 bank-group 交织放在较低位，BG0 使用地址位 5。较短 AXI 访问也能跨 bank group，缓解连续同组访问的时序限制。长顺序流与随机流混用时，尽量分开 bank 能减少行冲突，但这是布局策略，必须用真实分布评估。

关键耦合是：自定义地址映射会禁用该 IP 的 AXI reordering core。因此“换 hash”和“保持原重排器”不是可任意组合的两个独立开关。论文应先明确物理地址如何落到 PC/BG/bank/row，再研究调度，不宜只比较抽象 FR-FCFS。

## 两级重排与公平性

MC 侧有 12 项 lookahead；可选 AXI 重排层可观察 64 项。它们是不同层次的资源，不能相加成一个统一队列深度。选择倾向包括：已打开行、不同 bank group、无需先 PRE 的可激活 bank，以及读写成批以减少方向切换。文中重排的 coherency 约束指此处请求依赖/顺序维护，不能推导完整 CPU/GPU cache coherence。

老化阈值 128 的语义是较新命令被服务到指定数量后提高老请求优先级，不能写成“128 周期内必定返回”。close-page 借助自动预充电，使下一次随机访问可能更早进入新行，但会损失未来行命中；取舍取决于访问局部性和时序，而非开关名称。

短写测试可能只测到队列吸收速度。需要持续注入后统计稳定吞吐并计入 drain；读返回受实际内存延迟限制更明显。建议记录每层 occupancy、row hit/conflict、读写切换、最老请求等待及请求接收/命令发出/响应返回三个时间点。

## 错误如何对应事务

AXI 写入 parity 校验错误可在启用相应配置时形成 BRESP；读取的 parity 或不可纠正 ECC 可形成 RRESP，重试是否发生另受配置限制。HBM 写 parity 的 DERR 是事件脉冲，不能仅凭它定位某一条 AXI 写命令。内部写路径发现 parity 错误时可故意形成后续 ECC 可检测的数据错误，这体现错误传播策略，不是“所有错误立即在原请求上返回”。

应为 ECC/parity/poison 分别写清检测点、可定位程度、回报通道、数据是否继续传播、软件是否隔离页面。与 [MEM3](../../UMC/sources/MEM3-amdgpu-ras.md)、[MEM14](../../UMC/sources/MEM14-umc810-ras-address.md) 联读，才形成控制器到驱动的闭环。

## 刷新、低功耗与观察窗口

单 bank 刷新、lookahead refresh 和温度补偿有配置依赖。延后刷新以完成读写后，可能需要更密集刷新补偿，不能把推迟当作永久免除维护；power-down 中控制器仍负责按要求刷新，self-refresh 的责任不同。

指南以 900 MHz HBM2 时钟计算单 stack 原始带宽 230.4 GB/s，并以 16 个 256 位、450 MHz AXI 端口匹配。该器件示例中 4H/8H 的刷新占用约 7%/9%，高温时 tREFI 缩短；这些数字仅属于此配置，不能用来固定 HBM3E 可用带宽。

Activity Monitor 按所选 PC 采集，每窗口 450M memory clock cycles，窗口内连续、窗口之间有间隙；汇总吞吐只相加选中的 channel，Average 是本次会话采样点的平均。必须记录选择范围和采样空隙，不能把图形面板当成持续无遗漏的总 stack 流量计。

## 时钟与 PHY-only 的职责变化

HBM reference PLL、APB 配置时钟和各 AXI 时钟是不同域；AXI 可异步。全局 switch 使用所选 AXI 时钟，其选择会影响跨端口效率。PHY-only 绕过 AXI switch/控制器并暴露 DFI，自定义控制器须承担调度、维护和相应可靠性职责，不能只画成少了一层转接。

本例适合为 AMD UMC 建立问题清单；队列数、映射位、时钟约束和错误策略都不能直接作为目标芯片参数。[MEM12](../../UMC/sources/MEM12-ramulator-hbm-controller.md) 提供另一种公开控制器实现，[MEM13](../../HBM/sources/MEM13-ramulator-hbm3-model.md) 提供 HBM3 时序模型，二者也不能与 HBM2 配置混成一代实现。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
