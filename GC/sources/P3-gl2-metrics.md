# P3：gfx115x GL2 的访问边界与计数口径

更新日期：2026-09-24。

导读：把 GL2 命中、客户请求和向 GCEA 下发的流量分开，适合建立缓存到仲裁器的观测模型。它提供计数语义，不提供 GL2 队列深度或替换算法。
来源：[GL2 cache，docs-7.14.0 / Profiler 3.7.0](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/gl2-cache.html)。旧 P3 的 7.14.1 链接保留在总索引；本笔记以本次成功读取的 7.14.0 为准。
阅读状态：页面正文全部已读，包括性能、请求统计、带宽和 Memory Chart；未核对每项面板 YAML 的底层表达式，未实测。

## 在微架构中的位置

gfx115x 的 GL2/GL2C 是多数客户离开 GFX 缓存层级前的末级缓存。资料将 Instinct 的 L2/TCC 作为功能对照，不意味着寄存器和实现完全相同。GL2 的上游包括 GL1 和其他客户；未在这里满足的请求向 GCEA 等内存系统接口推进。

必须分别观察三个边界：客户到 GL2、GL2 本地服务、GL2 到 GCEA。总请求包括读、写、原子请求，写流量也可能来自上级 cache writeback。原子操作可能在热点地址产生串行化，不能只按“每个原子等于一次普通写”建立模型。

## 指标怎样组合使用

命中率回答本地满足的比例；总请求数回答 GL2 承受的入口压力；EA read/write requests 回答向下游发出了多少请求；GL2 read/write bandwidth 回答相应缓存边界的数据量/时间。这些指标的统计位置不同，不能互换。

页面带有 DRAM 字样的 EA 请求仍可能被系统级缓存服务。因此“向 EA 发出”不是“HBM/DRAM 已执行”，更不是“DRAM 返回完成”。与 [VM6](../../EA/sources/VM6-gcea-metrics.md) 的 return 指标、[P5](../../GC/sources/P5-mi200-counters.md) 的 outstanding/credit 事件结合，才能分析下游等待。

Count per Normalization Unit 也不等于原始硬件事件总数。比较多个 kernel、客户端或采样时，先统一 normalization、实例求和和时间范围，再计算比值。若所选事件确实分别计数所有 hit/miss，可计算 `hit/(hit+miss)`；该公式不能未经 YAML 核验直接当作所有面板的实现。

## 一个可复用的分析例子

假设同一采样范围内入口请求增加、命中率稳定、EA 请求也增加，可先检查工作量是否增加。若入口相近而 EA 增加，需检查局部性、写回、缓存策略或原子流量。若 EA 不高但延迟上升，要转查 credit、返回停顿、热点和翻译，不能只说“显存带宽不足”。这些是根据观测位置形成的分析步骤，不是页面给出的实测结论。

未提供的细节包括 line/sector 组织、bank 映射、MSHR 合并、仲裁算法和失效时序。后续设计这些结构时，应使用新证据；只做缓存到 EA 的边界分析时，本笔记足以复用。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
