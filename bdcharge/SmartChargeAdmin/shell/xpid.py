#通过采购给的excel补全焊点数量, 不支持xls格式

import openpyxl
import binascii

binfile="C:\\Users\\Administrator\\Desktop\\HPLC_LN_HF_191037__00001.TXT"
file_name="C:\\Users\\Administrator\\Desktop\\芯片ID.xlsx"
def duemain():

    wb = openpyxl.load_workbook(filename=file_name, read_only=False)
    ws = wb.active

    try:
        i=0
        #打开文件
        print('打开文件')
        fp=open(file=binfile, mode='r',encoding='utf-8',errors='ignore')
        fileline=fp.read(4584888)
        xpid = binascii.hexlify(fileline.encode()).decode()
        for item in xpid.split('01020102485a'):
            # print(item)
            i=i+1
            xpid='01020102485a'+item
            print('xpid=',xpid)
            # if i>100:
            #     break
            ws.append(xpid)
        fp.close()
        wb.close()
        print('总记录数：', i)
    except Exception as ex:
        print(ex)

duemain()
