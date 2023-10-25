# Generated by Django 3.2.22 on 2023-10-25 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_skill', models.CharField(max_length=50, verbose_name='Навык студента')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.BigIntegerField(unique=True, verbose_name='ID пользователя в телеграмме')),
                ('name', models.CharField(max_length=100, verbose_name='Имя студента')),
                ('preferred_start_time', models.TimeField(verbose_name='Начальное время созвона')),
                ('preferred_end_time', models.TimeField(verbose_name='Конечное время созвона')),
                ('far_east', models.BooleanField(default=False, verbose_name='Регион Дальний Восток')),
                ('week', models.CharField(choices=[('third', 'Третья'), ('fourth', 'Четвёртая')], max_length=10, verbose_name='Неделя проекта')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='projects.skill', verbose_name='Навык студента')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Имя ПМ')),
                ('work_start_time', models.TimeField(verbose_name='Время начала работы')),
                ('work_end_time', models.TimeField(verbose_name='Время окончания работы')),
                ('students', models.ManyToManyField(blank=True, to='projects.Student', verbose_name='Студенты')),
            ],
        ),
        migrations.CreateModel(
            name='Preferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('not_one_team', models.ManyToManyField(related_name='not_with_students', to='projects.Student', verbose_name='Исключение студентов')),
                ('one_team', models.ManyToManyField(related_name='team_with_students', to='projects.Student', verbose_name='Студенты в одной команде')),
                ('project_menger', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.projectmenger', verbose_name='Проект менеджер')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.student', verbose_name='Студент')),
            ],
        ),
    ]
