# C05：MMHUB：翻译、TAP/DAGB、EA 队列与 DF 边界

> 2026-09-25：所引用页图已按用户要求移出仓库；下文保留此前阅读记录，无法通过 GitHub 复核原图。

更新日期：2026-09-24。

导读：连接客户端 AXI、按需翻译、TAP/DAGB 预约、EA 分组排队和 SDP 返回，是 HUBS/EA 整体微架构的重要参考；保留共享存储、独立 credit、失效路径及与 C01 的差异。
来源：原图已移出仓库。用户提供的 HYGON 标识资料，未确认等同于研究目标芯片的某一 AMD 实现版本。
阅读状态：读取 41 页可提取文字，直接核看第 7、18、27、32、33、34、40 页关键图表；图中缺乏的 RTL 时序、RAM 端口数和严格完成定义保持未知。

## 页码与子模块索引

| 页码 | 内容 | 可复用模块 |
|---|---|---|
| 3–7 | 客户端、总体位置、翻译类型及条件分支 | HUBS、UTCL1/2、SDMA |
| 9–19 | aperture、VML2/walker、ATC、失效、xGMI 转换 | UTCL2、DF、PCIE |
| 21–23 | TAP/NIU 与 AXI→DAGB 信息映射 | HUBS、NBIF |
| 25–28 | Ask/Go/Send、scoreboard 与 credit | HUBS、EA、SWITCH 对照 |
| 31–35 | EA 内部路径、共享存储、list manager、调度 | EA、UMC、DF |
| 37–40 | sideband、两种 MMHUB 路径、失效 | UTCL1/2、RSMU、SDMA |

## 整体职责与分支路径

MMHUB 为 SDMA、MP、HDP、IH/semaphore、DBGU 等客户端提供接入、必要翻译和面向 DF 的服务。数据路径包含 AXI 接入、TAP/NIU、DAGB、EA、SDP；翻译可以走 UTCL1/UTCL2 sideband，也可以在路径内由 VML1 请求。图中实例、客户端数量和命名只适用于该资料。

第 7 页区分五件事：物理地址直通；aperture 地址空间转换；GPUVM PDE/PTE 翻译；必要时继续 ATC；面向 VF/远端 framebuffer 的 xGMI 转换。aperture 主要用于 VMID0 等场景并不意味着所有 VMID0 请求都无保护；GPUVM 到系统内存的进一步翻译也受表项、模式和配置控制。把五项全部画成串行必经阶段，会错判延迟和资源依赖。

页表路径的 PTE cache、PDE cache、ATC work queue 各有自己的状态；第 11–17 页提供结构线索。写作时先画返回来源与故障分支，再讨论容量、替换、预取，避免把子 feature 从所属数据路径中抽离。

## TAP/NIU：物理分布影响协议组织

第 21–23 页中，客户端 AXI 经 ANIU 接入分布式 Ask-Go Bus，NIU 由 TAP 串接。客户端 NIU 可随客户端电源门控，而 TAP 保持工作；MMHUB 靠近 DF SDP，客户端分布在不同位置。因此 TAP 不只是抽象“一个 FIFO”，还承担跨距离传递与持续连通性要求。

AXI 的地址、数据、读/写响应及 USER 属性映射到内部事务；space、VMID/VFID、只读/一致性/安全属性与 client/tag 都应跟随请求。地址已翻译并不允许丢弃权限或排序属性。文中字段宽度和编码不能迁移到其他版本；有疑问时回看第 23 页而非依赖 OCR。

## DAGB：请求有效不等于具备发射资格

第 26–28 页的 Ask、Go、Send 把预约和实际发送分开。地址一侧进入 TLB 请求及地址存储，翻译返回更新相关信息；数据一侧有 link/data FIFO。地址与数据的 Go/准备状态进入 scoreboard，满足条件后才形成送往 EA 的请求。因而地址早到、数据晚到、翻译 miss、下游无空间都是不同停顿原因。

