from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import path

from projects.forms import UploadJsonFileForm
from projects.models import Skill, Student, ProjectManager, Preferences, Team
from projects.services import create_users, create_teams


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    change_list_template = "admin/team_change_list.html"

    def get_urls(self):
        urls = super(TeamAdmin, self).get_urls()
        custom_urls = [
            path('create/', self.admin_site.admin_view(self.create_teams), name='team_view'),
            path('load/', self.admin_site.admin_view(self.load_users), name='users_view'),
        ]
        return custom_urls + urls

    def create_teams(self, request):
        if request.method == 'POST':
            create_teams()
            return redirect(request.META['HTTP_REFERER'])
        return HttpResponseNotAllowed(['GET'])


    def load_users(self, request):
        if request.method == 'POST':
            form = UploadJsonFileForm(request.POST, request.FILES)
            if form.is_valid():
                create_users(form.cleaned_data['json_file'])
                return redirect(request.META['HTTP_REFERER'])
            else:
                raise ValidationError(form.errors['__all__'])
        return HttpResponseNotAllowed(['GET'])


admin.site.register(Skill)
admin.site.register(ProjectManager)
admin.site.register(Preferences)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'skill')
    list_filter = ('skill',)
