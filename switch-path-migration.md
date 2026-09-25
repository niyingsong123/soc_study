# SWITCH path migration

Date: 2026-09-25. User authorization: U36.

Baseline: `8c70f1d4086d97600c0b44ed1c51c9e94aa98171`. The original main history remains intact. Thirteen lowercase-path updates were replayed in original topological order under uppercase `SWITCH/`, followed by the saved local content and path/documentation normalization. Replay commits have new identities; original author/date and commit IDs are recorded in their messages.

The existing uppercase module entry and source collection were preserved. No original_file, HUBS/assets or UTCL2/assets files were read, restored or uploaded. Unrelated uncommitted module research remains local.

## Replay correspondence

| Order | Original commit | Replay commit |
| --- | --- | --- |
| 1 | [fb48a74](https://github.com/niyingsong123/soc_study/commit/fb48a74191a3b091cc3bf18073c28abf13b35a30) | [312066b](https://github.com/niyingsong123/soc_study/commit/312066b9e241288d3653c5a5ed3dc0f31c92e922) |
| 2 | [9dfec9f](https://github.com/niyingsong123/soc_study/commit/9dfec9fa4cfa4ba75fd3805d403b024058737f7a) | [e6bf29b](https://github.com/niyingsong123/soc_study/commit/e6bf29b02a74aac740861d7268e8080843d7ce44) |
| 3 | [f83363c](https://github.com/niyingsong123/soc_study/commit/f83363c964647581f9fdcbdf78d84f5e69894574) | [19bd3da](https://github.com/niyingsong123/soc_study/commit/19bd3da46ad49f7dd23b2cc5a25e1a7defee3a2b) |
| 4 | [31b769f](https://github.com/niyingsong123/soc_study/commit/31b769f28af8f1092578e8e0047c044cee6225fc) | [2f88e87](https://github.com/niyingsong123/soc_study/commit/2f88e87f10c98fa454855f41b37e54571f045985) |
| 5 | [0c65b6d](https://github.com/niyingsong123/soc_study/commit/0c65b6d08921f9f463724c1c2ec14605a69c1d5e) | [3870ced](https://github.com/niyingsong123/soc_study/commit/3870ceddc7d4664606ac631b2ebb5919bd41e42c) |
| 6 | [99cbdd7](https://github.com/niyingsong123/soc_study/commit/99cbdd77051389b1e67d903ea3caa24c39d9da5d) | [b740d2c](https://github.com/niyingsong123/soc_study/commit/b740d2cd3954793fc01286d4e7e7ef1d956a6dc3) |
| 7 | [57dcff2](https://github.com/niyingsong123/soc_study/commit/57dcff24ab5c8b27e6c6340bafde6e60cdc17063) | [c798fa6](https://github.com/niyingsong123/soc_study/commit/c798fa6c716f8bd5e008e167260916585ac47551) |
| 8 | [585661d](https://github.com/niyingsong123/soc_study/commit/585661dfa3d90f3d0488cd3f6c5d50f6be8103a6) | [84d75fd](https://github.com/niyingsong123/soc_study/commit/84d75fd14d259aba5b67b16c409d939adcc67b1c) |
| 9 | [60c4feb](https://github.com/niyingsong123/soc_study/commit/60c4feb43c0ee7d42a22f3a09c059d5800acf13d) | [de1679b](https://github.com/niyingsong123/soc_study/commit/de1679b47499f43dac8467dc90f4e4bf84894087) |
| 10 | [7fd0d17](https://github.com/niyingsong123/soc_study/commit/7fd0d1761ec7f9399ff9df21963ae3ab3c1ddf27) | [a934600](https://github.com/niyingsong123/soc_study/commit/a9346009b5ebad33abe326072393092d807a80e4) |
| 11 | [d655c9e](https://github.com/niyingsong123/soc_study/commit/d655c9efc40ffbd1bd0c6c296d749b75a489dbd2) | [93a351d](https://github.com/niyingsong123/soc_study/commit/93a351dca35e737c89b4a8d728702ceca806d7e7) |
| 12 | [bdfd16a](https://github.com/niyingsong123/soc_study/commit/bdfd16a203c0d34187bcbb4cc122a6bb8495ff39) | [f9bac12](https://github.com/niyingsong123/soc_study/commit/f9bac12bdc314a04ac9d56d9e06197f5204a6fcf) |
| 13 | [8c70f1d](https://github.com/niyingsong123/soc_study/commit/8c70f1d4086d97600c0b44ed1c51c9e94aa98171) | [2ca8533](https://github.com/niyingsong123/soc_study/commit/2ca85337eb6358825fc67a960c6d338fac6c262b) |

## Verification scope

Each replay tree uses exactly the original blob IDs and modes for the corresponding lowercase files, mapped to uppercase. The subsequent local snapshot uses the saved local file content with Git-standard LF text line endings. The final normalization changes current links, command paths and obsolete split-directory instructions; immutable historical URLs retain their original path. Current uppercase file content is checked against the final local working files. No research simulation was rerun.
