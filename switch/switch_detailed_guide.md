# 从可实现微架构理解 Switch：NoC Router、Die-to-Die 与 SDMA

> 版本：2.1；第二轮 Router 专项深化日期：2026-09-24。
>
> 研究进度：第一轮综合基线与第二轮 Router 专项已完成；第三至第六轮尚未完成。版本号、R0/R1 设计编号不代表研究轮次。
>
> 阅读目标：能够在白板上画出一个可以继续细化成 RTL 的 Router，说明缓冲区、状态、仲裁与接口在什么时刻更新；再连接跨 die 网关，解释一笔 SDMA 事务的数据路径、阻塞原因和延迟。
>
> 范围：片内 NoC 与封装内 die-to-die。板级 PCIe switch、以太网与多节点 scale-out 暂不展开。本文不是 AMD 某代 GPU 的内部设计说明，教学参数不能冒充厂商实现。
>
> 版本保留：[第一轮完整原稿](switch_detailed_guide_v2.0.md) 以原 Git blob 留存，内容未删改。本稿重整前 37 章并在第 38—49 章展开第二轮成果；需要查阅第一轮的完整展开说明时使用历史原稿，不把两个版本当作两套并行设计。

## 摘要：先确定要实现什么

互联必须同时解决运输、资源和语义问题：数据从哪进、从哪出；竞争或下游没空间时怎样保存状态；响应属于谁、写入何时完成、重放是否重复执行、请求和响应是否互相等死。

本文定义参考设计 R0：二维 mesh、五端口 Router、输入排队、四 VC、128-bit 数据 flit、信用流控、XY 路由、独立 VA 与 SA。R0 承载有限的非一致性读写，不实现完整 CHI。一套双 die 参考设计 R1 加入网关、整包资源预留、教学可靠链路和跨网络依赖隔离。

第二轮在第 38—49 章继续下钻 Router 的事件提交、allocator、SRAM/共享池、credit 周转和失败路径，并提供真正运行的有限缓冲 mesh 模型。它们是同一篇研究正文的续章，不是另一套互相矛盾的 Switch 定义。第一轮系统、D2D、SDMA 主线在第 1—37 章保留并整理。

全文区分：**来源事实**（附编号）、**本文设计**（明确选择的参考参数/格式）、**推导与检查**（声明假设下的分析和实验）。经典 Router 可参考原始论文和公开模型；实际实现也可以合并 VA/SA，分离流水不是所有产品的强制结构。[R1][R2][R3][R4]

## 阅读路线

| 层次 | 章节 | 目标 |
|---|---|---|
| 系统与数据 | 1—6 | 层级、参考参数、包格式、NI 与目标 |
| Router 基线 | 7—15 | FIFO、RC、VA、SA、crossbar、credit 与逐拍行为 |
| 正确性与实现 | 16—21 | HOL、死锁、QoS、ordering、优化、CDC/复位 |
| 性能 | 22—23 | 首/尾 flit、吞吐、三种 BDP |
| D2D | 24—30 | 网关、重组、重放、PHY、跨 die 依赖 |
| SDMA 与验证 | 31—37 | 完整算例、契约、软件、基线检查与来源 |
| **第二轮核心** | **38—45** | **事件原子性、allocator/存储细节、失败路径与资源依赖** |
| **第二轮执行证据** | **46—49** | **有限缓冲模型、实际测试、资料对照和进度** |

# 第一部分：整体层次

## 1. Switch 不是固定层级的名字

### 1.1 从系统打开到数据选择器

```text
Package / System
+-- Die A
|   +-- CPU / GPU / SDMA / other requesters
|   +-- Translation / protection where required
|   +-- NI / NIU
|   +-- On-die NoC
|   |   +-- Router
|   |   |   +-- input ports and VC FIFOs
|   |   |   +-- route computation (RC)
|   |   |   +-- virtual-channel allocation (VA)
|   |   |   +-- switch allocation (SA)
|   |   |   +-- crossbar / pipeline registers
|   |   |   +-- output-VC ownership / credit state
|   |   +-- forward links / reverse credits
|   +-- D2D gateway / protocol bridge
|   +-- link adapter
|   +-- PHY
+========== package channel ==========
+-- Die B: PHY -> adapter -> gateway -> NoC -> NI -> memory side
```

crossbar 是选择矩阵；Router 还含排队、路由、流控和状态；D2D switch/gateway 可能连接多个 NoC/D2D 端口，选择目的 die。点对点链路本身不必具有多目的地交换能力。问“有几个 buffer”之前，必须先指明方框。

运输一致性消息与承担 directory、home-node、snoop 和完成语义也不同。不能因网络能送某种消息，就认为 Router 实现了其全部协议。

### 1.2 UCIe 不天然等于多端口路由器

```text
Die A: Requester -> NI -> NoC -> Gateway -> Protocol/Adapter -> PHY
                                                               ||
                                                            Package
                                                               ||
Die B: Memory   <- NI <- NoC <- Gateway <- Protocol/Adapter <- PHY
```

UCIe 分层中的协议、Adapter 和 PHY 职责不同；协议复用也不等于任意 die 路由。[R10] CHI-C2C 还把一致性消息封装与所选 transport 分开，不能把普通 CHI 信号直接接任意 UCIe PHY 就当作兼容。[R12]

## 2. 为什么不能只用几组 MUX

```text
SDMA --+             +-- MC0
       +-- SWITCH ---+
CPU ---+             +-- MC1

Different outputs: parallel
Same output: arbitrate
Target stopped: buffer and backpressure
Response returns: recover source and transaction identity
```

组合 MUX 只解决本周期选哪根线，不保存未完成包、响应归属和下游空间。真正互联是数据选择、分布式资源管理与端到端事务管理的组合。

直连不一定错误：IP 少、距离短、带宽独占时可能更合适。NoC 改善扩展与物理集成，不保证比直连更低延迟。

## 3. 固定 R0 的边界与参数

以下为本文设计，后续算例必须沿用这些选择，不可把论文或产品参数随意混入。

| 项目 | 选择 | 含义 |
|---|---|---|
| 拓扑 | 单 die 4×4 mesh | 无 wraparound，不是 torus |
| 端口 | N/E/S/W/Local，最多五入五出 | 各方向收发分别有通路 |
| 数据 | 128 bit = 16 B/flit | 不含 valid、VC、H/T 边带 |
| 速率 | 每输出每周期最多一 flit，示例 1 GHz | 不是 STA 结果 |
| VC | 每输入四个 | 请求 VN 两个，响应 VN 两个 |
| Buffer | 每 VC 八槽，寄存器 FIFO | 不是未说明端口的 SRAM 宏 |
| input VC 占有 | 一个 VC 同时归一个 packet | local tail pop 后可释放 |
| output VC 复用 | 等下游 tail-free credit | 不在本端 tail 发出时立即复用 |
| 路由 | XY，先 X 再 Y | head 计算，body/tail 继承 |
| 仲裁 | 独立 VA；SA 两级 RR | packet 资源与 flit 带宽分开 |
| 事务 | 16 B 对齐、16 B 倍数、最多 256 B | 不含任意 byte enable、原子、snoop、多播 |
| 地址 | 已完成所需翻译的 48-bit 地址 | Router 不执行页表遍历 |
| ordering | 普通事务可独立乱序；ordered 流限制并发 | 不把 FIFO 当完整内存模型 |
| 错误模型 | 正常片内 flit 不丢失；严重异常受控恢复 | 不表示物理电路永不出错 |

一个 Router 同时从 West 接收和向 West 发送使用不同逻辑方向。R0 扩展成完整 CHI 还需要节点职责、一致性状态与消息依赖；装得下字段不等于实现协议。

# 第二部分：数据包与端点

## 4. Transaction、packet、flit 与物理传输

```text
SDMA command
 +-- read transactions
 +-- write transactions
 +-- completion/fence sequencing

One transaction -> request packet + response packet
One data packet -> [HEAD][DATA0] ... [DATA15 / TAIL]
One flit        -> one or more physical transfer units
```

transaction 可产生多个 packet；packet 可分为多个 flit；flit 是否一拍送完取决于通路宽度与时钟。phit 常用来表示物理传输粒度，但并非各规范都使用相同名字或大小。

R0 一条 128-bit 通路一拍一 flit；若只改成 32-bit 通路，通常需四个传输节拍，不能仍假定原带宽。

### 4.1 原创 128-bit head 格式

这不是 AXI、CHI 或 UCIe 标准格式。

```text
127:120  119:112  111:100  99:96  95:92  91:84  83:80
 DstID    SrcID     TxnID    Op     QoS    Len-1   Attr
79:32                    31:16       15:8       7:0
 Address                  Context    Epoch      Status
```

| 字段 | 宽度 | 定义 |
|---|---:|---|
| DstID / SrcID | 各 8 | `die[3:0],y[1:0],x[1:0]`，指 NI/节点 |
| TransactionID | 12 | 在源 NI 有效事务集合中标识一次事务 |
| Op | 4 | 0 读请求，1 写请求，2 读响应，3 写响应，4 错误 |
| QoS | 4 | 预留分类；基线 RR 不冒充带宽保证 |
| Length-1 | 8 | 有效字节数减一；无数据确认忽略 |
| Attr | 4 | 示例 ordered、privileged、两位安全域 |
| Address | 48 | 目标地址；响应按规则回送或置零 |
| Context | 16 | NI 分配的上下文标签，不直接等于 AMD VMID/PASID |
| Epoch | 8 | 受控重启世代，回绕前需排除旧包 |
| Status | 8 | 请求置零；响应表明结果 |

多个 requester 汇入一个 NI 时，NI 保存原 requester/ID/ordering stream 与内部 TransactionID 的映射。Router 不必按软件 queue 名称分配固定 FIFO。有限位宽 epoch 不是无限期防旧包机制，回绕必须配合系统生命周期。

### 4.2 单跳边带

```text
Forward: valid, data[127:0], vc[1:0], head, tail
Reverse: credit_valid, credit_vc[1:0], vc_free
```

H/T 表示包边界，VC 指定接收 FIFO。VC 编号逐跳重新分配，不是端到端身份。FIFO 按 VC 分 bank，因此每槽存 128-bit data 加 H/T，不必再存自身 bank 号。

裸存储：`5×4×8×130=20,800 bit=2,600 B`。不含指针、route、head cache、credit、流水寄存器、ECC 与实现浪费，不是最终面积。

### 4.3 包长度

```text
256 B ReadReq:   [HEAD_TAIL, Length-1=255]                  1 flit
256 B WriteReq:  [HEAD][16 B] ... [last 16 B,TAIL]         17 flits
256 B ReadRsp:   [HEAD][16 B] ... [last 16 B,TAIL]         17 flits
WriteRsp/Error:  [HEAD_TAIL]                               1 flit
```

