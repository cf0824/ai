# from charge.utils.eq_api.tieta_api import TietaApi

import datetime

now_hour = 23
begin_hour = now_hour + 1
labels = [f"{str(item).rjust(2, '0')}时" for item in range(begin_hour, 24)] + [f"{str(item).rjust(2, '0')}时" for item in range(0, now_hour + 1)]

print(labels, len(labels))