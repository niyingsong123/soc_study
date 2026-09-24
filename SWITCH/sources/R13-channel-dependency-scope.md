# R13：Dally/Seitz：channel dependency 的可用结论与阅读范围

更新日期：2026-09-24。

导读：保存原作者记录可确认的 CDG/虚通道断环思想，并明确正文未成功取得；可用于定位死锁研究入口，不能代替原证明或覆盖所有自适应/协议级依赖。
来源：[Caltech 原作者技术报告记录，修订版 5231-TR-86](https://authors.library.caltech.edu/records/fd0yr-br438)；[正文入口](https://authors.library.caltech.edu/records/fd0yr-br438/files/5231-TR-86.pdf)。记录年份与常引用的 1987 年期刊版不同，引用时不可混为同一版本。
阅读状态：已核读原作者摘要和版本信息；原 PDF 本次未成功取得，另一教学链接需要授权。因此本篇为明确限于摘要的概念/使用边界笔记，未宣称读过原证明。

## 已有证据与研究推导分开

摘要确认利用 virtual channels 为网络构造 deadlock-free routing，并用 channel dependency graph 中的环描述相关问题；还说明可通过把物理通道拆成虚通道组移除依赖环。它没有给出本次可见的完整模型假设、证明细节和各拓扑算法实现，所以不能把摘要中的必要充分表述推广到所有带自适应路由、协议响应和任意端点行为的系统。

作为后续研究方法，可把一个节点定义成“可被持有的 channel/VC 资源”，若包持有 A 时可能等待 B，就画 A→B。物理拓扑有环不等于 CDG 有环，物理链路无环也不能自动覆盖端点缓存/协议响应形成的环。这个建模说明是本资料集的分析框架，不冒充原文逐段结论。

## 后续需要补足什么

取得正文后应核对 routing function 的确定性/适应性范围、buffer/packet 假设、目的地消费前提、虚通道组转换限制，以及 torus 等拓扑的具体构造。未取得前，不编写某套 AMD VC 编号的无死锁证明，也不声称本项目已有验证结果。

规划可以继续使用已读的 [R16](../../SWITCH/sources/R16-remote-control-deadlock.md) 讨论多个无死锁子网组合后的边界依赖，用 [R22](../../SWITCH/sources/R22-garnet-network-interface.md) 展示 NI tail 等待，用 [R19](../../SWITCH/sources/R19-booksim-buffer-state.md) 检查资源释放时点。它们不能被写成已经替代本报告的完整数学证明。本索引应让 Codex 明确：查基本入口可读本篇，写严格定理时必须继续取得原文。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