读请求里的长度是请求读取的数据量，不代表请求包携带那些数据。实际包长由 Op 与长度共同确定。256 B 数据包经过主数据通路共 272 B，效率 `256/272=94.12%`，尚未计空拍等开销。

## 5. NI：事务管理不能都推给 Router

```text
Requester interfaces
      |
+-----v---------------------------------------------------+
| admission / alignment / address and protection checks    |
| address-to-DstID map; transaction table / ID translation |
| ordered-stream issue gate; response reservations        |
| packetizer -> VN/VC injection                           |
| depacketizer <- response buffers -> completion delivery  |
+---------------------------------------------------------+
      |
Router Local interface
```

### 5.1 事务表

每有效项至少保存原 requester/ID、context、epoch、op、目的地、预期/已收字节、响应 buffer slot、ordering stream 和 completion 状态。在不可撤销地接受新事务时就必须落实表项，不能先承诺再发现没空间。

请求离开 NI 后表项仍然有效；完整响应按上层规则交付、错误收尾完成后才复用 ID。响应 head 到达不等于所有 body 已被接收。

### 5.2 保守注入规则

写请求在 NI 收齐 payload 后再注入；读请求在分配完整返回空间后再注入。这样 head 已占网络资源却无限等本地数据的风险限制在 NI 之前。

代价是 NI 包级 buffer 与首包延迟。流式写可优化，但要重新定义生产者前进、取消包与部分状态释放规则。

### 5.3 响应空间与请求资源

```text
Bad cycle:
response cannot enter -> waits for write issue
write issue blocked -> request network waits for response drain

R0 rule:
reserve response space before read issue
response ejection must not require issuing another request
```

SDMA 可把已收数据放自己的搬运 buffer，再等写口；不能因写拥塞撤销已承诺的读返回空间。第二轮第 42、45 章进一步讨论共享容量如何破坏这种隔离。

### 5.4 ordered 流

对需要保持完成顺序的 `(requester,context,stream)`，最简实现同一时刻只放行一个相关事务，定义的完成后再发下一个。普通独立流可多 outstanding。

这不是完整 AXI 的替代品，不自动提供不同 requester 间全局排序；它只是使 R0 的有限子集语义明确。

## 6. 目标端的最小闭环

```text
ejection -> reserve request slot -> reconstruct packet
         -> access target -> wait for defined completion
         -> response {Dst=old Src, Txn=old Txn} -> Response VN
```

目标 NI 需要重组、合法性检查、接口转换、返回信息、响应空间及错误能力。可先把 target 定义为受控 SRAM：读数据取出后响应；写入完成且随后该控制器的读可见后响应。

换成缓存、DRAM、posted-write 桥，就须重新声明完成点。非法地址/权限/操作可返回相关 ErrorRsp；Router 内部损坏包边界不能靠随便丢一个 body 处理。

# 第三部分：Router 基线

## 7. 数据面与控制面

```text
             RC -> VA -> SA-I -> SA-II
                        |          |
                        +-- grants +
                              |
IN0 -> [VC0..3 FIFO] -> VC MUX-+
IN1 -> [VC0..3 FIFO] -> VC MUX-+
IN2 -> [VC0..3 FIFO] -> VC MUX-+-> 5x5 XBAR -> ST/LT -> OUTs
IN3 -> [VC0..3 FIFO] -> VC MUX-+
IN4 -> [VC0..3 FIFO] -> VC MUX-+

input pop -> upstream credit
returned downstream credit -> output-VC state
```

数据通常留在 FIFO；RC/VA/SA 处理头信息、状态和请求向量。获得最终资格后才读出并经过 crossbar。五输入可同时各收一 flit，五输出也可同时各送一 flit，但每物理输入和输出本拍都最多参与一次传输。

## 8. Input VC FIFO 与 requester 的关系

```text
Requester A/B/C -> upstream NI/router -> one West input
                                          +-- Req VC0
                                          +-- Req VC1
                                          +-- Rsp VC2
                                          +-- Rsp VC3
```

一个输入汇聚多个来源；四个 VC 不等于四个 requester。packet 临时占一个 VC，释放后可供另一来源使用。VF/租户隔离需 NI 队列、quota 或资源分区，不能从 VC 数直接推断。

### 8.1 每 VC 状态

| 状态 | 用途/更新 |
|---|---|
| mem、rd_ptr、wr_ptr、occupancy | 数据/队列位置，按 push/pop 更新 |
| packet_state | IDLE、RC、WAIT_VA、ACTIVE |
| route_out、assigned_outvc | RC 与 VA 的已提交结果 |
| VN、head_sent | 类别与包首是否已发送 |
| QoS/age | 可选调度信息 |
| 边界/错误状态 | 检查非法 head/body/tail |

occupancy=0 不等于 IDLE：head 已走、body 暂未到时，route 和 ownership 仍必须保留。

### 8.2 同拍 push/pop

```text
count_next = count + push - pop
rd_next = pop  ? (rd+1) mod D : rd
wr_next = push ? (wr+1) mod D : wr
```

D=8 的指针三位，表示 0—8 的 count 需四位。满时一进一出是否可接受，要按接口承诺；上游不能借一个尚未返回的本拍 pop 擅自发 flit。

### 8.3 存储端口是架构的一部分

寄存器 FIFO 可提供组合队头；同步 SRAM 可能需要额外读阶段、预取、bank 仲裁和明确的同址读写语义。第 41 章进一步给出 head cache、landing register、复制/搬移式预取的区别，第 42 章展开真实共享池。

## 9. RC：选择方向，不分配空间

```text
if dst.x > x: East
elif dst.x < x: West
elif dst.y > y: North
elif dst.y < y: South
else: Local
```

North 对应 y 增大是本文坐标约定。NI 做 Address->DstID，Router 做 DstID+当前位置->下一跳；每个中间 Router 不必存全系统地址表。

RC 结果保存，body/tail 继承，不独立改道。NI 检查目的节点有效性，边界 Router 禁止向不存在端口送包。异常时任意绕路可能破坏 XY 的依赖约束。

Adaptive routing 还需拥塞信息、选择规则、escape 资源和依赖证明；本轮不以一个“选较空队列”替代完整设计。

## 10. VA：预订下一 Router 的 VC

```text
input West.VC0 -> East output -> next router West.{VC0,VC1}

VA: reserve one downstream VC for a packet
SA: reserve one actual cycle of physical bandwidth
```

每输出 VC 保存 IDLE/RESERVED/DRAIN_WAIT、owner 与 credit。它是下游输入资源的本地镜像。credit 回到 D 时，packet 仍可能未发 tail，因此 ownership 不能只从 credit 推断。[R6]

R0 简单算法：每 WAIT_VA input VC 提名一个合法空闲 output VC；每被提名 output VC 做 RR；赢家同边沿更新双方映射。输入 VC 不会拿到两个 grant，输出 VC 不会被重复授予。不同输入 VC 可同时拿同一物理输出的不同 VC，但不承诺同拍送数据。

候选选择需轮转/前进规则；匹配可能非最优。多拍 VA 要防旧空闲状态导致双重预订。第 39 章给出矩阵、位宽和 reservation 的进一步实现细节。

## 11. SA：解决本周期真实冲突

eligible 至少需要非空、ACTIVE、route 与 output VC 有效、credit>0、阶段就绪、链路可提交及必要 ordering gate 通过。

```text
SA-I : choose one eligible VC per physical input
SA-II: choose one nominated input per physical output
```

只做每输出 arbiter 可能让同一输入的两个 VC 同拍赢不同输出，但输入只有一个读口。合法 grant 满足每输入/输出的求和均≤1。

示例：I0.VC0->E、I0.VC1->N、I1.VC0->E。如果 SA-I 都提名 E，SA-II 选 I1，N 会闲置；其实 I0->N、I1->E 可以并行。这说明非阻塞 crossbar 不保证 allocator 总找到最好匹配。

Garnet 有相应两级结构，但它在胜出的 head 路径合并分配 VC，与 R0 独立 VA 不同。[R5] 第 40 章对照 iSLIP、maximal/maximum 与 pointer 更新。

## 12. RR 的 request、grant、commit

```text
winner = first asserted request scanning from pointer, wrapping around
if actual_transfer_commit:
    pointer_next = (winner + 1) mod N
else:
    pointer_next = pointer
```

可综合实现可用 mask、旋转与优先编码，不是要求电路顺序执行软件循环。没有真实传输时不要按“看起来被选中”更新公平性状态。

R0 的 commit 原子 pop、扣下游 credit、更新指针、返回上游槽 credit、锁存 ST 数据/元数据。若输出可停住，则 grant 可能不等于 commit。第 38 章给出完整事件冲突表。

孤立、持续可服务的 RR 有轮转公平性；动态完整网络不因此获得固定端到端 deadline。

## 13. Crossbar 与流水元数据

一个直观 5×5、128-bit 实现是每输出一个 5:1 宽 MUX。输入侧先从四个 VC 选一个，因此 VC 增多不必让 crossbar 变成 20×20，但会增加存储、状态与仲裁成本。

ST/LT 必须锁存 data、valid、output、outvc、H/T。tail pop 后本地 VC 可复用，旧 tail 还在 pipeline；若旧 tail 此时回读新的 route，就会误送。

五拍首 flit 延迟不等于每五拍才能发一 flit，流水稳态可以一拍一 flit。反之单拍大组合逻辑可能降低频率，必须以 ns、有效吞吐和物理实现共同评价。

## 14. Credit：分布式容量守恒

```text
A output credit -- charged at SA --> forward ST/LT --> B input FIFO
        ^                                               |
        +-------------- reverse credit <------ B pop ----+
```

credit 是许可而非瞬时下游探测；扣减在不可撤销的 SA commit，不能等真正离开长流水线才扣。

```text
C = available permissions
F = charged forward flits, including ST/LT
Q = downstream stored flits
R = freed slots whose credits are returning
C + F + Q + R = D
```

每一步搬 token：C->F->Q->R->C。同拍 send 与 return 可以让 C 不变，但两个事件都须记账；未定义的同拍 credit 旁路不能靠模拟器执行顺序偷偷加入。

普通 pop 返一个 slot；tail pop 返 slot 加 free。input VC 在自己的 tail pop 后空闲；上游 output VC 等 free 真正返回后才复用。BookSim 对不同复用策略有明确区分，R0 选择保守模式。[R3][R19]

每输入每拍最多 pop 一 flit，因此反向每拍一个携带 VC/free 的事件可承载该速率。若提高内部读口或 speedup，也须提高 reverse 带宽或加事件队列。反向 credit 不应依赖会被它自己堵住的普通数据 packet。

第 42—43 章把这一守恒推广到共享容量，并用有限网络检查复算延迟。

## 15. 状态机与逐周期例子

```text
Input VC:
IDLE -> RC -> WAIT_VA -> ACTIVE ->(tail pop)-> IDLE
                        ^  |
                        +--+ ordinary pop or temporary empty

Output VC:
IDLE -> RESERVED ->(local tail commit)-> DRAIN_WAIT
 ^                                           |
 +-------- downstream free credit -----------+
```

