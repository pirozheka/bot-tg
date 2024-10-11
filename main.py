from telebot import types
from extensions import *
from timer import timers, input_time
from datetime import datetime

def main():

    # Команда /start
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup()
        btn_vacation = types.InlineKeyboardButton('Отпуск', callback_data="vacation")
        btn_diary = types.InlineKeyboardButton('Ежедневник', callback_data="diary")
        markup.row(btn_vacation, btn_diary)
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.username}!  Выберите команду:", reply_markup=markup)


    # обработка команды /timer
    @bot.message_handler(commands=['timer'])
    # запрашивает у пользователя формат ввода даты и времени
    def start_timer(message):
        bot.send_message(message.chat.id, "'Введите дату и время события в формате 'YYYY-MM-DD HH:MM:SS'.")
        # регистрирует следующий шаг
        bot.register_next_step_handler(message, input_time)


    # обработчик команды, вызывающей таймер
    @bot.message_handler(commands=['mytimer'])
    def check_timer(message):
        # получаем id пользователя
        user_id = message.chat.id
        # проверяем есть ли активный таймер
        if user_id in timers:
            # если пользователь имеет таймер, то получаем данные: поток, событие остановки и время срабатывания
            thread, stop_event, set_time = timers[user_id]
            # получаем сейчас
            now = datetime.now()
            # вычисляем время до срабатывания
            difference_time = set_time - now

            # если оставшееся время больше 0
            if difference_time.total_seconds() > 0:
                # вычисляем дни, часы, минуты, секунды
                days = difference_time.days
                sec = difference_time.seconds
                hour = sec // 3600
                minutes = (sec // 60) % 60
                seconds = sec % 60

                # отправка сообщения
                time_message = f'Осталось {days} дней, {hour} часов, {minutes} минут, {seconds} секунд.'
                bot.send_message(user_id, time_message)
        # если активного таймера нет, отправляем сообщение
        else:
            bot.send_message(user_id, "У вас нет активного таймера.")


    # обработка команды удаления таймера
    @bot.message_handler(commands=['deletetimer'])
    def delete_timer(message):
        # получаем id пользователя
        user_id = message.chat.id
        # если пользователь существует
        if user_id in timers:
            # если пользователь имеет таймер, то получаем данные: поток, событие остановки и время срабатывания
            thread, stop_event, set_time = timers[user_id]
            # устанавливаем событие остановки потока
            stop_event.set()
            # удаляем таймер из словаря
            del timers[user_id]
            # отправляем сообщение
            bot.send_message(user_id, "Все ваши активные таймеры были удалены.")
        # если пользователя нет в таймерах
        else:
            bot.send_message(user_id, "У вас нет активных таймеров для удаления.")


    # Команда /help
    @bot.message_handler(commands=['help'])
    def help(message):
        bot.send_message(message.chat.id, "Полезная информация")


    @bot.callback_query_handler(func=lambda callback: True)
    def callback_start(callback):
        if callback.data == "diary":
            markup = types.InlineKeyboardMarkup()
            btn_add_note = types.InlineKeyboardButton('Добавить заметку', callback_data="add_note")
            btn_view_note = types.InlineKeyboardButton('Просмотреть заметку', callback_data="view_note")
            btn_view_note = types.InlineKeyboardButton('Редактировать заметку', callback_data="add_note")
            btn_delete_note = types.InlineKeyboardButton('Удалить заметку', callback_data="delete_note")
            markup.row(btn_add_note, btn_view_note, btn_delete_note)
            btn_categories_list = types.InlineKeyboardButton('Просмотр категорий', callback_data="categories_list")
            btn_categories_filter = types.InlineKeyboardButton('Задачи по категориям', callback_data="categories_filter")
            markup.row(btn_categories_list, btn_categories_filter)
            bot.edit_message_text("Пожалуйста, выберите действие", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "add_note":
            chat_id = callback.message.chat.id
            notes_data[chat_id] = {}
            bot.send_message(chat_id, "Введите заголовок заметки:")
            bot.register_next_step_handler(callback.message, process_caption_step)

        if callback.data == "view_note":
            chat_id = callback.message.chat.id
            bot.send_message(chat_id, "Введите заголовок заметки для просмотра:")
            bot.register_next_step_handler(callback.message, process_view_note)

        if callback.data == "categories_list":
            chat_id = callback.message.chat.id
            categories = get_categories_list()
            if categories:
                categories_str = "\n".join(categories)
                bot.send_message(chat_id, f"Список категорий:\n{categories_str}")
            else:
                bot.send_message(chat_id, "Категорий пока нет.")

        if callback.data == "delete_note":
            chat_id = callback.message.chat.id
            bot.send_message(chat_id, "Введите заголовок заметки для удаления:")
            bot.register_next_step_handler(callback.message, process_delete_note)

        if callback.data == "categories_filter":
            chat_id = callback.message.chat.id
            bot.send_message(chat_id, "Введите категорию для получения заметок:")
            bot.register_next_step_handler(callback.message, send_notes_by_category)

        if callback.data == "vacation":
            markup = types.InlineKeyboardMarkup()
            btn_dp_yes = types.InlineKeyboardButton('Да', callback_data="vacation_yes")
            btn_dp_no = types.InlineKeyboardButton('Нет', callback_data="vacation_no")
            markup.row(btn_dp_yes, btn_dp_no)
            bot.edit_message_text("Вы уже выбрали место?", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "vacation_yes":
            markup = types.InlineKeyboardMarkup()
            btn_vp_yes = types.InlineKeyboardButton('Да', callback_data="vacation_prepare_yes")
            btn_vp_no = types.InlineKeyboardButton('Нет', callback_data="vacation_prepare_no")
            markup.row(btn_vp_yes, btn_vp_no)
            bot.edit_message_text("Приступим к подготовке", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "vacation_no":
            markup = types.InlineKeyboardMarkup()
            btn_vacation_add = types.InlineKeyboardButton('Далее', callback_data="vacation_yes")
            markup.row(btn_vacation_add)
            bot.edit_message_text("Вот рекомендации от наших партнёров", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "vacation_prepare_yes":
            markup = types.InlineKeyboardMarkup()
            btn_employer = types.InlineKeyboardButton('Работа', callback_data="employer")
            btn_tickets = types.InlineKeyboardButton('Билеты', callback_data="tickets")
            markup.row(btn_employer, btn_tickets)
            btn_hotel = types.InlineKeyboardButton('Отель', callback_data="hotel")
            btn_plans = types.InlineKeyboardButton('Планы', callback_data="plans")
            markup.row(btn_hotel, btn_plans)
            bot.edit_message_text("Выберите действие", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "vacation_prepare_no":
            bot.edit_message_text("Приятного отдыха!", callback.message.chat.id, callback.message.message_id)


        if callback.data == "tickets":
            markup = types.InlineKeyboardMarkup()
            btn_tickets_yes = types.InlineKeyboardButton('Да', callback_data="tickets_reminder")
            btn_tickets_no = types.InlineKeyboardButton('Нет', callback_data="tickets_no")
            markup.row(btn_tickets_yes, btn_tickets_no)
            bot.send_message( callback.message.chat.id, "Вы уже приобрели билеты?", reply_markup=markup)

        if callback.data == "tickets_no":
            markup = types.InlineKeyboardMarkup()
            btn_tickets_reminder = types.InlineKeyboardButton('Следующий шаг', callback_data="tickets_reminder")
            markup.row(btn_tickets_reminder)
            bot.edit_message_text("Вот хорошие предложения от наших партнёров: ", callback.message.chat.id, callback.message.message_id)

        if callback.data == "tickets_reminder":
            markup = types.InlineKeyboardMarkup()
            btn_tickets_set_timer = types.InlineKeyboardButton('Установить напоминание', callback_data="tickets_set_timer")
            markup.row(btn_tickets_set_timer)
            bot.edit_message_text("Давай запишем чтобы не забыть!", callback.message.chat.id, callback.message.message_id)

        if callback.data == "employer":
            markup = types.InlineKeyboardMarkup()
            btn_yes = types.InlineKeyboardButton('Да', callback_data='yes')
            btn_no = types.InlineKeyboardButton('Нет', callback_data='no')
            markup.row(btn_yes, btn_no)
            bot.send_message(callback.message.chat.id, f'Ты уже предупредил начальство, {callback.message.chat.username}?', reply_markup=markup)

        if callback.data == 'yes':
            bot.send_message(callback.message.chat.id, "Отлично! Когда планируешь отдыхать? Введите дату и время события в формате 'YYYY-MM-DD HH:MM:SS'.")
            bot.register_next_step_handler(callback.message, input_date)

        if callback.data == 'no':
            markup = types.InlineKeyboardMarkup()
            btn_yes_start = types.InlineKeyboardButton('Да', callback_data='yes_start')
            btn_no_start = types.InlineKeyboardButton('Нет', callback_data='no_start')
            markup.row(btn_yes_start, btn_no_start)
            bot.send_message(callback.message.chat.id, 'Тебе нужно об этом напомнить?', reply_markup=markup)

        if callback.data == 'yes_start':
            bot.send_message(callback.message.chat.id, 'Давай создадим напоминание! Введите дату и время события в формате "YYYY-MM-DD HH:MM:SS".')
            bot.register_next_step_handler(callback.message, input_date)

        if callback.data == 'no_start':
            bot.send_message(callback.message.chat.id, 'Если нужно, напомни мне позже!')
            time.sleep(2)
            bot.send_message(callback.message.chat.id, 'Воспользуйся командой "Приступим к подготовке", что бы продолжить заполнять другие пункты.')

        if callback.data == 'yes_time':
            # Здесь можно добавить расписание напоминаний
            bot.edit_message_text('Создал напоминание', callback.message.chat.id, callback.message.message_id)

        if callback.data == 'no_time':
            bot.edit_message_text('Хорошо, напоминание не будет создано.', callback.message.chat.id, callback.message.message_id)

        if callback.data == "hotel":
            markup = types.InlineKeyboardMarkup()
            btn_hotel_reminder = types.InlineKeyboardButton('Да', callback_data="hotel_reminder")
            btn_hotel_no = types.InlineKeyboardButton('нет', callback_data="hotel_no")
            markup.row(btn_hotel_reminder, btn_hotel_no)
            bot.send_message(callback.message.chat.id, "Ты уже выбрал отель?", reply_markup=markup)

        if callback.data == "hotel_no":
            markup = types.InlineKeyboardMarkup()
            btn_hotel_yes = types.InlineKeyboardButton('Далее', callback_data="hotel")
            markup.row(btn_hotel_yes)
            bot.edit_message_text("Вот хорошие предложения от наших партнеров:", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "hotel_reminder":
            markup = types.InlineKeyboardMarkup()
            btn_hotel_yes = types.InlineKeyboardButton('Да', callback_data="hotel_reminder_yes")
            btn_hotel_no = types.InlineKeyboardButton('нет', callback_data="hotel_reminder_no")
            markup.row(btn_hotel_yes, btn_hotel_no)
            bot.edit_message_text("Давай запишем чтобы не забыть!", callback.message.chat.id, callback.message.message_id, reply_markup=markup)

        if callback.data == "plans":
            pass

    # Включение бота
    bot.polling(none_stop=True)


if __name__ == "__main__":
    scheduler.add_job(check_timers, 'interval', seconds=60)  # Проверяем каждые 60 секунд
    scheduler.start()
    main()