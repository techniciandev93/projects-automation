from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Team
from .management.commands.bot import bot


@receiver(post_save, sender=Team)
def post_save_team(created, **kwargs):
    instance = kwargs['instance']
    if created:
        teams = Team.objects.filter(project_manager=instance.project_manager)
        for team in teams:
            students = team.students.all()
            print(*students)
            # for student in students:
            #     if student.telegram_id:
            #         print(student.telegram_id)


    # bot.send_message(920533145, 'Hello')