body 可在 WAIT_VA 时继续进入合法预留空间；ACTIVE 暂时空 FIFO 不释放。HEAD_TAIL 经正常 RC/VA/SA，在第一次 pop 同时结束。IDLE 收 body、ACTIVE 收另一个 head、H/T 数不符都是边界错误。

| 时刻 | head 行为 |
|---|---|
| edge 0 | 捕获到输入 FIFO |
| [0,1] / edge 1 | RC / 保存 route |
| [1,2] / edge 2 | VA / 保留 output VC |
| [2,3] / edge 3 | SA / pop、扣 credit、锁存数据 |
| [3,4] | ST / crossbar |
| [4,5] / edge 5 | LT / 下一节点捕获 |

无竞争、足够 credit 时 body/tail 按一拍间隔跟随。三跳首 flit edge 15，17-flit 包尾 edge 31，不是把 F、H 与所有阶段串行相乘。

一个 credit 例子：A edge3预留、B edge5收到、edge8 pop、A edge9捕获返回、最早 edge10再次提交，约七拍许可闭环。D=8 只是本例有余量，竞争/长链路可能使其不足。

单 flit 包仍要等 VC 所有权释放。按保守时序，一个 output VC 从 edge2分配到 edge10能再次分配，周转约八拍；一个 VN 仅两个 VC，短包吞吐可能受约2/8 packet/cycle限制。深 buffer 不等于有更多 packet ownership。第二轮模型更精确地区分尾到达、消费与 drain。

# 第四部分：正确性与实现

## 16. HOL、VOQ 与共享存储

```text
[A -> blocked East][B -> free North][C -> free Local]
 ^ single FIFO can only read A
```

多个 VC 可把独立 packet 的阻塞分开，但包内 body 不能越过 head。组织选择包括单 FIFO、每输入多 VC、按目的输出 VOQ 和 shared pool。

VOQ 减少不同目的地 HOL，代价是队列与匹配复杂度。shared buffer 提高容量利用，必须补齐 free list、队列描述符、多口/bank、指针并发更新和最小保留份额。第 41—42 章给出可以继续实现的结构与同拍更新表。

已授出的 credit 是不可随意撤销的容量承诺；某 VC 的空间不能因另一流增加而被直接拿走。更多 buffer 只吸收短突发，不创造持续出口带宽，且可能加大排队延迟。

## 17. Deadlock：画资源等待图

把可持有资源作为节点；持有 A 等待 B 就画 A->B。确定性路由中利用无环通道依赖建立死锁规避，是经典设计方法。[R13]

```text
VC_ab -> VC_bc -> VC_ca -> VC_ab
```

mesh XY 不允许完成 Y 阶段后回到 X，且无环回边。第一轮脚本枚举4×4所有源目的路径得到48有向通道、68依赖边并可拓扑排序；这只检查该模型，不含复杂 endpoint/协议资源。

请求等响应、响应等请求空间可能形成另一类环。R0 分请求/响应 VN，并在 NI 保留响应接收资源，使响应消费不依赖再发新请求。两 VN 并非所有协议的通用答案。第二轮第45章把共享池和 endpoint 等隐藏资源加入分析。

死锁、饥饿、活锁不同：前者循环等待，第二种某流拿不到服务但别人前进，第三种不断移动/重试却不完成。公平 arbiter 不能消除结构性环，大 buffer 也不能。

## 18. QoS 不只是四个 bit

基线 QoS 字段预留，纯 RR 不提供硬实时保证。扩展可由 NI token bucket 限流、output class scheduler、类内 RR 组成。

```text
NI rate/burst limit -> eligible class selection -> within-class RR
```

按包、flit、byte 计权重得到不同带宽公平性。固定优先级有饥饿风险。端到端 deadline 还要求每个瓶颈和目标有明确服务约束，单 Router 优先级不够。第40、45章继续讨论匹配与观察指标。

## 19. 对照 AXI、CHI 与公开 NoC

### 19.1 AXI4 桥接

AXI4 有独立读地址、读数据、写地址、写数据、写响应通道；其 ID 与 ordering 有具体约束，不能简化为“相同 ID 所有读写全局自动有序”。AXI4 写数据不靠 WID 任意交织，burst/边界与握手也要遵循规范。[R8]

```text
AW FIFO --+-> write assembler -> internal WriteReq
W FIFO ---+
AR FIFO ----> transaction map -> internal ReadReq
internal responses -> optional reorder -> original R/B interfaces
```

R0 有限桥先保存 AW 上下文、按对应顺序收齐 W，检查对齐/长度后封装。读侧保存 ARID 映射。R0 不含任意 WSTRB、exclusive、所有 burst，因此要限制接受子集或显式转换，不能静默丢属性。

### 19.2 CHI 只是概念对照，未完成协议实现

CHI 有 REQ/RSP/SNP/DAT，字段与消息职责不同。旧版 Protocol Bundle Guide 可用于识别接口信息，但其中 C++ 类型不是最新规范线上位宽。[R9]

REQ涉及操作、地址与事务；RSP涉及控制/完成；DAT含数据身份及状态；SNP涉及一致性请求。链路 credit 与事务级 retry 等资源机制也不能全等同 R0 槽 credit。

运输 CHI 与实现 CHI 不同：后者需节点角色、一致性状态和消息依赖。第三轮仍须锁定协议版本和子集逐项映射。

### 19.3 FlooNoC 的对照价值

FlooNoC 论文与公开 RTL 可用于观察宽链路、端点事务处理、FIFO 与可配置物理/虚拟通道的另一种组织。[R7][R15] 不应把论文版本与后来 main RTL 混成冻结设计，也不应认定所有 NoC 必须窄化序列化。

## 20. 流水优化必须补失败路径

look-ahead 把下一跳 RC 提前，但增加元数据/检查责任；推测 VA+SA 允许并行，却必须在 VA 失败时取消 SA，不 pop、不扣 credit；bypass 需同时满足旧数据顺序、容量、输出空间与唯一接受点。[R1][R2]

合并 VA/SA 改变候选和匹配，Garnet 是具体实例，而不是把基线某阶段“设成零拍”即可。[R5] BookSim 的求值/更新区分也提醒，模拟器不得提前看到本拍尚未提交的状态。[R3]

第44章给出结果表、非推测优先、fallback 和弹性缓冲分支。本轮没有完成这些优化的全网 RTL/仿真实现。

## 21. CDC、reset、电源与错误

跨时钟域宽数据不能每 bit 独立过两级同步。常见异步 FIFO 使用双口存储与同步指针，必须规定编码、满空判断、复位顺序和实际延迟。

```text
Clock A write -> dual-clock storage -> Clock B read
       <------- synchronized pointer views ------->
```

CDC 只吸收有限速率差，长期慢端仍会反压，并可能扩大 credit RTT。reset 时若 A把C重置成D而B保留旧数据，就会覆盖。应先停止注入，drain或协调abort，再共同建立容量和epoch；致命故障需要相关域状态一致恢复。

非法地址是可返回事务错误；FIFO ECC、非法VC、缺tail、credit overflow可能破坏运输完整性。片内可以有parity/ECC/poison/retry，不能笼统说无需可靠性；跨die持续故障也不能无限重放。

# 第五部分：延迟与容量

## 22. 先定义测量边界

| 指标 | 起止 |
|---|---|
| 一跳head | 当前输入捕获到下一跳输入捕获 |
| 单向首flit | 指定源NI接受/注入点到目标首项到达 |
| 完整packet | 指定起点到tail接收 |
| 读事务RTT | 接受请求到完整响应完成 |
| SDMA copy | 命令定义起点到数据/通知定义完成点 |

PHY datapath latency 不等于远端HBM访问延迟。无竞争、同宽虫洞路径：

```text
T_head = injection + H * Lhop + ejection
T_tail = T_head + (F-1) * flit_service_interval
```

要求无credit气泡、排队、速率转换或整包等待。store-and-forward边界须另计完整前段等待；普通流水不能每hop重复增加整包serialization。

有负载时需考虑 admission、VA、SA、credit、conversion、endpoint，但同拍原因可重叠，不能把counter无条件相加。接近瓶颈服务率时backlog难排空；有限FIFO会把等待传回NI/SDMA，而非自动消失。应看offered/admitted/completed和p50/p95/p99，不只看网络内部平均值。

## 23. 三种不同的 BDP

R0裸数据通路单向 `16B/cycle×1GHz=16GB/s`，256B数据packet理想payload约15.06GB/s。五口不能都把完整独占带宽送给同一单口MC，全双工也不能合成单向数字。

```text
Router slot BDP  ≈ flit rate * credit reuse latency
Transaction BDP  ≈ payload bandwidth * transaction RTT
Replay BDP       ≈ link byte rate * ACK latency
```

第一个约束下一跳许可，第二个约束SDMA/NI未完成事务，第三个约束已发未确认副本。它们可能都叫outstanding，但对象与释放点不同。更多VC也要考虑packet所有权周转；只扩大D未必改善短包。

# 第六部分：跨 die 的新增微架构

## 24. 网关不是加长导线

```text
Local NoC -> TX gateway -> link/PHY -> RX gateway -> Remote NoC
               |                          |
      packet slots/VN isolation     reassembly/new VC injection

local credits      link resources       remote NoC credits
```

R1暂只支持两die点对点，一packet最多跨一次。网关终止本地VC，在远端重新申请，不保持端到端VC编号。两侧都采用收齐整包后转发，head接受时预留完整packet slot，避免收半包后永远等剩余空间。

更低延迟cut-through可能可行，但要重新分析重放、远端credit、部分包状态和依赖，不能无条件删buffer。

R1 record增加8B header：version1B、record length2B、VN/class1B、src die1B、dst die1B、flags1B、reserved1B；多字节大端。读请求record24B；256B数据record280B。长度包含整个record。

NoC VC/H/T边带不逐bit原样运输，远端根据合法Op、长度及record边界重建。必须交叉校验长度一致。

## 25. 原创可靠链路 LRP-64

> LRP-64 是教学协议，**不是 UCIe 帧格式，不声称互操作**。用它把CRC、sequence、ACK、replay和接收承诺的关系讲完整；实际UCIe对照见第28章。

### 25.1 80 B cell

```text
[12 B header][up to 64 B payload, zero padding][4 B CRC32C]
```

| 字节 | 字段 |
|---|---|
| 0 | version/type，高4位版本1，低4位Data/ACK/NAK/Credit |
| 1 | class：0请求、1响应 |
| 2—3 | 16-bit sequence |
| 4—5 | ACK-next，累计确认后应发的下一个序号 |
| 6 | payload length 0—64 |
| 7 | SOP/EOP/ACK-valid flags |
| 8—9 | 累计returned-packet-credit total |
| 10—11 | link epoch |
| 12—75 | payload/padding |
| 76—79 | 覆盖前76B的CRC32C，大端编码 |

