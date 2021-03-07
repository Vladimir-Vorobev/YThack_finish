# -*- coding: utf-8 -*-
from server import db, sio, mail
users = db.users
codes = db.codes
rooms = db.rooms

from datetime import datetime
import threading
import bcrypt
import time as tim
import sys
from flask_mail import Message

class helpful_functions():

    def __init__(self):
        pass

    def check_reg_codes(self): # проверяем коды подтверждения на актуальность. Если он был создан более часа назад, удаляем его
        for user in codes.find():
            if (datetime.utcnow() - user['time']).seconds > 3600:
                codes.delete_one({
                    "email": user['email']
                })

    def send_email(self, subject, to, text): # почтовый бот
        msg = Message(subject,
                      sender="educationalgamehack@gmail.com",
                      recipients=[to])
        msg.body = text + "\n\n\n------\nЭто письмо было отправлено автоматически. Отвечать на него не нужно"
        mail.send(msg)

    def check_session_id(self, data): # проверяем session_id (защита аккаунта), не используем, тк сервер слабый и работает на нем очень долго
        nick = data['nick']
        user = users.find_one({
            'nick': nick,
        })
        if user != None and bcrypt.checkpw(data['session_id'].encode(), user['session_id']):
            return True
        else:
            return False

class timer(object):

    def __init__(self, num): # инициализируем класс с данными по умолчанию
        self.num = num
        self.users = []
        self.timer_time = -1
        self.run = True

    def timer(self): # пока таймер должен работать, отправляем таймер и обновляем значение
        while self.run:
            tim.sleep(1)
            for user in self.users:
                sio.emit('timer', {'timer': self.timer_time}, room=user)
            rooms.update_one(
                {'num': self.num},
                {"$set":
                    {
                        'timer': self.timer_time
                    }
                }
            )
            self.timer_time -= 1
            if self.timer_time < 0: # сообщаем всем, что игра закончилась
                for user in self.users:
                    sio.emit('info', {'info': 'game_is_over'}, room=user)
                self.stop_timer()


    def set_timer_time(self, time): # задаем начальное время таймера
        self.timer_time = time

    def set_users(self, users): # задаем значения socket-подключений пользователя
        self.users = users

    def start_timer(self): # запускаем таймер
        t = threading.Thread(target=self.timer)
        t.start()

    def stop_timer(self): # останавливаем таймер
        self.run = False
        rooms.remove({
            'num': self.num,
        })

hf = helpful_functions()