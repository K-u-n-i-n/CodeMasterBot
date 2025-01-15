from django.contrib import admin

from .models import (
    CustomUser,
    Tag,
    Question
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = (
        'user_id',
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
        'avatar'
    )
    list_editable = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
        'avatar'
    )
    search_fields = (
        'user_id',
        'email',
        'username'
    )
    empty_value_display = 'Не задано'
    list_per_page = 10


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug'
    )
    list_editable = ('slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'description',
        'syntax'
    )
    list_editable = (
        'description',
        'syntax'
    )
    autocomplete_fields = ('tags',)
    search_fields = ('name',)
    list_filter = ('tags',)