同VN record顺序发送、不交织两个record；不同VN可逐cell交替。每VN独立seq、expected、replay与packet-credit。CRC不是身份认证，不抵抗恶意篡改。

### 25.2 发送状态

每VN保存next_sequence、oldest_unacknowledged、32-entry replay ring及指针、replay_cursor、peer returned-credit total、packets_started、control mailbox、timer/retry count/epoch。

新cell需replay槽、对应远端packet许可和调度服务。不可撤销提交前保存副本，PHY送出不能删除；收到合法窗口内ACK-next才回收。不能直接把任意ACK值当回收指针。

### 25.3 接收与去重

```text
collect -> CRC/format/epoch check -> compare seq with expected
  bad CRC: do not trust corrupted header; no commit
  equal:   commit once; expected++; ACK-next
  older:   duplicate, no delivery; repeat ACK
  newer:   missing earlier cell; NAK expected, no commit
```

CRC失败时class/seq也可能坏，不能使用坏header发一个假精确重放命令；可依赖发送超时或可信控制恢复。只有slot已预留且数据真正接管才推进expected，ACK不只是“看见波形”。

### 25.4 重放不重新创建事务

首次SOP消耗packet credit；重放沿用原seq，不再次扣逻辑packet许可、不重复副作用。接收slot真正释放才增加returned total。ACK丢失导致的重复cell应被去重。

16-bit序号用模65536比较，未确认窗口须远小于半空间，R1选32cell。epoch重建需双方协调。若接收端在执行副作用后丢失去重状态，链路不能保证跨重启exactly-once，应报告不确定并由上层恢复，不可随意重发MMIO。

## 26. RX packet slots 与 TX replay ring

每VN四个record slot，每槽至少280B，1120B/VN另加状态。状态为FREE->ASSEMBLING->COMPLETE->INJECTING->FREE；只有tail提交到远端NoC、不再读取原槽，才归还packet许可。每class一次重组一个record，其余槽存已完成/待注入包。

接收CRC与写入吞吐必须满足链路速率；packet credit不能解决CRC单元来不及处理一拍数据的问题，需弹性流控或降低速率。

Replay每VN32×80=2560B，两VN5120B另加状态。32GB/s、ACK闭环50ns时线上在途约1600B=20cells，32是余量示例，不是保证所有拥塞都够。

```text
local credit:      next local FIFO slot
remote packet credit: remote complete-record capacity
replay free slot: ability to retain an unacknowledged copy
```

累计归还避免控制重传重复加许可：`available=K+returned_total-new_packets_started`，K初始4。回绕有界模差、周期刷新和epoch隔离都要定义。

## 27. 调度、状态和错误恢复

```text
control mailbox ----+
replay data --------+-> scheduler -> formatter/PHY
new Request data ---+
new Response data --+
```

R1每八个可用发送时隙至少给控制一次机会，两VN控制轮询；累计状态可合并，无控制时让数据使用。ACK/credit发送不依赖普通data packet credit，避免信用耗尽连归还都无法发送。

重放也不能永久压倒响应；持续错误超过门限进入故障，不无限占线。

```text
RESET -> PHY_INIT -> NEGOTIATE -> CREDIT_INIT -> ACTIVE
                                                |
                         QUIESCE -> DRAIN -> LOW_POWER
                              \-> ERROR on unrecoverable condition
```

这是参考状态机，不是完整UCIe状态名复刻。quiesce禁新事务但允许旧响应/ACK/replay/drain。无法排空应报告可能部分完成，不能抹掉表项假装旧流量消失。

链路重放重送同一cell并去重；事务重试可能再次访问目标，幂等性、原子与MMIO副作用必须另行分析。

## 28. 真实 UCIe 的已核验范围

官方Hot Chips教程给出Protocol->FDI->D2D Adapter->RDI->PHY分层及相关复用、CRC/retry、状态管理职责。Raw模式不能一概套用Adapter格式化与可靠重放能力；版本和mode必须一起确认。[R10]

UCIe1.1官方说明补充streaming检错/重放机制，旧模式表不能当作所有后续版本限制。[R11]

教程指定的68B Format2示例：

```text
[2 B adapter header][64 B protocol information][2 B CRC]
```

适用该指定PCIe non-Flit/CXL.io场景，CRC覆盖header与协议信息。64/68只是这一层效率，不是SDMA用户payload效率；不同256B格式不能一律假设相同有效字节。它与LRP-64只是对照，绝不兼容。[R10]

未逐项取得/核验全部正式版本条文，因此不把假定CRC多项式、seq位宽、完整FDI/RDI时序、训练FSM或retry窗口写成标准事实。第四轮需要锁定版本和模式继续核验。

## 29. PHY 不仅是 serializer

```text
link data -> width adaptation -> lane striping / mapping
          -> TX circuits / timing -> package -> RX sampling
          -> alignment/deskew -> lane reconstruction -> link data
```

具体lane、训练、时钟、修复/降宽能力依封装与版本。官方电气/协议教程可定位这些职责，不应把其PHY指标当SDMA远端内存延迟。[R14][R10]

裸带宽 `L lanes × per-lane bit rate / 8`，还未扣编码/空闲/错误；与NoC宽度×时钟之间可能有gearbox与不同频域。D2D不自动等于长距离以太网SerDes。

训练/唤醒与稳态packet延迟分开报告。传播约L/v，serialization是有效位数通过带宽的时间，deskew是对齐等待；短走线不代表Adapter、CDC、校验总延迟都低。

## 30. 跨 die 重新做依赖分析

两个分别无死锁NoC连接后可形成跨边界等待环，模块化chiplet研究也专门讨论这一问题。[R16]

R1保守规则：单packet最多跨die一次，资源分PRE/POST，禁止POST返回PRE或再次D2D。

```text
PRE NoC -> TX gateway -> D2D -> RX gateway -> POST NoC -> endpoint
```

按2VN×2phase×2VC扩为8VC/input，独立buffer/ownership。源远程包PRE、远端重注入POST；phase可由可信注入/VC类别产生，不必改原head。各阶段内部仍XY，网关TX/RX和请求/响应资源分开，控制流有进展机会。

这是可用于构造无环依赖的参考约束，不是全系统证明；NI、目标与SDMA消费也须纳入。脚本未形式化验证整个R1。多次die跳转或多gateway需重做阶段规则。

# 第七部分：SDMA 系统闭环

## 31. 219 ns 的声明假设算例

全部数值是教学假设，不是量产芯片测量。SDMA读远die256B，两die各三个R0 hop，网关两侧整包接收，目标服务从完整请求到完整数据可用。

| 固定项 | ns |
|---|---:|
| 源NI | 2 |
| 源die首flit网络 | 15 |
| 两端gateway固定合计 | 4 |
| D2D固定含PHY/CDC/校验，不含serialization | 8 |
| 目标die首flit网络 | 15 |
| 目标NI | 2 |
| 单向固定合计 | 46 |

D2D raw32B/ns；target80ns；无排队、错误、唤醒。

请求24B record占一80B cell：`46+80/32=48.5ns`。

响应17flit在源NoC首项后多16ns收齐；record280B占五cell=400B；远端重新注入NoC尾部再16ns：`46+16+400/32+16=90.5ns`。

读RTT=`48.5+80+90.5=219ns`。没有重复加LT，也没有每hop重复加整包serialization。两段16ns来自明确的整包网关边界。

目标12GB/s，即12B/ns，需要2628B在途，`ceil(2628/256)=11`事务只是初始BDP估计。NI空间、ID、MC队列、gateway与replay可能先限流。

R0有效payload上限约15.06GB/s；LRP在此包长下理想`32×256/400=20.48GB/s`，未扣控制时隙。因此更可能先受NoC口限制，不能拿raw D2D32GB/s直接当SDMA可用带宽。

## 32. SDMA 与互联需要签清楚的契约

### 32.1 返回空间

```text
free slot -> read issued / response reserved
          -> partial response -> data ready to write
          -> write issued -> completion accounted -> reusable
```

哪些阶段共享存储、何时可覆盖须明确。Routercredit只保护下一跳FIFO，不替代SDMA读返回预留。

### 32.2 包大小与并发

大包降低header比例，也更久占packet VC/replay/目标空间。flit级仲裁允许其他VC穿插，packet lock则可能加大他人等待。应联动扫包长、outstanding、吞吐和尾延迟，而不是“大burst一定好”。

queue数、transactionID数、NI表项数和RouterVC数不同；VC不是VMID。context隔离要靠可信权限、quota与注入策略，不能只加标签。

### 32.3 完成与 fence

```text
C0 accept command
C1 leave SDMA/NI
C2 leave local NoC
C3 remote link accepts validated data
C4 target accepts operation
C5 target-defined ordering/visibility achieved
C6 completion reaches SDMA
C7 software observes record/interrupt
```

linkACK不等于C5，FIFO空不等于C6。fence等哪个集合在哪一点完成，必须由具体指令与系统模型定义。Router不自动实现GCR、cache flush、IOMMU/TLB invalidation；可运输相关消息，但语义在相应模块，不推测AMD专有packet完成点。

### 32.4 Preemption/reset 与流量方向

停止issue后旧响应仍在途，必须drain、保存可恢复状态或按架构abort，不能过早复用ID/context。晚到响应不得交给新context。

复制N字节的读写是否共享同一瓶颈方向取决于拓扑。按每个cut统计read request/data与write data/response，不能总把全双工相加或机械除二。

## 33. 软件与硬件协同

```text
clock/reset -> linkActive -> epoch/credit init -> route/protection
            -> NI/response resources ready -> SDMA enable
```

动态路由、端口禁用或quota缩小不得撤销已承诺资源；可quiesce/drain再改，在线无停顿需要版本化与更多证明。

Linux DMA API区分CPU与DMA地址、映射生命周期和同步；coherent映射也不替代必要的内存屏障。[R17] 发布descriptor、敲doorbell、读取completion须用目标平台规则，不因NoC保序或D2DCRC就省软件排序。

建议能力寄存器含ports/VC/depth/maxpacket/ID容量；配置包括address map、权限、rate/weight、quiesce/drain；错误记录source/VC/epoch/syndrome；性能记录byte/flit、stall与latencyhistogram。它们是参考组，不是实际厂商地址。

观察链：`offered -> admitted -> routed -> VA granted -> SA committed -> sent -> acknowledged -> completed`。仅transmittedbytes无法定位慢在谁。

# 第八部分：检查与验证边界

## 34. 不变量与定向场景

```text
0<=occupancy<=D; 0<=credit<=D
one grant per physical input/output
one owner per output VC
no pop without data; no send without reserved space
no body/tail starting an IDLE packet
old tail carries old metadata after input VC reuse
```

READY/VALID接口在停顿时保持payload；这条规则不能不加区分地套到纯credit驱动接口。

