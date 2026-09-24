# FAB2：Linux DF 3.6：通道编码、hash、实例访问与性能计数器

更新日期：2026-09-24。

导读：从 AMDGPU 的 DF 3.6 回调识别软件能观察的配置与计数器生命周期，特别说明寄存器编码不等于实际通道数、计数器零值也可能来自未支持或重装失败。
来源：[Linux v6.12 df_v3_6.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/df_v3_6.c)。
阅读状态：已读 channel/hash、broadcast、clock gating、PMC 分配/启动/读回/停止及 poison-query 相关函数；本文件是软件编程视图，不是 DF RTL。

## 配置读取与实例边界

`get_fb_channel_number()` 读取 interleave 编码，Aldebaran 与其他 ASIC 使用不同寄存器路径；`get_hbm_channel_number()` 再通过映射表变成数量。直接把原字段当 channel 个数会错误。`query_hashes()` 还在特定 ASIC/编码条件下读取 64K、2M、1G hash 开关，说明地址分布与实例配置有关。

配置访问有 broadcast 与实例选择语义。调研一处寄存器时应同时记录 DF 版本、ASIC、寄存器实例和访问模式，不能凭同名寄存器在一个实例读出的值推断全系统。

## PMC 的完整生命周期

计数器先分配槽位与 config，再设置控制地址和 enable。部分路径只针对 Vega20/Arcturus；分配成功、硬件 arm 成功、有效读数是三个阶段。arm 失败可能记录 deferred，读数路径尝试重装；重装失败直接返回初始零值。超过该实现判断阈值的数值也可被处理成零。

因此零值可能表示无事件，也可能表示版本未支持、配置无效、资源未就绪或异常处理。研究应把硬件支持/分配状态与计数结果一起保存。停止计数与释放槽位也是不同操作，重复配置和并发采集必须追踪所属槽位，避免把其他实验的计数归入本次。

## 从软件证据到研究方案

此文件支持在 DF 方案中加入通道/interleave 配置、hash、时钟门控、RAS poison 模式和观测能力。它没有公开 router 端口结构、CS coherence FSM 或 credit 深度；不能把回调集合当作全部 DF feature。

建议把地址流量实验与 [FAB3](../../DF/sources/FAB3-atl-address-core.md)/[FAB6](../../DF/sources/FAB6-atl-denormalization.md) 的映射模型对齐，先验证通道数量和 hash，再解释流量不均；把低利用率与 clock gating/无效计数区分。指标采用每 channel/每实例和聚合两种口径，但须说明实际采样支持范围。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
