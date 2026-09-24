# P5：MI200 的翻译、EA credit 与在途请求计数

更新日期：2026-09-24。

导读：提供可操作的观测点：UTCL1 translation/permission miss、UTCL2 busy、EA 按 IO/GMI/DRAM 分类的 credit stall，以及在途请求积分。适合做跨模块性能诊断，但不是目标芯片的计数器规格。
来源：[MI200 performance counters and metrics，ROCm 6.0.0](https://rocm.docs.amd.com/en/docs-6.0.0/conceptual/gpu-arch/mi200-performance-counters.html)。
阅读状态：本次成功读取页面，精读 GRBM、CPF/CPC 的翻译相关项、TCP UTCL1、TCC/EA 及 derived metrics 对应条目和缩写；未逐一研究全部指令/纹理计数，未采样验证。

## 翻译观测位置

`TCP_UTCL1_REQUEST/HIT/MISS/PERMISSION_MISS[n]` 将翻译请求、映射命中、未命中和权限问题分开。permission miss 不能未经说明并入普通容量 miss，也不能仅凭事件名当作操作系统最终 page fault。CPF/CPC 的 translation stall 是客户端等待翻译的周期，而 `GRBM_UTCL2_BUSY` 是 UTCL2 活跃周期；两者是因果分析的两端，不是相同事件。

`CPC_CPC_UTCL2IU_BUSY/IDLE/STALL` 指定了某客户端接口。它不能代表所有 UTCL1 或整个共享 UTCL2。对实例求和时，需记录 n 范围和当前启用实例，不能把停用实例或不同产品参数混入。

## 下游背压的分解

TCC 到 EA 的读写请求可以因 IO、GMI、DRAM credit 不足而停顿。另有 `TCC_TOO_MANY_EA_WRREQS_STALL` 表示本地未完成写请求已达到允许容量。前者关注远端/接口信用，后者关注源端在途资源；加大本地队列不一定解决下游信用不足。

`TCC_EA_WRREQ` 统计 32B 和 64B 事务，部分 atomic 走写接口且归到写请求；probe commands 不在该项中。`TCC_EA_WR_UNCACHED_32B` 以 32B 单位计，64B 请求贡献 2，且 CC mtype 也可产生此类 uncached 请求。因此请求数、字节量、普通 store 数是三个不同口径。读端同样应区分总请求、32B 请求和 uncached 流量。

## 在途积分与平均延迟

页面给出 `EA_RDREQ_LEVEL / EA_RDREQ` 等平均延迟口径。其意义是对在途请求数量按周期累积，再除以对应请求数；不是“某一时刻队列长度/请求数”。若积分为 1200 request-cycles、对应完成/计数请求为 100，得到 12 个相应计数时钟周期，而非 12ns。转换为时间还需该计数域频率。

这个关系要求统计对象和窗口匹配。窗口开始已有在途请求、结束仍有未完成请求、计数溢出或事件采集不同步，都会造成边界偏差。多个实例需先对同口径积分和请求数分别求和，不能无权重平均各实例延迟。

## 形成闭环而非堆事件

可以按“客户翻译等待 → 缓存请求 → EA 接纳与在途 → HBM 目标分类/返回”组织测量；每一步保留自己的计数位置。[VM6](../../EA/sources/VM6-gcea-metrics.md) 属于另一产品的 GCEA 面板，只能对照观察方法，不混算 MI200 的结果。

同页 CS 指 Compute Shader，而 [P1](../../DF/sources/P1-ryzen-fabric-topology.md) 中 CS 是 Coherent Slave。这是命名检索必须保留上下文的直接例子。后续正式测量仍需核验目标 ASIC、计数使能、采样互斥和公式；本次不声称任何性能结果。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