必须覆盖HEAD_TAIL、body间歇、tail在ST而新head到、同拍credit+send、全输入抢一输出、一个输入多VC抢不同输出、VN隔离、quiesce、CRC/ACK丢失/重复和epoch旧响应。

Liveness需要环境前进假设：目标最终处理、链路恢复或报告错误、eligible流最终服务、控制有机会。随机没卡住不等于死锁证明，安全性断言也不自动证明活性。

## 35. 第一轮检查与第二轮升级

第一轮 [reference_checks.py](examples/reference_checks.py) 包含九组局部检查：head位域、RR、随机SA、非最大匹配、credit守恒、ownership区分、XY依赖图、预算算式、CRC/序号/epoch。

```bash
python3 switch/examples/reference_checks.py
```

第一轮记录包括4×4 XY48节点68依赖边无环、三跳17flit到达15..31、219ns/11事务算例。这不是当时已实现完整网络模拟。

**第二轮新增真正有有限FIFO与延迟事件的 [router_round2.py](examples/router_round2.py)**，见第46—47章。第一轮历史结果和第二轮实测分开，不把版本升级写成旧脚本突然具备新能力。

本稿仍未完成真实RTL、STA、门级功耗、CDC、完整CHI/UCIe合规或全系统死锁证明。后续性能研究需扫traffic、packetlength、VC/depth、RTT、hotspot、负载与p99，而非只看单个无竞争算例。

# 第九部分：基线认识与来源

## 36. 必须避免的错误认识

NoC不等于D2D；Router不等于MUX；每requester不一定有独立FIFO；credit不等于VC idle；VA不等于SA；RR不等于最优匹配和硬实时；更多buffer/outstanding不必更快；各种协议flit不是统一格式；Raw模式不能套用所有Adapter能力；局部无死锁不能自动组合；离开SDMA、linkACK、可见、软件完成不同；模拟stage数不是物理时序证明。

第二轮把这些认识落实到寄存器、事件表和有限网络模型，而不是再堆一套名词。

## 37. 第一轮参考资料与边界

以下保留来源定位；第二轮新增R18—R21见第48章。读过特定章节不表示核验了全部标准。

**[R1] Li-Shiuan Peh, William J. Dally, A Delay Model and Speculative Architecture for Pipelined Routers, 2001。** 原始论文，流水、推测allocation、credit延迟。https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf

**[R2] Robert Mullins, Andrew West, Simon Moore, Low-Latency Virtual-Channel Routers for On-Chip Networks, ISCA2004。** Router结构、allocation、look-ahead、低延迟控制。https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf

**[R3] Nan Jiang et al., A Detailed and Flexible Cycle-Accurate Network-on-Chip Simulator, ISPASS2013。** BookSim2求值/更新、资源和流水模型。https://icn.kaist.ac.kr/~jjk12/papers/2013ISPASS.pdf

**[R4] gem5, Garnet2.0官方文档。** 模型边界和NI/Router/link/credit。https://www.gem5.org/documentation/general_docs/ruby/garnet-2/

**[R5] gem5源码，tag v24.1.0.1，SwitchAllocator.cc。** `arbitrate_inports/outports,send_allowed,vc_allocate`；第二轮读取的blob为`e31733d42e1d2a84f5afc86050a8209367983aa1`。https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc

**[R6] 同tag的InputUnit.cc、OutputUnit.cc。** head、inputpop、credit/free处理。https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/InputUnit.cc
https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/OutputUnit.cc

**[R7] FlooNoC原始论文，arXiv:2409.17606v1，2024。** 宽通路和NI/transport分工。https://arxiv.org/html/2409.17606v1

**[R8] Arm AMBA AXI and ACE Protocol Specification, IHI0022H，2020。** AXI4对照固定IssueH，A3/A5/A6/A8。https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf

**[R9] Arm AMBA CHI Protocol Bundle User Guide, DUI0954C，2016。** 第8节，页15—17通道接口；不是最新architecture规范，C++类型不作位宽依据。https://documentation-service.arm.com/static/5ed104c1ca06a95ce53f8869

**[R10] UCIe Consortium, Hot Chips2023 Tutorial—Protocol。** 分层、Raw/68B/256B、打印页37的Format2、初始化。https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf

**[R11] UCIe Consortium, UCIe1.1 Provides Streaming Protocol Solution for Error Detection and Replay, 2023-08-28。** 版本变化，不能替代完整规范。https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay

**[R12] Arm, Learn the architecture—Arm System Architectures,110303_0100_01_en，2025。** 第4.4节Fig4-2，CHI-C2C/CXS/transport分层。https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749

**[R13] William J.Dally, Charles L.Seitz, Deadlock-Free Message Routing in Multiprocessor Interconnection Networks。** Caltech1986技术报告与后续正式论文，确定性通道依赖基础，不作为任意自适应网络通用结论。https://authors.library.caltech.edu/records/fd0yr-br438

**[R14] UCIe Consortium, Hot Chips2023 Tutorial—Electrical, Form Factor and Compliance。** 封装/时钟/物理职责，不将PHY KPI当远端内存RTT。https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf

**[R15] PULP Platform，FlooNoC公开RTL，hw/floo_router.sv。** 第一轮读取blob`af7e41e51f04fa2e53b6cddebb20a24a56b1df9c`；main可变，论文版本与后续RTL分开。https://github.com/pulp-platform/FlooNoC/blob/main/hw/floo_router.sv

**[R16] A Simple Deadlock Avoidance Scheme for Modular System-on-Chip,arXiv:1910.04882v1，2019。** 引言与第2节的跨chiplet依赖；R1阶段方案不是该算法复刻。https://arxiv.org/pdf/1910.04882

**[R17] Linux Kernel Documentation, Dynamic DMA mapping Guide。** CPU/DMA地址、coherent barrier与streaming生命周期；驱动需使用目标内核版本规则。https://docs.kernel.org/core-api/dma-api-howto.html

---
# 第十部分：第二轮下钻——把 Router 的每个动作落实到资源和时钟边沿

> 第二轮专项研究，2026-09-24。以下内容继续使用第 3 章的 R0，不把经典论文、gem5 和本文模型拼成某一实际芯片的 RTL。本轮用 R0.2 指“把 R0 的状态更新约定进一步明确”，不是一个新的行业协议。第 1—37 章提供系统主线，本部分是其中 Router 章节的下钻正文；研究进度为第 2 轮完成，第 3—6 轮仍未完成。

## 38. 先冻结一个所有模块共同遵守的时序契约

### 38.1 一个方框图还缺什么

画出 `FIFO -> RC -> VA -> SA -> Crossbar` 之后，距离可实现设计还有一段关键工作：确定哪些量是寄存器旧值，哪些量是组合结果，哪些事件可以同拍发生，以及一个动作一旦执行，哪个模块必须保证它不会被取消。

本文把每拍分成三个逻辑步骤：**observe/evaluate，reserve/select，commit/update**。它们描述设计方法，不一定是三个物理流水级。真正的寄存器边界仍由第 15 章定义。

```text
                  state_q at edge t-1
                          |
       +------------------+--------------------+
       |                  |                    |
    RC evaluate       VA evaluate          SA evaluate
       |                  |                    |
       +------------------+--------------------+
                          |
                  selected operations
                          |
                atomic commit at edge t
                          |
                       state_d

Arrivals/credits captured at edge t are visible to the NEXT evaluation.
They do not retroactively change the selection committed at edge t.
```

这个规则直接影响 credit 和资源复用：edge 9 捕获的 free credit，不让 edge 9 已经完成的 VA“提前知道”VC 空闲；它可用于 [9,10] 的计算，edge 10 才提交新的 VA。若希望同边沿旁路，需要明确组合路径、优先级与时序，而不能只更改模拟器代码的执行顺序。

BookSim2 的分离求值/更新模型可用于理解这个问题；Garnet 的调度语义则要结合该模拟器的 tick 与事件模型阅读。本文 Python 模型不是任意一个模拟器的时序复制。[R3][R5]

### 38.2 定义唯一的 send_commit

R0.2 的 ST/LT 是固定延迟、不可回堵的已预留通路。`send_commit` 的前提为：队头有效、VA 已完成、下游 credit 可用、输入与输出都获得匹配、链路处于允许提交的状态。

```text
send_commit = valid_head_of_queue
           && active_packet_state
           && valid_output_vc_mapping
           && credit_q > 0
           && final_input_output_match
           && guaranteed_ST_LT_capacity
```

同一个 commit 原子执行以下动作：读取并移走旧队头；扣减一份下游接收许可；锁存 data、H/T、output、output-VC；更新真正获胜的 RR 指针；向上游生成一个槽返回事件；若为 tail，再结束本地输入 packet 状态。

其中 data 已经离开 FIFO，不代表它已到下一个 Router；因此必须计入前向在途 F。若后续把 output FIFO 改成可能停住的弹性队列，`guaranteed_ST_LT_capacity` 就不再是常量，commit 条件和 F 的定义都必须修改。

### 38.3 事件冲突表：RTL 评审应逐行过一遍

| 同一时钟边沿的事件 | R0.2 约定 | 不允许的实现 |
|---|---|---|
| 普通 pop + 新 body 到达 | 旧队头被读出，新 body 写入，count 加一减一 | 把 count 的两次非阻塞赋值互相覆盖 |
| credit return + send_commit | C 做净变化；记录两个独立事件 | 只执行最后一条 `C<=...` |
| input tail pop + 新 head 想注入同一 VC | 本轮不支持同边沿复用，新 head 下一拍再考虑 | 根据刚清除的 IDLE 提前接受新 head |
| free credit + 新 VA 申请同一 output VC | 本轮下一次 VA 提交才能使用 | 两个不同申请者分别看到不同阶段的“空闲” |
| tail 进入 ST + local VC 后续被复用 | ST 保存旧包的 route/VC/H/T | ST 再回读已被新包覆盖的 route 寄存器 |
| reset + outstanding traffic | quiesce/drain 或一致 abort，不按正常传输处理 | 只把一侧 C 清成 D |

同步 RTL 常用 `state_q/state_d` 或单一集中 next-state 逻辑表达这些合并更新。将 `credit <= credit - 1` 和 `credit <= credit + 1` 散落在两个 `if` 中，不是一个正确的并发计数器设计。

### 38.4 Packet identity、VC index、generation 为什么要分开

VC index 是可复用槽位的编号；packet identity 是业务/验证对象；generation 表示同一个 VC 被分配给第几批状态。输入 VC 可能已经服务新包，某个旧 output VC 却仍在等前一个包的 free 返回。

```text
Input L.VC0:
  packet A --tail popped--> IDLE --> packet B
                    |
                    +-- A's tail still in ST/LT or downstream

Output E.VC1:
  owns A -------------------------> waits for A's free credit
```

