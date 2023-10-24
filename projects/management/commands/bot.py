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