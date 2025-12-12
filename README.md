## Object-Oriented Programming

------
### 该仓库为笔者为实现开源qlib项目的数据预处理拓展的仓库

##### Qlib

https://github.com/microsoft/qlib

pdf：[2009.11189](https://arxiv.org/pdf/2009.11189)

------

**RD-Agent（Research & Development Agent）** 是微软开源的一个 **基于大语言模型（LLM）驱动的科研与量化投资研发智能体系统**。

---

**流程**

```bash
# clone仓库
git clone https://github.com/microsoft/qlib.git

# 创建虚拟环境
python3 -m venv myqlib

source myqlib/bin/activate

# 安装工具
pip install numpy

（提速：pip install numpy -i https://pypi.tuna.tsinghua.edu.cn/simple）

 pip install --upgrade cython -i https://pypi.tuna.tsinghua.edu.cn/simple
 
# 安装依赖
pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 得到数据
python scripts/get_data.py qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn

# 运行
cd qlib/examples/

qrun benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml


```


