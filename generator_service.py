import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
from lib.orders_bot_manager import OrdersBotManager
from threading import Thread
from multiprocessing import Process
import sys
from orders_bot import orders_telebot_service
from multiprocessing import Process, Queue
import time
from lib.telebot_commands import TelebotCommand, TelebotRequest, TelebotResponse
from lib.telebot_users import TelebotUser

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "TradingTeleBotViewer"
    _svc_display_name_ = "TradingTeleBotViewer"
    _telebot_name="MetaTteleBot"
    _telebot_api="5219495110:AAE5zbY4G9Eeqqd1Gqo40qo-VivJgYblR1I",

    #_telebot_name="MetaTteleDebugBot"
    #_telebot_api="5432738304:AAFZ7F2lB4j-42RsWAiZcBcBV38FKhwUYhU"
    _host="localhost"
    _user="tradingview"
    _password="Zse45tgB"
    _database="trading"


    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.listen_thread= None
        self.process = None
        self.started = False

    def SvcStop(self):
        self.started = False
        self.process.terminate()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STOPPED,
                              (self._svc_name_,''))
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.started = True
        self.main()


    def add_event(self,info):
        if isinstance(info,str):
            self.info(info)
        elif isinstance(info,dict):
            if "text" in info.keys() and "type" in info.keys():
                if info['type'] == "error":
                    self.error(info['text'])
                elif info['type'] == "warning":
                    self.warning(info['text'])
                else:
                    self.info(info['text'])

    def info(self,info):
        servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                0xF000, #  generic message
                (info, ''))
         
    def error(self,info):
         servicemanager.LogMsg(
                servicemanager.EVENTLOG_ERROR_TYPE,
                0xF000, #  generic message
                (info, '')
                ) 
         
    def warning(self,info):
         servicemanager.LogMsg(
                servicemanager.EVENTLOG_WARNING_TYPE,
                0xF000, #  generic message
                (info, '')
                )          

    def main(self):
        self.info('Start main service')
        self.info('Create ordersBotManager')
        try:
            messages = Queue()
            self.process = Process(target=orders_telebot_service, args=(messages,
                                                                        self._telebot_name,
                                                                        self._telebot_api,
                                                                        self._host,
                                                                        self._user,
                                                                        self._password,
                                                                        self._database))
            self.process.start()
            while self.started:
                while messages.qsize() > 0:
                    mess = messages.get()
                    self.add_event(mess)
                time.sleep(1)
        except:
            ex=sys.exc_info()[1]
            self.error("Exception in main service:" + str(ex))
            time.sleep(1)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)