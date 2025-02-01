from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from rest_framework.authtoken.models import Token
        from .models import CustomUser

        @receiver(post_save, sender=CustomUser)
        def create_auth_token(sender, instance=None, created=False, **kwargs):
            if created:
                Token.objects.create(user=instance)
