#获取流程申请数据并插入流程路线表

import time
import datetime
import pymysql
import logging
import os
import json

#日志初始化,日志名称
localhome="/home/admin/lqkj_admin/"
global logger, fh
logger = logging.getLogger(str(os.getpid()))
def loger_init( ):
    #日志初始化
    now_time = datetime.datetime.now().strftime('%Y%m%d')
    logger = logging.getLogger(str(os.getpid()))
    logger.setLevel(logging.INFO)
    logname = os.path.basename(__file__).split('.py')[0]
    if os.path.exists(+'log/'):
        log_file_temp = localhome+'log/'+logname+'_'+now_time+'.log'
    else:
        log_file_temp = logname + '_' + now_time + '.log'
    # print(log_file_temp)
    fh = logging.FileHandler(log_file_temp)  # 定义一个写文件的handler
    fh.setLevel(logging.INFO)  # 设置写文件的等级
    fh_formatter = logging.Formatter(
        '[%(levelname)-5s] [%(filename)-12s line:%(lineno)-4d] [%(asctime)s] [%(process)-7d] [%(message)s]')  # 设置输出格式
    fh.setFormatter(fh_formatter)  # 将输出格式设置给handler
    #print('public',logger)
    if  not logger.handlers:
        logger.addHandler(fh)  # 将handler加入logger
    return logger, fh


#判断where条件是否成立
def whereCheck(where_list, value_dict):
    print('where',where_list,value_dict)
    for where in where_list:
        filed_value = value_dict.get(where['a'])
        if not filed_value:
            return False
        to = where['to']
        b = where['b']
        flag = False
        for bitem in b:
            if type(filed_value)==int:
                bitem=int(bitem)
            if to == 'equare':
                if filed_value == bitem:
                    flag = True
                    break
            elif to == 'lower':
                if filed_value < bitem:
                    flag = True
                    break
            elif to == 'upper':
                if filed_value > bitem:
                    flag = True
                    break
        if not flag:
            return False

    return True


# 插入list表一条数据并返回插入后的id
def insert_workflow_node_list(cur,kvs):
    # kvs = {
    #     'wf_id': wf_id,
    #     'wf_type': wf_type,
    #     'condition': wf_cfg,
    #     'gl_id': gl_id,
    #     'node_prev': node_prev,
    # }
    knames = ','.join(kvs.keys())
    vnames = ','.join(['%s' for i in range(len(kvs))])
    sql = "insert into sys_workflow_node_list(%s) value(%s)" % (knames, vnames)
    print('sql=', sql % tuple(kvs.values()))
    try:
        cur.execute(sql, tuple(kvs.values()))
    except pymysql.err.IntegrityError:
        pass
    return cur.lastrowid



# 递归插入list表
def insert_list_table_dfs(cur,form_id, operate_orgid, gl_id,order_number,value_dict,old_prev=0,new_prev=0):
    sql = "select wf_id,form_id,wf_type,wf_prev,wf_next,wf_cfg,wf_notes from sys_workflow_node_cfg " \
          "where form_id='%s' and wf_state='1' and wf_prev=%s" % (form_id,old_prev)
    cur.execute(sql)
    rows=cur.fetchall()
    for wf_id,form_id,wf_type,wf_prev,wf_next,wf_cfg,wf_notes in rows:
        wf_cfg=eval(wf_cfg)
        user_ids=wf_cfg['auditPerson']
        where=wf_cfg['where']
        # 判斷條件是否成立
        if wf_type == 'branch':
            flag = whereCheck(where, value_dict)
            print('判斷條件', flag)
            if not flag:
                continue
        for user_id in user_ids:
            if user_id=='org_leader':  #部门负责人审核
                sql="select distinct b.USER_ID from sys_org a, sys_user_org b, sys_user c " \
                    "where a.ORG_ID=b.ORG_ID and b.USER_ID=c.USER_ID and c.STATION='104' and a.ORG_SPELL ='%s'" % (operate_orgid)
                cur.execute(sql)
                rows_leader = cur.fetchall()
                for item in rows_leader:
                    row_user= item[0]
                    new_prev = insert_workflow_node_list(cur, {
                        'wf_id': wf_id,
                        'wf_type': wf_type,
                        'node_prev': new_prev,
                        'gl_id': gl_id,
                        'update_date': datetime.datetime.now(),
                        'node_state': '0',
                        'title': wf_notes,
                        'user_id': row_user,
                        'order_number': order_number,
                        'form_id': form_id
                    })
            else: #指定的审核用户
                new_prev = insert_workflow_node_list(cur, {
                    'wf_id': wf_id,
                    'wf_type': wf_type,
                    'node_prev': new_prev,
                    'gl_id': gl_id,
                    'update_date': datetime.datetime.now(),
                    'node_state': '0',
                    'title':wf_notes,
                    'user_id': user_id,
                    'order_number':order_number,
                    'form_id':form_id
                })
        ret=insert_list_table_dfs(cur, form_id, operate_orgid, gl_id,order_number, value_dict,wf_id, new_prev)
        if ret:
            new_prev=ret
    return new_prev


