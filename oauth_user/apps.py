from django.apps import AppConfig


class OauthUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oauth_user'

    # def ready(self):
    #     from django.db.models.signals import post_save
    #
    #     from oauth_user.signals.signals import create_profile_
    #     from django.contrib.auth.models import User
    #     post_save.connect(create_profile_, sender=User)

