# 从可实现微架构理解 Switch：NoC Router、Die-to-Die 与 SDMA

> 版本：2.0；研究与重构日期：2026-09-24。
>
> 阅读目标：不只是认识 routing、VC、credit 等名词，而是能够在白板上画出一个可以继续细化成 RTL 的 Router，说明每个缓冲区、状态寄存器、仲裁器和接口在什么时刻更新；再把这个 Router 接到跨 die 网关，解释一笔 SDMA 事务的完整数据路径、阻塞原因和延迟。
>
> 范围：片内 NoC 与封装内 die-to-die。板级 PCIe switch、以太网 switch、多节点 scale-out fabric 不在本篇展开。本文不是 AMD 某代 GPU 的内部设计说明，不把教学参数冒充厂商实现。

## 摘要：先确定我们到底要“实现什么”

一个能工作的互联，必须同时解决三种问题。第一是运输问题：数据从哪个输入进入、从哪个输出离开。第二是资源问题：下游没空间、多个输入抢一个输出、事务超过缓冲容量时，状态如何保持一致。第三是语义问题：响应属于谁、写入何时算完成、发生重放会不会执行两次、请求和响应会不会相互等死。

本文先定义一套小而完整的**参考设计 R0**：二维 mesh、五端口 Router、输入排队、四个 VC、128-bit 数据 flit、信用流控、确定性 XY 路由、分离的 VC allocation 和 switch allocation。然后用明确的寄存器、事件和时序把它补齐。R0 承载有限的非一致性读写事务，不实现完整 CHI 一致性协议。之后扩展出**双 die 参考设计 R1**，加入网关、整包资源预留、可靠链路教学协议和跨网络依赖隔离。

阅读时区分三个标签：

- **【来源事实】**：来自协议文档、原始论文或已阅读的公开实现，附参考编号。
- **【本文设计】**：为构造自洽微架构而选择的参数、包格式和状态机；不是标准要求，也不声称是唯一方案。
- **【推导/检查】**：从已声明假设得到的计算、反例或可执行检查；不等同于流片验证。

经典 VC Router 的结构可以在 Peh/Dally、Mullins 等原始论文中找到；BookSim 和 Garnet 提供进一步对照。需要特别注意，**不同实现可以把 VA 与 SA 合并**，因此下面的分离流水线是一种教学基线，不是“所有 Router 都必须这样做”。[R1][R2][R3][R4]

## 阅读路线

| 层次 | 对应章节 | 读完应能回答的问题 |
|---|---|---|
| 全局定位 | 1—3 | NoC、Router、crossbar、网关和 PHY 分别在哪一层？ |
| 数据与端点 | 4—6 | 包长什么样？Requester 怎样进入网络？ |
| Router 核心 | 7—15 | FIFO、RC、VA、SA、crossbar、credit 怎样逐拍协同？ |
| 网络正确性与实现 | 16—21 | 如何处理拥塞、死锁、QoS、ordering、CDC 和异常？ |
| 性能建模 | 22—23 | 首 flit、尾 flit、吞吐和 outstanding 怎样计算？ |
| D2D | 24—30 | 多 die 怎样连接？CRC、重放、网关和 PHY 如何配合？ |
| 系统闭环 | 31—35 | 如何算 SDMA 的端到端代价，并配置、验证和调试？ |
| 证据与局限 | 36—37 | 读了哪些资料？哪些已检查，哪些不能冒称完成？ |

---

# 第一部分：先建立整体层次

## 1. Switch 不是一个固定层级的名字

### 1.1 从系统一直打开到门级功能块

```text
Package / System
|
+-- Die A
|   +-- CPU / GPU / SDMA / other requesters
|   +-- Address translation / protection, where required
|   +-- Network Interface, NI / NIU
|   +-- On-die NoC
|   |   +-- Router
|   |   |   +-- Input ports and VC FIFOs
|   |   |   +-- Route computation, RC
|   |   |   +-- Virtual-channel allocator, VA
|   |   |   +-- Switch allocator, SA
|   |   |   +-- Crossbar and pipeline registers
|   |   |   +-- Output-VC ownership and credit state
|   |   +-- Forward links and reverse credit links
|   +-- D2D gateway / protocol bridge
|   +-- Link adapter
|   +-- PHY
|
+========== package channel ==========
|
+-- Die B: PHY -> adapter -> gateway -> NoC -> NI -> memory side
```

这里有三个容易混淆的“交换”。Router 中的 **crossbar** 是数据选择矩阵；**NoC Router** 除了 crossbar，还包含排队、路由、流控和资源状态；系统中的 **D2D switch/gateway** 可能连接多个 NoC 或 D2D 端口，决定一笔事务应去哪个 die。一个点对点 D2D 链路本身不必具有多目的地交换能力。

因此，问“switch 有几个 buffer”之前，先问指的是哪一个方框。问“switch 是否支持一致性”也要分清：是运输一致性消息，还是自己承担目录、snoop、home-node 和完成语义。

### 1.2 UCIe 链路不是一个天然的多端口路由器

```text
Die A                                                    Die B
Requester -> NI -> NoC -> Gateway -> Protocol/Adapter -> PHY
                                                           ||
                                                        Package
                                                           ||
Memory   <- NI <- NoC <- Gateway <- Protocol/Adapter <- PHY
```

UCIe 的协议层、D2D Adapter 和物理层是不同职责；协议复用也不等于按任意目的地址选择 die。若要做多端口 die 互联，路由决策仍必须放在网关、上层 fabric 或专用交换节点中。[R10]

在完整一致性系统中，还可能出现 `CHI -> CHI-C2C -> transport`。Arm 的系统架构资料明确把 CHI-C2C 封装与所选传输层分开，UCIe streaming 是其中一种运输选择。不能据此假定“把普通 CHI 信号直接接到任意 UCIe PHY 就兼容”。[R12]

## 2. 为什么不能只用几组 MUX

假设 SDMA 和 CPU 都要访问两个存储控制器。两个请求去不同控制器时，最好同时通过；去同一控制器时，只能仲裁；某控制器暂停时，不能丢掉已经接受的数据；读结果晚回来时，还要找到原来的 requester 和 transaction。

```text
                 +------ MC0
SDMA ----+       |
         +-- SWITCH
CPU -----+       |
                 +------ MC1

Case A: SDMA -> MC0, CPU -> MC1 : 可以并行
Case B: SDMA -> MC0, CPU -> MC0 : 输出冲突
Case C: MC0 stopped            : 必须缓存并反压
Case D: responses return      : 必须恢复来源与事务身份
```

单个组合 MUX 只解决“本周期选哪一根线”。它没有保存未完成包、响应归属、下游空间和异常恢复状态。因此，真正的互联微架构是 **MUX 数据面 + 分布式资源管理 + 端到端事务管理**。

点对点连接并不是错误方案。IP 很少、带宽独占、物理距离短时，它可能更合适。NoC 的价值是使连接、并行性和物理布局可扩展，不是保证所有场景都比直连延迟低。

## 3. 先把 R0 的边界和参数固定下来

以下全部为【本文设计】。把参数固定下来，后面的“什么时候满”“谁更新哪个计数器”才有确定答案。

| 项目 | R0 选择 | 设计含义 |
|---|---|---|
| 拓扑 | 单 die 4×4 mesh | 无环回边，不是 torus |
| Router 端口 | N/E/S/W/Local，最多五入五出 | 每个方向分别有发送和接收通路 |
| 数据宽度 | 128 bit，即 16 B/flit | 不包含 valid、VC、H/T 边带 |
| 传输速率 | 每输出每周期最多一个 flit | 示例频率 1 GHz，不是时序收敛结果 |
| VC | 每物理输入四个 | 请求 VN 两个 VC；响应 VN 两个 VC |
| Buffer | 每 VC 八个槽 | 寄存器式 FIFO，先不假定 SRAM 宏 |
| 包占有规则 | 一个 VC 同时归一个 packet | 直到 tail 被本 Router 取走 |
| 输出 VC 复用 | 等下游返回 tail-free indication | 不在本端 tail 发出时立刻重新分配 |
| 路由 | XY，先 X 后 Y | head 计算，body/tail 继承 |
| 仲裁 | VA 与 SA 分离；SA 为两级 RR | packet 级资源和 flit 级带宽分开 |
| 数据可靠性 | 正常工作时片内 flit 不丢失 | 检测到内部严重错误进入受控故障处理 |
| 事务 | 16 B 对齐，长度为 16 B 的倍数，最多 256 B | 不支持任意 byte enable、原子、snoop、多播 |
| 地址 | 已完成必要翻译的 48-bit 目标地址 | Router 不执行页表遍历 |
| ordering | 普通流允许独立事务乱序；ordered 流由 NI 限制并发 | 不把 FIFO 顺序误当完整内存模型 |

每方向的输入和输出是两条逻辑通路。一个 Router 可以同时从 West 接收、向 West 发送；这不意味着同一条单向线在两个方向共用。

R0 只实现有限的非一致性读写运输。若扩展为 CHI，必须增加协议节点职责、消息依赖、更多资源类别和一致性状态机；“能装下 CHI 字段”远远不等于“实现 CHI”。

---

# 第二部分：先确定包，再确定端点

## 4. Transaction、packet、flit、物理传输不是同一个东西

```text
SDMA command: copy a large region
       |
       +-- read transaction 0
       +-- read transaction 1
       +-- write transaction 0
       +-- completion / fence sequencing

One transaction
       +-- request packet
       +-- response packet

One data packet, R0 example
       [HEAD][DATA0][DATA1] ... [DATA15, TAIL]
          |      |                         |
          +------ each item is one flit ---+

One flit
       +-- may fit one link transfer
       +-- or be serialized into several physical transfers
```

一个 transaction 可以产生多个 packet；一个 packet 可以有多个 flit；一个 flit 是否能在一个物理周期送完，取决于链路宽度与时钟。`phit` 常被用来描述一次物理传输单元，但并非所有规范使用这个名字或同一个粒度。

R0 规定 128-bit flit 一周期通过一条 128-bit 数据通路。以后若把链路缩成 32 bit，一 flit 需要四个传输节拍；除非提高频率或并行通道数，带宽就会降低。

### 4.1 R0 的 128-bit head 格式

下面是原创教学格式，**不是 AXI、CHI 或 UCIe 的标准 flit**。

```text
127                    112 111             100 99           92
+-----------+-------------+-------------------+------+------+
| DstID 8   | SrcID 8     | TransactionID 12  | Op 4 | QoS4 |
+-----------+-------------+-------------------+------+------+
91         84 83       80 79                              32
+------------+-----------+----------------------------------+
| Length-1 8 | Attr 4    | Address 48                       |
+------------+-----------+----------------------------------+
31                      16 15             8 7              0
+-------------------------+----------------+----------------+
| Context 16              | Epoch 8        | Status 8       |
+-------------------------+----------------+----------------+
```

| 位域 | 宽度 | 本文定义 |
|---|---:|---|
| `[127:120] DstID` | 8 | `die[3:0], y[1:0], x[1:0]`，目的 NI/节点 |
| `[119:112] SrcID` | 8 | 同样编码源 NI，不一定直接等于一个软件 queue |
| `[111:100] TransactionID` | 12 | 在源 NI 的有效事务集合内标识一次事务 |
| `[99:96] Op` | 4 | 0 读请求，1 写请求，2 读响应，3 写响应，4 错误响应 |
| `[95:92] QoS` | 4 | 预留分类；R0 纯 RR，不假装已经提供带宽保证 |
| `[91:84] Length-1` | 8 | 请求/数据响应的有效字节数减一；无数据确认忽略该域 |
| `[83:80] Attr` | 4 | 示例：ordered、privileged、两位安全域标签 |
| `[79:32] Address` | 48 | 目标地址；响应可按规则回送或置零 |
| `[31:16] Context` | 16 | NI 分配的上下文标签，不代表直接采用 AMD VMID/PASID |
| `[15:8] Epoch` | 8 | 区分受控重启前后的事务世代 |
| `[7:0] Status` | 8 | 请求置零，响应表示成功或错误类别 |

