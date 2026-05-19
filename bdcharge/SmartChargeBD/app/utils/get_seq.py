import datetime
from django.db import connection
from django.db import transaction

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'SmartChargeBD.settings'

# 根据配置获取序列号
@transaction.atomic
def Get_SeqNo( seqname ):
    cur = connection.cursor()  # 创建游标
    sql = "select current_val, curval_len, max_val, expression from sys_sequence where seq_name=%s for update"
    cur.execute(sql, seqname)
    row = cur.fetchone()
    if not row:
        connection.commit()
        cur.close()
        return None
    curval = row[0]
    curvallen = row[1]
    maxval = row[2]
    express = row[3]
    if curval >= maxval:
        sql_max = "update sys_sequence set current_val=begin_val where seq_name = %s"
        cur.execute(sql_max, seqname)
    sql = "update sys_sequence set current_val = current_val + increment_val where seq_name = %s"
    cur.execute(sql, seqname)
    cur.close()
    ret = express
    if '[YYYY]' in ret:
        ret = ret.replace('[YYYY]', datetime.datetime.now().strftime('%Y'))
    if '[YYYYMM]' in ret:
        ret = ret.replace('[YYYYMM]', datetime.datetime.now().strftime('%Y%m'))
    if '[YYYYMMDD]' in ret:
        ret = ret.replace('[YYYYMMDD]', datetime.datetime.now().strftime('%Y%m%d'))
    if '[SEQNO]'  in ret:
        strcurval=str(curval)
        if curvallen:
            strcurval =  strcurval.rjust(curvallen, '0')
        ret = ret.replace('[SEQNO]', strcurval )
    print(f'ret:{ret}')
    return ret


if __name__ == '__main__':
    Get_SeqNo("COMMON")
    # order = '0000000015'
    # a = hex(int(order)).lstrip('0x').zfill(8)
    # print(a)
    # b = 'WF_CD_2024_0000000015'
    # print(b[-10:])
    # print(int('ffffffff', 16))
