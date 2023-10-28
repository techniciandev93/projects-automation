import json
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projects_automation.settings')
import django

django.setup()
from projects.models import ProjectManager, Team, Student, Skill, Week

from datetime import datetime, timedelta


def create_users(path="users.json"):
    with open(path, 'r') as file:
        users = json.load(file, )

    project_managers = users.get('project_managers')
    students = users.get('students')

    Skill.objects.all().delete()
    Student.objects.all().delete()
    ProjectManager.objects.all().delete()

    for student in students:
        skill_instance, created = Skill.objects.get_or_create(student_skill=student['skill'])
        Student.objects.create(
            telegram_id=student['telegram_id'],
            name=student['name'],
            skill=skill_instance,
            # preferred_start_time=student['work_start'],
            # preferred_end_time=student['work_end'],
        )

    for project_manager in project_managers:
        ProjectManager.objects.create(
            telegram_id=str(project_manager['telegram_id']),
            name=project_manager['name'],
            # work_start_time=project_manager['work_start'],
            # work_end_time=project_manager['work_end']
        )


def create_teams_by_week(maximum_students=3, break_time=0):
    Team.objects.all().delete()
    weeks = Week.objects.all()
    for week in weeks.iterator():
        create_teams(week, maximum_students, break_time)


def create_teams(week, maximum_students, break_time):
    project_managers = ProjectManager.objects.all()
    students = Student.objects.all()

    groups_count_by_skill = {}
    for manager in project_managers.iterator():
        time_range_students = students.filter(
            teams__isnull=True,
            preferred_start_time__gte=manager.work_start_time,
            preferred_end_time__lte=manager.work_end_time
        )

        time_format = "%H:%M:%S"
        manager_work_start = datetime.strptime(str(manager.work_start_time), time_format)
        manager_work_end = datetime.strptime(str(manager.work_end_time), time_format)

        student_by_skill = {}
        for student in time_range_students.iterator():
            skill_group = student_by_skill.setdefault(student.skill, [])
            skill_group.append(student)
            if len(skill_group) < maximum_students:
                continue

            group_count = groups_count_by_skill.setdefault(student.skill.student_skill, 0)
            group_count += 1
            groups_count_by_skill[student.skill.student_skill] = group_count
            group_name = f"{student.skill.student_skill} {group_count}"

            work_end = manager_work_start + timedelta(minutes=20)
            if work_end > manager_work_end:
                break

            created_team = Team.objects.create(  # todo bulk create
                name=group_name,
                project_manager=manager,
                start_call_time=manager_work_start.strftime(time_format),
                end_call_time=work_end.strftime(time_format),
                week=week
            )
            created_team.students.set(skill_group)

            print(f"New group {group_name}: {skill_group}")
            manager_work_start = work_end + timedelta(minutes=break_time)
            skill_group.clear()


if __name__ == '__main__':
    create_users('users.json')
    # create_teams()