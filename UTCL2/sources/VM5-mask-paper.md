# VM5：MASK：把地址翻译需求传递到共享缓存和 DRAM 调度

更新日期：2026-09-25。

导读：解释 token/fill 与两种 cache 旁路、DRAM 三队列预算；保存公式、容量、工作负载筛选、基线与吞吐/公平性结果，适合 UTCL2–EA–UMC 的翻译干扰研究。
来源：[MASK，ASPLOS 2018 作者公开稿](https://rausavar.github.io/pubs/mask-asplos18.pdf)，DOI 10.1145/3173162.3173169。
阅读状态：补核 §5–7 的机制、预算式、Table 1 原图和主结果，记录 warp 配置疑点；未复现模拟器或重算全部实验。

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

向下游传递翻译请求类别需要哪些属性？优先服务 walker 是否会饿死普通数据？每级页表缓存的命中是否有不同价值？合并 miss 之后应该按“原始客户数”还是“实际下发数”计成本？这些问题分别落在 [VM9](../../UTCL1/sources/VM9-gem5-coalescer.md)、EA、UMC，而非只在 UTCL2 内讨论。以下保存 §5–7 的配置、预算与比较条件，避免接续时只记住性能百分比。

## token、旁路与反馈的具体控制

epoch 为 100K cycles。第一个 epoch 不启用 TLB bypass，用观测结果启动分配；每个应用的初始 token 数取该应用 warp 总数的 80%。所有 warp 都查询 L2 TLB，只有持 token 的 warp 可以向它填充；与此同时查询一个 32-entry、全相联 LRU bypass cache，只有无 token 的 warp 向后者填充。因此“禁填 L2”不等于“禁查 L2”，也不等于停止 page walk。

miss rate 相比上一 epoch 增加超过论文所写 2% 时减少 token，下降超过 2% 时增加，处于阈值内不变；保持较低 warp ID 的 token 有助于跨 epoch 延续性。该处没有给出每次增减的精确步长，2% 的实现口径也应结合模拟器确认，不应自行补成固定增减一个或两个百分点。更新 PTE 时，论文清空 TLB 和 bypass cache 的全部内容；这不足以代替完整系统 shootdown 协议。

给内存请求增加 3-bit page-walk 深度属性：0 为普通数据，1–6 为对应层级，7 表示更深层级。按层级比较翻译数据与普通数据在 L2 data cache 的命中率，低收益层级不占用该数据缓存。该机制跳过相应翻译数据在数据 L2 的查询与填充，不取消页表权限检查。

## DRAM 预算公式、状态与边界

每通道 Golden/Silver/Normal 分别为 16/64/192 项；Golden 用 FIFO，Silver 与 Normal 用 FR-FCFS，严格优先级依次递减。一个应用占有 Silver 服务机会的请求预算，式 (1) 为：

`thresh_i = 500 × (ConPTW_i × WarpsStalled_i) / Σ_j(ConPTW_j × WarpsStalled_j)`。

ConPTW 记录应用并发 page walks；WarpsStalled 反映 TLB miss 关联的阻塞 warp，论文使用按应用的 6-bit 并发计数；每个 TLB MSHR 另有 6-bit 计数，记录命中该 miss 条目的最大 warp 数，相关计数每 epoch 重置。预算既关心翻译并发量，也关心每个 miss 的影响面，不等于按实际内存请求数平均切分。

例如两个应用权重为 4×8 和 2×4，代入得 400 与 100；这是解释公式的计算例，不是论文测量值。原式没有完整规定分母为零、整数取整、计数饱和的实现处理，复现时需查实现或明确补充假设。Golden 的高优先级在原评估中有效，但不构成任意持续翻译洪泛下 Normal 永不饥饿的形式化证明。

## 模型配置、基线和指标

Table 1（PDF 第 8 页）和 §6 使用 Mosaic/GPGPU-Sim 3.2.2、NVIDIA Maxwell 风格研究配置，不是 AMD UTCL2 测量。

| 资源 | 原文配置 |
| --- | --- |
| 计算侧 | 30 cores，64 execution units/core，1020 MHz，9-stage pipeline，GTO |
| 私有 L1 data / L1 TLB | 16 KB、4-way、1 cycle / 64-entry 全相联、1 cycle |
| 共享 L2 data / L2 TLB | 2 MB、16-way、16 banks、每 bank 2 ports、10 cycles / 512-entry、16-way、2 ports、10 cycles |
| page-walk cache / walker | 8 KB、16-way、10 cycles / 64 并发 walk、4-level 页表 |
| DRAM | GDDR5 1674 MHz，8 channels、每 rank 8 banks、每通道 1 rank、BL8、FR-FCFS |

**原图 Table 1 确实写着“64 threads per warp”**。这与常见 NVIDIA warp 认识不一致，暂按原表记录为需对照模拟器核实的疑点；不能悄悄改成 32，也不能据此声称论文实现 AMD wave64。

应用取自 CUDA、Rodinia、Parboil、LULESH、SHOC 等共 27 个程序，组成 35 个随机双应用组合；排除两个应用的 L1/L2 TLB miss 都低于 20% 的低压力组合。较快的应用重新启动以持续制造竞争，不能把此选样解释为所有 GPU 工作负载的平均收益。用 oracle 搜索 core partition 以最大化 weighted speedup，单跑基准使用相同 core 数；除 Static 基线外，不同时给 L2/memory 作静态分区。

Static 使用 oracle core 分配和等分的共享资源；PWCache、SharedTLB、所有翻译都 L1 命中的 Ideal 是不同基线。另有 MASK-TLB、MASK-Cache、MASK-DRAM 消融以分离三项机制。Weighted speedup 为 `Σ IPC_shared,i / IPC_alone,i`；公平性采用最坏 slowdown `max(IPC_alone,i / IPC_shared,i)`，不能混成普通 IPC 百分比。

§7 主结果：完整 MASK 的平均 weighted speedup 比 SharedTLB 高 **57.8%**，仍比 Ideal 低 **23.2%**；最坏 slowdown 所表示的不公平程度比 **SharedTLB** 降低 **22.4%**。这两项主结果均以 SharedTLB 为对照，但指标不同，不能把 weighted speedup 与最坏 slowdown 混为同一种增益。以上是原论文报告，未重新运行模拟器；完整缺页恢复和低开销失效机制仍在该工作的范围之外。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
