from django.db import connection
import datetime
from admin_app.sys import public
###########################################################################################################
#数据库公共操作流程
#add by litz, 20200509
#
###########################################################################################################

#根据用户ID获取用户名称
def get_username( userid ):
    # 根据user_id获取user_name
    sql = "select user_name from sys_user where user_id=%s"
    cur = connection.cursor()  # 创建游标
    cur.execute(sql, userid)
    row = cur.fetchone()
    cur.close()
    if row:
        return row[0]
    else:
        return ''

#根据配置获取序列号
def Get_SeqNo( seqname ):

    cur = connection.cursor()  # 创建游标

    sql = "select current_val, curval_len, expression from sys_sequence where seq_name=%s for update"
    cur.execute(sql, seqname)
    row = cur.fetchone()

    if not row:
        connection.commit()
        cur.close
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


# 递归获取机构树
def _get_org_tree_dfs( cur, above_org_id, org_id_name='id', org_name_name='label'):
    log = public.logger
    OrgTreeData = []
    sql = "select org_id, org_name from sys_org where above_org_id='%s' and org_state='1' "  % ( above_org_id )
    # log.info("获取机构信息列表:" + sql, extra={'ptlsh': public.req_seq})
    cur.execute(sql)
    rows = cur.fetchall()
    for item in rows:
        orginfo = {}
        org_id = str(item[0])
        orginfo[org_id_name] = org_id
        orginfo[org_name_name] = item[1]
        orginfo['disabled'] = True
        tempchild = _get_org_tree_dfs(cur, org_id, org_id_name, org_name_name)
        if len(tempchild) > 0:
            orginfo['children'] = tempchild
        OrgTreeData.append(orginfo)
    # log.info("OrgTreeData" + str(OrgTreeData))
    # 返回结果
    return OrgTreeData


def _tmp_set_org_power_dfs(tree_item):
    tree_item['disabled'] = False
    children = tree_item.get('children')
    if children:
        for item in children:
            _tmp_set_org_power_dfs(item)


# 当前节点有权限或下级有权限就保留，否则删除；own_org_ids节点和其下级节点有编辑权限
def _org_list_format_dfs_bak(tmp_tree, own_org_ids, org_id_name, org_name_name):
    log = public.logger
    log.info(f"tmp_tree={tmp_tree}")
    log.info(f"own_org_ids={own_org_ids}")
    all_flag = False
    del_index = []
    for i, item in enumerate(tmp_tree):
        flag1, flag2 = False, False
        if str(item[org_id_name]) in own_org_ids:
            # 遍历下级并设置可编辑权限(包括当前级)
            _tmp_set_org_power_dfs(item)
            flag1 = True
        children = item.get('children')
        log.info(f'children={children}')
        # 如果当前节点已有权限就不再遍历子节点了（默认都有权限）
        if not flag1 and children:
            flag2 = _org_list_format_dfs(children, own_org_ids, org_id_name, org_name_name)
            if not flag2:
                del item['children']
        log.info(f'id={item[org_id_name]},flag1={flag1},flag2={flag2}')
        if not flag1 and not flag2:
            # del tmp_tree[i]
            del_index.append(i)
        else:
            all_flag = True
    del_index.sort(reverse=True)
    for i in del_index:
        del tmp_tree[i]
    return all_flag


# 20221223 当前节点有权限或下级有权限就保留，否则删除；own_org_ids节点有编辑权限
def _org_list_format_dfs(tmp_tree, own_org_ids, org_id_name, org_name_name):
    log = public.logger
    log.info(f"tmp_tree={tmp_tree}")
    log.info(f"own_org_ids={own_org_ids}")
    all_flag = False
    del_index = []
    for i, item in enumerate(tmp_tree):
        flag1, flag2 = False, False
        if str(item[org_id_name]) in own_org_ids:
            # 并设置当前级可编辑权限
            item['disabled'] = False
            flag1 = True
        children = item.get('children')
        log.info(f'children={children}')
        # 遍历子节点
        if children:
            flag2 = _org_list_format_dfs(children, own_org_ids, org_id_name, org_name_name)
            if not flag2:
                del item['children']
        log.info(f'id={item[org_id_name]},flag1={flag1},flag2={flag2}')
        if not flag1 and not flag2:
            del_index.append(i)
        else:
            all_flag = True
    del_index.sort(reverse=True)
    for i in del_index:
        del tmp_tree[i]
    return all_flag


def _get_own_org_list(user_id, cur, org_id_name='id', org_name_name='label', super_admin=False):
    if super_admin:
        sql = "select org_id from sys_org"
        cur.execute(sql)
    else:
        sql = "select org_id from sys_user_org where user_id=%s"
        cur.execute(sql, user_id)
    rows = cur.fetchall()
    own_org_ids = [str(org_id) for org_id, in rows]
    org_tree = _get_org_tree_dfs(cur, 'root', org_id_name, org_name_name)
    _org_list_format_dfs(org_tree, own_org_ids, org_id_name, org_name_name)
    return org_tree


def is_super_admin(user_id):
    cur = connection.cursor()
    sql = "select * from sys_user_role where user_id=%s and role_id='root'"
    cur.execute(sql, user_id)
    row = cur.fetchone()
    if row and row[0]:
        is_super_admin = True
    else:
        is_super_admin = False
    cur.close()
    return is_super_admin