from celery import shared_task
from django.db.models import F

from .models import Audio, Video


@shared_task(
        bind=True,
        autoretry_for=(Exception,),
        retry_backoff=True,
        max_retries=5
)
def counters_for_page(self, page_id: int) -> dict:
    """
    Атомарно увеличиваем счётчик просмотров
    у контента привязанного к странице.
    """
    updated_videos = Video.objects.filter(page_id=page_id).update(
        counter=F('counter') + 1
    )
    updated_audios = Audio.objects.filter(page_id=page_id).update(
        counter=F('counter') + 1
    )

    return {'updated_videos': updated_videos, 'updated_audios': updated_audios}