`SrcID` 表示 NI。如果多个 requester 汇聚到一个 NI，NI 要把 `(requester, original ID, ordering stream)` 映射成内部 TransactionID，并保存反向映射。Router 不必为每一个软件队列认识一套身份。

`Epoch` 不是无限有效的防旧包机制。八位会回绕；重新使用一个 epoch 前，必须保证旧世代包已经清除，或通过更大的世代空间和系统重置协议避免别名。

### 4.2 H/T 和 VC 为什么放在边带

R0 的单跳接口为：

```text
Forward: valid, data[127:0], vc[1:0], head, tail
Reverse: credit_valid, credit_vc[1:0], vc_free
```

head/tail 使 Router 不必解码业务 Op 才能判断包边界。VC 让接收 Router 知道当前 flit 应进入哪个输入 FIFO。VC 是**单跳资源编号**：R0 的 West.VC1 可以映射到下一个 Router 的 East.VC0，没有必要端到端保持 VC1。

FIFO 已经按 VC 分银行，因此每个槽存 `128-bit data + H + T`，而不必再保存自己的 bank 编号。原始容量为：

```text
5 ports × 4 VCs × 8 slots × 130 bits = 20,800 bits = 2,600 bytes
```

这没有计入 head 缓存、指针、路由状态、credit、流水寄存器、ECC 和实现浪费，更不是最终芯片面积。

### 4.3 四种包长度例子

```text
Read request, 256 B requested:
  [H=T=1, Op=ReadReq, Length-1=255]                  1 flit

Write request, 256 B data:
  [H=1,T=0][16 B] ... [last 16 B,T=1]             17 flits

Read response, 256 B data:
  [H=1,T=0][16 B] ... [last 16 B,T=1]             17 flits

Write acknowledgement / error:
  [H=T=1, Op=WriteRsp or Error]                     1 flit
```

注意读请求的 `Length-1=255` 不表示该请求包本身有 256 B 数据；它表示要读多少数据。包的实际 flit 数由 Op 与长度共同确定。NI 在注入前检查合法性，Router 的包边界检查再防止畸形 H/T 序列。

256 B 数据使用 `16 B header + 256 B data = 272 B` 主数据通路流量，效率是 `256/272 = 94.12%`，还未计边带、空周期或其他业务。

## 5. NI：不能把所有复杂性都推给 Router

```text
Requester interfaces
  | address / command / data / original ID
  v
+---------------------------------------------------------+
| NI                                                      |
|  Admission / range / alignment / permission checks       |
|  Address-to-destination map                             |
|  Transaction table and ID translation                   |
|  Ordered-stream issue gate                              |
|  Request packet buffers / response reservations          |
|  Packetizer -> VN/VC injection arbiter                   |
|  Depacketizer <- response buffers <- response link        |
|  Completion / error delivery                            |
+---------------------------------------------------------+
  | packet flits + local credit contract
  v
Router Local port
```

### 5.1 事务表究竟保存什么

【本文设计】每个有效表项至少包含：`valid、source requester、original ID、context、epoch、op、destination、expected response bytes、received bytes、response-buffer slot、ordering stream、completion state`。

表项在**接收 requester 的新事务之前或同一次不可撤销接受事件中**分配。不能先告诉 requester 已接受，下一拍才发现没有表项。对于读事务，还必须保证将来有地方接收结果。

事务表的生命周期比一个 Router VC 长。请求离开本 NI 的 Local port 后，事务表依然有效；只有完整响应按上层接口规则交付、错误收尾完成，才能复用 ID。看到响应 head 就释放表项，会让后续 body 找不到接收位置。

### 5.2 一种保守、容易实现的注入规则

R0 选择：写请求在 NI 内收齐整个有效载荷后再注入；读请求分配完整返回数据空间后再注入。这样一个 Router 已经收到了 head，却永远等不到本地 requester 产生 tail 的风险被限制在 NI 之前。

代价是 NI 需要包级缓冲，首包延迟更长。以后可以改成流式写入，但必须重新规定：生产者是否保证前进、可暂停多久、其他 VC 能否旁路、取消事务时怎样释放已占用网络资源。

### 5.3 请求和响应的资源必须分开考虑

```text
Bad dependency:
  response FIFO full
       -> wait for new write request to leave
       -> new write blocked by request network
       -> request network waiting for responses to drain

R0 rule:
  read response reservation exists before read issue
  response ejection does not require issuing another request
```

SDMA 可以在响应被接收之后再等待写出机会，但不能因为写口堵塞，就把已经承诺接收的所有读响应空间都拿走。将数据临时存在 SDMA 自有搬运缓冲里，是切断这种依赖的一种方式。

### 5.4 ordered 流如何简化

R0 不在所有 Router 里实现复杂 reorder buffer。对于标为 ordered 的 `(requester, context, stream)`，NI 同时最多放行一个需要完成顺序的事务；得到定义的完成后再发下一个。普通独立事务允许多 outstanding，响应由事务表匹配。

这会降低 ordered 流吞吐，但其语义简单。它不是完整 AXI ordering 的替代品，也不自动保证跨两个独立 requester 的全局顺序。

## 6. 一个最小可工作的目标端

目的 NI 也不是“去掉包头就结束”。它至少需要：包重组、合法性检查、目标接口转换、返回路径信息、响应空间和错误响应能力。

```text
NoC ejection
  -> reserve request slot
  -> reconstruct address / data / source / txn
  -> target access
  -> wait for target-defined completion
  -> construct response {Dst=original Src, Txn=original Txn}
  -> response VN injection
```

为了建立最小闭环，可以先把 target 定义成一个受控 SRAM 控制器：读在数据取出后响应；写在数据写入该 SRAM 且后续该控制器读能观察到后响应。若替换成缓存、DRAM 控制器或带 posted-write 的桥，就必须重新声明 completion point。

对无法译码、越权或不支持的事务，目标 NI 返回可关联到原事务的错误；内部 Router 不能随手丢掉一个 body flit 后假装后续包仍然完整。

---

# 第三部分：真正打开 Router

## 7. Router 的数据面与控制面

```text
                          CONTROL
             +----------------------------------+
             | RC -> VA -> SA-I -> SA-II         |
             | route  owner  nomination  grant   |
             +------------+---------------------+
                          | grants / selections
                          v
IN0 -> [VC0..VC3 FIFO] -> [VC select] --+
IN1 -> [VC0..VC3 FIFO] -> [VC select] --+
IN2 -> [VC0..VC3 FIFO] -> [VC select] --+-> [5 x 5 XBAR] -> ST/LT -> OUTs
IN3 -> [VC0..VC3 FIFO] -> [VC select] --+
IN4 -> [VC0..VC3 FIFO] -> [VC select] --+
                    DATA

Upstream credits <- input pop          downstream credits
                                      -> output-VC state
```

图中的箭头不是说数据先经过 RC 再经过 VA 算法本体。数据主要留在 FIFO，RC/VA/SA 操作的是 header、状态和请求向量。只有获得最终传输资格后，数据才被读出并通过 crossbar。

五个输入可以同时各接收一个 flit，五个输出也可能同时各发送一个 flit。但同一个物理输入，R0 每拍只能选一个 VC 读出；同一个输出每拍只能有一个赢家。这两个约束必须由仲裁器共同保证。

## 8. Input port 与 VC FIFO：多个 requester 是否有独立 buffer

### 8.1 requester、input port、VC 不是一一对应

```text
Requester A --+
Requester B --+-> upstream NI/router -> one physical link -> Input West
Requester C --+                                         |
                                                        +-- Req VC0 FIFO
                                                        +-- Req VC1 FIFO
                                                        +-- Rsp VC2 FIFO
                                                        +-- Rsp VC3 FIFO
```

West 输入的流量可能来自很多远端 requester。这里的四个 FIFO 按 VC 区分，不按 requester 名称永久分配。一个 packet 获得某 VC 后，暂时独占该 VC；释放后，另一 requester 的 packet 可以使用它。

如果必须防止某 VF/租户垄断资源，应在 NI、VC 分配或 shared-buffer quota 中增加隔离规则。仅仅看见“每输入四个 VC”不能推出“支持四个 requester”或“每 requester 有四个 FIFO”。

### 8.2 每个输入 VC 保存哪些状态

| 状态 | 用途 | 典型更新事件 |
|---|---|---|
| `mem[0..7]` | 存 128-bit data 与 H/T | 合法 flit 到达 |
| `rd_ptr/wr_ptr` | FIFO 读写位置 | pop / push |
| `occupancy` | 当前存储槽数，0—8 | `push - pop` |
| `packet_state` | IDLE、RC、WAIT_VA、ACTIVE | head、route、VA、tail |
| `route_out` | 该包选择的输出端口 | RC 成功 |
| `assigned_outvc` | 下游已分配 VC | VA grant |
| `vn` | 请求/响应类别 | head 检查/端口约束 |
| `head_sent` | head 是否已离开 | head 的 SA commit |
| `packet_qos/age` | 可选 QoS/等待信息 | head 到达、等待、释放 |
| `boundary/error state` | 检测非法包序列 | 每次 push/pop |

`occupancy==0` **不意味着 VC 空闲**。如果 head 已经发送、body 还没到，这个 VC 依然属于原 packet，route 和 assigned_outvc 必须保留。

### 8.3 FIFO 的同拍 push/pop

```text
occupancy_next = occupancy + push - pop
rd_ptr_next    = pop  ? (rd_ptr + 1) mod D : rd_ptr
wr_ptr_next    = push ? (wr_ptr + 1) mod D : wr_ptr
```

四种情况分别是保持、只写、只读、同时读写。计数器应能表示 0 到 D，因此 D=8 时 occupancy 需要四位，不是三位。指针可以用三位，但两者的用途不同。

“满时同拍出一项又进一项”是否允许，取决于接收侧契约。R0 的上游依据已经获得的 credit 发送，因此**不能依赖一个尚未返回的本拍 pop 来冒险发送**。接收 FIFO 应承受所有合法已预留在途 flit，而不是靠组合 READY 在最后一刻补救。

### 8.4 为什么这里先选择寄存器 FIFO

浅、宽 FIFO 可以用寄存器和组合读构成，队头可供仲裁准备。若换成同步 SRAM，地址提交到数据出现可能额外一拍；还必须解决多个 VC 队头预取、bank 冲突、读写端口数量和 read-during-write 语义。

因此，`D=8` 的抽象容量不够定义硬件。还要说清楚存储端口和读延迟，否则“SA 后立刻把数据送 crossbar”可能没有数据可用。R0 假设每输入可获得所选 VC 的队头，采用显式 ST 寄存器接住数据；SRAM 优化需要重新画流水线。

## 9. Route Computation：选择方向，而不是分配资源

### 9.1 XY 的组合逻辑

```text
if dst.x > current.x: East
else if dst.x < current.x: West
else if dst.y > current.y: North
else if dst.y < current.y: South
else: Local
```

此处 North 取 y 增大方向，是本文约定，不是所有网格图的通用坐标约定。

路由结果保存为 `route_out`。对于同一个 packet，body 和 tail 不重新根据业务地址计算方向。否则它们可能和 head 分离，破坏路径、缓冲占有和包边界。

### 9.2 Address decode 与 RC 分工

NI 把地址范围转换成 `DstID`，例如确定该地址属于哪个 memory-side NI。Router 用 DstID 决定下一跳。这样每个中间 Router 不必都保存完整系统地址映射。

```text
Address -> NI address map -> DstID
DstID + local coordinates -> Router RC -> output port
```

这是 R0 的选择。实际互联也可以用地址、source route、查表或混合方式路由，但必须在设计中选定，不能一句“按地址或 ID 都可以”之后省掉具体实现。

### 9.3 无效目的地如何处理

