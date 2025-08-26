from django.urls import path

from .views import PageView, PageDetailView

urlpatterns = [
    path('pages/', PageView.as_view(), name='page_list'),
    path('pages/<int:pk>/', PageDetailView.as_view(), name='page_detail')
]
