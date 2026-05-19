import datetime

axis=[]
data=[]
now = datetime.datetime.now()
tmp_dt = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,microseconds=now.microsecond)
for i in range(int(60*24/5)):
    tmp_dt.strftime('%H:%M')
    axis.append(tmp_dt.strftime('%H:%M'))
    tmp_dt = tmp_dt+datetime.timedelta(minutes=5)

# print(axis)

if []:
    print('1')
else:
    print('2')