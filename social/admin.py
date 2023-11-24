from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .actions import make_activation, make_deactivation


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username', 'phone', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('date_of_birth', 'bio', 'photo', 'job', 'phone')}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'created', 'description']
    ordering = ['created']
    search_fields = ['description']
    inlines = [ImageInline]
    actions = [make_deactivation, make_activation]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'created', 'active']
    list_filter = ['active', 'created', 'updated', ]
    search_fields = ['name', 'body']
    list_editable = ['active']


admin.site.register(Contact)
admin.site.register(Image)
