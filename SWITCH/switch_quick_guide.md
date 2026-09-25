# Switch / NoC / Die-to-Die：六个问题快速理解

> 版本 2.1，2026-09-25。已同步第三轮 NI 契约，对应同目录的 [详细微架构文档 v2.3](switch_detailed_guide.md)。
>
> 本篇用于建立结构和快速复习；FIFO、VA/SA、credit、包头、逐拍时序、D2D 重放和完整算例见详细版。所有标为 R0/R1 的参数都是教学参考设计，不是 AMD、Arm 或 UCIe 的固定实现。

## 1）为什么需要这个模块？没有它会遇到什么问题？

多个 CPU、GPU、SDMA、NPU 等请求方，需要访问多个缓存、存储控制器和外设。全部直连会增加连接和物理集成复杂度；共享一条简单总线又可能限制并行访问。互联需要让不同目标的流量并行，让争用同一目标的流量有序竞争，并在下游忙时保存状态而不丢数据。

```text
                 One package

+---------------- Die A ----------------+
| CPU --+                              |
| GPU --+-> NI -> NoC -> D2D gateway    |
| SDMA -+                    |          |
+----------------------------|----------+
                             v
                     Adapter -> PHY
                                 || package channel
                     Adapter <- PHY
                             |
+----------------------------|----------+
|                            v          |
| Memory <- NI <- NoC <- D2D gateway    |
+---------------- Die B ----------------+
```

必须分清：**crossbar 是数据选择矩阵，Router 是带状态和流控的交换节点，NoC 是由多个节点和链路构成的片内网络，D2D 则是跨 die 的连接层次。** 点对点 D2D 链路不天然是多端口 switch；多目的 die 的选择由网关或上层 fabric 完成。

小规模、短距离、独占带宽的场景仍可能适合直连。Switch/NoC 的价值是共享与扩展，不是保证比直连更低延迟。

## 2）主要功能是什么？解决什么问题？

最重要的六件事是：**决定去哪里、决定谁先走、保存暂时走不了的数据、确保下游有空间、保持身份与必要顺序、正确处理完成和错误。**

从内部结构看：

```text
Inputs
  |
  v
Per-input VC FIFOs
  |        |
  |        +-> RC: select output direction
  |        +-> VA: reserve a downstream VC for the packet
  |        +-> SA: select this cycle's input/output transfers
  v
Crossbar -> pipeline/link -> next router
                               |
             returned credits <-+
```

三个动作不能混淆：

| 动作 | 回答的问题 | 资源粒度 |
|---|---|---|
| RC，Route Computation | 下一跳往哪个方向？ | 路径选择 |
| VA，VC Allocation | 这个包使用下游哪个 VC？ | packet 所有权 |
| SA，Switch Allocation | 本周期谁能经过 crossbar？ | flit 带宽 |

D2D 另外需要封装/重组、链路状态、速率转换、PHY，以及所选模式要求的检错和恢复。CRC/replay 是否由 Adapter 提供，必须看协议版本和模式；不能一概套用到 Raw 模式。

## 3）主要上下游是谁？数据和控制怎样流动？

### 正向与反向通路

```text
Read request / write data:
SDMA -> NI -> Routers -> Gateway -> D2D -> Remote NI -> target

Read data / write response:
SDMA <- NI <- Routers <- Gateway <- D2D <- Remote NI <- target

Local control:
next-router buffer pop -> credit -> previous router

D2D control:
remote receive/validation -> ACK/NAK/packet-credit -> sender
```

以上是远端分支；本地访问从 NoC 到本地目标 NI，不经过 D2D。NI 做地址到目的地的映射、transaction ID 管理、admission 和 response 重组。中间 Router 通常只需理解 transport 路由、VC、包边界等信息，不必理解整个软件命令。目标侧可能是缓存/home node、存储控制器、外设或协议桥，具体位置由系统架构决定。

