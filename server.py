# -*- coding: utf-8 -*-
from flask import Flask
from flask_mail import Mail
from flask_cors import CORS
app = Flask(__name__)
app.config.update( # для почтового бота
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'educationalgamehack@gmail.com',
	MAIL_PASSWORD = 'loAhwn7rAzl!iosnkag',
)
CORS(app)

mail = Mail(app)

from flask_socketio import SocketIO
sio = SocketIO(app, cors_allowed_origins = "*", async_mode='threading') # сокеты

from pymongo import MongoClient
client = MongoClient("127.0.0.1:27017") # MongoDB
db = client.hackDB