# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class SAccountDetail(models.Model):
    change_type = models.CharField(max_length=10)
    change_money = models.DecimalField(max_digits=12, decimal_places=2)
    now_money = models.DecimalField(max_digits=12, decimal_places=2)
    order_id = models.CharField(max_length=30, blank=True, null=True)
    user_id = models.IntegerField()
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_account_detail'


class SAccountDetailBak1122(models.Model):
    change_type = models.CharField(max_length=10)
    change_money = models.DecimalField(max_digits=12, decimal_places=2)
    order_id = models.CharField(max_length=30, blank=True, null=True)
    user_id = models.IntegerField()
    remark = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_account_detail_bak1122'


class SAccountIce(models.Model):
    ice_amount = models.DecimalField(max_digits=12, decimal_places=2)
    link_type = models.CharField(max_length=20)
    link_id = models.CharField(max_length=20)
    user_id = models.IntegerField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_account_ice'


class SCmdDetail(models.Model):
    # cmd_type = models.CharField(max_length=20, blank=True, null=True)  # 20241220：不知道啥意思，先注释掉
    cmd = models.TextField()
    seq_no = models.CharField(max_length=30, blank=True, null=True)
    eq_id = models.CharField(max_length=20, blank=True, null=True)
    eq_code = models.CharField(max_length=20)
    send_type = models.CharField(max_length=1)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_cmd_detail'


class SCmdDetailBak1122(models.Model):
    cmd = models.TextField()
    seq_no = models.CharField(max_length=30, blank=True, null=True)
    eq_id = models.IntegerField(blank=True, null=True)
    eq_code = models.CharField(max_length=20)
    send_type = models.CharField(max_length=1)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_cmd_detail_bak1122'


class SDevopsTaskInfo(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20)
    task_desc = models.CharField(max_length=255)
    repair_id = models.IntegerField(blank=True, null=True)
    site_id = models.IntegerField()
    eq_id = models.CharField(max_length=20, blank=True, null=True)
    feedback_tel = models.CharField(max_length=20, blank=True, null=True)
    create_type = models.CharField(max_length=10)
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_devops_task_info'


class SDevopsTaskRecv(models.Model):
    recv_id = models.AutoField(primary_key=True)
    task_id = models.IntegerField()
    user_id = models.IntegerField(blank=True, null=True)
    fault_reason = models.CharField(max_length=255, blank=True, null=True)
    repair_way = models.CharField(max_length=255, blank=True, null=True)
    repair_img = models.CharField(max_length=255, blank=True, null=True)
    report_reason = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_devops_task_recv'


class SDevopsTaskReport(models.Model):
    task_id = models.IntegerField()
    recv_id = models.IntegerField()
    user_id = models.IntegerField()
    fault_reason = models.CharField(max_length=255, blank=True, null=True)
    report_reason = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_devops_task_report'


class SDevopsUserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30)
    user_sex = models.CharField(max_length=1, blank=True, null=True)
    user_comp = models.CharField(max_length=255, blank=True, null=True)
    user_post = models.CharField(max_length=255, blank=True, null=True)
    user_no = models.CharField(max_length=30, blank=True, null=True)
    open_id = models.CharField(max_length=32, blank=True, null=True)
    union_id = models.CharField(max_length=32, blank=True, null=True)
    from_operator = models.CharField(max_length=30)
    user_tel = models.CharField(max_length=20, blank=True, null=True)
    user_password = models.CharField(max_length=255)
    login_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_devops_user_info'


class SDisProfitCfgBak(models.Model):
    eq_id = models.CharField(max_length=20)
    user_id = models.IntegerField()
    dis_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 's_dis_profit_cfg_bak'


class SDisProfitCfg(models.Model):
    site_id = models.IntegerField()
    user_id = models.IntegerField()
    dis_rate = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 's_dis_profit_cfg'

class SDisProfitDetail(models.Model):
    eq_id = models.IntegerField()
    site_id = models.IntegerField(blank=True, null=True)
    order_id = models.CharField(max_length=32)
    user_id = models.IntegerField()
    order_money = models.DecimalField(max_digits=12, decimal_places=2)
    dis_rate = models.DecimalField(max_digits=12, decimal_places=2)
    dis_money = models.DecimalField(max_digits=12, decimal_places=2)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)
    profit_no = models.IntegerField(blank=True, null=True)
    profit_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 's_dis_profit_detail'



# class SDisProfitMode(models.Model):
#     dis_mode_id = models.AutoField(primary_key=True)
#     mode_name = models.CharField(max_length=100)
#     mode_desc = models.CharField(max_length=255, blank=True, null=True)
#     plat_rate = models.IntegerField()
#     opera_rate = models.IntegerField()
#     hard_rate = models.IntegerField()
#     dis_begin_time = models.DateTimeField()
#     state = models.CharField(max_length=1)
#
#     class Meta:
#         managed = True
#         db_table = 's_dis_profit_mode'


class SEndTypeKv(models.Model):
    end_type = models.CharField(primary_key=True, max_length=2)
    end_reason = models.CharField(max_length=255)
    end_tip = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 's_end_type_kv'


class SEqArgData(models.Model):
    eq_id = models.CharField(max_length=20)
    arg_key = models.CharField(max_length=50)
    arg_value = models.CharField(max_length=100)
    create_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_eq_arg_data'


class SEqAttrData(models.Model):
    eq_id = models.CharField(max_length=20)
    attr_key = models.CharField(max_length=20)
    attr_value = models.CharField(max_length=50)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_eq_attr_data'


class SEqCommDataBak(models.Model):
    id = models.IntegerField(primary_key=True)
    eq_id = models.IntegerField()
    eq_data = models.TextField(blank=True, null=True)
    server_data = models.TextField(blank=True, null=True)
    req_type = models.CharField(max_length=20)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_eq_comm_data_bak'


