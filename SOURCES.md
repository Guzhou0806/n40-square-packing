# ZH: 来源、署名与派生
# EN: Sources, credit and derivation

ZH: 密度输入逐字节来自 [wand125/square-packing-bounds](https://github.com/wand125/square-packing-bounds/tree/1a25a5ed745fdd905a52f48fcc48150a0669032d/certificates/rect_n40_L67)，固定 commit 1a25a5ed745fdd905a52f48fcc48150a0669032d，SHA-256 为 71011d0356dd179c6e7e6e02c9a064ff30f6f13844016ce3b97463bf7ef53dc0。文件名或内部状态属于来源元数据，验证程序不据此判定通过。
EN: The density input is byte-identical to [wand125/square-packing-bounds](https://github.com/wand125/square-packing-bounds/tree/1a25a5ed745fdd905a52f48fcc48150a0669032d/certificates/rect_n40_L67), pinned at commit 1a25a5ed745fdd905a52f48fcc48150a0669032d, SHA-256 71011d0356dd179c6e7e6e02c9a064ff30f6f13844016ce3b97463bf7ef53dc0. Its filename and internal status are source metadata, not acceptance criteria.

ZH: 矩形密度与来源验证工作归于 wand125、Tokoharu 及其明确引用的前人；一般测度覆盖思路与 Burns、Massaccesi 等工作相关。本仓库不将既有密度或算法署为自己的研究成果。
EN: Credit for rectangle density and source verification belongs to wand125, Tokoharu and their cited predecessors; the general measure-capture approach relates to work by Burns, Massaccesi and others. This repository does not claim the existing density or algorithms as its own research results.

ZH: Rust 代码逐字节保留自 [Joshua Levy, the squares project](https://github.com/jlevy/squares/tree/ef79288a498b5469e6b944f7b150d83aeeab5f94/packing/sqverify_fast)。[独立性记录](https://github.com/jlevy/squares/blob/ef79288a498b5469e6b944f7b150d83aeeab5f94/packing/sqverify_fast/INDEPENDENCE.md) 的限制同样适用。保留原第三方注释，不将它们冒充新写的双语材料。
EN: Rust code is retained byte for byte from [Joshua Levy, the squares project](https://github.com/jlevy/squares/tree/ef79288a498b5469e6b944f7b150d83aeeab5f94/packing/sqverify_fast). The limitations in its [independence record](https://github.com/jlevy/squares/blob/ef79288a498b5469e6b944f7b150d83aeeab5f94/packing/sqverify_fast/INDEPENDENCE.md) apply. Original third-party comments are preserved and are not presented as newly authored bilingual material.

ZH: 端点削角与增强阈值由 Guzhou0806 的 AI 辅助研究提出；本次程序、运行整理及文字由 Codex 辅助完成。独立代码与数学审查也有 AI 参与，不等同人类专家同行评议。
EN: The endpoint caps and enhanced thresholds were proposed in Guzhou0806's AI-assisted research. Codex assisted this implementation, execution packaging and exposition. Independent code and mathematical review also involved AI and is not human expert peer review.

ZH: 新增文件按根目录 MIT 许可提供。密度的原 MIT 许可完整保留在 licenses/wand125.txt；Rust 的原项目许可完整保留在 licenses/jlevy-squares.txt，其中代码适用 MIT，其余项目材料适用 CC BY 4.0，第三方存档另有边界。本仓库未复制那些第三方论文存档。
EN: New files are offered under the root MIT license. The density's original MIT license is retained in licenses/wand125.txt; the Rust project's original license is retained in licenses/jlevy-squares.txt, granting MIT for code and CC BY 4.0 for other project materials, with separate boundaries for third-party archives. Those third-party paper archives are not copied here.

ZH: caps.py 从独立审查过的削角实现派生，只调整相对路径、显式拒绝优化模式和命令帮助文本；数学函数保持不变。完整入口、集成检查、控制和依赖下载器为新增。精确文件身份和派生摘要见 results/source-identity.json。
EN: caps.py derives from the reviewed independent cap implementation, changing only relative paths, explicit optimized-mode refusal and command help; mathematical functions are unchanged. The full entry point, integrated checks, controls and dependency downloader are new. Exact file identities and derivation hashes are in results/source-identity.json.