# 根据表名获取未插入流程路线表的关联业务id
def get_glid_list_by_tablename(cur,table_name):
    sql = "select id, order_number, user_id, department from %s where apply_state='0'" % table_name
    cur.execute(sql)
    rows = cur.fetchall()
    gl_id_list=[]
    order_number_list=[]
    user_id_list=[]
    org_id_list = []
    for row in rows:
        gl_id_list.append(row[0])  # 关联业务表的id
        order_number_list.append(row[1])
        user_id_list.append(row[2])
        org_id_list.append(row[3])
    return gl_id_list, order_number_list, user_id_list, org_id_list

# 获取form值字典
def getValueDict(cur,form_id,table_name,gl_id):
    #查询字段类型
    # value_type_dict={}
    # sql="select column_name,data_type from information_schema.columns where table_schema='lqkj_db' and table_name='%s'"%table_name
    # cur.execute(sql)
    # rows=cur.fetchall()
    # for column_name,data_type in rows:
    #     value_type_dict[column_name]=data_type
    # print('value_type_dict=',value_type_dict)

    #获取查询SQL
    sql="select selsql from sys_workflow_tran where form_id=%s and statue='1'"
    cur.execute(sql, form_id)
    row=cur.fetchone()
    filed_name_list = []
    if row and row[0]:
        sql = row[0] % (gl_id)
        for field_id in sql.split('select')[1].split('from')[0].split(','):
            filed_name_list.append(field_id.strip())
    else:
        # 获取记录字段名列表
        sql = "select field_id from sys_form_cfg_fieldlist where form_id='%s' and comp_type in ('textarea', 'input', 'datetime', 'select', 'radio', 'date')" % (
        form_id)
        cur.execute(sql)
        rows = cur.fetchall()
        for field_id, in rows:
            filed_name_list.append(field_id)
        sql = "select %s from %s where id=%s" % (','.join(filed_name_list), table_name, gl_id)

    print('get sql=', sql)
    filed_dict={}
    cur.execute(sql)
    row = cur.fetchone()
    for i in range(len(row)):
        filed_dict[filed_name_list[i]]=row[i]
        # if value_type_dict[filed_name_list[i]]=='int':
        #     filed_dict[filed_name_list[i]] = int(row[i])
    print('filed_dict=',filed_dict)
    return filed_dict


def main():
    # 连接数据库
    try:
        mysql_conn = pymysql.Connect(
            host='192.168.2.174',
            port=3306,
            user='lqkj',
            passwd='LQkj666_2019',
            db='lqkj_db',
            charset='utf8')
        cur = mysql_conn.cursor()
    except Exception as e:
        print("MySql数据库连接失败!" + str(e))
        return -1

    # 流程列表对应关系
    # flow_list_tran = [
    #     {
    #         'form_id': '10021',
    #         'table_name': 'shang_test'
    #     }
    # ]
    # 查詢流程列表对应关系
    flow_list_tran=[]
    sql="select form_id,table_name from sys_workflow_tran where statue='1'"
    cur.execute(sql)
    rows=cur.fetchall()
    for form_id,table_name in rows:
        flow_list_tran.append({
            'form_id':form_id,
            'table_name':table_name
        })

    # 开始获取并插表
    for flow in flow_list_tran:
        #查询代插入的业务id列表
        gl_id_list,order_number_list,user_id_list, org_id_list=get_glid_list_by_tablename(cur,flow['table_name'])
        #递归插入list表
        for i,gl_id in enumerate(gl_id_list):
            # 获取字段字典
            value_dict=getValueDict(cur, flow['form_id'], flow['table_name'], gl_id)
            #插入第一条用户申请记录
            insert_workflow_node_list(cur, {
                'wf_id':'0',
                'wf_type': 'apply_user',
                'node_prev': '-1',
                'gl_id': gl_id,
                'update_date': datetime.datetime.now(),
                'node_state': '0',
                'title': '发起申请',
                'user_id': user_id_list[i],
                'org_id': org_id_list[i],
                'order_number': order_number_list[i],
                'form_id':flow['form_id']
            })
            # 递归插入list表
            insert_list_table_dfs(cur, flow['form_id'], org_id_list[i], gl_id,order_number_list[i],value_dict)
    mysql_conn.commit()
    mysql_conn.close()

#持续运行
if __name__ == '__main__':
    while True:
        main()
        time.sleep(10)
