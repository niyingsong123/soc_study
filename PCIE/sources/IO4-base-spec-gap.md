# IO4：PCIe Base 5.0：规范入口与待补读范围

更新日期：2026-09-25。

导读：正式规范全文未取得的缺口记录，指明链路层/事务层哪些细节不能只靠 FPGA 指南推定；无需把它当成已完成的技术精读。
来源：[PCI-SIG PCIe Base 5.0 登记入口](https://pcisig.com/PCIExpress/Specs/Base/_5.0_1.0)。
阅读状态：未取得全文；未声明规范合规阅读，版本以原有 5.0 登记为限，不推定当前最新标准。

## 缺口的具体范围

后续需要正式标准确认 TLP 类型与属性、Posted/Non-Posted/Completion 顺序规则、tag 生命周期、Completion 分段与错误、各类 flow-control credit、Data Link retry、LTSSM/复位及虚拟化能力。应按所研究产品支持版本选择，不能为了覆盖面同时拼接不同代际规定。

本笔记不填写未读取的位编码、超时数值和时序表。PCIe 的标准规范层、IP 实例层、Linux 软件层必须分别标注：实例可能增加本地接口机制，软件 API 也不会暴露全部链路细节。

## 目前可用的替代证据

[IO1](../../PCIE/sources/IO1-pg213-transactions.md) 支持 CQ/CC/RQ 侧接口与本地 NP credit 的实例研究；[IO11](../../PCIE/sources/IO11-ats-pri-pasid.md) 展示 ATS/PRI/PASID 的配置和资源管理；[IO9](../../PCIE/sources/IO9-pci-error-recovery.md)/[IO12](../../PCIE/sources/IO12-aer-error-path.md) 展示软件恢复状态机；[MEM6](../../PHY/sources/MEM6-pcie-equalization.md) 展示 FPGA PHY 的均衡接口。它们能帮助规划子模块，不能一起构成“已核验完整 PCIe Base”的声明。

若后续只研究 SoC 接口，可以先完成上述路径和未知项；若要实现协议 checker、链路状态机或精确字段，则须补齐匹配版本规范。保留本编号以便取得全文后直接更新，不另建一个看似新增、实际重复的标准条目。

## 2026-09-25 再次取得原文的结果

从本条 PCI-SIG 官方入口跟随 Base 5.0 下载，实际目标是 [PCI-SIG member document 13005](https://members.pcisig.com/wg/PCI-SIG/document/13005)，返回会员登录页。本会话未获得可用正文，因而不能把此次访问记成规范补读成功，也没有自动注册账号、联系他人或替换成其他版本。

已可在 [VM10](../../UTCL2/sources/VM10-iommu-spec.md) 阅读 AMD IOMMU 对 PRI/PPR 的处理，在 [R8](../../SWITCH/sources/R8-axi-ordering-contract.md) 阅读 SoC bridge 的 AXI 契约；它们缩小周边问题的未知，不会替本条完成 PCIe Data Link、TLP 顺序或 Base 原文核验。具备合法访问条件的本地 Codex 应先记录原文修订号，再按本篇范围补读，不需要重做所有外围资料。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
