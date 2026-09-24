# MEM12：Ramulator 当前 HBM 控制器：双命令槽与 FRFCFS

更新日期：2026-09-24。

导读：研究请求如何变成可发出的列/行命令，以及优先级、激活缓冲和共享命令总线怎样约束吞吐；提供代码级 UMC 对照实例。
来源：Ramulator2 commit `72427a1bba3771564c4fb0e494ba02242fd1eaa7`：[hbm34_controller.cpp](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/impl/hbm34_controller.cpp)、[hbm_controller_base.h](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/impl/hbm_controller_base.h)、[hbm_controller_base.cpp](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/impl/hbm_controller_base.cpp)、[frfcfs.cpp](https://github.com/CMU-SAFARI/ramulator2/blob/72427a1bba3771564c4fb0e494ba02242fd1eaa7/src/ramulator/controller/scheduler/impl/frfcfs.cpp)。
阅读状态：已读所列文件的队列选择、时钟推进、slot eligibility、发命令和调度比较函数；未运行仿真，未通读所有插件/完成回调实现。

## 从请求到命令

控制器每步先执行 tick/refresh/row-policy 和插件前处理，再挑候选命令，最后进行后处理。候选请求的下一步命令由 DRAM prerequisite 决定；同一个读请求可能先产生 PRE 或 ACT，而不是马上 RD。

调度器先判断当前命令是否 ready，再按到达时间选较老请求，并应用 slot 的额外 eligibility 过滤。因此“FRFCFS 等于永远 row-hit first”不准确：代码的直接比较依据是当前前置命令是否满足条件，是否命中行会通过前置命令与时序间接影响结果。

## 两条总线不等于无限并行

基础 HBM 控制器分 ColumnBus 和 RowBus 两个 slot，先处理列槽、再处理行槽。候选优先查看 active buffer，再看 priority buffer；普通读写队列只有在相应优先条件允许时才进入选择。优先队列存在但请求暂不 eligible，仍可能影响其他请求的机会，需要按分支研究，不能只看优先级名字。

row policy 若把候选升级成另一命令，还要重新确认命令适合当前 slot；不合适需要撤回更改。发出 ACT 后请求可进入 active buffer，而发出该请求最后命令后的移除是另一种生命周期事件。

## HBM3/4 半周期约束

所读实现把控制步分上升/下降半周期；列命令只在上升侧尝试，行命令还受同周期组合限制。同 PC 的 all-bank 行命令不能与相应列命令随意配对。下降侧主要允许 PREpb/PREab，并检查先前上升侧命令是否冲突；同 PC 的 bank 选择还要区分 SID/BG/bank，不能只比较 bank 编号。

ACT 的配对/占用状态继续影响后续半周期。此处体现了“PC 有独立数据资源但存在共享命令资源”：仅按 bank timing 判 ready 还不够，必须同时过 command-bus eligibility。

## 用于 UMC 方案的检查点

分别记录队列阻塞、DRAM timing 不就绪、slot 不兼容、同周期配对冲突以及完成等待。饥饿研究必须考虑优先维护请求，吞吐研究须区分每半周期候选与真正 issue。[MEM13](../../HBM/sources/MEM13-ramulator-hbm3-model.md) 给出同提交的层级/时序定义；[MEM2](../../UMC/sources/MEM2-ramulator2-paper.md) 是较早论文，两者结构已有演进，不应混写版本。

以上是模拟器事实及其建模启发，不证明 AMD UMC 使用相同调度、队列深度或半周期实现。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
