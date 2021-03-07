# -*- coding: utf-8 -*-
from flask import Flask, make_response, request, session, copy_current_request_context
import threading
import os
from server import app, sio

from socket_processing import sp
from request_processing import rp
from modules import hf

@app.route('/', methods = ['GET','POST']) # проверка, что сервер работает
def code():
    return "Все работает"

@app.route('/reg-code/', methods = ['POST']) # обрабатываем код подтверждения
def reg_code():
    return rp.reg_code(request.data)

@app.route('/registration/', methods = ['POST']) # обрабатываем регистрацию
def reg_in():
    return rp.reg_in(request.data)

@app.route('/login/', methods = ['POST']) # обрабатываем логин
def log_in():
    return rp.log_in(request.data)

@sio.on('play_alone') # обрабатываем одиночную игру
def play_alone(data):
    data['sid'] = request.sid
    sp.play_alone(data)

@sio.on('multi_play') # обрабатываем мультиплеер
def multi_play(data):
    data['sid'] = request.sid
    sp.multi_play(data)

@sio.on('play_alone_answer') # обрабатываем ответ для одиночной игры
def play_alone_answer(data):
    sp.play_alone_answer(data)

@sio.on('multi_play_answer') # обрабатываем ответ для мультиплеера
def multi_play_answer(data):
    sp.multi_play_answer(data)

@sio.on('leave_multi_play') # обрабатываем выход из мультиплеера
def leave_multi_play(data):
    sp.leave_multi_play(data)

@sio.on('get_multu_play_task') # получаем задание для мультиплеера, если не удалось в первый раз (редко)
def get_multu_play_task(data):
    sp.get_multu_play_task(data)

@sio.on('objects_boosting') # обрабатываем прокачку воды и горелки
def objects_boosting(data):
    sp.objects_boosting(data)

@sio.on('connect_to_room') # обрабатываем подключение к комнате при вылете соединения
def connect_to_room(data):
    data['sid'] = request.sid
    sp.connect_to_room(data)

def check_reg_codes(): # обрабатываем проверяем коды подтверждения регистрации на валидность по времени
    def func():
        hf.check_reg_codes()
        check_reg_codes()
    t = threading.Timer(604800, func)
    t.start()

if __name__ == "__main__": # запускаем сервер
    import cherrypy
    check_reg_codes()
    cherrypy.tree.graft(app.wsgi_app, '/')
    cherrypy.config.update({'server.socket_host': "0.0.0.0", 'server.socket_port': 5000, 'engine.autoreload.on': False})
    cherrypy.engine.start()
    cherrypy.engine.block()
    # app.run(threaded=True, port=int(os.environ.get('PORT', 5000)))