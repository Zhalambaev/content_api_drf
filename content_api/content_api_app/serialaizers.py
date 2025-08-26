from django.urls import reverse
from rest_framework import serializers

from .models import Page


class PageSerialaizer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'title', 'detail_url']

    def get_detail_url(self, obj):
        request = self.context.get('request')
        url = reverse('page_detail', args=[obj.pk])

        return request.build_absolute_uri(url) if request else url


class PageDetailSerialaizer(serializers.ModelSerializer):
    contents = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'title', 'contents']

    def get_contents(self, page: Page):
        """
        Метод собирает контент для страницы в один список и сортирует его
        по order_id, order_id можно задать в админке,
        тем самым регулировать положение контента.
        """
        contents_list = []
        videos = page.videos.all()
        audios = page.audios.all()
        for video in videos:
            contents_list.append(
                {
                    'order_id': video.order_id,
                    'content': {
                        'id': video.id,
                        'title': video.title,
                        'counter': video.counter,
                        'video_url': video.video_url,
                        'subtitles_url': video.subtitles_url
                    }
                }
            )

        for audio in audios:
            contents_list.append(
                {
                    'order_id': audio.order_id,
                    'content': {
                        'id': audio.id,
                        'title': audio.title,
                        'counter': audio.counter,
                        'audio_url': audio.audio_url,
                        'text': audio.text
                    }
                }
            )

        contents_list.sort(key=lambda x: (x['order_id']))

        return contents_list
