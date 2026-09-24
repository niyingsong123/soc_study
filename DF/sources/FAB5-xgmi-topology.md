# FAB5：AMDGPU XGMI：hive、节点拓扑、链路信息与 RAS

更新日期：2026-09-24。

导读：从驱动观察 XGMI 多设备拓扑的建立、固件协作、hop/link 信息和错误入口；特别记录 v6.12 中 pstate 切换实际被提前返回禁用，防止把死代码当现行功能。
来源：[Linux v6.12 amdgpu_xgmi.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/amdgpu_xgmi.c)。
阅读状态：已读 hive 生命周期、add/remove、PSP topology、hop/link 查询、pstate 和 RAS 入口；未获得 XGMI 私有线协议。

## 软件拓扑与物理链路

驱动用 hive 集合管理相关设备，每个节点有 node ID，hive 有独立 ID 与锁。支持时由 PSP 初始化会话并取得这些身份，再更新每个成员看到的 topology；部分恢复/无 PSP 路径使用替代初始化，不能把其中常数当硬件固定节点号。

新增设备不只改变本设备列表，还需要其他成员获得更新。扩展拓扑信息可能要求整个 hive 使用一致的能力/缓冲模式；VF 路径也有不同处理。因而拓扑应作为具有版本和生命周期的控制状态，而不是每次随意读一张静态表。

`num_hops` 字段含 link type 与实际 hop 子字段，查询函数掩出低位；`num_links` 另行取得。hop、link 数和带宽不是同一个指标，更多 link 也不能直接证明所有流量均匀分摊。地址可达性、分区、目标内存、路由策略还需另证。

## 功能存在于代码不等于正在运行

v6.12 的 `amdgpu_xgmi_set_pstate()` 在取得/释放 hive 后因 firmware bug 注释直接返回 0；后面 high-request 计数与切换逻辑在该版本不可达。因此只能记录其设计意图，不能宣称驱动当前会依据每个 peer 的请求动态切换 hive pstate。返回成功也可能表示 no-op。

RAS 处理按不同 XGMI/ASIC 版本选择 PCS 或 MCA/ACA 路径。错误计数、状态清除与错误注入接口各有作用，不能把任意 PCS 错误计数直接解释成重放次数或丢失事务数。

## 研究用途

DF/SWITCH 的跨 die 研究应增加控制面前提：节点身份、topology 建立、peer 可见性、VF 差异、复位后重建，再讨论数据面路由和顺序。PHY 用链路类型及 RAS 入口定位物理层证据，但无需从驱动猜测编码/FEC。与 [P1](../../DF/sources/P1-ryzen-fabric-topology.md) 的 CAKE 历史定义关联时仅比较职责，不声称 XGMI hive 就是某一代 CAKE 拓扑。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