第 28 页将 store FIFO/pool、EA VC/pool/IO、return FIFO、TLB/data/misc 等 credit 分开，还有限制 outstanding 和带宽的控制。每个 credit 都应明确代表什么物理资源、何时减、哪个事件归还。不能把“EA 接收命令”当成所有 credit 同时释放，也不能只用一个总 free count 表示整个路径。

后续应检查预约后未发送、失效/复位中途取消、地址与数据不匹配、返回拥塞时资源是否最终归还。这些是由结构推导的检查需求，资料没有给出全部处理状态，不能写成已实现功能。

## EA：共享存储上的逻辑队列与多级选择

第 32 页把 read/write 各自分为 DRAM、GMI、IO 类目的地，选择后送 SDP request；写数据有独立 SDP data 路径，读响应和写响应也不同。link manager 与时钟/电源控制在旁边，不应混作调度算法。完成分析必须分“命令选出”“数据发出”“响应返回”“上游可见”几个时点。

第 33–34 页的内部结构比简单端口 RR 更丰富：地址先得到 page/bank 信息；命令/数据进入共享存储；list manager 按 bank×group 管理链，维护 size、next、handle 等元数据，并与 refill/pop/push 协作。DRAM 与 IO list manager 的操作集合不同。逻辑上分组排队不代表每队列一块物理独立 RAM；后续容量推导须把共享池与每组元数据分开。

调度还涉及 group priority、urgency、LRU/组选择、bank 状态及顺序限制。选中后读取 command storage 并释放相应资源。图未说明 RAM 的具体端口冲突、每周期 issue 数和全部仲裁优先级，不能从箭头数推吞吐。

第 35 页的配置包括 client→group→VC 映射、年龄/队长/固定/urgency 等优先因素、带宽量化控制、地址归一化 base/limit/offset、bank hash/harvest。研究应把策略连接到资源：公平性保护哪个 group，urgency 来自何处，row locality 与 starvation 如何取舍，harvest 后地址与队列映射怎样保持一致。[EA1](../../EA/sources/EA1-rr-arbiter.md) 的 RR 代码只是通用仲裁对照，不足以代表该 EA 总体。

## 失效与控制路径的范围

第 18 页列出 VM 与 ATHUB 两类失效，按 PF/VF/VMID/范围作用，并有共享失效 engine 的 semaphore 和 ACK 寄存器。其 VM 01/10 对 UTCL1 子类型的标注与 [C01](../../UTCL2/sources/C01-mm-utcl2-testbench.md) 第 31 页不一致；本笔记不选择性抹掉冲突，应由目标文档/RTL确认。PTE/PDE 列中的 “no ack” 不能泛化为整个操作不需要确认。

第 40 页把 PCIe/ATHUB 到 UTCL2、再到 VML1 与客户端 UTCL1 的分发画出来，同时显示 remote SMU 与寄存器接口。该标签是研究 [MG5](../../RSMU/sources/MG5-rsmu-umc-index.md) 等 RSMU 证据的线索，仍不足以单独证明所有 AMD RSMU 的全称、拓扑或功能。与 [VM10](../../UTCL2/sources/VM10-iommu-spec.md) 结合时，要区分缓存条目失效和依赖旧翻译事务的系统完成。

## 面向后续论文的复用

HUBS 应先写“接入、按需翻译、预约、数据/地址配对、返回”骨架；EA 在此骨架上研究共享存储、bank/group、QoS 和 credit；DF 接着研究地址归一化、目标路由与一致性边界。统计指标至少分入口阻塞、翻译等待、预约等待、可发但未选、下游 credit 不足、返回堵塞。资料支持这些分解方向，但不提供目标平台性能结论；实际瓶颈需用 [VM6](../../EA/sources/VM6-gcea-metrics.md)/[P5](../../GC/sources/P5-mi200-counters.md) 等观测对齐。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
