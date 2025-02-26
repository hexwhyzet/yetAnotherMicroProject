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
git clone https://github.com/hexwhyzet/yetAnotherMicroProject.git
cd yetAnotherMicroProject
docker build -t telegram_bot_container .
docker run -d --name telegram_bot -e API_TOKEN=<your-secret-telegram-bot-token> telegram_bot_container
```

## Тестовые базы данных
[sample_databases/car.db](sample_databases%2Fcar.db) источник: [GitHub](https://github.com/dtaivpp/car_company_database)

[sample_databases/sakila.db](sample_databases%2Fsakila.db) источник: [GitHub](https://github.com/bradleygrant/sakila-sqlite3)

## Демонстрация работы

[](https://github.com/user-attachments/assets/d4903ee1-d09c-4cd1-ba7d-03e4dd489da3)
