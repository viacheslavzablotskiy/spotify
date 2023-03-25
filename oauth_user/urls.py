from django.urls import path
from django.views.generic import TemplateView

from . import views
from oauth_user import views
from .oauth import auth_views

urlpatterns = [
    path('me/', views.UserView.as_view({'get': 'retrieve', 'put': 'update'})),

    path('author/', views.AuthorView.as_view({'get': 'list'})),
    path('author/<int:pk>/', views.AuthorView.as_view({'get': 'retrieve'})),

    path('social/', views.SocialLinkView.as_view({'get': 'list', 'post': 'create'})),
    path('social/<int:pk>/', views.SocialLinkView.as_view({'put': 'update', 'delete': 'destroy'})),

    # path('google/', auth_views.google_auth),
    # path('spotify-callback/', auth_views.spotify_auth),
    path('hello', TemplateView.as_view(template_name="index.html")),
    # path('spotify-login/', auth_views.spotify_login),
    path('template', auth_views.google_login),
    path('my_login', auth_views.login_my_account)
]