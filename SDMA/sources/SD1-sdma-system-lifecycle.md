# SD1：AMDGPU SDMA 公共层：实例、固件和 RAS 接口

更新日期：2026-09-24。

导读：只研究 SDMA 如何接入 SoC：ring 到实例映射、固件版本条件、ECC 通知和复位责任；不替代外部 SDMA 项目的 FE/BE/TBE 内部资料。
来源：[Linux v6.12 amdgpu_sdma.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c)。
阅读状态：已读实例查找、上下文地址条件、固件头/feature 与 RAS 入口；未复制或修改独立 sdma_repo，未研究目标 FE/BE/TBE RTL。

## 实例和上下文

公共代码按 ring/page ring 指针寻找 SDMA instance/index，说明软件“队列”和“引擎实例”不是同义词。上下文保存地址还受 VF、VMID0、抢占能力和 MES queue 等条件影响；返回零可能表示该场景不使用该上下文机制，不能当成错误物理地址。

实例数量由设备上下文提供，不能从某个数组最大值或固件文件命名猜测目标引擎数。与 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md)/[IO13](../../NBIF/sources/IO13-nbio79-partition-doorbell.md) 连接时还要核对 NBIO 的实例/AID doorbell 映射。

## 固件是版本化接口

解析固件头时区分多个 major 格式，从相应字段取 firmware/feature version，未知格式返回错误。所读代码依据 feature version 决定 burst_nop 能力；不同装载模式还区分共享副本、多个实例和不同微码组成。

这证明驱动行为依赖 IP/固件版本，不能用某一组 packet 名称声明所有 SDMA 行为。固件内部线程、前后端微架构仍不在本源已知范围，不能据 TH0/TH1 字段直接映射项目 FE/BE/TBE。

## RAS 接入

支持 RAS 时为相应实例取得 ECC IRQ，使事件经过 RAS 分派。回调设置 KFD 的 SRAM ECC 标志；VF 分支不在这里直接 reset GPU，其他分支可发起 GPU reset。中断接收、错误分类和复位责任因此与虚拟化身份相关。

## 接续方式

SDMA 系统接口方案围绕提交、寻址、可见性、完成、事件和恢复展开。内部工作流继续以外部项目为准；[L1](../../SDMA/sources/L1-external-glossary-scope.md)–[L3](../../SDMA/sources/L3-external-open-questions.md) 明确原有登记内容及未读取状态，[SD2](../../SDMA/sources/SD2-sdma52-completion-maintenance.md) 提供公开维护/完成路径参照。任何新增 SoC 结论应注明是公共驱动实例还是本地目标证据。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
