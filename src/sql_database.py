import pymysql
import re

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

    def _crop(self, text, length):
        if text:
            text = bytes(str(text), 'utf-8').decode('utf-8', 'ignore')
            text = re.sub(r'[^\w,.:;!?]', ' ', text)
            text = text[:length]
        else:
            text = ''
        return text

    def _reconnect(self):
        if self.connection.open != True:
            self.connection = pymysql.connect(host=self.host,
                                     user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
    
    #чтение из базы
    def get_texts(self):
        """
        возвращает список пользователей из базы
        :return: объекты типа Users
        """
        self._reconnect()
        with self.connection.cursor() as cursor:
            sql = "SELECT name, body FROM `texts`"
            cursor.execute(sql)
            texts = cursor.fetchall()
            res = {}
            for line in texts:
                res[line['name']] = line['body']
            return res

    def create_user(self, name, user_id):
        """
        регистрирует в базе нового пользователя.
        Параметры: name, user_id
        """
        self._reconnect()
        with self.connection:
            with self.connection.cursor() as cursor:
                sql = "INSERT INTO seobot.users (`user_id`, `name`) VALUES (%s, %s)"
                cursor.execute(sql, (name, user_id))
            self.connection.commit()
        
    # запись в базу
    def save_query_request(self, request):
        """
        сохраняет в базу данных запрос пользователя
        :return: query_request_id
        """
        self._reconnect()
        id=0
        with self.connection:
            with self.connection.cursor() as cursor:
                # Create a new record
                sql = "INSERT INTO seobot.query_request (`user_id`, `lang`, `search_engine`, `query`, `how_many_pages`, " \
                      "`target_page`) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (self._crop(request.user_id, 45), 
                                     self._crop(request.lang, 4), 
                                     self._crop(request.search_engine, 45), 
                                     self._crop(request.query, 500),
                                     request.how_many_pages, 
                                     self._crop(request.target_page, 500)))
                id = cursor.lastrowid
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            self.connection.commit()
        return id

    