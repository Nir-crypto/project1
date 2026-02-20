from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login', LoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('accounts.urls')),
    path('api/', include('learning.urls')),
    path('api/', include('recommendations.urls')),
    path('api/', include('roadmaps.urls')),
]
