import json
import os
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projects_automation.settings')
import django

django.setup()
from projects.models import ProjectMenger, Team, Student, Skill


def split_into_teams():
    teams = defaultdict(list)
    project_managers = ProjectMenger.objects.all()
    for manager in project_managers:
        remaining_students = []
        skill_students = defaultdict(list)
        students = manager.students.all()

        # Получаем студентов, которые входят во временной диапазон ПМ
        time_range_students = students.filter(preferred_start_time__gte=manager.work_start_time,
                                              preferred_end_time__lte=manager.work_end_time)
        print(time_range_students)
        # Группируем студентов по скиллам
        for student in time_range_students.iterator():
            skill = student.skill.student_skill
            skill_students[skill].append(student)

        # Разбиваем студентов на команды по 3 человека
        for skill, students in skill_students.items():
            while len(students) >= 3:
                teams[manager].append(students[:3])
                students = students[3:]
            # Если остаются 2 студента, добавьте их в отдельную команду
            if len(students) == 2:
                teams[manager].append(students)
            remaining_students.extend(students)
        print(remaining_students)
    return teams


def create_teams():
    teams = split_into_teams()
    for manager in teams:
        for number, team in enumerate(teams[manager]):
            team_object = Team.objects.create(name=f'team-{number}', project_menger=manager)
            team_object.students.set(team)


def create_users(path):
    with open(path, 'r') as file:
        users = json.load(file)

    project_managers = users.get('project_managers')
    students = users.get('students')
    students_for_managers = defaultdict(list)

    for student in students:
        skill_instance, created = Skill.objects.get_or_create(student_skill=student['skill'])
        object_student = Student.objects.create(
            telegram_id=student['telegram_id'],
            name=student['name'],
            skill=skill_instance)
        students_for_managers[student['pm']].append(object_student)

    for project_manager in project_managers:
        object_manager = ProjectMenger.objects.create(
            telegram_id=project_manager['telegram_id'],
            name=project_manager['name'],
            work_start_time=project_manager['work_start'],
            work_end_time=project_manager['work_end'])
        object_manager.students.set(students_for_managers[project_manager['telegram_id']])


if __name__ == '__main__':
    #create_users('users.json')
    create_teams()
