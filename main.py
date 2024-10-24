import os
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

BASE_DIR = './user_databases'

user_db_selections = {}

commands_description = (
    "Чтобы добавить базу данных просто отправьте ее файлом в чат.\n\n"
    "Просто отправьте SQL-запрос, начиная с 'SELECT', и я выполню его на выбранной базе данных!\n\n"
    "/help - Получить описание всех команд.\n"
    "/list - Показать список доступных баз данных, количество таблиц и строк в каждой базе.\n"
    "/info [индекс базы (опционально)] [имя таблицы (опционально)] [имя столбца (опционально)] - Показать схемы всех таблиц базы данных. Можно указать базу, таблицу и столбец для детальной информации.\n"
    "/clear - Удалить все загруженные базы данных.\n"
    "/select - Выбрать базу данных для выполнения запросов.\n"
    "Просто отправьте SQL-запрос, начиная с 'SELECT', и я выполню его на выбранной базе данных!"
)


def get_user_dir(user_id):
    user_dir = os.path.join(BASE_DIR, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return user_dir


@dp.message(F.document.file_name.endswith('.sqlite') | F.document.file_name.endswith('.db'))
async def handle_file(message: Message):
    document = message.document

    if document:
        user_dir = get_user_dir(message.from_user.id)
        file_path = os.path.join(user_dir, document.file_name)

        if os.path.exists(file_path):
            await message.answer(f"Файл '{document.file_name}' уже существует. Переименуйте файл или загрузите другой.")
        else:
            await bot.download(document, file_path)
            await message.answer(f"База данных '{document.file_name}' сохранена.")
    else:
        await message.answer("Пожалуйста, отправьте файл с расширением .sqlite или .db.")


@dp.message(F.text.lower().startswith("select"))
async def handle_sql_query(message: Message):
    user_id = message.from_user.id

    if user_id not in user_db_selections:
        await message.answer("Вы не выбрали базу данных. Используйте команду /select, чтобы выбрать базу данных.")
        return

    db_path = user_db_selections[user_id]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(message.text)
        rows = cursor.fetchall()

        if rows:
            result = "\n".join([str(row) for row in rows])
            await message.answer(f"Результат:\n{result}")
        else:
            await message.answer("Запрос выполнен, но данных не найдено.")

        conn.close()
    except sqlite3.Error as e:
        await message.answer(f"Ошибка выполнения запроса: {e}")


@dp.message(Command("select"))
async def select_database(message: Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    files = [f for f in os.listdir(user_dir) if f.endswith('.sqlite') or f.endswith('.db')]

    if not files:
        await message.answer("Нет сохраненных баз данных.")
        return

    file_list = "\n".join([f"{idx + 1}. {f}" for idx, f in enumerate(files)])
    await message.answer(f"Выберите базу данных для выполнения запросов:\n{file_list}\nОтветьте номером файла.")


@dp.message(F.text.regexp(r'^\d+$'))
async def handle_database_selection(message: Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    files = [f for f in os.listdir(user_dir) if f.endswith('.sqlite') or f.endswith('.db')]

    if not files:
        await message.answer("Нет сохраненных баз данных.")
        return

    selection = int(message.text) - 1
    if selection < 0 or selection >= len(files):
        await message.answer("Неверный номер файла. Попробуйте снова.")
        return

    db_path = os.path.join(user_dir, files[selection])
    user_db_selections[user_id] = db_path

    await message.answer(f"Вы выбрали базу данных: {files[selection]}. Теперь вы можете отправить SQL-запрос.")


@dp.message(Command("clear"))
async def clear_databases(message: Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    for file_name in os.listdir(user_dir):
        file_path = os.path.join(user_dir, file_name)
        os.remove(file_path)

    if user_id in user_db_selections:
        del user_db_selections[user_id]

    await message.answer("Все базы данных были удалены.")


@dp.message(Command("info"))
async def status_command(message: Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    args = message.text.split()[1:]
    db_index = int(args[0]) - 1 if len(args) > 0 else None
    table_name_filter = args[1] if len(args) > 1 else None
    column_name_filter = args[2] if len(args) > 2 else None

    files = [f for f in os.listdir(user_dir) if f.endswith('.sqlite') or f.endswith('.db')]

    if not files:
        await message.answer("У вас нет загруженных баз данных.")
        return

    result = []

    if db_index is not None:
        if db_index < 0 or db_index >= len(files):
            await message.answer("Неверный индекс базы данных.")
            return
        db_files_to_check = [files[db_index]]
    else:
        db_files_to_check = files

    for db_file in db_files_to_check:
        db_path = os.path.join(user_dir, db_file)
        result.append(f"База данных: {db_file}")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            if tables:
                for table in tables:
                    table_name = table[0]

                    if table_name_filter and table_name != table_name_filter:
                        continue

                    result.append(f"  Таблица: {table_name}")

                    cursor.execute(f"PRAGMA table_info({table_name});")
                    schema = cursor.fetchall()

                    if schema:
                        for column in schema:
                            column_name = column[1]
                            column_type = column[2]

                            if column_name_filter and column_name != column_name_filter:
                                continue

                            column_info = f"    {column_name} {column_type}"
                            result.append(column_info)
                    else:
                        result.append("    Схема таблицы не найдена.")
                    result.append('')
            else:
                result.append("  Нет таблиц в базе данных.")

            conn.close()
        except sqlite3.Error as e:
            result.append(f"Ошибка при доступе к базе данных {db_file}: {e}")

    await message.answer("\n".join(result))


@dp.message(Command("list"))
async def list_databases(message: Message):
    user_id = message.from_user.id
    user_dir = get_user_dir(user_id)

    files = [f for f in os.listdir(user_dir) if f.endswith('.sqlite') or f.endswith('.db')]

    if not files:
        await message.answer("У вас нет загруженных баз данных.")
        return

    result = []
    total_bases = len(files)
    result.append(f"Количество доступных баз данных: {total_bases}")
    result.append("")

    for db_file in files:
        db_path = os.path.join(user_dir, db_file)
        db_size = os.path.getsize(db_path) / (1024 * 1024)
        result.append(f"База данных: {db_file} (Размер: {db_size:.2f} МБ)")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_count = len(tables)
            total_rows = 0

            if tables:
                for table in tables:
                    table_name = table[0]

                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    row_count = cursor.fetchone()[0]
                    total_rows += row_count

                result.append(f"  Количество таблиц: {table_count}")
                result.append(f"  Суммарное количество строк: {total_rows}")
            else:
                result.append("  Нет таблиц в базе данных.")

            conn.close()
        except sqlite3.Error as e:
            result.append(f"Ошибка при доступе к базе данных {db_file}: {e}")

        result.append("")

    await message.answer("\n".join(result))


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот для работы с базами данных SQLite. Вот список доступных команд:\n\n" + commands_description
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Список доступных команд:\n\n" + commands_description
    )


if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    dp.run_polling(bot)
