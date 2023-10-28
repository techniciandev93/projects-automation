from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import path
from projects.forms import UploadJsonFileForm, CreateTeamForm
from projects.models import Skill, Student, ProjectManager, Preferences, Team, Week
from projects.services import create_users, create_teams_by_week


class StudentsInlines(admin.TabularInline):
    model = Team.students.through
    raw_id_fields = ('student',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'skill')
    list_filter = ('skill',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    change_list_template = 'admin/team_change_list.html'
    list_filter = ('week', 'project_manager',)
    list_display = ('name', 'project_manager', 'week', 'start_call_time', 'end_call_time',)
    list_editable = ('week', 'start_call_time', 'end_call_time',)
    raw_id_fields = ('students',)
    inlines = [
        StudentsInlines,
    ]

    def get_urls(self):
        urls = super(TeamAdmin, self).get_urls()
        custom_urls = [
            path('create/', self.admin_site.admin_view(self.create_teams), name='team_view'),
            path('load/', self.admin_site.admin_view(self.load_users), name='users_view'),
        ]
        return custom_urls + urls

    def create_teams(self, request):
        if request.method == 'POST':
            form = CreateTeamForm(request.POST)
            if form.is_valid():
                create_teams_by_week(form.cleaned_data['maximum_students'], form.cleaned_data['break_time'])
                return redirect(request.META['HTTP_REFERER'])
            else:
                raise ValidationError(form.errors)
        return HttpResponseNotAllowed(['GET'])

    def load_users(self, request):
        if request.method == 'POST':
            form = UploadJsonFileForm(request.POST, request.FILES)
            if form.is_valid():
                create_users(form.cleaned_data['json_file'])
                return redirect(request.META['HTTP_REFERER'])
            else:
                raise ValidationError(form.errors)
        return HttpResponseNotAllowed(['GET'])


admin.site.register(Skill)
admin.site.register(ProjectManager)
admin.site.register(Preferences)
admin.site.register(Week)
