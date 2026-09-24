# MEM13：Ramulator HBM3：层级状态、时序与生成式模型

更新日期：2026-09-24。

导读：适合逐项理解 HBM3 模型的共享/独立资源、命令依赖与时序作用范围；可与控制器代码联读，不能替代 JEDEC 标准。
来源：Ramulator2 commit `72427a1bba3771564c4fb0e494ba02242fd1eaa7`：[生成的 HBM3.cpp](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/dram/impl/HBM3.cpp)、[生成源 hbm3.py](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/python/ramulator/dram/hbm3.py)。
阅读状态：已读层级、命令/时序声明、命令总线分类及主要 timing 约束；未运行模型，未与完整 JEDEC 逐条核验。

## 模型的结构语言

组织层级为 Channel、PseudoChannel、SID、BankGroup、Bank、Row、Column。命令包括 ACT、按 bank/全部 PRE、RD/WR 及自动预充电变体、REFab/REFpb、RFMab/RFMpb。名称存在只表示模型支持该操作，不等于任意器件/AMD 平台都启用它。

生成的 C++ 提供编号、元数据及配置加载；具体组织和 timing 数值还要从运行配置取得。仅阅读 HBM3.cpp 中的参数名称不能声称已经掌握某 speed bin 的完整时序。生成文件与 Python 源必须固定同一提交。

## 时序按资源层次生效

PC 层处理数据总线占用和读写转向，SID 及相邻 SID 的列命令关系另有约束，BG 层区分相同组与不同组的列/激活间隔，bank 层处理 ACT→RD/WR、PRE→ACT、自动预充电恢复等状态。刷新/维护还会阻断正常访问。

模型把 ACT、REFpb/RFMpb 等活动纳入特定激活窗口检查，并声明 nFAW、nRRD、nCCD、nWTR、nRTW、nRFC 等约束。这里的组合是本模型定义；在完整标准未读时，不应将模型每一条组合都升级成标准条文。

## 命令总线也是资源

Python 生成过程根据 command cycles 与行/列分类建立占用约束。不同 PC 的数据并行性不消除共享命令资源；控制器还要检查同周期能否配对发命令。[MEM12](../../UMC/sources/MEM12-ramulator-hbm-controller.md) 展示这一额外过滤，解释为何即使多个 bank 都 ready，也未必能同拍服务。

## 后续研究怎样使用

每项 timing 写清“约束哪一级资源、什么前驱、什么后继、最小间隔、参数来源”。分析瓶颈时区分 bank 状态、bank-group 限制、数据方向切换、命令总线冲突和维护占用。模型实验必须保存配置与提交，不能用单个 HBM3 文件代表完整可复现平台。

与 [MEM11](../../HBM/sources/MEM11-jedec-scope-gap.md) 对照可列正式规范缺口；与 [MEM9](../../HBM/sources/MEM9-micron-hbm3e.md) 对照只能做数量级检查，不能从 HBM3E 产品峰值倒填本模型时序。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
