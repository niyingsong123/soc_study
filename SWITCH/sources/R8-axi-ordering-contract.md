# R8：AMBA AXI：握手、独立通道、ID 顺序与完成边界

更新日期：2026-09-25。

导读：保存 AXI 数据通路必须遵守的 VALID/READY、AW/W/B 依赖、burst/ID 和响应顺序规则；适合研究 bridge、NI、buffer 和“收到响应意味着什么”。
来源：[Arm IHI 0022H，AMBA AXI and ACE Protocol Specification，2020](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf)。
阅读状态：已取得完整规范，重点核读 A3 握手/通道关系、A5 ID、A6 ordering/observation/completion，并补核 A3.4 burst/error 与 A7.2 exclusive；本笔记只覆盖 AXI 主干，不宣称完整整理 ACE、AXI5 原子等全部扩展。

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

对应具体队列研究：AW 先到/W 先到、长 burst、R/B 返回堵塞、同 ID 跨目的地、ID 扩展/缩减、错误响应、最后一拍与 reset 交错。数据稳定性与 no-combinatorial-interface-path 要在实际切分处落实；[R15](../../SWITCH/sources/R15-floonoc-router-code.md) 的内部握手依赖必须经适配后才可接 AXI endpoint。与当前 NI/bridge 有关的 burst、错误与 exclusive 规则补在下文；AXI5 原子与 ACE 细节按后续实际范围继续选读。

## A3.4：burst 的地址、字节与拆分边界

令每 beat 最大字节数 `B=2^AxSIZE`，beat 数 `L=AxLEN+1`。AXI3 各 burst 为 1–16 beats；AXI4 的 INCR 可为 1–256，FIXED 仍最多 16，WRAP 只能 2/4/8/16。每 beat 的宽度不能超过参与接口的数据宽度，**整个 burst 不能跨 4 KB 边界**；这项检查独立于内部 NoC packet 大小。

INCR 首拍地址为 AxADDR，其后第 N 拍地址为 `floor(AxADDR/B)×B+(N−1)×B`，因此非对齐起点不能简单每次在原始地址上加 B。WRAP 起点必须按 B 对齐，回绕下界为 `floor(AxADDR/(B×L))×(B×L)`，到达上界后回到下界。FIXED 每拍地址和允许的 byte lanes 不变，但 WSTRB 可以在允许的 lanes 内逐拍不同。

例如起点 0x1003、B=4 的 INCR，后续地址是 0x1004、0x1008，而非 0x1007、0x100B；首拍只覆盖由非对齐地址允许的字节，WSTRB 还可进一步关闭有效 lane。示例为对规范地址公式的计算，不代表所有 slave 都必须在内部以同样方式实现。

burst **不能提前终止**。写端可以将剩余拍的 WSTRB 全清，但仍必须完成剩余握手；读端可以丢弃不需要的数据，却仍要接受完整拍数。对读敏感 FIFO，多读再丢弃会产生副作用，不能以该方法代替正确的请求长度。SLVERR/DECERR 也不能用来跳过余下的拍。

AXI4 有一个明确的拆分例外：长度大于 16 的 INCR，即使 Non-modifiable，也允许拆成多个较短 burst，以兼容 AXI3 或控制 QoS；生成请求保持其他事务特性，只调整长度和地址。不能由此推出任意短 burst、exclusive 或不同属性请求都能随意拆并。NI 若分包还需分别保留上游事务身份、下游片段计数及最后一拍，写侧最终对原 burst 只返回一次 B。

## A3.4.5：错误响应仍然要完成事务

| 响应 | 语义 | bridge/NI 要保存的责任 |
| --- | --- | --- |
| OKAY | 普通访问成功；也可能是 exclusive 未成功或不支持 | 必须结合 AxLOCK/monitor 能力判断，不能统一当原子成功 |
| EXOKAY | exclusive 读或写成功 | 仅适用于 exclusive；成功读表示建立监控，不等于后续写必成 |
| SLVERR | 已到 slave，但该访问出错 | 消费/返回所需全部 beats，保留错误归属 |
| DECERR | 通常是互联无法解码目标 | 默认错误端点也必须完整收尾，不能让没有目标的请求永久占资源 |

读响应按 beat 携带 RRESP，同一 burst 可有不同错误；写响应对整个 burst 只有一个 BRESP。若窄化、拆分或内部重试，原请求的错误聚合必须按对应适配规则完成，不能因先看到 OKAY 就提前报告整笔成功。规范不保证已报错的写完全没有副作用，不能把错误响应自动当作可安全重试的事务回滚。

## A7.2：exclusive 的细节与容易遗漏的例外

exclusive read 建立地址与 ID 的监控，后续 exclusive write 需使用匹配的 AWID/ARID、地址、长度、size、burst、cache/protection 等相关属性；写阶段必须在读阶段完成后启动。期间其他写入或 monitor 被同 ID 新读替换，都可能使独占失败。在**支持 exclusive 的 slave**上，成功写回 EXOKAY 并更新内存，失败回 OKAY 且不更新。

关键例外：不支持 exclusive 的 slave 可以忽略 AxLOCK，回 OKAY，**该 exclusive write 会按普通写更新内存**。因此主端收到 exclusive read 的 OKAY 后不应继续假定原子序列受保护。文档在 A7.2.5 明列这个区别，不能写成“所有 OKAY 的独占写都不落内存”。

exclusive burst 总字节数必须是 1/2/4/8/16/32/64/128 之一，起点按**总字节数**对齐，最多 16 beats、最多 128 bytes；属性还要保证请求抵达负责监控的部件。monitor 可以观察比请求更大的区域，最多 128 bytes，因此相邻字节被写也可能导致失败。ID 压缩、缓存提前响应和地址重映射都可能破坏监控身份，bridge 设计需显式分析。

本次补核 A3.4、A7.1–A7.2 的相关正文。这里只覆盖 AXI 主干的 burst/错误/独占；ACE 额外信号、AXI5 atomics 的完整表和所有宽度转换组合不在当前选读范围。研究范围已明确时，不需要为了“全文精读”机械扩写无关章节。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