class SEqInfo(models.Model):
    eq_id = models.AutoField(primary_key=True)
    eq_code = models.CharField(max_length=20, blank=True, null=True)
    org_id = models.IntegerField()
    terminal_address = models.CharField(unique=True, max_length=10)
    password = models.CharField(max_length=18, blank=True, null=True)
    region_id_1 = models.IntegerField()
    region_id_2 = models.IntegerField()
    region_id_3 = models.IntegerField()
    site_id = models.IntegerField()
    conn_state = models.CharField(max_length=1)
    eq_firm = models.CharField(max_length=100)
    rated_power = models.DecimalField(max_digits=12, decimal_places=2)
    hard_version = models.CharField(max_length=30, blank=True, null=True)
    soft_version = models.CharField(max_length=10, blank=True, null=True)
    agree_version = models.CharField(max_length=10, blank=True, null=True)
    eq_type_id = models.IntegerField()
    eq_state = models.CharField(max_length=1)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)
    hard_id = models.IntegerField()
    mode_id = models.IntegerField(blank=True, null=True)
    iccid = models.CharField(max_length=50, blank=True, null=True)
    sim_type = models.CharField(max_length=20, blank=True, null=True)
    imei = models.CharField(max_length=50, blank=True, null=True)
    last_conn_time = models.DateTimeField(blank=True, null=True)
    last_active_time = models.DateTimeField(blank=True, null=True)
    eq_arg_no = models.CharField(max_length=50, blank=True, null=True)
    signal_strength = models.CharField(max_length=255, blank=True, null=True)
    total_electricity = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sim_card = models.CharField(max_length=255, blank=True, null=True)
    sim_card_len = models.CharField(max_length=255, blank=True, null=True)
    geography = models.CharField(max_length=255, blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    fee_type = models.CharField(max_length=10, blank=True, null=True)
    elec_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 's_eq_info'



class SEqPort(models.Model):
    eq_id = models.IntegerField()
    terminal_address = models.CharField(max_length=10)
    eq_port = models.CharField(max_length=10)
    state = models.CharField(max_length=10)
    use_state = models.CharField(max_length=10)
    conn_state = models.CharField(max_length=10)
    update_time = models.DateTimeField(blank=True, null=True)
    power_time = models.DateTimeField(blank=True, null=True)
    power = models.DecimalField(max_digits=10, decimal_places=2)
    QR_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_eq_port'




class SFeedbackDetail(models.Model):
    feed_type = models.CharField(max_length=20)
    order_id = models.CharField(max_length=32, blank=True, null=True)
    eq_id = models.IntegerField(blank=True, null=True)
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    user_tel = models.CharField(max_length=20)
    feedback_content = models.CharField(max_length=255)
    feedback_img = models.TextField(blank=True, null=True)
    user_id = models.IntegerField()
    create_time = models.DateTimeField()
    reply = models.CharField(max_length=255, blank=True, null=True)
    reply_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)
    reply_img = models.TextField(blank=True, null=True)
    handle_user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 's_feedback_detail'



class SHardEqInfo(models.Model):
    hard_id = models.IntegerField()
    eq_name = models.CharField(max_length=50)
    eq_mode = models.CharField(max_length=50, blank=True, null=True)
    eq_rated_power = models.IntegerField()
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_hard_eq_info'


class SHardFirmInfo(models.Model):
    hard_no = models.CharField(max_length=20)
    hard_name = models.CharField(max_length=100)
    hard_type = models.CharField(max_length=20, blank=True, null=True)
    hard_desc = models.CharField(max_length=255, blank=True, null=True)
    hard_user_name = models.CharField(max_length=50, blank=True, null=True)
    hard_user_tel = models.CharField(max_length=20, blank=True, null=True)
    bind_user_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField()
    create_uid = models.IntegerField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_hard_firm_info'


class SInvoiceDetail(models.Model):
    sub_type = models.CharField(max_length=1)
    sub_name = models.CharField(max_length=255)
    sub_taxes_no = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=255)
    order_id = models.CharField(max_length=20)
    user_id = models.IntegerField()
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_invoice_detail'


class SJoinApply(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=50)
    tel = models.CharField(max_length=20)
    leave_msg = models.CharField(max_length=255, blank=True, null=True)
    sub_type = models.CharField(max_length=20, blank=True, null=True)
    comp_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_join_apply'


class SNoticeInfo(models.Model):
    notice_name = models.CharField(max_length=100)
    notice_content = models.TextField()
    notice_remark = models.CharField(max_length=50, blank=True, null=True)
    notice_desc = models.CharField(max_length=255, blank=True, null=True)
    look_num = models.IntegerField()
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_notice_info'


class SOperaDetail(models.Model):
    opera_type = models.CharField(max_length=20)
    eq_id = models.CharField(max_length=20)
    seq_no = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    create_class = models.CharField(max_length=1)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_opera_detail'


class SOperaDetailBak1122(models.Model):
    opera_type = models.CharField(max_length=20)
    eq_id = models.IntegerField()
    seq_no = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.CharField(max_length=20, blank=True, null=True)
    create_class = models.CharField(max_length=1)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_opera_detail_bak1122'


class SOperatorInfo(models.Model):
    operator_id = models.AutoField(primary_key=True)
    operator_name = models.CharField(max_length=100)
    operator_user_name = models.CharField(max_length=20, blank=True, null=True)
    operator_tel = models.CharField(max_length=20, blank=True, null=True)
    operator_address = models.CharField(max_length=255, blank=True, null=True)
    dock_user_name = models.CharField(max_length=20, blank=True, null=True)
    bind_user_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField()
    create_uid = models.IntegerField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_operator_info'


class SOrderInfo(models.Model):
    order_id = models.CharField(primary_key=True, max_length=30)
    site_id = models.IntegerField()
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    term_address = models.CharField(max_length=20, blank=True, null=True)
    user_id = models.IntegerField()
    card_num = models.CharField(max_length=20, blank=True, null=True)
    open_type = models.CharField(max_length=10, blank=True, null=True)
    pay_way = models.CharField(max_length=10, blank=True, null=True)
    charge_type = models.CharField(max_length=10)
    charge_time = models.IntegerField(blank=True, null=True)
    charge_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    charge_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    begin_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    end_type = models.CharField(max_length=1, blank=True, null=True)
    end_reason = models.CharField(max_length=50, blank=True, null=True)
    use_time = models.IntegerField(blank=True, null=True)
    use_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    return_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    refund_state = models.CharField(max_length=10, blank=True, null=True)
    use_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    error_times = models.IntegerField()
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=10)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    fee_type = models.CharField(max_length=1, blank=True, null=True)
    elec_cost = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    order_source = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 's_order_info'


class SOrderInfoBak1118(models.Model):
    order_id = models.CharField(primary_key=True, max_length=30)
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    user_id = models.IntegerField()
    charge_type = models.CharField(max_length=10)
    charge_time = models.IntegerField(blank=True, null=True)
    charge_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    charge_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    begin_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    end_type = models.CharField(max_length=1, blank=True, null=True)
    use_time = models.IntegerField(blank=True, null=True)
    use_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    return_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    use_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField()
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_order_info_bak1118'


class SOrderInfoBak1122(models.Model):
    order_id = models.CharField(primary_key=True, max_length=30)
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    user_id = models.IntegerField()
    charge_type = models.CharField(max_length=10)
    charge_time = models.IntegerField(blank=True, null=True)
    charge_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    charge_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    begin_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    end_type = models.CharField(max_length=2, blank=True, null=True)
    use_time = models.IntegerField(blank=True, null=True)
    use_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    return_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    use_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_order_info_bak1122'