NI 注入前检查目的节点是否存在。边界 Router 禁止向不存在的 N/E/S/W 端口发包。检测到内部路由矛盾时，记录错误并进入受控处理，而不是任意改道。临时改变方向可能破坏 XY 的死锁约束。

### 9.4 自适应路由增加了什么

如果 RC 可以从 East/North 两个最短方向择优，就需要拥塞信息、选择规则、信息时效和安全逃逸路径。动态选择不是简单 `pick smaller occupancy`：两个 Router 看到的状态可能已经过期，路由变化也会改变通道依赖图。

R0 因此先不支持 adaptive routing。先使确定性网络正确，再研究如何增加自适应能力，比从一开始把所有优化混在一起更容易验证。

## 10. Virtual-channel Allocation：预订下一个 Router 的一间“房间”

### 10.1 分配的不是 crossbar 时间片

```text
R0 West.VC0 -- wants East output --> R1 West.{VC0,VC1}
                                     ^
                                     only request-VN VCs

VA chooses one downstream VC and records ownership.
SA later chooses which cycle can carry an actual flit.
```

VA 解决“这个 packet 在下一个 Router 使用哪个 VC”。即使 VA 成功，输出线仍可能被另一 VC 的 flit 占用；即使线空闲，也可能因为没有下游 VC 而无法发送新 head。

### 10.2 每个输出 VC 的状态是远端输入资源的镜像

本 Router 的 `outvc_state[East][v]` 对应邻居 Router 的 West 输入 VC。R0 至少保存：

```text
ownership: IDLE / RESERVED / DRAIN_WAIT
owner:     (local input port, local input VC)
credits:   0..D
```

`ownership` 与 `credits` 必须分开。长包的 head 已被下游转发、所有已发送 body 也被转发时，credits 可以回到 D，但 tail 还没发完，VC 仍属于原包。

这个区别可以在 Garnet 的输出状态与 credit 处理代码中直接看到：收到普通 credit 只增加空间；收到带 free 标志的 credit 才将输出 VC 标记空闲。[R6]

### 10.3 R0 的可实现 VA 算法

把每个等待 VA 的输入 VC 看成一个申请者，总计最多 20 个。每个输出端口有四个 VC，但申请者只能选择其 VN 允许的两个。

一个简单的两步实现是：

```text
Step 1: each WAIT_VA input VC nominates one eligible IDLE output VC
Step 2: each nominated output VC runs RR among its applicants
Commit: each winner reserves that output VC and updates its own mapping
```

每个输入 VC 只提名一个目标，因此不会同拍得到两个 grant；每个输出 VC 只有一个仲裁器，因此不会分配给两个输入 VC。不同输入 VC 可以同拍预订同一物理输出的不同 VC，这是合法的，因为 VA 没有承诺它们同拍传数据。

候选 output VC 的选择需要公平轮转或其他前进策略。固定永远选编号最小者可能降低利用率。R0 允许这一级匹配非最优，下一拍重试；不能把这个简单实现描述成 maximum matching。

### 10.4 时钟边界上的原子性

所有仲裁器应读取本拍旧状态，生成 grant，再在同一时钟边界统一更新。不能让软件模型先更新 VC0 的 ownership，后执行的另一个仲裁器却像“提前知道本拍结果”一样重新挑选，除非硬件真的实现了对应的组合级联。

多周期 VA 还需要 reservation 或 grant-valid 检查：某个输出 VC 在请求进入流水线时空闲，不代表两拍后提交时仍空闲。R0 先采用单个 VA 计算阶段与统一提交，避免隐藏这类状态竞争。

## 11. Switch Allocation：解决本周期的真实竞争

### 11.1 什么叫 eligible

一个输入 VC 要申请 crossbar，R0 要同时满足：

```text
nonempty
AND packet_state == ACTIVE
AND route_valid
AND assigned_output_VC_valid
AND output_credit > 0
AND head/body pipeline timing ready
AND output/link Active
AND any required ordering gate passed
```

“FIFO 里有数据”只是其中一个条件。没有 credit 时，它不是一个能够实际发送的候选者。把它不断选为赢家，会制造无效 grant 和带宽空洞。

### 11.2 两级 SA 为什么必不可少

```text
SA-I: one nomination per physical input

Input0: VC0 -> East, VC1 -> North, VC2 blocked
             RR picks one VC

SA-II: one winner per physical output

Input0 nomination --+
Input1 nomination --+--> East arbiter --> one final winner
Input2 nomination --+
```

如果只做“每输出一个 arbiter”，Input0 的两个 VC 可能同时赢得 East 和 North。但 R0 Input0 只有一个读口、一条进入 crossbar 的总线，无法真的送两份数据。SA-I 就是为了先满足每输入最多一份数据的约束。

最终 grant 矩阵必须满足：

```text
for each input i:  sum_o grant[i][o] <= 1
for each output o: sum_i grant[i][o] <= 1
```

这使 grant 成为一个输入—输出二分图匹配。Crossbar 非阻塞，指的是一个合法无冲突匹配可以同时通过，不是说它能让多个输入同拍占用一个输出。

### 11.3 三路竞争的逐拍例子

假设三个输入各有一个长期 eligible 的 VC，都去 East，credit 始终足够，East 初始 RR 指针指向 I1。

```text
cycle       eligible inputs        winner       next pointer
  0             I0 I1 I2              I1             I2
  1             I0 I1 I2              I2             I3
  2             I0 I1 I2              I0             I1
  3             I0 I1 I2              I1             I2
```

指针 I3 不要求 I3 有请求；仲裁器从该位置环绕扫描，跳过未申请者。若 cycle 2 East credit 为零，则没有 commit，指针不因一个虚假的“轮到你了”而前进。

### 11.4 简单 SA 并不保证最大吞吐匹配

```text
I0.VC0 -> East
I0.VC1 -> North
I1.VC0 -> East

SA-I chooses: I0.VC0 and I1.VC0
SA-II gives East to I1
Result: one transfer; North idle

A better matching exists:
I0.VC1 -> North, I1.VC0 -> East
Result: two transfers
```

这个例子说明：增加 VC 不代表自动吃满输出；仲裁算法可能没有看见某个可行并行组合。可以用迭代匹配、更复杂提名、优先空闲输出或内部 speedup 改善，但要付出逻辑深度、面积或延迟。

Garnet 的公开代码是研究两级仲裁的具体入口：输入选择、输出选择、成功后更新 RR 指针，以及 head 在获得输出机会时分配 VC。它的 VA/SA 组合方式与本文 R0 分离 VA 不同，不能混写成同一个实现。[R5]

## 12. Round-robin 的 RTL 思维方式

### 12.1 最简单的参考逻辑

```text
winner = NONE
for offset = 0 .. N-1:
    k = (pointer + offset) mod N
    if request[k] and winner == NONE:
        winner = k

if transfer_commit:
    pointer_next = (winner + 1) mod N
else:
    pointer_next = pointer
```

这是行为描述。综合可用旋转、priority encoder、mask 两次编码等结构实现；不是要求在电路中放一个顺序执行的 CPU 循环。

### 12.2 request、grant、commit 必须分开

request 是“希望传”；grant 是仲裁器的选择；commit 是“相关数据和资源状态都能不可撤销地前进”。在有输出 skid buffer 或可暂停流水级的设计里，grant 不一定等于 commit。

R0 规定：SA 已确认 credit 并预留后续不可阻塞 ST/LT 槽，最终 grant 在边沿作为 commit。这个边沿统一发生：FIFO pop、下游 credit 扣减、RR 指针推进、返回上游 credit、ST 元数据锁存。

```text
                 one atomic SA commit event
                /        |       |         \
           FIFO pop   credit--   RR++    latch {data,route,VC,H/T}
```

若加入可阻塞输出 FIFO，必须修改 commit 条件；不能仍然在“猜测 grant”时把 FIFO 弹出。

### 12.3 公平性到底保证到哪里

对于一个孤立输出 arbiter，在固定 eligible 集合和持续服务条件下，RR 可给出有限的轮转等待。若有 N 个持续申请者，轮转量级是 N 次成功服务。

但完整两级 SA 中，某 VC 是否能在 SA-I 被提名、下游是否有 credit、所需 VC 是否空闲都在变化。不能据“用了 RR”就宣称每个 requester 必在 N 个墙钟周期内完成。严格 QoS 延迟界需要对注入、所有瓶颈和服务策略一起约束。

## 13. Crossbar 与 ST/LT：数据什么时候真正离开 FIFO

### 13.1 数据矩阵

```text
             I0      I1      I2      I3      I4
              |       |       |       |       |
Output E  <---+-------[selected 128-bit input]----+
Output N  <---+-------[selected 128-bit input]----+
Output S  <---+-------[selected 128-bit input]----+
Output W  <---+-------[selected 128-bit input]----+
Output L  <---+-------[selected 128-bit input]----+
```

一个直观实现是每输出一个 5:1、128-bit 宽 MUX，选择 SA 给出的输入。实际物理实现还涉及扇出、布线、时钟和寄存器位置。

VC 增加不一定把 crossbar 变成 20×20。R0 在每个输入先从四个 VC 选一个，再进入 5×5 crossbar。更多 VC 主要增加 FIFO、状态、VC 选择和仲裁成本。

### 13.2 每一级必须锁存与数据一致的元数据

ST/LT 不能只保存 data，还需要保存该 flit 的 output、下游 VC、H/T 和 valid。尤其在 tail 的 SA commit 后，本地 input VC 可以转 IDLE 并被新包复用；旧 tail 仍在 ST/LT 中。若流水线还去读已经被新包改写的 `route_out`，旧 tail 会被送错位置。

这类 bug 的根本原因是混淆“包的当前状态”与“已经离开 FIFO 的 flit 的状态”。

### 13.3 pipeline latency 与 throughput 是不同量

五拍才能把第一个 head 送到下一跳，不代表每五拍只能发一个 flit。只要各级能每拍接受新项，就可以形成流水线，稳定状态每拍一 flit。

相反，把所有组合逻辑塞成一拍，可能降低可达频率，导致以 ns 计的延迟和以 GB/s 计的吞吐都变差。必须看时钟周期，而不只看 stage 数量。

## 14. Credit 流控：用守恒关系防止覆盖下游

### 14.1 credit 代表的是预留许可，不是瞬时探测

```text
Router A                                      Router B
output VC state                              input VC FIFO
C available credits                         D storage slots
       |                                          |
       +--- flit, already charged to C ---------->|
       |                                          | pop
       |<----- credit for a released slot ---------+
```

A 无法零延迟看到 B 的占用。它根据初始化得到的 D 个许可，以及后来收到的返回许可发送。在 R0 中，扣减发生在 **SA commit 时**，即 flit 进入不可撤销前向流水线之前；不能等到两拍后 PHY/link 真正发出时才扣，否则流水线中的多份数据可能重复消费同一 credit。

### 14.2 四项守恒

对一个输出 VC 定义：

```text
C: A 当前可用 credit
F: 已扣 credit、尚未写入 B FIFO 的前向在途 flit
Q: B FIFO 中尚未 pop 的 flit
R: B 已释放、但 credit 还没返回 A 的槽

C + F + Q + R = D
```

R0 所有正常传输动作只在这四项之间搬移一个 token：`C->F->Q->R->C`。任何额外加一次 credit、漏扣一次、丢掉一次返回，都破坏守恒。

```text
C_next = C - send_commit + credit_return
Q_next = Q + receive_flit - pop
```

同拍 send 和 return 可以让 C 不变，但两个事件都必须被记账。C=0 时是否允许用同拍刚返回的 credit 发出，取决于组合旁路；R0 保守地只用本拍逻辑可见的寄存器状态，不跨未定义时序边界借 credit。

### 14.3 槽释放与 VC 释放是两个事件

- 普通 pop：返还一个 buffer slot，`vc_free=0`。
- tail/HEAD_TAIL pop：返还一个 slot，并带 `vc_free=1`。

