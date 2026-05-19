# 从仓库拉取 带有 python 3.7 的 Linux 环境
FROM python:3.7

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

# 替换软件包源
#COPY sources.list .
#RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && mv sources.list /etc/apt/

# 创建 app 文件夹并将其设置为工作目录
RUN mkdir /app
WORKDIR /app
# 安装crontab
#RUN apt-get update && apt install libgl1-mesa-glx -y
# 更新 pip
RUN pip install pip -U -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装库
ADD requirements.txt /app/
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 将当前目录复制到容器的 code 目录
ADD ./ /app/
