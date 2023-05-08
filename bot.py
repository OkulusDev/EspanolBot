#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Телеграм-бот для изучения испанского языка. Данный бот позволит вам 
Создатель: Okulus Dev (C) 2023 ALL RIGHTS REVERSED | ВСЕ ПРАВА СОХРАНЕНЫ
Лицензия: GNU GPL v3"""
import sys													# Импорт системной библиотеки
import os													# Импорт OS
import logging                                              # Импорт библиотеки логирования
import re 													# Импорт библиотеки для регулярных выражений
from random import choice

import telebot												# Импорт pytelegrambotapi
from telebot import types									# Импорт типов pytelegrambotapi
from youtube_transcript_api import YouTubeTranscriptApi     # Импорт Youtube Transcript Api
from deep_translator import GoogleTranslator                # Импорт переводчика

import config as cfg 										# Импорт конфигурации
import datalog                                              # Импорт библиотеки для сбора данных
import dbhelper												# Импорт библиотеки для взаимодействия с базой данных
import lessons                                              # Импорт уроков

# Создание бота и базы данных
bot = telebot.TeleBot(cfg.TOKEN)
db_helper = dbhelper.DBHelper()

# Настройка логгера
logger = telebot.logger
logger.setLevel(level=logging.INFO)
filehandler = logging.FileHandler('bot.log', mode='a')
formatter_handler = logging.Formatter('%(name)s %(asctime)s [%(levelname)s]: %(message)s')
filehandler.setFormatter(formatter_handler)
logger.addHandler(filehandler)

START_OVER, ADDING, END = range(1, -2, -1)
# Регулярное выражение для ссылки на видео ютуба
re_youtube = re.compile('^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+')
re_text = re.compile('^[a-z]{3,20}$')


def is_youtube_link(link: str) -> bool:
	"""Проверка, является ли ссылка ссылкой на ютуб-видео
	Аргументы:
	 + link: str - переменная строчного типа, ссылка
	Возвращает:
	 + bool - True, если ссылка прошла проверку, и False, если не прошла
	"""
	if re_youtube.match(link) is not None:
		return True
	else:
		return False


def clear_text(text: str) -> str:
	"""Превращение текста в чистый.
	Аргументы:
	 + text: str - текст
	Возвращает:
	 + str - очищенный текст"""
	return text.strip()


def add_words(message):
	"""Транскрипция на испанский ютуб-видео."""
	bot.send_message(message.chat.id, 'Загрузка... Подождите...')

	if is_youtube_link(message.text):
		try:
			logger.info(f'Попытка транскрипции youtube-видео {message.text}')
			transcript_list = YouTubeTranscriptApi.list_transcripts(message.text.split('/')[-1])
			t = transcript_list.find_transcript(['es'])
			text = clear_text('.'.join([i['text'] for i in t.fetch()]))

			with open('trans.txt', 'w') as file:
				logger.info(f'Сохранение транскрипции {message.text} в файл')
				file.write(text)

			with open("trans.txt", 'rb') as file:
				logger.info('Отправка файла с транскрипцией пользователю')
				bot.send_document(message.chat.id, file)

			logger.info(f'Удаление файла с транскрипцией {message.text}')
			os.system('rm trans.txt')

			db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
			bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')
		except Exception as ex:
			print(ex)
			logger.error(f'Ошибка обработки видео {message.text}: {ex}')
			bot.send_message(message.chat.id, 'Некорректное или без субтитров видео. Попробуйте еще раз!')
	else:''
		bot.send_message(message.chat.id, 'Это не youtube-видео!')

                                                                                               
def translate_esp2rus(message):
	"""Перевод с испанского на русский"""
	translator = GoogleTranslator(source='es', target='ru')
	result = translator.translate(message.text)
	bot.send_message(message.chat.id, f'Оригинал: {message.text}\nПеревод: {result}')
	db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
	bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')


def test_translate(message, word):
	translator = GoogleTranslator(source='ru', target='es')
	result = translator.translate(word)

	if message.text.lower().strip() == result.lower().strip():
		bot.send_message(message.chat.id, 'Абсолютно правильно!')
		db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
		bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')
	else:
		bot.send_message(message.chat.id, f'Неверно! Правильный перевод - {result}')
		db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) - 1)
		bot.send_message(message.chat.id, 'Ваш уровень владения языком понижен!')


def translate_rus2esp(message):
	"""Перевод с русского на испанский"""
	translator = GoogleTranslator(source='ru', target='es')
	result = translator.translate(message.text)
	bot.send_message(message.chat.id, f'Оригинал: {message.text}\nПеревод: {result}')
	db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
	bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')


def bot_start_alert():
	# Предупреждение администраторов о том, что бот был запущен
	for admin_id in cfg.ADMINS_IDS:
		bot.send_message(admin_id, "Внимание! Бот @espanol_russian_learning_bot запущен!")


def delete_user_from_db(message):
	db_helper.delete_user(message.text)
	bot.send_message(message.chat.id, f'Пользователь {message.text} удален!')


def add_user_to_db(message):
	db_helper.add_user(message.text)
	bot.send_message(message.chat.id, f'Пользователь {message.text} добавлен!')


def set_level_to_user_first(message):
	mesg = bot.send_message(message.chat.id, f'Введите новое значение уровня пользователя {message.text}')
	bot.register_next_step_handler(mesg, set_level_to_user_end, message.text)


def set_level_to_user_end(message, user_id):
	db_helper.update_level(user_id, message.text)
	bot.send_message(message.chat.id, f'Уровень пользователя {user_id} теперь {message.text}!')


@bot.message_handler(commands=['start'])
def start_message(message):
	# Команда /start
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item0 = types.KeyboardButton('Админ-панель')
	item1 = types.KeyboardButton('Профиль')
	item2 = types.KeyboardButton('Таблица пользователей')
	item3 = types.KeyboardButton('Расшифровка видео')
	item4 = types.KeyboardButton('Переводчик')
	item5 = types.KeyboardButton('Уроки')
	item6 = types.KeyboardButton('Перевод случайного слова')
	item7 = types.KeyboardButton('Материалы для изучения')
	markup.add(item1, item2)
	markup.add(item3, item4)
	markup.add(item5, item6)
	markup.add(item7)

	# Регистрация пользователя в базе данных
	if message.from_user.id not in db_helper.get_users_ids():
		# Если пользователя нету, то мы его регистрируем. Если он есть, то ничего не делаем
		db_helper.add_user(user_id=message.from_user.id, level=0)
	# Проверка доступа к админ-панели
	if message.from_user.id in cfg.ADMINS_IDS:
		bot.send_message(message.chat.id, 'Приветствую вас, администратор!')
		markup.add(item0)

	bot.send_message(message.chat.id, 'Привет! Я бот для изучения испанского языка!', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
	# Обработчик запроса обратного вызова
	if call.data == 'esp2rus':
		mesg = bot.send_message(call.message.chat.id, 'Введите текст на испанском языке:')
		bot.register_next_step_handler(mesg, translate_esp2rus)
	elif call.data == 'rus2esp':
		mesg = bot.send_message(call.message.chat.id, 'Введите текст на русском языке:')
		bot.register_next_step_handler(mesg, translate_rus2esp)
	elif call.data == 'lesson0':
		bot.send_message(call.message.chat.id, lessons.LESSON0, parse_mode='html')
		db_helper.update_level(call.message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
		bot.send_message(call.message.chat.id, 'Ваш уровень владения языком повышен!')
	elif call.data == 'delete_user':
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя:')
		bot.register_next_step_handler(mesg, delete_user_from_db)
	elif call.data == 'add_user':
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя в телеграмме:')
		bot.register_next_step_handler(mesg, add_user_to_db)
	elif call.data == 'set_level':
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя:')
		bot.register_next_step_handler(mesg, set_level_to_user_first)


@bot.message_handler()
def text_messages(message):
	# Абсолютно любой текст, введенный пользователем
	chatid = message.chat.id
	msgtext = message.text

	if msgtext == 'Профиль':
		level = db_helper.get_user_level(message.from_user.id)
		bot.send_message(chatid, f'Ваш уровень: {level[0][0]}. Ваш ID: {message.from_user.id}')
	elif msgtext == 'Таблица пользователей':
		data = db_helper.get_users()
		result = ''
		for i in data:
			result += str(f'ID: {i[0]}. Уровень: {i[1]}\n')
		bot.send_message(chatid, result)
	elif msgtext == 'Админ-панель':
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user'))
		markup.add(types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user'))
		markup.add(types.InlineKeyboardButton(text='Выдать уровень пользователю', callback_data='set_level'))
		bot.send_message(message.chat.id, 'Добро пожаловать в админ-панель!', reply_markup=markup)
	elif msgtext == 'Расшифровка видео':
		msg = bot.send_message(chatid, 'Введите ссылку на испанское youtube-видео:')
		bot.register_next_step_handler(msg, add_words)
	elif msgtext == 'Переводчик':
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton(text='С испанского на русский', callback_data='esp2rus'))
		markup.add(types.InlineKeyboardButton(text='С русского на испанский', callback_data='rus2esp'))
		bot.send_message(chatid, 'Выберите язык', reply_markup=markup)
	elif msgtext == 'Уроки':
		markup = types.InlineKeyboardMarkup()
		item1 = types.InlineKeyboardButton(text='Вводный урок', callback_data='lesson0')
		markup.add(item1)
		bot.send_message(chatid, 'Выберите урок', reply_markup=markup)
	elif msgtext == 'Перевод случайного слова':
		word = choice(lessons.words)
		mesg = bot.send_message(message.chat.id, f'Введите перевод слова "{word}"')
		bot.register_next_step_handler(mesg, test_translate, word)
	elif msgtext == 'Материалы для изучения':
		bot.send_message(message.chat.id, 'Вот материалы для изучения испанского языка!')
	else:
		bot.send_message(chatid, f'Команда "{msgtext}" не найдена :(')


if __name__ == '__main__':
	db_helper.setup()										# Установка базы данных
	
	# Старт бота
	bot_start_alert()
	bot.infinity_polling()
