from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'wishlist', views.UserWishlistViewSet, basename='wishlist')

app_name = 'users'

urlpatterns = [
    # User registration
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # Authentication endpoints
    path('login/', views.CustomAuthToken.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('', include(router.urls)),
]
