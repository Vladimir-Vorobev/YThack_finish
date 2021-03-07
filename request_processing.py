# -*- coding: utf-8 -*-
import json
import random
import bcrypt
from datetime import datetime

from server import db
users = db.users
codes = db.codes

from modules import hf
from antimat import am

class request_precessing():

    def reg_code(self, data): # отправляем код подтверждения для регистрации
        data = dict(json.loads(data))
        user = users.find_one({
            "email": data['email']
        })
        if user != None: # если пользователь с таким email уже есть
            return "incorrect_email"
        user = codes.find_one({
            "email": data['email']
        })
        if user != None: # если все хорошо
            code = random.randrange(10**6, 10**7, 1)
            codes.update_one(
                {"email": data['email']},
                {"$set":
                     {"code": code, "time": datetime.utcnow()}
                }
            )
            hf.send_email('Подтверждение регистрации', data['email'], 'Ваш код подтверждения: %s, он будет действителен в течение часа. Если это не Вы, то просто проигнорируйте данное письмо' % (code))
            return "send_code"
        else: # если пользователь повторно просит код подтверждения
            code = random.randrange(10 ** 6, 10 ** 7, 1)
            codes.insert_one({
                "email": data['email'],
                "code": code,
                "time": datetime.utcnow(),
            })
            hf.send_email('Подтверждение регистрации', data['email'], 'Ваш код подтверждения: %s, он будет действителен в течение часа. Если это не Вы, то просто проигнорируйте данное письмо' % (code))
            return "send_code"

    def reg_in(self, data): # обрабатываем регистрацию
        data = dict(json.loads(data.decode("utf-8")))
        user = users.find_one({
            "email": data['email']
        })
        nick = users.find_one({
            "nick": data['nick']
        })
        if user != None: # если пользователь с таким email уже есть
            return "incorrect_email"
        if nick != None: # если пользователь с таким ником уже есть
            return "incorrect_nick"
        if am.find_mat(data['nick']): # если пользователь указал матный ник
            return "mat_nick"
        else: # если все хорошо
            user = codes.find_one({
                "email": data['email']
            })
            if (datetime.utcnow() - user['time']).seconds > 3600: # если код подтверждения истек
                codes.delete_one({
                    "email": data['email']
                })
                return 'code_time_out'
            elif user['code'] == int(data['code']):
                users.insert_one({
                    "nick": data['nick'],
                    "email": data['email'],
                    "password": data['password'], # пароль пока не хэшируется, т.к. это долго и сервер медленный
                    "avatar": '',
                    "role": 'user',
                    "user_id": self.make_user_id(),
                    "session_id": bcrypt.hashpw(self.make_session_id().encode(), bcrypt.gensalt(16)),
                    "chats": {},
                    "store": 0,
                    "rang": 0,
                    "money": 0,
                    "water_vlv": 5,
                    "gorelka_vlv": 5,
                    "banned": False,
                    "ban_time": [],
                    "ban_reason": '',
                })
                codes.delete_one({
                    "email": data['email']
                })
                return "reg_in"
            else: # если код подтверждения неверный
                return "incorrect_code"

    def log_in(self, data): # проверяем логин
        data = dict(json.loads(data))
        user = users.find_one({
            "email": data['email']
        })
        if user == None: # если пользователь не найден
            return "incorrect_email"
        elif data['password'] != user['password']: # если пароли не совпадают
            return "incorrect_password"
        else:
            session_id = 'sgdhfrbugfyukguyafeyfusgrrshjerareyhgzrgryaryh'
            # users.update_one(
            #     {"email": data['email']},
            #     {"$set":
            #          {"session_id": bcrypt.hashpw(session_id.encode(), bcrypt.gensalt(16))}
            #      }
            # )
            del user['_id']
            del user['password']
            del user['banned']
            del user['ban_time']
            del user['ban_reason']
            user['session_id'] = session_id
            return user

    def make_user_id(self): # создаем user_id
        user = {}
        while user != None:
            result = ''
            letters = '0123456789qwertyuiopasdfghjklzxcvbnm'
            maximum = len(letters)
            for i in range(16):
                result += letters[random.randrange(0, maximum, 1)]
            user = users.find_one({
                "user_id": result
            })
        return result

    def make_session_id(self): # создаем session_id
        user = {}
        while user != None:
            result = ''
            letters = '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
            maximum = len(letters)
            for i in range(256):
                result += letters[random.randrange(0, maximum, 1)]
            user = users.find_one({
                "session_id": result
            })
        return result

rp = request_precessing()