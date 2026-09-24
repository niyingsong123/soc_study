# IO6：HDP 4.0 驱动：flush、invalidate 与 RAS 代际差异

更新日期：2026-09-24。

导读：研究 HDP 维护命令怎样由 CPU 或 ring 发起、哪些 IP 跳过 invalidate，以及计数清除为何有读清/写清区别；用于准确写完成与恢复边界。
来源：[Linux v6.12 hdp_v4_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c)。
阅读状态：已读 flush/invalidate、RAS query/reset、初始化及相关代际判断；没有目标硬件测试。

## 两种提交路径

flush 可直接写 remapped HDP_MEM_FLUSH_CNTL，也可向具备 emit_wreg 的 ring 追加寄存器写命令。函数返回只表示这段代码完成提交步骤，ring 命令可能尚未执行；本函数中看不到通用“等待所有系统写可见”的过程。

invalidate 使用 HDP_READ_CACHE_INVALIDATE，但 4.4.0、4.4.2、4.4.5 分支直接返回。不能把 no-op 解释成所有芯片自动一致，也不能强行要求所有代际执行相同寄存器操作。目标一致性责任要结合周围调用链和产品文档判断。

## 初始化与错误计数

初始化中部分 IP 有 HDP_MMHUB 控制设置；VF 会避开后续某些寄存器配置。支持 RAS 时，所读 EDC counter 归入 UE；清除方式在较新分支写零，旧分支读回清除。由此产生两项重要约束：读寄存器可能有副作用，重复采样可能改变结果；“计数已清零”不是错误根因已解决。

## 放进微架构主线

HDP 应分别研究入口映射、内部暂存/读缓存、维护提交、完成可见性、错误与低功耗。原始 MMIO 写、HDP flush、GPU cache flush 和 TLB invalidation 的对象不同。[IO2](../../HDP/sources/IO2-linux-device-io.md) 解释 posted write，[FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) 解释 fence，[IO14](../../HDP/sources/IO14-hdp60-power-sequence.md) 给另一代 power/clock 编程序列。

本源能确认软件操作和条件分支，不能独立给出 HDP cache 容量、所有旁路路径或目标模块物理连接。后续 Codex 若讨论“flush 完成”，必须继续找到等待点及其约束范围。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
