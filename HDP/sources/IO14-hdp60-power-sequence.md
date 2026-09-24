# IO14：HDP 6.0：维护提交与时钟/存储低功耗切换

更新日期：2026-09-24。

导读：研究 HDP power/clock 配置的顺序约束和代际地址差异，适合把低功耗放回可访问性与状态保持主线；不能据此推导 SRAM retention 细节。
来源：[Linux v6.12 hdp_v6_0.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c)。
阅读状态：已读完整短文件的 flush、clock-gating 更新及查询；未取得目标电源状态机/电气规范。

## 维护操作的边界

flush 保留直接 MMIO 或 ring emit_wreg 两种路径，与 [IO6](../../HDP/sources/IO6-hdp40-maintenance.md) 相似；没有因函数名而增加全系统完成保证。该函数表不含 4.0 文件中的同一组 invalidate/RAS 操作，不能通过缺少 callback 推断硬件全部功能。

## 编程序列

先检查支持的 LS/DS/SD flag；6.1 使用不同 HDP_CLK_CNTL 偏移。切换前强制相关时钟打开，再关闭原 clock/power gating 控制，按支持模式配置 SRAM 低功耗，最后撤销时钟 override。临时强制时钟是为了使切换期间控制访问可进行，并不等同永久禁止节能。

查询函数通过特定位报告一种模式，并采用 if/else 优先关系；返回值是软件解释后的状态，不是所有寄存器的无损快照。不能从一个 flag 推断全部内部 SRAM 同时处于同一状态。

## 规划中的问题

研究低功耗应先说明正常请求路径，然后明确进入条件、在途操作处置、状态保留、唤醒与重新服务时点。此文件只给编程序列，没有完整证明排空、数据保持或唤醒延迟；这些继续作为目标材料缺口。

与 [MG2](../../SMU/sources/MG2-smu13-control.md) 的系统管理操作相连时，区分 SMU 策略请求与 HDP 本地寄存器操作。不能把两份文件自动组成一条真实调用链，应通过调用者和对应 IP 版本补证。

---

[本模块资料索引](README.md) · [模块研究方案](../research-plan.md) · [全局资料入口](../../sources.md)
