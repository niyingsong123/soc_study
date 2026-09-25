# Switch / NoC 快速理解版

这篇是详细版的快速复习材料，重点回答六个问题。

## 1）为什么需要这个模块？没有会怎样？

真实 SoC 有 CPU、GPU、SDMA、NPU、Display、PCIe 等多个请求方，也有 L2/LLC、DDR/HBM、MMIO、PCIe 等多个目标。

```
CPU ----\
GPU -----\
SDMA -----+-- [ Switch / NoC ] -- L2/Memory
NPU -----/          |            PCIe/MMIO
```

没有 Switch，如果全部点对点连接，wire、mux、area、timing 和系统集成复杂度会快速增加；如果共享单总线，又会形成带宽和并行度瓶颈。

现代 NoC 还通过 packetization、serialization、分布式 routing 和 pipeline 缓解长距离宽总线的物理实现问题。

**一句话：Switch 让很多 master 能共享很多 target，同时保持系统可扩展。**

## 2）主要功能是什么？解决什么问题？

核心任务是：

**把多个 initiator 的 transaction 正确、高效地送到目标，并把 response 正确送回来。**

主要功能：

- Address decode / destination selection：决定请求去哪里。
- Routing：决定走哪条路径。
- Arbitration：多个请求争用同一出口时决定谁先走。
- Buffer：吸收瞬时速率差。
- Flow control / backpressure / credit：下游忙时安全地让上游减速。
- ID/source tracking：让 response 回到正确 requester/transaction。
- Ordering：保证协议要求的顺序。
- QoS：在 CPU、Display、SDMA 等流量间分配延迟和带宽。
- Error propagation：传递 decode、permission、timeout 等错误。
- 常见附加功能：width conversion、CDC、power-domain bridge、protocol bridge、security。

本质上解决：

**有限的 wire、buffer、port 和 target bandwidth，如何被大量模块安全、高效、可预测地共享。**

## 3）上下游模块、数据和控制流向

典型路径：

```
             Request / Write Data
SDMA/CPU/GPU ----------------------> Switch/NoC ----------------> L2/MC/PCIe
     ^                                  |                            |
     |                                  |                            |
     +------------- Response / Read Data <---------------------------+
```

### 上游
通常是 initiator/requester：
- CPU
- GPU
- SDMA/DMA
- NPU
- Display/Video
- PCIe 等

### 下游
通常是 target/home/memory side：
- L2/LLC
- Memory Controller
- DDR/HBM
- PCIe bridge
- MMIO peripheral

### 控制信息

transaction 通常携带 address、length/burst、ID、QoS、cache/coherency/security attribute、VM/context 等信息。NoC 内部可能把这些编码进 packet/flit header。

另一个非常重要的反向控制流是 **backpressure**：

```
SDMA -> Switch -> Memory Controller
  ^                   |
  +---- backpressure--+
```

下游拥塞会通过 READY、credit 或 retry 等机制逐级影响 SDMA。

## 4）最关键的设计参数和功能

| 类别 | 最重要的参数/功能 |
|---|---|
| 带宽 | link/data width、frequency、serialization、实际可用 BW |
| 延迟 | router hop、pipeline stage、queueing latency |
| 并发 | outstanding 数、ID/source-ID 数、buffer/credit |
| 拓扑 | crossbar/ring/mesh/tree/custom、port 数 |
| 仲裁 | round-robin、priority、weighted、age/QoS aware |
| QoS | priority、weight、bandwidth reservation、rate limit |
| 流控 | ready/valid、credit、retry |
| 正确性 | ordering、atomic/barrier、error、deadlock freedom |
| 系统 | address map、coherency、security、CDC、power domain |

### 三个特别重要的性能概念

**① Bandwidth**

粗略峰值：

```
BW = link_bytes_per_cycle × frequency
```

但真实带宽还会被 arbitration、header、credit stall、target stall、serialization 等降低。

**② Outstanding**

为了隐藏 memory latency，需要多个事务同时在 flight 中。一个有用估算：

```
required_inflight_bytes ≈ target_bandwidth × round_trip_latency
```

**③ Buffer / Credit**

Buffer 太少容易频繁 backpressure；太多增加 area、power 和排队延迟。它必须和 outstanding、link latency、target acceptance capability 一起设计。

## 5）Switch 与 SDMA 有什么关联？

**关联很强。**

SDMA 是典型高带宽 initiator：

```
SDMA -> Switch/NoC -> L2/LLC/Memory Controller -> DRAM/HBM
```

设计 SDMA 时至少要考虑：

### Burst size
较大 burst 通常效率更高，但可能长期占用共享资源、影响其他 master QoS，并可能因 boundary/target limit 被 split。

### Outstanding depth
SDMA 能支持 128 outstanding，不代表系统就能利用 128。Switch 可能只有较少 credit/buffer，Memory Controller queue 也有限。

### Backpressure
Switch 堵塞时 SDMA 必须安全停止。要保证 request/payload 不丢、FIFO 不 overflow、状态不被覆盖。

### Ordering
SDMA 的 descriptor、data、completion、doorbell、interrupt、fence 之间可能存在顺序依赖。Switch 允许的 reordering 必须与 SDMA 语义一致。

### Fence / Visibility
这是非常关键的一点：

**“transaction 已经离开 SDMA”不等于“write 已经全局可见”。**

Fence/interrupt/completion 的定义必须明确它需要等到 Switch、cache、Memory Controller 路径中的哪个 completion/visibility point。

### QoS
SDMA bulk copy 可以持续吃满带宽，因此需要考虑 priority、weight、rate limit，避免影响 CPU/Display 等 latency-sensitive traffic。

### Address / VM / Security
SDMA 发出的 address、VMID/PASID、cache/coherency/security attribute 必须被 fabric 正确解释、route 和保护。

### 性能分析
不能只看 SDMA 内部 datapath。必须分析：

```
SDMA issue
 -> Switch ingress
 -> arbitration
 -> link/credit
 -> cache/MC
 -> DRAM/HBM
 -> response path
```

如果 SDMA 内部 128B/cycle，但 fabric 实际只分给它 64B/cycle，那么继续扩大 SDMA datapath 没有意义。

## 6）如果需要软硬件协同，怎么做？

如果 Switch/NoC 是可配置的，firmware/driver 可能需要配置：

- address window / route；
- QoS priority / weight；
- bandwidth limit；
- security/firewall；
- clock/power state；
- timeout/error interrupt；
- performance counter。

推荐分工：

**硬件**负责 protocol correctness、routing、flow control、ordering、基本 deadlock safety。

**Firmware** 在 boot 阶段建立 address map、route、安全和基础 QoS。

**OS/Driver** 根据 workload 动态设置 priority/rate，并读取 bandwidth、latency、stall、queue occupancy 等 counter 调优。

**SDMA driver/firmware** 可以根据 fabric 能力选择 queue priority、burst 和 outstanding policy，而不是所有 workload 固定一个值。

---

## 最后记住一句话

**Switch/NoC = Routing + Arbitration + Buffer/Flow Control + Ordering + QoS。**

对 SDMA 来说最重要的是：

**Bandwidth、Outstanding、Backpressure、Ordering/Fence、QoS。**

如果以后分析 SDMA 性能问题，优先沿下面路径查：

```
SDMA issue rate
 -> Switch ingress stall
 -> arbitration wait
 -> credit/buffer full
 -> QoS throttle
 -> link utilization
 -> Memory Controller queue
 -> DRAM/HBM efficiency
 -> response-path congestion
```

详细原理见同目录的 `switch_detailed_guide.md`。
