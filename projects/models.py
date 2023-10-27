from django.db import models


class Skill(models.Model):
    student_skill = models.CharField(max_length=50, verbose_name='Навык студента')

    def __str__(self):
        return self.student_skill


class Student(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='ID пользователя в телеграмме')
    name = models.CharField(max_length=100, verbose_name='Имя студента')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name='Навык студента', related_name='students')
    preferred_start_time = models.TimeField(blank=True, null=True, verbose_name='Начальное время созвона')
    preferred_end_time = models.TimeField(blank=True, null=True, verbose_name='Конечное время созвона')
    far_east = models.BooleanField(default=False, verbose_name='Регион Дальний Восток')

    def __str__(self):
        return self.name


class ProjectManager(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name='ID ПМ в телеграмме')
    name = models.CharField(max_length=100, verbose_name='Имя ПМ')
    work_start_time = models.TimeField(verbose_name='Время начала работы')
    work_end_time = models.TimeField(verbose_name='Время окончания работы')
    students = models.ManyToManyField(Student, blank=True, verbose_name='Студенты')

    def __str__(self):
        return self.name


class Team(models.Model):
    choices_week = (
        ('third', 'Третья'),
        ('fourth', 'Четвёртая')
    )
    start_call_time = models.TimeField(verbose_name='Начало созвона')
    end_call_time = models.TimeField(verbose_name='Конец созвона')
    name = models.CharField(max_length=100, verbose_name='Название команды')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.CASCADE, null=True, blank=True,
                                       verbose_name='Проект менеджер')
    students = models.ManyToManyField(Student, related_name='teams', verbose_name='Студенты в команде')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания команды')
    week = models.CharField(choices=choices_week, default='', blank=True, max_length=10, verbose_name='Неделя проекта')

    def __str__(self):
        return self.name


class Preferences(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Студент')
    project_manager = models.ForeignKey(ProjectManager, on_delete=models.SET_NULL, null=True, blank=True,
                                       verbose_name='Проект менеджер')
    one_team = models.ManyToManyField(Student, related_name='team_with_students',
                                      verbose_name='Студенты в одной команде')
    not_one_team = models.ManyToManyField(Student, related_name='not_with_students',
                                          verbose_name='Исключение студентов')

    def __str__(self):
        return self.student.name
