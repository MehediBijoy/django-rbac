from rest_framework_simplejwt.tokens import AccessToken

from .serializers import UserSerializer


class UserAuthResponse:
    token_class = AccessToken

    def __init__(self, user) -> None:
        self.user = user

    @property
    def data(self):
        data = dict()

        data['user'] = UserSerializer(instance=self.user).data
        data['token'] = str(self.get_token(self.user))

        return data

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)
