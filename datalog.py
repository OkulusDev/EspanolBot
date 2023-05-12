#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Телеграм-бот для изучения испанского языка: библиотека для сбора данных
Создатель: Okulus Dev (C) 2023 ALL RIGHTS REVERSED | ВСЕ ПРАВА СОХРАНЕНЫ
Лицензия: GNU GPL v3"""
import os


def file_is_empty(path: str) -> bool:
	"""Данная функция проверяет, пустой ли файл.
	Аргументы:
	 + path: str - путь до файла
	Возвращает:
	 + bool - True, если файл пустой, если не пустой, то False"""
	return os.stat(path).st_size == 0


def clear_file(path: str) -> None:
	with open(path, 'w'): pass
