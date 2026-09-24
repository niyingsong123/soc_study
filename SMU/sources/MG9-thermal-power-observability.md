# MG9：AMDGPU 温度/功耗接口：单位、策略与同步快照

更新日期：2026-09-24。

导读：用于设计性能实验的观测表，区分功率上限、实际功率、档位与平均频率；适合 SMU 的反馈路径，不是固件调频算法说明。
来源：[Linux 6.12 AMDGPU Thermal/Power](https://docs.kernel.org/6.12/gpu/amdgpu/thermal.html)。
阅读状态：已读 hwmon、performance level、pp_dpm 与 gpu_metrics 段；未执行任何调频、功耗或风扇写操作。

## 单位和对象

温度通常以毫摄氏度暴露，电压以毫伏，功率以微瓦，风扇 PWM 与 RPM 又是不同量。功率接口区分 average、instantaneous 和 cap；APU SoC 功率可能包含 CPU，不能直接与独立 GPU 的同名读数比较。

多个温度传感器及某些时钟接口只对特定代际可用，需读取 label 和平台支持。没有某节点不能立即认定没有相应硬件传感器，也可能是驱动未暴露。

## 策略与实测

auto/low/high/manual 改变性能管理模式；manual 才能按支持接口控制允许的档位。profiling 模式为了测量减少 clock/power gating 的变化，其实际频率仍有 ASIC 差异。pp_dpm 显示的可用 level、当前选择和 deep sleep 特殊项不是一张静态 PLL 列表。

gpu_metrics 提供同一快照语境下的温度、频率、利用率、功率、节流等，比分散读多个节点更适合关联分析；但各字段内部平均窗口仍需按 [MG3](../../SMU/sources/MG3-smu13-firmware-abi.md) 核对，不代表所有数值均为同一瞬时采样。

## 对研究方案的用法

实验记录 workload、功率/温度限制、策略模式、传感器单位与版本，先确认性能变化是否伴随时钟/节流变化，再归因 UMC/NoC 仲裁。设置 power cap 不等于实际功耗，节流通知也不直接等于吞吐损失比例。

这些接口帮助观察闭环，不揭示 SMU firmware 如何计算控制量。精确控制周期、稳定性和响应时延仍须固件说明或测量。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
