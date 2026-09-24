# R20：Tamir/Frazier：动态多队列缓冲与共享存储实现

更新日期：2026-09-24。

导读：解释 DAMQ 怎样用每目的队列与共享 free list 同时减少 HOL 和静态分区浪费，保留指针阵列、头尾、分块分配和 cut-through 的关键实现条件。
来源：[High-Performance Multi-Queue Buffers for VLSI Communication Switches，ISCA 1988，作者 UCLA PDF](https://web.cs.ucla.edu/~tamir/papers/isca88.pdf)。
阅读状态：通过公开 PDF 核读 §II–IV 的架构、分配/回收、接收/发送及评价设定；历史字节宽度和工艺速度不外推到当前芯片。

## 为什么需要同时看逻辑队列与物理池

单输入 FIFO 容易因某输出阻塞而挡住其他目的地；每目的地固定切容量则可能一队满、其他队空。完全中央共享又带来多端口带宽、拥塞流占池等问题。DAMQ 在每输入的存储内维护多个目的队列，容量动态从共同 free list 取得，在保持单输入接收边界的同时避免硬分区浪费。

因此“共享 buffer”并不等于“所有端口共用一块无限多端口 RAM”。共享范围、读写带宽和队列数是独立选择，必须与 crossbar 接口能力对应。

## 关键实现结构

存储按固定大小 block 管理，变长 packet 可占多个 block；每 block 有 next pointer，指针阵列与数据阵列分离以便并行访问。每个目的队列和 free list 有 head/tail。接收时取 free block 并链接到相应队尾，发送时从队头沿链读取并把已用 block 归还。

资料案例选择 8-byte block，是元数据/控制开销与内部碎片间的折中，不是通用最优值。块大减少指针操作但浪费尾块空间；块小改善容量利用却增加指针访问、状态机活动和带宽压力。

## cut-through 与元数据时序

包头解析和输出仲裁可与后续数据到达重叠；目的队列为空且输出可用时允许 cut-through。为缩短启动延迟，空队列头指向预期分配位置等元数据安排很重要。接收、路由、发送状态机可并行，但必须同步访问共享寄存器/总线，不能同时破坏同一指针或读写同一字节。

分配成功、完整包到齐、输出选中、block 回收是不同节点。后续在现代 RTL 中还要分析单块包、同时 push/pop、最后一块被释放、free list 空和取消等边界；这是由结构提出的需求，不声称原论文覆盖所有现代错误场景。

## 对当前项目的价值

[C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) EA 图里的共享 cmd/data storage、list manager、size/next/handle 可用这种方法理解，但不能因此断言它采用完全相同算法。方案应画出数据 RAM 与元数据、free pool、逻辑队列的关系，并把端口数/仲裁和队列吞吐一起研究。论文支持架构比较，不是目标 RTL 的证据。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
