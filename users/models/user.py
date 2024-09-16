import json
from typing import Self
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from .mixins.otp_mixin import OneTimePasswordMixin
from .mixins.email_confirmation_mixin import EmailConfirmationMixin
from .mixins.forgot_password_mixin import ForgotPasswordMixin


class UserStatus(models.TextChoices):
    ACTIVE = 'active', 'active'
    INACTIVE = 'inactive', 'inactive'
    INVESTIGATE = 'investigate', 'investigate'
    BLOCKED = 'blocked', 'blocked'


class UserRole(models.TextChoices):
    USER = 'user', 'user'
    ADMIN = 'admin', 'admin'
    EDITOR_ADMIN = 'editor_admin', 'editor_admin'
    SUPER_ADMIN = 'super_admin', 'super_admin'

    @classmethod
    def get_role(cls, value):
        for choice in cls.choices:
            if choice[0] == value:
                return choice[1]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('User must have email')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('role', UserRole.ADMIN)
        return self.create_user(email, password, **kwargs)


class User(
    AbstractBaseUser,
    PermissionsMixin,
    OneTimePasswordMixin,
    EmailConfirmationMixin,
    ForgotPasswordMixin,
):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=25, choices=UserStatus.choices, default=UserStatus.ACTIVE)
    status_reason = models.TextField(null=True)
    role = models.CharField(max_length=25, choices=UserRole.choices, default=UserRole.USER)
    # django default fields for django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:  # type: ignore
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('-id',)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'phone_number']

    objects = UserManager()

    @property
    def is_user(self) -> bool:
        return self.role == UserRole.USER

    @property
    def is_admin(self) -> bool:
        return not self.is_user

    def write_log(self, log_type: str, payload=None, reference: Self | None = None):
        self.user_logs.create( # type: ignore
            type=log_type,
            payload=json.dumps(payload) if payload else None,
            reference=reference if reference and reference != self else None
        )
