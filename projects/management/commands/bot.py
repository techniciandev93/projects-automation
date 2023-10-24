from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Команда для запуска Telegram-бота.'

    def handle(self, *args, **kwargs):
        pass