R0 的 admission 是资源承诺：AR 接纳时预约 read-response slot，AW 接纳时预约 write-payload slot 和 B status。W 先出现时先由 backpressure 等待对应 AW；按 AW 接纳顺序收齐数据后再注入。不同 ID 可以有限并发，同一源、ID、读写方向的一笔访问要到最后 R handshake 或 B handshake 才 retire。**收到网络 response、释放写 payload、释放 transaction entry 是不同事件。** 目标 NI 也有有限 record，不能接下请求后再假设返回空间总会出现。

### 多个 requester 有独立 buffer 吗？

**不一定。** 一个 Router 输入可能汇聚很多 requester，而 buffer 按输入端口与 VC 划分。一个 VC 在某段时间归一个 packet，释放后可被另一 requester 使用。按 requester、VF 或租户隔离，需要额外的 NI 队列、配额或资源分区。

### 本文两层包格式

详细版 R0 保留一个 16 B NoC head，用于当前子集的目标/来源、事务号、操作、长度等控制信息；具体旧位段按详细稿附录追溯，扩展身份/属性时须重新核算格式。VC 和 head/tail 属于单跳传输状态。256 B 数据包使用一个 head 加十六个 data flit，共 17 flits；分成 flit 不等于生成了 17 个内存请求。

D2D gateway 重新封装并在远端重建 NoC VC 关系。详细版用原创 LRP-64 解释 replay，再按固定版本/模式比较 UCIe 的职责。NoC flit、教学 cell 和 UCIe flit 的边界分别计算，不能把教学格式当成 UCIe 实现。

## 4）最关键的设计参数和功能是什么？

| 类别 | 必须问清的问题 |
|---|---|
| 拓扑/端口 | 有多少输入输出、走几跳、哪些流量共用出口？ |
| 通路 | flit 宽度、频率、每周期吞吐、流水级数？ |
| Buffer | 按输入、VC、目的输出还是共享池？深度和端口数？ |
| VC/VN | 每类有几个 VC，所有权何时释放，资源依赖怎样隔离？ |
| 仲裁 | packet 级还是 flit 级？两级匹配是否损失并行度？ |
| 流控 | credit 扣在哪一拍，返在哪一拍，反向带宽够不够？ |
| 语义 | ordering、ID 回收、completion、错误、死锁条件？ |
| D2D | 模式、有效带宽、packet credit、replay 窗口、ACK RTT？ |
| 实现 | CDC、reset、电源切换、物理布线与时序是否闭合？ |

### 必须记住的资源区别

**Credit 是槽许可，VC idle 是包所有权空闲。** 某 VC 的已发送数据都被下游取走，credit 可以回满，但如果 tail 尚未结束，该 VC 仍不能给另一包。

详细版 R0 选择五端口、每输入四个 VC、每 VC 八槽、128-bit 数据通路。每输出最多一 flit/cycle，示例频率 1 GHz。R1 为 PRE/POST 依赖隔离增加 VC 类别；VC 数变化也意味着索引位宽、buffer 和状态要一起变化，不能只改一个配置数字。

NI 正确性演算另用每源 4 个 entry、2 个 256 B read slot、2 个 256 B write slot；每目标 2 个 record。slot 空间和 table entry 分别限制 admission，同 ID domain busy 又是另一项约束。这套小配置用于解释有限资源，尚未接入既有 Router 模型，也不是带宽优化结果。

### 延迟怎样算？

先区分首 flit、尾 flit 和完整 transaction。既有模型例子经过三个 Router 服务段，包含终点的 Local 弹出服务；在所选连续流水配置中首/尾到达为 15/31 个模型 edge。若以教学 1 GHz 换算才对应 ns；这不是三个物理 Router 间链路的实测值，也不是包含完整 NI 和目标的 transaction RTT。

D2D 若整包收齐再转发，会新增无法与前一段重叠的等待；若 cut-through，计算和资源依赖都要重新分析。负载下还要加注入等待、VA/SA 等待、credit stall、目标排队和可能的重放。

三个容量公式不要混用：

