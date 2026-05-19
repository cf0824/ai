"""
检测文件是否运行
"""
import time

import psutil
import os

# 可能存在重复文件名情况 应避免
def check_run(processname):
    pl = psutil.pids()
    flag = False
    for pid in pl:
        try:
            tmpprcname = psutil.Process(pid).cmdline()
        except Exception as e:
            print(e)
            continue
        for procname in tmpprcname:
            if processname in procname and "grep" not in procname:
                if os.getpid() != pid:
                    flag = True
                    break
        if flag:
            break
    else:
        print("not found")
    return flag


if __name__ == "__main__":
    res = check_run(__file__)
    print('res=',res)
    time.sleep(10)