class SPlatInfo(models.Model):
    plat_id = models.AutoField(primary_key=True)
    plat_name = models.CharField(max_length=255)
    plat_link_name = models.CharField(max_length=100)
    plat_link_tel = models.CharField(max_length=30, blank=True, null=True)
    plat_address = models.CharField(max_length=255, blank=True, null=True)
    bind_user_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField()
    create_uid = models.IntegerField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_plat_info'


class SPriceMode(models.Model):
    mode_id = models.AutoField(primary_key=True)
    mode_name = models.CharField(max_length=50)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_price_mode'


class SPriceModeDetail(models.Model):
    begin_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=12, decimal_places=6)
    mode_id = models.IntegerField()
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_price_mode_detail'


class SRepairInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    repair_type = models.CharField(max_length=10)
    other_type_text = models.CharField(max_length=50, blank=True, null=True)
    repair_tel = models.CharField(max_length=20, blank=True, null=True)
    repair_img = models.TextField(blank=True, null=True)
    eq_id = models.CharField(max_length=20)
    user_id = models.IntegerField()
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)
    reply_img = models.TextField(blank=True, null=True)
    reply = models.CharField(max_length=255, blank=True, null=True)
    handle_user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_repair_info'



class SRepairKv(models.Model):
    repair_key = models.CharField(primary_key=True, max_length=10)
    repair_label = models.CharField(max_length=100)
    auto_task = models.CharField(max_length=1)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_repair_kv'


class SSiteDevopsUser(models.Model):
    site_id = models.IntegerField()
    dev_user_id = models.IntegerField()
    update_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_site_devops_user'


class SSiteInfo(models.Model):
    site_id = models.AutoField(primary_key=True)
    site_name = models.CharField(max_length=100)
    site_address = models.CharField(max_length=255, blank=True, null=True)
    site_gps = models.CharField(max_length=100, blank=True, null=True)
    site_position = models.CharField(max_length=100, blank=True, null=True)
    site_build = models.CharField(max_length=100, blank=True, null=True)
    mode_id = models.IntegerField()
    site_desc = models.CharField(max_length=500, blank=True, null=True)
    org_id = models.IntegerField(blank=True, null=True)
    plat_id = models.IntegerField(blank=True, null=True)
    # dis_mode_id = models.IntegerField(blank=True, null=True)
    operator_id = models.IntegerField(blank=True, null=True)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_site_info'


