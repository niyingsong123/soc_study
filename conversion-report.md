# Markdown 转换校验报告

日期：2026-09-23。范围：UTCL2 与 HUBS 新增的 3 份 PPTX、2 份 PDF。已有 README.md 保留；SDMA 独立项目未参与转换或移动。

## 结果

五份资料均已生成 Markdown，原件已平铺归档到 original_file。原件保留原名和字节内容。对应的页面图像与原始嵌入图像位于各模块 assets 目录，属于 Markdown 必需资源。

| 来源 | 转换文档 | 页数 | PPT 原生表格 | 有备注的页数 | 校验 |
| --- | --- | --- | --- | --- | --- |
| C01 | [tb_mm_utcl2.pptx](UTCL2/tb_mm_utcl2.md) | 49 | 14 | 3 | 通过 |
| C02 | [UTCL2 结构和使用简介 by Wang Junmin.pptx](UTCL2/UTCL2%20%E7%BB%93%E6%9E%84%E5%92%8C%E4%BD%BF%E7%94%A8%E7%AE%80%E4%BB%8B%20by%20Wang%20Junmin.md) | 38 | 0 | 12 | 通过 |
| C03 | [utcl2_top.pdf](UTCL2/utcl2_top.md) | 1 | 0 | 0 | 通过 |
| C04 | [UTCL2地址翻译及预取技术介绍.pdf](UTCL2/UTCL2%E5%9C%B0%E5%9D%80%E7%BF%BB%E8%AF%91%E5%8F%8A%E9%A2%84%E5%8F%96%E6%8A%80%E6%9C%AF%E4%BB%8B%E7%BB%8D.md) | 26 | 0 | 0 | 通过 |
| C05 | [MMHUB_introduction.pptx](HUBS/MMHUB_introduction.md) | 41 | 22 | 1 | 通过 |

## 已完成的校验

- 原页数与 Markdown 页标题、逐页预览数量一致：155 页，其中 PPTX 128 页、PDF 27 页，包含空白页和隐藏页。
- 将 PPTX 原始文字节点、备注以及 PDF 文本层逐项与 Markdown 比对：6,445 段均可在转换结果中找到。
- 36 个 PPTX 原生表格均已转为 Markdown 表格；合并单元格的空间关系以同时保留的页面图像为准。
- 16 页演讲者备注已保留。
- 223 个配套资源中，202 张常规位图通过解码校验；其余为原始 EMF/WMF 矢量图，保留文件并可在完整页面 PNG 中查看。
- PPTX 嵌入媒体与压缩包中的原始字节逐一比对一致；128 张 PPT 页面图与 PowerPoint 只读导出结果逐一比对一致。
- 抽查了中文页面、复杂表格与架构图的渲染效果，未发现转换引入的文字或图形缺失。未宣称逐字人工复核图片内文字。
- 归档前、归档后五份原件的 SHA-256 全部一致；转换文件及图片校验值记录在 [校验清单](source-manifest.json)。
- 归档后的本地文档链接已进行检查，结果见清单中的 final_links_checked。

## 原资料的限制

tb_mm_utcl2.pptx 第 6 页引用 code_coverage_improve.xlsx，但该附件没有随资料提供。转换文档保留名称并注明缺失，未生成失效链接。

文字框按原文件对象顺序转写；图中连线、布局、公式外观及图片内部文字通过图像保留。原始资料的技术结论、过时说明和笔误均未在转换时改写。