本地输入 VC 在自己的 tail pop 后回到 IDLE；上游对该 VC 的 ownership 视图，要等 free indication 到达才改变。某节点发出 tail，只能说明它已经不再需要那个包的本地输入状态，不能说明下一个节点也已经处理完 tail。

```text
A sends TAIL -----forward-----> B receives TAIL
     |                               |
     |                         B may wait / arbitrate
     |                               |
     |                         B pops TAIL
     |<------ free credit -----------+
     |
A can allocate B's VC to a new packet
```

BookSim 对“等 tail credit 再复用”和较早复用的策略有所区分。R0 选择前者，换取一个 VC 内不混入多个 packet 的简洁性；这不是唯一合法实现。[R3]

### 14.4 reverse credit 也要有实现

R0 每物理输入每拍最多 pop 一个 flit，因此它每拍最多产生一个返回事件。一条含 VC 编号和 free 标志的专用反向通道能够承载该速率。

如果加入多读口或内部 speedup，同拍可能产生多个 credit；此时要增加反向带宽、计数返回或 credit FIFO。不能扩大前向吞吐却忘记返回许可也需要吞吐。

反向 credit 不依赖普通请求/响应 packet 排队。否则“没 credit 导致数据不走，返 credit 的包又被数据堵住”可能形成新的环。

## 15. 把状态机和逐周期例子放在一起

### 15.1 输入 VC 状态机

```text
IDLE -- legal HEAD arrives --> RC
RC   -- route committed ----> WAIT_VA
WAIT_VA -- VA grant --------> ACTIVE
ACTIVE -- ordinary pop ----> ACTIVE
ACTIVE -- TAIL pop ---------> IDLE
```

head 后的 body 可以在 WAIT_VA 时继续进入，只要先前的 credit 合法、FIFO 还有承诺空间。ACTIVE 期间暂时空 FIFO 只是等待后续 flit，不转 IDLE。

H=T=1 的单 flit 包仍然需要 RC、VA 和 SA，但它在第一次 pop 时同时结束。非法序列包括 IDLE 收到 body、ACTIVE 收到另一包的 head、错误 tail 数量以及 VN/VC 不匹配。

### 15.2 输出 VC 状态机

```text
IDLE -- VA reservation --> RESERVED
RESERVED -- body/head transmissions --> RESERVED
RESERVED -- local TAIL commit --> DRAIN_WAIT
DRAIN_WAIT -- downstream free credit --> IDLE
```

RESERVED 和 DRAIN_WAIT 都不允许另一个 packet 获得该输出 VC。Credit count 在这些状态中独立增减。R0 的专用反向链路保持相关返回顺序；释放检查还应核对没有未处理的本 VC 前向数据。

### 15.3 一跳的精确定时

规定：edge 0 时 head 已写入输入 FIFO；每个列出的计算区间是一拍，时钟 1 GHz。

```text
edge / interval     head action
edge 0              input FIFO captures HEAD
[0,1]               RC
edge 1              save route
[1,2]               VA
edge 2              reserve downstream VC
[2,3]               SA
edge 3              pop, charge credit, latch ST metadata
[3,4]               crossbar / ST
[4,5]               forward link / LT
edge 5              next router captures HEAD
```

因此本文一跳 head latency 为 5 ns。这里“跳”明确包含本 Router 的处理和一段前向 LT，不可在总公式中再多加一次相同 LT。

在 head 路由和 VC 已确定、无竞争且 credit 充足时，后续 body 只需要可发送资格、SA、ST、LT，并保持包内顺序：

```text
flit          H     D0    D1    D2    ...   D15/T
input edge    0      1     2     3    ...     16
output edge   5      6     7     8    ...     21
```

三跳同宽流水网络：head 到达 edge 15，最后一项到达 edge 31，而不是 `17 flits × 3 hops × 5 cycles`。后者把能够重叠的流水阶段重复串行化了。

### 15.4 credit RTT 的取点也要明确

在这套流水线里，A 于 edge 3 扣 credit；B 于 edge 5 收到 head，edge 8 pop；假设反向返回一拍，A 于 edge 9 看到 credit，最早在下一次提交边沿 edge 10 再消费该许可。

从 edge 3 的预留到 edge 10 的再次提交，示例 credit reuse 间隔为七拍。为每拍连续发送，需要足够多 token 覆盖这段闭环。D=8 是一个有余量的教学选择，但不保证有竞争或更长反向链路时仍不断流。

### 15.5 小包还有 VC 所有权周转瓶颈

单 flit 包即使只消费一个槽，仍会占用一个 VC 直到 free 返回。按照上面的保守阶段，某个 output VC 从 edge 2 分配，到 edge 9 free 可见、edge 10 能再次完成 VA，周转约八拍。

因此一个 VN 仅两个 VC 时，持续单 flit 包可能受约 `2/8 packet/cycle` 的所有权周转限制，远达不到物理口的一 flit/cycle。这个值是特定无旁路时序下的估算，不是通用标准数值。

这解释了一个反直觉现象：**很多空 buffer slot，不代表可以接收很多新 packet。** 扩大 FIFO 深度、增加 VC 数、提前安全复用 VC、合并 VA/SA，解决的是不同瓶颈。

---

# 第四部分：从单 Router 扩展到网络正确性

## 16. HOL、buffer 组织与 area/power 取舍

### 16.1 一个 FIFO 为什么挡住本可前进的数据

```text
single input FIFO:
 [A -> busy East][B -> free North][C -> free Local]
  ^ only this item can be selected
```

如果 B 和 C 在 A 后面，而存储只允许取队头，空闲输出也没有用。增加 VC 可以让互不依赖的 packet 占不同队列，但同一个 packet 内的 body 仍不能绕过自己的 head。

### 16.2 四种常见组织方式的实现差别

| 组织 | 需要保存什么 | 主要好处 | 主要代价 |
|---|---|---|---|
| 每输入一个 FIFO | 一个读写队列 | 简单、低状态开销 | HOL 严重 |
| 每输入多 VC | 每 VC 队列和 packet 状态 | 隔离阻塞、可分资源类 | 更多仲裁与状态，容量可能闲置 |
| 按目的输出排队 VOQ | 每输入每输出队列/描述符 | 减少不同目的地之间的 HOL | 队列数与匹配复杂度增加 |
| shared buffer | 公共存储、free list、队列指针、配额 | 容量利用率较高 | 多端口/banking、分配回收、隔离困难 |

shared buffer 不是“把四个 FIFO 改成一块 SRAM”就结束。每个入口可能同拍写入；多个出口可能同拍读出；至少要设计 bank 映射、冲突仲裁、队头缓存、free-list 并发更新以及最小保留份额。

### 16.3 shared buffer 的资源承诺不能随意撤销

若上游已获得八个 credit，表示它可以在未来送来八份已授权 flit。接收方不能因为另一 VC 流量增大，就把这些已承诺槽全拿走。

一种可实现策略是：每 VC 有保证的保留容量，额外容量来自动态池；发出动态 credit 之前就将相应槽或等价 quota 预留。否则 credit 数量与实际可用存储不一致，拥塞时一定会暴露覆盖问题。

### 16.4 更多 buffer 不创造出口带宽

一个输出只能每拍一 flit，持续注入两 flit/cycle，就算加倍 buffer，也只是推迟反压开始。短突发可能受益；长期过载仍需限流、更多物理带宽或改变映射。

深 FIFO 还可能提高负载下的排队时间。选择 D 时应同时看 credit RTT、最大突发、QoS 和面积，而不是笼统地“越大越好”。

## 17. Deadlock：必须画资源依赖，而不只画数据箭头

### 17.1 什么是通道依赖图

把可被持有的通道/VC 资源视为节点。如果 packet 可以持有资源 A，同时等待资源 B，就画 `A -> B`。在适用的确定性路由模型下，用无环依赖约束构建无死锁路由，是经典方法。[R13]

```text
A holds VC_ab, waits VC_bc
B holds VC_bc, waits VC_ca
C holds VC_ca, waits VC_ab

VC_ab -> VC_bc -> VC_ca -> VC_ab
```

“每个 FIFO 都很大”“每个 arbiter 都公平”都不能消除已经存在的结构性等待环。

### 17.2 R0 的 XY 为什么有帮助

在无环回的二维 mesh 中，XY 不允许完成 Y 阶段后再返回 X 阶段；一个维度内也不会为了最短路径反复改变方向。按这套规则构造出的通道依赖可以无环。

本文附带脚本枚举 4×4 mesh 所有源—目的路径：得到 48 个有向物理通道、68 条通道依赖边，拓扑排序成功。它验证的是**这个特定 XY 通道模型**，没有包含一致性控制、复杂端点或任意自适应路由。

### 17.3 路由无死锁不等于协议无死锁

请求网络可能等目标产生响应，而目标响应又等请求网络释放空间。这种 request/response 依赖不一定出现在单纯 XY 路径图里。

R0 把请求和响应放入两个 VN，并给它们独立 VC/buffer 资源；更关键的是 NI 的响应预留和目标端前进约定，防止响应消费再依赖新的请求发出。

```text
Request VN -> target service -> Response VN -> pre-reserved sink buffer
                                                  |
                                                  +-- no dependency back
                                                      to Request VN for ejection
```

“分成两个 VN 就保证所有协议无死锁”仍然是错误的。VN 的数量与依赖分配应来自具体协议分析，而不是固定口诀。

### 17.4 Deadlock、starvation、livelock 不同

死锁是一个资源循环里谁也不能前进；饥饿是某流长期拿不到服务，但其他流仍在走；活锁是不断移动/重试，却不完成目标。XY 的有界路径可以避免随意绕路，但不能替代公平服务、目标前进和错误超时约定。

## 18. QoS：要控制“谁可以占多久”，不是只加四个 bit

R0 包头预留 QoS，但基础仲裁只做 RR。以下是【可选扩展设计】，不把“有字段”写成“已保证实时性”。

一个简单扩展可以分成三层：NI 限制注入速率；每输出先选择有资格的 traffic class；类内再做 RR。对 bulk SDMA 使用 token bucket 或带宽配额，对必须及时完成的控制流保留最低服务机会。

```text
NI token bucket -> per-class eligible set
                              |
                              v
                    class scheduler / weights
                              |
                              v
                        within-class RR
```

token bucket 保存 token 数、补充速率和最大 burst。发出一次数据按字节或 flit 扣 token，不应在一个长包只扣一次“包计数”却宣称字节带宽公平。

fixed priority 可以降低高优先级延迟，但低优先级有饥饿风险。weighted RR 的权重也必须明确按包、flit 还是 byte 记账：一个 17-flit 包和一个 1-flit 包“各一次”不是相同带宽。

硬延迟上界还要求每个瓶颈都提供足够服务，目标控制器也不能无限暂停。单个 Router 的优先级不能推导整条 NoC+D2D+DRAM 路径的 deadline 保证。

## 19. 对照真实协议：AXI 与 CHI 应放在哪一层

### 19.1 AXI4 的关键约束

AXI4 有独立的读地址、读数据、写地址、写数据和写响应通道；通道使用握手，支持事务 ID。写数据没有可用于任意交织写事务的 WID；同 ID ordering 也不能简化成“所有读写自动全局排队”。突发边界、响应和观察点都受规范约束。[R8]

R0 接 AXI4 时，一个可行的有限子集桥接方案是：先按 AW 顺序保存写上下文，把对应 W beat 收齐，检查边界和长度，再形成内部写 packet；读侧用事务表映射 ARID 与内部 TransactionID。响应侧恢复 RID/BID，并对要求保持顺序的流设置重排或注入限制。

```text
AW FIFO -----+--> write assembler --> internal WriteReq packet
W data FIFO -+
AR FIFO --------> transaction map --> internal ReadReq packet

internal ReadRsp  -> optional reorder -> R channel
internal WriteRsp -> optional reorder -> B channel
```

