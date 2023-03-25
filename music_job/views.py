import os

from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, parsers, views
from rest_framework.permissions import IsAuthenticated
from .models import *
from music_job import models, serializer
from oauth_user.my_permissions.permissions import IsAuthor
from oauth_user.services.classes import MixedSerializer, Pagination
from oauth_user.services.services import delete_old_file


class GenreView(generics.ListAPIView):
    """ Список жанров
    """
    queryset = models.Genre.objects.all()
    serializer_class = serializer.GenreSerializer


class LicenseView(viewsets.ModelViewSet):
    """ CRUD лицензий автора
    """
    queryset = License.objects.all()
    serializer_class = serializer.LicenseSerializer
    permission_classes = [IsAuthor, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.id
        return License.objects.filter(user_id=user)

    def perform_create(self, serializer):
        user = self.request.user.id
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user_id=models_profile.id)


class AlbumView(viewsets.ModelViewSet):
    """ CRUD альбомов автора
    """
    parser_classes = (parsers.MultiPartParser,)
    serializer_class = serializer.AlbumSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        user = self.request.user.id

        return models.Album.objects.filter(user_id=user)

    def perform_create(self, serializer):
        user = self.request.user.id
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user_id=models_profile.id)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class PublicAlbumView(generics.ListAPIView):
    """ Список публичных альбомов автора
    """
    serializer_class = serializer.AlbumSerializer

    def get_queryset(self):
        return models.Album.objects.filter(user__id=self.kwargs.get('pk'), private=False)


class PlayListView(MixedSerializer, viewsets.ModelViewSet):
    """ CRUD плейлистов пользователя
    """
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreatePlayListSerializer
    serializer_classes_by_action = {
        'list': serializer.PlayListSerializer
    }

    def get_queryset(self):
        return models.PlayList.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        user = self.request.user.id
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user_id=models_profile.id)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        instance.delete()


class TrackView(MixedSerializer, viewsets.ModelViewSet):
    """ CRUD треков
    """
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = [IsAuthor]
    serializer_class = serializer.CreateAuthorTrackSerializer
    serializer_classes_by_action = {
        'list': serializer.AuthorTrackSerializer
    }

    def get_queryset(self):
        return models.Track.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        user = self.request.user.id
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user=models_profile)

    def perform_destroy(self, instance):
        delete_old_file(instance.cover.path)
        delete_old_file(instance.file.path)
        instance.delete()


class TrackListView(generics.ListAPIView):
    """ Список всех треков
    """
    queryset = models.Track.objects.filter(album__private=False, private=False)
    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'user__display_name', 'album__name', 'genre__name']


class AuthorTrackListView(generics.ListAPIView):
    """ Список всех треков автора
    """
    serializer_class = serializer.AuthorTrackSerializer
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'album__name', 'genre__name']

    def get_queryset(self):
        return models.Track.objects.filter(
            user__id=self.kwargs.get('pk'), album__private=False, private=False
        )


class CommentAuthorView(viewsets.ModelViewSet):
    """ CRUD комментариев автора
    """
    serializer_class = serializer.CommentAuthorSerializer
    permission_classes = [IsAuthor]

    def get_queryset(self):
        return models.Comment.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        user = self.request.user
        models_profile = AuthUser.objects.filter(user_id=user).first()
        serializer.save(user_id=models_profile.id)


class CommentView(viewsets.ModelViewSet):
    """ Комментарии к треку
    """
    serializer_class = serializer.CommentSerializer

    def get_queryset(self):
        return models.Comment.objects.filter(track_id=self.kwargs.get('pk'))


class StreamingFileView(views.APIView):
    """ Воспроизведение трека
    """

    def set_play(self, track):
        track.plays_count += 1
        track.save()

    def get(self, request, pk):
        track = get_object_or_404(models.Track, id=pk)
        if os.path.exists(track.file.path):
            self.set_play(track)
            return FileResponse(open(track.file.path, "rb"), filename=track.file.name)
        else:
            return Http404

    # def set_play(self):
    #     self.track.plays_count += 1
    #     self.track.save()
    #
    # def get(self, request, pk):
    #     self.track = get_object_or_404(models.Track, id=pk, private=False)
    #     if os.path.exists(self.track.file.path):
    #         self.set_play()
    #         response = HttpResponse('', content_type="audio/mpeg", status=206)
    #         response['X-Accel-Redirect'] = f"/mp3/{self.track.file.name}"
    #         return response
    #     else:
    #         return Http404


class DownloadTrackView(views.APIView):
    """ Скачивание трека
    """

    def set_download(self):
        self.track.download += 1
        self.track.save()

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk)
        if os.path.exists(self.track.file.path):
            self.set_download()
            return FileResponse(open(self.track.file.path, "rb"), filename= self.track.file.name, as_attachment=True)
        else:
            return Http404

    # def set_download(self):
    #     self.track.download += 1
    #     self.track.save()
    #
    # def get(self, request, pk):
    #     self.track = get_object_or_404(models.Track, id=pk, private=False)
    #     if os.path.exists(self.track.file.path):
    #         self.set_download()
    #         response = HttpResponse('', content_type="audio/mpeg", status=206)
    #         response["Content-Disposition"] = f"attachment; filename={self.track.file.name}"
    #         response['X-Accel-Redirect'] = f"/media/{self.track.file.name}"
    #         return response
    #     else:
    #         return Http404


class StreamingFileAuthorView(views.APIView):
    """ Воспроизведение трека автора
    """
    permission_classes = [IsAuthor]

    def get(self, request, pk):
        self.track = get_object_or_404(models.Track, id=pk, user=request.user)
        if os.path.exists(self.track.file.path):
            response = HttpResponse('', content_type="audio/mpeg", status=206)
            response['X-Accel-Redirect'] = f"/mp3/{self.track.file.name}"
            return response
        else:
            return
