# MG3：SMU 13.0.0 ABI：DPM 描述、表结构与指标语义

更新日期：2026-09-24。

导读：研究固件接口版本、参数表和 telemetry 的字段差异；重点是 target/pre-DS/post-DS、平均时间常数与累计量，适合设计可信观测表。
来源：[Linux v6.12 smu13_driver_if_v13_0_0.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu13_driver_if_v13_0_0.h)。
阅读状态：已读版本、feature 定义、DpmDescriptor、PPTable 组合、DriverSmuConfig、DriverInfo 和 SmuMetrics；未逐字段研究完整板级参数/算法。

## ABI 不是微架构实物清单

该文件 driver interface version 为 0x3D、PP table version 为 0x2B；PPTable 组合 SKU 与 Board table，并规定相关打包。字段宽度、数组上限、padding 都属于版本契约，不能任意删除后继续声称二进制兼容。

feature bit 覆盖多个时钟域 DPM、deep sleep、GFXOFF、BACO、节流和管理功能。它们表示接口可描述的能力，不证明每个 SKU 全部支持/启用。数组最大项数也不是正在使用的 DPM level 数。

## DPM 与平均值

DpmDescriptor 区分细粒度/离散档位，细粒度场景可用两端值表示范围；转换函数、最优频率及计算选择是固件的输入，不能从表结构反推出具体控制算法。

DriverSmuConfig 给时钟、活动率、功率平均值配置 LPF 时间常数，单位毫秒。Metrics 同时区分当前 clock、目标平均频率、deep sleep 前后平均频率，内存频率字段还注明缩放到实际 memory clock。比较不同字段前必须说明采样/平均窗口和时钟定义。

## 累计量和系统口径

MetricsCounter、EnergyAccumulator、平均 socket/board power、温度、PCIe rate/width、节流百分比和 D3hot 计数属于不同量纲。能量累计值需配时间差、缩放与回绕处理；节流百分比不能直接当成丢失吞吐百分比。padding 的 MmHub 命名只说明 ABI 内部用途，不足以推定 MMHUB 数据路径。

## 后续使用

为每个指标保存原字段、类型、单位、时间口径、版本和有效条件。[MG1](../../SMU/sources/MG1-smu-message-table.md) 说明表如何传输，[MG9](../../SMU/sources/MG9-thermal-power-observability.md) 说明用户可见接口。不能用同一偏移解析其他 SMU13 子版本，也不能把频率数组直接写成目标 PLL 数量。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
