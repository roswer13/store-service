import bcrypt

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name', 'lastname', 'email', 'phone', 'image', 'password', 'notification_token',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        raw_password = validated_data.pop('password', None)
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        validated_data['password'] = hashed_password.decode('utf-8')

        return User.objects.create(**validated_data)
