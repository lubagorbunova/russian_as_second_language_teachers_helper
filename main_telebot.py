from rsl_telebot.telebot_base import TeleBotBase
from multiprocessing import Queue
from rsl_telebot.telebot_commands import TelebotRequest, TelebotResponse, TelebotCommand
import time
from src.exercise import SentProcessor, Exercise
from nltk.tokenize import sent_tokenize
import random
from src.constants import ui_texts
from src.sql_database import RSLmysql

connected_users = []
telebot_api = '7828918234:AAHANMlaM2a2hBUyiL1b8k899N5Ho65yyDQ'
telebot_name = 'rsl_exercise_teacher_helper_bot'

rsl_db = RSLmysql(host="localhost", user="rsl_user", database="rsl_exgenerator", password="rsl24EX@g")

commands = {"/help":"Help", "/start": 'Start', '/mytext': 'Ввести свой текст'}
choose_exercise_buttons = [{'command_text': 'составить предложение', 'command_name': '/ex3'},
                           {'command_text': 'падежи', 'command_name': '/ex4'},
                           {'command_text': 'грамматика', 'command_name': '/ex5'},
                           {'command_text': 'лексика', 'command_name': '/ex6'}]

responseQueue = Queue()
requestQueue = Queue()
request = TelebotRequest()

tb = TeleBotBase(telebot_name, telebot_api, connected_users, commands)
           
tb.start(responseQueue, requestQueue)

started = True
while started == True:
    if requestQueue.qsize() > 0:
        request = requestQueue.get()

        my_text_or_base = [{'command_text': 'свой текст', 'command_name': '/user_file'}, {'command_text': 'текст из базы', 'command_name': '/base_file'}]
        choose_text_buttons_from_db = []
        textfiles = {}
        texts = rsl_db.get_texts(chat=request.chat)
        for index, name in enumerate(texts.keys()):
            textfiles[f'/file_{index}']=name
            choose_text_buttons_from_db.append({'command_text': name, 'command_name': f'/file_{index}'})

        if request.text == '/start':
            if request.chat not in connected_users:
                connected_users.append(request.chat)
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['start'], commands=my_text_or_base))

        if request.text.startswith('/file'):
            text = texts[textfiles[request.text]]
            
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['chosen_text']+textfiles[request.text]))
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['choose_ex'], commands=choose_exercise_buttons))
        
        if request.text == '/choose_ex':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['choose_ex'], commands=choose_exercise_buttons))
        
        if request.text == '/another_text':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['more_texts'], commands=[{'command_text': 'да', 'command_name': '/start'}, {'command_text': 'нет', 'command_name': '/end'}]))
        
        if request.text == '/end':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['end_text']))

        if request.text == '/user_file':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['get_user_text']))
        
        if request.text == '/base_file':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['get_base_text'], commands=choose_text_buttons_from_db))

        if request.text.startswith('/mytext'):
            text = request.text
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['save_usertext'], commands=[{'command_text': 'Сохранить', 'command_name': '/savetodb'},
                                                                                                            {'command_text': 'Не сохранять', 'command_name': '/dontsavetodb'}]))

        if request.text == '/savetodb':
            rsl_db.save_usertext(text, request.chat)
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['saved']))
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['choose_ex'], commands=choose_exercise_buttons))

        if request.text == '/dontsavetodb':
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['not_saved']))
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['choose_ex'], commands=choose_exercise_buttons))


        if request.text.startswith('/ex'): 
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['ex_is_being_generated']))

            sentences = sent_tokenize(text)
            if len(sentences)>5:
                begin = random.randint(0, len(sentences)-5)
            else:
                begin = 0
            sent_to_process = sentences[begin:begin+5]

            processed_sentences = []
            for sent in sent_to_process:
                processed_sent = SentProcessor(sent)
                processed_sent.process_text()
                processed_sentences.append(processed_sent)

            exercise = Exercise(processed_sentences, number_of_sent_in_each_ex=3)
            exercise.run_exercises([int(request.text.replace('/ex', ''))])
            ex, answers = exercise.form_exercises()
            responseQueue.put(TelebotResponse(chat= request.chat, text = f'{ex}\n\n{answers}'))
            responseQueue.put(TelebotResponse(chat= request.chat, text = ui_texts['more_tasks'], commands=[{'command_text': 'да', 'command_name': '/choose_ex'}, {'command_text': 'нет', 'command_name': '/another_text'}]))
           
    time.sleep(0.5)
