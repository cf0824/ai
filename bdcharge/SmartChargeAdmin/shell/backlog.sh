#!/bin/sh
echo "--开始备份日志！""$(date +"%Y%m%d%H%M%S")"
yestoday=$(date +"%Y%m%d" -d "-1day")
#将备份文件上传到服务器
cd ${HOME}/lqkj_admin/log
pwd
echo *${yestoday}*.log
gzip *${yestoday}*.log
mv *.gz back
echo "--备份日志成功!"
