import pymysql


class DBBase:
    def __init__(self, host, port, user, password, dbname, charset='utf8mb4'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.charset = charset
        self.db = pymysql.Connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.password,
            db=self.dbname,
            charset=self.charset
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def get_db(self):
        try:
            self.db.ping(reconnect=True)
        except:
            self.__init__(self.host, self.port, self.user, self.password, self.dbname, self.charset)
        return self.db

    def get_cursor(self):
        db = self.get_db()
        cursor = db.cursor()
        return cursor

    def close_cursor(self, cursor):
        try:
            cursor.close()
        except:
            pass
