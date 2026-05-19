#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""=================================================
@project -> File:  MyCode -> cos.py
@Software:   PyCharm
@Author  :   Mr. Dzy
@Contact :   qq1632236273@163.com
@File    :   cos.py
@Time    :   2024/4/3 11:17
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
@License :   (C) Copyright 2023-- dzy
=================================================="""
import hashlib
import os
import time
import uuid
from datetime import datetime
from django.core.files.uploadedfile import InMemoryUploadedFile

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from admin_cfg.settings import TENCENT_OSS_CONFIG

OSS_CONFIG = TENCENT_OSS_CONFIG


class TencentCOS:
    def __init__(self, log):
        self.log = log
        self.secret_id = OSS_CONFIG.get('TENCENT_OSS_SECRET_ID')
        self.secret_key = OSS_CONFIG.get('TENCENT_OSS_SECRET_KEY')
        self.bucket = OSS_CONFIG.get('TENCENT_OSS_BUCKET')
        self.region = OSS_CONFIG.get('TENCENT_OSS_REGION')
        self.token = OSS_CONFIG.get('TENCENT_OSS_TOKEN')
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

    def get_obj_url(self, bucket, key):
        return self.client().get_object_url(bucket, key)

    def get_file_list(self, prefix=''):
        response = self.client().list_objects(Bucket=self.bucket,
                                              Prefix=prefix,
                                              Delimiter='/',
                                              EncodingType='url')
        if 'Contents' in response.keys():
            return [b['Key'] for b in response['Contents']]
        else:
            return []

    def delete(self, obj_name):
        response = self.client().delete_object(Bucket=self.bucket,
                                               Key=obj_name)

    def tencent_cos_upload(self, files, path):
        _uploads = []
        if isinstance(files, list):
            for file in files:
                _upload = self.read_build_file(file, path)
                _uploads.append(_upload)
        else:
            _uploads.append(self.read_build_file(files, path))
        return _uploads  # 返回列表

    def read_build_file(self, file, dir):
        _upload = {}  # 在里面定义，每次都可以刷新，不然返回的结果都一样
        today = datetime.strftime(datetime.now(), '%Y%m%d')
        uuid_str = uuid.uuid4().hex
        self.log.info(file)
        self.log.info(type(file))
        # upload_name = secure_filename(file.filename)
        # file_name = file.name

        if isinstance(file, InMemoryUploadedFile):
            file_name = file.name
            blob = file.read()
        else:
            file_name = os.path.basename(file)
            with open(file, 'rb') as f:
                blob = f.read()
        file_suffix = os.path.splitext(file_name)[1]

        # file_type = file.content_type

        type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            # 其他扩展名补充...
        }
        file_type = type_map.get(file_suffix, 'application/octet-stream')

        save_name = uuid_str + file_suffix
        file_path = 'tencent_oss/%s/%s/%s' % (dir, today, save_name)  # tencent_oss/path/年-月-日/filename

        #

        file_size = len(blob)
        _upload['fileName'] = file_name
        _upload['saveName'] = save_name
        _upload['fileSuffix'] = file_suffix
        _upload['fileType'] = file_type
        _upload['filePath'] = file_path
        _upload['fileSize'] = file_size
        self.log.info(f'_upload: {_upload}')
        response = self.client().put_object(
            Bucket=self.bucket,
            Body=blob,  # 上传的文件对象
            Key=file_path,  # 带路径的文件名，无须/开头
            CacheControl='no-cache'
        )
        self.log.info(f'response: {response}')
        file_url = self.get_obj_url(self.bucket, file_path)
        _upload['fileUrl'] = file_url
        return _upload

    def do_put_object(self, body, file_name):
        today = datetime.strftime(datetime.now(), '%Y%m%d')
        file_path = 'tencent_oss/%s/%s' % (today, file_name)  # tencent_oss/年-月-日/filename
        self.client().put_object(
            Bucket=self.bucket,
            Body=body,  # 上传的文件对象
            Key=file_path,  # 带路径的文件名，无须/开头
            # CacheControl='no-cache',
            # ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        file_url = self.get_obj_url(self.bucket, file_path)
        return file_url


class LocalUploader:
    def __init__(self, storage_path="uploads", user_md5_prefix=True, use_time_sub_directory=True):
        self.http_url = flaskConfig.API_URL
        self.storage_path = storage_path
        self.user_md5_prefix = user_md5_prefix
        self.use_time_sub_directory = use_time_sub_directory

    def local_upload(self, files):
        _uploads = []
        if isinstance(files, list):
            for file in files:
                _upload = self.read_build_file(file)
                _uploads.append(_upload)
        else:
            _uploads.append(self.read_build_file(files))
        return _uploads  # 返回列表

    def read_build_file(self, file):
        _upload = {}
        file_name = file.filename
        file_content_type = file.content_type
        # 文件扩展名
        filename_ext = os.path.splitext(file_name)[1]

        # 获取文件内容到变量中
        file_info = file.stream.read()
        file_size = len(file_info)
        # 是否设置当前需要存储以时间戳为名称的目录
        time_path = time.strftime("%Y-%m-%d", time.gmtime(time.time())) if self.use_time_sub_directory else ""

        # 判断存储目录是否存在，如果不存在则创建目录
        absolute_path = os.path.join(self.storage_path, time_path)
        os.makedirs(absolute_path, exist_ok=True)

        # 定义新的文件路径
        if self.user_md5_prefix:
            # 生成md5值的文件名
            m2 = hashlib.md5()
            m2.update(file_info)
            file_md5 = m2.hexdigest()
            new_file_name = file_md5 + filename_ext
        else:
            new_file_name = file_name

        new_file_path = os.path.join(absolute_path, new_file_name)
        new_file_path = new_file_path.replace('\\', '/')
        if not os.path.exists(new_file_path):
            # 写入本地指定目录
            with open(new_file_path, 'wb') as f:
                f.write(file_info)

        # 指定文件可被访问的 Url
        base_url = os.path.join(self.storage_path, time_path, new_file_name)
        http_url = f"{self.http_url}/{base_url}"
        file_url = http_url.replace('\\', '/')
        _upload['fileName'] = file_name
        _upload['saveName'] = new_file_name
        _upload['fileSuffix'] = filename_ext
        _upload['fileType'] = file_content_type
        _upload['filePath'] = new_file_path
        _upload['fileSize'] = file_size
        _upload['fileUrl'] = file_url
        return _upload
