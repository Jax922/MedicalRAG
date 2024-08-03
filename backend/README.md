# Install

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

或者 -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com

# start
conda create --name myenv python=3.10
conda activate myenv(自定义环境名字)
python api.py 
或者vscode点击运行

交互式 API 文档（基于 Swagger UI）：http://127.0.0.1:8000/docs
API 文档（基于 ReDoc）：http://127.0.0.1:8000/redoc