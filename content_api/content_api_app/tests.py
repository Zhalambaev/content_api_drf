from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Page, Video, Audio


class PagesListApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # создаём 12 страниц, чтобы проверить пагинацию (page_size=10)
        for i in range(1, 13):
            Page.objects.create(title=f'page_{i}')

    def test_pages_list_pagination_and_detail_url(self):
        url = reverse('page_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        # Проверяем структуру ответа DRF с пагинацией
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)

        # На первой странице должно быть 10 объектов (PagePagination.page_size)
        self.assertEqual(len(data['results']), 10)

        # У каждого элемента есть id, title, detail_url
        item = data['results'][0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('detail_url', item)
        self.assertTrue(item['detail_url'].endswith(f'/api/pages/{item["id"]}/'))

        # Проверяем, что можно изменить размер страницы через ?page_size=5
        resp2 = self.client.get(url + '?page_size=5')
        data2 = resp2.json()
        self.assertEqual(len(data2['results']), 5)


class PageDetailApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Страница
        self.page = Page.objects.create(title='detail_page')
        # Контент: два видео и одно аудио
        self.v1 = Video.objects.create(
            page=self.page, title='Video_1',
            order_id=2,
            video_url='http://video.com/1/',
            subtitles_url='http://video.com/1/subtitles/'
        )
        self.v2 = Video.objects.create(
            page=self.page,
            title='Video_2',
            order_id=1,
            video_url='http://video.com/2/'
        )
        self.a1 = Audio.objects.create(
            page=self.page,
            title='Audio_1',
            order_id=3,
            audio_url='	http://audio.com/1/',
            text='audio_text_1'
        )

    @patch('content_api_app.tasks.counters_for_page.delay')
    def test_page_detail_returns_full_sorted_contents_and_triggers_celery(self, mock_delay):
        url = reverse('page_detail', args=[self.page.id]) 
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        # Базовые поля страницы
        self.assertEqual(data['id'], self.page.id)
        self.assertEqual(data['title'], self.page.title)
        self.assertIn('contents', data)

        contents = data['contents']
        # Должны быть все 3 элемента
        self.assertEqual(len(contents), 3)

        # Проверяем сортировку по order_id
        order_ids = [c['order_id'] for c in contents]
        self.assertEqual(order_ids, [1, 2, 3])

        # Видео содержит video_url
        self.assertIn('video_url', contents[0]['content'])
        # Аудио содержит audio_url
        self.assertIn('audio_url', contents[-1]['content'])

        # Celery-таска вызвана
        mock_delay.assert_called_once_with(self.page.id)
