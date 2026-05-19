import datetime
from django.db import connection
from django.db import transaction


# 根据配置获取序列号
def Get_SeqNo( seqname ):
    cur = connection.cursor()  # 创建游标
    sql = "select current_val, curval_len, expression from sys_sequence where seq_name=%s for update"
    cur.execute(sql, seqname)
    row = cur.fetchone()
    if not row:
        connection.commit()
        cur.close()
        return None

    curval = row[0]
    curvallen = row[1]
    express = row[2]
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
    return ret


@transaction.atomic
def Get_SeqNoV2(seqname):
    return Get_SeqNo(seqname)
