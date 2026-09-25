# 芯片互联 Switch / NoC：详细学习笔记

> 本文把 Switch 泛指 SoC/GPU/chiplet 中的交换与路由 fabric，包括 crossbar、packetized NoC router，以及 NIU、buffer、QoS、CDC、协议桥等。重点是可迁移的架构原理，并以 SDMA 为主要例子。

## 1. 为什么需要 Switch

单一 SDMA 到单一 Memory Controller 可以点对点连接，但真实 SoC 同时有 CPU、GPU、SDMA、NPU、Display、PCIe 等 initiator，以及 L2/LLC、DDR/HBM、MMIO、PCIe 等 target。全部点对点会使连接数、长距离宽总线、布线和 timing 快速恶化；共享单总线又会限制并行度。因此需要互联层：

```
CPU ----\
GPU -----\
SDMA -----+-- [ Switch / Interconnect / NoC ] -- L2/LLC
NPU -----/              |                      DDR/HBM
PCIe ---/               +--------------------- MMIO/PCIe
```

现代 NoC 常由 NIU 把 AXI/CHI/私有协议事务 packetize 成 packet/flit，经 router/link 传输，再在目的端还原。这样能降低全局宽线压力、pipeline 长链路，并让 topology 更适合 floorplan。

## 2. Switch 的核心职责

Switch 不是简单 mux，而是“受协议约束的交通系统”：

1. Connectivity：N 个 initiator 到 M 个 target。
2. Decode/Routing：按 address、region、destination ID 选择目标和路径。
3. Arbitration：多个输入争用同一资源时决定先后。
4. Buffer/Flow Control：吸收速率差，以 READY、credit、retry 等传播拥塞。
5. Protocol preservation：保持 ordering、ID、response、burst、atomic/barrier 等语义。
6. QoS：分配 latency、bandwidth、priority。
7. Adaptation：常包含 width conversion、CDC、power-domain、protocol bridge。
8. Protection/RAS：地址权限、错误响应、timeout、parity/ECC 等（依实现）。

所以 Switch 同时影响 correctness、performance 和 physical design。

## 3. 一笔 SDMA 事务怎样经过 Switch

```
SDMA
 | addr/len/ID/QoS/attribute
 v
Ingress / NIU
 |-- protocol check / packetization
 |-- address decode
 v
Router / Switch
 |-- input queue
 |-- route selection
 |-- arbitration
 |-- credit/backpressure
 v
Memory-side NIU -> Memory Controller -> DRAM/HBM
```

Response 再沿 fabric 回到 SDMA。多个 initiator、多个 outstanding 并存时，transaction/source/route ID 用于把 response 返回正确 requester。

当 CPU 与 SDMA 同时访问 DDR 时会竞争出口。常见 arbitration 有 fixed priority、round-robin、weighted RR、age-based、QoS-aware 或混合算法。协议通常不规定唯一算法，但仲裁不能违反 ordering 等协议规则。

DDR 忙时 Switch buffer 会逐渐填满，压力最终向 SDMA 传播。AXI 风格常用 VALID/READY，packet NoC 常用 credit。SDMA 必须能在任意合法 stall 下停止发送而不丢事务、不覆盖状态、不破坏顺序。

## 4. Outstanding：与 SDMA 性能最重要的交点之一

如果 SDMA 每发一个 request 都等 response 再发下一个，高延迟 memory 会让链路大量空闲。因此需要多个 in-flight transaction。

一个有用估算：

```
required_inflight_bytes ≈ target_bandwidth × round_trip_latency
```

例如目标 64 GB/s、有效往返 200 ns，仅 bandwidth-delay product 就约 12.8 KB；若每事务 256B，是约 50 个事务的数量级。真实值还受 burst、DRAM efficiency、ID、buffer、credit 限制。

因此 SDMA outstanding 从 32 增到 128 不一定更快。必须一起检查 Switch ingress/egress buffer、per-source/per-ID 限制、memory-controller queue、response buffer、ordering restriction 和 target acceptance rate。

