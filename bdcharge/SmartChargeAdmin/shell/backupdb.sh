#!/bin/sh
echo "--开始备份数据库！""$(date +"%Y%m%d%H%M%S")"
db_user="lqkj"
db_passwd="LQkj666_2019"
db_name="lqkj_db"
filename="$(date +"%Y%m%d%H%M%S")"".sql"
mysqldump -h192.168.2.174 -p3306 -u${db_user} -p${db_passwd} ${db_name} > ${HOME}/backup/${filename}
echo "--mysql数据库备份成功"
gzip ${HOME}/backup/${filename}
echo "--备份文件压缩成功"


#将备份文件上传到服务器
cd ${HOME}/backup
export putfile=${filename}.gz
ftp -v -n 192.168.2.18<<EOF
user root root
passive on
binary
put ${putfile}
passive off
bye
EOF
echo "--FTP上传文件成功!"
