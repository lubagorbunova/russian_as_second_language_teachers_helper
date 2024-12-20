import pymysql

class Basemysql():
    """
    базовый класс для работы с базой данных
    """
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
    
    
    