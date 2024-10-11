# Импорт необходимых библиотек
import telebot
from config import API_TOKEN
from sqlalchemy.orm import Session
from dbcreate import Note, engine
import time
from telebot import types
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# Инициализация бота и переменных
bot = telebot.TeleBot(API_TOKEN)
notes_data = {}  # Переменная для временного хранения данных заметки
scheduler = BackgroundScheduler()  # Инициализируем расписание

# Функции для работы с заметками

# Проверяет поля таймеров у каждой заметки
def check_timers():
    with Session(autoflush=False, bind=engine) as db:
        now = datetime.now()
        # Извлекаем заметки с таймером, сработавшим на текущий момент или ранее
        notes = db.query(Note).filter(Note.timer != None, Note.timer <= now).all()

        for note in notes:
            send_notification(note)  # Отправляем уведомление
            note.timer = None  # Сброс таймера после срабатывания
            db.commit()

# Отправляет уведомление о заметке в чат
def send_notification(note):
    bot.send_message(note.chat_id, f"Напоминание о записи: '{note.caption}': \n '{note.body}'")


# Функция для сохранения заметки
def save_note(bot, caption, category, body, chat_id, timer=None):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption, Note.chat_id == chat_id).first()

        if note:
            # Обновляем существующую заметку
            note.category = category
            note.body = body
            note.timer = timer
            message = f'Запись "{caption}" обновлена.'
        else:
            # Создаем новую заметку
            new_note = Note(caption=caption, category=category, body=body, chat_id=chat_id, timer=timer)
            db.add(new_note)
            message = f'Запись "{caption}" добавлена.'

        # Пытаемся сохранить изменения в базе данных
        try:
            db.commit()
            # Уведомляем пользователя в чате о добавлении или редактировании заметки
            bot.send_message(chat_id, message)
        except Exception as e:
            db.rollback()  # В случае ошибки откатываем изменения
            print(f'Ошибка при сохранении заметки: {e}')
            bot.send_message(chat_id, 'Ошибка при сохранении заметки. Пожалуйста, повторите попытку.')


# Функция для удаления заметки
def delete_note(caption):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption).first()
        
        if note:
            db.delete(note)  # Удаляем заметку
            try:
                db.commit()
                print(f'Запись "{caption}" удалена.')
                return True
            except Exception as e:
                db.rollback()  # В случае ошибки откатываем изменения
                print(f'Ошибка при удалении заметки: {e}')
                return False
        else:
            print(f'Запись "{caption}" не найдена.')
            return False

# Функция для просмотра заметки
def view_note(caption):
    with Session(autoflush=False, bind=engine) as db:
        note = db.query(Note).filter(Note.caption == caption).first()
        return note

# Получение списка категорий 
def get_categories_list():
    with Session(autoflush=False, bind=engine) as db:
        categories = db.query(Note.category).distinct().all()
        cat_list = [category[0] for category in categories]  # Создаем список категорий
        return cat_list

# Получение заметок по категории    
def get_notes_by_category(category):
    with Session(autoflush=False, bind=engine) as db:
        notes = db.query(Note).filter(Note.category == category).all()
        return notes

# Обработка сообщений от пользователя

def process_caption_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['caption'] = message.text
    bot.send_message(chat_id, "Теперь введите текст заметки:")
    bot.register_next_step_handler(message, process_body_step)

def process_body_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['body'] = message.text
    bot.send_message(chat_id, "Введите категорию заметки:")
    bot.register_next_step_handler(message, process_category_step)

def process_category_step(message):
    chat_id = message.chat.id
    notes_data[chat_id]['category'] = message.text
    bot.send_message(chat_id, "Хотите установить таймер на эту заметку? Введите дату и время в формате 'YYYY-MM-DD HH:MM:SS' или 'нет', чтобы пропустить:")
    bot.register_next_step_handler(message, process_timer_step)

def process_timer_step(message):
    chat_id = message.chat.id
    timer_text = message.text

    if timer_text.lower() != 'нет':
        try:
            timer = datetime.strptime(timer_text, '%Y-%m-%d %H:%M:%S')  # Преобразуем текст в дату
            notes_data[chat_id]['timer'] = timer
        except ValueError:
            bot.send_message(chat_id, "Неверный формат даты. Пожалуйста, введите дату в формате 'YYYY-MM-DD HH:MM:SS'.")
            bot.register_next_step_handler(message, process_timer_step)
            return
    else:
        notes_data[chat_id]['timer'] = None

    # Сохраняем заметку в базу данных
    save_note(
        bot,
        caption=notes_data[chat_id]['caption'],
        body=notes_data[chat_id]['body'],
        category=notes_data[chat_id]['category'],
        chat_id=chat_id,
        timer=notes_data[chat_id].get('timer')
    )
    del notes_data[chat_id]  # Удаляем временные данные
    bot.send_message(chat_id, "Заметка сохранена успешно.")

# Функции для взаимодействия с заметками

def send_notes_by_category(message):
    chat_id = message.chat.id
    category = message.text
    notes = get_notes_by_category(category)
    
    if notes:
        notes_text = "\n\n".join(
            [
                f"Заголовок: {note.caption}\nТекст: {note.body}\nТаймер: {note.timer.strftime('%Y-%m-%d %H:%M:%S') if note.timer else 'Не установлен'}"
                for note in notes
            ]
        )
        bot.send_message(chat_id, f"Заметки в категории '{category}':\n\n{notes_text}")
    else:
        bot.send_message(chat_id, f"В категории '{category}' заметок не найдено.")

def process_delete_note(message):
    chat_id = message.chat.id
    caption = message.text
    if delete_note(caption):
        bot.send_message(chat_id, f'Заметка "{caption}" успешно удалена.')
    else:
        bot.send_message(chat_id, f'Заметка "{caption}" не найдена.')

def process_view_note(message):
    chat_id = message.chat.id
    caption = message.text
    note = view_note(caption)
    
    if note:
        bot.send_message(chat_id, f"{note.caption}\n{note.body}")
    else:
        bot.send_message(chat_id, f'Заметка "{caption}" не найдена.')

# Обработка ввода даты
def input_date(message):
    try:
        planned_date = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')  # Проверяем формат даты
        bot.send_message(message.chat.id, f'Вы запланировали отдых на {planned_date.date()}.')
        time.sleep(2)  # Задержка перед следующим сообщением
        markup_time_start = types.InlineKeyboardMarkup()
        btn_yes_start = types.InlineKeyboardButton('Да', callback_data='yes_time')
        btn_no_start = types.InlineKeyboardButton('Нет', callback_data='no_time')
        markup_time_start.row(btn_yes_start, btn_no_start)
        bot.send_message(message.chat.id, f'Начнем отсчет?', reply_markup=markup_time_start)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД ЧЧ:MM:СС.')
        bot.register_next_step_handler(message, input_date)