```text
Router slot requirement ≈ flit rate × credit reuse latency
SDMA outstanding bytes  ≈ payload bandwidth × transaction RTT
D2D replay storage       ≈ link byte rate × ACK latency
```

它们分别约束下一跳 buffer、未完成事务和已发未确认副本。

## 5）与 SDMA 有什么关联？设计 SDMA 应考虑什么？

对于经该互联到达目标的 SDMA 访问，Switch/NoC 及适用的 D2D 分支参与数据与返回路径；真实连接仍须按目标芯片核实。

首先，SDMA 发读之前要预留返回数据和事务表空间。Router credit 只能保护下一跳 FIFO，不会自动防止 SDMA 搬运缓冲溢出。其次，packet/burst 大小、ID 数、outstanding 和 QoS 必须与整条路径匹配；单纯扩大 SDMA datapath 不会突破共享出口的上限。

```text
SDMA issue
  -> NI admission
  -> Router VC available?
  -> credit available?
  -> output arbitration won?
  -> gateway packet slot?
  -> replay window / physical link?
  -> remote NoC / target queue?
  -> response accepted by reserved SDMA buffer?
```

**Fence/完成点尤其重要。** 请求离开 SDMA、D2D link ACK、目标接受写入、达到规定可见性、软件看到完成，是不同事件。Router FIFO 空不等于写已全局可见。cache flush、GCR、IOMMU/TLB invalidation 的语义也不由普通 Router 自动提供。

preemption/reset 时，即使停止新 issue，旧响应仍可能返回。ID、context 和 epoch 不能过早复用。链路重放和事务重试也不同：正常链路重放要消除重复交付，不能把 MMIO 写直接执行两遍。

详细版的教学算例得到 219 ns 读 RTT。在目标 payload 为 12 GB/s、每事务 256 B 时，BDP 初始估计是至少 11 个事务。**这是声明假设下的算例，不是某 AMD/UCIe 产品的参数。**

第三轮的两个 read slot 不满足上述 11 笔在途预算，旧算例也未纳入新 NI 逐 beat 上游交付的全部时序；两者不能拼成该小配置的性能结论。地址无法解码或目标报错时，NI 仍需完整收尾 R/W burst，错误不代表事务回滚或可以任意重发。

## 6）软硬件需要怎样协同？

硬件负责数据运输、资源状态、流控和定义好的协议行为；firmware/driver 建立系统配置、管理流量、处理错误与电源状态。

```text
Initialization:
clock/reset -> PHY/link -> epoch/credit -> route/protection
            -> NI/response resources -> enable SDMA queues

Power-down / reconfiguration:
stop new injection -> drain or coordinated abort
                   -> change state/configuration
                   -> re-establish consistent resources
```

软件应读取能力，配置地址窗口、权限、注入速率/QoS、错误处理和性能计数。不能在线减少已经承诺给在途包的 buffer 资源，也不能只重置本地 credit 而让远端保留旧包。

驱动仍要正确使用 DMA 地址映射、cache 同步和内存屏障。coherent memory、NoC ordering 或 D2D CRC 都不能替代软件发布 descriptor、敲 doorbell 和读取 completion 时的系统排序要求。

## 最后形成这个完整模型

**NI 管事务；Router 管单跳路径、buffer、VC 与周期带宽；网关管理跨 die 的封装和资源边界；链路/PHY 管相应模式下的可靠运输与物理传输；目标模块定义操作的实际完成。**

详细依据及证据边界见 [详细版 v2.3 第 17 节](switch_detailed_guide.md#17-证据模型与后续阅读)，逐篇导读和原文位置见 [SWITCH 资料索引](../SWITCH/sources/README.md)。第三轮的状态/资源推演和算术核查见[核查记录](../SWITCH/round3-review.md)。既有 [reference_checks.py](examples/reference_checks.py) 和 Router 模型继续保留原验证边界，本轮未重跑；它们不是新增 NI 的执行证据，也不是完整 RTL 或 UCIe/CHI 合规验证。
