from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("music_job.urls")),
    path("i/", include("oauth_user.urls")),
    path('api/login/', include("rest_framework.urls")),
    # path('social-auth/', include('social_django.urls', namespace="social"))
    path('accounts/', include('allauth.urls')),
]
