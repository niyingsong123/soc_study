# R15：FlooNoC router RTL：参数化队列、路由裁剪与握手边界

更新日期：2026-09-24。

导读：从固定版本 RTL 识别输入 FIFO、route select、输出仲裁、可选输出 FIFO 和 VC/物理通道复用，并记录代码较原论文的新能力和端点握手约束。
来源：[FlooNoC floo_router.sv，固定提交 c58f1bf](https://github.com/pulp-platform/FlooNoC/blob/c58f1bf13baeda147b4e87e961683d389db090a1/hw/floo_router.sv)；原资料入口为 main，现以固定提交避免漂移。
阅读状态：已读参数、FIFO/route/mask、output/VC arbiter、credit 和 assertions；被实例化子模块的所有内部算法未在此文件展开。

## 参数化结构

每个输入/虚通道建立 FIFO，随后 route_select 得到路由 mask。mask 裁剪禁止回环或 XY/YX 不可能连接；输出按虚通道仲裁，再可选插入 OutFifo，最后由 VC arbiter 映射到物理通道。深度为零的 FIFO/bypass 与非零结构不同，不能只看模块名判断一定有寄存器切分。

NumVirtChannels、NumPhysChannels、VcImpl、collective/reduction 等参数在当前代码中存在，而 [R7](../../SWITCH/sources/R7-floonoc-paper.md) 的核心实验强调独立物理网络与简单 router。两者是版本演进关系，不能据此声称论文与代码矛盾，也不能把当前参数全部归于原论文。

物理与虚拟通道数量的组合并非全部实现；代码对某些组合显式报 unimplemented。规划时应先列合法配置空间，避免生成看似通用却无法 elaboration 的组合。

## 发射资格和 credit 时点

Credit 模式在输入被下一级逻辑握手消费后登记归还事件；输出 VC arbiter 另用对端 credit。credit 对应的是特定缓冲/通道资源，不能以端口 ready 替代全部 credit 状态。

代码特别提醒 VC arbiter 中 valid 可依赖 ready，因此接到要求保持独立握手的 endpoint 时需要 cuts。内部握手规则不必与边界 AXI 完全一致，但适配必须明确；否则组合 ready/valid 依赖可能形成环或破坏稳定性。

## 断言与证据限度

文件有 valid-stability、路由方向和无回环检查，某些 data-stability 检查在该版本仍被注释。不能把注释中的断言当作已执行的验证。collective、原子/归约支持还涉及额外路径，研究普通 unicast 应说明关闭哪些配置。

本文件提供结构级证据，不独自证明全网无死锁、所有流公平或目标频率。具体仲裁需跟进 output_arbiter/VC arbiter，协议语义需看 NI；资料集目前以此固定边界供后续 Codex 深入。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
