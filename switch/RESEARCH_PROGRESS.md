# Switch 研究进度与接续记录

更新日期：2026-09-24。此页记录实际完成的研究轮次，不用文档版本号或 R0/R1 参考设计编号代替进度。

## 当前结论

**第一轮综合基线与第二轮 Router 专项深化已完成；第三至第六轮尚未完成。** 第二轮的模型与测试在本次云端会话环境中执行，研究结果写回同一个 GitHub 仓库；没有建立后台持续任务，也没有把用户本地电脑作为文件来源。

当前正文是 [switch_detailed_guide.md](switch_detailed_guide.md)，第二轮重点在第 38—49 章。前 37 章重整系统主线；第一轮完整展开内容另以 [v2.0 历史原稿](switch_detailed_guide_v2.0.md) 保留，使用原 blob `185212bdbd8e3784c6ca6aa655489432fbd0ba2d`，并非重新生成的近似副本。

简化版 [switch_quick_guide.md](switch_quick_guide.md) 本轮保持不变。它仍适合作为六问入口，但不替代第二轮的详细实现讨论。

## 原六轮安排与实际状态

2026-09-24 已完成后续方案复核，当前第 3–6 轮任务以 [SWITCH/research-plan.md](../SWITCH/research-plan.md) 为准：先研究 NI 事务契约，再研究 D2D 交接、性能，最后在相关模块已有详细结论后做系统复审。下表保留原目标和真实进度；本次规划没有执行第 3 轮，也没有重新运行第二轮模型。

| 轮次 | 目标 | 实际状态 |
|---|---|---|
| 1 | Router/packet/NI/NoC/D2D/SDMA 综合基线 | 已形成；没有声称完成 RTL 实现 |
| 2 | allocator、buffer、credit、pipeline、失败路径、资源依赖 | 本轮完成专项阅读、文稿深化及有限模型检查 |
| 3 | 选定 AXI/CHI 子集的准确映射 | 未完成；现有内容是概念对照 |
| 4 | 锁定 UCIe 版本/模式的 Adapter/PHY/retry 规范细化 | 未完成；原创 LRP-64 不等于 UCIe 实现 |
| 5 | 完整流量、拥塞、吞吐与尾延迟研究 | 未完成；本轮小范围 credit 扫描不能算作全部完成 |
| 6 | 基于前述结果做 SDMA 系统交叉复审 | 未完成；不把已有 SDMA 章节当作最终复审 |

## 第二轮的具体交付

本轮补充了 observe/reserve/commit 的旧值/新值契约、同边沿冲突表、VC generation 与流水元数据、VA 稀疏申请图及多拍预订问题、SA matching 和 iSLIP 指针规则、SRAM 队头缓存与 landing register、linked-pool 指针更新、共享容量的不可撤销承诺、credit 与 packet ownership 两种闭环、推测/bypass 失败路径，以及含共享资源的死锁分析。

公开资料对照包括 Peh/Dally、Mullins 等原始 Router 论文、iSLIP、DAMQ、ElastiStore，以及固定版本的 Garnet/BookSim 源码。具体章节、文件、版本和证据边界见详细稿第 37、48 章及根目录 [sources.md](../sources.md)。

## 可复现检查

```bash
python3 switch/examples/router_round2.py --report /tmp/round2_results.json
```

代码：[router_round2.py](examples/router_round2.py)。本次结果：[round2_results.json](examples/round2_results.json)。仅使用 Python 标准库；没有依赖本地芯片资料、gem5 安装或闭源 IP。

实际通过 14 个测试组。16 次随机网络检查覆盖 12 个 2×2 与 4 个 3×3 配置/种子，共交付 1,728 个 packet、11,249 个 flit，执行 25,343 次 SA commit、8,665 个模型 edge 的不变量检查；这些计数只汇总报告中的指定随机运行，不把测试与报告生成的重复执行重复累加。

同一 17-flit 包的三跳实验：D=1/反向延迟1时首/尾到达15/95；D=8/反向延迟1时15/31；D=8/反向延迟12时15/47。单位是模型 clock edge，不是某实际芯片的 ns 测量。

脚本 SHA-256：`67676b1cf4841f45bdc7d9574342dc92d997ce434c62c88ac119ed666a18fbd5`。
脚本 Git blob：`9bd6b43f804b80242be6a3a836d1f9d053f539e8`。

## 模型与验证边界

mesh 模型实现有限私有 VC FIFO、独立 RC/VA、两级 SA、延迟 credit、tail-free、有限 sink 与源端流量。iSLIP、shared-pool 许可和 linked-list 存储是独立局部检查，未替换进 mesh。源码中的部分 packet/generation 信息用于旁观验证，不代表新增行业标准线上字段。

未完成真实 RTL、SRAM/CDC 时序、STA、功耗、推测/bypass 全网实现、完整 UCIe/CHI 合规、全系统形式化死锁证明和实际 SDMA 指令模型。随机检查通过只覆盖本次轨迹，不是所有输入和所有状态的证明。

## 接续方式

资料集入口：[SWITCH 逐篇资料索引](../SWITCH/sources/README.md)，全局编号见[资料总入口](../sources.md)。模块上下文见 [SWITCH/README.md](../SWITCH/README.md)的“资料集与接续”。先根据索引导读选择相关笔记，复用其中的机制、版本与限制，再按需回原文；同一来源跨模块只维护一份主笔记。R9 是 CHI 模型指南、R12 是架构概述；2026-09-25 已补 R13 原文定理前提/证明，并新增 R23 正式 CHI E.a 选读。仍不将来源定理当作目标系统已验证的无死锁证明。本次资料整理不新增论文完成轮次。

下一轮开始时先读本页、[修订研究方案](../SWITCH/research-plan.md)、主文档第 49 章及当前代码；从 GitHub 当前提交检查是否有并行修改。需要补充结论时区分公开来源、参考设计与目标芯片事实，新增细节同时审查是否改变 buffer、credit、ownership、ordering 或完成点。

本轮基于提交 `0c65b6d08921f9f463724c1c2ec14605a69c1d5e` 开展。保留项目原件不上传、独立 SDMA 项目不复制/修改、缺失 C01–C05 正文不自行恢复等既有约定。本目录研究的是公开 NoC/D2D 参考微架构，不能直接认定为 shaobo/anshi 或某代 AMD 的实际 SWITCH。
