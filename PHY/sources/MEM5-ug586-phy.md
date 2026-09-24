# MEM5：UG586：字节组 PHY 与初始化、校准分工

更新日期：2026-09-24。

导读：研究 DQ/DQS、相位调节、FIFO 和校准逻辑如何组成 PHY；用于从控制器侧跨到物理接口侧，需注意实际读取的是 LPDDR2 章节。
来源：[UG586](https://docs.amd.com/r/en-US/ug586_7Series_MIS)、[Overall PHY Architecture](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Overall-PHY-Architecture)、[Memory Initialization and Calibration Sequence](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Memory-Initialization-and-Calibration-Sequence)。
阅读状态：已读上述路径实际解析到的 7 Series LPDDR2 PHY 架构/初始化说明；未核验全书各 DDR 类型训练顺序或图中全部阶段。

## 结构分解

该 FPGA 实例把专用硬件块与软校准逻辑配合使用，要求布局接近以控制时序。I/O bank 内的字节组包含相位调节、输入/输出 FIFO、序列化/反序列化及延迟单元。PHASER_IN/OUT 提供采样/发送相位调节，并参与 DQS 跟踪；不是用一根“PHY ready”信号就能表达内部状态。

在所读 LPDDR2 配置中，控制器/校准逻辑可运行于存储时钟的较低比率。FIFO 和位宽转换因此既承担吞吐匹配，也承担命令与数据相位关系的组织。不能把慢时钟侧一个周期直接等于一条外部 DRAM 命令，更不能套到 GPU HBM PHY。

## 初始化完成与可服务状态

上电/复位后先进行存储器初始化，再执行写/读路径校准，正常控制器流量须等待相应完成条件。模块研究至少拆出：复位有效、外部器件初始化、采样窗口建立、数据路径校准、正常运行。某个 PLL 锁定只是其中条件之一，不等价整个内存子系统已能返回正确数据。

本次没有根据导航目录臆造 write leveling、deskew 等步骤的完整先后关系。若需要这些算法，应转向 [MEM15](../../PHY/sources/MEM15-pg150-dqs-gate.md) 的已读 DQS gate 实例，并明确那是另一产品指南。

## 可迁移的研究问题

以每个 byte/rank 的相位与延迟状态为对象，区分训练产生的配置、运行时跟踪、软件可读诊断。查明失败能否定位到 byte/nibble/bit、是否支持重训、控制器如何停止新请求以及复位后参数是否失效。上述是本项目的分析框架，不是 UG586 证明目标 PHY 具备的功能。

该资料适合建立 PHY 内部结构图和控制器接口边界，不适合提供先进工艺 PHY 面积、带宽或训练时延。外部串行链路的 CDR/均衡应另读 [MEM7](../../PHY/sources/MEM7-versal-cdr-equalizer.md)，不要把 DQS 门控与串行时钟恢复混为一谈。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
