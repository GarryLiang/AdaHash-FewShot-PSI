# AdaHash-FewShot-PSI: Adaptive Small-sample Hash PSI Protocol

> **Small-sample Scenario Adaptive Noise Hash Bucket TPSI Protocol under MP-SPDZ Framework**

本项目实现了一种针对小样本场景的自适应噪声哈希分桶隐私集合求交（PSI）协议。该协议基于 MP-SPDZ 框架执行，旨在解决在小数据集规模下，传统 PSI 协议效率低或安全性冗余的问题，通过自适应调整噪声和哈希策略，在保证安全性的前提下提升计算效率。

## 📖 项目简介 (Introduction)

在隐私保护计算领域，当参与方的数据量较小（Few-shot/Small-sample）时，标准的 PSI 协议往往因为通信开销过大或常数项过高而显得不够高效。

`AdaHash-FewShot-PSI` 提出了一种改进方案：
- **自适应噪声机制**：根据样本规模动态调整填充噪声，平衡安全性与性能。
- **哈希分桶优化**：利用优化的哈希策略减少不必要的比较操作。
- **MP-SPDZ 实现**：核心逻辑使用 `.mpc` 语言编写，运行于业界标准的 MP-SPDZ 多方安全计算框架之上。

## 🛠️ 环境依赖 (Prerequisites)

在运行本项目之前，请确保你的环境中已安装以下组件：

1. **MP-SPDZ 框架**:
   - 本项目核心代码依赖于 MP-SPDZ。请参照 [MP-SPDZ 官方文档](https://github.com/data61/MP-SPDZ) 进行源码编译安装。
   - 确保 `compile.py` 和 `emulate.x` (或 `player.x`) 等可执行文件在你的 PATH 中或已配置好路径。

2. **Python 环境**:
   - Python 3.7+
   - 建议安装 `numpy`, `scipy` 等基础科学计算库用于数据处理和测试脚本运行。
     ```bash
     pip install numpy scipy tqdm
     ```

## 📂 文件结构 (File Structure)

```text
AdaHash-FewShot-PSI/
├── hashpsi.mpc          # 核心 MPC 协议代码 (MP-SPDZ 语法)
├── testhash_10.py       # 自动化测试脚本
├── requirements.txt     # Python 依赖列表
└── README.md            # 项目说明文档