这里是桥的参考设计，不是对所有 AXI4 功能的完整实现。R0 没有任意 WSTRB、exclusive 和所有 burst 类型，因此 bridge 必须限定接受子集，或在 NI 中显式转换，不能静默丢弃属性。

### 19.2 CHI 的真实消息类别与我们的教学格式

Arm 的 CHI 接口资料可见 REQ、RSP、SNP、DAT 四类通道，以及 QoS、目标/来源、事务号、Opcode、地址、响应状态和数据相关标识等信息。不同通道字段不同。本文阅读到的旧版 Protocol Bundle Guide 是模型接口资料，**其中 C++ 参数类型不能直接当作当前 CHI 规范的线上位宽**。[R9]

因此只建立概念对应：

| CHI 概念 | 用来理解什么 | 不应作出的推断 |
|---|---|---|
| REQ | 操作、地址、事务及排序属性 | 所有请求都与 R0 ReadReq 一样 |
| RSP | 控制响应与完成相关消息 | 任意 RSP 都表示数据已写到 DRAM |
| DAT | 数据与数据身份、状态 | 数据 flit 只有纯 payload，没有元数据 |
| SNP | 一致性 snoop 请求 | 非一致性 R0 已经实现 snoop |
| 链路信用/事务级机制 | 不同层次的资源控制 | 全都等价于 R0 每 VC 的槽 credit |

R0 Router 只需要识别自己的 transport header 和边带。要运输 CHI，可以封装消息、映射 VN/VC；要实现 CHI，则还需要正确的节点角色、一致性状态和依赖规则。这两件事不能混为一谈。

### 19.3 为什么 FlooNoC 值得作为反例学习

FlooNoC 的论文和公开 RTL 提供了宽物理链路、NI 端事务处理与不同通道组织的实例。当前阅读的 Router RTL 含可配置输入/输出、物理/虚拟通道、FIFO 和路由选择，因此可用于观察参数怎样进入可综合结构。[R7][R15]

它提醒我们：NoC 并不必然依赖窄链路把一切序列化；将复杂顺序处理放在端点，也是一条设计路线。但论文版本与后来 main 分支 RTL 不应混作同一个冻结实现。

## 20. 流水优化：每次减少一拍，都要指出删掉了什么依赖

### 20.1 Look-ahead RC

在上游就计算下一 Router 要使用的方向，随 flit 或状态送过去，减少本跳 RC 等待。代价是更多 metadata/组合计算，且路由表变化、边界条件和拥塞信息时效需要重新处理。

### 20.2 VA/SA 推测并行

head 同时申请 VC 与 crossbar，猜测 VA 会成功。若 SA 成功、VA 失败，不能发送，也不能扣 credit/pop FIFO。应该把推测 grant 取消，避免侵占已能实际发送的 body/tail 服务机会。

Peh/Dally 的工作给出了这种优化的早期具体讨论；Mullins 等进一步研究低延迟控制路径。它们是特定电路与假设下的设计研究，不是“把几个参数设零就能单周期”的证明。[R1][R2]

### 20.3 合并 allocation

另一条路线是先确定输出赢家，再给获胜 head 选择一个可用 VC。这减少了独立 VA 阶段，但也改变了候选判定、匹配质量和拥塞行为。前文读过的 Garnet SA 实现属于值得对照的例子。[R5]

### 20.4 Bypass

如果输入 FIFO 空、输出无竞争、资源许可齐全，可以让刚来的 flit 绕过常规排队路径。必须同时满足：不越过更老的必须排序数据、credit 真实存在、输出 pipeline 有空间、失败时 flit 能落入正确 buffer。

bypass 和正常 FIFO 路径不能同时提交同一个 flit；两条路径合流处需要唯一 commit 点。否则低负载下看似低延迟，拥塞切换时却可能重复或丢包。

### 20.5 不要用模拟器阶段数代替物理时序

BookSim2 专门区分求值和更新阶段，以免模型在同一拍“提前看到”另一个流水级的更新结果。这种模拟顺序错误会把不存在的硬件旁路模拟出来。[R3]

真实评价应比较 `阶段数 × 时钟周期`、稳定吞吐、面积、功耗和验证复杂度。一个两拍低频 Router 未必胜过三拍高频 Router。

## 21. CDC、复位、电源和错误会改变正常流控契约

### 21.1 异步边界

跨时钟域不能把 128-bit data 每 bit 独立过两级同步器。常见结构是双口存储加异步 FIFO 指针同步，或者经过验证的握手机制。指针编码、同步延迟、满空判断与复位顺序必须一起设计。

```text
Clock A               Clock B
write side -> dual-clock storage -> read side
   |                               |
   +-- synchronized pointer view --+
```

CDC FIFO 能吸收有限相位/速率差，不能让长期慢于发送方的接收方无限接收。同步延迟还会扩大 credit 闭环，使原来够用的 D 不再够用。

### 21.2 复位不是把所有 counter 清零

如果 A 忽然把 credit 重置为 D，而 B 仍有旧包，A 会覆盖旧数据。正常重置顺序应先停止新注入，drain 或一致地 abort 在途事务，再让两端建立同一 epoch 和容量初始状态。

若发生无法 drain 的致命错误，要由系统协议清理相关 Router/NI 的占有和事务表，并向软件报告可能部分完成。不能只清一个 Router，然后假装其他节点的旧状态仍可继续。

### 21.3 错误的层次

地址非法通常是 NI/目标端的可返回事务错误。FIFO parity/ECC、非法 VC、缺失 tail、credit overflow 是互联完整性错误。前者通常可正常生成 ErrorRsp；后者可能已无法保证包边界，需要隔离、诊断和域级恢复。

片内不一定“无需可靠性”：可以做 parity/ECC、端到端校验、poison 或重试。是否需要哪一种，取决于错误模型和产品要求。跨 die 链路也不是必然对所有错误无限重试，持续故障必须退出正常传输。

---

# 第五部分：把延迟、带宽和容量算清楚

## 22. 首 flit、尾 flit、事务往返是三个指标

### 22.1 必须先声明测量起止点

| 指标 | 起点 | 终点 |
|---|---|---|
| 一跳 head latency | head 写入当前输入 FIFO | head 写入下一跳 FIFO |
| 单向首 flit 延迟 | 源 NI 接受/注入，需注明 | 目标首 flit 到达 |
| 单向完整包延迟 | 同上 | tail 到达并完成接收 |
| read transaction RTT | 源接受读事务 | 完整读响应按接口完成 |
| SDMA copy latency | 命令达到定义的开始点 | 目标数据与完成通知达到定义点 |

不同论文的 latency 数字若边界不同，不能直接比较。尤其 PHY datapath latency 不等于“SDMA 访问远端 HBM 的延迟”。

### 22.2 无竞争、同宽 wormhole 路径

对 R0，H 跳，每跳 head 固定延迟 `Lhop`，包长 F flits，瓶颈通道每周期一 flit：

```text
T_head = T_injection + H × Lhop + T_ejection
T_tail = T_head + (F - 1) × T_cycle
```

这些式子要求没有排队、credit 缺口、速率转换或中途整包等待。R0 的 `H=3,Lhop=5 ns,F=17` 给出网络内 `T_head=15 ns,T_tail=31 ns`。

如果不同链路速率不同，尾部跟随时间由瓶颈服务间隔和中间转换缓冲共同决定，不能把每一段 `F × serialization` 简单相加。只有真正 store-and-forward 的边界才需要等待完整前一段再启动下一段。

### 22.3 有负载时如何拆账

```text
T_path = fixed_pipeline
       + source_admission_wait
       + VC_allocation_wait
       + switch_arbitration_wait
       + credit_stall
       + rate_conversion_wait
       + endpoint_wait
```

这些项的观测窗口可能重叠。若一个 VC 同时没有 credit、也没有被 SA-I 选中，不能把同一拍在总 latency 中加两次。实现性能 counter 时应采用互斥的主要阻塞原因，或明确它们是可重叠事件计数而非可直接相加的时长。

### 22.4 为什么接近饱和时延迟上升很快

当到达速率接近服务速率，短暂突发造成的 backlog 很难被排空。实际硬件有限 FIFO 最终会反压源端；队列不一定无限长，但等待会转移到 NI、SDMA 和软件队列。

```text
latency
  ^                         / heavy contention
  |                       /
  |                    __/
  |___________________/
  +-----------------------------> offered load
                 approaching bottleneck capacity
```

这个图是定性关系，不是某个芯片的实测曲线。测量时同时记录 offered load、accepted throughput、完成速率和 p50/p95/p99，不能只展示“进入网络后的平均延迟”来隐藏源端等待。

## 23. 带宽与三种不同的 bandwidth-delay product

### 23.1 主数据通路峰值

R0 每方向 `16 B/cycle × 1 GHz = 16 GB/s`，这里 GB 使用十进制。对于连续 256 B 数据 packet，扣除 16 B header 后，理想 payload 上限约 `16 × 256/272 = 15.06 GB/s`。

这不是一个 Router 五个口都同时送给同一个 MC 的带宽。一个 MC 出口仍只有一个口的服务能力。全双工两方向带宽也不能直接加起来冒充单向复制速率。

### 23.2 credit BDP

```text
required slot count ≳ flit_rate × credit_reuse_latency
```

它决定某个链路/VC 需要多少个允许在途的槽许可，单位是 flit slots。还要考虑多个 VC 的分布、所有权周转和是否只有一个流真的可以使用这些容量。

### 23.3 transaction BDP

```text
required outstanding bytes ≳ target payload bandwidth × transaction RTT
required transactions ≳ ceil(outstanding bytes / bytes per transaction)
```

它决定 SDMA/NI 为隐藏远端访问延迟需要多少个事务，不是 Router 的 buffer 深度。中间很多 flit 已经离开 Router，事务仍可能在目标控制器执行。

### 23.4 replay BDP

```text
replay storage ≳ link transmit rate × acknowledgment latency
```

它决定已发出但尚不能删除的重放副本需要多大，通常按链路 frame/cell 的字节数计算。它不能替代接收端 packet buffer，也不能直接等同于 NoC credit。

把这三种 BDP 分开，是分析 SDMA、Router 和 D2D 容量的关键。三个计数器都可能叫“outstanding”，但计量对象和释放事件不同。

---

# 第六部分：跨 die 时究竟增加了哪些微架构

## 24. D2D 网关是流控与封装边界，不是一根加长导线

【本文设计 R1】在两个 die 的 NoC 边界加入网关。每个 die 暂只配置一条点对点 D2D 链路，不讨论任意多跳 die 拓扑。

```text
Local NoC                         D2D                         Remote NoC
       |                                                       ^
       v                                                       |
+----------------+       +--------------------+       +----------------+
| TX gateway     |       | link transport     |       | RX gateway     |
| packet slots   |------>| framing / replay   |------>| reassembly     |
| VN separation  |       | PHY / package / PHY|       | packet slots   |
| route to die   |       | ACK / link control |       | new VC injection|
+----------------+       +--------------------+       +----------------+
    local flit credits       own link resources          remote credits
```

R1 终止本地 VC 关系：网关先接收包，再在远端重新申请 NoC VC。它不会把本地 `VC1` 当作远端永恒有效的资源编号。

这可以把短 RTT 的片内流控和长 RTT 的 D2D 可靠传输解耦。代价是网关缓冲、封装、重组和可能的整包等待延迟。

### 24.1 为什么先选择整包网关

为让参考实现容易检查，R1 的发送网关在接受 head 时预留一个足够容纳整个 packet 的 slot；收齐 tail 后，才能开始此包的跨 die 发送。接收网关也收齐完整 record 后再注入远端 NoC。

不能先接受半个 packet、占住若干槽，后来才发现没有容量存剩余部分，却又等待只有在整包到齐后才释放的资源。这会在网关形成自我阻塞。

