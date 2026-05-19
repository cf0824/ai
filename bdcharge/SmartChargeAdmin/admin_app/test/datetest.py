

import datetime
import calendar


# now=datetime.datetime.now()
# print(calendar.monthrange(now.year,now.month)[1])
# month_end=datetime.datetime(now.year,now.month,calendar.monthrange(now.year,now.month)[1])
# print(now.day)

# s='20201021'
# date=datetime.datetime(int(s[0:4]),int(s[4:6]),int(s[6:8]))
# print(date)
# month_day=31
# month_end_date = datetime.datetime(date.year,date.month,month_day)
# year_begin_date = datetime.datetime(date.year,1,1)
# print(month_end_date,year_begin_date)
# print((month_end_date-year_begin_date).days)


# 计算月均预测
def calc_month_yc(date,month_sum_balance,balance):
    now_day=date.day()
    month_day=calendar.monthrange(date.year,date.month)[1]
    result=6200000-month_sum_balance-balance*(month_day-now_day)
    return round(result,2)
# 计算年均预测
def calc_year_yc(date,year_sum_balance,balance):
    now_day = date.day
    month_day = calendar.monthrange(date.year, date.month)[1]
    month_end_date = datetime.datetime(date.year,date.month,month_day)
    year_begin_date = datetime.datetime(date.year,1,1)
    month_end_year_begin_day = (month_end_date-year_begin_date).days+1
    result = 200001*month_end_year_begin_day-year_sum_balance-balance*(month_day-now_day)
    return round(result,2)

s='20201021'
date=datetime.datetime(int(s[0:4]),int(s[4:6]),int(s[6:8]))
result = calc_year_yc(date,46888299.23,21939.64)
print(result)