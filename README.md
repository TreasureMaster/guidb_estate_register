# Инструкция для запуска

## Установка библиотек

1. Запуск установки требуемых библиотек: `pip install -r requirements.txt`
2. Если модули **win32api** и **win32print** не определяются, то нужно запустить:
   `py Scripts/pywin32_postinstall.py -install`
   Файл находится либо в пути интерпретатора, либо в папке `venv` при использовании **virtualenv**.

## Инициализация базы данных

Чтобы создать и заполнить базу данных первыми данными, нужно запустить скрипт: `python init_db.py`.

При изменении констант в файле конфигурации `models/models.py` необходимо удалить папку `__pycache__`.

Данные входа для администратора:
1. логин - `admin1`
2. пароль - `pswd`

Также можно использовать предустановленного пользователя с логином `user1` и тем же паролем, что и у админа.

## Запуск приложения

Запуск приложения осуществляется командой `python app.py`.
