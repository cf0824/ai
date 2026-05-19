import logging
import os
import multiprocessing
from logging.handlers import TimedRotatingFileHandler
import time


lock = multiprocessing.Lock()


class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(MyTimedRotatingFileHandler, self).__init__(*args, **kwargs)
        self.suffix_time = ""
        self.origin_basename = self.baseFilename

    def shouldRollover(self, record):
        timeTuple = time.localtime()
        if self.suffix_time != time.strftime(self.suffix, timeTuple) or not os.path.exists(
                self.origin_basename + '.' + self.suffix_time):
            return 1
        else:
            return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTimeTuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
        self.baseFilename = self.origin_basename + '.' + self.suffix_time

        self.mode = 'a'

        global lock
        with lock:
            if self.backupCount > 0:
                for s in self.getFilesToDelete():
                    os.remove(s)

        if not self.delay:
            self.stream = self._open()

    def getFilesToDelete(self):
        # 将源代码的 self.baseFilename 改为 self.origin_basename
        dirName, baseName = os.path.split(self.origin_basename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


class MyLog:
    logger = None

    def __init__(self, name, filename='log.log', base_dir=None):
        self.logger = logging.getLogger(name)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        format = '[%(asctime)s] [%(levelname)s] [%(filename)s] [line:%(lineno)d] %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        if not base_dir:
            base_dir = os.getcwd()
        log_path = os.path.join(base_dir, "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_filepath = os.path.join(log_path, filename)
        # th = handlers.TimedRotatingFileHandler(filename=log_filepath,when='midnight',encoding='utf-8')
        th = MyTimedRotatingFileHandler(filename=log_filepath, when='midnight', encoding='utf-8')
        # th = handlers.TimedRotatingFileHandler(filename=log_filepath,when='S')
        # th.suffix='%Y-%m-%d_%H-%M-%S.log'
        th.setFormatter(logging.Formatter(format, datefmt))
        self.logger.addHandler(th)
        console = logging.StreamHandler()
        # console.setLevel(logging.INFO)
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(format, datefmt))
        self.logger.addHandler(console)


def getLogger(name):
    mylog = MyLog(name)
    return mylog.logger


log = getLogger(__name__)


def test(num):
    i = 0
    while True:
        log.info('pid=%s,times=%s' % (num, i))
        i += 1
        time.sleep(1)


if __name__ == '__main__':

    # 测试
    pool = multiprocessing.Pool(processes=3)

    for i in range(3):
        pool.apply_async(func=test, args=(i,))
    pool.close()
    pool.join()
    print('完毕')
