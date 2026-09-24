# VM6：GCEA 的接纳、停顿、目标与返回观测

更新日期：2026-09-24。

导读：按 read/write、SARB 和 return 三个边界整理 gfx115x 的 GCEA 指标，帮助判断请求缺乏、下游背压和返回受阻的区别。
来源：[Graphics Core Efficiency Arbiter，docs-7.14.0](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gcea.html)，Profiler 3.7.0。
阅读状态：页面正文全部已读；未跑硬件计数或核验所有 YAML。2026-09-24 另查 develop 页，只作内容对照，版本不混算。

## 从整体工作流读指标

该页面把离开 GL2 的读写内存接口、system arbiter 和返回路径放在一起。gfx115x 是使用 DDR5/LPDDR5 的 APU 语境，不能把这里的 DRAM 计数直接改名为 HBM 控制器事件。

读写端各有 requests、chained requests、banks active、size（32B increments）。request 计数、链式访问次数和字节量代表不同量：连续访问可能更高效，但仅凭 chain count 不能推出实际命令合并粒度；pending banks 反映并行性观察，也不告诉我们 bank 地址映射算法。

SARB busy 表示活动，stalled 表示有请求但因下游背压不能推进，starving 表示无请求可处理。三者在诊断中分别对应服务、等待、供应不足。只有先核验底层定义和分母，才能判断它们是否互斥或穷尽所有周期，不能自动要求三项百分比相加为 100%。

## 返回和完成

read return、write return 与 probe 是不同事件。write return 是该观察边界的应答，不应仅凭面板描述宣称持久化、CPU 所有 cache 可见或所有 DMA 完成。若请求增多而返回偏少，应同时考虑窗口边界的在途请求和返回方向拥塞。

页面给出的 stall rate 采用 `GCEA_SARB_STALLED_sum / GCEA_ALWAYS_COUNT_sum × 100`，分母是 GCEA sample cycles。其他每 normalization unit 的事件不可直接拿来替代该分母。[P5](../../GC/sources/P5-mi200-counters.md) 中 MI200 的在途积分/credit 分类则属于另一个产品参考。

## 面向 EA 微架构的分析

建议保持接纳资格、仲裁选择、真正下发、等待返回和资源释放五个动作分离。例如输出选中某请求而下游不接受，不应立即释放入口槽或转移公平指针。页面没有公开采用何种仲裁器；具体可实现例子见 [EA1](../../EA/sources/EA1-rr-arbiter.md)，其身份始终是参考 RTL。

本笔记可以直接服务 EA 性能问题与 GC→内存边界研究。需要选择字段、恢复实际拓扑或解释某个目标 ASIC 时，继续核对对应 IP 资料；不能从性能分组推出 EA/DF/UMC 的物理父子关系。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
