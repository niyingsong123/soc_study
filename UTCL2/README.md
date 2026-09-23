# UTCL2 — 二级地址翻译缓存

[项目入口](../README.md) · [模块关系](../module-map.md) · [来源](../sources.md)

公开术语为 Unified Translation Cache - Level 2 [P5]。本地资料确认 shaobo TBE 的 UTCL1 miss 会请求 UTCL2 [L2]。

作为公共翻译主题独立管理。本项目 UTCL2 的 hub 归属尚待框图确认；不包含所有 UTCL1，也不同于 GL2 数据缓存。

学习客户端共享、翻译 miss、权限/异常和 invalidation。谁负责页表遍历、遍历单元是否在 UTCL2 内，均需目标设计资料。关联：[UTCL1](../UTCL1/README.md)、[HUBS](../HUBS/README.md)。


## 已转换资料

以下原始资料已转换为 Markdown；原件统一归档于项目根目录 original_file。图片保存在本目录 assets，移动 Markdown 时需同时保留配套图片。此前入口中的待确认项属于初始化记录，本次转换不替代按产品/版本进行的架构核验。

- [tb_mm_utcl2.md](tb_mm_utcl2.md)：49 页，[原件](../original_file/tb_mm_utcl2.pptx)。
- [UTCL2 结构和使用简介 by Wang Junmin.md](UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin.md)：38 页，[原件](../original_file/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin.pptx)。
- [utcl2_top.md](utcl2_top.md)：1 页，[原件](../original_file/utcl2_top.pdf)。
- [UTCL2地址翻译及预取技术介绍.md](UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D.md)：26 页，[原件](../original_file/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D.pdf)。

[转换校验报告](../conversion-report.md) · [来源与哈希清单](../source-manifest.json)
