from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'authors', views.AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('books/search/', views.BookSearchView.as_view(), name='book-search'),
]
