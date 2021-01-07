from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from sample_app.models import Country

# Create your models here.


class UserSampleManager(UserManager):
    # Subclaseamos para que el name del usuario lo saque de la primera parte del email
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario tiene que tener el EMAIL informado')

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if not username:
            username, dummy = self.normalize_email(email).split('@')

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario tiene que tener el EMAIL informado')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not username:
            username, dummy = self.normalize_email(email).split('@')

        return self._create_user(username, email, password, **extra_fields)


class UserSample(AbstractUser):
    email = models.EmailField(
        max_length=255,
        unique=True,
    )
    countries = models.ManyToManyField(Country, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserSampleManager()

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.normalize_username(self.email)

        return super(UserSample, self).save()

    class Meta:
        db_table = 'user_sample'
        verbose_name_plural = 'Users Sample'


@receiver(post_save, sender=get_user_model())
def handler_post_save_user(sender, instance=None, created=False, **kwargs):
    """

    Args:
        sender (UserSample):
        instance (UserSample):
        created (bool):
        **kwargs:

    Returns:

    """
    token_objs = Token.objects
    if instance and instance.has_usable_password() and not token_objs.filter(user=instance).exists():
        token_objs.create(user=instance)
