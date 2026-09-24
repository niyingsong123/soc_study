# IO1：PG213：TLP 接收、选择性流控与跨接口保序

更新日期：2026-09-24。

导读：围绕 TLP 到用户逻辑的转换，解释 descriptor、有效字节、NP credit、Split Completion 及 Posted 顺序检查点；适合 PCIe 请求/完成微架构研究。
来源：[Completer Request](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Request-Interface-Operation)、[Memory Read](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Memory-Read-Operation)、[Memory Write](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Completer-Memory-Write-Operation)、[Selective NP Flow Control](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Selective-Flow-Control-for-Non-Posted-Requests)、[Maintaining Transaction Order](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Maintaining-Transaction-Order)，PG213 v1.3，页面更新 2026-07-31。
阅读状态：已读所列正文；FPGA PCIe4 IP 的接口实例，不是完整 PCIe Base 规范或 AMD GPU PCIe RTL。

## 接收时保留什么信息

CQ 接口把 TLP 变成 AXI4-Stream 包，起始是 16 字节 descriptor，有数据的请求再带 payload。descriptor、对齐填充和真实 payload 是三种不同字节；tkeep 表示有效 Dword 范围，并不等于每个被覆盖字节都应写入存储器。实际写 mask 要结合 first/last byte enable 或 byte_en。

短至一两个 Dword 的请求可有不连续 byte enable；零长度写仍可能携带一个 Dword 但全部 byte enable 为零。零长度读的长度编码也不是简单零，而是相应 descriptor 与 byte enable 组合。教学模型若只按长度连续覆盖内存，会遗漏这些边界。

## 读完成与请求身份

读请求没有 payload，目标逻辑必须通过 CC 接口返回 Completion，可拆成多次。不同请求的 Completion 可以乱序，而同一请求的 Split Completions 要保序。因此需要保存 request identity、剩余字节/地址位置、错误状态和资源释放条件；收到第一段不等于整个请求完成。

## NP 反压不能堵死 Posted

该 IP 用额外 NP credit 表示用户侧接收 Non-Posted 的空间，credit 为零时仍可递交 Posted。普通 tready 若阻塞整个 CQ，不能替代这一选择性机制。credit 复位为零，可提前返还额度，计数饱和于 32，观察端存在流水延迟；它是此用户接口资源，与 PCIe 链路层的各类 credit 不应混成一个池。

NP 暂停期间，Posted 可以越过积压 NP；恢复后再处理较早的 NP 并回到正常顺序。研究应区分协议允许的绕行与目标依赖需要的保序。页面关于同时归还/消费额度的文字算法较简化，RTL 精确同拍更新还需匹配配置/完整接口说明，不能凭概述补写所有组合。

## Posted 的顺序检查点

RQ 与 CC 是不同提交口。为避免 Completion 越过某个 Posted，请求可带 6 位 sequence number；IP 在其走到内部不可再被 Completion 越过的位置时回报序号。存在两组回报通道，必须同时检查。

该回报只证明内部发送流水的先后位置，不证明远端内存更新已经对所有观察者可见。研究时分别标记 CQ/RQ 握手、顺序检查点、链路发送、目标完成和软件观察；结合 [IO2](../../HDP/sources/IO2-linux-device-io.md)/[IO3](../../PCIE/sources/IO3-linux-dma-api.md) 才能解释主机可见性。CF 可以借鉴这种契约写法，但本项目 CF 协议尚未被此资料确认。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
