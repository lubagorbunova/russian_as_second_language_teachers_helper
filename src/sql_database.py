import pymysql

class RSLmysql():
    def __init__(self, host, user, database, password):
        self.host = host
        self.user = user
        self.database = database
        self.password = password
        self.connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

    def _reconnect(self):
        if self.connection.open != True:
            self.connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
    
    #чтение из базы
    def get_texts(self, chat):
        """
        возвращает список пользователей из базы
        :return: объекты типа Users
        """
        self._reconnect()
        with self.connection.cursor() as cursor:
            sql = "SELECT name, body FROM `texts` WHERE chat = %s or chat = 0"
            cursor.execute(sql, chat)
            texts = cursor.fetchall()
            res = {}
            for line in texts:
                res[line['name']] = line['body']
            return res
        

    # запись в базу
    def save_usertext(self, usertext, chat=0):
        """
        сохраняет в базу данных запрос пользователя
        :return: query_request_id
        """
        self._reconnect()
        id=0
        with self.connection:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO rsl_exgenerator.texts (`name`, `body`, `chat`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (usertext[:100], usertext, chat))
                id = cursor.lastrowid
            self.connection.commit()
        return id

    