正确实现让旧 free 只作用于它对应的 output VC 所有权，不能顺着一个已经过时的 `(input,VC)` 指针把 B 的输入状态清掉。硬件不一定需要在线携带无限位宽的 generation；可以通过资源生命周期保证无歧义。但验证模型使用 packet/generation 标签，有助于抓住旧状态误用。

本轮脚本中的 packet ID 和 generation 有一部分是**旁观检查信息**，不等于修改了第 4 章线上 flit 格式。若产品确实在接口增加有限位宽 tag，还要定义回绕与 reset 规则。

## 39. VA 再拆一层：从申请矩阵到寄存器写使能

### 39.1 具体要造几个逻辑单元

R0 有 5×4=20 个 input-VC 申请者和 5×4=20 个 output-VC 资源。不是每个申请者都能申请全部 20 项：RC 已固定输出方向，VN 又限定两个 output VCs，因而申请图很稀疏。

```text
Input VC descriptor
 {state, route_out, VN, packet identity}
                   |
                   v
      allowed-mask & idle-mask
                   |
         candidate selection
                   |
          request[o][outvc][inputvc]
                   |
          one RR per output VC
                   |
   grant -> input mapping WE + output ownership WE
```

若使用二十输入 RR，每个 output-VC arbiter 的轮转指针需要表示 0—19，逻辑位宽至少五位。输入 route 五选一编码至少三位；四 VC 编码两位。把端口数、VC 数做成参数时，应使用安全的向上取整位宽，而不把 `P=1` 时的零位向量留给综合器碰运气。

### 39.2 为什么“申请所有空 VC”需要更多协调

假设 A、B 两个输入 VC 都申请下游 VC0 与 VC1，两个 output-VC arbiter 可能都选 A。若没有 input-side accept 阶段，A 会拿到两个资源，B 一个也没有。

R0 的“每申请者只提名一个候选”就是一种简单规避。另一方案允许全申请，再做 grant/accept 匹配，但要有拒绝后的资源撤销和公平性规则。两者都可以实现，不能把两种方案的局部逻辑混接。

### 39.3 多拍 VA 必须防止重复预订

若 VA 的仲裁路径要两拍，第一拍读到 output VC 空闲后，第二拍提交之前可能有另一个申请也读到它空闲。解决方法包括：第一拍建立 reservation；在最终提交重新验证并允许失败；或者串行化分配。

```text
FREE -> PROVISIONALLY_RESERVED -> OWNED
              |                    |
              +-- cancel -> FREE   +-- downstream release -> FREE
```

临时预留也需要 owner、有效位、撤销条件和复位行为。没有这些状态，只是在论文图上给 VA 多加一个寄存器，并不能保证行为仍然正确。本轮可执行模型仍使用一阶段 VA，未冒称已经实现多拍 reservation。

### 39.4 Ownership 与空间分配的分工

VA 只授予 packet 使用某个 VC 的资格，逐 flit 的空间仍由 credit 约束。对于当前严格 tail-credit 释放的 R0，空闲 output VC 在正常状态下也应有 D 个 credit；模型对此作断言。

如果扩展成 shared buffer 或允许多个包排在同一个 VC，空闲/可分配的定义要变化，不能照搬“IDLE 必有 D 个槽”这一私有-buffer 基线断言。BookSim 的策略代码显示，容量管理与占用/所有权是不同层面。[R19]

## 40. SA 再拆一层：匹配质量、公平性与时序不能只选一个

### 40.1 从三维 VC 请求压成二维端口匹配

同一物理输入的四个 VC 可请求不同输出，但只有一条输入数据总线。R0 先在每输入选一个 VC，再在每输出选一个输入，最后形成合法的部分一对一匹配。

```text
VC requests:  input i, VC v -> output o
                       |
            input-side VC selection
                       |
Port matrix M[i][o] ---+
                       |
            output-side arbitration
                       |
             crossbar selection
```

Garnet `v24.1.0.1` 的 `arbitrate_inports`、`arbitrate_outports` 提供了具体对照：两级选择、获胜后读出 flit、更新输出元数据、扣 credit、tail/free 处理和 RR 更新。它在 SA 成功路径上给 head 分配输出 VC，没有独立的 VA 阶段，不能把它的每拍行为照搬为 R0。[R5]

### 40.2 maximal 和 maximum 不同

maximum matching 是当前申请图中边数最多的合法匹配；maximal matching 是再也无法直接增加一条不冲突的边，但重新安排已有边可能得到更多并行传输。

```text
I0 -> O0, O1
I1 -> O0

Matching A: I0->O0
  已经 maximal：剩余 I1 只能去已占用 O0
  但不是 maximum。

Matching B: I0->O1, I1->O0
  两条边，才是本例 maximum。
```

所以“多迭代直到没有新边”并不自动等于 maximum。最大匹配也不是队列稳定、公平或低延迟的充分条件：它不一定照顾长期等待的队列。

### 40.3 iSLIP 的有用之处和适用边界

iSLIP 的一次迭代包含未匹配输入发 request、输出 grant、输入 accept；未匹配端口可继续迭代。原算法只对**第一轮迭代中被接受的匹配**更新相关轮转指针，后续迭代补充匹配而不照样更新指针。[R18]

```text
unmatched requests -> per-output grant -> per-input accept
       ^                                      |
       +--------- repeat for unmatched -------+

Persistent pointer updates: accepted matches of iteration 0 only.
```

这不是说 R0 的简单 SA 也必须套用相同规则。R0 的“一级提名+二级赢家”和 iSLIP 的“request/grant/accept”是不同算法；前者的指针跟真正 commit 走，后者还含迭代层次。原论文研究固定 cell 的输入排队交换机，不能把其特定负载吞吐结论直接当成带 VC、credit、路由依赖的 NoC 保证。

### 40.4 把匹配接到可暂停通路时，要增加哪一步

纯匹配函数返回 `(i,o)` 不代表数据已被消费者接受。若 output register 不可写、head 没拿到 VC，或链路临时停止，必须过滤为实际 commit，并按所选算法决定是否保留授权。

有两种可实现契约：第一种在 request 生成前把所有资源许可筛干净，保证赢家一定能提交；第二种保存 grant 与 payload，等待消费者接收，期间不让另一个包抢占这份授权。不能一边重做仲裁、一边让停住的 payload 变化。

### 40.5 RR 能保证什么，不能保证什么

孤立输出、请求集合稳定、每拍都可服务时，RR 可给出有限轮转等待；整个网络中，VC 是否有 credit、是否被输入一级提名、目标是否服务，都可能变化。

尤其不能把“每级 RR 不饥饿”随手相乘，得出一个无条件的端到端 deadline。多个竞争者间歇 eligible、不同输出交替堵塞时，输入侧候选也会变化。本文不为一般动态流量声称固定 P×V 拍上界。

工程上至少要同时测：等待时间分布、最长连续 eligible 未服务时间、每类成功 flit/byte 数、仲裁空洞，以及与目标不 ready 分开的服务缺失。

### 40.6 逻辑复杂度的真正代价

增加迭代次数可能提高当前拍匹配数量，但增加组合深度。若流水化仲裁，就需要在计算期间锁定或版本化候选队头；否则第二拍依据第一拍旧队头的结果去 pop 新队头。

若使用内部 speedup，使一个输入/输出每外部周期可处理多项，FIFO 读写口、crossbar、credit 返回吞吐也都要同步扩展。不应只给 allocator 增加一个参数，便宣称系统吞吐翻倍。

## 41. FIFO 落到存储电路：队头何时真的可读

### 41.1 寄存器 FIFO 与 SRAM FIFO 的数据可用性不同

基线的浅 FIFO 可以让队头经组合路径可见。同步 SRAM 则通常先提交读地址，随后得到数据。若 SA 在某拍才选定 VC，本拍末就要求 ST 锁存该 VC 数据，可能根本来不及。

```text
Register FIFO:
  head pointers -> combinational data -> SA-selected MUX -> ST

Synchronous SRAM:
  read request -> memory latency -> response/landing register
                                      |
                                      v
                             data-ready arbitration -> ST
```

于是设计需要预读、队头缓存或把读存储加入流水线。header metadata 可与 payload 分开保存，使 RC/VA 不用为了几个目的字段读整条宽数据。

### 41.2 一个可继续实现的 per-input SRAM 方案

【扩展设计，不是本轮模型已实现】每物理输入一块 1R1W 数据存储，允许一拍写一个到达 flit、读一个候选 flit；每 VC 保存队头描述符、状态和至少一个预读有效位。被选中读出的数据进入 landing register，再参与或完成真正的传输提交。

关键控制量至少包括：`read_pending、read_vc、read_address、read_generation、landing_valid、landing_vc、landing_generation`。返回的数据必须匹配发出读请求时的对象，而不是匹配此刻可能已复用的 VC 状态。

只配一个全输入共享 landing slot 时，一个被 credit 堵住的 VC 可能占住它，让其他 VC 即使有数据也不能预读。增加 per-VC head cache 或多个 landing slots 可以缓解，但会增加面积与调度逻辑。

### 41.3 预取队头不一定释放网络 credit

有两种完全不同的设计：

**复制式预取**：SRAM 中的数据仍然保留，landing/head cache 只是副本。真正 send_commit 才释放原槽并返回 credit。原来 D 的计量无需改变，但应防止过期副本被重复发送。

**搬移式预取**：数据从 SRAM 槽搬进另一个独占存储，原槽可复用。若此时提前返 credit，landing register 就已经进入接收容量承诺范围，新的总容量与在途定义必须把它算进去。

```text
Copy prefetch:  memory [X] -> cached copy [X] ; one logical flit
Move prefetch:  memory [ ]    landing [X]     ; capacity moved, not destroyed
```

不把副本和新增容量分清，可能把一份数据算成两份空间，也可能在 landing 满时仍然对上游发许可。

### 41.4 端口与 bank 冲突不能藏起来

如果把五个输入 FIFO 合到一块全 Router SRAM，最坏每拍可能有五写、五读需求。一块 1R1W SRAM 不能实现这种吞吐。选择 banking 后，还必须讨论同 bank 多请求、元数据写冲突和流量分布。

例如按 `slot_address % bank_count` 分 bank，两个被 SA 选中的队头仍可能落到同 bank。此时要在请求筛选中加入 bank 许可，或保留数据直到冲突解开。否则 allocator 发出的“两个 grant”在数据面只兑现一个。

### 41.5 能耗的检查点

buffer 深度、flit 宽度和 VC 数一起增加时，访问能耗、头部广播、宽 MUX 切换和时钟负载都可能上升。可采用独立写使能、无效数据隔离、按 VC clock-enable 和队头字段分离，但要用实际综合/功耗分析评价；本文不凭逻辑图给出 pJ 或面积百分比。

## 42. Shared buffer：不再只说“用一块公共 SRAM”

### 42.1 一个具体的 per-input linked-pool 微架构

