"""
数据相关接口
"""
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：SmartChargeBD 
@File    ：information.py.py
@IDE     ：PyCharm 
@Author  ：marverdol
@Date    ：2025/3/17 9:27 
@Description :
'''
import json
import time

from django.db import transaction
from django.db.models import F

from app.models import SUserInfo, SWxTranDetail
from app.models_view import ViewUserAccountOk
from app.utils.comm import api_handle
from app.utils import token_handle, Error
from SmartChargeBD.settings import WX_XCX_TOKEN_EXP_TIME
from app.models import *
from django.db.models import Count, Sum, Case, When, Q
from django.db.models.functions import TruncMonth, TruncDay, TruncYear, TruncHour
from django.utils import timezone
from django.db.models.functions import Coalesce
import datetime
from django.core.paginator import Paginator
from django.db.models import Sum
from decimal import Decimal
from app.utils import wx
from app.utils import get_seq
from app.utils import wx_pay
from app.utils import handle
from app.utils import time_range

from app.utils import MyLog

log = MyLog.log

# 系统通用处理
def sys_handle(request):
    gb = globals()
    return api_handle(request, gb)


def test(request, data, resp):
    print('test')
    return resp


# 获取运维页面详情
def get_OM_detail(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR

    def get_eq_count_by_site(site_id):
        result = SEqInfo.objects.filter(site_id=site_id).aggregate(
            total=Count('eq_id'),  # 总设备数
            online=Count(Case(When(conn_state='1', then=1))),  # 在线设备数
            error=Count(Case(When(eq_state='-1', then=1)))  # 故障设备数
        )
        return result['total'], result['online'], result['error']

    def get_eq_use_state_by_site(site_id):
        # 查设备
        eqs = SEqInfo.objects.filter(site_id=site_id, conn_state='1', state='1')
        free_count = 0
        using_count = 0
        for eq in eqs:
            port_info = SEqPort.objects.filter(eq_id=eq.eq_id, use_state='1')
            if port_info.exists():
                using_count += 1
            else:
                free_count += 1

        return free_count, using_count



    # from django.db.models import Count, Case, When, Q



    def get_user_order_stats(user_id, start_time=None, end_time=None):
        """
        获取用户订单统计信息（支持自定义时间范围）

        :param user_id: 用户ID
        :param start_time: 起始时间（带时区的datetime对象，可选）
        :param end_time: 结束时间（带时区的datetime对象，可选）
        :return: (总订单数, 时间范围内订单数, 总收入, 时间范围内收入)
        """
        log.info(f'查询订单统计信息：{user_id}, {start_time}, {end_time}')
        # 基础查询集
        queryset = SDisProfitDetail.objects.filter(user_id=user_id)

        queryset_deduct = SDeductionDetail.objects.filter(user_id=user_id)

        # 构建时间过滤条件
        time_filter = Q()
        if start_time:
            time_filter &= Q(create_time__gte=start_time)
        if end_time:
            time_filter &= Q(create_time__lt=end_time)

        # 单次聚合查询
        result = queryset.aggregate(
            total_orders=Count('id'),  # 总订单数
            total_income=Coalesce(Sum('dis_money'), 0.0),  # 总收入（处理空值）
            filtered_orders=Count(Case(When(time_filter, then=1))),  # 时间范围内订单数
            filtered_income=Coalesce(
                Sum('dis_money', filter=time_filter),  # 时间范围内收入
                0.0
            )
        )

        result_deduct = queryset_deduct.aggregate(
            total_deduct=Coalesce(Sum('money'), 0.0),
            filtered_deduct=Coalesce(Sum('money', filter=time_filter),
                                     0.0)
        )
        result['total_income'] = result['total_income'] - result_deduct['total_deduct']
        result['filtered_income'] = result['filtered_income'] - result_deduct['filtered_deduct']

        return (
            result['total_orders'],
            result['filtered_orders'],
            result['total_income'],
            result['filtered_income']
        )


    # 调用示例：获取自定义时间范围统计
    def get_custom_range_stats(user_id, start_time, end_time):
        """获取自定义日期范围统计（自动处理时区）"""
        # start_time = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
        # end_time = timezone.make_aware(
        #     timezone.datetime.combine(end_date, timezone.datetime.min.time())) + timezone.timedelta(days=1)

        return get_user_order_stats(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time
        )

    # undivided
    def get_undivided_profit(user_id):
        profit_detail = SDisProfitDetail.objects.filter(user_id=user_id, state='0')
        total_amount = (
                           SDisProfitDetail.objects
                           .filter(user_id=user_id, state='0')  # 过滤未转账记录
                           .aggregate(total=Sum('dis_money'))  # 对金额字段求和（假设金额字段名为 amount）
                       )['total'] or 0

        deduct_amount = (
                           SDeductionDetail.objects
                           .filter(user_id=user_id, state='0')  # 过滤未转账记录
                           .aggregate(total=Sum('money'))  # 对金额字段求和（假设金额字段名为 amount）
                       )['total'] or 0
        return total_amount - deduct_amount

        # 查询该用户属于哪个站点
    site_info = SDisProfitCfg.objects.filter(user_id=user_id)
    log.info(f'该用户所属站点：{site_info}')
    site_count = site_info.count()
    # 查询站点设备总数
    eq_count = 0
    eq_online_count = 0
    eq_error_count = 0
    eq_free_count = 0
    eq_using_count = 0
    for site in site_info:
        eq_count_, eq_online_count_, eq_error_count_ = get_eq_count_by_site(site.site_id)
        log.info(f'站点：{site.site_id}, eq_count_: {eq_count_}, eq_online_count_: {eq_online_count_}, eq_error_count_: {eq_error_count_}')
        eq_count += eq_count_
        eq_online_count += eq_online_count_
        eq_error_count += eq_error_count_
        free_count_, using_count_ = get_eq_use_state_by_site(site.site_id)
        eq_free_count += free_count_
        eq_using_count += using_count_
        log.info(f'空闲：{free_count_}, 使用中：{using_count_}')


    # 查询订单数量
    now = datetime.datetime.now()  # 当前时间
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timezone.timedelta(days=1)
    total_orders_, today_orders_, total_income_, today_income_ = get_custom_range_stats(user_id, today_start, today_end)
    log.info(f'total_orders_: {total_orders_}, today_orders_: {today_orders_}, total_income_: {total_income_}, today_income_: {today_income_}')
    # 昨天订单
    yesterday_start = (now - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + datetime.timedelta(days=1)
    y_total_orders_, yesterday_orders_, y_total_income_, yesterday_income_ = get_custom_range_stats(user_id, yesterday_start, yesterday_end)
    log.info(f'y_total_orders_: {y_total_orders_}, yesterday_orders_: {yesterday_orders_}, y_total_income_: {y_total_income_}, yesterday_income_: {yesterday_income_}')
    if today_income_ > yesterday_income_:
        today_income_state = 'up'
    elif today_income_ == yesterday_income_:
        today_income_state = 'equal'
    else:
        today_income_state = 'down'
    if today_orders_ > yesterday_orders_:
        today_order_state = 'up'
    elif today_orders_ == yesterday_orders_:
        today_order_state = 'equal'
    else:
        today_order_state = 'down'

    undivided_profit = get_undivided_profit(user_id)

    resp['site_count'] = site_count
    resp['eq_count'] = eq_count
    resp['eq_online_count'] = eq_online_count
    resp['eq_error_count'] = eq_error_count
    resp['eq_free_count'] = eq_free_count
    resp['eq_using_count'] = eq_using_count
    resp['total_orders'] = total_orders_
    resp['today_orders'] = today_orders_
    resp['total_income'] = total_income_
    resp['today_income'] = today_income_
    resp['yesterday_orders'] = yesterday_orders_
    resp['yesterday_income'] = yesterday_income_
    resp['today_income_state'] = today_income_state
    resp['today_order_state'] = today_order_state
    resp['undivided_profit'] = undivided_profit

    resp['online_rate'] = round(eq_online_count / eq_count, 2) * 100 if eq_count > 0 else 0
    resp['using_rate'] = round(eq_using_count / eq_online_count, 2) * 100 if eq_using_count > 0 else 0
    resp['free_rate'] = round(eq_free_count / eq_online_count, 2) * 100 if eq_free_count > 0 else 0
    return resp


def get_my_earnings(request, data, resp):
    user_id = data.get('user_id')
    year = data.get('year')
    month = data.get('month')
    day = data.get('day')
    if not user_id or not year:
        return Error.REQ_PARAMS_ERROR

    # ------获取收益信息-------
    def get_yearly_profit(user_id, year):
        results = SDisProfitDetail.objects.filter(
            user_id=user_id,
            create_time__year=year
        ).annotate(
            month=TruncMonth('create_time')  # 将时间截断到月
        ).values('month').annotate(
            total=Sum('order_money'),
            my_profit=Sum('dis_money')
        ).order_by('month')
        result_dict = {item['month'].month: {'total': item['total'], 'my_profit': item['my_profit']} for item in results}
        # total_list = []
        # my_list = []
        # for item in results:
        #     total_list.append(item['total'])
        #     my_list.append(item['my_profit'])
        return result_dict

    def get_monthly_profit(user_id, year, month):
        results = SDisProfitDetail.objects.filter(
            user_id=user_id,
            create_time__year=year,
            create_time__month=month
        ).annotate(
            day=TruncDay('create_time')  # 将时间截断到日
        ).values('day').annotate(
            total=Sum('order_money'),
            my_profit=Sum('dis_money')
        ).order_by('day')
        result_dict = {item['day'].day: {'total': item['total'], 'my_profit': item['my_profit']} for item in results}
        # total_list = []
        # my_list = []
        # for item in results:
        #     total_list.append(item['total'])
        #     my_list.append(item['my_profit'])
        return result_dict

    def get_dayly_profit(user_id, year, month, day):
        results = SDisProfitDetail.objects.filter(
            user_id=user_id,
            create_time__year=year,
            create_time__month=month,
            create_time__day=day
        ).annotate(
            hour=TruncHour('create_time')  # 将时间截断到日
        ).values('hour').annotate(
            total=Sum('order_money'),
            my_profit=Sum('dis_money')
        ).order_by('hour')
        result_dict = {item['hour'].hour: {'total': item['total'], 'my_profit': item['my_profit']} for item in results}
        # total_list = []
        # my_list = []
        # for item in results:
        #     total_list.append(item['total'])
        #     my_list.append(item['my_profit'])
        return result_dict

    if year and month and day:
        log.info(f'查询日收益')
        granularity = 'day_hours'
        profit_dict = get_dayly_profit(user_id, year, month, day)
    elif year and month and not day:
        log.info(f'查询月收益')
        granularity = 'month_days'
        profit_dict = get_monthly_profit(user_id, year, month)
    elif year and not month and not day:
        log.info(f'查询年收益')
        granularity = 'year_months'
        profit_dict = get_yearly_profit(user_id, year)
    else:
        return Error.REQ_PARAMS_ERROR
    year = int(year) if year else None
    month = int(month) if month else None
    day = int(day) if day else None
    timerange = time_range.generate_time_ranges(granularity, year, month, day)
    time_list = []
    if granularity == 'day_hours':
        for item in timerange:
            time_list.append(item.hour)
    if granularity == 'month_days':
        for item in timerange:
            time_list.append(item.day)
    if granularity == 'year_months':
        for item in timerange:
            time_list.append(item.month)
    log.info(f'日期列表： {time_list}')
    log.info(f'收益字典： {profit_dict}')

    total_list = []
    my_list = []
    for item in time_list:
        log.info(f'item:{item}')
        data = profit_dict.get(item, {})
        total = data.get('total', 0.00)
        my_profit = data.get('my_profit', 0.00)
        total_list.append(total)
        my_list.append(my_profit)
    log.info(f'总收益列表： {total_list}')
    log.info(f'我的收益列表： {my_list}')

    series = [
        {
            "name": "我的收益",
            "data": my_list
        },
        {
            "name": "总收益",
            "data": total_list
        }
    ]
    resp['categories'] = time_list
    resp['series'] = series

    return resp


def get_repair_list(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    state = data.get('state', '0')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    repairs_info = SRepairInfo.objects.filter(state=state).order_by('-id')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        repairs_info = repairs_info.filter(create_time__gte=begin_date, create_time__lt=end_date)
    list_order = []
    for i in repairs_info:
        id = i.id
        eq_id = i.eq_id
        create_time = i.create_time
        repair_type = i.repair_type
        repair_tel = i.repair_tel
        state = i.state
        if repair_type:
            repair = SRepairKv.objects.filter(repair_key=repair_type).first()
            repair_name = repair.repair_label if repair else ''
        else:
            repair_name = ''
        list_order.append(
            {
                "id": id,
                "create_time": create_time,
                "eq_id": eq_id,
                "repair_type": repair_name,
                "repair_tel": repair_tel,
                "state": state
            }
        )

    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp

def get_repair_detail(request, data, resp):
    user_id = data.get('user_id')
    repair_id = data.get('repair_id')
    if not (user_id and repair_id):
        return Error.REQ_PARAMS_ERROR
    repair_info = SRepairInfo.objects.filter(id=repair_id).first()
    if repair_info:
        id = repair_info.id
        state = repair_info.state
        create_time = repair_info.create_time
        eq_id = repair_info.eq_id
        repair_type = repair_info.repair_type
        if repair_type:
            repair = SRepairKv.objects.filter(repair_key=repair_type).first()
            repair_name = repair.repair_label if repair else ''
        else:
            repair_name = ''
        repair_tel = repair_info.repair_tel
        other_text = repair_info.other_type_text
        image_list = []
        imgUrls = []
        feedImgList = repair_info.repair_img
        if feedImgList:
            image_list = json.loads(feedImgList.replace("'", '"'))
        reply = repair_info.reply
        reply_img = repair_info.reply_img
        if reply_img:
            imgUrls = json.loads(reply_img.replace("'", '"'))

        resp["id"] = id
        resp["state"] = state
        resp["create_time"] = create_time
        resp["eq_id"] = eq_id
        resp["repair_type"] = repair_name
        resp["repair_tel"] = repair_tel
        resp["other_text"] = other_text
        resp["feedImgList"] = image_list
        resp["reply"] = reply
        resp["imgUrls"] = imgUrls

    return resp

def handle_repair(request, data, resp):
    user_id = data.get('user_id')
    repair_id = data.get('repair_id')
    reply = data.get("reply")
    reply_img = data.get("imgUrls")
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    try:
        SRepairInfo.objects.filter(id=repair_id).update(
            state='1',
            handle_time=datetime.datetime.now(),
            reply_img=reply_img,
            handle_user_id=user_id,
            reply=reply
        )
    except Exception as e:
        log.error(f'{e}', exc_info=True)
    resp['success'] = True
    return resp

def get_feedback_list_order_admin(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    state = data.get('state', '0')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    feedbacks_info = SFeedbackDetail.objects.filter(feed_type='complain', state=state).order_by('-id')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        feedbacks_info = feedbacks_info.filter(create_time__gte=begin_date, create_time__lt=end_date)
    list_order = []
    for i in feedbacks_info:
        id = i.id
        create_time = i.create_time
        order_id = i.order_id
        eq_id = i.eq_id
        eq_port = i.eq_port
        state = i.state
        list_order.append(
            {
                "id": id,
                "create_time": create_time,
                "eq_id": eq_id,
                "order_id": order_id,
                "eq_port": eq_port,
                "state": state
            }
        )

    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp

def get_order_list_admin(request, data, resp): # 获取运行中的订单。。
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    state = data.get('state', '1')

    eq_id = data.get('eq_id')
    order_id = data.get('order_id')

    if not user_id:
        return Error.REQ_PARAMS_ERROR

    orders_info = SOrderInfo.objects.filter(state=state).order_by('-begin_time')  # 1-充电中
    log.info(f'{len(orders_info)}')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        orders_info = orders_info.filter(begin_time__gte=begin_date, begin_time__lt=end_date)
    if eq_id:
        orders_info = orders_info.filter(eq_id=eq_id)
    if order_id:
        orders_info = orders_info.filter(order_id=order_id)
        
    list_order = []
    i = 0
    for item in orders_info:
        i = i + 1
        if i> 1000:
            break

        id = item.order_id
        create_time = item.begin_time
        order_id = item.order_id
        eq_id = item.eq_id
        eq_port = item.eq_port
        state = item.state
        list_order.append(
            {
                "id": id,
                "create_time": create_time,
                "eq_id": eq_id,
                "order_id": order_id,
                "eq_port": eq_port,
                "state": state
            }
        )

    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp


def get_feedback_detail_order_admin(request, data, resp):
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    if not (user_id and feedback_id):
        return Error.REQ_PARAMS_ERROR
    feedback_info = SFeedbackDetail.objects.filter(id=feedback_id).first()
    if feedback_info:
        id = feedback_info.id
        state = feedback_info.state
        create_time = feedback_info.create_time
        order_id = feedback_info.order_id
        eq_id = feedback_info.eq_id
        eq_port = feedback_info.eq_port
        user_tel = feedback_info.user_tel
        feedback_content = feedback_info.feedback_content
        feedImgList = feedback_info.feedback_img
        reply = feedback_info.reply
        imgUrl = feedback_info.reply_img
        image_list = []
        imgUrls = []
        if feedImgList:
            image_list = json.loads(feedImgList.replace("'", '"'))

        if imgUrl:
            imgUrls = json.loads(imgUrl.replace("'", '"'))

        resp["id"] = id
        resp["state"] = state
        resp["create_time"] = create_time
        resp["order_id"] = order_id
        resp["eq_id"] = eq_id
        resp["eq_port"] = eq_port
        resp["user_tel"] = user_tel
        resp["feedback_content"] = feedback_content
        resp["feedImgList"] = image_list
        resp["reply"] = reply
        resp["imgUrls"] = imgUrls

    return resp

def handle_feedback_order_admin(request, data, resp):
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    reply = data.get("reply")
    reply_img = data.get("imgUrls")
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    try:
        SFeedbackDetail.objects.filter(id=feedback_id).update(
            state='1',
            reply_time=datetime.datetime.now(),
            reply_img=reply_img,
            handle_user_id=user_id,
            reply=reply
        )
    except Exception as e:
        log.error(f'{e}', exc_info=True)
    resp['success'] = True
    return resp

def get_feedback_list_opinion_admin(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')
    state = data.get('state', '0')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    feedbacks_info = SFeedbackDetail.objects.filter(feed_type='opinion', state=state).order_by('-id')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        feedbacks_info = feedbacks_info.filter(create_time__gte=begin_date, create_time__lt=end_date)
    list_order = []
    for i in feedbacks_info:
        id = i.id
        create_time = i.create_time
        state = i.state
        user_tel = i.user_tel
        feedback_content = i.feedback_content
        list_order.append(
            {
                "id": id,
                "create_time": create_time,
                "user_tel": user_tel,
                "feedback_content": feedback_content,
                "state": state
            }
        )

    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp


def get_feedback_detail_opinion_admin(request, data, resp):
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    if not (user_id and feedback_id):
        return Error.REQ_PARAMS_ERROR
    feedback_info = SFeedbackDetail.objects.filter(id=feedback_id).first()
    if feedback_info:
        id = feedback_info.id
        state = feedback_info.state
        create_time = feedback_info.create_time
        user_tel = feedback_info.user_tel
        feedback_content = feedback_info.feedback_content
        feedImgList = feedback_info.feedback_img
        reply = feedback_info.reply
        imgUrl = feedback_info.reply_img
        image_list = []
        imgUrls = []
        if feedImgList:
            image_list = json.loads(feedImgList.replace("'", '"'))

        if imgUrl:
            imgUrls = json.loads(imgUrl.replace("'", '"'))

        resp["id"] = id
        resp["state"] = state
        resp["create_time"] = create_time
        resp["user_tel"] = user_tel
        resp["feedback_content"] = feedback_content
        resp["feedImgList"] = image_list
        resp["reply"] = reply
        resp["imgUrls"] = imgUrls

    return resp

def handle_feedback_opinion_admin(request, data, resp):
    user_id = data.get('user_id')
    feedback_id = data.get('feedback_id')
    reply = data.get("reply")
    reply_img = data.get("imgUrls")
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    try:
        SFeedbackDetail.objects.filter(id=feedback_id).update(
            state='1',
            reply_time=datetime.datetime.now(),
            reply_img=reply_img,
            handle_user_id=user_id,
            reply=reply
        )
    except Exception as e:
        log.error(f'{e}', exc_info=True)
    resp['success'] = True
    return resp


def get_site_list_admin(request, data, resp):
    user_id = data.get('user_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    page = data.get('page', 1)
    search_term = data.get('search_term')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    # 该用户负责的站点
    site_list = SSiteUser.objects.filter(user_id=user_id).values_list('site_id', flat=True)
    if search_term:
        site_info = SSiteInfo.objects.filter(site_id__in=site_list, site_name__contains=search_term, state='1').order_by('-site_id')
    else:
        site_info = SSiteInfo.objects.filter(site_id__in=site_list, state='1').order_by('-site_id')
    list_site = []
    for i in site_info:
        site_id = i.site_id
        site_name = i.site_name
        site_address = i.site_address
        eq_info = SEqInfo.objects.filter(site_id=site_id)
        pile_num = eq_info.count()
        port_num = 0
        for item in eq_info:
            port_num_ = SEqPort.objects.filter(eq_id=item.eq_id).count()
            port_num = port_num + port_num_

        list_site.append(
            {
                "site_id": site_id,
                "site_name": site_name,
                "site_address": site_address,
                "pile_num": pile_num,
                "port_num": port_num
            }
        )

    paginator = Paginator(list_site, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_site)
    resp['list_site'] = list_page_data
    return resp

def get_site_detail(request, data, resp):
    user_id = data.get('user_id')
    site_id = data.get('site_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    site_info = SSiteInfo.objects.filter(site_id=site_id)
    site_name = site_info[0].site_name
    site_address = site_info[0].site_address
    pile_list = []
    eq_info = SEqInfo.objects.filter(site_id=site_id)
    for item in eq_info:
        port_list = []
        state = None
        state_text = None
        port_info = SEqPort.objects.filter(eq_id=item.eq_id)
        for i in port_info:
            port_no = i.eq_port
            conn_state = i.conn_state
            if conn_state == '1':
                if i.state == '-1':
                    state = '-1'
                    state_text = '异常'
                elif i.state == '1':
                    if i.use_state == '0':
                        state = '0'
                        state_text = '空闲'
                    elif i.use_state == '1':
                        state = '1'
                        state_text = '占用'
            elif conn_state == '0':
                state = '-1'
                state_text = '离线'
            port_info = {
                'id': i.id,
                'port_no': port_no,
                'state': state,
                'state_text': state_text
            }
            port_list.append(port_info)
        pile_list.append(
            {
                'terminal_address': item.terminal_address,
                'eq_id': item.eq_id,
                'portlist': port_list
            }
        )
    resp['site_name'] = site_name
    resp['site_address'] = site_address
    resp['pilelist'] = pile_list
    return resp

@transaction.atomic()
def add_site_info(request, data, resp):
    user_id = data.get('user_id')
    site_id = data.get('site_id')
    site_name = data.get('site_name')
    site_address = data.get('site_address')
    pile_list = data.get('pile_list')

    if not (user_id and site_name and site_address):
        return Error.REQ_PARAMS_ERROR
    if not site_id:  # 没有有电站id,新增
        # 创建电站
        site_info = SSiteInfo.objects.create(
            site_name=site_name,
            site_address=site_address,
            create_time=datetime.datetime.now(),
            state='1'
        )
        for item in pile_list:
            eq_info = SEqInfo.objects.create(
                site_id=site_info.site_id,
                terminal_address=item.get('terminal_address'),
                eq_state='1',
                state='1',
                create_time=datetime.datetime.now()
            )
            port_list = item.get('portlist')
            for i in port_list:
                port_info = SEqPort.objects.create(
                    eq_id=eq_info.eq_id,
                    terminal_address=item.get('terminal_address'),
                    use_state='0',
                    eq_port=i.get('port_no'),
                    state='1'
                )
    elif site_id:  # 有电站id，执行更新
        site_info = SSiteInfo.objects.filter(site_id=site_id).update(
            site_name=site_name,
            site_address=site_address
        )
    resp['success'] = True
    return resp


# 删除设备
@transaction.atomic()
def del_eq_info(request, data, resp):
    user_id = data.get('user_id')
    terminal_address = data.get('terminal_address')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    eq_info = SEqInfo.objects.get(terminal_address=terminal_address)
    port_info = SEqPort.objects.filter(terminal_address=terminal_address)
    eq_info.delete()
    port_info.delete()
    resp['success'] = True
    return resp

def update_eq_info(request, data, resp):
    user_id = data.get('user_id')
    operator_type = data.get('operator_type')
    site_id = data.get('site_id')
    if not user_id:
        return Error.REQ_PARAMS_ERROR
    terminal_address = data.get('terminal_address')
    port_list = data.get('port_list')
    if operator_type == 'add':
        eq_exist = SEqInfo.objects.filter(terminal_address=terminal_address).exists()
        if eq_exist:
            resp['success'] = False
            resp['tip'] = '设备已存在'
            return resp
        eq_info = SEqInfo.objects.create(
            site_id=site_id,
            terminal_address=terminal_address,
            eq_state='1',
            state='1',
            create_time=datetime.datetime.now()
        )
        for i in port_list:
            port_info = SEqPort.objects.create(
                eq_id=eq_info.eq_id,
                terminal_address=terminal_address,
                eq_port=i.get('port_no'),
                state='1'
            )
    elif operator_type == 'edit':
        eq_info = SEqInfo.objects.filter(terminal_address=terminal_address)
        eq_id = eq_info[0].eq_id
        existing_ports = set(
            SEqPort.objects.filter(terminal_address=terminal_address)
            .values_list('eq_port', flat=True)
        )
        current_ports = {p['port_no'] for p in port_list}
        to_delete = existing_ports - current_ports
        to_create = current_ports - existing_ports
        log.info(f'已有插座：{existing_ports}, 最新插座列表： {current_ports}')
        log.info(f'需删除的插座： {to_delete}， 需添加的插座： {to_create}')
        with transaction.atomic():
            # 删除数据库中多余的端口
            if to_delete:
                SEqPort.objects.filter(
                    terminal_address=terminal_address,
                    eq_port__in=to_delete
                ).delete()

            # 批量创建新增的端口
            # 按数值从小到大排序
            to_create = sorted(to_create, key=lambda x: int(x))
            log.info(f'排序后的新增插座：{to_create}')
            new_ports = [
                SEqPort(terminal_address=terminal_address, eq_port=eq_port, eq_id=eq_id, state='1')
                for eq_port in to_create
            ]
            if new_ports:
                SEqPort.objects.bulk_create(new_ports)
    resp['success'] = True
    return resp



def get_disprofit_record_list(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')

    if not user_id:
        return Error.REQ_PARAMS_ERROR
    disprofits_info = SDisProfitRecord.objects.filter(user_id=user_id).order_by('-id')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        disprofits_info = disprofits_info.filter(profit_time__gte=begin_date, profit_time__lt=end_date)
    list_disprofit = []
    for i in disprofits_info:
        id = i.id
        profit_time = i.profit_time
        profit_no = i.profit_no
        # evidence_img = i.evidence_img
        profit_money = i.profit_money


        list_disprofit.append(
            {
                "id": id,
                "profit_time": profit_time,
                "profit_no": profit_no,
                "profit_money": profit_money
            }
        )

    paginator = Paginator(list_disprofit, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_disprofit)
    resp['list_disprofit'] = list_page_data
    return resp


def get_disprofit_record_detail(request, data, resp):
    user_id = data.get('user_id')
    profit_no = data.get('profit_no')
    if not (user_id and profit_no):
        return Error.REQ_PARAMS_ERROR
    disprofit_info = SDisProfitRecord.objects.filter(profit_no=profit_no).first()
    if disprofit_info:
        id = disprofit_info.id
        evidence_imgs = disprofit_info.evidence_img
        profit_money = disprofit_info.profit_money
        profit_time = disprofit_info.profit_time

        # imgUrl = disprofit_info.reply_img
        image_list = []
        if evidence_imgs:
            image_list = json.loads(evidence_imgs.replace("'", '"'))

        resp["id"] = id
        resp["profit_money"] = profit_money
        resp["profit_time"] = profit_time
        resp["feedImgList"] = image_list


    return resp




def get_charge_order_list(request, data, resp):
    user_id = data.get('user_id')
    page = data.get('page', 1)
    begin_date = data.get('begin_date')
    end_date = data.get('end_date')

    if not user_id:
        return Error.REQ_PARAMS_ERROR
    orders_info = SOrderInfo.objects.order_by('-create_time')
    if begin_date and end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
        # “大于或等于”（greater than or equal）,“小于”（less than）
        orders_info = orders_info.filter(create_time__gte=begin_date, create_time__lt=end_date)
    list_order = []
    for i in orders_info:
        order_id = i.order_id
        create_time = i.create_time
        pay_way = i.pay_way
        charge_type = i.charge_type
        state = i.state
        use_money = i.use_money


        list_order.append(
            {
                "order_id": order_id,
                "create_time": create_time,
                "pay_way": pay_way,
                "charge_type": charge_type,
                "state": state,
                "use_money": use_money
            }
        )

    paginator = Paginator(list_order, 10)
    list_page_data = paginator.page(page).object_list
    resp['num_pages'] = paginator.num_pages
    resp['list_len'] = len(list_order)
    resp['list_order'] = list_page_data
    return resp


def refund_order_money(request, data, resp):
    user_id = data.get('user_id')
    order_id = data.get('order_id')


    if not user_id:
        return Error.REQ_PARAMS_ERROR
    order_info = SOrderInfo.objects.filter(order_id=order_id).first()
    user_info = SUserInfo.objects.filter(user_id=user_id).first()


    if order_info.refund_state == '9':
        resp['success'] = False
        resp['tip'] = '该订单已全额退款！'
        return resp

    order_use_money = SOrderUseMoney.objects.filter(order_id=order_id).first()
    user_account = ViewUserAccountOk.objects.filter(user_id=user_id).first()

    account = order_use_money.account
    gift_money = order_use_money.gift_money

    user_account = user_account.filter(account=account)

    user_account.real_money += account
    user_account.ok_money += account
    user_account.gift_money += gift_money
    user_account.save()
    user_info.account += account
    user_info.save()
    order_info.refund_state = '9'
    order_info.save()

    resp['success'] = True
    return resp
