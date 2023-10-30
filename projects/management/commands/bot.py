from django.core.management import BaseCommand
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from projects_automation.settings import TELEGRAM_TOKEN
from projects.models import Student, ProjectManager, Team
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
import json


state_storage = StateMemoryStorage()
bot = TeleBot(TELEGRAM_TOKEN, threaded=False, state_storage=state_storage)


class BotStates(StatesGroup):
    student_set_time = State()


@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_message = f'Привет, {message.from_user.username}!'
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    kb_main_menu = get_main_menu_kb()
    bot.send_message(message.chat.id, text=welcome_message, reply_markup=kb_main_menu)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Назад в основное меню 🔙')
def back_to_main_menu(message):
    main_menu_message = 'Вы вернулись в основное меню'
    kb_main_menu = get_main_menu_kb()
    bot.send_message(message.chat.id, main_menu_message, reply_markup=kb_main_menu)
    bot.delete_state(message.from_user.id, message.chat.id)


def get_user(message):
    try:
        user = Student.objects.get(username=message.from_user.username)
        user.telegram_id = message.from_user.id
        user.chat_id = message.chat.id
        user.save()
    except Student.DoesNotExist:
        try:
            user = ProjectManager.objects.get(username=message.from_user.username)
            user.telegram_id = message.from_user.id
            user.chat_id = message.chat.id
            user.save()
        except ProjectManager.DoesNotExist:
            bot.send_message(message.chat.id, 'Вы не являетесь зарегистрированным пользователем')
            return
    return user


