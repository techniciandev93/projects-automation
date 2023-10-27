# Generated by Django 3.2.22 on 2023-10-27 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='preferences',
            old_name='project_menger',
            new_name='project_manager',
        ),
        migrations.RenameField(
            model_name='team',
            old_name='project_menger',
            new_name='project_manager',
        ),
        migrations.RemoveField(
            model_name='student',
            name='week',
        ),
        migrations.AddField(
            model_name='team',
            name='week',
            field=models.CharField(blank=True, choices=[('third', 'Третья'), ('fourth', 'Четвёртая')], default='', max_length=10, verbose_name='Неделя проекта'),
        ),
    ]
