from lib.telebot_base import TeleBotBase, TelebotRequest, TelebotResponse, TelebotCommand
import pandas as pd
from multiprocessing import Process, Queue
import time
from lib.order_users_manager import  OrderUsersManager
from lib.orders_manager import OrdersManager
import time
from lib.orders_bot_manager import OrdersBotManager



def log(info):
    if isinstance(info,str):
        print(info)
    elif isinstance(info,dict):
        if "text" in info.keys():
            print(info["text"])

def orders_telebot_service(messageQueue: Queue, 
                           telebot_name: str,
                           telebot_api: str,
                           host: str, user:str, 
                           password: str, database: str
                           ):
    messageQueue.put("Orders telebot started")

    def add_message(mess):
        messageQueue.put(mess)

    obm = OrdersBotManager(telebot_name=telebot_name,telebot_api=telebot_api,
                           host=host,user=user,password=password,
                           database=database,repfunc=add_message)
                        
    obm.start()

if __name__ == '__main__':
    messages = Queue()
    telebot_name="MetaTteleBot"
    telebot_api="5219495110:AAE5zbY4G9Eeqqd1Gqo40qo-VivJgYblR1I"

    #telebot_name="MetaTteleDebugBot"
    #telebot_api="5432738304:AAFZ7F2lB4j-42RsWAiZcBcBV38FKhwUYhU"
    host="localhost"
    user="tradingview"
    password="Zse45tgB"
    database="trading"

    p = Process(target=orders_telebot_service, args=(messages,telebot_name,telebot_api,host,user,password,database))
    p.start()
    while True:
        while messages.qsize() > 0:
            mess = messages.get()
            log(mess)
        time.sleep(1)
        

