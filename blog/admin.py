from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Post, ReadPost, SavedPost, SiteSettings, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'date_posted']
    list_filter = ['status', 'category', 'tags']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']


@admin.register(ReadPost)
class ReadPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__username', 'post__title']


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'post__title']


@admin.register(SiteSettings)
class SiteSettingsAdmin(SummernoteModelAdmin):
    summernote_fields = ('about_content',)
    fieldsets = (
        ('Branding', {
            'fields': ('site_name', 'tab_title'),
        }),
        ('Homepage Hero', {
            'description': 'Shown to guest (logged-out) visitors on the homepage.',
            'fields': ('tagline', 'hero_subtext'),
        }),
        ('About Page', {
            'fields': ('about_title', 'about_content'),
        }),
        ('Display', {
            'fields': ('posts_per_page',),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
