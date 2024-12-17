import telebot 
from telebot import types
from threading import Thread
import sys
import time
from multiprocessing import Queue
from rsl_telebot.telebot_commands import TelebotCommand, TelebotRequest, TelebotResponse
from rsl_telebot.telebot_users import TelebotUser


class TeleBotBase():
    """Базовый класс для телеграм бота"""
    def __init__(self, telebot_name :str, telebot_api : str, logged_users : list, commands : dict, repfunc = None):
        self.name=telebot_name
        self.bot = telebot.TeleBot(telebot_api)
        self.logged_users=logged_users  # TelebotUser list
        self.commands=commands
        # Очередь сообщений для пользователей в формате
        self.responseQueue=Queue() 
        # Очередь команд
        self.requestQueue=Queue() 
        self.repfunc = repfunc

    def log(self,msg):
        if self.repfunc != None:
            self.repfunc(msg)


    def start(self,responseQueue :Queue ,requestQueue  :Queue):
        self.responseQueue=responseQueue
        self.requestQueue=requestQueue
        self.comm_thread = Thread(target=self.telebot_controller_run)
        self.comm_thread.start()
        self.log("Telebot controller started")

    def telebot_controller_run(self):
        self.stopped=False
        self.listen_thread = Thread(target=self.telebot_controller_listen)
        self.listen_thread.start()
        self.log("Telebot listen thread started")
        
        mess = TelebotResponse()
        user = TelebotUser()
        while self.stopped == False:
            if self.responseQueue.qsize() > 0: # есть сообщения
                while self.responseQueue.qsize() > 0:
                    try:
                        mess = self.responseQueue.get()
                        self.log("New message from bot")
                        if mess.all == True:
                            for user in self.logged_users:
                                self._send_message(user.telegram_id ,mess)
                        #elif mess.chat in self.get_all_active_users_ids():
                        #    self._send_message(mess.chat,mess)
                        elif mess.chat != "":
                            self._send_message(mess.chat,mess)
                        time.sleep(1)
                    except:
                        ex=sys.exc_info()[1]
                        self.log("Exception in controller: " + str(ex))
            time.sleep(1)

    def get_all_active_users_ids(self):
        users_id = list()
        for user in self.logged_users:   
            if user.allow_info == 1:      
                users_id.append(user.telegram_id)
        return users_id

    # Отправка сообщений клиентам
    def _send_message(self, chat, mess: TelebotResponse):
        if  len(mess.commands) > 0:
            keyboard = self.get_inline_keybords(mess.commands)
            if mess.mess_type == 'text':
                self.bot.send_message(chat, text=mess.text, reply_markup=keyboard)
            elif mess.mess_type == 'photo':
                self.bot.send_photo(chat, mess.text )
        elif len(mess.buttons) > 0:
            keyboard = self.get_keybords(mess.buttons)
            if mess.mess_type == 'text':
                self.bot.send_message(chat, text=mess.text, reply_markup=keyboard)
            elif mess.mess_type == 'photo':
                self.bot.send_photo(chat, mess.text )
        else:
            if mess.mess_type == 'text':
                self.bot.send_message(chat, mess.text ,reply_markup=types.ReplyKeyboardRemove() )
            elif mess.mess_type == 'photo':
                self.bot.send_photo(chat, mess.text )                

    def telebot_controller_listen(self):

        #@self.bot.message_handler(commands=['start', 'help'])
        #def get_started(message):
        #    self.send_commands_info(message.from_user.id)

        @self.bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            self.log("New message from user")
            if message.text == "/help":
                self.send_commands_info(message.from_user.id)
            else:
                self.requestQueue.put(TelebotRequest(chat=message.from_user.id, name=message.from_user.full_name, text=message.text))
            time.sleep(1)

        @self.bot.message_handler(content_types=['photo'])
        def get_photo(message):
            idphoto = message.photo[0].file_id
            self.requestQueue.put(TelebotRequest(chat=message.chat.id,text=idphoto, mess_type='photo'))


        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            self.log("New callback from user")
            self.requestQueue.put(TelebotRequest(chat=call.message.chat.id,text=call.data))
            self.bot.answer_callback_query(call.id)

        while self.stopped == False:
            try:
                self.bot.polling(none_stop=True, interval=0)
            except:
                ex=sys.exc_info()[1]
                self.log("Exception in listener: " + str(ex))
                time.sleep(1)

    def get_inline_keybords(self,commands):
        keyboard = types.InlineKeyboardMarkup(); #клавиатура
        for cmd in commands:
            key = types.InlineKeyboardButton(text=cmd['command_text'], callback_data=cmd['command_name']); 
            keyboard.add(key); #добавляем кнопку в клавиатуру
        return keyboard

    def get_keybords(self,commands):
        keyboard = types.ReplyKeyboardMarkup(True,selective=True); #наша клавиатура
        cmds = list()
        for cmd in commands:
            key = types.KeyboardButton(cmd.name); 
            cmds.append(key)  #добавляем кнопку в клавиатуру
            keyboard.add(key)
        return keyboard

    def send_commands_info(self,from_user_id):
        comms = self.commands.keys()
        mess="Команды управления ботом:\n"
        for c in comms:
            mess += c + " - " + self.commands[c] + "\n"
        self.bot.send_message(from_user_id,mess)