本节选择**每物理输入共享**，不是全 Router 共享，因此每拍最多一入一出，资源模型较容易闭合。假设有 B 个 flit slots 和 V 个逻辑队列：

```text
                       per-queue registers
                   head[V], tail[V], count[V]
                           |          |
Arrival -> allocate ------+          +------ dequeue -> read data
             |                                  |
         free bitmap / free list                |
             |                                  |
             v                                  v
       data[B] + next[B] <---------------- slot release
```

`data[a]` 保存 flit，`next[a]` 保存同队列下一槽地址；每队列 head/tail 指向链表两端；空闲池跟踪未占用地址。历史 DAMQ 论文提供了动态多队列、独立指针与共享存储的具体实现思路，但本节是按 R0 需求重新设计的 flit 级方案，不是复制其旧器件参数。[R20]

### 42.2 入队与出队

入队先从旧 free 集合预留地址 a，写 data[a] 与 next[a]=NULL。队列为空则 head=tail=a；非空则 old_tail.next=a，再将 tail=a。出队先读 old_head 数据，head=next[old_head]；若原来只有一项，head/tail 都变空，旧槽再归还 free 池。

free list 与 payload 可以分开实现，避免为更新一个指针读写整条数据。若元数据本身用 SRAM，也要明确同拍写 old_tail.next 与清 old_head.next 是否需要两个写口，或是否采用合并更新/独立寄存器。

### 42.3 同队列一进一出：四种边界

| 旧队列长度 | pop | push | 正确的新状态 |
|---:|---:|---:|---|
| 0 | 0 | 1 | head=tail=new slot，count=1 |
| 1 | 1 | 0 | head=tail=NULL，count=0 |
| 1 | 1 | 1 | 弹出旧数据，head=tail=new slot，count=1 |
| ≥2 | 1 | 1 | head 指向旧第二项，旧 tail 连新项，count 不变 |

当 old_count=1、同时 pop/push 时，若两段 RTL 分别独立更新 head/tail，可能把刚挂入的新节点清掉。本轮检查脚本显式实现了这个边界，并用普通 deque 作参考比较。

R0.2 教学 linked-pool 不使用“本拍刚释放的地址立即再分配”的组合回收；只有旧 free 集合有地址才接受 append。可以增加同拍回收优化，但要先定义 read-during-write 和元数据冲突语义。

### 42.4 物理空闲不等于逻辑未承诺

这是本轮最重要的细化之一。一个 8-slot shared pool 即使物理上一个 flit 都没有，只要已经向 VC0 发了八份许可，就不能再向 VC1 发一份许可；VC0 的八个 flit 可能都还在远端或前向流水线里。

对共享容量 B 定义：U 是尚未授出的池许可，C_v 是上游可用许可，F_v 是前向在途，Q_v 是占用，R_v 是正在返回的许可：

```text
B = U + sum_v(C_v + F_v + Q_v + R_v)

physical_empty_slots = B - sum_v(Q_v)
unpromised_capacity  = U
```

两者不相等。降低某 VC 的软件 quota 不能凭空撤回已经发出的 C_v 或 F_v。若需要回收闲置许可，应有受控撤回/静默重配置握手，并证明不会与最后一份在途发送交叉。

### 42.5 最小保留容量与动态池

让请求与响应共用存储可以节省闲置容量，但也可能使请求占满所有槽，响应无法进入，进而反过来阻止请求释放。逻辑上画了两条 VN，并不表示其底层容量已经隔离。

一种参考策略是给每个进展关键类别保留不可被借走的最低容量，超出部分才借动态池；申请和 credit 发放必须维护这些保留约束。保留多少不是固定“一个槽就足够”的答案，要看协议消息依赖、整包/虫洞方式和接收端承诺。

本轮 `SharedPool` 测试只证明所选许可记账的局部守恒，不证明一般 shared-buffer 协议无死锁。

## 43. Credit 往返、VC 周转与短包吞吐

### 43.1 同一条路径有两个不同的回路

```text
Space loop:
  send reservation -> arrival -> buffer pop -> slot credit return

Packet-ownership loop:
  VA reservation -> ... HEAD/BODY/TAIL ... -> downstream TAIL pop
                  -> free indication return -> next packet VA
```

第一个决定同一 packet 的 flit 能否连续流动；第二个决定新的 packet 何时可以复用 VC。深度 D 增加主要改善槽闭环，不自动缩短 packet 所有权周转。

经典 Router 延迟论文明确把 credit 的传输、处理与流水影响纳入模型。本文的具体 edge 数值仍由 R0.2 自己定义，不把论文的示意周期当作所有芯片参数。[R1]

### 43.2 用真实队列事件复算，而不是输入同一个公式

新增 Python 模型真的安排：head 到达、RC、VA、SA、两拍前向 ST/LT、接收 FIFO pop 和可配置反向返回。每拍检查 C+F+Q+R=D，最终还要等 owner 释放与 credit 全部归还，才报告 drained。

对同一个 17-flit 包、三个 Router 服务跳、1 flit/cycle 源注入，本次实际结果：

| 每 VC 深度 D | 反向返回延迟 | 首 flit 到达 edge | 尾 flit 到达 edge | drain 后下一模型 edge |
|---:|---:|---:|---:|---:|
| 1 | 1 | 15 | 95 | 98 |
| 8 | 1 | 15 | 31 | 34 |
| 8 | 12 | 15 | 47 | 61 |

三个实验的 head 固定路径相同，但后续 flit 因 credit 可复用时间不同而出现不同气泡。因此，单看首 flit latency 会漏掉很严重的完整包与吞吐问题。

`drain 后下一模型 edge` 是 Python 循环完成最后一次状态更新后的计数值，不是另一种物理传播延迟。sink 消费数据和网络最后一份 free 返回，也晚于 tail 到达。

### 43.3 D 不足时不要用错误补救

不能为了让模型“达到理论带宽”在 C=0 时放行一拍，或者初始化多于真实接收槽的 credit。合法改进是增加容量、缩短闭环、采用经过证明的同拍 credit bypass、增加可用 VC 或改变通路与缓冲组织。

D2D 的长返回路径往往需要在网关终止短范围流控，采用另一层资源协议。但这属于后续 D2D 深化，不应通过偷偷扩大 R0 的 credit 定义来掩盖。

### 43.4 提前释放 output VC 到底改变了什么

如果在本端 tail 发出就让另一个 packet 使用同一 downstream VC，线上顺序仍可保证旧 tail 在新 head 前。但接收端可能在处理旧 packet 时已经收到新 packet，因而不能再采用“一个 VC 永远只保存一个 packet 的 route/state”的最简结构。

可能需要包头队列/描述符 FIFO、分段状态、每包顺序和多次完成跟踪，并重新定义 free/credit 的意义。BookSim 的 `wait_for_tail_credit` 分支是对照入口；它存在不同模式不代表 R0 可以只关掉一个 busy bit 而其余逻辑不变。[R19]

## 44. Speculation、look-ahead、bypass：把失败路径补全

### 44.1 VA 与 SA 并行时的结果表

【参考扩展】假定 VA 和 SA 为 head 并行计算，非推测的 body/tail 保留应有优先权。下表中的“VA 成功但 SA 失败”采用保留 VC 的策略，其他设计可以取消，但必须保持一致。

| VA | SA | 本拍行为 |
|---|---|---|
| 成功 | 成功 | 所有许可有效后 commit，pop、扣 credit、锁存数据 |
| 成功 | 失败 | 保存 output-VC ownership，head 留 FIFO，下一拍申请 SA |
| 失败 | 成功 | speculative grant 作废，不 pop、不扣 credit、不按已传输更新 RR |
| 失败 | 失败 | head 与队列不前进；等待/重试状态按约定更新 |

“SA 成功”只有在其使用的 VC/路径与最终 VA 一致、数据可用且输出可接收时才能转成 commit。否则误发的 head 可能进入别人拥有的 VC。早期推测 Router 论文用于说明这种并行化思想；此处失败表是本文选定的具体契约。[R1]

### 44.2 Speculative traffic 不能挤掉可兑现的传输

一个 body 已有 VC 和 credit，本可以本拍发送；另一个 head 猜测 VA 会成功，却抢走 output。若后者 VA 失败，本拍输出空转，而且损失的是已可兑现的服务。

因此常见的设计目标是：非推测请求优先，或在授权结构中隔离推测请求，并在失败时有明确回退。是否能在同拍补选 body，取决于关键路径，不能不计代价地假定“失败后再仲裁一次”。

### 44.3 Look-ahead 搬走的是 RC 延迟，不是路由责任

在上游计算下一节点的方向，可以让 head 少等本地 RC。需要随 flit 携带或保存下一跳信息，并处理拓扑边界、错误目的地、路由表世代以及是否允许本地重新检查。

若采用自适应策略，上游看到的远端拥塞可能过时。Look-ahead 元数据不应绕过当前节点的安全资源检查，也不能把一个非法转向当作“上游已经算过，所以必然正确”。

### 44.4 Bypass 必须有失败落点

```text
new incoming flit
        |
        +-- bypass conditions all true ---> reserved output stage
        |
        +-- any condition fails ----------> normal input FIFO
```

条件至少包括没有必须先走的旧 flit、packet/VC 状态匹配、下游容量许可、输出匹配以及 fallback FIFO 能接住失败路径。在同一拍只能有一个接受归宿，不能既 enqueue 又作为新数据发送两次。

body bypass 还必须继承其 head 已建立的路径；不能因另一个输出空闲就随意改变方向。若 bypass 与正常队头同时抢资源，必须规定年龄/优先级和双重 pop 防护。

### 44.5 Elastic buffering 是另一种体系，不是给 credit 代码加 READY

ElastiStore 提供按 VC 维护弹性状态、共享辅助存储和仲裁的具体研究实例；其容量节省伴随特定阻塞场景下的服务取舍，不能当作无代价优化。[R21]

一般设计推导是：反压经过寄存器返回，需要吸收在停顿被上游看见之前仍然合法发来的数据。若最大继续传输量为 K，就需要对应的弹性容量或更早停止阈值；两槽结构只适用于相应的一拍反馈与一拍传输假设，不是所有链路的固定答案。

```text
consumer stops now
    -> registered stop propagates later
    -> previously authorized flit can still arrive
    -> skid/elastic capacity absorbs it
```

本轮网络模型采用 credit+固定 ST/LT，不同时冒称实现 ElastiStore、异步 FIFO 或完整 ready/valid elastic router。不同体系在文档中作为明确的设计分支讨论。

## 45. Deadlock 与 QoS：把隐藏的共享资源画出来

### 45.1 单纯 XY 图漏掉什么

一个只含有向链路的 XY 依赖图，不含 SRAM bank、共享池许可、NI 返回数据空间、重排缓冲、target queue 或软件消费。这些资源也可能被占有并参与等待。

例如：请求占满 shared pool，target 等待有响应空间才接收请求，响应又因 shared pool 无剩余而无法进入。物理路由没有环，也仍然可能存在协议资源环。

