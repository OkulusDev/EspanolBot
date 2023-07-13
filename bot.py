#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Телеграм-бот для изучения испанского языка. Данный бот позволит вам 
Создатель: Okulus Dev (C) 2023 ALL RIGHTS REVERSED | ВСЕ ПРАВА СОХРАНЕНЫ
Лицензия: GNU GPL v3
Версия: 1.1.2 BETA"""

# Импорт стандартных библиотек
import sys													# Импорт системной библиотеки
import os													# Импорт OS
import logging                                              # Импорт библиотеки логирования
import re 													# Импорт библиотеки для регулярных выражений
from random import choice									# Импорт библиотеки рандома
from datetime import datetime								# Импорт библиотеки даты и времени

# Импорт сторонних библиотек
import telebot												# Импорт pytelegrambotapi (telebot)
from telebot import types									# Импорт типов pytelegrambotapi
from youtube_transcript_api import YouTubeTranscriptApi     # Импорт Youtube Transcript Api
from deep_translator import GoogleTranslator                # Импорт переводчика Google

# Импорт существующих файлов
import config as cfg 										# Импорт конфигурации бота
import datalog                                              # Импорт библиотеки для сбора данных
import dbhelper												# Импорт библиотеки для взаимодействия с базой данных
import lessons                                              # Импорт уроков и тестов

# Создание бота и базы данных
bot = telebot.TeleBot(cfg.TOKEN)
db_helper = dbhelper.DBHelper()

# Настройка логгера
logger = telebot.logger
logger.setLevel(level=logging.INFO)						# Установка уровня INFO в логгере
filehandler = logging.FileHandler('bot.log', mode='a')      # Создание лог-файла

# Формат строк для логов: имя время [уровень] сообщение
formatter_handler = logging.Formatter('%(name)s %(asctime)s [%(levelname)s]: %(message)s')

filehandler.setFormatter(formatter_handler) 				# Установка формата
logger.addHandler(filehandler)								# Установка обработчика

# Регулярное выражение для ссылки на youtube-видео
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


def add_words(message) -> None:
	"""Транскрипция на испанский youtube-видео. Данная функция использует Youtube Transcript API
	для преобразования речи в текст на испанском языке"""
	bot.send_message(message.chat.id, 'Загрузка... Подождите...')

	if is_youtube_link(message.text):
		# Если ссылка проходит валидацию
		try:
			# Попытка транскрипции
			logger.info(f'Попытка транскрипции youtube-видео {message.text}')
			
			# Получаем транскрипцию и очищаем ее
			transcript_list = YouTubeTranscriptApi.list_transcripts(message.text.split('/')[-1])
			t = transcript_list.find_transcript(['es'])
			text = clear_text('.'.join([i['text'] for i in t.fetch()]))

			# Сохранение в файл
			with open('trans.txt', 'w') as file:
				logger.info(f'Сохранение транскрипции {message.text} в файл')
				file.write(text)

			# Отправка файла пользователя
			with open("trans.txt", 'rb') as file:
				logger.info(f'Отправка файла с транскрипцией {message.text} пользователю')
				bot.send_document(message.chat.id, file)

			# Удаление файла
			logger.info(f'Удаление файла с транскрипцией {message.text}')
			os.system('rm trans.txt')

			# Повышение уровня
			db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
			bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')
		except Exception as ex:
			# При исключении, выводим информацию о ошибке
			print(ex)
			logger.error(f'Ошибка обработки видео {message.text}: {ex}')
			bot.send_message(message.chat.id, 'Некорректное или без субтитров видео. Попробуйте еще раз!')
	else:
		# Если ссылка не прошла валидацию, уведомим об этом пользователя
		bot.send_message(message.chat.id, 'Это не youtube-видео!')

                                                                                               
def translate_esp2rus(message) -> None:
	"""Перевод с испанского на русский. Данная функция использует Google-Переводчик для перевода
	фразы с испанского на русский."""
	translator = GoogleTranslator(source='es', target='ru')
	result = translator.translate(message.text)

	bot.send_message(message.chat.id, f'Оригинал: {message.text}\nПеревод: {result}')
	
	db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
	bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')


def test_translate(message, word: str) -> None:
	"""Тест на знание слова. Данная функция требует от пользователя перевод слова на испанский
	Аргумент:
	 + word - исходное слово"""
	translator = GoogleTranslator(source='ru', target='es')
	result = translator.translate(word)

	if message.text.lower().strip() == result.lower().strip():
		# Если перевод соответствует, то уведомляем пользователя об этом и повышаем его уровень
		bot.send_message(message.chat.id, 'Абсолютно правильно!')
		db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
		bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')
	else:
		# Если перевод неверен, то уведомим пользователя об этом и понижаем его уровень
		bot.send_message(message.chat.id, f'Неверно! Правильный перевод - {result}')
		db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) - 1)
		bot.send_message(message.chat.id, 'Ваш уровень владения языком понижен!')


def translate_rus2esp(message) -> None:
	"""Перевод с испанского на русский. Данная функция использует Google-Переводчик для перевода
	фразы с русского на испанский."""
	translator = GoogleTranslator(source='ru', target='es')
	result = translator.translate(message.text)
	bot.send_message(message.chat.id, f'Оригинал: {message.text}\nПеревод: {result}')
	db_helper.update_level(message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
	bot.send_message(message.chat.id, 'Ваш уровень владения языком повышен!')


def bot_start_alert() -> None:
	# Предупреждение администраторов о том, что бот был запущен
	for admin_id in cfg.ADMINS_IDS:
		# Проходимся в цикле по списку ID администраторов
		bot.send_message(admin_id, "Внимание! Бот @espanol_russian_learning_bot запущен!")


def delete_user_from_db(message) -> None:
	"""Данная фунция удаляет пользователя из базы данных по его ID"""
	db_helper.delete_user(message.text)
	bot.send_message(message.chat.id, f'Пользователь {message.text} удален!')


def add_user_to_db(message) -> None:
	"""Данная функция добавляет пользователя в базу данных по его ID"""
	db_helper.add_user(message.text)
	bot.send_message(message.chat.id, f'Пользователь {message.text} добавлен!')


def set_level_to_user_first(message) -> None:
	"""Данная функция устанавливает новое значение для пользователя по его ID.
	Эта функция - первый шаг. Здесь мы пересылаем ID пользователя и получаем новое значение
	уровня для пользователя"""
	mesg = bot.send_message(message.chat.id, f'Введите новое значение уровня пользователя {message.text}')
	bot.register_next_step_handler(mesg, set_level_to_user_end, message.text)


def set_level_to_user_end(message, user_id) -> None:
	"""Данная функция устанавливает новое значение для пользователя по его ID.
	Эта функция - последний шаг. Здесь мы получаем ID пользователя и новое значение уровня.
	Аргументы:
	 + user_id - ID пользователя"""
	db_helper.update_level(user_id, message.text)
	bot.send_message(message.chat.id, f'Уровень пользователя {user_id} теперь {message.text}!')


def send_report(message) -> None:
	"""Функция отправки репорта разработчикам от пользователя"""
	user_id = message.from_user.id 						# ID пользователя
	time = datetime.now()								# текущее время
	
	# Записываем текст репорта в файл report_{id пользователя}_{время}
	with open(f'report_{user_id}_{time}.txt', 'w') as file:
		file.write(message.text)
		# Сообщаем в конце файла о времени отправки и ID отправителя
		file.write(f'\n\nРепорт получен в {time} от пользователя {user_id}')

	for admin in cfg.ADMINS_IDS:
		# Отправляем репорт всем администраторам
		bot.send_message(admin, f'''Здравствуйте, администратор {admin}!
Пользователь под ID {user_id} прислал репорт ({time}):\n
{message.text}''')
		# Сообщаем о сохранении в файл
		bot.send_message(message.chat.id, f'Репорт сохранен в файл "report_{user_id}_{time}.txt"')

		# Отправляем файл с репортом всем администраторам
		with open(f'report_{user_id}_{time}.txt', 'r') as file:
			# Отправляем txt-файл администраторам
			bot.send_document(message.chat.id, file)


@bot.message_handler(commands=['start'])
def start_message(message) -> None:
	# Команда /start

	# Создаем reply-клавиатуру
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	item0 = types.KeyboardButton('Админ-панель')
	item1 = types.KeyboardButton('Профиль')
	item2 = types.KeyboardButton('Таблица пользователей')
	item3 = types.KeyboardButton('Транскрипция видео')
	item4 = types.KeyboardButton('Переводчик')
	item5 = types.KeyboardButton('Уроки')
	item6 = types.KeyboardButton('Тест на знание испанских слов')
	item7 = types.KeyboardButton('Материалы для изучения')
	item8 = types.KeyboardButton('О нас')
	item9 = types.KeyboardButton('Правила отправки репорта')
	item10 = types.KeyboardButton('Отправить репорт разработчикам')

	# Добавляем кнопки в reply-клавиатуру
	markup.add(item1, item2)
	markup.add(item3, item4)
	markup.add(item5, item6)
	markup.add(item7, item8)
	markup.add(item9, item10)

	# Регистрация пользователя в базе данных
	if message.from_user.id not in db_helper.get_users_ids():
		# Если пользователя нету, то мы его регистрируем. Если он есть, то ничего не делаем
		db_helper.add_user(user_id=message.from_user.id, level=0)

	# Проверка доступа к админ-панели
	if message.from_user.id in cfg.ADMINS_IDS:
		bot.send_message(message.chat.id, 'Приветствую вас, администратор!')
		# Добавляем еще одну кнопку в reply-клавиатуру
		markup.add(item0)

	# Приветственное сообщение
	bot.send_message(message.chat.id, 'Привет! Я бот для изучения испанского языка!', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call) -> None:
	# Обработчик запроса обратного вызова
	if call.data == 'esp2rus':
		# Перевод с испанского на русский
		mesg = bot.send_message(call.message.chat.id, 'Введите текст на испанском языке:')
		bot.register_next_step_handler(mesg, translate_esp2rus)
	elif call.data == 'rus2esp':
		# Перевод с русского на испанский
		mesg = bot.send_message(call.message.chat.id, 'Введите текст на русском языке:')
		bot.register_next_step_handler(mesg, translate_rus2esp)
	elif call.data == 'lesson0':
		# Первый, вводный урок по испанскому. Уроки берутся из файла lessons
		bot.send_message(call.message.chat.id, lessons.LESSON0, parse_mode='html')
		db_helper.update_level(call.message.from_user.id, int(db_helper.get_user_level(message.from_user.id)[0][0]) + 1)
		bot.send_message(call.message.chat.id, 'Ваш уровень владения языком повышен!')
	elif call.data == 'delete_user':
		# Удаление пользователя (админ-панель)
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя:')
		bot.register_next_step_handler(mesg, delete_user_from_db)
	elif call.data == 'add_user':
		# Добавляем пользователя (админ-панель)
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя в телеграмме:')
		bot.register_next_step_handler(mesg, add_user_to_db)
	elif call.data == 'set_level':
		# Устанавливаем новое значение уровня пользователя (админ панель)
		mesg = bot.send_message(call.message.chat.id, 'Введите ID пользователя:')
		bot.register_next_step_handler(mesg, set_level_to_user_first)


@bot.message_handler()
def text_messages(message) -> None:
	# Абсолютно любой текст, введенный пользователем, который не является командой
	chatid = message.chat.id
	msgtext = message.text

	if msgtext == 'Профиль':
		# Выводим профиль пользователя
		level = db_helper.get_user_level(message.from_user.id)				# Получаем уровень пользователя по ID
		bot.send_message(chatid, f'Ваш уровень: {level[0][0]}. Ваш ID: {message.from_user.id}')
	elif msgtext == 'Таблица пользователей':
		# Выводим список пользователей
		data = db_helper.get_users()				# Список
		result = ''									# Результат
		
		for i in data:
			# Проходимся по каждому элементу в списке и добавляем его в строку результата
			result += str(f'ID: {i[0]}. Уровень: {i[1]}\n')

		# Выводим результат
		bot.send_message(chatid, result)
	elif msgtext == 'О нас':
		# Вывод текста "О нас"
		bot.send_message(chatid, '''Бот для бесплатного изучения испанского языка.
Данный бот позволит вам бесплатно изучать испанский язык. Здесь вы можете оттачить свои знания слов, лексики, грамматики.
Этот бот вам предлагает переводить YouTube-видео на испанский текст, проходить тесты, а также он имеет свою таблицу пользователей!
Вы можете становиться лучше, повышая свой уровень до высот!
Создатель: @OkulusDev
Лицензия: GNU GPL v3
Исходный код (GitHub): https://github.com/OkulusDev/EspanolBot/
			''')
	elif msgtext == 'Правила отправки репорта':
		# Выводим правила отправки репорта
		bot.send_message(chatid, '''Вы заметили баг в боте? Вы перевели слово правильно, а вам не засчитали?
Составьте репорт разработчикам! Они обязательно узнают о баге и будут активно его исправлять!
Или у вас есть пожелания? То можете тоже составить репорт, чтобы разработчики добавили ваши желания в ближайшее время.

Текст составления репорта такой:
Здравствуйте, разработчики EspanolBot!
[Расскажите о багах или пожеланиях]''')
	elif msgtext == 'Отправить репорт разработчикам':
		# Отправка репорта администраторам

		# Ознакомляем пользователя с правилами
		bot.send_message(chatid, 'Для того, чтобы ваш репорт точно был прочитан, прочитайте правила отправки репорта:')
		bot.send_message(chatid, '''
Текст составления репорта такой:
Здравствуйте, разработчики EspanolBot!
[Расскажите о багах или пожеланиях]''')

		# Регистрируем следующий обработчик для отправки репорта. В этом обработчике мы получаем
		# сам текст репорта
		report = bot.send_message(chatid, 'Введите текст репорта:')
		bot.register_next_step_handler(report, send_report)
	elif msgtext == 'Админ-панель':
		# Выводим админ-панель, если пользователь - администратор
		if message.from_user.id in cfg.ADMINS_IDS:
			# Создание Inline клавиатуры и кнопок, и их вывод
			markup = types.InlineKeyboardMarkup()
			markup.add(types.InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user'))
			markup.add(types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user'))
			markup.add(types.InlineKeyboardButton(text='Выдать уровень пользователю', callback_data='set_level'))
			bot.send_message(message.chat.id, 'Добро пожаловать в админ-панель!', reply_markup=markup)
	elif msgtext == 'Транскрипция видео':
		# Транскрипция youtube-видео
		msg = bot.send_message(chatid, 'Введите ссылку на испанское youtube-видео:')
		bot.register_next_step_handler(msg, add_words)
	elif msgtext == 'Переводчик':
		# Переводчик. Создаем Inline-клавиатуру и кнопки, а затем выводим их
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton(text='С испанского на русский', callback_data='esp2rus'))
		markup.add(types.InlineKeyboardButton(text='С русского на испанский', callback_data='rus2esp'))
		bot.send_message(chatid, 'Выберите язык', reply_markup=markup)
	elif msgtext == 'Уроки':
		# Уроки. Создаем Inline-клавиатуру и кнопки, а затем выводим их
		markup = types.InlineKeyboardMarkup()
		item1 = types.InlineKeyboardButton(text='Вводный урок', callback_data='lesson0')
		markup.add(item1)
		bot.send_message(chatid, 'Выберите урок', reply_markup=markup)
	elif msgtext == 'Перевод случайного слова':
		# Тест на знание испанских слов. Получаем случайное слово и переходим
		# к обработчику-тесту.
		word = choice(lessons.words)
		mesg = bot.send_message(message.chat.id, f'Введите перевод слова "{word}"')
		bot.register_next_step_handler(mesg, test_translate, word)
	elif msgtext == 'Материалы для изучения':
		# Вывод материалов для изучения
		bot.send_message(message.chat.id, '''
Вот материалы для изучения испанского языка:

<b>Книги</b>
<u>Р.А. Гонсалес, Р.Р. Алимова - "Испанский за 3 месяца. Интенсивный курс"</u>
		''', parse_mode='html')
	else:
		# Выводим сообщение что команда не найдена
		bot.send_message(chatid, f'Команда "{msgtext}" не найдена :(')


def launch_bot() -> None:
	# Запуск бота
	db_helper.setup()										# Установка базы данных
	
	bot_start_alert()										# Уведомление администраторам о запуске бота
	bot.infinity_polling()									# Бесконечный поллинг бота


if __name__ == '__main__':
	# Если файл исполняемый, то запускаем метод launch_bot, который стартует бота
	print('[+] Запускаем бота')
	print('Бот создан @OkulusDev, больше на @OkulusHub_public')
	launch_bot()
