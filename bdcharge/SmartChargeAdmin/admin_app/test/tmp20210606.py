import pymysql

try:
    mysql_conn = pymysql.Connect(
        host='119.27.169.45',
        port=3306,
        user='root',
        passwd='Pinma_2020',
        db='pm_admin_pure',
        autocommit=1,
        charset='utf8')
    cursor = mysql_conn.cursor()
except Exception as e:
    print("MySql数据库连接失败!" + str(e))
    exit(-1)


def get_quota_level(quota_key, score):
    sql = "select min,max,level from wh_quota_level where quota_key=%s"
    cursor.execute(sql, quota_key)
    rows = cursor.fetchall()
    detail = []
    for min, max, level in rows:
        detail.append({
            'min': min,
            'max': max,
            'level': level
        })
    for item in detail:
        if score >= item['min'] and score <= item['max']:
            return item['level'],detail
    return None,detail

score = 24
level,detail = get_quota_level('trade_real', score)
print(level,detail)



# a = [
#     {'key':'a','value':1},
#     {'key':'b','value':2},
#     {'key':'c','value':None}
# ]
#
# res = sum(list(map(lambda x:x['value'] if x['value'] else 0,a)))
# print(res)

# s = '客户稳定xxx,'
# tmp = '得分%s-%s分为%s段，'
# for item in detail:
#     s+=tmp%(item['min'],item['max'],item['level'])
#
# s += '该xxx，得分%s,位于%s段。'%(score,level)
#
# print(s)


a = 'a'
b = 'b'
print(ord(b)-ord(a))