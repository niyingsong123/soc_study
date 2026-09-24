# FAB1：CDNA 3 白皮书：XCD/IOD、memory-side cache 与一致性层次

更新日期：2026-09-24。

导读：解释 CDNA 3 把计算侧 L2、IOD 存储侧 cache、HBM 与互联重新分配后的职责，特别区分 snoop filter、cache 数据和 CPU/GPU 统一内存；适合校准模块边界与带宽口径。
来源：[AMD CDNA 3 Architecture 白皮书](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/white-papers/amd-cdna-3-white-paper.pdf)。本次读取版本已含 MI325X/HBM3E 内容，不能当作最初发布版本的逐字快照。
阅读状态：已核读 XCD、memory architecture、IOD/Infinity Cache、HBM 和分区段落，重点印刷第 9–13 页；没有据此补写未公开的 DF 协议状态机。

## 结构变化先于 feature 列表

XCD 承担计算及近端 cache，IOD 承担更大范围的存储和通信。资料给出每 XCD 的 4 MiB L2、16-way、16 个 channel；IOD 下连 HBM，上接多个 XCD，四个 IOD 与八个 HBM stack 形成产品级系统。MI300X 与 MI300A 的计算芯粒构成不同，不能把某一产品 XCD 数量无条件复制到另一产品。

L2 使用 writeback/write-allocate 来合并流量并减少跨 Infinity Fabric 请求；它在 XCD 内提供硬件维护的一致性边界。更近计算侧的向量 cache 仍需显式同步才能满足强可见性/顺序要求。于是“系统是 coherent”并不表示所有 cache 层都无需软件管理，参见 [GC3](../../GC/sources/GC3-llvm-memory-model.md)。

## memory-side cache 与 snoop filter 的区别

白皮书描述 Infinity Cache 为 memory-side cache：缓存 memory 内容，不作为接收下层 dirty victim 的普通末级 cache。它的数据阵列不以普通 coherent cache 的方式吸收 snoop；同一系统还包含覆盖 XCD L2 的 snoop filter，用于尽量在 IOD 侧判断一致性请求是否需要打扰 XCD。

这两段需要一起理解：存在 snoop filter 不代表 memory-side data array 本身保存全部 ownership 状态；“数据 cache 不参与某类 coherency traffic”也不代表 IOD 不承担一致性协调。后续 DF 方案应分别研究目录/过滤信息、数据命中路径、真正需要远端 L2 响应的情况，以及 dirty data 的最新版本归属。

## 数量和带宽必须注明层级

资料把 L2 channel、XCD→IOD 通道、Infinity Cache channel 和 HBM stack 联系起来，但它们的字节宽度、方向和聚合范围不同。总计 256 MiB Infinity Cache 的构成为 128 个 channel、每 channel 2 MiB；这是该产品架构范围，不是每个 XCD 各自拥有 256 MiB。

L2 read、write/fill 能力不对称，跨层带宽也不同。峰值带宽应注明读/写、单 XCD/全封装、每周期/每秒、cache hit/HBM 路径；不能把图中若干 TB/s 相加得到端到端带宽。具体性能仍受分区、局部性、地址分布、时钟和协议流量限制。

MI300A 的 CPU/GPU 共用 HBM 有助于避免设备间显式搬运，但不消除缓存、翻译、同步和 ownership 的管理。spatial partitioning 又可能改变 XCD 归属和用户可见设备边界；软件 agent 的作用域不能仅凭封装外观判断。

## 可复用的研究任务

GC 写近端 L2 合并、可见性与请求流；DF 写跨 XCD 路由和一致性服务；UMC/HBM 写实际介质路径；SWITCH/PHY 写跨 die 的承载。白皮书不足以证明精确队列深度、VC 分配、目录组织和 CAKE 内部，后续必须继续保留这些空白。与 [GC1](../../GC/sources/GC1-cdna2-memory.md) 做代际对照时比较职责迁移，而非只比较 cache 容量。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
