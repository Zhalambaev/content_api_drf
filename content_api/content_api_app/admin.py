from django.contrib import admin

from .models import Page, Video, Audio


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'page', 'video_url', 'subtitles_url', 'counter', 'order_id'
    )
    search_fields = ('title',)
    readonly_fields = ('counter',)


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'page', 'audio_url', 'text', 'counter', 'order_id'
    )
    search_fields = ('title',)
    readonly_fields = ('counter',)


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = (
        'title', 'page', 'video_url', 'subtitles_url', 'counter', 'order_id'
    )
    readonly_fields = ('counter',)


class AudioInline(admin.TabularInline):
    model = Audio
    extra = 1
    fields = (
        'title', 'page', 'audio_url', 'text', 'counter', 'order_id'
    )
    readonly_fields = ('counter',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    inlines = [VideoInline, AudioInline]
