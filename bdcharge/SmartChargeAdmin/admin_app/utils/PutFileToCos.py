#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  django_admin -> UploadFile.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   UploadFile.py
@Time    :   2024-06-20 10:28
@Desc    :
             ┏┓       ┏┓
            ┏┛┻━━━━━━━┛┻┓
            ┃    ☃      ┃
            ┃  ┳┛   ┗┳  ┃
            ┃     ┻     ┃
            ┗━┓       ┏━┛
              ┃       ┗━━━━┓
              ┃ 神兽保佑     ┣┓
              ┃　永无BUG！   ┏┛
              ┗┓┓┏━━━┳┓┏━━━┛
               ┃┫┫   ┃┫┫
               ┗┻┛   ┗┻┛
@License :   (C) Copyright 2023-- 河南品码信息科技有限公司
=================================================="""

from admin_app.sys import public
import os
import uuid
from datetime import datetime

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

COS_Bucket_Name = "sc-consum-1257596698"
COS_TOKEN = ""
COS_Region = "ap-nanjing"
COS_Secret_Key = "U8dyDG7mDkA3nLhv0K0Z3MVSXeuDVeij"
COS_Secret_Id = "AKIDe8VhiWAuTqYCfw1u1we9TabP1QddR2Qc"

log = public.logger


class TencentCOS:
    def __init__(self):
        self.secret_id = COS_Secret_Id
        self.secret_key = COS_Secret_Key
        self.bucket = COS_Bucket_Name
        self.region = COS_Region
        self.token = COS_TOKEN
        self.scheme = 'https'
        # 初始化客户端

    def client(self):
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Token=self.token,
            Scheme=self.scheme
        )
        # 返回一个初始化的客户端，后续操作都需要基于这个客户端实例
        return CosS3Client(config)

    def tencent_cos_upload(self, files):
        _uploads = []
        if isinstance(files, list):
            for file in files:
                _upload = self.read_build_file(file)
                _uploads.append(_upload)
        else:
            _uploads.append(self.read_build_file(files))
        return _uploads  # 返回列表

    def read_build_file(self, file):
        _upload = {}  # 在里面定义，每次都可以刷新，不然返回的结果都一样
        today = datetime.strftime(datetime.now(), '%Y%m%d')
        uuid_str = uuid.uuid4().hex
        upload_name = file.name
        file_suffix = os.path.splitext(upload_name)[1]
        file_type = file.content_type
        save_name = uuid_str + file_suffix
        file_path = 'tencent_oss/%s/%s' % (today, save_name)  # tencent_oss/年-月-日/filename
        blob = file.read()
        file_size = len(blob)
        _upload['uploadName'] = upload_name
        _upload['saveName'] = save_name
        # _upload['fileSuffix'] = file_suffix
        _upload['fileType'] = file_type
        # _upload['filePath'] = file_path
        # _upload['fileSize'] = file_size
        self.client().put_object(
            Bucket=self.bucket,
            Body=blob,  # 上传的文件对象
            Key=file_path,  # 带路径的文件名，无须/开头
            CacheControl='no-cache'
        )
        file_url = self.get_download_url(file_path)
        _upload['fileUrl'] = file_url
        return _upload

    def get_download_url(self, file_path):
        # 假设你已经有了腾讯云 COS 的访问域名，通常这个域名会在你的 COS 控制台中给出
        # 例如: https://bucket-APPID.cos.REGION.myqcloud.com
        # 这里需要替换为你的实际域名
        base_url = f"https://{self.bucket}.cos.{self.region}.myqcloud.com"

        # 对象的键（Key），即你在 COS 中存储的文件路径
        # 例如: 'folder/subfolder/myfile.txt'
        # 这里需要替换为你的实际文件路径
        download_url = f"{base_url}/{file_path}"
        # 你可以根据需要添加签名等参数，以实现私有文件的下载
        # 但对于公开文件，直接返回上述 URL 即可

        return download_url
