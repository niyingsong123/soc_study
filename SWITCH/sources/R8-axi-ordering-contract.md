# R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界

更新日期：2026-09-24。

导读：保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。
来源：[Arm IHI 0022H，AMBA AXI and ACE Protocol Specification，2020](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)。
阅读状态：已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。

## 单次传输与完整事务

五条独立通道分别承载 AW、W、B、AR、R。每通道仅在采样沿 VALID 与 READY 同时成立时发生 transfer。发送者不得等待 READY 才拉起 VALID；一旦 VALID 有效，在握手前必须保持它和对应信息稳定。接收者可以先等 VALID 再给 READY，但由此形成的跨模块依赖仍要检查。

AW 与 W 是独立到达的通道，不能假设地址总先于数据或同拍到达。AXI4 写响应要等待地址被接受和最后一拍写数据被接受；写数据顺序要与地址顺序匹配。AXI3 的 WID/写交织规则不能套到 AXI4。桥接到分组网络后，需要保存地址、burst 长度、data beat、byte strobe 与来源身份的关联。

## ID 与排序范围

同 ARID 的读响应即使目标不同，也需按规定顺序回到 master；互联可以扩展 ID 位来区分不同入口，再在返回时去掉附加部分。原 ID、互联分配的源标识、NoC tag/ROB index 不是同一对象，复用前必须等待对应生命周期结束。

同 ID 的读顺序、写响应顺序与不同通道之间的内存观察顺序不能混为一谈。不同 ID 允许一定重排，不代表所有访问都可忽略设备属性、地址 hazard 或软件同步。若 bridge 改变路由并产生乱序响应，需要端点重排或限制 outstanding，例如 [R7](../../SWITCH/sources/R7-floonoc-paper.md) 的两种 NI 设计。

## 响应与最终可见性

规范分别定义 observation、completion 和允许提前响应的条件。BVALID/B handshake 表示该 AXI 边界的响应，不应无条件解释为写入已经到 DRAM cell、已被所有 coherent agent 观察或已对持久介质保存。bufferable/cacheable/device 等属性及后续事务 hazard 的责任必须跟着 bridge 传递。

因此技术论文应为每个边界写“响应者接手了哪些责任、可否缓冲、何时保证后续访问看到正确顺序”。CPU MMIO posted write 和 DMA 同步分别见 [IO2](../../HDP/sources/IO2-linux-device-io.md)/[IO3](../../PCIE/sources/IO3-linux-dma-api.md)，不能以一个 AXI B 通道结论代替。

## 研究和检查重点

对应具体队列研究：AW 先到/W 先到、长 burst、R/B 返回堵塞、同 ID 跨目的地、ID 扩展/缩减、错误响应、最后一拍与 reset 交错。数据稳定性与 no-combinatorial-interface-path 要在实际切分处落实；[R15](../../SWITCH/sources/R15-floonoc-router-code.md) 的内部握手依赖必须经适配后才可接 AXI endpoint。精确的 burst 限制、原子/独占和 ACE 操作仍需查相应章节。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
