from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from users.models import User


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['id']
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

        user.is_authenticated = True  # Ensure the user is marked as authenticated
        return user