class SUserCar(models.Model):
    user_id = models.IntegerField()
    car_number = models.CharField(max_length=10, blank=True, null=True)
    car_brand = models.CharField(max_length=20, blank=True, null=True)
    car_model = models.CharField(max_length=20, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 's_user_car'


class SUserInfo(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_no = models.CharField(max_length=20, blank=True, null=True)
    wx_open_id = models.CharField(max_length=100, blank=True, null=True)
    xcx_open_id = models.CharField(max_length=100, blank=True, null=True)
    union_id = models.CharField(max_length=100, blank=True, null=True)
    account = models.DecimalField(max_digits=12, decimal_places=2)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    wx_nickname = models.CharField(max_length=100, blank=True, null=True)
    wx_headimgurl = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    wx_sex = models.CharField(max_length=1, blank=True, null=True)
    wx_country = models.CharField(max_length=100, blank=True, null=True)
    wx_province = models.CharField(max_length=100, blank=True, null=True)
    wx_city = models.CharField(max_length=100, blank=True, null=True)
    wx_language = models.CharField(max_length=20, blank=True, null=True)
    wx_session_key = models.CharField(max_length=100)
    wx_update_time = models.DateTimeField(blank=True, null=True)
    is_fetch_wx_info = models.CharField(max_length=1)
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)
    identity = models.CharField(max_length=10, blank=True, null=True)
    remark_name = models.CharField(max_length=50, blank=True, null=True)
    max_order_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 's_user_info'


class SWarnDetail(models.Model):
    warn_type = models.CharField(max_length=20)
    warn_content = models.CharField(max_length=255)
    site_id = models.IntegerField()
    eq_id = models.CharField(max_length=20)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    handle_user = models.IntegerField(blank=True, null=True)
    handle_remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_warn_detail'


class SWxCashoutDetail(models.Model):
    order_id = models.CharField(primary_key=True, max_length=30)
    transfer_bill_no = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    user_id = models.IntegerField()
    open_id = models.CharField(max_length=50)
    batch_id = models.CharField(max_length=64, blank=True, null=True)
    detail_id = models.CharField(max_length=64, blank=True, null=True)
    create_time = models.DateTimeField()
    verify_time = models.DateTimeField(blank=True, null=True)
    pay_start_time = models.DateTimeField(blank=True, null=True)
    finish_time = models.DateTimeField(blank=True, null=True)
    package_info = models.CharField(max_length=255, blank=True, null=True)
    fail_reason = models.CharField(max_length=500, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    verify_state = models.CharField(max_length=1)
    state = models.CharField(max_length=1)
    user_varify_state = models.CharField(max_length=10, blank=True, null=True)
    wx_state_str = models.CharField(max_length=20, blank=True, null=True)
    wx_state = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 's_wx_cashout_detail_1'


class SWxTempMsgBak(models.Model):
    temp_type = models.CharField(max_length=20)
    open_id = models.CharField(max_length=32)
    k1 = models.CharField(max_length=50, blank=True, null=True)
    k2 = models.CharField(max_length=50, blank=True, null=True)
    k3 = models.CharField(max_length=50, blank=True, null=True)
    k4 = models.CharField(max_length=50, blank=True, null=True)
    k5 = models.CharField(max_length=50, blank=True, null=True)
    k6 = models.CharField(max_length=50, blank=True, null=True)
    k7 = models.CharField(max_length=50, blank=True, null=True)
    k8 = models.CharField(max_length=50, blank=True, null=True)
    url = models.CharField(max_length=100, blank=True, null=True)
    xcx_app_id = models.CharField(max_length=20, blank=True, null=True)
    xcx_path = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField()
    handle_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_wx_temp_msg_bak'


class SWxTranDetail(models.Model):
    change_type = models.CharField(max_length=10)
    change_money = models.DecimalField(max_digits=12, decimal_places=2)
    user_id = models.IntegerField()
    order_id = models.CharField(max_length=32)
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    verify_state = models.CharField(max_length=1)
    verify_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_wx_tran_detail'


class SYwOrgLink(models.Model):
    yw_type = models.CharField(max_length=20)
    yw_id = models.IntegerField()
    org_id = models.IntegerField()

    class Meta:
        managed = True
        db_table = 's_yw_org_link'


class SysApiTest(models.Model):
    api_name = models.CharField(max_length=60)
    req_url = models.CharField(max_length=200)
    req_pkg = models.TextField()
    resp_pkg = models.TextField(blank=True, null=True)
    resp_code = models.CharField(max_length=6, blank=True, null=True)
    create_userid = models.IntegerField(blank=True, null=True)
    create_datetime = models.DateTimeField(blank=True, null=True)
    snote = models.CharField(max_length=90, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_api_test'


class SysChartCfg(models.Model):
    cid = models.AutoField(primary_key=True)
    cname = models.CharField(max_length=255)
    cfg = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_chart_cfg'


class SysCrudCfgBody(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    app_id = models.IntegerField(db_column='APP_ID')  # Field name made lowercase.
    tran_id = models.CharField(db_column='TRAN_ID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    field_id = models.CharField(db_column='FIELD_ID', max_length=30)  # Field name made lowercase.
    field_name = models.CharField(db_column='FIELD_NAME', max_length=50)  # Field name made lowercase.
    state = models.CharField(db_column='STATE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    data_type = models.CharField(db_column='DATA_TYPE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    field_length = models.IntegerField(db_column='FIELD_LENGTH', blank=True, null=True)  # Field name made lowercase.
    max_length = models.IntegerField(db_column='MAX_LENGTH', blank=True, null=True)  # Field name made lowercase.
    ui_type = models.CharField(db_column='UI_TYPE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    allow_blank = models.CharField(db_column='ALLOW_BLANK', max_length=1, blank=True, null=True)  # Field name made lowercase.
    is_key = models.CharField(db_column='IS_KEY', max_length=1, blank=True, null=True)  # Field name made lowercase.
    search_type = models.CharField(db_column='SEARCH_TYPE', max_length=30, blank=True, null=True)  # Field name made lowercase.
    search_exts = models.CharField(db_column='SEARCH_EXTS', max_length=254, blank=True, null=True)  # Field name made lowercase.
    edit_able = models.CharField(db_column='EDIT_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    def_value = models.CharField(db_column='DEF_VALUE', max_length=254, blank=True, null=True)  # Field name made lowercase.
    order_id = models.IntegerField(db_column='ORDER_ID', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_crud_cfg_body'
        unique_together = (('app_id', 'field_id'),)


class SysCrudCfgHead(models.Model):
    app_id = models.AutoField(db_column='APP_ID', primary_key=True)  # Field name made lowercase.
    app_name = models.CharField(db_column='APP_NAME', max_length=100)  # Field name made lowercase.
    tran_id = models.CharField(db_column='TRAN_ID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    where_ctrl = models.CharField(db_column='WHERE_CTRL', max_length=200, blank=True, null=True)  # Field name made lowercase.
    order_ctrl = models.CharField(db_column='ORDER_CTRL', max_length=200, blank=True, null=True)  # Field name made lowercase.
    group_ctrl = models.CharField(db_column='GROUP_CTRL', max_length=200, blank=True, null=True)  # Field name made lowercase.
    table_name = models.CharField(db_column='TABLE_NAME', max_length=60)  # Field name made lowercase.
    data_source = models.CharField(db_column='DATA_SOURCE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    main_control = models.CharField(db_column='MAIN_CONTROL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    select_able = models.CharField(db_column='SELECT_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    insert_able = models.CharField(db_column='INSERT_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    update_able = models.CharField(db_column='UPDATE_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    delete_able = models.CharField(db_column='DELETE_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    export_able = models.CharField(db_column='EXPORT_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    import_able = models.CharField(db_column='IMPORT_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    plugins = models.CharField(db_column='PLUGINS', max_length=254, blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.
    upd_time = models.DateTimeField(db_column='UPD_TIME')  # Field name made lowercase.
    insert_formid = models.CharField(db_column='INSERT_FORMID', max_length=8, blank=True, null=True)  # Field name made lowercase.
    update_formid = models.CharField(db_column='UPDATE_FORMID', max_length=8, blank=True, null=True)  # Field name made lowercase.
    delete_formid = models.CharField(db_column='DELETE_FORMID', max_length=8, blank=True, null=True)  # Field name made lowercase.
    export_formid = models.CharField(db_column='EXPORT_FORMID', max_length=8, blank=True, null=True)  # Field name made lowercase.
    import_formid = models.CharField(db_column='IMPORT_FORMID', max_length=8, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_crud_cfg_head'


class SysDbCfg(models.Model):
    db_host = models.CharField(max_length=20)
    db_port = models.CharField(max_length=10)
    db_name = models.CharField(max_length=50)
    db_user = models.CharField(max_length=50)
    db_password = models.CharField(max_length=50)
    db_type = models.CharField(max_length=10)
    user_id = models.IntegerField()
    create_time = models.DateTimeField()
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 'sys_db_cfg'


class SysFileup(models.Model):
    file_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField()
    md5_name = models.CharField(max_length=60)
    tran_date = models.DateTimeField()
    user_id = models.IntegerField()
    menu_id = models.IntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    req_ip = models.CharField(max_length=20)
    req_seq = models.CharField(max_length=25)
    state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 'sys_fileup'


class SysFormCfgFieldlist(models.Model):
    form_id = models.IntegerField()
    comp_id = models.CharField(max_length=30)
    comp_type = models.CharField(max_length=20, blank=True, null=True)
    field_id = models.CharField(max_length=60)
    field_name = models.CharField(max_length=120, blank=True, null=True)
    show_able = models.CharField(max_length=1, blank=True, null=True)
    dis_able = models.CharField(max_length=1, blank=True, null=True)
    options_sql = models.CharField(max_length=2000, blank=True, null=True)
    options_val = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_form_cfg_fieldlist'
        unique_together = (('form_id', 'comp_id'),)


class SysFormCfgInfo(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.CharField(max_length=60, blank=True, null=True)
    form_show_tran_type = models.CharField(max_length=60, blank=True, null=True)
    form_show_api = models.CharField(max_length=200, blank=True, null=True)
    form_cfg = models.TextField(blank=True, null=True)
    form_var = models.TextField(blank=True, null=True)
    form_attr = models.TextField(blank=True, null=True)
    form_sql = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField()
    update_user = models.IntegerField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_form_cfg_info'


class SysMenu(models.Model):
    menu_id = models.AutoField(db_column='MENU_ID', primary_key=True)  # Field name made lowercase.
    above_menu_id = models.CharField(db_column='ABOVE_MENU_ID', max_length=20)  # Field name made lowercase.
    menu_deep = models.IntegerField(db_column='MENU_DEEP')  # Field name made lowercase.
    menu_name = models.CharField(db_column='MENU_NAME', max_length=30)  # Field name made lowercase.
    menu_desc = models.CharField(db_column='MENU_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_run_menu = models.CharField(db_column='IS_RUN_MENU', max_length=1, blank=True, null=True)  # Field name made lowercase.
    app_id = models.IntegerField(db_column='APP_ID', blank=True, null=True)  # Field name made lowercase.
    tran_id = models.CharField(db_column='TRAN_ID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    is_enable = models.CharField(db_column='IS_ENABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    order_id = models.IntegerField(db_column='ORDER_ID', blank=True, null=True)  # Field name made lowercase.
    menu_type = models.CharField(db_column='MENU_TYPE', max_length=20)  # Field name made lowercase.
    menu_path = models.CharField(db_column='MENU_PATH', max_length=30, blank=True, null=True)  # Field name made lowercase.
    menu_icon = models.CharField(db_column='MENU_ICON', max_length=30, blank=True, null=True)  # Field name made lowercase.
    is_new_page = models.CharField(db_column='IS_NEW_PAGE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    system_id = models.CharField(db_column='SYSTEM_ID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.
    create_time = models.DateTimeField(db_column='CREATE_TIME', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_menu'


class SysNologTrantype(models.Model):
    tran_type = models.CharField(db_column='TRAN_TYPE', primary_key=True, max_length=20)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_nolog_trantype'


class SysOrg(models.Model):
    org_id = models.AutoField(db_column='ORG_ID', primary_key=True)  # Field name made lowercase.
    org_name = models.CharField(db_column='ORG_NAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    above_org_id = models.CharField(db_column='ABOVE_ORG_ID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    org_type = models.CharField(db_column='ORG_TYPE', max_length=10, blank=True, null=True)  # Field name made lowercase.
    org_level = models.CharField(db_column='ORG_LEVEL', max_length=10, blank=True, null=True)  # Field name made lowercase.
    org_addr = models.CharField(db_column='ORG_ADDR', max_length=60, blank=True, null=True)  # Field name made lowercase.
    org_leader = models.CharField(db_column='ORG_LEADER', max_length=30, blank=True, null=True)  # Field name made lowercase.
    org_spell = models.CharField(db_column='ORG_SPELL', max_length=10, blank=True, null=True)  # Field name made lowercase.
    org_state = models.CharField(db_column='ORG_STATE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID', blank=True, null=True)  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_org'
        unique_together = (('org_spell', 'org_name'),)


class SysReportCfgInfo(models.Model):
    report_id = models.AutoField(primary_key=True)
    report_name = models.CharField(max_length=60)
    report_startrows = models.IntegerField(db_column='report_startRows')  # Field name made lowercase.
    report_startcols = models.IntegerField(db_column='report_startCols')  # Field name made lowercase.
    report_show_api = models.CharField(max_length=200, blank=True, null=True)
    report_show_tran_type = models.CharField(max_length=60, blank=True, null=True)
    report_data_api = models.CharField(max_length=200, blank=True, null=True)
    report_data_tran_type = models.CharField(max_length=60, blank=True, null=True)
    report_data_sql = models.TextField(blank=True, null=True)
    report_other_cfg = models.TextField(blank=True, null=True)
    report_cellsmap = models.TextField(db_column='report_cellsMap', blank=True, null=True)  # Field name made lowercase.
    report_datasource = models.TextField(db_column='report_dataSource', blank=True, null=True)  # Field name made lowercase.
    report_rows = models.TextField(blank=True, null=True)
    report_colums = models.TextField(blank=True, null=True)
    report_mergecells = models.TextField(db_column='report_mergeCells', blank=True, null=True)  # Field name made lowercase.
    report_sourcedata = models.TextField(db_column='report_sourceData', blank=True, null=True)  # Field name made lowercase.
    create_user_id = models.IntegerField(blank=True, null=True)
    create_date = models.DateTimeField()
    update_user_id = models.IntegerField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_report_cfg_info'


class SysRole(models.Model):
    role_id = models.CharField(db_column='ROLE_ID', primary_key=True, max_length=20)  # Field name made lowercase.
    role_name = models.CharField(db_column='ROLE_NAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    role_above_id = models.CharField(db_column='ROLE_ABOVE_ID', max_length=20, blank=True, null=True)  # Field name made lowercase.
    role_state = models.CharField(db_column='ROLE_STATE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID', blank=True, null=True)  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_role'


class SysRolePurvBody(models.Model):
    role_id = models.CharField(db_column='ROLE_ID', max_length=20)  # Field name made lowercase.
    menu_id = models.IntegerField(db_column='MENU_ID')  # Field name made lowercase.
    app_id = models.IntegerField(db_column='APP_ID', blank=True, null=True)  # Field name made lowercase.
    form_id = models.IntegerField(db_column='FORM_ID', blank=True, null=True)  # Field name made lowercase.
    field_id = models.CharField(db_column='FIELD_ID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    field_name = models.CharField(db_column='FIELD_NAME', max_length=60, blank=True, null=True)  # Field name made lowercase.
    show_able = models.CharField(db_column='SHOW_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    dis_able = models.CharField(db_column='DIS_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_role_purv_body'


class SysRolePurvHead(models.Model):
    role_id = models.CharField(db_column='ROLE_ID', max_length=20)  # Field name made lowercase.
    menu_id = models.IntegerField(db_column='MENU_ID')  # Field name made lowercase.
    app_id = models.IntegerField(db_column='APP_ID', blank=True, null=True)  # Field name made lowercase.
    auth_type = models.CharField(db_column='AUTH_TYPE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    auth_flag = models.CharField(db_column='AUTH_FLAG', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_role_purv_head'


class SysSequence(models.Model):
    seq_name = models.CharField(primary_key=True, max_length=50)
    current_val = models.IntegerField()
    curval_len = models.IntegerField(blank=True, null=True)
    increment_val = models.IntegerField()
    expression = models.CharField(max_length=50)
    snote = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_sequence'


class SysUser(models.Model):
    user_id = models.AutoField(db_column='USER_ID', primary_key=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='USER_NAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    login_name = models.CharField(db_column='LOGIN_NAME', unique=True, max_length=30)  # Field name made lowercase.
    passwd = models.CharField(db_column='PASSWD', max_length=32, blank=True, null=True)  # Field name made lowercase.
    station = models.CharField(db_column='STATION', max_length=20, blank=True, null=True)  # Field name made lowercase.
    certi_type = models.CharField(db_column='CERTI_TYPE', max_length=2, blank=True, null=True)  # Field name made lowercase.
    certi = models.CharField(db_column='CERTI', max_length=18, blank=True, null=True)  # Field name made lowercase.
    sex = models.CharField(db_column='SEX', max_length=1, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='ADDRESS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tel = models.CharField(db_column='TEL', max_length=25, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='STATE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=90, blank=True, null=True)  # Field name made lowercase.
    head_imgurl = models.CharField(db_column='HEAD_IMGURL', max_length=300, blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID', blank=True, null=True)  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_user'


class SysUserFieldPurv(models.Model):
    user_id = models.CharField(db_column='USER_ID', max_length=20)  # Field name made lowercase.
    menu_id = models.IntegerField(db_column='MENU_ID')  # Field name made lowercase.
    field_id = models.CharField(db_column='FIELD_ID', max_length=30, blank=True, null=True)  # Field name made lowercase.
    show_able = models.CharField(db_column='SHOW_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    upd_able = models.CharField(db_column='UPD_ABLE', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_user_field_purv'


class SysUserHis(models.Model):
    user_id = models.AutoField(db_column='USER_ID', primary_key=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='USER_NAME', max_length=30, blank=True, null=True)  # Field name made lowercase.
    login_name = models.CharField(db_column='LOGIN_NAME', unique=True, max_length=30)  # Field name made lowercase.
    passwd = models.CharField(db_column='PASSWD', max_length=32, blank=True, null=True)  # Field name made lowercase.
    station = models.CharField(db_column='STATION', max_length=20, blank=True, null=True)  # Field name made lowercase.
    certi_type = models.CharField(db_column='CERTI_TYPE', max_length=2, blank=True, null=True)  # Field name made lowercase.
    certi = models.CharField(db_column='CERTI', max_length=18, blank=True, null=True)  # Field name made lowercase.
    sex = models.CharField(db_column='SEX', max_length=1, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='ADDRESS', max_length=200, blank=True, null=True)  # Field name made lowercase.
    tel = models.CharField(db_column='TEL', max_length=25, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='EMAIL', max_length=50, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='STATE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=90, blank=True, null=True)  # Field name made lowercase.
    head_imgurl = models.CharField(db_column='HEAD_IMGURL', max_length=300, blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID', blank=True, null=True)  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_user_his'


class SysUserMessage(models.Model):
    user_id = models.IntegerField()
    tran_date = models.DateTimeField()
    type = models.CharField(max_length=20, blank=True, null=True)
    content = models.CharField(max_length=60, blank=True, null=True)
    message = models.CharField(max_length=1024, blank=True, null=True)
    msg_status = models.CharField(max_length=20, blank=True, null=True)
    read_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_user_message'


class SysUserOperateList(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    tran_type = models.CharField(max_length=50)
    req_ip = models.CharField(max_length=20)
    req_time = models.DateTimeField()
    req_seq = models.CharField(unique=True, max_length=30)
    req_pkg = models.TextField(blank=True, null=True)
    resp_time = models.DateTimeField(blank=True, null=True)
    resp_code = models.CharField(max_length=8, blank=True, null=True)
    resp_msg = models.CharField(max_length=1024, blank=True, null=True)
    resp_pkg = models.TextField(blank=True, null=True)
    error_msg = models.CharField(max_length=4096, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_user_operate_list'


class SysUserOrg(models.Model):
    user_id = models.IntegerField(db_column='USER_ID')  # Field name made lowercase.
    org_id = models.CharField(db_column='ORG_ID', max_length=20)  # Field name made lowercase.
    user_above_id = models.IntegerField(db_column='USER_ABOVE_ID', blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID')  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.
    snote = models.CharField(db_column='SNOTE', max_length=90, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_user_org'


class SysUserRole(models.Model):
    user_id = models.CharField(db_column='USER_ID', max_length=20)  # Field name made lowercase.
    role_id = models.CharField(db_column='ROLE_ID', max_length=20)  # Field name made lowercase.
    user_above_id = models.IntegerField(db_column='USER_ABOVE_ID', blank=True, null=True)  # Field name made lowercase.
    operate_userid = models.IntegerField(db_column='OPERATE_USERID', blank=True, null=True)  # Field name made lowercase.
    operate_datetime = models.DateTimeField(db_column='OPERATE_DATETIME', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_user_role'
        unique_together = (('user_id', 'role_id'),)


class SysWfCfg(models.Model):
    form_id = models.IntegerField(primary_key=True)
    wf_cfg = models.TextField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'sys_wf_cfg'


class SysWorkflowNodeCfg(models.Model):
    wf_id = models.AutoField(primary_key=True)
    form_id = models.IntegerField()
    wf_type = models.CharField(max_length=20, blank=True, null=True)
    wf_prev = models.IntegerField(blank=True, null=True)
    wf_next = models.IntegerField(blank=True, null=True)
    wf_cfg = models.TextField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    wf_state = models.CharField(max_length=1, blank=True, null=True)
    wf_notes = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_workflow_node_cfg'
        unique_together = (('wf_id', 'form_id'),)


class SysWorkflowNodeList(models.Model):
    node_id = models.AutoField(primary_key=True)
    wf_id = models.IntegerField()
    wf_type = models.CharField(max_length=20)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    gl_id = models.IntegerField(blank=True, null=True)
    node_prev = models.IntegerField(blank=True, null=True)
    node_next = models.IntegerField(blank=True, null=True)
    insert_date = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField()
    org_id = models.CharField(max_length=20, blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    node_state = models.CharField(max_length=1, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    form_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_workflow_node_list'
        unique_together = (('wf_id', 'gl_id', 'user_id'),)


class SysWorkflowNodeListHis(models.Model):
    node_id = models.IntegerField(primary_key=True)
    wf_id = models.IntegerField()
    wf_type = models.CharField(max_length=20)
    order_number = models.CharField(max_length=50, blank=True, null=True)
    gl_id = models.IntegerField(blank=True, null=True)
    node_prev = models.IntegerField(blank=True, null=True)
    node_next = models.IntegerField(blank=True, null=True)
    insert_date = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField()
    org_id = models.CharField(max_length=20, blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    node_state = models.CharField(max_length=1, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    form_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sys_workflow_node_list_his'


class SysWorkflowTran(models.Model):
    form_id = models.CharField(max_length=10)
    table_name = models.CharField(max_length=30)
    wf_name = models.CharField(max_length=50, blank=True, null=True)
    selsql = models.CharField(max_length=300, blank=True, null=True)
    table_head = models.TextField(blank=True, null=True)
    statue = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 'sys_workflow_tran'


class SysYwtyDict(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dict_name = models.CharField(db_column='DICT_NAME', max_length=50)  # Field name made lowercase.
    dict_code = models.CharField(db_column='DICT_CODE', max_length=50)  # Field name made lowercase.
    dict_target = models.CharField(db_column='DICT_TARGET', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dict_default = models.CharField(db_column='DICT_DEFAULT', max_length=1, blank=True, null=True)  # Field name made lowercase.
    dict_snote = models.CharField(db_column='DICT_SNOTE', max_length=200, blank=True, null=True)  # Field name made lowercase.
    dict_public_flag = models.CharField(db_column='DICT_PUBLIC_FLAG', max_length=1, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'sys_ywty_dict'
        unique_together = (('dict_name', 'dict_code'),)


class Tmp0528(models.Model):
    eq_id = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'tmp_0528'


class SCmdInfo(models.Model):
    # cmd_type = models.CharField(max_length=20, blank=True, null=True)  # 20241220：不知道啥意思，先注释掉
    term_address = models.CharField(max_length=64, blank=True, null=True)
    PR_SEQ = models.CharField(max_length=10, blank=True, null=True)
    active_station = models.CharField(max_length=10, blank=True, null=True)
    cmd_type = models.CharField(max_length=30, blank=True, null=True)
    req_cmd = models.TextField(blank=True, null=True)
    resp_cmd = models.TextField(blank=True, null=True)
    api_code = models.CharField(max_length=32, blank=True, null=True)
    resp_status = models.CharField(max_length=1, blank=True, null=True)
    update_status = models.CharField(max_length=1, blank=True, null=True)
    operate_result = models.CharField(max_length=10, blank=True, null=True)
    req_time = models.DateTimeField(blank=True, null=True)
    resp_time = models.DateTimeField(blank=True, null=True)
    resend_times = models.IntegerField(blank=True, null=True)
    resend_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)

    # cmd = models.TextField()
    # seq_no = models.CharField(max_length=30, blank=True, null=True)
    # eq_id = models.CharField(max_length=20, blank=True, null=True)
    # eq_code = models.CharField(max_length=20)
    # send_type = models.CharField(max_length=1)
    # create_time = models.DateTimeField()
    # handle_time = models.DateTimeField(blank=True, null=True)
    # state = models.CharField(max_length=1)

    class Meta:
        managed = True
        db_table = 's_cmd_info'

class SEqArgCommon(models.Model):
    site_id = models.IntegerField(blank=True, null=True)
    arg_no = models.CharField(max_length=50, blank=True, null=True)
    arg_name = models.CharField(max_length=255, blank=True, null=True)
    heart_time = models.CharField(max_length=20, blank=True, null=True)
    uplink_time = models.CharField(max_length=20, blank=True, null=True)
    delay_time = models.CharField(max_length=20, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    domain_len = models.CharField(max_length=20, blank=True, null=True)
    port = models.CharField(max_length=10, blank=True, null=True)
    max_power = models.CharField(max_length=50, blank=True, null=True)
    min_power = models.CharField(max_length=50, blank=True, null=True)



    class Meta:
        managed = True
        db_table = 's_eq_args_common'


class SEqArgsPrivate(models.Model):
    eq_id = models.CharField(max_length=50)
    terminal_address = models.CharField(max_length=10)
    heart_time = models.CharField(max_length=20, blank=True, null=True)
    uplink_interval = models.CharField(max_length=20, blank=True, null=True)
    delay_time = models.CharField(max_length=20, blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    port = models.CharField(max_length=10, blank=True, null=True)
    signal_strength = models.CharField(max_length=10, blank=True, null=True)
    QR_code = models.CharField(max_length=255, blank=True, null=True)  # Field name made lowercase.
    max_power = models.CharField(max_length=50, blank=True, null=True)
    min_power = models.CharField(max_length=50, blank=True, null=True)
    measure_model = models.CharField(max_length=10, blank=True, null=True)
    hourly_price = models.CharField(max_length=10, blank=True, null=True)
    rate_duration = models.CharField(max_length=10, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_eq_args_private'


class SOrderFee1(models.Model):
    order_id = models.CharField(max_length=30, blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    time_frame_no = models.CharField(max_length=50, blank=True, null=True)
    standard_name = models.CharField(max_length=50, blank=True, null=True)
    begin_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    use_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    use_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electric_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cal_status = models.CharField(max_length=1, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_fee_1'


class SOrderFee2(models.Model):
    order_id = models.CharField(max_length=30, blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    grads_no = models.CharField(max_length=50, blank=True, null=True)
    standard_name = models.CharField(max_length=50, blank=True, null=True)
    electric_down = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    electric_up = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    use_electric = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    use_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electric_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_fee_2'




class SFeeStandard1(models.Model):
    site_id = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    time_frame_no = models.CharField(max_length=50, blank=True, null=True)
    standard_name = models.CharField(max_length=50, blank=True, null=True)
    begin_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    electric_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_fee_standard_1'

class SFeeStandard2(models.Model):
    site_id = models.IntegerField(blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    grads_no = models.CharField(max_length=50, blank=True, null=True)
    standard_name = models.CharField(max_length=50, blank=True, null=True)
    electric_down = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    electric_up = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    electric_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_fee_standard_2'


class SOrderPower(models.Model):
    order_id = models.CharField(max_length=30, blank=True, null=True)
    power = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    power_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_power'

class SChargeArgs(models.Model):
    site_id = models.IntegerField(blank=True, null=True)
    arg_type = models.CharField(max_length=10, blank=True, null=True)
    value = models.CharField(max_length=10, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_charge_args'


class SCardsInfo(models.Model):
    card_sn = models.CharField(max_length=60)
    card_num = models.CharField(unique=True, max_length=50, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    user_name = models.CharField(max_length=10, blank=True, null=True)
    tel = models.CharField(max_length=11)
    money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gift_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    use_state = models.CharField(max_length=2, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_cards_info'


class SWxTranCardDetail(models.Model):
    card_sn = models.CharField(max_length=255, blank=True, null=True)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    card_tel = models.CharField(max_length=20)
    change_type = models.CharField(max_length=10)
    change_money = models.DecimalField(max_digits=12, decimal_places=2)
    user_id = models.IntegerField()
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    order_id = models.CharField(max_length=32)
    verify_state = models.CharField(max_length=1)
    verify_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_wx_tran_card_detail'


class SCardRechargeDetail(models.Model):
    card_sn = models.CharField(max_length=255)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    card_tel = models.CharField(max_length=20)
    recharge_type = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    recharge_money = models.DecimalField(max_digits=12, decimal_places=2)
    user_id = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 's_card_recharge_detail'


class SWxTranOrderDetail(models.Model):
    change_type = models.CharField(max_length=10)
    change_money = models.DecimalField(max_digits=12, decimal_places=2)
    user_id = models.IntegerField()
    order_id = models.CharField(max_length=32)
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    verify_state = models.CharField(max_length=1)
    verify_time = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField()
    finish_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=10)
    remark = models.CharField(max_length=255, blank=True, null=True)
    charge_order = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_wx_tran_order_detail'


class SOrderNumMap(models.Model):
    sub_order = models.CharField(max_length=50)
    charge_order = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)
    site_id = models.IntegerField()
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    term_address = models.CharField(max_length=20, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    charge_money = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    fee_no = models.CharField(max_length=50, blank=True, null=True)
    fee_type = models.CharField(max_length=1, blank=True, null=True)
    order_source = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 's_order_num_map'


class SWxDisProfitOrder(models.Model):
    dis_order_id = models.CharField(max_length=50, blank=True, null=True)
    tran_order_id = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=20, blank=True, null=True)
    transaction_id = models.CharField(max_length=32, blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)
    receiver_type = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField()
    wx_order_id = models.CharField(max_length=50, blank=True, null=True)
    wx_state_str = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    detail_id = models.CharField(max_length=50, blank=True, null=True)
    fail_reason = models.TextField(blank=True, null=True)
    finish_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_wx_dis_profit_order'

class SDisProfitReceiver(models.Model):
    type = models.CharField(max_length=20, blank=True, null=True)
    account = models.CharField(max_length=50, blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_dis_profit_receiver'


class SErrorRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    remark = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 's_error_record'


class SDisProfitRecord(models.Model):
    profit_no = models.CharField(max_length=20, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    evidence_img = models.TextField(blank=True, null=True)
    profit_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profit_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_dis_profit_record'


class SEqType(models.Model):
    eq_type_id = models.IntegerField(primary_key=True)
    eq_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_eq_type'


class SEqSimCard(models.Model):
    id = models.IntegerField(primary_key=True)
    eq_id = models.IntegerField()
    terminal_address = models.CharField(max_length=50, blank=True, null=True)
    sim_card = models.CharField(max_length=100, blank=True, null=True)
    msisdn = models.CharField(max_length=100, blank=True, null=True)
    imsi = models.CharField(max_length=255, blank=True, null=True)
    imei = models.CharField(max_length=255, blank=True, null=True)
    cardtype = models.CharField(db_column='cardType', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cardstatus = models.CharField(db_column='cardStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    operator = models.CharField(max_length=10, blank=True, null=True)
    packagename = models.CharField(db_column='packageName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    totalflow = models.CharField(db_column='totalFlow', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cardflow = models.CharField(db_column='cardFlow', max_length=10, blank=True, null=True)  # Field name made lowercase.
    lastactivatetime = models.DateTimeField(db_column='lastActivateTime', blank=True, null=True)  # Field name made lowercase.
    activatetime = models.DateTimeField(db_column='activateTime', blank=True, null=True)  # Field name made lowercase.
    packagetime = models.DateTimeField(db_column='packageTime', blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(max_length=255, blank=True, null=True)
    realnamestatus = models.CharField(db_column='realNameStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.
    channelid = models.IntegerField(db_column='channelId', blank=True, null=True)  # Field name made lowercase.
    packageid = models.IntegerField(db_column='packageId', blank=True, null=True)  # Field name made lowercase.
    networktype = models.CharField(db_column='networkType', max_length=10, blank=True, null=True)  # Field name made lowercase.
    packagetotalflow = models.CharField(db_column='packageTotalFlow', max_length=10, blank=True, null=True)  # Field name made lowercase.
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_eq_sim_card'


class SSiteUser(models.Model):
    id = models.IntegerField(primary_key=True)
    site_id = models.IntegerField()
    user_id = models.IntegerField()
    identify_id = models.IntegerField()
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_site_user'


class SUserIdentify(models.Model):
    identify_id = models.IntegerField(primary_key=True)
    identify = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_user_identify'


class SWxTempMsg(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    wx_open_id = models.CharField(max_length=100, blank=True, null=True)
    xcx_open_id = models.CharField(max_length=100, blank=True, null=True)
    union_id = models.CharField(max_length=100, blank=True, null=True)
    msg_type = models.CharField(max_length=50, blank=True, null=True)
    send_data = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    handle_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_wx_temp_msg'


class SDeductionCfg(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    time_interval = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    last_deduct_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_deduction_cfg'


class SDeductionDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(blank=True, null=True)
    money = models.CharField(max_length=255, blank=True, null=True)
    type_id = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    batch_no = models.CharField(max_length=20, blank=True, null=True)
    handle_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_deduction_detail'


class SOrderUseMoney(models.Model):
    order_id = models.CharField(max_length=30, blank=True, null=True)
    account = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    online_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gift_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ice_account = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ice_gift = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_use_money'

class SCardConsumeDetail(models.Model):
    card_sn = models.CharField(max_length=255)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    card_tel = models.CharField(max_length=20)
    use_money = models.DecimalField(max_digits=12, decimal_places=2)
    now_money = models.DecimalField(max_digits=12, decimal_places=2)
    order_id = models.CharField(max_length=30, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    create_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 's_card_consume_detail'

class SCardLibrary(models.Model):
    card_no = models.CharField(unique=True, max_length=20, blank=True, null=True)
    card_sn = models.CharField(unique=True, max_length=255, blank=True, null=True)
    bind_state = models.CharField(max_length=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    bind_time = models.DateTimeField(blank=True, null=True)
    is_enable = models.CharField(max_length=2, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_card_library'


class SOrderCardPre(models.Model):
    terminal_address = models.CharField(max_length=20, blank=True, null=True)
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    handle_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_card_pre'

class SOrderCardStop(models.Model):
    terminal_address = models.CharField(max_length=20, blank=True, null=True)
    eq_id = models.IntegerField()
    eq_port = models.CharField(max_length=20, blank=True, null=True)
    card_num = models.CharField(max_length=50, blank=True, null=True)
    order_id = models.CharField(max_length=30)
    state = models.CharField(max_length=2, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    handle_time = models.DateTimeField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_card_stop'


class SOrderErrorCorrection(models.Model):
    order_id = models.CharField(max_length=30)
    user_id = models.IntegerField(blank=True, null=True)
    error_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    create_date = models.DateField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    create_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 's_order_error_correction'




from .models_view import *

