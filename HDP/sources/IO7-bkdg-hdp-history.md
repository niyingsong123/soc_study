# IO7：AMD 15h BKDG：HDP 历史职责与 UMA 窗口

更新日期：2026-09-24。

导读：HDP 全称和 host framebuffer 地址转换的 AMD 原厂历史依据；适合确认命名与窗口概念，不能作为现代 GPU 容量/拓扑参数。
来源：[AMD 50742 Rev 3.05，2016-05-21](https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/50742_15h_Models_60h-6Fh_BKDG.pdf)，Family 15h Models 60h–6Fh BKDG，§2.14.1–2.14.2.2，纸面页 169–170。
阅读状态：已读上述 GMC、framebuffer、HDP 正文及配置表；未研读整本寄存器手册。

## 历史架构关系

GMC 负责接收 GPU 各块内存请求、路由到相应接口，并处理 GPU 虚拟到 GPU 物理、再到系统地址的转换。HDP 的说明位于 framebuffer 章节，明确与 host 访问 framebuffer 的地址转换有关。它支持 Host Data Path 的历史命名，不支持把 HDP 自动解释成任意“数据 hub”。

此 APU 用系统内存的一部分作为 framebuffer/UMA。HDP aperture 的配置与 UMA 总容量不是同一个数，示例存在两者不同的情况。文中按该产品要求选择窗口大小并列出寄存器控制，这是 BIOS/平台配置边界，不是所有 GPU 的通用寻址规则。

## 防止错误迁移

旧文的窗口上限、推荐 framebuffer 大小及显示分辨率配置只适用于该产品语境。现代独立 GPU 的 VRAM、可调整 BAR 和 NBIO/HDP 分工不能从本表外推。GMC 这个旧聚合名称也不能直接映射为当前 UMC，翻译和 DRAM 控制在本项目需要分别研究。

## 后续复用

将本源用于术语来源和“host 地址→窗口→framebuffer 地址”概念；把现代实现问题交给 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md)/[IO6](../../HDP/sources/IO6-hdp40-maintenance.md)。HUBS/UTCL2 则通过 [VM1](../../UTCL2/sources/VM1-gpuvm-address-spaces.md)/[VM2](../../HUBS/sources/VM2-mmhub-v2.md) 研究 GPUVM 与系统地址边界。引用时写清历史 APU，避免把 2016 年说明和现代代码拼成同一颗芯片。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
