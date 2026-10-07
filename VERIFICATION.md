# ZH: 验证范围与限制
# EN: Verification scope and limitations

ZH: 来源实现 full-mixed 的 49 个阶段已完整执行并退出 0，包括全水平域、200 个非水平节点、42 个增强节点、新削角包络和组合。历史原始 201 方向 runner 的水平任务曾终止，其整体仍为 FAILED/INCOMPLETE；不把 full-mixed 称为该原始 runner 的完整成功。
EN: All 49 producer full-mixed stages executed and exited 0, covering the full axis domain, 200 nonaxis nodes, 42 enhanced nodes, fresh cap envelopes and composition. The historical original 201-direction runner had its axis task terminated and remains FAILED/INCOMPLETE as a whole; full-mixed is not represented as a complete success of that original runner.

ZH: 第二节点路线固定 sqverify_fast commit ef79288a498b5469e6b944f7b150d83aeeab5f94，使用凹截线梯形积分与区间导数，五组阈值均完整执行。新的有理数削角程序自行解析密度、半平面裁剪、生成 16 块支持域并计算全部 65 个全局上界；不导入来源几何或组合函数。
EN: The second nodal route pins sqverify_fast commit ef79288a498b5469e6b944f7b150d83aeeab5f94, using concave-section trapezoids and interval derivatives, and executes all five threshold groups. The new rational cap program parses the density, clips half-planes, constructs 16-piece supports and computes all 65 global bounds itself, without importing producer geometry or composition functions.

ZH: 独立代码审查重建了全部 200 分类与 65 条收费，并用另一种差分前缀扫描重算 r=1、64 的最大值；其余 63 个最大值依据已审代码的完整运行。审查未发现固定实例的数学反例。共享前提包括密度、D4 对称、角网格、连续中心二分、导数界与端点削角引理，故使用 CODE_DISTINCT_FULL。
EN: Independent code review rebuilt all 200 classifications and 65 charges, and separately recomputed maxima for r=1 and 64 by difference-prefix scans; the other 63 maxima rely on complete execution of reviewed code. No mathematical counterexample was found for the fixed instance. Shared premises include the density, D4 symmetry, angular net, continuous-centre subdivision, derivative bounds and endpoint-cap lemma, so the grade is CODE_DISTINCT_FULL.

ZH: sqverify_fast 的独立性记录披露其作者阅读过相关证明评审、回执和性能信息；本项目没有核实完全隔离的历史开发过程，也不使用 METHOD_DISTINCT_FULL 标签。详见来源记录链接。
EN: sqverify_fast's independence record discloses reading related proof reviews, receipts and performance information. This project has not established a fully isolated historical development process and does not use METHOD_DISTINCT_FULL. See the linked source record.

ZH: 对抗测试覆盖缺失/重复方向、漏增强节点、错误重数、精确参数浮点化、漏小三角形、事件顺序、调小 G、目标变更复用参数、旧回执和断言关闭；整数扫描使用无界整数，并检查超过 128 位的测试权重。合法边界接触是必须通过的正控制。Rust 自带 38 个单元和对抗测试也在完整入口中运行。
EN: Adversarial tests cover missing/duplicate directions, omitted enhanced nodes, wrong multiplicity, floatified exact parameters, missing subtriangles, event order, reduced G, changed targets with stale parameters, stale receipts and disabled assertions. The integer sweep uses unbounded integers and tests weights beyond 128 bits. Legal boundary contact is a required positive control. The full entry point also runs Rust's 38 unit and adversarial tests.

ZH: 公开目录自身的执行结果保存在 results/public-replay.json；该文件是最小化结果，不是原始日志。完整入口每次从真实输入重新计算。对应提交的 GitHub Actions 状态由 GitHub 实际运行记录给出，不能从本说明推断为通过。
EN: The public directory's execution result is retained in results/public-replay.json, a minimized result rather than raw logs. Each full invocation recomputes from the actual input. Commit-matched GitHub Actions status is given by the actual GitHub run and cannot be inferred as passed from this document.

ZH: 集成器中的 G 变更控制检验不一致数值会被拒绝；它不是另一个支持域扫描算法，也不保证拒绝人为协调伪造的全部字段。全量入口的证据来自同次新执行的削角扫描，而不是仅靠回执字段一致性。
EN: The integrated G-mutation control checks rejection of inconsistent numbers; it is not another support-domain sweep and does not guarantee rejection of deliberately coordinated forgery of every field. Evidence in the full entry point comes from its fresh cap sweep, not receipt-field consistency alone.
