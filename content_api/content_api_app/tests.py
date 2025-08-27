from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Page, Video, Audio


class PagesListApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        for i in range(1, 13):
            Page.objects.create(title=f'page_{i}')

    def test_status_ok(self):
        resp = self.client.get(reverse('page_list'))
        self.assertEqual(resp.status_code, 200)

    def test_response_has_pagination_keys(self):
        data = self.client.get(reverse('page_list')).json()
        for key in ('count', 'next', 'previous', 'results'):
            self.assertIn(key, data)

    def test_default_page_size_is_10(self):
        data = self.client.get(reverse('page_list')).json()
        self.assertEqual(len(data['results']), 10)

    def test_detail_url_present_and_correct(self):
        data = self.client.get(reverse('page_list')).json()
        item = data['results'][0]
        self.assertIn('id', item)
        self.assertIn('title', item)
        self.assertIn('detail_url', item)
        self.assertTrue(item['detail_url'].endswith(f'/api/pages/{item["id"]}/'))

    def test_page_size_query_param_overrides_default(self):
        data = self.client.get(reverse('page_list') + '?page_size=5').json()
        self.assertEqual(len(data['results']), 5)


class PageDetailApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.page = Page.objects.create(title='detail_page')

        Video.objects.create(
            page=self.page,
            title='Video_1',
            order_id=2,
            video_url='http://video.com/1/',
            subtitles_url='http://video.com/1/subtitles/'
        )
        Video.objects.create(
            page=self.page,
            title='Video_2',
            order_id=1,
            video_url='http://video.com/2/'
        )
        Audio.objects.create(
            page=self.page,
            title='Audio_1',
            order_id=3,
            audio_url='http://audio.com/1/',
            text='audio_text_1'
        )

    def _get_detail(self):
        url = reverse('page_detail', args=[self.page.id])
        return self.client.get(url).json()

    @patch('content_api_app.views.counters_for_page.delay')
    def test_status_ok(self, _mock_delay):
        resp = self.client.get(reverse('page_detail', args=[self.page.id]))
        self.assertEqual(resp.status_code, 200)

    @patch('content_api_app.views.counters_for_page.delay')
    def test_base_fields_present(self, _mock_delay):
        data = self._get_detail()
        self.assertEqual(data['id'], self.page.id)
        self.assertEqual(data['title'], self.page.title)
        self.assertIn('contents', data)

    @patch('content_api_app.views.counters_for_page.delay')
    def test_contents_length_is_3(self, _mock_delay):
        data = self._get_detail()
        self.assertEqual(len(data['contents']), 3)

    @patch('content_api_app.views.counters_for_page.delay')
    def test_contents_sorted_by_order_id(self, _mock_delay):
        data = self._get_detail()
        order_ids = [c['order_id'] for c in data['contents']]
        self.assertEqual(order_ids, [1, 2, 3])

    @patch('content_api_app.views.counters_for_page.delay')
    def test_first_item_has_video_specific_fields(self, _mock_delay):
        data = self._get_detail()
        first = data['contents'][0]['content']
        self.assertIn('video_url', first)

    @patch('content_api_app.views.counters_for_page.delay')
    def test_last_item_has_audio_specific_fields(self, _mock_delay):
        data = self._get_detail()
        last = data['contents'][-1]['content']
        self.assertIn('audio_url', last)
        self.assertIn('text', last)

    @patch('content_api_app.views.counters_for_page.delay')
    def test_celery_task_is_triggered(self, mock_delay):
        self.client.get(reverse('page_detail', args=[self.page.id]))
        mock_delay.assert_called_once_with(self.page.id)
