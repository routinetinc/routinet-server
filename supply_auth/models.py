from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created and instance is not None:
        Token.objects.create(user=instance)


class UserManager(BaseUserManager):
    def _create_user(self, email, username, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user.full_clean()

        Token.objects.create(user=user)

        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields['is_active'] = True
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self._create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    username          = models.CharField(max_length=150)
    email             = models.EmailField(unique=True)
    age               = models.IntegerField(null=True,blank=True)
    job               = models.CharField(null=True,max_length=150)
    profile_media_id  = models.IntegerField(null=True)
    self_introduction = models.CharField(null=True,max_length=400)
    is_hot_user       = models.BooleanField(default=True)
    is_active         = models.BooleanField(default=True)
    tag_ids           = ArrayField(models.IntegerField(null=True))

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
        
    def __str__(self):
        return self.username