#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeAdmin 
@File    ：handle_qrcode.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/4/1 15:52 
@Description :
'''
import base64
import sys
import os
import requests
from admin_cfg.settings import BASE_DIR
import datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
from admin_app.utils import uploadUtil
from admin_app.utils.dbFunc import MySQLDB

from admin_app.utils import MyLog

file_name = os.path.basename(__file__)[:-3]
file_path = os.path.dirname(__file__)
log = MyLog.MyLog(__file__, file_name + '.log', file_path).logger

upload_obj = uploadUtil.TencentCOS(log)

def generate_qrcode(data, text, save_dir):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # 创建画布
    width, height = img_qr.size
    new_height = height + 60
    img_canvas = Image.new('RGB', (width, new_height), color='white')
    img_canvas.paste(img_qr, (0, 0))

    # 添加文字
    draw = ImageDraw.Draw(img_canvas)
    try:
        # font = ImageFont.truetype("simhei.ttf", 50)
        font = ImageFont.truetype("simsunb.ttf", 40)
    except:
        font = ImageFont.load_default()

    # 使用 textbbox 计算文字尺寸
    text_bbox = draw.textbbox((0, 0), text, font=font)
    print(text_bbox)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (width - text_width) // 2
    text_y = height

    draw.text((text_x, text_y), text, fill="black", font=font)
    time_stamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{text}_{time_stamp}.png"
    file_path = os.path.abspath(os.path.join(save_dir, filename))
    img_canvas.save(file_path)

    return file_path


def upload_to_tencent(file, path):
    try:
        res = upload_obj.tencent_cos_upload(file, path)
        log.info(f'{res}')
        db = MySQLDB()
        qr_no = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
        data = {
            'qr_no': qr_no,
            'file_name': res[0].get('fileName'),
            'encrypt_name': res[0].get('saveName'),
            'local_path': file,
            'cos_path': res[0].get('filePath'),
            'cos_url': res[0].get('fileUrl'),
            'upload_time': datetime.datetime.now()
        }
        db.insert('s_qrcode_info', data)
        return data
    except Exception as e:
        log.error(f'上传失败：{e}', exc_info=True)


def generate_miniprogram_code(save_dir, args):
    from admin_app.utils.wx import get_access_token, generate_qrcode_safely
    token = get_access_token()
    token = token.get('access_token')
    result = generate_qrcode_safely(token, args)
    pileNum = str(args.get('pileNum'))
    port = args.get('port')
    filename = f'{pileNum}-{port}.png'
    file_path = os.path.abspath(os.path.join(save_dir, filename))
    if result:
        with open(file_path, 'wb') as f:
            f.write(result)

        return file_path
    else:
        return None



def add_text_below_qrcode(qrcode_path, output_path, text,
                          font_path="msyh.ttc", font_size=65,
                          text_color="#2C2C2C", padding=15,
                          bg_color=(255, 255, 255, 0)):
    """
    在小程序码下方添加独立文字区域（自动扩展画布）

    参数：
    qrcode_path: 小程序码路径
    output_path: 输出路径
    text: 要添加的文字
    font_path: 中文字体路径
    font_size: 字体大小
    text_color: 文字颜色
    padding: 文字区域上下边距
    bg_color: 扩展区域背景色（默认透明）
    """
    # 打开原始小程序码
    qrcode_img = Image.open(qrcode_path).convert("RGBA")
    qr_width, qr_height = qrcode_img.size

    # 创建字体对象
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise Exception("字体文件加载失败，请使用正确的中文字体路径")

    # 计算文字所需高度
    text_bbox = font.getbbox(text)
    text_height = text_bbox[3] - text_bbox[1] + 2 * padding  # 总扩展高度

    # 创建新画布（原高度+文字区域高度）
    new_height = qr_height + text_height
    new_img = Image.new("RGBA", (qr_width, new_height), bg_color)

    # 合并图片（原始二维码在上部）
    new_img.paste(qrcode_img, (0, 0))

    # 准备绘制文字
    draw = ImageDraw.Draw(new_img)

    # 计算文字位置（居中于扩展区域）
    text_y = qr_height + padding  # 从扩展区域顶部开始
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (qr_width - text_width) // 2

    # 添加文字描边（增强可读性）
    border = 1
    stroke_color = (0, 0, 0, 255) if bg_color[3] == 0 else (255, 255, 255, 255)

    for dx in [-border, border]:
        for dy in [-border, border]:
            draw.text((text_x + dx, text_y + dy), text, font=font, fill=stroke_color)

    # 添加主文字
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # 保存结果
    new_img.save(output_path)
    log.info(f"生成成功：文字区域独立显示在二维码下方 | 输出文件：{output_path}")

if __name__ == '__main__':

    # data = '123456'
    # text = '100002-00'
    # img_path = BASE_DIR + '/file/port_qrcode/'
    # print(img_path)
    # res = generate_qrcode(data=data, text=text, save_dir=img_path)
    #
    # print(res)
    # filename = os.path.basename(res)
    # print(filename)
    # upload_to_tencent(res, 'qrcode')
    add_text_below_qrcode(
        qrcode_path="qrcode_体验版.jpg",
        output_path="带文字的小程序码.png",
        text="100002-00",
        font_path="simsunb.ttf",
        font_size=70,
        text_color="#2C2C2C",  # 深灰色文字
        padding=20,  # 文字上下边距
        bg_color=(255, 255, 255, 0)  # 透明背景
    )
