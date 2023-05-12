#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Телеграм-бот для изучения испанского языка: библиотека для взаимодействия с базой данных
Создатель: Okulus Dev (C) 2023 ALL RIGHTS REVERSED | ВСЕ ПРАВА СОХРАНЕНЫ
Лицензия: GNU GPL v3"""
import sqlite3														# Импорт библиотеки для взаимодействия с базами данных SQLite3


class DBHelper:
	"""Помощник для взаимодействия с базой данных"""
	def __init__(self, dbname='bot.sqlite'):
		"""Инициализация помощника
		Аргументы:
		 + dbname - название базы данных"""
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname, check_same_thread=False)
		self.cursor = self.conn.cursor()

	def setup(self) -> None:
		"""Создание таблицы. Данная функция создает таблицу в базе данных, если она не создана, 
		со значениями id - ID пользователя и level - уровнем пользователя. 
		id является цифровым объектом, а level строковым."""
		sql = 'CREATE TABLE IF NOT EXISTS users (id integer, level text)'
		self.conn.execute(sql)
		self.conn.commit()

	def add_user(self, user_id, level=0) -> None:
		"""Добавление пользователя: данная функция добавляет пользователя в базу данных
		с его уникальным идентификатором - ID и уровнем, который по умолчанию равен 0
		Аргументы:
		 + user_id - ID пользователя
		 + level - уровень пользователя (значение по умолчанию = 0)"""
		sql = 'INSERT INTO users (id, level) VALUES (?, ?)'
		args = (user_id, level)
		self.conn.execute(sql, args)
		self.conn.commit()

	def delete_user(self, user_id) -> None:
		"""Удаление пользователя по ID в базе данных. Данная функция удаляет пользователя из
		базы данных, используя его ID.
		Аргументы:
		 + user_id - ID пользователя"""
		sql = 'DELETE FROM users WHERE id = (?)'
		args = (user_id, )
		self.conn.execute(sql, args)
		self.conn.commit()

	def get_user_level(self, user_id):
		"""Получение уровня пользователя. Данная функция получает уровень пользователя по ID
		Аргументы:
		 + user_id - ID пользователя
		Возвращает:
		 + data - информация о пользователе"""
		sql = 'SELECT level FROM users WHERE id = ?'
		args = (user_id, )
		data = self.conn.execute(sql, args).fetchall()
		self.conn.commit()

		return data

	def update_level(self, user_id, new_level) -> None:
		"""Обновление уровня. Данная функция обновляет уровень пользователя по ID.
		Аргументы:
		 + user_id - ID пользователя
		 + new_level - новое значение уровня"""
		sql = 'UPDATE users SET level = ? WHERE id = ?'
		args = (new_level, user_id)
		self.conn.execute(sql, args)
		self.conn.commit()		

	def get_users_ids(self):
		"""Получение всех ID пользователей. Данная функция получает только все ID пользователей
		в базе"""
		sql = 'SELECT id FROM users'
		return [x[0] for x in self.conn.execute(sql)]

	def get_users(self) -> list:
		"""Получение всех пользователей.. Данная функция получает всех пользователей, вместе
		с их ID и уровнем.
		Возвращает:
		 + list (список) - список с информацией о пользователях"""
		sql = 'SELECT id, level FROM users'
		result = []
		for i in self.conn.execute(sql):
			result.append(i)
		
		return result
