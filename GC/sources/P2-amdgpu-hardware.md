# P2：AMDGPU 驱动中的 IP 边界与系统入口

更新日期：2026-09-24。

导读：解释 Linux 如何按 IP 组织 GPU，以及 GMC、GC/RLC、SDMA、SMU、IH 的职责。适合首次建立系统边界；查具体队列或硬件协议时应转入对应代码笔记。
来源：[Core Driver Infrastructure，Linux 6.12](https://docs.kernel.org/6.12/gpu/amdgpu/driver-core.html#gpu-hardware-structure)。
阅读状态：已精读 GPU Hardware Structure、Graphics and Compute Microcontrollers、Driver Structure、Memory Domains、IB 说明；其余 API 参考未逐项研究。

## 结构和容易误判的边界

驱动以 IP 版本组织代码。同一 SoC 可以组合不同代 IP，因此不能把文件中的 `v9`、`v6` 当成整片统一代际。IP 列表被用于初始化、销毁、休眠与恢复；寄存器访问、芯片复位等跨 IP 功能还位于 SoC 层文件。研究时需要同时查“这个 IP 的操作”及“上层何时调用它”。

GMC 在老芯片中较集中，Vega 及之后功能分散到面向不同 IP 的 memory hub，驱动仍把相近的编程模型统称为 GMC。因此软件目录或结构体是组织方式，不能直接画成唯一物理 memory controller。地址空间与访存接入问题见 [VM1](../../UTCL2/sources/VM1-gpuvm-address-spaces.md)、[VM2](../../HUBS/sources/VM2-mmhub-v2.md)，HBM 命令控制器另见 UMC 资料。

GC 是完整图形/计算复合体；本项目只研究 GL2、GRBM、RLC，其他引擎作为外部请求源。RLC 是 GC 内处理电源管理相关功能的微控制器，RunList 这个历史名字不足以推定现今功能。SMU 则承担 SoC 层的时钟、电压与供电管理；二者需要协调，但不是同一控制器。

IH 汇聚各 IP 的事件到 ring，驱动读取记录后交给对应源处理。事件记录与源模块的业务状态是两层，读走记录不自动清除故障。SDMA 可用于分页和 GPU 页表更新，也可以服务用户态命令；这说明“页表更新由谁写入”与“页表由谁遍历”应分别研究。

## 环境中的对象

IB 是放在内存中的命令缓冲；ring 中的命令可指向 IB，硬件取完 IB 后继续 ring。它不是新的执行引擎。Doorbell 是通知队列的 MMIO 区域，不是队列数据本体。

CPU domain 表示 GPU 不可直接访问的系统内存池；GTT 表示经 GART 等映射供 GPU 使用的系统内存；VRAM 是显存，APU 语境可以是 BIOS 划出的内存。这里的分配域、GPUVA、DMA 地址、硬件物理目标不能混为一谈，后两者对照 [IO3](../../PCIE/sources/IO3-linux-dma-api.md)。

## 跨模块复用与回读条件

画总图时可复用以上职责，不用重新通读数千行 API 页面。要判断目标 hub 数量、某实例属于哪一个 die、初始化顺序或特定代际功能时，仍须查目标 IP 表和调用链。本资料没有提供完整 RTL 拓扑，也没有证明 CF、SMN、RSMU 的包含关系。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
