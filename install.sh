#!/usr/bin/sh
# -*- coding:utf-8 -*-
# Этот скрипт установит зависимости для EspanolBot или других python3-програм

distro=$(lsb_release --id --short)							# Имя дистрибутива/операционной системы

# Начало установки
echo "Нажмите Enter чтобы начать установку"
read start
clear

# Установка python3
echo "Установить python3? (y/n)"
read installing
if [ $installing = 'y' ]; then
	echo "Установка . . . "
	if [ $distro = "Debian" ]; then
		# Устанавливаем пакет с помощью пакетного менеджера apt (dpkg), если система - debian
		sudo apt install python3
	elif [ $distro = "Arch" ]; then
		# Устанавливаем пакет с помощью пакетного менеджера pacman, если система - arch
		sudo pacman -Sy python3
	elif [ $distro == 'Fedora' ]; then
		# Устанавливаем пакет с помощью пакетного менеджера dnf (rpm), если система - fedora
		sudo dnf install python3
	else
		# Сообщаем пользователю, что его система не поддерживается
		echo "Ваша операционная система ($distro) не поддерживается. Установите python3 самостоятельно."
	fi
fi

# Установка python3-pip
echo "Установить python3-pip? (y/n)"
read installing2
if [ $installing2 = 'y' ]; then
	echo "Установка . . . "
	if [ $distro = "Debian" ]; then
		# Устанавливаем пакет с помощью пакетного менеджера apt (dpkg), если система - debian
		sudo apt install python3-pip
	elif [ $distro = "Arch" ]; then
		# Устанавливаем пакет с помощью пакетного менеджера pacman, если система - arch
		sudo pacman -Sy python-pip
	elif [ $distro = "Fedora" ]; then
		# Устанавливаем пакет с помощью пакетного менеджера dnf (rpm), если система - fedora
		sudo dnf install python3-pip
	else
		# Сообщаем пользователю, что его система не поддерживается
		echo "Ваша операционная система ($distro) не поддерживается. Установите python-pip самостоятельно."
	fi
fi

# Устанавливаем зависимости (пакетный менеджер python3 - pip)
echo "Установка зависимостей (pip) . . . "
pip3 install -r req.txt											# Устанавливаем зависимости из файла req.txt
echo "Зависимости установлены (pip)!"

# Сообщаем о завершении установки
echo "Установка завершена!"
