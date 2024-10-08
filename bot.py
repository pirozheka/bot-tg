import telebot
from env import TOKEN
from sqlalchemy.orm import Session
from dbcreating import Note, engine


bot = telebot.TeleBot(TOKEN)

# Функция для сохранения заметки
def save_note(caption, body, category):
    with Session(autoflush=False, bind=engine) as db:
        note = Note(caption=caption, body=body, category=category)
        db.add(note)
        db.commit()
        print("Заметка сохранена успешно")




#Реакция на команду start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello!")

#Реакция на команду addnote
@bot.message_handler(commands=['addnote'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello!")

bot.polling()