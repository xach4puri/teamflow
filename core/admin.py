from django.contrib import admin
from .models import UserProfile, Project, Task


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio_preview']
    search_fields = ['user__username', 'user__email', 'bio']

    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Bio'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'owner__username']
    filter_horizontal = ['members']

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'status', 'priority', 'deadline']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']