更低延迟的 cut-through 网关是可能的，但必须另外证明跨 link 重试、远端 credit 和部分包状态之间不会形成环；不能在没有这些机制时直接删除整包缓冲。

### 24.2 NoC packet 变成跨 die record

R1 添加八字节 record header：`version 1B、record length 2B、VN/class 1B、src die 1B、dst die 1B、flags 1B、reserved 1B`。多字节数使用统一大端编码。这里 length 指整个 record 长度。

```text
Read request record:
 [8 B record header][16 B NoC head]                  = 24 B

256 B data record:
 [8 B record header][16 B NoC head][256 B data]       = 280 B
```

NoC 的 VC 与 H/T 边带不原样占用 record 字节；远端依据校验后的 Op、长度和 record 边界重新生成 H/T，并重新申请合适的 VC。接收端必须交叉检查 record 长度与内部包长度一致。

## 25. 给可靠链路一个可追踪的教学实现：LRP-64

> **LRP-64 是本文原创的简化可靠链路协议，不是 UCIe 的帧格式，也不声称与任何 UCIe IP 互操作。** 它用于把 CRC、sequence、ACK、replay、接收资源与 NoC 网关的关系讲清楚。真实 UCIe 的已核验格式另见第 28 章。

### 25.1 固定 80 B cell

```text
+----------------------+-----------------------------+-----------+
| 12 B link header     | up to 64 B payload          | CRC32C 4B |
|                      | unused bytes zero padded    |           |
+----------------------+-----------------------------+-----------+
```

| 字节 | 字段 | 参考定义 |
|---|---|---|
| 0 | version/type | 高四位版本 1；低四位 Data/ACK/NAK/Credit |
| 1 | class | 0 请求，1 响应；独立接收/重放状态 |
| 2—3 | sequence | 16-bit 当前 data cell 序号 |
| 4—5 | ACK-next | 对方应发送的下一个序号；累计确认 |
| 6 | payload length | 0—64；最后一个 cell 可不足 64 B |
| 7 | flags | SOP、EOP、ACK-valid 等 |
| 8—9 | returned-packet-credit total | 累计归还 packet slot 数 |
| 10—11 | link epoch | 16-bit 链路世代 |
| 12—75 | payload/padding | 当前 record 的一段数据 |
| 76—79 | CRC32C | 覆盖前 76 B；CRC 本身大端编码 |

一个 VN 内，record 的 cells 顺序发送，不交织两个 record；不同 VN 可以在物理链路上交替传 cell。每个 VN 有自己的 sequence、expected、replay 窗口和 packet-credit 计数。

CRC32C 检错不提供身份认证或抗恶意篡改能力。安全标签也不是密码学保护；跨不可信边界还需要额外安全协议。

### 25.2 发送端状态

```text
Per VN:
  next_sequence
  oldest_unacknowledged
  replay ring[32 cells]
  replay read / write pointers
  replay_active and replay_cursor
  peer returned-credit total
  packets_started counter
  pending control mailbox
  retry timer / retry count / epoch
```

一个新 data cell 只有在 replay ring 有空间、对应 packet 已获得远端 packet credit、发送调度允许时才可提交。提交时先保存可重发的副本，再允许物理发送，最后推进 `next_sequence`。

“PHY 已发送”不能删除副本。ACK-next 确认其之前所有 cell 已被接收端校验并提交，发送端才回收对应 replay 槽。ACK 必须落在本地合法未确认窗口内，不能不经检查就把任意值当成回收指针。

### 25.3 接收端：CRC 通过后才承诺一次交付

```text
collect complete cell
       |
       v
CRC / format / epoch check
       |
       +-- bad CRC -> do not trust header, do not commit
       |
       v
compare sequence with expected
       +-- equal  -> commit payload once; expected++ ; ACK-next
       +-- older  -> duplicate; do not deliver again; repeat ACK-next
       +-- newer  -> missing earlier cell; do not commit; NAK expected
```

CRC 失败时连 class、seq 都可能被破坏，因此不能盲目使用坏 header 指定某个重放位置。简化实现可以依赖发送超时，或通过可信链路控制请求重新同步，而不是把损坏内容当控制指令执行。

接收方只在确认 packet slot 已预留且 cell 合法时推进 expected。这样 ACK 的意义不是“我看见线上波形了”，而是“这份数据已经被接收状态机可靠地接管”。

### 25.4 为什么重放不能再次扣逻辑 packet credit

第一次发送 record 的 SOP 时消耗一个远端 packet slot 许可。若第几个 cell CRC 错误，重放的仍是同一个逻辑 packet，不是新 packet。重复扣 packet credit 会逐渐耗尽许可；重复返还 credit 则会超额授权。

R1 因此按**新 packet 的首次 SOP**记 `packets_started`，按接收 packet 真正释放记累计 returned total。replay 用原 sequence，只重复物理运输，不重新创建事务或 packet 资源。

### 25.5 ACK 丢失、序号回绕和接收端复位

ACK 丢失会导致发送方重放已经提交的 cell。接收方通过 expected 检出旧序号，重复 ACK 而不再次交付。否则一次 MMIO 写或非幂等操作可能执行两次。

16-bit 序号采用模 65536 比较，未确认窗口必须远小于半个序号空间；R1 选择 32 cells。世代变化先经过双方重建状态。**若接收端在已执行副作用后丢失去重状态，链路层不能继续声称跨重启 exactly-once**。这时应报告事务状态不确定，由更高层恢复，不可随意重发 MMIO。

## 26. 两种 buffer：接收 packet slot 与发送 replay ring

### 26.1 RX packet slot

R1 每 VN 至少配置四个完整 record slot，每槽可放最大 280 B。每个 VN 的有效存储量至少 `4×280=1120 B`，另外还需要描述符、对齐和 CRC 接收暂存。

一个 slot 可以处于 FREE、ASSEMBLING、COMPLETE、INJECTING。只有对应 record 的 tail 已按远端 NoC Local 接口提交、该槽不再被读，才能回到 FREE 并增加 returned total。

```text
FREE -> ASSEMBLING -> COMPLETE -> INJECTING -> FREE
          link RX                  remote NoC
```

R1 选择每 class 同时重组一个 record，其余槽用于已完成或待注入记录。cell 的 CRC 检查和写入吞吐必须至少跟上声明的接收速率；如果做不到，要增加链路级弹性流控或降低协商速率。packet credit 本身不会修复一个来不及每拍处理数据的 CRC 单元。

### 26.2 TX replay ring

每 VN 32 cells、每 cell 80 B，至少 `2560 B/VN`；两个 VN 共 5120 B 的已发未确认副本容量，另加状态。这些副本可能对应已在对端接收、但 ACK 尚未返回的数据。

```text
local NoC credit   : free slot at next local router
remote packet credit: complete record capacity at remote gateway
replay free entry  : ability to remember unacknowledged transmission

New send may need all relevant resources, but they are not the same counter.
```

假设 link 32 GB/s，ACK 闭环为 50 ns，则在途线上数据约 1600 B，对 80 B cell 是 20 cells。32-entry ring 留有一定余量，但 ACK 调度拥塞、错误和模式开销都可能增大实际需要。

### 26.3 累计 credit 怎样避免控制包重复导致多加

初始化双方知道 K=4 个接收 slot。发送方可用 packet credit 按下式维护：

```text
available = K + total_returned_by_peer - total_new_packets_started
```

线上传回累计计数而不是“无条件加一脉冲”。重复收到同一个累计值，不会再次增加 available。计数回绕采用有界模差值，控制信息必须周期性刷新，且两个世代不能混算。

## 27. 调度、重放和链路状态机

### 27.1 数据流量不能饿死控制流量

```text
pending ACK / NAK / credit mailbox --+
replay data -------------------------+--> link scheduler --> formatter / PHY
new request-VN data -----------------+
new response-VN data ----------------+
```

R1 规定每八个可用发送时隙至少提供一次控制服务机会；两个 VN 的控制 mailbox 轮询。控制信息采用可合并的累计状态，避免因大量重复 ACK 把控制 FIFO 填满。无控制待发时，时隙可供数据使用。

控制发送不要求普通数据 packet credit，否则双方都没数据 credit 时，就可能连归还 credit 都发不出。重放也不能无条件永久压倒响应 VN；持续错误超过门限应进入故障状态，而不是无限占用链路。

### 27.2 一个教学链路状态机

```text
RESET -> PHY_INIT -> PARAM_NEGOTIATE -> CREDIT_INIT -> ACTIVE
                                                   |
                         +-------------------------+
                         v
                      QUIESCE -> DRAIN -> LOW_POWER
                         |
                         +-- unrecoverable / timeout -> ERROR
```

这是 R1 的抽象状态机，不是 UCIe 标准状态名的完整复刻。ACTIVE 前必须已确定版本、速率、容量、epoch 和控制通路。QUIESCE 禁止新事务，但仍允许在途响应、ACK、重放和资源释放。

若 DRAIN 超时，软件需要知道哪些事务可能部分完成。不能因为进入低功耗就抹掉 replay ring、packet slot 和 NI outstanding 表，然后等待旧响应自己消失。

### 27.3 链路层 retry 不等于事务层 retry

链路重放重送同一 cell，接收端消除重复，事务通常只交付一次。事务层重试可能重新访问目标，必须考虑幂等性、写副作用、原子和已经执行但响应丢失等问题。

这个区别直接影响 SDMA 的 fault recovery：普通内存复制可以采用某种软件恢复策略，不代表门铃、寄存器写、原子操作都能照搬。

## 28. 对照真实 UCIe：哪些细节已经有可靠来源

### 28.1 分层与模式

UCIe consortium 的 Hot Chips 2023 教程给出 `Protocol -> FDI -> D2D Adapter -> RDI -> PHY` 的分层，以及 adapter 的相关 CRC/retry、复用和链路管理职责。**Raw 模式不能一概套用 adapter 格式化与可靠重放的结论**，上层承担什么必须按模式确认。[R10]

UCIe 1.1 的官方说明另外介绍了 streaming 协议可使用的检错/重放机制。因此不能把旧版 streaming-only-raw 的模式表当成以后所有版本的约束。[R11]

### 28.2 一个已核验的实际 flit：68 B Format 2

Hot Chips 教程明确展示：在其指定的 PCIe non-Flit/CXL.io 68B 使用场景下，64 B 协议信息加上 2 B adapter header 与 2 B CRC，形成 68 B 格式；CRC 覆盖 header 和协议信息。[R10]

```text
[2 B adapter header][64 B protocol information][2 B CRC]
                         = 68 B
```

线上/内部宽接口可能连续打包多个这样的格式，不能推断“68 B 必须占一个 64 B 总线周期”。还存在不同 256 B 格式，不能统一假设所有版本都具有同样的 payload 字节数。

这里的 `64/68` 只是这一层协议信息效率，不是 SDMA 用户数据效率；协议信息内部仍可能有地址、TLP/header 等开销。也不能把该格式直接替换成前面的 LRP-64：两者的用途是对照，不是兼容。

### 28.3 本稿没有冒称完成的标准细节

本次未取得并逐项核验所有目标版本的完整 UCIe/CHI 合规条文，因此不提供假定为标准的 CRC 多项式、全部 sequence 位宽、retry-window 上限、完整 FDI/RDI 时序表、训练状态转换或所有 256 B 格式。

工程实现时应先锁定版本和模式，再从正式规范取得这些参数。本文用有明确标签的原创 R1 补足微架构理解，不用二手网站上的零散字段假装标准已经查全。

## 29. PHY：不仅是 serializer

### 29.1 向下打开物理路径

```text
Link cells / protocol data
          |
      width adaptation
          |
      byte/lane striping
          |
      scramble / lane mapping
          |
      TX circuits / forwarded timing
          || package channel ||
      RX sampling / alignment
          |
      lane reconstruction / deskew
          |
      link data output
```

