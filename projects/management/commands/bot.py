from django.core.management import BaseCommand
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from projects_automation.settings import TELEGRAM_TOKEN
from projects.models import User

bot = TeleBot(TELEGRAM_TOKEN, threaded=False)


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
    user = User.objects.get(tg_id=message.from_user.id)
    user_status = user.status

    if user_status == 'admin':
        kb_admin_main = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        kb_admin_main_btn = (
            KeyboardButton(text='Загрузить ПМ-ов'),
            KeyboardButton(text='Загрузить учеников'),
        )
        kb_admin_main.add(*kb_admin_main_btn)
        welcome_message = f'Привет, {message.from_user.username}!\n' \
                          f'Пожалуйста загрузите список ПМ-ов и учеников'
        bot.send_message(message.chat.id, welcome_message, reply_markup=kb_admin_main)

    elif user_status == 'PM':
        welcome_message = f'Привет, {message.from_user.username}!\n' \
                          f'Пожалуйста, введите желаемое время в период с 7:00 - 12:00, либо 14:00 - 23:00.\n' \
                          f'Время должно быть кратно 30 минутам, иначе оно будет округлено в меньшую сторону'
        bot.send_message(message.chat.id, welcome_message)

    elif user_status == 'student':
        welcome_message = f'Привет, {message.from_user.username}!\n' \
                          f'Пожалуйста, введите желаемое время в период с 7:00 - 12:00, либо 14:00 - 23:00.\n' \
                          f'Время должно быть кратно 30 минутам'
        bot.send_message(message.chat.id, welcome_message)


@bot.message_handler(func=lambda message: message.text == 'Ваш профиль ☑️')
def handler_get_status(message):
    user = User.objects.get(tg_id=message.from_user.id)
    user_status = user.status
    status_message = f'Ваш статус {user_status}'
    far_eastern = User.objects.get(tg_id=message.from_user.id)
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
    bot.send_message(message.chat.id, text=status_message)


@bot.message_handler(func=lambda message: message.text == 'Я езжу на праворуком авто 🚗')
def handler_far_eastern(message):
    pass


@bot.message_handler(func=lambda message: message.text == 'Я купил себе немца 🚗')
def handler_far_eastern(message):
    pass


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