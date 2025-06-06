from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from users.serializers import UserSerializer
from roles.models import Role
from roles.serializers import RoleSerializer
from users.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    """
    Retrieve user information by user ID.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "message": "User not found.",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    roles = Role.objects.filter(users__id=user.id)
    roles_serializer = RoleSerializer(roles, many=True)

    data = UserSerializer(user).data
    data['image'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{user.image}" if user.image else None
    response_data = {
        **data,
        "roles": roles_serializer.data
    }
    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    """
    Retrieve all users.
    """
    users = User.objects.all()
    all_users_data = []

    for user in users:
        roles = Role.objects.filter(users__id=user.id)
        roles_serializer = RoleSerializer(roles, many=True)

        data = UserSerializer(user).data
        data['image'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{user.image}" if user.image else None

        response_data = {
            **data,
            "roles": roles_serializer.data
        }
        all_users_data.append(response_data)

    return Response(all_users_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, user_id):
    """
    Update user information.
    """
    if str(request.user.id) != str(user_id):
        return Response(
            {
                "message": "You do not have permission to update this user.",
                "statusCode": status.HTTP_403_FORBIDDEN
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "message": "User not found.",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', None)
    lastname = request.data.get('lastname', None)
    phone = request.data.get('phone', None)

    if name is None and lastname is None and phone is None:
        return Response(
            {
                "message": "No fields to update.",
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if name is not None:
        user.name = name

    if lastname is not None:
        user.lastname = lastname

    if phone is not None:
        user.phone = phone

    user.save()

    roles = Role.objects.filter(users__id=user.id).distinct()
    roles_serializer = RoleSerializer(roles, many=True)

    data = UserSerializer(user).data
    data['image'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{user.image}" if user.image else None

    response_data = {
        **data,
        "roles": roles_serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_image(request, user_id):
    """
    Update user image.
    """
    if str(request.user.id) != str(user_id):
        return Response(
            {
                "message": "You do not have permission to update this user.",
                "statusCode": status.HTTP_403_FORBIDDEN
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {
                "message": "User not found.",
                "statusCode": status.HTTP_404_NOT_FOUND
            },
            status=status.HTTP_404_NOT_FOUND
        )

    name = request.data.get('name', None)
    lastname = request.data.get('lastname', None)
    phone = request.data.get('phone', None)
    image = request.FILES.get('file', None)

    if name is None and lastname is None and phone is None and image is None:
        return Response(
            {
                "message": "No fields to update.",
                "statusCode": status.HTTP_400_BAD_REQUEST
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if name is not None:
        user.name = name

    if lastname is not None:
        user.lastname = lastname

    if phone is not None:
        user.phone = phone

    if image is not None:
        file_path = f'uploads/users/{user.id}/{image.name}'
        save_path = default_storage.save(file_path, ContentFile(image.read()))
        user.image = default_storage.url(save_path)

    user.save()

    roles = Role.objects.filter(users__id=user.id).distinct()
    roles_serializer = RoleSerializer(roles, many=True)

    data = UserSerializer(user).data
    data['image'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{user.image}" if user.image else None

    response_data = {
        **data,
        "roles": roles_serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)