```text
request-held shared capacity
        -> target waits for response acceptance
        -> response waits for shared capacity
        -> request cannot retire
```

修正方法不是机械增加 VC 数，而是切断依赖：保留响应容量、在 NI 注入前预留接收资源、使目标不因发新请求才能消耗响应、或为各阶段提供受保护资源类别。

### 45.2 Escape VC 不是万能标签

若设计支持 adaptive route 并希望用 escape network 保证前进，至少要定义逃逸网络的合法路由、进入/退出规则、buffer 获取方式和公平服务。若 escape buffer 仍被普通流量借光，或 packet 进入逃逸类后又返回更早资源，名字叫 escape 并不能提供证明。

本轮 R0 继续使用确定性 XY，没有通过增加一个 VC 名称就宣称实现一般自适应死锁避免。

### 45.3 QoS 仲裁粒度影响 SDMA

按 packet 轮转，一次 17-flit SDMA 数据包与一次 1-flit 控制包得到的字节服务不等。按 flit 轮转改善交错，但 packet 占用 VC 的时长可能更长。按 byte/deficit 调度则要保存配额、补充量以及不能发送时是否累积额度等状态。

延迟敏感控制流的要求通常不是“有一个高优先级 bit”，而是它在请求 buffer、VA、SA、链路和目标端都不能被无限阻塞。某一级严格优先权也可能让 bulk SDMA 饿死，因此需要区分最低服务保证、上限限流和突发容忍。

### 45.4 排队计数器不能无条件求和

一个 VC 同时没有 credit、也没有 SA grant 时，两种观察都可能为真；把两个 stall counter 相加当成真实等待拍数，会重复记账。

建议同时提供两类统计：互斥的主阻塞原因用于分解延迟；允许重叠的事件计数用于诊断相关性。指标名称、触发点和单位需要写在寄存器说明中。不能把本轮脚本的 `vc_credit_stall_observations` 误读为整个 Router 的独占停顿周期：它按 VC 观察，多 VC 可在同一拍各加一次。

## 46. 一个真正运行起来的有限缓冲模型

### 46.1 模型实现了什么

本轮新增 [router_round2.py](examples/router_round2.py)，仅依赖 Python 标准库。它实现 2D mesh、每输入四个私有 VC FIFO、独立 RC/VA、两级 SA、固定两拍 ST/LT、带延迟的反向 credit、tail-free 所有权释放以及有限 sink queue。

源 NI 一次在一个 node 注入最多一个 flit，使用明确标注的理想 ready/valid 接口；中间 Router 与 sink 接口采用信用流控。packet 带有用于检查的不可变身份，输出事件保存快照，因此可以检查 local VC 被复用后旧 tail 是否仍正确到达。

```text
Packet source -> Local FIFO -> RC/VA/SA -> scheduled forward event
                                            |
                                            v
                                     next finite FIFO
                                            |
                                       later pop
                                            |
                               scheduled reverse credit event
```

没有调用 gem5/BookSim，也没有把其中源码复制后改名。公开实现用于对照设计选择；本轮代码是自行编写的教学模型。

### 46.2 为什么它比第一轮检查更进一步

第一轮的到达时间检查主要是按照给定递推计算。第二轮中到达 edge 是排队、仲裁、有限 credit 和事件执行的结果；低 D、长返回路径或 sink 暂停会自然改变结果，不需要人为把一个延迟项加到公式里。

每拍还逐 link/VC 检查容量守恒与 owner 映射，最终验证 packet 内顺序、不丢失、不重复、正确目的地，以及所有 owner/credit 能否排空恢复。错误增发一份 credit 的故障注入会触发断言。

### 46.3 模型没有实现什么

没有真实 RTL 电路、同步 SRAM 读延迟、bank 仲裁、VA 多拍 reservation、推测/bypass 网络、CDC 亚稳态、ECC 纠错、UCIe/CHI 合规、一致性协议、SDMA 指令状态机或完整多 die 系统。iSLIP、shared-pool 许可与 linked-list 存储是**独立局部检查**，尚未替换进基线 mesh。

运行随机种子并排空，只说明这些有限测试轨迹通过，不证明所有状态都无死锁。为了不把研究阶段混淆，本轮的局部 depth/credit 对照也不计作第五轮的完整性能研究。

## 47. 本次云端实际检查结果与复现方式

```bash
python3 switch/examples/router_round2.py --report /tmp/round2_results.json
```

本次 **14 个测试组全部通过**。测试覆盖：RR、3×3 全部 512 个申请图在三种统一指针初值下的匹配约束与 maximal 检查、iSLIP 第一迭代指针规则、两级 SA 非最优例子、无负载流水、源端间歇发包、credit 参数变化、sink 暂停恢复、随机 mesh 流量、共享容量承诺、链表同拍入出队、错误 credit 检出、tail/新包状态复用和非法调用的原子性。

| 随机网络检查汇总 | 实际值 |
|---|---:|
| 配置/种子运行数 | 16：12 个 2×2，4 个 3×3 |
| 逻辑 packet 数 | 1,728 |
| 端点成功交付 flit 数 | 11,249 |
| 实际 SA commit 次数 | 25,343 |
| 逐拍不变量检查 edge 数 | 8,665 |
| tail-free 返回事件 | 3,900 |
| credit 不足的 VC 观察次数 | 30,279 |

上表仅汇总指定的 16 次随机网络实验，不把单元测试与生成报告时的重复运行再次累加。packet 长度选自 1、2、5、17 flits，D 选自 2、4、8，反向延迟选自 1、2、4；sink 前 25 拍阻塞，之后按固定种子、每拍 0.61 的可服务概率取样。它是压力测试，不是代表实际 SDMA workload 的测量。

linked-pool 另外进行了 10,000 拍随机入队/出队与 deque 对照。`test_14` 是编写过程审查后新增的改进：非法 pop+push 调用必须在改变 free list 之前被拒绝，避免“抛出错误但状态已经部分改变”。这属于参考代码接口健壮性修正，不应夸大为发现实际芯片漏洞。

本次脚本 SHA-256：`67676b1cf4841f45bdc7d9574342dc92d997ce434c62c88ac119ed666a18fbd5`。完整机器可读结果见 [round2_results.json](examples/round2_results.json)。执行耗时取决于机器，不作为 Router 性能指标。

## 48. 第二轮证据清单：具体读到哪里，具体改变什么

| 来源 | 本轮实际定位 | 带来的细化 | 边界 |
|---|---|---|---|
| Peh/Dally Router 延迟论文 [R1] | VC/推测流水、credit turnaround 图与相关正文 | 拆分空间闭环、所有权闭环和失败路径 | 不套用其工艺/性能数字 |
| Mullins 等低延迟 Router [R2] | 基线结构图、低延迟控制路径讨论 | 强调流水压缩需要实现机制 | 未重做物理设计 |
| iSLIP 原论文 [R18] | 第 III、VI、IX 节，指针与迭代规则 | 独立 matching 函数和第一迭代更新测试 | 不把固定 cell 保证当 NoC 保证 |
| BookSim 固定提交 [R19] | `buffer_state.cpp` 私有/共享策略、SendingFlit、ProcessCredit、TakeBuffer | 容量与所有权分开，提前释放不能只改 busy bit | 模拟器策略不是本文 RTL |
| Garnet 固定 tag [R5] | `arbitrate_inports/outports` 与 commit 路径 | 源码动作逐项对照，说明合并 VA/SA 的差别 | 本文仍独立 VA |
| Tamir/Frazier DAMQ [R20] | 第 III 节、buffer organisation 与 timing 表 | 明确数据/指针/free-pool 的结构 | 本文改成 flit 级原创示例 |
| ElastiStore [R21] | 第 II—IV 节、Fig.1—5 | 解释弹性容量、延迟反压与共享辅助槽 | 未合入 mesh 模型 |

**新增参考：**

**[R18] Nick McKeown, The iSLIP Scheduling Algorithm for Input-Queued Switches, IEEE/ACM Transactions on Networking, 7(2), 1999。** 原论文，特别是第一迭代更新规则与硬件 arbiter 结构。https://www.cs.cmu.edu/~dga/15-744/S07/papers/islip-ton.pdf

**[R19] BookSim2，固定提交 `28f43299f1706a3160ffac721ca461d74eb6e618`。** 本轮读 `src/buffer_state.cpp`，blob `228d91d0ab1a221cf6ced0461e650959eecce0f8`；不把未来 master 更新混入当前描述。https://github.com/booksim/booksim2/blob/28f43299f1706a3160ffac721ca461d74eb6e618/src/buffer_state.cpp

**[R20] Yuval Tamir, Gregory L. Frazier, High-Performance Multi-Queue Buffers for VLSI Communication Switches, ISCA 1988。** 本轮读取原论文的动态队列、指针和数据组织；不要与后续年份的相近题名论文混淆。https://web.cs.ucla.edu/~tamir/papers/isca88.pdf

**[R21] I. Seitanidis, A. Psarras, G. Dimitrakopoulos, C. Nicopoulos, ElastiStore: An Elastic Buffer Architecture for Network-on-Chip Routers, DATE 2014。** 作者公开版本，重点为第 II—IV 节的弹性 VC 与共享辅助存储。https://gdimitrak.github.io/papers/date14a.pdf

资料索引中的“读过”指上述定位，不声称已完整核验所有列举规范或所有源码文件。没取得全文的论文不作为已完成专项研究的证据。

## 49. 第二轮的结论与后续边界

> 规划接续更新（2026-09-24）：后续任务以 [SWITCH 修订方案](../SWITCH/research-plan.md) 为准；第 3 轮先明确 NI 事务契约，AXI/CHI 与 UCIe 作为有条件的参考。第 6 轮须等相关模块形成必要的详细研究结论。下文保留第二轮当时的结论，本次规划修订不计为完成新研究轮次。


第二轮将“一个可讲通的 Router 方框图”推进到**明确更新事件、资源守恒、仲裁接入条件、存储实现分支和可执行有限网络检查的参考设计**。几个重要结论是：一个 grant 不一定等于传输；一个空槽不一定可重新承诺；一个满 credit 的 VC 不一定空闲；一个 maximal 匹配不一定最大；几个局部无死锁部件不一定能安全组合。

本轮完成的是 Router 微架构专项深化。第三轮仍需把选定 AXI/CHI 子集逐项映射到 NI 与 transport；第四轮仍需锁定 UCIe 版本/模式核验真实 D2D 接口；第五轮仍需完整流量、吞吐与尾延迟研究；第六轮仍需在这些结论稳定后做 SDMA 系统交叉复审。

本轮没有后台持续运行任务。报告和脚本是本次云端会话执行后保存的结果；以后继续研究时，应读取本章、对应代码及当时的 GitHub 提交，不把文档版本号或 R0/R1 编号误认为迭代轮次。
