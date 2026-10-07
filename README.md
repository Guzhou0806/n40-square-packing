# ZH: 40 个单位正方形的严格下界
# EN: A strict lower bound for 40 unit squares

ZH: 对允许任意旋转、平移及边界接触、内部两两不交的 40 个单位正方形，计算机辅助证明给出 s(40)>33509/5000=6.7018。本仓库提供固定密度输入、数学转移证明和完整复验程序。
EN: For 40 unit squares with arbitrary rotations, translations and boundary contacts, and pairwise disjoint interiors, the computer-assisted proof gives s(40)>33509/5000=6.7018. This repository supplies the fixed density input, mathematical transfer proof and complete replay program.

ZH: 密度来自 wand125 在 Tokoharu 验证方法基础上的矩形证书；连续节点第二验证器来自 Joshua Levy 的 squares 项目。本次贡献是针对该固定密度的增强阈值、削角转移与严格下界的独立代码复验和可复现整理；不主张密度证书或验证方法的原创归属，也不主张当前最佳或优先权。
EN: The density comes from wand125's rectangle certificate using Tokoharu's verification method; the second continuous-node verifier comes from Joshua Levy's squares project. This contribution independently rechecks the enhanced thresholds, cap transfer and strict bound for that fixed density with distinct code and packages a reproducible result. It claims neither authorship of the density/verifier methods nor current-best status or priority.

ZH: 完整运行覆盖 201 个连续中心域、42 个增强非水平节点、200 个角区间和 65 个有损区间。CODE_DISTINCT_FULL 表示实现不同而共享数学结构；不是方法完全独立、形式化证明或同行评议认证。
EN: A complete run covers 201 continuous centre domains, 42 enhanced nonhorizontal nodes, 200 angular intervals and 65 lossy intervals. CODE_DISTINCT_FULL means distinct implementations sharing mathematical structure; it is not full method independence, formal proof or peer-review certification.

ZH: 运行步骤见 [复现说明](REPRODUCIBILITY.md)，数学论证见 [证明](PROOF.md)，证据边界见 [验证说明](VERIFICATION.md)，来源与许可见 [署名](SOURCES.md)。
EN: See [reproduction](REPRODUCIBILITY.md) for execution, [proof](PROOF.md) for mathematics, [verification](VERIFICATION.md) for evidence boundaries and [sources](SOURCES.md) for credit and licensing.
