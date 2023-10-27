from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import path
from projects.forms import UploadJsonFileForm
from projects.models import Skill, Student, ProjectManager, Preferences, Team


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
        pass

    def load_users(self, request):
        form = UploadJsonFileForm(request.POST, request.FILES)
        if form.is_valid():
            pass
        else:
            raise ValidationError(form.errors['__all__'])


admin.site.register(Skill)
admin.site.register(ProjectManager)
admin.site.register(Preferences)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ('name', 'skill')
    list_filter = ('skill',)
