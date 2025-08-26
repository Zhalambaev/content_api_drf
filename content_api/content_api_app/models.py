from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=250, db_index=True)

    def __str__(self):
        return self.title


class BaseContent(models.Model):
    title = models.CharField(max_length=250, db_index=True)
    counter = models.PositiveBigIntegerField(default=0)
    order_id = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True


class Video(BaseContent):
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name='videos'
    )
    video_url = models.URLField()
    subtitles_url = models.URLField(blank=True)

    class Meta:
        ordering = ('order_id',)

    def __str__(self):
        return f'Video: {self.title}'


class Audio(BaseContent):
    """В ТЗ ссылки хранения нет. Но хранить где-то нужно.
    При реальной работе уточнил бы этот момент.
    В тестовом решил добавить audio_url.
    """
    page = models.ForeignKey(
        Page, on_delete=models.CASCADE, related_name='audios'
    )
    audio_url = models.URLField()
    text = models.TextField(blank=True)

    class Meta:
        ordering = ('order_id',)

    def __str__(self):
        return f'Audio: {self.title}'
