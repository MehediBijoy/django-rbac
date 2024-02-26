from rest_framework_simplejwt.tokens import AccessToken

from users.models import UserRole
from .serializers.users import UserSerializer


class UserAuthResponse:
    token_class = AccessToken

    def __init__(self, user, remember_me=False) -> None:
        self.user = user
        self.remember = remember_me

    @property
    def data(self):
        data = dict()

        data['user'] = UserSerializer(instance=self.user).data
        data['token'] = str(self.get_token(self.user))

        return data

    def get_token(self, user):
        token = self.token_class.for_user(user)
        token['role'] = UserRole.get_role(user.role)

        if self.remember:
            token.set_exp(lifetime=token.lifetime * 2)

        return token
