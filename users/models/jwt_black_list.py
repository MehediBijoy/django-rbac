from django.db import models
from datetime import datetime
from django.utils import timezone
from rest_framework_simplejwt import tokens


class JwtBlackList(models.Model):
    exp = models.DateTimeField()
    jti = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jwt_black_list'
        verbose_name = 'jwt black list'
        verbose_name_plural = 'jwt black lists'

    @classmethod
    def check_revoked(cls, token: tokens.Token) -> bool:
        """check auth token is active or not"""
        try:
            obj = cls.objects.get(jti=token.get('jti'))
        except cls.DoesNotExist:
            return False

        return obj.is_valid

    @classmethod
    def revoke_token(cls, token: tokens.Token):
        cls.objects.create(
            jti=token.get('jti'),
            exp=timezone.make_aware(
                datetime.fromtimestamp(token.get('exp')),
                timezone=timezone.get_current_timezone()
            ),
        )

    @property
    def is_valid(self):
        return timezone.now() <= self.exp
