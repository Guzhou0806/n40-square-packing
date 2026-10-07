# ZH: 完整复现
# EN: Complete reproduction

ZH: 使用 x86_64 Linux 或 WSL、Python 3.11 及以上、Rust/Cargo 1.98.0 和 C 链接器。建议至少 4 GB 可用内存；四进程运行。Python 部分仅使用标准库。先安装工具链，再下载 Cargo.lock 固定的 30 个依赖；每个下载均核对 SHA-256。
EN: Use x86_64 Linux or WSL, Python 3.11 or later, Rust/Cargo 1.98.0 and a C linker. At least 4 GB of available memory is recommended, with four workers. Python uses only its standard library. Install the toolchain first, then download the 30 Cargo.lock-pinned dependencies, checking each SHA-256.

```sh
rustup toolchain install 1.98.0 --profile minimal
export RUSTUP_TOOLCHAIN=1.98.0
python3 -B verifier/prepare.py --runtime /tmp/n40-replay
python3 -B verifier/run.py --runtime /tmp/n40-replay --workers 4
```

ZH: 运行目录必须新建且不在仓库内；重复运行使用另一个新目录。准备步骤联网，完整验证步骤强制 Cargo 离线，重新编译、执行 Rust 测试、五组节点、所有削角上界和对抗控制；不读取已提交结果来决定通过。可在准备结束后关闭网络再运行验证。
EN: Use a new runtime directory outside the repository and a different directory for each repeat. Preparation uses the network; full verification forces Cargo offline, rebuilds, runs Rust tests, five node groups, every cap bound and adversarial controls. Committed results are not used to decide acceptance. Networking may be disabled after preparation.

ZH: 禁止 Python -O、断言关闭、fast-math、未经审查的 Rust 编译标志和编译器包装器。任何缺行、超时、失败、未决叶子或阈值不足都会失败；原始输出及退出码保存在运行目录的 replay 中。
EN: Python -O, disabled assertions, fast-math, unreviewed Rust compiler flags and compiler wrappers are prohibited. Missing rows, timeouts, failures, unresolved leaves and insufficient thresholds fail closed; raw outputs and exit codes are retained in the runtime's replay directory.

ZH: SHA256SUMS 固定公开文件字节；它自身不列入摘要。所有输入小数按原始十进制有理数解析，方向和收费比较使用精确分数。
EN: SHA256SUMS pins public file bytes, excluding itself. Input decimals are parsed as literal decimal rationals; directions and charge comparisons use exact fractions.

ZH: x86_64、仓库外的新运行目录和干净构建环境是调用者必须满足的前提。入口拒绝常见编译标志与包装器，但不隔离全部环境变量或上级 Cargo 配置；调用者还须排除目标专用 rustflags、RUSTC 替换及未审查的 Cargo 配置。这里不宣称防御能控制环境的恶意执行者。
EN: x86_64, a fresh runtime directory outside the repository and a clean build environment are caller preconditions. The entry point rejects common compiler flags and wrappers but does not isolate every environment variable or ancestor Cargo configuration; callers must also exclude target-specific rustflags, RUSTC substitution and unreviewed Cargo configuration. No defence against a malicious operator controlling the environment is claimed.