## 5. Ordering 与 ID

要区分 issue order、target execution/arrival order、completion/response order。多路径、不同 queue 和不同 target latency 都可能产生 reordering，互联只能在协议允许范围内重排。

SDMA 特别要检查：
- descriptor fetch 与 data access 的依赖；
- 多 block copy 是否可 pipeline；
- fence 前后的 completion 定义；
- doorbell/MMIO 与 memory write 的可见性；
- 同地址/重叠地址访问；
- VMID/PASID/context 隔离；
- response ID 数是否支持目标并发。

## 6. Routing、Crossbar 与 Packet NoC

简单系统按 address decode 路由；复杂 NoC 可能经过多个 hop：

```
SDMA -> R0 -> R1 -> R4 -> Memory
              \
               -> R2 -> PCIe
```

需要考虑 topology（crossbar/ring/mesh/tree/custom）、static/adaptive route、path latency、deadlock avoidance、virtual channel/network。

Crossbar 在小规模系统中低延迟且直观，但规模增大后 mux、wire、area、timing 成本上升。Packet NoC 可通过 router/link、serialization 和 pipeline 扩展到更多 IP，也更容易适应 clock/power domain 和 floorplan，但 buffer、credit、VC、deadlock 和 QoS verification 更复杂。

## 7. Buffer、Flow Control 与 HOL

Ready/Valid 的接受条件是 VALID && READY。Credit-based flow control 则由 receiver 告诉 sender 剩余 buffer slot，更适合长 pipeline。

Buffer 太小会频繁 backpressure；太大增加 area、power 和 queueing latency。因此 buffer depth 是架构参数，不只是 RTL 细节。

单 FIFO 还可能有 Head-of-Line blocking：

```
[A -> busy DDR] [B -> free PCIe]
```

A 堵在队头使 B 也无法前进。常用多 queue、virtual channel 或 virtual network 解决。VC/VN 还可用于 traffic isolation 和 deadlock avoidance。

## 8. QoS 与 Deadlock

CPU cache miss 通常 latency-sensitive；display 有实时 deadline；SDMA bulk copy 多为 bandwidth-sensitive；后台流量可 best-effort。因此平均公平不等于系统正确。

QoS 可包含 priority、weighted arbitration、bandwidth reservation、rate limiting、traffic shaping、latency target 和 congestion propagation。AXI 提供 QoS signaling，但 system policy 由实现决定，而且 ordering 约束优先。

多级 NoC 的资源依赖还可能形成环路 deadlock。常见手段包括 deadlock-free routing、VC/VN 隔离、request/response dependency 分离、资源顺序和 escape path。

## 9. Width、频率与真实带宽

理论单方向 raw bandwidth 可粗略写成：

```
BW = link_bytes_per_cycle × frequency × transfers_per_cycle
```

256-bit link 是 32B/cycle，1GHz 理论 raw BW 为 32GB/s。但有效带宽还受 header、arbitration bubble、credit stall、target stall、read/write turnaround、burst efficiency、serialization 和共享比例影响。

NoC 可在不同区域使用不同 link width，以 serialization 在 wire count、area、latency 和 bandwidth 间折中。

## 10. Clock/Power/Error

大型 SoC 中 SDMA、NoC、Memory Controller 常不同频，fabric 可能包含 async FIFO/CDC、frequency conversion、power isolation 和 power handshake。SDMA reset/power-down 时必须考虑 outstanding 是否 drain、fabric 是否仍接收请求、response 是否可能晚到。

常见错误包括 unmapped address、permission violation、decode error、target timeout、poison/corruption、link/protocol error。Switch 不能简单丢事务；SDMA也必须正确回收 outstanding，把错误关联到 queue/context/descriptor，并按架构 stop/skip/retry、更新 status、报告软件。

## 11. 最关键设计参数

