import time
from datetime import datetime
import threading
from extensions import bot

# глобальная переменная хранит в себе инфо о таймерах по ключу user_id)
timers = {}

# основная функция таймера
def timer(user_id, set_time, stop_event):
    # цикл будет продолжаться, пока stop_event не будет установлено (is_set вернет True)
    # позволяет завершить работу функции из потока
    while not stop_event.is_set():
        # получаем текущее время
        now = datetime.now()
        # если сейчас больше или равно полученному времени
        if now >= set_time:
            try:
                bot.send_message(user_id, 'Настало время события!')
                del timers[user_id]
            except Exception as e:
                print(f'Ошибка отправки сообщения: {e}')
            break
        time.sleep(1)



# следующий шаг после ввода
def input_time(message):
    # блок try обрабатывает сообщение с датой и временем
    try:
        # полученное время преобразовывается в объект datetime
        set_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S')
        # от юзера
        user_id = message.chat.id

        # Проверка на то, что введенная дата больше текущего момента
        if set_time <= datetime.now():
            bot.send_message(user_id, 'Вызовите команду /timer и введите дату и время, которые больше текущего времени.')
            return

        # если пользователя нет в таймерах, то создается новый поток
        if user_id not in timers:
            # Используем Event для завершения потока
            stop_event = threading.Event()
            # создание отдельного потока, функция таймер не будет мешать выполнению других задач
            timer_th = threading.Thread(target=timer, args=(user_id, set_time, stop_event))
            # запуск потока
            timer_th.start()
            # сохраняем по ключу в словаре (проверяет запущен ли таймер у пользователя)
            timers[user_id] = (timer_th, stop_event, set_time)
            bot.send_message(user_id, 'Таймер установлен.')
        else:
            bot.send_message(user_id, 'Вы уже запустили таймер.')

    # срабатывает, если введен неверный формат
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, используйте формат 'YYYY-MM-DD HH:MM:SS'.")
