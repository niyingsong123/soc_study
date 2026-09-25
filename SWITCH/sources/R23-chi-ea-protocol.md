# R23：CHI E.a 原始规范：事务资源、顺序、重试与链路 credit

更新日期：2026-09-25。

导读：从 CHI 正式规范解释 RN/HN/SN、四类通道、TxnID/DBID 生命周期、完成与可见性、P-Credit/L-Credit 以及链路低功耗收敛；适合 SWITCH/DF/GC 的行业协议对照，不是 AMD fabric 实现说明。
来源：[Arm 官方 AMBA 5 CHI Architecture Specification，IHI 0050E.a](https://documentation-service.arm.com/static/6087f99b5e70d934bc69f1f0)，ID081920，2020。固定 E.a，不以本笔记代替更新版本或 CHI-C2C 规范。
阅读状态：取得完整 PDF，选读 §1.1–1.3、§2.1、§2.3 读写/retry 主干、§2.4–2.5、§2.8、§2.11、§4.1、§14.1–14.2/14.5。未将所有 coherence transition、atomic、DVM、MPAM 或 memory tagging 表标为精读。R9 仍是模型指南，R12 仍是架构介绍，两者不再承担正式协议来源的角色。

## 三层与节点责任

Protocol 层决定请求/响应、一致性状态变化和协议级流控；Network 层添加路由所需的源/目标标识；Link 层负责相邻节点 flit 传送和容量流控。拓扑可以是 crossbar、ring、mesh 等，CHI 本身并不规定一种 router 微架构。不能根据符合 CHI 推出固定 VC 数、路由算法或 snoop-filter 容量。

RN 发起访问，HN 承担 home 侧处理；典型 HN-F 是一致性点 PoC。SN 是后端响应节点，可能连接内存控制器。PoS 表示请求串行化/排序位置，PoC 表示观察一致数据的位置，PoP 才涉及掉电后保持；三者不能因“完成”一词合并。这里是行业职责参照，不将 AMD DF 某块直接更名 HN。

## 通道要按方向和功能分开

| 类别 | RN 侧典型方向 | 代表消息/资源 |
| --- | --- | --- |
| REQ | TXREQ | 读写、维护、重试后的请求 |
| SNP | RXSNP | 互联发给 coherent RN 的 snoop |
| RSP | TXRSP 与 RXRSP | Snoop response、CompAck，或 Comp/DBIDResp/RetryAck/PCrdGrant |
| DAT | TXDAT 与 RXDAT | 写数据、snoop/forward data、读返回 |

WDAT/RDAT、SRSP/CRSP 是事务描述中的方向性称呼，不是另外发明四种协议类别。snoop response 不一定带数据，数据可能经 DAT 单独发送。REQ 有空位不代表 DAT 或 RSP 能接收；研究死锁时必须建完整通道依赖，不能只给请求画 credit 环。

## 两个基本事务闭环

**读：** RN-F 的 ReadShared 等 coherent 读到 ICN 后，数据可由 home 路径返回，也可使用 direct memory transfer：ICN 发 ReadNoSnp 给 SN，SN 的 CompData 直接回原 RN。设置 ExpCompAck 时 RN 再回 CompAck；§2.3 的 DMT 流程允许收到至少一个 CompData packet 后发送 CompAck，不能把它统一写成“所有数据 beat 已到才允许 ACK”。具体合并/分离 Comp、Data 的规则按事务类型区分。

**非 CopyBack 写：** WriteNoSnp 不要求 snoop，WriteUnique 可能需要先取得写权限。Completer 用 DBIDResp/DBIDRespOrd 告知可收数据，用 Comp 表达规定的观察语义，也可用 CompDBIDResp 合并两者。RN 获得 DBID 后送 NonCopyBackWrData，带 byte enables；需要 CompAck 的有序写还完成相应确认，可按允许形式与数据合并。不能把拿到数据缓冲 ID 当作所有写数据已落 DRAM，也不能将 WriteBack 与这一流程混为一类。

## TxnID 与 DBID：两侧独立的资源生命周期

SrcID/TgtID 用于节点路由；TxnID 在给定 Requester 下关联在途事务。E.a 定义 12-bit TxnID 字段，但每 Requester outstanding 上限为 **1024**，不能按字段宽度直接推为 4096 项。接到该事务全部所需响应，或接到 RetryAck 后，可按规则重用 TxnID；重发不要求沿用旧 TxnID。

DBID 由 Completer 提供，后续写数据或 CompAck 把它作为 TxnID 使用，使响应端能定位自己的保留状态。DBID 的唯一性以相应 requester/事务类别为条件；不同 requester 可以复用数值，但 Completer 此时必须将 SrcID 纳入关联键。必须收到允许释放旧事务的全部 packets 后才能复用相应 DBID。

DMT 等路径还用 ReturnNID/ReturnTxnID 指定真正收数者，CompData 中的 HomeNID 告诉 RN 把 CompAck 发给谁。由此可见“数据从谁来”与“事务在哪个 home 收敛”可以不同；NI 不能仅用最后一跳源节点猜响应归属。

## 完成、排序收据与一致性不是一个事件

§2.8 将 Request Order 与 Endpoint Order 区分：前者关心同源同地址，后者扩展到同一 endpoint address range（范围大小由实现定义）。对所列需排序的读，ReadReceipt 表示到达能保持相应顺序的位置；符合条件时 RespSepData 可承担此作用。对写，DBIDResp/DBIDRespOrd 还承担相关排序位置的承诺。它们允许决定下一笔何时发出，不等于读数据已经交付或写已持久化。

Comp/CompData 的观察保证依 Cacheable、Non-cacheable、Device 类型及事务类型而异，不能脱离属性写成全局 fence。对于相关 coherent 事务，HN-F 等待 CompAck 后才发同地址后续 snoop，防止 snoop 越过之前的事务完成；ReadOnce* 等具有例外，ReadNoSnp/ReadOnce* 的 CompAck 也不是无条件必须。HN→SN 的请求者不得再套用 RN→HN 的 CompAck 流程。

§4.1 的状态也必须保留语义：UC/UD 分别是 Unique Clean/Dirty，UCE 是持唯一所有权但无有效数据，UDP 为唯一但仅部分字节 dirty，需要合并形成完整 line；SC/SD 都可能有其他共享副本。特别是 **SC 并不保证与主存相同**：它可持有已修改数据的共享副本，只是不承担写回责任；SD 则承担 dirty 写回。不能把“clean”机械等同于“DRAM 已最新”。本笔记不替代逐 opcode 的状态转移表。

## Request Retry：P-Credit 预留端点处理资源

除 PrefetchTgt 例外，首次请求设置 AllowRetry=1。Completer 无法接纳时回 RetryAck，并记录请求来源及所需 PCrdType；有资源后发 PCrdGrant。Requester 必须保存原请求，等待 RetryAck 和合适的 grant **两者都收到**后才重发，重发 AllowRetry=0，保证被接纳。

RetryAck 与 PCrdGrant 允许乱序到达；先收到 grant 必须保留，不能丢弃或立即无条件重发。P-Credit 不是固定绑定一笔请求的 tag：同一 Completer 与适合的 PCrdType 下，可分配给符合条件的待重试请求。支持最多 16 类 credit。原 TxnID 可在 RetryAck 后复用，但还欠着的 credit/重试责任并未消失；因此 TxnID 表项与 retry bookkeeping 不能当成同一个计数。

取消不再需要的重试时，用 PCrdReturn 及时退还 credit，不能无限囤积。Completer 还必须防饥饿，确保不同 QoS/credit 类型的待重试事务最终得到进展。首次请求尚未 RetryAck 就重复发送，必须能接受两笔都实际执行，不能对有副作用的 MMIO 随便使用这种办法。

## Link credit 与低功耗收敛

§14.2 的 L-Credit 仅担保**相邻接收端一个 flit**的容量；每 channel 独立 LCRDV，每发送一个 flit 消耗一份 credit。该版接收端可提供 1–15 个 L-Credits，发出的 credit 必须有真实可接收能力；新收到的 credit **不能同拍使用**。不能把这 15 个槽等同于整个 coherent 事务的 outstanding，或把 P-Credit 当链路 buffer 空位。

| LINKACTIVEREQ/ACK | 状态 | 关键责任 |
| --- | --- | --- |
| 0/0 | STOP | credits 在接收端，发送端不得发 flit |
| 1/0 | ACTIVATE | 发送端准备收 credit，但进入 RUN 前不能使用；接收端需先进入 RUN 才发 credit |
| 1/1 | RUN | 正常交换 flit/credit |
| 0/1 | DEACTIVATE | 停止正常发送并收回 credits，接收端收齐后才撤 ACK |

DEACTIVATE 存在末尾 flit/credit 与状态变化的竞争，详细表允许接收这些在途项；不能用一句“REQ 拉低即清空队列”实现。复位要求 FLITV、LCRDV 与相应激活信号撤销，退出复位按时钟沿初始化。完整双向交互还有 §14.6，本笔记未代替其所有竞态表，也不据此定义目标系统的 reset tree。

## 与本项目研究的连接

SWITCH 第 3 轮按需借 TxnID/DBID、两类 credit 比较 transaction table、端点资源和 link buffer 的责任；第 4 轮在相关协议对照中分析 retry、CompAck、snoop 和 link state 所增加的等待与恢复条件；第 5 轮沿已定义的接口研究跨 die control 进展。第 6 轮只评价实际模型包含的流量与机制。这些 CHI 交互不自动加入 R0，也不要求本轮完整实现 CHI。[R13](R13-channel-dependency-scope.md) 的确定性路由定理不能单独证明这些协议依赖无环。DF/GC 使用本篇比较一致性责任和完成边界，仍需 AMD 原文确认具体实现。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
