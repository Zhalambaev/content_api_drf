from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Page
from .serialaizers import PageSerialaizer, PageDetailSerialaizer
from .tasks import counters_for_page


class PagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PageView(ListAPIView):
    queryset = Page.objects.all().order_by('id')
    serializer_class = PageSerialaizer
    pagination_class = PagePagination


class PageDetailView(RetrieveAPIView):
    serializer_class = PageDetailSerialaizer
    lookup_field = 'pk'

    def get_queryset(self):
        return Page.objects.prefetch_related('videos', 'audios').order_by('id')

    def retrieve(self, request, *args, **kwargs):
        page = self.get_object()
        counters_for_page.delay(page.id)
        serializer = self.get_serializer(page, context={"request": request})

        return Response(serializer.data)