UCIe 官方电气教程介绍了其封装、转发时钟、训练和相关物理考虑；协议教程还给出 lane 映射、重排、修复/降宽及链路状态的职责。具体可用能力随封装配置和规范版本变化。[R14][R10]

### 29.2 lane 与内部 flit 宽度不等价

若有 L 条数据 lane，每 lane 有效 bit rate 为 r，先不计编码、空闲和错误：

```text
B_raw = L × r / 8
```

这不是 `NoC flit width × NoC clock` 的另一种写法。二者中间可能有 gearbox、不同频率、多个模块和打包开销。

D2D 也不应自动被想象成一套与长距离以太网完全相同的 SerDes。时钟方式、距离、封装电气和训练目标不同，PHY 固定延迟必须取具体实现的数据。

### 29.3 training 为什么不应计入每一个 packet 的稳态延迟

训练建立能够可靠采样的链路状态；正常 ACTIVE 传输不应为每个 packet 重做完整训练。可以分开报告 cold-start latency、低功耗唤醒延迟、retrain 停顿和 steady-state data latency。

如果 benchmark 第一次搬运包含链路唤醒，而后续搬运不包含，平均值会受测试方法显著影响。

### 29.4 propagation、serialization 和 deskew 分开

封装传播约为 `T_prop = length / propagation_velocity`，由实际通道决定。Serialization 是把有效位数送过有限 lane 带宽所需时间；deskew 则需要等待相对晚到的 lane 并重新对齐。

走线很短只说明传播可能很小，不说明 adapter buffering、CDC、CRC 或训练状态带来的延迟都小。不能用 `L/v` 代替整个 PHY 延迟。

## 30. 跨 die 后必须重做死锁分析

把两个各自无死锁的 NoC 接起来，可能增加跨边界等待环；这也是模块化 chiplet 互联研究专门讨论的问题。[R16]

R1 采用一个保守的【本文设计】约束：每个 packet 最多跨 die 一次，并把本地资源分成 PRE 和 POST 两阶段。

```text
PRE NoC -> TX gateway -> D2D -> RX gateway -> POST NoC -> endpoint

Forbidden for the same packet:
POST -> PRE
POST -> another D2D crossing
```

实现上把 R0 的 VC 类别扩展为 `2 VN × 2 phase × 2 VC = 8 VC/input`；PRE/POST 使用独立 buffer/ownership 资源。源端远程包使用 PRE，到远端重新注入为 POST；本地包选定一个不会造成反向依赖的本地阶段。头格式不必新增 phase 位，可以由注入端与 VC 类别产生可信 phase metadata。

每阶段内部保持 XY；网关 TX/RX 存储、请求/响应存储分离；控制 ACK/credit 有独立前进机会。这样可以按资源阶段单向增加来构造无环依赖论证，而不是允许包跨 die 后任意返回旧资源类别。

这仍需把 NI、目标控制器和 SDMA 响应消费依赖纳入系统检查。本文脚本只检查单 die XY 图，没有宣称对 R1 全部 RTL 状态空间完成形式化证明。若要支持多次 die 跳转或更多 gateway，需要重新设计阶段规则，不能机械复用“一次跨越”的结论。

---

# 第七部分：用一笔 SDMA 远端访问把全部模块连起来

## 31. 219 ns 算例：所有假设都摊开

> 本节全部数值为 R0/R1 的教学假设，不是 AMD、Arm、UCIe 或任何量产芯片的测量。

考虑 Die A 的 SDMA 读取 Die B 的 256 B 数据。两个 die 各经过三个 R0 Router hop；D2D 网关两侧均整包接收后再发送；目标服务时间从完整请求接收后开始，到完整 256 B 数据可用于响应为止。

### 31.1 固定项与每包项分开

| 项目 | 假设 |
|---|---:|
| 源 NI 固定处理 | 2 ns |
| 源 die 首 flit 网络延迟 | 3×5=15 ns |
| 两端 gateway 固定处理合计 | 4 ns |
| D2D 固定流水合计 | 8 ns，包含本例 PHY/CDC/校验固定项，不含线上 serialization |
| 目标 die 首 flit 网络延迟 | 15 ns |
| 目标 NI 固定处理 | 2 ns |
| D2D raw bandwidth | 32 GB/s，即 32 B/ns |
| target service | 80 ns |
| 排队、错误、唤醒 | 本例均不发生 |

单向固定项合计：`2+15+4+8+15+2 = 46 ns`。固定 PHY/CDC 项在真实异步系统可能是一个范围；本例只是选定一个预算值。

### 31.2 读请求单向延迟

读请求 NoC packet 是一个 flit；D2D record 24 B，放进一个 LRP cell，线上 80 B。

```text
T_request = 46 + 80/32 = 48.5 ns
```

### 31.3 读数据响应单向延迟

响应 packet 有 17 flits。因为发送 gateway 等整包，源 NoC 需要在首 flit 后再等 16 ns；因为接收 gateway 收完整 record 才注入远端 NoC，远端尾部也需要 16 ns。

D2D record 为 280 B，需要 `ceil(280/64)=5` cells，线上 400 B：

```text
T_response = 46 + 16 + 400/32 + 16 = 90.5 ns
```

于是：

```text
Read RTT = 48.5 + 80 + 90.5 = 219 ns
```

这个算式不把同一段 LT 加两次，也没有给每个 NoC hop 都重复增加整包 serialization。新增的两段 16 ns，来自**明确声明的整包网关边界**。

### 31.4 到底需要多少 outstanding

若目标有效读 payload 带宽为 12 GB/s：

```text
inflight bytes >= 12 B/ns × 219 ns = 2628 B
transactions   >= ceil(2628/256)  = 11
```

11 是无排队假设下的初始容量估算，不是满足所有 workload 的设计保证。ID、NI 返回空间、目标队列、网关 packet credit、replay window、实际负载延迟都可能提出更高要求或先形成瓶颈。

### 31.5 检查目标带宽有没有超过路径上限

R0 对连续 256 B 数据包的单方向 payload 理想上限约 15.06 GB/s。LRP 对这个 record 的理想用户数据效率为 `256/400`，乘 32 GB/s 得 20.48 GB/s，尚未计控制时隙与空闲。

所以本例首先可能受 NoC 口限制，而不是 raw D2D lane 带宽限制。若盲目拿 32 GB/s 当 SDMA 可获得的复制带宽，outstanding 再多也达不到。

## 32. SDMA 设计者需要和互联团队签清楚哪些契约

### 32.1 Read issue 与 response storage

SDMA 发读请求之前，至少要确认事务表和返回数据缓冲有容量。这里的“预留”可以是实际 slot，也可以是经过证明的分层配额，但不能只是期待写通路很快会空出来。

一个有用的内部状态划分是：

```text
free read slot
 -> issued, response reserved
 -> response partially received
 -> data ready for write
 -> write issued
 -> write completion accounted
 -> slot reusable
```

其中哪些阶段共享存储、哪些允许覆盖，需要在 SDMA 微架构中明确。Router 的 credit 只保护下一跳 FIFO，不会自动保护 SDMA 的搬运缓冲。

### 32.2 Burst/packet size

大包减少 header 比例，却更久占用 packet VC、replay 空间和目标缓冲。若 flit-level arbitration，其他 VC 可以在包中间获得输出；若采用 packet lock，长包会增加他人阻塞时间。

因此，不能脱离 packet/flit 级仲裁策略说“大 burst 一定更高效”。实际应扫包大小与并发，观察吞吐、尾延迟、VC 周转和其他业务受影响程度。

### 32.3 多 queue、VM/VF 与身份空间

SDMA queue 数、transaction ID 数、NI 表项数、Router VC 数是四种不同资源。多个 queue 可以共享同一个物理口和 VC 池；一个 queue 可以使用许多 transaction IDs；VC 不代表 VMID。

上游身份在 NI 映射，权限由可信逻辑核验。跨 context 的公平和隔离可能需要专用配额、注入限流与性能计数，而不仅是给 packet 增加一个 context 字段。

### 32.4 Fence、flush 与 completion

至少区分以下时刻：

```text
C0: requester/SDMA accepts command
C1: request leaves SDMA/NI
C2: last request flit leaves local NoC
C3: remote gateway validates and accepts link data
C4: target accepts operation
C5: target-defined ordering/visibility condition met
C6: response/completion delivered to SDMA
C7: completion record / interrupt observed by software
```

link ACK 通常对应某个接收/校验承诺，不等于 C5；FIFO 空也不等于 C6。SDMA fence 等待哪个集合达到哪个点，必须由具体指令与系统内存模型定义。

同样，Router 不会因为运输一个写包就自动执行 GCR、cache flush 或 IOMMU/TLB invalidation。它可能承载相关控制消息，但缓存和翻译维护的语义属于相应模块及协议。本文不推断任何 AMD 特定 packet 的完成点。

### 32.5 Preemption/reset

停止向互联发新请求，不意味着旧 context 已经没有流量。preemption 可以先停止 issue，再选择 drain、保存可恢复事务状态，或按架构允许的方式 abort。必须保留在途响应所需的 ID/context/epoch 映射。

晚到响应不能被误交给复用同一个 ID 的新 context。这个问题跨 NoC、D2D retry 和软件故障恢复，不能只在 SDMA queue arbiter 内解决。

### 32.6 读写复制的流量放大

复制 N 字节至少涉及读取和写入，但它们是否竞争同一个方向的链路，取决于源、目标与路径。若两者穿过同一个共享瓶颈，同一 N 字节可能造成多次经过；若分别使用相反方向的全双工通路，就不能机械把单向带宽除二。

应按每个 cut/port 统计 `read request、read data、write data、write response` 的字节和方向，再计算限制，而不是用一个含糊的“总带宽”数字。

## 33. 软硬件协同：先建立资源，再允许 SDMA 发流量

### 33.1 初始化顺序

【本文参考流程】先确认 reset/clock，建立 PHY 和 link，协商容量与模式，初始化 epoch/credit，再配置地址—目的映射和权限。确认目标 NI、响应缓冲和错误处理可用后，最后开放 SDMA 注入。

```text
clock/reset -> link Active -> resource initialization
            -> route/protection -> error handlers
            -> NI ready -> SDMA queues enabled
```

运行中改路由、禁用端口或减少 buffer quota，不能破坏已经承诺给在途包的资源。可先 quiesce/drain，再切换配置；无停机切换需要更复杂的版本化路由与依赖证明。

### 33.2 操作系统的 DMA 责任

Linux DMA API 文档区分 CPU 地址与设备使用的 DMA 地址，并要求按照映射类型处理同步和生命周期；coherent DMA memory 也不能替代必要的 memory barrier。[R17]

因此，软件向 descriptor 写入地址、发布 valid、敲 doorbell、读取 completion 的顺序，应使用平台和驱动框架规定的 DMA mapping、同步及屏障接口。不能因为 D2D 有 CRC，或 NoC 保序，就省掉 CPU cache/内存排序规则。

### 33.3 建议的可编程寄存器组

下面是本设计建议，不是某厂商的真实寄存器地址：

| 组 | 示例字段 | 注意点 |
|---|---|---|
| 资源能力 | ports、VC 数、深度、最大 packet、ID 容量 | 能力读取不等于运行时可任意改动 |
| 地址与保护 | region base/limit、DstID、domain permission | 配置更新需考虑在途事务 |
| 注入与 QoS | rate、burst tokens、class weight | 配额按 byte/flit/packet 要写清 |
| 运行控制 | inject_enable、quiesce、drain_status | drain 要覆盖相关 NI/link 状态 |
| 错误 | first_error、source、VC、epoch、syndrome | 先保留诊断再恢复 |
| 性能 | byte/flit counts、stall cycles、latency histogram | 明确计数边界和溢出行为 |

### 33.4 不要让性能计数器自己成为误导

一个 port utilization 低，可能是上游没需求、没有输出 VC、没有 credit、SA 匹配不佳、QoS 限速，也可能是目标已经饱和。应同时观察：

