# GC2：GC 9.4.3 的 GRBM 选址与 RLC 控制闭环

更新日期：2026-09-24。

导读：从驱动调用看实例选择、广播、safe-mode、RLC 启停和门控顺序。适合恢复控制路径的状态与握手；不等同 RLC 固件或硬件内部算法。
来源：[gfx_v9_4_3.c，Linux v6.12](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c)，Git blob `c100845409f7948cd060c2e44d978aec8bf35997`。
阅读状态：精读 `xcc_select_se_sh`、safe-mode、`init_rlcg_reg_access_ctrl`、`wait_for_rlc_serdes`、RLC stop/reset/start/resume、`xcc_update_gfx_clock_gating`；其余引擎不扩展研究。

## GRBM 选址是持续状态

`xcc_select_se_sh` 根据 instance、SE、SH 参数设置 `GRBM_GFX_INDEX`；参数 `0xffffffff` 在此帮助函数中表示相应维度启用 broadcast writes，而非普通实例号。XCC 通过寄存器实例宏选取，是另一层寻址。后续读写的目标依赖这个选择状态，因此“选择”和“访问”必须作为一个逻辑序列观察。

等待 RLC SERDES 的代码取得 `grbm_idx_mutex`，遍历 SE/SH，选择实例并轮询 CU master busy；退出时恢复广播选择并释放锁。超时路径也恢复选择。这是共享选址状态需要互斥和清理的具体证据，不能把锁推断成硬件总线只能有一个在途请求。

## RLC safe-mode 和完成条件

进入 safe-mode 写 `RLC_SAFE_MODE` 的 CMD 与 MESSAGE，然后逐微秒轮询 CMD 清零。写命令只是提交，观察 CMD 清零才是此例中的握手点。退出路径写 CMD，MESSAGE 为退出含义，未在该函数中执行同样的轮询。

必须保留实现限制：该进入函数返回 `void`，循环达到 `usec_timeout` 后没有向调用者返回错误码。因此“驱动函数返回”不能直接写成“硬件已成功进入 safe-mode”。公共层状态维护见 [GC4](../../GC/sources/GC4-rlc-common.md)，其软件布尔值同样不能替代真实握手证据。

## 生命周期和门控

stop 清 RLC enable、关闭相关 idle interrupt、等待 SERDES；reset 置位/清除 RLC soft reset 并等待；start 置 enable，特定非 APU 路径再开 idle interrupt。resume 区分 PSP 与 legacy firmware loading：legacy 路径停机、加载 microcode、启动，然后进入 safe-mode 配置门控/电源相关状态。VF 分支会跳过一些操作，不能复制宿主路径到 VF。

clock-gating 的启用顺序是先较细粒度，再 medium，再 coarse；关闭采用反向顺序，并由 safe-mode 包围。它说明控制操作有依赖关系，不能把多个 enable 位当作可以任意排序的独立开关。代码中的 50µs 延时是软件序列参数，不是目标 RTL 某状态的必然持续时间。

## 对跨模块研究的价值

SMU/RLC 的协作需要区分策略请求、局部门控、固件接管、操作确认；SMN/GRBM 间接访问需要区分共享 selector 与数据访问。可复用的检查是：谁拥有当前状态、谁允许变更、完成怎样返回、超时后是否留下旧选择。内部固件执行、全部复位 drain 和所有 ASIC 特例仍不由这些函数证明。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
