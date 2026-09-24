# SD2：SDMA 5.2：doorbell、维护命令、fence 与 trap

更新日期：2026-09-24。

导读：把 SDMA 系统接口串成“提交→维护/翻译→完成记录→通知”，重点是不同 flush 的对象、wptr 单位与可选中断；只读公开代码的 SoC 边界。
来源：[Linux v6.12 sdma_v5_2.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c)。
阅读状态：已读 ring get/set_wptr、mem_sync、HDP flush、VM flush、pipeline sync、fence 和 trap handler；未扩写引擎内部 packet 全规格或 FE/BE/TBE 论文。

## 提交位置与执行进度

软件 ring wptr 转为 byte 单位后写 shadow 并敲 64 位 doorbell；读回时再右移恢复软件单位。doorbell 表示新命令范围可见，不代表这些命令已被执行。NBIO 的窗口配置必须匹配，见 [IO5](../../NBIF/sources/IO5-nbio74-host-bridge.md)/[IO13](../../NBIF/sources/IO13-nbio79-partition-doorbell.md)。

## 三种维护操作不能混为一谈

mem_sync 发 GCR 请求并包含相应图形 cache 的 writeback/invalidate 控制，所读实现选择较大维护范围。HDP flush 在前两个实例使用带 HDP_FLUSH 标志的 POLL_REGMEM，结合 NBIO req/done 地址和实例 mask；更多实例走公共 HDP 路径。VM flush 则委托 GMC 更新页表基址/失效 GPU TLB。

这些操作分别面向数据 cache、host data path 和翻译状态。pipeline sync 通过轮询 fence 地址的序号等待相关前序工作，不是无条件检测全部硬件空闲。每种等待需注明对象、范围、重试条件和错误退出。

## 完成记录与中断

emit_fence 发出写序号的命令，64 位模式以两个写入表达高低部分；这段代码本身不能证明 CPU 任意一次 64 位读都原子观察更新。只有请求 INT flag 才追加 TRAP，因此没有 trap 不等于没有 fence 进度。

trap handler 通过 MES queue ID 或 client/ring ID 找到相应 ring，再调用 amdgpu_fence_process。它是“通知到了→检查完成记录”的路径，不能把每个 trap 直接对应一条拷贝。[FAB7](../../DF/sources/FAB7-amdgpu-fence-lifecycle.md) 解释 fence 扩展与软件完成，[MG7](../../IH/sources/MG7-ih-core-consumer.md)/[MG8](../../IH/sources/MG8-irq-dispatch-lifecycle.md) 解释 IV 传输和分派。

## 微架构与外部项目边界

后续只在 SoC 方案中定义缓冲区所有权、请求身份、维护依赖、完成和复位后的在途处理。目标 SDMA 的 FE/BE/TBE 分工、内部仲裁与流水继续回外部只读项目核对；公开 Navi 相关驱动不能直接作为 shaobo/anshi 的细节。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