- Connectivity：port 数、topology、address map、coherent/non-coherent。
- Datapath：link/flit width、frequency、serialization ratio、pipeline、max burst/packet。
- Concurrency：outstanding capacity、ID/source-ID width、buffer depth、queue/VC/VN 数。
- Performance：peak/effective BW、unloaded/loaded latency、arbitration、QoS、oversubscription。
- Correctness：ordering、atomic/barrier、coherency attribute、error、deadlock freedom、security。
- Physical：floorplan、long-link pipeline、CDC、power domain、area/power。

## 12. SDMA 设计必须考虑什么

**End-to-end bandwidth**：SDMA datapath 128B/cycle，而实际可分到的 fabric 只有 64B/cycle，继续扩 datapath 不会提高系统吞吐。

**Burst**：大 burst 可减少控制开销、提高 memory efficiency，但可能增加别人等待时间、影响 QoS，并可能因 boundary/target limit 被 split。

**Outstanding**：先用 bandwidth-delay product 估算，再受 Switch credit/buffer、ID 和 MC queue 约束。

**Backpressure**：验证任意合法 stall 下 request/payload 稳定、FIFO 不 overflow、counter 正确，并避免 read-response 与 write-issue pipeline 相互锁死。

**Fence/Visibility**：“请求离开 SDMA”不等于“数据全局可见”。Fence、descriptor completion、interrupt、doorbell 必须和 Switch/cache/MC 的 completion/visibility point 对齐。

**QoS**：定义 SDMA traffic class、priority/weight/rate limit，必要时区分 descriptor/control traffic 与 bulk data traffic。

**Address/VM/Security**：SDMA 的 address、VMID/PASID、cacheability/coherency/security attribute 必须能被 fabric 正确 route 和保护。

## 13. 软件/硬件协同

若 Switch 可编程，firmware/driver 常配置 address window/route、QoS priority/weight/rate limit、security/firewall、power/clock、performance counter、error/timeout/interrupt。

合理分工是：硬件保证 protocol correctness、flow control 和基本 deadlock safety；firmware 在 boot 建立 topology/address/security；OS/driver 根据 workload 设置 QoS，并读取 congestion/BW/latency counter 调优。SDMA driver 可根据 fabric 能力选择 queue priority、burst/outstanding policy。

## 14. 性能问题的排查顺序

```
SDMA issue rate
 -> ingress stall?
 -> route/arbitration wait?
 -> credit/buffer full?
 -> QoS throttling?
 -> link utilization/serialization?
 -> MC queue?
 -> DRAM/HBM efficiency?
 -> response-path congestion?
```

不要只看平均 bandwidth，也要看 latency distribution、stall reason 和各级 queue occupancy。

## 15. 最终心智模型

Switch/NoC 的本质是：

**把很多 requester 的 transaction，在有限的 wire、buffer、port 和 target bandwidth 上，按照 routing + arbitration + flow control + ordering + QoS 的规则安全而高效地送到目的地，并把 response 正确送回来。**

对 SDMA 而言，Switch 是端到端性能模型的一部分。SDMA 的 burst、outstanding、ID、fence、QoS、buffer 和 error handling 都必须与 fabric contract 协同设计。

## 高质量参考资料

- Arm AMBA AXI Protocol Specification：multiple outstanding、ordering、QoS、channel semantics。
- Arm AMBA CHI Architecture Specification：packet/flit、credit、retry、coherent interconnect。
- Arm CoreLink NI-700 / NI-710AE：packetized NoC、QoS、clock/power-domain。
- Arm CoreLink NIC：可配置 AMBA interconnect。
- Arteris NoC Technology、Packetization & Serialization、End-to-End QoS：NIU、packetization、serialization、QoS、congestion。
- AMD EPYC Architecture White Paper：Infinity Fabric、多 die 与 I/O die 互联实例。

> 具体芯片的 buffer 数、routing、QoS 算法、ID 宽度和 completion semantics 必须以该芯片/IP 的 architecture/specification 为准。
