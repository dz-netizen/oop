# Qlib 源码阅读与扩展实现分析报告

## 一、项目概述

**项目名称**：Qlib  
**项目地址**：[https://github.com/microsoft/qlib](https://github.com/microsoft/qlib)  
**项目定位**：  
Qlib 是微软开源的一个面向 **人工智能驱动的量化投资研究** 平台，旨在通过 AI 技术赋能量化研究的全流程，包括数据处理、特征构建、模型训练、回测与部署。  

该平台提供了灵活的数据框架、可扩展的建模接口，以及完整的回测与策略执行组件，支持多种机器学习与深度学习范式，如监督学习、市场动态建模和强化学习。

---

## 二、整体架构分析

Qlib 的项目结构主要包括以下几个核心模块：

| 模块 | 作用 | 主要文件 |
|------|------|----------|
| `qlib/data` | 数据层：数据获取、缓存、预处理 | `data.py`, `dataset.py`, `data_handler.py` |
| `qlib/model` | 模型层：机器学习与深度学习模型实现 | `model/gbdt.py`, `model/pytorch_nn.py` |
| `qlib/workflow` | 实验与任务流管理：回测、记录、指标评估 | `workflow/record_temp.py`, `workflow/task/job.py` |
| `qlib/backtest` | 回测框架：模拟策略执行、评估收益 | `backtest/executor.py`, `backtest/account.py` |
| `qlib/contrib` | 扩展模块：外部贡献的策略与模型 | `contrib/model/pytorch_lstm.py` |
| `qlib/utils` | 工具模块：日志、配置、性能计时、缓存等 | `utils/__init__.py`, `utils/time.py` |

模块间关系如下：

数据层 → 特征工程层 → 模型层 → 回测层 → 记录层

---

## 三 扩展实现与自定义相关构思

### 3.1 自定义因子

Qlib 允许用户扩展新的特征（因子）。  
例如定义一个动量与成交量比因子，可以继承 `DataHandler` 实现自定义 `process()` 方法：

定义动量因子（过去 10 日收益率）与成交量比（5 日均量比），可直接集成进 Qlib 数据管线，用于后续训练与回测。

---

### 3.2 混合模型：LSTM + GBDT

Qlib 模型层支持灵活组合。可以融合深度模型与树模型，将时序特征与结构化特征共同建模。  
例如：使用 LSTM 提取序列特征后，将其作为输入传给 GBDT 做非线性回归。

这种设计结合了深度模型的时间建模能力与 GBDT 的泛化能力，在金融预测中效果显著。

---

### 3.3 与 tushare 结合

tushare能够提供相关股票数据信息的接口提供平台，可以将其中一些qlib没有的内容移植扩展到qlib中。
 
---

## 四、Qlib 的运行与回测流程

典型使用流程如下：

1. **数据初始化**  
   下载并准备中国市场数据：  
   `python scripts/get_data.py qlib_data --target_dir ~/.qlib/qlib_data/cn_data`

2. **启动数据服务**  
   `python scripts/qlib_data.py --region cn`

3. **运行实验配置文件**  
   `python scripts/run_task.py examples/benchmarks/LightGBM/workflow_config_lightgbm.yaml`

实验完成后，Qlib 会自动生成记录文件，包括：
- 模型参数与配置；
- 回测结果与绩效指标；
- 可视化收益曲线；
- 日志与中间文件。

---



