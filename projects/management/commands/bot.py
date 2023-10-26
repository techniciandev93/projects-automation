from django.core.management import BaseCommand
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from projects_automation.settings import TELEGRAM_TOKEN
from projects.models import Student, ProjectMenger
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage


state_storage = StateMemoryStorage
bot = TeleBot(TELEGRAM_TOKEN, threaded=False)


class BotStates(StatesGroup):
    pm_set_time = State()


@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_message = f'Привет, {message.from_user.username}!'
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    kb_main_menu = get_main_menu_kb()
    bot.send_message(message.chat.id, text=welcome_message, reply_markup=kb_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Назад в основное меню 🔙')
def back_to_main_menu(message):
    main_menu_message = 'Вы вернулись в основное меню'
    kb_main_menu = get_main_menu_kb()
    bot.send_message(message.chat.id, main_menu_message, reply_markup=kb_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Ваши команды 💻')
def handler_commands(message):
    try:
        user = Student.objects.get(telegram_id=message.from_user.id)
        status = 'Student'
    except Student.DoesNotExist:
        user = ProjectMenger.objects.get(telegram_id=message.from_user.id)
        status = 'PM'
    except ProjectMenger.DoesNotExist:
        bot.send_message(message.chat.id, 'Вы не являетесь зарегистрированным пользователем')
        return
    kb_call_time = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    if status == 'Student' and user.far_east:
        call_time_btn = (
            KeyboardButton(text='7:00 - 9:00'),
            KeyboardButton(text='9:00 - 12:00'),
        )

    else:
        call_time_btn = (
            KeyboardButton(text='14:00 - 17:00'),
            KeyboardButton(text='17:00 - 20:00'),
            KeyboardButton(text='20:00 - 23:00'),
        )
    kb_call_time.add(*call_time_btn)
    message_time = f'Пожалуйста, выберите желаемый диапазон времени для занятий'

    if status == 'PM':
        kb_work_time = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        work_time_btn = [
            KeyboardButton(text='Посмотреть рассписание созвонов')
        ]
        kb_work_time.add(*work_time_btn)
        bot.send_message(message.chat.id, message_time, reply_markup=kb_work_time)

    elif status == 'student':
        bot.send_message(message.chat.id, message_time, reply_markup=kb_call_time)


@bot.message_handler(func=lambda message: message.text == 'Ваш профиль ☑️')
def handler_get_status(message):
    try:
        user = Student.objects.get(telegram_id=message.from_user.id)
        status = 'Student'
    except Student.DoesNotExist:
        user = ProjectMenger.objects.get(telegram_id=message.from_user.id)
        status = 'PM'
    except ProjectMenger.DoesNotExist:
        bot.send_message(message.chat.id, 'Вы не являетесь зарегистрированным пользователем')
        return
    status_message = f'Ваш статус - {status}'
    if status == 'Student':
        far_eastern = user.far_east
        if far_eastern:
            far_eastern_btn = KeyboardButton(text='Я купил себе немца 🚗')
        else:
            far_eastern_btn = KeyboardButton(text='Я езжу на праворуком авто 🚗')
        kb_status = ReplyKeyboardMarkup(resize_keyboard=True)
        kb_status_button = [
            far_eastern_btn,
            KeyboardButton(text='Назад в основное меню 🔙')
        ]
        kb_status.add(*kb_status_button)
    else:
        kb_status = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb_status_button = [
            KeyboardButton(text='Назад в основное меню 🔙')
        ]
        kb_status.add(*kb_status_button)
    bot.send_message(message.chat.id, text=status_message, reply_markup=kb_status)


@bot.message_handler(func=lambda message: message.text == 'Я езжу на праворуком авто 🚗')
def handler_far_eastern(message):
    try:
        user = Student.objects.get(telegram_id=message.from_user.id)
        status = 'Student'
    except Student.DoesNotExist:
        user = ProjectMenger.objects.get(telegram_id=message.from_user.id)
        status = 'PM'
    except ProjectMenger.DoesNotExist:
        bot.send_message(message.chat.id, 'Вы не являетесь зарегистрированным пользователем')
        return
    if status == 'Student':
        user.far_east = True
        user.save()
        kb_main_menu = get_main_menu_kb()
        bot.send_message(message.chat.id, 'Ваш промежуток занятий обновлен', reply_markup=kb_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Я купил себе немца 🚗')
def handler_far_eastern(message):
    try:
        user = Student.objects.get(telegram_id=message.from_user.id)
        status = 'Student'
    except Student.DoesNotExist:
        user = ProjectMenger.objects.get(telegram_id=message.from_user.id)
        status = 'PM'
    except ProjectMenger.DoesNotExist:
        bot.send_message(message.chat.id, 'Вы не являетесь зарегистрированным пользователем')
        return
    if status == 'Student':
        user.far_east = False
        user.save()
        kb_main_menu = get_main_menu_kb()
        bot.send_message(message.chat.id, 'Ваш промежуток занятий обновлен', reply_markup=kb_main_menu)


def get_main_menu_kb():
    kb_main_menu = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    kb_main_menu_btn = (
        KeyboardButton(text='Ваш профиль ☑️'),
        KeyboardButton(text='Ваши команды 💻'),
    )
    kb_main_menu.add(kb_main_menu_btn)
    return kb_main_menu


def main():
    bot.polling(skip_pending=True)


class Command(BaseCommand):
    help = 'Команда для запуска Telegram-бота.'

    def handle(self, *args, **options):
        while True:
            try:
                main()
            except Exception as error:
                continue


if __name__ == '__main__':
    main()