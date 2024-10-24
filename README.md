# Telegram SQLite Bot

Проект представляет собой Telegram-бота для работы с SQLite базами данных. Бот позволяет пользователю загружать базы
данных, выполнять SQL-запросы, получать информацию о таблицах и схеме базы данных.

## Функциональность

- Загрузка SQLite баз данных.
- Выполнение SQL-запросов.
- Получение схемы таблиц базы данных.
- Показ списка доступных баз данных с их размером, количеством строк и количеством таблиц.
- Удаление всех загруженных баз данных из контекста.

## Установка и запуск

```bash
git clone https://github.com/your_username/telegram-sqlite-bot.git
cd telegram-sqlite-bot
docker build -t telegram_bot_container .
docker run -d --name telegram_bot -e API_TOKEN=your_telegram_api_token telegram_bot_container
```

## Тестовые базы данных
[sample_databases/car.db](sample_databases%2Fcar.db) источник: [GitHub](https://github.com/dtaivpp/car_company_database)

[sample_databases/sakila.db](sample_databases%2Fsakila.db) источник: [GitHub](https://github.com/bradleygrant/sakila-sqlite3)

## Демонстрация работы

<video src="./demo/video.mp4" width="600" controls></video>