```text
offered -> admitted -> routed -> VA granted -> SA committed
        -> transmitted -> acknowledged -> completed
```

如果只有 transmitted bytes，一个“慢”问题无法定位到哪一级停住。

---

# 第八部分：如何验证它真的没有明显的结构漏洞

## 34. 从不变量到定向测试

### 34.1 Router 安全性不变量

```text
0 <= occupancy[i][v] <= D
0 <= credit[o][v] <= D
sum grants per input <= 1
sum grants per output <= 1
one output VC has at most one owner
no pop without valid data
no send without reserved downstream capacity
body/tail cannot start a new idle VC
tail departure latches old routing metadata before local state reuse
```

如果使用 ready/valid 的 NI/bridge 接口，还要检查 `valid && !ready` 时 payload 和相关控制信息保持稳定。不要把这一条不加区分地套到 R0 的纯 credit 驱动前向 valid 接口；两者的接受契约不同。

### 34.2 需要专门构造的边界场景

| 场景 | 预期检查 |
|---|---|
| HEAD_TAIL 单 flit | 同时开始/结束，不漏释放 |
| body 间隔很长 | FIFO 空但 VC 不释放 |
| tail 在 ST，下一包 head 已到同一 input VC | 旧 tail 不读取新 route |
| 同拍 credit return 和 send | counter 只做净更新但两个事件都记账 |
| 所有输入抢同一个输出 | one-hot grant，无覆盖 |
| 一个输入不同 VC 去不同输出 | 不出现多读口能力之外的双重 grant |
| 一个 VN 满、另一个 VN 有响应 | 资源隔离仍允许响应前进 |
| link 进入 QUIESCE | 不收新包，旧响应/ACK 可完成 |
| CRC 错误、ACK 丢失、duplicate | 不重复交付，不重复加 credit |
| epoch 变化后收到旧响应 | 不匹配给新事务 |

### 34.3 Liveness 检查需要环境假设

不能在“目标永远不接收”的环境里要求每个包都完成。应明确：链路最终恢复或报告错误、仲裁最终服务 eligible 请求、目标最终处理已接受事务、控制通道获得有限延迟服务。

在这些假设下，再检查 packet 最终离开、VC 最终释放、事务最终完成或错误收尾。随机仿真没卡住不是一般性死锁证明；形式化安全性通过也不自动意味着所有活性条件成立。

## 35. 本次可执行检查与性能实验建议

仓库附带 `examples/reference_checks.py`，只依赖 Python 标准库。它是本文原创参考算法检查，不是下载某个 simulator 后宣称完成整网验证。

```bash
python3 SWITCH/examples/reference_checks.py
```

本次本地运行通过九个测试组：包头位域无重叠且可往返编码；RR 轮转；10,000 组随机 SA 匹配约束；非最大匹配反例；100 个随机种子、每个 2,000 拍加 drain 的 credit 守恒；credit 与 ownership 分离；4×4 XY 依赖图；NoC/端到端预算算式；CRC32C、重复/缺失/回绕/epoch 检查。

关键输出为：

```text
4x4 XY: 48 channel nodes, 68 dependency edges, acyclic
17-flit, 3-hop unloaded arrival edges: 15,16,...,31
request: 48.5 ns; response: 90.5 ns; total read RTT: 219 ns
12 GB/s × 219 ns / 256 B -> ceil = 11 transactions
9 test groups passed
```

这些测试没有实现完整 4×4 网络逐周期调度，也没有验证 UCIe/CHI 合规、完整 CRC 故障空间、CDC 亚稳态、STA、门级功耗、协议级死锁或所有重放控制状态。因此不使用“已验证可流片”之类表述。

后续性能仿真应至少扫描 packet length、VC count、depth、credit RTT、hotspot、transpose/random 流量、读写比例和 gateway 数，报告吞吐与尾延迟。应把真正的瓶颈逐一替换为理想资源做对照实验，例如无限 credit 仅用于定位，不能把它当可实现设计性能。

---

# 第九部分：修正、证据与继续深化的入口

## 36. 相比上一版，必须明确修正的认识

1. **NoC 不等于 D2D。** 本稿新增网关、链路适配、PHY 和资源终止/重建边界。
2. **Router 不等于一组名词。** R0 明确端口、FIFO、状态、位域、VA/SA、提交事件和 tail 释放。
3. **每 requester 不一定有独立 Router FIFO。** 隔离可以按 NI、物理输入、VC、VN 或 quota 实现。
4. **credit 不等于 VC 空闲。** 前者是槽许可，后者是 packet ownership。
5. **VA 不等于 SA。** 一个预订下一跳 packet 资源，一个分配本拍数据通路。
6. **多个 RR arbiter 不保证最优匹配或端到端硬实时。** 必须检查两级选择和所有服务约束。
7. **更宽、更深、更多 outstanding 不必然更快。** 需要分别分析出口带宽、credit RTT、VC 周转和事务 RTT。
8. **NoC/CHI/UCIe 的 flit 不是一个统一格式。** 标准字段与原创例子严格分开。
9. **Raw D2D 模式不一定由 adapter 提供所需的 CRC/replay。** 先锁定版本和模式。
10. **局部无死锁不自动组合成全局无死锁。** 网关、控制流和端点资源都必须进入依赖分析。
11. **数据离开 SDMA、link ACK、目标接受、可见、软件完成是不同事件。** fence 不能只盯 Router FIFO。
12. **论文/模拟器阶段数不是物理实现证明。** 本稿测试范围与未验证项分别列出。

## 37. 参考资料与阅读定位

下面只列本次实际用于建立或交叉检查论述的一手资料。商业规范全文没有取得的部分，不以营销概述替代规范细则。正文的大量寄存器、格式和算例是明确标注的本文设计，并非逐段翻译某篇论文。

### Router、模型与公开实现

**[R1] Li-Shiuan Peh, William J. Dally, 2001, A Delay Model and Speculative Architecture for Pipelined Routers.**
原始论文；用于经典流水划分、推测 allocation 和物理延迟边界。
https://projects.csail.mit.edu/wiki/pub/LSPgroup/PublicationList/specmodel.pdf

**[R2] Robert Mullins, Andrew West, Simon Moore, ISCA 2004, Low-Latency Virtual-Channel Routers for On-Chip Networks.**
原始论文；特别参考第 2 节与 Router 结构图，区分低延迟电路设计和简单合并抽象阶段。
https://www.cl.cam.ac.uk/~swm11/research/papers/isca2004.pdf

**[R3] Nan Jiang et al., ISPASS 2013, A Detailed and Flexible Cycle-Accurate Network-on-Chip Simulator.**
BookSim2 原始论文；参考第 III—IV 节、Fig.4、状态求值/更新、VC 释放与 allocation 模型。
https://icn.kaist.ac.kr/~jjk12/papers/2013ISPASS.pdf

**[R4] gem5, Garnet 2.0 官方文档。**
用于模型边界、NI/Router/link/credit 结构定位；网页可更新，源码版本另行固定。
https://www.gem5.org/documentation/general_docs/ruby/garnet-2/

**[R5] gem5 源码，tag v24.1.0.1，SwitchAllocator.cc。**
阅读 `arbitrate_inports`、`arbitrate_outports`、`send_allowed`、`vc_allocate`；注意它没有照搬本文独立 VA 阶段。
https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/SwitchAllocator.cc

**[R6] gem5 源码，tag v24.1.0.1，InputUnit.cc 与 OutputUnit.cc。**
用于核对 head 路由、input pop、credit 与 free indication。
https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/InputUnit.cc
https://github.com/gem5/gem5/blob/v24.1.0.1/src/mem/ruby/network/garnet/OutputUnit.cc

**[R7] FlooNoC 原始论文，arXiv:2409.17606v1，2024。**
用于宽物理通路、NI 与 transport 分工的对照；不把论文性能数字代入 R0。
https://arxiv.org/html/2409.17606v1

### 协议与系统接口

**[R8] Arm, AMBA AXI and ACE Protocol Specification, IHI0022H，2020。**
本稿 AXI4 对照固定使用 Issue H；重点定位 A3、A5、A6、A8。没有用后续只描述其他接口的章节替代 AXI4 规则。
https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf

**[R9] Arm, AMBA CHI Protocol Bundle User Guide, DUI0954C，2016。**
参考第 8 节、文档页 15—17 的通道和接口字段。它是模型接口指南，不是最新 CHI architecture specification，不据其中 C++ 参数类型推断线上位宽。
https://documentation-service.arm.com/static/5ed104c1ca06a95ce53f8869

**[R10] UCIe Consortium, Hot Chips 2023 UCIe Tutorial — Protocol。**
核对协议/Adapter/PHY 分层、Raw/68B/256B 模式区别、打印页 37 的 68B Format 2、状态与初始化。PDF 自身页码与幻灯片打印页码不同。
https://hc2023.hotchips.org/assets/program/tutorials/ucie/UCIe%20Protocol.pdf

**[R11] UCIe Consortium, UCIe 1.1 Provides Streaming Protocol Solution for Error Detection and Replay，2023-08-28。**
用于核对 streaming 检错/重放能力的版本变化；不能替代完整规范。
https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay

**[R12] Arm, Learn the architecture — Arm System Architectures, 110303_0100_01_en，2025。**
参考第 4.4 节、Fig.4-2 与 CHI-C2C/CXS/transport 的分层说明。
https://documentation-service.arm.com/static/682ae34f0aae2a5d8f045749

### 正确性、物理层与软件

**[R13] William J. Dally, Charles L. Seitz, Deadlock-Free Message Routing in Multiprocessor Interconnection Networks。**
Caltech 原始技术报告记录，1986；相关正式论文发表于后续期刊。用于确定性通道依赖分析的基础概念，而非任意现代自适应协议的无条件定理。
https://authors.library.caltech.edu/records/fd0yr-br438

**[R14] UCIe Consortium, Hot Chips 2023 UCIe Tutorial — Electrical, Form Factor and Compliance。**
用于封装、时钟及物理层职责定位；本稿不把其中 KPI 当作完整远端内存访问延迟。
https://www.hc2023.hotchips.org/assets/program/tutorials/ucie/Electrical%20Form%20Factor%20and%20Compliance.pdf

**[R15] PULP Platform / ETH Zurich / University of Bologna，FlooNoC 公开 RTL。**
本次实际阅读 `hw/floo_router.sv` 的端口参数、输入 VC FIFO、路由及 credit 生成；读取时 blob SHA 为 `af7e41e51f04fa2e53b6cddebb20a24a56b1df9c`。main 链接可能变化，且后续 RTL 具有论文版本之外的扩展，不把两者视为同一冻结版本。
https://github.com/pulp-platform/FlooNoC/blob/main/hw/floo_router.sv

**[R16] A Simple Deadlock Avoidance Scheme for Modular System-on-Chip, arXiv:1910.04882v1，2019。**
参考引言与第 2 节的跨 chiplet 依赖问题；本文 PRE/POST 参考扩展不是该论文算法的逐项复刻。
https://arxiv.org/pdf/1910.04882

**[R17] Linux Kernel Documentation, Dynamic DMA mapping Guide。**
参考 CPU/DMA address、coherent mapping 的 barrier 和 streaming mapping 生命周期部分。平台驱动仍应使用其目标内核版本的 API 规则。
https://docs.kernel.org/core-api/dma-api-howto.html

### 继续完善的精确入口

下一轮若需要深入，不应再次泛泛补“更多知识”，而应针对仍未闭合的工程项：完整 Router RTL 与随机/形式化验证；所选 CHI/UCIe 版本的正式合规规则；真实 memory-controller completion contract；异步 FIFO 与 reset crossing；带目标流量的多 die 依赖证明；综合、STA、功耗和实际延迟测量。

本稿已经把结构、资源、包格式、正常周期行为、故障边界和算例放进同一个参考体系；这些工程项则决定它能否从可讨论的微架构文档进入具体产品实现。
