# -*- coding: utf-8 -*-
from flask_socketio import send, emit
from datetime import datetime
from antimat import am

from server import db, sio
from reaction_processing import rep
from modules import hf, timer
rooms = db.rooms
users = db.users
waiters_multiplayer = db.waiters_multiplayer
timers = {}

class socket_processing():

    def create_room(self, data): # создаем комнату с пользователем
        # if not hf.check_session_id(data): return
        num = 1
        while rooms.find_one({'num': num}):
            num += 1
        room = {
            'num': num,
            'users': data['user'],
            'res': data['res'],
            'timer': None,
            'creation_time': datetime.utcnow()
        }
        rooms.insert_one(room)
        return num

    def connect_to_room(self, data): # подключаемся к комнате, если вылетело socket-соединение
        # if not hf.check_session_id(data): return
        nick = data['nick']
        num = int(data['room_num'])
        room = rooms.find_one({
            'num': num
        })
        if room == None:
            emit('info', {'info': 'game_is_over'})
            return
        room['users'][nick]['sid'] = data['sid']
        rooms.update_one(
            {'num': num},
            {"$set":
                {
                    'users': room['users'],
                }
            }
        )
        users_sid = []
        for user in room['users']:
            users_sid.append(room['users'][user]['sid'])
        if num in timers:
            timers[num].set_users(users_sid)

    def play_alone(self, data): # создаем комнату, подбираем вопрос с реакцией и запускаем таймер для одиночной игры
        # if not hf.check_session_id(data): return
        res = rep.play(data, 'play_alone')
        res['room_num'] = self.create_room({'user': {data['nick']: {'sid': data['sid']}}, 'res': res})
        ti = timer(res['room_num'])
        ti.set_timer_time(60)
        ti.set_users([data['sid']])
        timers[res['room_num']] = ti
        ti.start_timer()
        emit('play_alone', res)

    def play_alone_answer(self, data): # проверяем ответ одиночной игры
        # if not hf.check_session_id(data): return
        room = rooms.find_one({
            'num': data['room_num']
        })
        if room['num'] == data['room_num'] and room['res']['index'] == data['index']:
            res = rep.play_alone_answer(data)
            emit('play_alone_answer', res)
            if res['reaction'] != 'incorrect':
                timers[data['room_num']].stop_timer()
                rooms.remove({
                    'num': data['room_num'],
                })
                user = users.find_one(
                    {"nick": data['nick']},
                )
                user['money'] += res['money']
                users.update_one(
                    {"nick": data['nick']},
                    {"$set":
                         {"money": user['money']}
                     }
                )
        else:
            emit('info', {'info': 'game_is_over'})

    def multi_play(self, data): # создаем комнату, подбираем вопрос с реакцией и запускаем таймер для мультиплеера
        # if not hf.check_session_id(data): return
        for waiter in waiters_multiplayer.find({'rang': {'$gte': data['rang'] - 1, '$lte': data['rang'] + 1}}): # если удалось найти соперника сразу
            room = rooms.find_one({
                'num': waiter['num']
            })
            if data['nick'] in room['users']:
                emit('multi_play_wait', {'room_num': room['num']})
                return
            res = room['res']
            res['room_num'] = waiter['num']
            res['users'] = [waiter['nick'], data['nick']]
            ti = timer(res['room_num'])
            ti.set_timer_time(60)
            room['users'][data['nick']] = {'sid': data['sid']}
            rooms.update_one(
                {'num': waiter['num']},
                {"$set":
                    {
                        'users': room['users']
                    }
                }
            )
            ti.set_users([room['users'][waiter['nick']]['sid'], data['sid']])
            timers[res['room_num']] = ti
            emit('multi_play_start', res, room=room['users'][waiter['nick']]['sid'])
            emit('multi_play_start', res, room=data['sid'])
            ti.start_timer()
            waiters_multiplayer.remove({
                'num': waiter['num']
            })
            return

        # если соперник сразу не найден
        res = rep.play(data, 'multi_play')
        room_num = self.create_room({'user': {data['nick']: {'sid': data['sid']}}, 'res': res})
        waiters_multiplayer.insert_one({
            'num': room_num,
            'nick': data['nick'],
            'rang': data['rang'],
        })
        emit('multi_play_wait', {'room_num': room_num})

    def multi_play_answer(self, data): # проверяем ответ мультиплеера
        # if not hf.check_session_id(data): return
        room = rooms.find_one({
            'num': data['room_num']
        })
        if room['num'] == data['room_num'] and room['res']['index'] == data['index']:
            res = rep.multi_play_answer(data)
            room = rooms.find_one({
                'num': data['room_num']
            })
            if room == None:
                return
            emit('multi_play_answer', res)
            if res['reaction'] != 'incorrect':
                timers[data['room_num']].stop_timer()
                rooms.remove({
                    'num': data['room_num'],
                })
                for user in room['users']:
                    emit('multi_play_finish', {'winner': data['nick']}, room=room['users'][user]['sid'])
                user = users.find_one(
                    {"nick": data['nick']},
                )
                if user['store'] // 1000 != (user['store'] + res['store']) // 1000 and user['rang'] < 2:
                    user['rang'] += 1
                user['store'] += res['store']
                users.update_one(
                    {"nick": data['nick']},
                    {"$set":
                         {"store": user['store'], "rang": user['rang']}
                     }
                )
        else:
            emit('info', {'info': 'game_is_over'})

    def get_multu_play_task(self, data): # если по причине вылета соединения реакция не пришла (бывает очень редко, но все же)
        # if not hf.check_session_id(data): return
        room = rooms.find_one({
            'num': data['room_num']
        })
        emit('multi_play_start', room['res'])

    def leave_multi_play(self, data): # если недождались соперника и реашили выйти (чтобы не играть с фантомами)
        # if not hf.check_session_id(data): return
        waiters_multiplayer.remove({
            'nick': data['nick'],
            'num': data['room_num'],
        })
        rooms.remove({
            'num': data['room_num'],
        })

    def objects_boosting(self, data): # прокачка уровня воды и горелки
        # if not hf.check_session_id(data): return
        user = users.find_one({
            'nick': data['nick']
        })
        if data['target'] == 'water' and user['money'] >= 500:
            if user['water_vlv'] != 1:
                users.update_one(
                    {"nick": data['nick']},
                    {"$set":
                         {"money": user['money'] - 500, "water_vlv": data['lvl']}
                    }
                )
                emit('objects_boosting', {'info': 'OK', 'device': 'water'})
        elif data['target'] == 'gorelka' and user['money'] >= 300:
            if user['gorelka_vlv'] != 1:
                users.update_one(
                    {"nick": data['nick']},
                    {"$set":
                         {"money": user['money'] - 300, "water_vlv": data['lvl']}
                    }
                )
                emit('objects_boosting', {'info': 'OK', 'device': 'gorelka'})
        else:
            emit('objects_boosting', {'info': 'Вам не хватает денег', 'device': None})

sp = socket_processing()