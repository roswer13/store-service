import bcrypt
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from roles.serializers import RoleSerializer
from roles.models import Role
from users.models import User, UserHasRoles
from users.serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        client_role = get_object_or_404(Role, id='CLIENT')
        UserHasRoles.objects.create(id_user=user, id_role=client_role)
        roles = Role.objects.filter(users__id=user.id).distinct()
        roles_serializer = RoleSerializer(roles, many=True)

        response_data = {
            **UserSerializer(user).data,
            'roles': roles_serializer.data
        }
        return Response(response_data,   status=status.HTTP_201_CREATED)

    error_messages = []
    for field, errors in serializer.errors.items():
        for error in errors:
            error_messages.append(f"{field}: {error}")

    error_response = {
        "message": error_messages,
        "status": status.HTTP_400_BAD_REQUEST
    }
    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


def geCustomTokenForUser(user: User):
    refresh_token = RefreshToken.for_user(user)
    del refresh_token.payload['user_id']
    refresh_token.payload['id'] = user.id
    refresh_token.payload['name'] = user.name
    return refresh_token


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email= request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response(
            {
                "message": "Email and password are required.",
                "status": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            refresh_token = geCustomTokenForUser(user)
            access_token = str(refresh_token.access_token)

            roles = Role.objects.filter(users__id=user.id).distinct()
            roles_serializer = RoleSerializer(roles, many=True)

            data = UserSerializer(user).data
            data['image'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{user.image}" if user.image else None

            response_data = {
                "user": {
                    **data,
                    "roles": roles_serializer.data
                },
                "token": "Bearer " + access_token
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "message": "Invalid password.",
                    "status": status.HTTP_401_UNAUTHORIZED
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {
                "message": "User not found.",
                "status": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )
