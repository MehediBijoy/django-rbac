from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserStatus(models.IntegerChoices):
    ACTIVE = 0, 'active'
    INACTIVE = 1, 'inactive'
    INVESTIGATE = 2, 'investigate'
    BLOCKED = 3, 'blocked'


class UserRole(models.IntegerChoices):
    USER = 0, 'user'
    ADMIN = 1, 'admin'
    SUPER_ADMIN = 2, 'super_admin'
    TOP_MANAGER = 3, 'top_manager'


class UserType(models.IntegerChoices):
    REGULAR = 0, 'regular'
    AFFILIATE = 1, 'affiliate'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('User must have email')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('role', UserRole.SUPER_ADMIN)
        return self.create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    deprecated_password = models.CharField(max_length=255, null=True)
    type = models.PositiveSmallIntegerField(
        choices=UserType.choices, default=UserType.REGULAR
    )
    status = models.PositiveSmallIntegerField(
        choices=UserStatus.choices, default=UserStatus.ACTIVE
    )
    role = models.PositiveSmallIntegerField(
        choices=UserRole.choices, default=UserRole.USER
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joined_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('-id',)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def access_tracks(self) -> 'UserAccessTracks':
        try:
            return self.user_access_tracks
        except UserAccessTracks.DoesNotExist:
            return UserAccessTracks.objects.create(user=self)

    def unlock(self):
        self.access_tracks.reset_failed_attempts()
        self.access_tracks.locked_at = None
        self.access_tracks.save()


class UserAccessTracks(models.Model):
    user = models.OneToOneField(
        User, related_name='user_access_tracks', on_delete=models.CASCADE
    )
    sign_in_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True)
    failed_attempts = models.IntegerField(default=0)
    locked_at = models.DateTimeField(null=True)
    user_agent = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'user_access_tracks'
        verbose_name = 'user_access_track'
        verbose_name_plural = 'user_access_tracks'

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.save()

    def increase_sign_in_count(self):
        self.sign_in_count += 1
        self.save()
