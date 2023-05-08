#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Телеграм-бот для изучения испанского языка: библиотека для взаимодействия с базой данных
Создатель: Okulus Dev (C) 2023 ALL RIGHTS REVERSED | ВСЕ ПРАВА СОХРАНЕНЫ
Лицензия: GNU GPL v3"""
import sqlite3


class DBHelper:
	"""Помощник для взаимодействия с базой данных"""
	def __init__(self, dbname='bot.sqlite'):
		"""Инициализация помощника
		Аргументы:
		 + dbname - название базы данных"""
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname, check_same_thread=False)
		self.cursor = self.conn.cursor()

	def setup(self):
		# Создание таблицы
		sql = 'CREATE TABLE IF NOT EXISTS users (id integer, level text)'
		self.conn.execute(sql)
		self.conn.commit()

	def add_user(self, user_id, level=0):
		# Добавление пользователя
		sql = 'INSERT INTO users (id, level) VALUES (?, ?)'
		args = (user_id, level)
		self.conn.execute(sql, args)
		self.conn.commit()

	def delete_user(self, user_id):
		# Удаление пользователя
		sql = 'DELETE FROM users WHERE id = (?)'
		args = (user_id, )
		self.conn.execute(sql, args)
		self.conn.commit()

	def get_user_level(self, user_id):
		# Получить уровень пользователя по ID
		sql = 'SELECT level FROM users WHERE id = ?'
		args = (user_id, )
		data = self.conn.execute(sql, args).fetchall()
		self.conn.commit()
		return data

	def update_level(self, user_id, new_level):
		# Обновить уровень пользователя по ID
		sql = 'UPDATE users SET level = ? WHERE id = ?'
		args = (new_level, user_id)
		self.conn.execute(sql, args)
		self.conn.commit()		

	def get_users_ids(self):
		# Получение ID пользователей
		sql = 'SELECT id FROM users'
		return [x[0] for x in self.conn.execute(sql)]

	def get_users(self):
		# Получение данных пользователей
		sql = 'SELECT id, level FROM users'
		result = []
		for i in self.conn.execute(sql):
			result.append(i)
		return result
