# C01：MM_UTCL2 图示与验证环境：从翻译事务到可观测检查点

更新日期：2026-09-25。

导读：覆盖 MM_UTCL2 的 APT1/2/3、VML2/ATCL2、fault/retry、两类失效以及验证环境，适合建立请求生命周期和验证检查点；所有容量与字段均须保留该资料版本范围。
来源：[仓库既有 tb_mm_utcl2 页图](https://github.com/niyingsong123/soc_study/tree/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6/UTCL2/assets/tb_mm_utcl2)。这是用户提供且已入库的 HYGON 标识资料，不是 AMD 官方公开规范。缺失的转换正文未恢复，未读取或上传 original_file。
阅读状态：49 页的已提交页图均已取得文字阅读或图像核看记录；2026-09-25 补回并直接核看了此前未读取的第 1、4 页。主要技术范围为第 3–5、15–31、33–47、49 页；并非对所有 OCR 字符逐字校勘。图示版本与目标芯片对应关系仍需本地确认。

## 页码导览

| 页码 | 内容 | 适合解决的问题 |
|---|---|---|
| 3–15 | MMHUB 位置、UTCL1 开关路径、RTL 总图 | 谁提供翻译服务、谁发数据请求 |
| 16–20 | APT1、APT2、fault 与 APT3 | 地址空间、权限和本地/远端目的地怎样分开处理 |
| 21–28 | PTE cache、walker、ATCL2 工作队列 | hit/miss 如何占资源与返回 |
| 29–31 | retry、中断及 invalidation | 错误、重试、清缓存和完成分别由谁负责 |
| 33–47 | agents、寄存器/页表生成、参考模型 | 如何把接口事务变成可检查的预期结果 |
| 49 | 未覆盖项与问答 | 哪些环境假设不能误当设计保证 |

## 第 4 页补读：BOWEN MMHUB 与 UTCL2 客户端增长

[第 1 页](../assets/tb_mm_utcl2/slide-001.png) 是 HYGON 的 MM_UTCL2 introduction 封面；[第 4 页](../assets/tb_mm_utcl2/slide-004.png) 则是有实质架构信息的 BOWEN MMHUB 总图，不能再将此前的缺图视为无影响。

图中有 mmhub_ip 与 mmhub_ip1 两组；每组包含共享 UTCL2、PCTL、rsmu、rdft，SMN 接至 rsmu、DFT 接至 rdft。lane 内画出 Tap Chain、VML1、DAGB、EA 以及到 DfSdpX 的连接。它是结构图，不能仅按方框纵向位置断言所有请求无条件串行经过每一块；具体翻译开关/sideband 仍需结合其他页。

左组包括 t9/t10/t6/t5/t4/t7/t8，右组 t3/t2/t1/t0；对应客户出现 SDMA、HDP、DBGU、MP、decoder/encoder 等。正文明确每增加一个 lane（一个 VML1）增加 **4 个 UTCL2 client**，lane 扩张会放大共享翻译接口数量。SDMA 内部还具有与 VML1 同类翻译作用的 UTCL1，历史 SDMA 采用 UTCL1 sideband translation；BOWEN_A0 新增的 SDMA_H0–6、decoder/encoder 可启用内部 UTCL1。这是端点内翻译与 HUB lane 翻译两种组织选择的直接参考。

图中关于合并 decoder/encoder sideband 以减少客户端数的文字带删除线；只能登记为被划除的候选讨论，**不得写成已采纳设计**。据此可安排三个微架构问题：内部 UTCL1 与 lane VML1 的使能/旁路互斥怎样控制；fan-in 增加后 client/tag、返回路由及背压怎样扩展；共享 UTCL2 的队列/仲裁是否随接口数增长。页图没有回答具体队列深度和仲裁算法，后两项属于待研究问题。

这页也为 [RSMU](../../RSMU/sources/MG5-rsmu-umc-index.md) 提供了“SMN 接入每个 MMHUB 的 rsmu”这一参考设计位置，不能直接映射为某代 AMD 目标芯片的实例数。

## 正常请求的地址与属性处理

入口携带 VA、VMID/VFID、client/tag、读写/执行属性等。APT1 依据 space、aperture、上下文模式判断是物理直通、地址空间变换还是 GPUVM 查询。VML2 命中后仍要检查表项合法性和权限；miss 交给 walker，后者沿 PDE 层级寻找 PTE。APT2 决定结果是否还需 ATC；APT3 根据 framebuffer 区间和本地节点配置作 xGMI 地址转换。多个阶段都是条件分支，不能把请求一律画成三次页表遍历。

第 19–20 页特别说明，本地 HBM、远端 DCU 和 APU UMA 主机地址不能只靠一个 spa 位区分。相同的地址属性还要结合区间、PF_OFFSET、模式和本地 region 编号；DF 仍需进行自己的目标解码。请求返回给 UTCL1 的 PA/属性与随后数据事务的路由决定，是相关但不同的检查点。

## 缓存、walker 与 ATC 的独立资源

第 22 页的示例 PTE cache 为 2 way、64 set，每 line 含 8 个 64-bit PTE，另存 valid、tag、VMID、parity。选 set 涉及 VA 与 VMID，取 line 内表项又有自己的 offset。命中必须同时满足身份、tag 和有效性，不能只比较地址。第 23 页的 BigK/QoS 配置与其他 C 资料不同；只用于该图示配置，不拼接成一个“统一 UTCL2 参数表”。

PDE-as-PTE 可提前终止遍历并提供大页映射；Translation Further 则允许继续细分。两者改变的是遍历终止条件，不能只在最终 PA 拼接阶段打补丁。需检查 walker 状态、缓存填充、权限传播和失效覆盖是否一致。

第 27 页给出 ATCL2 的两个 cache bank，各有 4K 与 2M cache，miss 进入独立 work queue，通过 ATHUB 取得 ATPT。文中 32 个 work 状态与 VML2 walker 的状态资源不同；不能把两种 miss 合成一个 outstanding 计数。第 28 页又区分正常、retry/fault、untranslated 返回状态，返回地址的解释依状态而变。一个有效返回不必然意味着可立即执行数据访存。

## fault、retry 与失效

第 29–30 页中，fault classification、retry 许可、中断使能、crash 控制是分别配置的。应记录异常类型、是否回 retry、是否发 IH 事件及客户端是否重发，不能由其中一项推导其余项。页表修复也不能替代缓存失效与旧请求收敛。

第 31 页区分寄存器发起的 VML1/VML2 失效和 ATHUB 发起的 ATCL1/ATCL2 失效；VM flush type 01/10 指向 UTCL1 中的 **VML1**，ATHUB 路径指向 **ATCL1**。有地址范围、VMID/PF/VF 条件与共享 engine 的 SEM。图中 PTE/PDE 列的 “no ack” 只描述该列，不能推出整个失效没有完成确认，旁边仍有 ENGx_ACK。第 49 页也明确 VM invalidate 不清 ATCL2 cache；并发 ATS 返回仍须单独验证。

与 [C05](../../HUBS/sources/C05-mmhub-dagb-ea.md) 第 18 页比较，VM 01/10 的 UTCL1 子类型标注不一致。后续应保留差异并查目标寄存器/RTL，不能默默合并。强失效是否等待在途读写的系统语义另见 [VM10](../../UTCL2/sources/VM10-iommu-spec.md)，不能靠这张表独自证明。

## 验证环境真正提供了什么

第 33–34 页把 DUT 的翻译请求、UTCL1/VML1 失效响应、ATHUB ATS/失效、取页表内存、GRBM 配置和 IH 分成不同 agent。这意味着可以独立施加返回延迟、错误和背压，而不是只喂一个 VA→PA 黄金字典。

第 36–41 页的 dpitran 是 SV/C++ 间的命名事务桥：monitor/interface 把字段推入共享对象，回调参考模型；寄存器配置完成后再生成相应页表；内存 agent 按取表物理地址返回表项。页表生成必须与 context 的 depth、block size、start/end、base、权限概率和生成样式一致，否则会把测试生成器的错误归因于 RTL。ATPT 可另行控制 4K/2M 格式、地址范围、错误状态和响应延迟。

第 45–47 页的 checker 既处理周期中的预期/实际比较，也在结束时检查遗留状态。适合继承的原则是：接受请求时建账，返回/取消时销账，结束时查未完成项；同时观察配置与失效，而非只比较 PA。第 49 页暴露 mm_utcl2 环境中 l1_id 固定为 0 的覆盖缺口，因此后续应补身份透传与多客户端返回交错问题。具体 UVM 类名只是该环境实现，不能宣称当前仓库已有可执行环境。

## 后续写作重点

用一张事务表串起“入口属性 → APT 决策 → cache/walker/ATC 资源 → 返回语义 → 失效/异常”。精确寄存器位值、延迟与状态数必须回看目标版本。[C02](../../UTCL2/sources/C02-utcl2-cache-organization.md) 解释 cache 组织与 BigK 反例，[C03](../../UTCL2/sources/C03-utcl2-topology.md) 补全总拓扑，[C04](../../UTCL2/sources/C04-translation-prefetch.md) 解释预取扩展；本笔记不会把三者不同代际参数混用。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