@bot.message_handler(func=lambda message: message.text == 'Отменить запись 🚫')
def handler_remove_entry(message):
    user = get_user(message)
    user.preferred_start_time = None
    user.preferred_end_time = None
    user.save()
    kb_main_menu = get_main_menu_kb()
    message_remove = 'Вы отменили свою запись'
    bot.send_message(message.chat.id, message_remove, reply_markup=kb_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Ваши команды 💻')
def handler_commands(message):
    user = get_user(message)
    kb_call_time = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    if isinstance(user, Student) and user.preferred_start_time:
        call_time_btn = (
            KeyboardButton(text='Отменить запись 🚫'),
            KeyboardButton(text='Назад в основное меню 🔙')
        )
        message_time = f'У вас уже имеется запись, вы можете отменить ее'
    elif isinstance(user, Student) and user.far_east:
        call_time_btn = (
            KeyboardButton(text='7:00 - 9:00'),
            KeyboardButton(text='9:00 - 12:00'),
            KeyboardButton(text='Назад в основное меню 🔙')
        )
        message_time = f'Пожалуйста, выберите желаемый диапазон времени для занятий'

    else:
        call_time_btn = (
            KeyboardButton(text='14:00 - 17:00'),
            KeyboardButton(text='17:00 - 20:00'),
            KeyboardButton(text='20:00 - 23:00'),
            KeyboardButton(text='Назад в основное меню 🔙')
        )
        message_time = f'Пожалуйста, выберите желаемый диапазон времени для занятий'
    kb_call_time.add(*call_time_btn)

    if isinstance(user, ProjectManager):
        kb_work_time = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        work_time_btn = [
            KeyboardButton(text='Посмотреть рассписание созвонов'),
            KeyboardButton(text='Назад в основное меню 🔙')
        ]
        kb_work_time.add(*work_time_btn)
        message_time = 'Доступные команды'
        bot.send_message(message.chat.id, message_time, reply_markup=kb_work_time)

    elif isinstance(user, Student):
        bot.set_state(message.from_user.id, BotStates.student_set_time, message.chat.id)
        bot.send_message(message.chat.id, message_time, reply_markup=kb_call_time)


@bot.message_handler(state=BotStates.student_set_time)
def set_student_time(message):
    kb_main_menu = get_main_menu_kb()
    user = get_user(message)
    bot.send_message(message.chat.id, text=f'Вы назначили время: {message.text}', reply_markup=kb_main_menu)
    start_time, end_time = message.text.split(' - ')
    user.preferred_start_time = start_time
    user.preferred_end_time = end_time
    user.save()
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Посмотреть рассписание созвонов')
def get_call_time(message):
    user = get_user(message)
    try:
        team = Team.objects.filter(project_manager=user)
        if team.exists():
            page = 1
            count = team.count()
            students_in_team = team[page - 1].students.all()
            student_names = ", ".join(student.name for student in students_in_team)
            skill = students_in_team[0].skill
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
            markup.add(InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->', callback_data=f'{{"method": "pagination",'
                                                                               f'"NumberPage": {page + 1}, '
                                                                               f'"CountPage": {count}}}'
                                            ))
            bot.send_message(message.from_user.id, f'Группа: <b>{team[page - 1].name}</b>\n\n'
                                                   f'Время старта созвона:\n{team[page - 1].start_call_time}\n\n'
                                                   f'Время окончания созвона:\n{team[page - 1].end_call_time}\n\n'
                                                   f'Рабочая неделя:\n{team[page - 1].week}\n\n'
                                                   f'Студенты:\n{student_names}\n\n'
                                                   f'Уровень группы:\n{skill}',

                             reply_markup=markup, parse_mode='HTML')
    except Team.DoesNotExist:
        bot.send_message(message.chat.id, text='Команды не сформированы')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user = ProjectManager.objects.get(username=call.from_user.username)
    team = Team.objects.filter(project_manager=user)
    req = call.data.split('_')
    if req[0] == 'unseen':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    elif 'pagination' in req[0]:
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']
        students_in_team = team[page - 1].students.all()
        student_names = ", ".join(student.name for student in students_in_team)
        skill = students_in_team[0].skill
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        if page == 1:
            markup.add(
                InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                InlineKeyboardButton(text=f'Вперёд --->',
                                     callback_data=f'{{"method":"pagination","NumberPage":{page + 1},'
                                                   f'"CountPage":{count}}}')
            )
        elif page == count:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data=f'{{"method":"pagination","NumberPage":{page - 1},'
                                                          f'"CountPage": {count}}}'
                                            ),

                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '))
        else:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data=f'{{"method":"pagination","NumberPage":{page - 1},'
                                                          f'"CountPage": {count}}}'),
                       InlineKeyboardButton(text=f'{page}/{count}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data=f'{{"method":"pagination","NumberPage":{page + 1},'
                                                          f'"CountPage":{count}}}'))

        bot.edit_message_text(f'Группа: <b>{team[page - 1].name}</b>\n\n'
                              f'Время старта созвона:\n{team[page - 1].start_call_time}\n\n'
                              f'Время окончания созвона:\n{team[page - 1].end_call_time}\n\n'
                              f'Рабочая неделя:\n{team[page - 1].week}\n\n'
                              f'Студенты:\n{student_names}\n\n'
                              f'Уровень группы:\n{skill}',

                              reply_markup=markup,
                              parse_mode='HTML',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Ваш профиль ☑️')
def handler_get_status(message):
    user = get_user(message)
    if isinstance(user, Student):
        status = 'Студент'
    elif isinstance(user, ProjectManager):
        status = 'ПМ'
    else:
        return
    status_message = f'Ваш статус - {status}'
    if isinstance(user, Student):
        far_eastern = user.far_east
        if far_eastern:
            far_eastern_btn = KeyboardButton(text='Изменить часовой пояс на Мск')
        else:
            far_eastern_btn = KeyboardButton(text='Изменить часовой пояс на  Дальний Восток')
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


@bot.message_handler(func=lambda message: message.text == 'Изменить часовой пояс на  Дальний Восток')
def handler_far_eastern(message):
    user = get_user(message)
    if isinstance(user, Student):
        user.far_east = True
        user.save()
        kb_main_menu = get_main_menu_kb()
        bot.send_message(message.chat.id, 'Ваш промежуток занятий обновлен', reply_markup=kb_main_menu)


@bot.message_handler(func=lambda message: message.text == 'Изменить часовой пояс на Мск')
def handler_far_eastern(message):
    user = get_user(message)
    if isinstance(user, Student):
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
    kb_main_menu.add(*kb_main_menu_btn)
    return kb_main_menu


def main():
    bot.add_custom_filter(custom_filters.StateFilter(bot))
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
