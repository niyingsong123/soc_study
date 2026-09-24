# VM5：MASK：把地址翻译需求传递到共享缓存和 DRAM 调度

更新日期：2026-09-24。

导读：解释一次 TLB miss 为何能阻塞许多 warp，以及共享 TLB、数据 cache、DRAM 三层怎样共同放大翻译开销。适合设计跨模块性能研究问题；不是 AMD 实现证据。
来源：[MASK，ASPLOS 2018 作者公开稿](https://rausavar.github.io/pubs/mask-asplos18.pdf)，DOI 10.1145/3173162.3173169。
阅读状态：精读 §3–6 的结构、干扰、三项机制及实验方法，阅读 §7.1 的主要对比；未复现模拟器或重新计算全部结果。

## 问题为什么是系统问题

GPU 中多个 warp 可能共享一页翻译，一次 miss 会同时使很多原本可调度的 warp 等待。单看页表流量占带宽不大，不能判断翻译影响小：页表读取在依赖链上，FR-FCFS 偏好的数据 row hit 可能使低局部性的 page-walk 请求等待更久。

## 三项机制与实际资源

TLB-Fill Tokens 控制哪些 warp 有资格向共享 L2 TLB 填入翻译，降低多应用相互驱逐；无 token 的请求仍可得到翻译，并使用小型 bypass cache，不能把 token 理解成禁止该 warp 访存的执行许可证。token 分配以 epoch 的命中等反馈调整，目标是限制污染而非固定给每个应用平均容量。

Address-Translation-Aware L2 Bypass 按页表遍历层级观察 translation-data 在共享数据 L2 的命中率，并与 demand data 比较；收益低的层级旁路数据 L2。这里被 bypass 的是存放页表项的数据 cache，不能误写成所有请求绕过共享翻译 TLB。

DRAM 调度分 Golden、Silver、Normal 三类队列：翻译请求进入 Golden；一个当前被照顾的应用的数据请求进入 Silver；其他数据进入 Normal。优先级为 Golden→Silver→Normal，后两类内部采用 FR-FCFS。Silver 的预算根据并行 walk 数与因 miss 阻塞的 warp 数分配，尝试兼顾关键性和应用公平。不同策略分别作用于 admission/fill、cache allocation 和 memory scheduling，不是一个单独的仲裁器参数。

## 保护、评估和局限

论文引入地址空间标识，并在改变页表根时保守 drain 相关在途访问。缺页处理的完整机制与低开销 shootdown 明确不是该工作的完整交付，不能拿它作为目标 ATS heavy invalidate 或 fault-replay 的证明。

评估基于 NVIDIA Maxwell 风格、Mosaic/GPGPU-Sim 的研究模型，比较 PWCache、SharedTLB、Ideal 等，并使用特定多应用组合。作者报告的主要提升属于这些模型和基线；它不意味着 AMD UTCL2 增加一个队列就能得到同样收益。本笔记保留机制和评估条件，不将论文百分比移植为目标性能承诺。

## 我们应复用的研究问题

向下游传递翻译请求类别需要哪些属性？优先服务 walker 是否会饿死普通数据？每级页表缓存的命中是否有不同价值？合并 miss 之后应该按“原始客户数”还是“实际下发数”计成本？这些问题分别落在 [VM9](../../UTCL1/sources/VM9-gem5-coalescer.md)、EA、UMC，而非只在 UTCL2 内讨论。量化比较时再回读 §6–7 的配置、工作负载和指标定义。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
