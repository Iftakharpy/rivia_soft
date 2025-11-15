from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    user_id = models.BigAutoField(verbose_name='user id', unique=True, editable=False, primary_key=True, db_index=True)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(max_length=64, blank=False, db_index=False)
    last_name = models.CharField(max_length=64, blank=True, db_index=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"📨{self.email} 👥{self.first_name}"
    
    @classmethod
    def get_active_superusers(cls):
        return cls.objects.filter(is_superuser=True, is_active=True)

    @classmethod
    def get_active_superusers_emails(cls):
        for active_admin in cls.get_active_superusers():
            yield f"{active_admin.get_full_name()} <{active_admin.get_email()}>"

    @property
    def name(self):
        return self.get_full_name()
    
    def get_username(self) -> str:
        return self.get_email()
    
    def get_email(self) -> str:
        return self.email
    
    def get_short_name(self) -> str:
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name
        return str(self._meta.verbose_name)
    
    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.get_short_name()
