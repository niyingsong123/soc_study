# VM7：gem5 Vega TLB：查找、回填、属性与模型简化

更新日期：2026-09-24。

导读：提供一套可以沿函数追踪的 TLB 模型，解释命中、miss、回填和返回。尤其记录其 ASID、fault 与失效处理的简化，避免后续 Codex 把模拟器当成完整硬件规格。
来源：[tlb.cc，gem5 v24.1.0.1](https://github.com/gem5/gem5/blob/v24.1.0.1/src/arch/amdgpu/vega/tlb.cc)。新增资料。
阅读状态：精读构造、lookup/insert、invalidate/demap、issue/translationReturn、protectionChecks、walkerResponse、cleanup；未运行模型。

## 微架构角色和资源

模型把 coalescer、TLB、walker 分成不同对象。TLB 自身有 set、way、free list 和按近期访问维护的 entry list；hit/miss latency 是配置参数，不代表 AMD 真实流水。上游 coalescer 对下游并发施加限制，不能只读 TLB 的构造注释就判断整个翻译路径无限并发。

lookup 以 VA 求 set，然后检查该地址是否落在 entry 的页面范围内，命中可更新近期使用次序。insert 优先取 free entry，否则取替换端 entry，再将新映射放到近期使用端。可变页大小意味着查找要比较覆盖范围，而不仅是固定 VPN 相等；代码也提醒用最小页粒度跟踪事件可能造成冗余 walk。

## 请求—返回闭环

`issueTLBLookup` 记录合并请求的数量与访问时间并安排事件；miss 根据端口配置交给下一层或 walker。返回携带 TLB entry，按 allocationPolicy 决定是否回填。随后做保护检查，重新结合页内 offset 产生物理地址，保留 uncacheable/system 等属性，向 coalescer 返回。

完成回复后还有 cleanup 事件。其同周期优先级与 coalescer cleanup 协调，以免 retry 新请求时旧条目仍占着 tracking 状态。这个行为是事件模型的调度要求，硬件设计应对应到明确的寄存器更新/旁路规则，不照抄软件事件优先级。

## 必须保留的局限

所读 `lookupIt` 只显示 VA 范围查找；`demapPage(va, asn)` 的 asn 未参与匹配；coalescer 还出现 `VMID TODO`。所以本例不构成多进程/VF 地址隔离的完整证明。写保护错误在所读路径中直接 fatal，也不是生产 GPU 的完整 fault-retry 流程。

`invalidateAll`/`demapPage` 移除已存 entry，却没有在这些函数中完整解决所有在途旧 walk 的回填抑制。若教学设计要支持 invalidate 与 miss 并发，应单独安排 epoch/tag、drain 或 replay 的设计与验证，明确这是新增设计，不是这里已经实现。

## 后续用途

UTCL1 研究 hit/miss/return 可直接复用本流程；UTCL2 研究共享资源时联读 [VM8](../../UTCL2/sources/VM8-gem5-page-walker.md)、[VM9](../../UTCL1/sources/VM9-gem5-coalescer.md)。实际参数、权限全组合、地址空间键和旧回填行为必须从目标资料确认。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
