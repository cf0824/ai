# 从仓库拉取 带有 python 3.7 的 Linux 环境
FROM python:3.7

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

# 创建 pmadmin 文件夹并将其设置为工作目录
RUN mkdir /app
WORKDIR /app
# 安装crontab
#RUN echo "deb http://mirrors.aliyun.com/debian/ buster main non-free contrib" > /etc/apt/sources.list && \
#    echo "deb http://mirrors.aliyun.com/debian-security buster/updates main" >> /etc/apt/sources.list && \
#    echo "deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib" >> /etc/apt/sources.list
# 更换镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update && apt-get install  -y cron
# 更新 pip
RUN pip install pip -U -i https://pypi.tuna.tsinghua.edu.cn/simple
# 将 requirements.txt 复制到容器的 pmadmin 目录
ADD requirements.txt /app/
# 安装库
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-dependencies
# 将当前目录复制到容器的 code 目录
ADD ./ /app/
