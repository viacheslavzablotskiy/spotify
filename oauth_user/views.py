from django.shortcuts import render
from rest_framework import viewsets, permissions, parsers, mixins
from . import serializer
from .models import *
from .my_permissions.permissions import IsAuthor


# def google_login(request):
#     """ Страница входа через Google
#     """
#     return render(request, 'google_login.html')


class UserView(viewsets.ModelViewSet):
    """ Просмотр и редактирование данных пользователя
    """
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.id
        my_models = AuthUser.objects.filter(user_id=user)

        if my_models.exists():
            my_models = my_models[0]
            return my_models

    def get_object(self):
        return self.get_queryset()


class AuthorView(viewsets.ReadOnlyModelViewSet):
    """ Список авторов
    """
    queryset = AuthUser.objects.all().prefetch_related('social_links')
    serializer_class = serializer.AuthorSerializer


class SocialLinkView(viewsets.ModelViewSet):
    """ CRUD ссылок соц. сетей пользователя
    """
    serializer_class = serializer.SocialLinkSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return SocialLink.objects.all()

    def perform_create(self, serializer):
        user = self.request.user.id
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user_id=models_profile.id)
