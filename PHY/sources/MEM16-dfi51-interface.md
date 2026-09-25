# MEM16：DFI 5.1：启动、训练交接与读写有效期选读

更新日期：2026-09-25。

导读：补足 DFI 官网介绍之外的接口机制：启动完成代表什么、PHY 如何取得训练控制、写命令与数据怎样对齐、读返回为什么不能假定固定连续延迟。适合 UMC/PHY 边界研究，不覆盖 DFI 6.0 HBM profile。
来源：[DFI 5.1 原始规范公开转录](https://studylib.net/doc/27487094/ddr-phy-interface-specification-v5-1)，正文标识 2021-05-21、163 页、Cadence/DFI；[DFI 官方入口](https://ddr-phy.org/)。平台只是原文读取渠道。
阅读状态：选读 §3.3.3、§3.8、§4.1–4.2、§4.7.1 的正文及 PHY-master 依赖项；未取得官方 PDF、未核全部波形图、比例转换表和低功耗交叉条件。不把官方门户登录页记成已取得规范。

## 启动与总线控制权

PHY 接到 dfi_init_start 后才可给 dfi_init_complete；相关频率/比例先确定。init_complete 表示能正确响应 MC，并保证 DRAM 命令接口完整性；DFI 不指定 PHY 内部训练算法。PHY-independent boot 由 PHY 完成内存初始化/训练，这次启动不使用 dfi_phymstr_req。

## 数据交接

写命令至 dfi_wrdata_en 的延迟为 tphy_wrlat；它与 tphy_wrdata 共同确定数据对齐，活动期间保持参数不变，可在 idle 时调整。不同 chip-select 转换还可能需要 PHY 指定的额外间隔。

读侧每 data slice 独立给 dfi_rddata_valid；enable 与 valid 的有效周期数量对应。tphy_rdlat 是返回上限而非固定等待值，满足每次时限时，valid 可以提前且不连续。

PHY-master 交接不能仅停止新命令：相关依赖要求命令/数据总线空闲、已有读写数据到达目的地，并约束低功耗及更新请求的并发。

## 如何据此组织 UMC/PHY 微架构研究

以下为本项目推导的问题表，不冒充标准规定的内部结构：

| 位置 | 应建立的模型 | 接续时的检查问题 |
| --- | --- | --- |
| MC 发射与 PHY 接收 | 命令、data-enable、data 三个时点及所属时钟域 | ratio/频率改变后，旧参数对应的在途事务是否已排空？ |
| 读返回聚合 | 分 slice 的 pending、valid 和拼接条件 | 某 slice 提前或间断返回时，能否保持原命令及数据位置？ |
| 初始化控制 | reset、boot 配置、PHY ready、普通业务放行分别建状态 | ready 的含义是否被误用为整个 SoC 已可接流量？ |
| 训练借用接口 | 控制权持有者、交接前提、退出与恢复配置 | 控制器是否仍承担 refresh 责任，目标版本如何约定？ |
| 参数更新 | 活动/idle、旧配置使用者、新配置生效点 | 不同 rank/chip-select 的额外切换间隔在哪里执行？ |

本篇适合先把接口责任拆清，再与 [MEM15](MEM15-pg150-dqs-gate.md) 的具体训练算法联读。MEM15 是 FPGA DDR3/4 实例；本篇是 DFI 5.1 选读；[MEM4](MEM4-dfi-version-boundary.md) 记录 6.0 加入 HBM 的公开版本信息，三者不能合成一个已核验的 HBM3 PHY。

## 仍须正式版本补核

后续优先补频率比例下 pN/wN 信号的映射、MC/PHY update 握手、训练与 refresh 的完整组合规则、低功耗进入/退出和异常恢复波形。当前转录里表格/波形有信息损失，所以本次不补造 cycle-accurate 状态机或目标信号表。若本地已获得相同版本原文，直接更新本篇阅读范围与差异；6.0 HBM 新规则应保留独立版本定位。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
