#!/usr/bin/python
# coding=utf-8
import paramiko
import os
# from unrar import rarfile
from shutil import copyfile

def copydir(src, dist):
    folders = os.listdir(src)
    for folder in folders:
        dir = src + '\\' + str(folder)
        files = os.listdir(dir)
        for file in files:
            source = dir + '\\' + str(file)
            deter = dist + '\\' + str(folder) + '\\'+ str(file)
            copyfile(source, deter)

#解压rar文件
# def exrarfile(local):
#     path = local+"dist.rar"
#     path2 = local+"dist\\"
#
#     if not os.path.exists(path):
#         print("文件不存在！")
#     if not os.path.exists(path2):
#         print("目录不存在！")
#
#     rf = rarfile.RarFile(path) # 待解压文件
#     print(path, path2)
#     rf.extractall(path='E:\\')  # 解压指定文件路径
#
#     copydir(path2+'static\\css', local+'static\\css')
#     copydir(path2 + 'static\\js', local + 'static\\js')

def get_sftp(host,port,username,password):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    return sftp,sf

def sftp_put(local,remote):
    if os.path.isdir(local):  # 判断本地参数是目录还是文件
        for f in os.listdir(local):  # 遍历本地目录
            sftp.put(os.path.join(local + f), os.path.join(remote + f))  # 上传目录中的文件
    else:
        sftp.put(local, remote)  # 上传文件

def sftp_upload(host,port,username,password,local,remote):
    sf = paramiko.Transport((host,port))
    sf.connect(username = username,password = password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):#判断本地参数是目录还是文件
            for f in os.listdir(local):#遍历本地目录
                sftp.put(os.path.join(local+f),os.path.join(remote+f))#上传目录中的文件
        else:
            sftp.put(local,remote)#上传文件
    except Exception as e:
        print('upload exception:',e)
    sf.close()



if __name__ == '__main__':
    local = 'E:\\lqkj_admin\\'
    # exrarfile(local)
    os.system('更新版本.bat')
    print('解压成功!')

    host = '192.168.2.174'#主机
    port = 22 #端口
    username = 'admin' #用户名
    password = 'admin2019' #密码

    print(local)
    remote = '/home/admin/lqkj_admin/'#远程文件或目录，与本地一致，当前为linux目录格式
    sftp, sf = get_sftp(host,port,username,password )#获取sftp句柄

    #上传文件夹
    sftp_put(local+'static\\css\\', '/home/admin/lqkj_admin/static/css/')
    print('put css ok')
    sftp_put(local+'static\\js\\', '/home/admin/lqkj_admin/static/js/')
    print('put js ok')
    sftp_put(local+'templates\\', '/home/admin/lqkj_admin/templates/')
    print('put index ok')

    sf.close()

