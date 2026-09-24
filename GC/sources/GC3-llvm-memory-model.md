# GC3：LLVM AMDGPU 内存模型：等待、缓存维护与一致性域

更新日期：2026-09-24。

导读：解释 acquire/release 为什么需要组合等待与 cache 操作，以及 gfx90a/gfx942 的 agent、L2 和远端内存条件。研究“写完成”“缓存可见”“TLB 失效”之间的区别时应优先读。
来源：[AMDGPUUsage.rst，LLVM llvmorg-18.1.7](https://github.com/llvm/llvm-project/blob/llvmorg-18.1.7/llvm/docs/AMDGPUUsage.rst)。新增资料。
阅读状态：精读 Memory Model 总论与 GFX90A、GFX942 的结构/一致性说明；未逐行验证全部编译序列表或后端代码，未编译测试。

## 三层问题不能合并

第一层是语言/LLVM ordering：acquire 限制后续相关访问提前，release 限制此前相关访问后移。第二层是本线程已发出的操作是否达到所需完成点，例如相应 `s_waitcnt`。第三层是其他观察者会不会读到自己 cache 中的旧值，或者生产者的脏数据是否仍留在局部 cache。等待与 cache 维护分别处理这些问题，单个“fence”名称不能替代全部条件。

本资料中的指令序列以一个线程执行的顺序为语境，也可能需要额外的等待来保证寄存器数据就绪。它不是一个全芯片任意请求的 drain 命令清单，更不是 GPUVM TLB 失效规范。

## GFX90A 的结构依据

向量/标量 L1 并不互相一致，标量访问通过受限使用场景维持编程模型。L2 为同一 agent 的 CU 共享，且存在独立通道和每 CU 的通道请求队列，不同 CU 的操作可以相对重排。因此同一 agent 共享 L2 不等于任意线程已经同步，也不等于无需 L1 维护。

跨 agent 的行为取决于内存相对该 L2 是 local 还是 remote，以及 MTYPE、PTE C-bit 和平台 probe 条件。文中具体讨论 local RW/CC、remote NC 配合 C-bit 或 UC。local line 可因远端 coherent write 的 probe 而失效；remote NC line 可能仍需显式 invalidate。不要把“RW”“CC”“NC”脱离代际和地址位置画成统一的强弱包含关系。

在这里，`buffer_wbl2` 用于相关脏 L2 line 的写回；`buffer_invl2` 对 remote NC 等需要的缓存内容做失效。CC write-through、UC bypass 会改变是否产生相应脏 line，但不能从“没有脏 line”推定操作不需要保序或完成等待。CPU 通过 XGMI cache GPU memory 的情况还依赖 probe filter 和地址属性。

## GFX942 的重要变化

GFX942 可以配置为多个较小 agent，也可以在较大 agent 内含多个独立 L2。于是“同一个 agent”不保证“同一个 L2”。文中区分 agent 内跨 L2 与跨 agent 的 writeback/invalidate 指令条件；例如 single-L2 配置下某些 agent 范围操作可以无实际 L2 工作，多 L2 时则需要维护。

`sc0/sc1` 必须按指令解释。在 atomic read-modify-write 中，sc0 还用于是否返回旧值，不能直接照搬普通 load/store 的 cache 含义。论文或方案若只写一个泛化的“SC 位控制缓存”，会遗漏这个重要条件。

## 一个原创的联系分析

生产者先写 payload，再发布 flag；消费者观察 flag 后读取 payload。需要分别证明：生产者旧写在发布前达到要求的可见域；flag 的同步语义成立；消费者随后读 payload 不会命中不允许的旧副本。仅等待 flag 指令完成、仅清 TLB、或仅发出中断都不能独立证明三项。实际指令序列必须选同一 gfx、scope、地址空间和内存属性对应的表。

## 后续可以直接复用什么

GC/DF 复用 agent–L2–local/remote 的划分；UTCL2 把翻译维护与数据一致性分开；HDP/SDMA/CF/IH 的完成研究先明确 observer 和可见域，再讨论具体 flush/fence。需要写可执行指令、建立具体 happens-before 证明或推广到新 gfx 时，回读相应序列表及 ISA；本笔记没有宣称 shaobo/anshi 支持这里所有机制。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
