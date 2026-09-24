# P4：GRBM 活动计数与利用率解释

更新日期：2026-09-24。

导读：说明 GRBM 提供哪些粗粒度忙碌度观测，以及为什么 GPU Busy、GL2C Busy 不能直接证明吞吐或瓶颈。研究 GRBM 寄存器选址和 RLC 协同时应联读 GC2。
来源：[Graphics Register Bus Manager，docs-7.14.0](https://rocm.docs.amd.com/projects/rocprofiler-compute/en/docs-7.14.0/conceptual/rdna/grbm.html)，Profiler 3.7.0，RDNA3.5/gfx115x。
阅读状态：正文全部已读；未实测采样，也未逐一核验面板代码。旧索引的 7.14.1 不作为本次实际阅读版本。

## 核心内容

GRBM 的利用率页面聚合整个 GPU 和 Shader Engine 的活动，而不是解释内部寄存器总线结构。GPU Busy 反映工作活跃的时间占比；CP Busy、GL2C Busy 等采用 GPU active time 语境；TA Busy 反映纹理地址计算相关活动。分母不同的百分比不能直接相加，也不能把它们当作互斥的流水阶段。

这些块可以同时忙碌，因此 `CP Busy + GL2C Busy` 超过 100% 并不必然意味着统计错误。相反，GPU Busy 很高也不意味着所有执行单元或所有内存通道均达到有效吞吐上限：等待、局部热点、资源冲突仍可能存在。根因应回到 GL2 请求、EA credit/返回或其他相应模块的指标。

## 放进研究骨架的方法

将 GRBM 分成两个研究问题：一是控制侧如何选择实例、广播和访问寄存器，二是观测侧如何汇总活动。本文支持第二个问题，[GC2](../../GC/sources/GC2-gfx943-rlc-grbm.md) 支持第一个问题的软件可见接口。两份资料不能拼接成已知的 GRBM RTL 流水图。

分析案例：GL2C 活跃但有效读带宽低，可以检查请求粒度、热点原子、miss 服务等待；CP 活跃但后端活动低，可以检查命令供应和调度。这里列的是排查方向，计数本身不证明某一个原因。若还要分析功耗，应同步记录时钟、电源状态和采样周期；不同频率下相同 busy 百分比不代表相同绝对吞吐。

## 复用与限制

本笔记可用于 GC 性能观察和 SMU 调频后的测量解释。需要新增精确公式、读取寄存器字段或比较 RDNA/CDNA 时回到目标版本文档和面板代码；无需为了“GRBM 是什么、busy 怎样读”重读整个 profiler 文档。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
