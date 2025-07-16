import os
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Category
from .serializers import CategorySerializer


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    serializer = CategorySerializer(data=request.data)

    if not serializer.is_valid():
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        error_response = {
            "message": error_messages,
            "status": status.HTTP_400_BAD_REQUEST
        }
        return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    if 'file' in request.FILES:
        image = request.FILES['file']
        file_path = f'uploads/categories/{serializer.instance.id}/{image.name}'
        save_path = default_storage.save(file_path, ContentFile(image.read()))
        serializer.instance.image = default_storage.url(save_path)
        serializer.instance.save()

    category = CategorySerializer(serializer.instance).data
    category.pop('file', None)  # Remove the file field from the response
    return Response({
        **category,
        "image" : f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{serializer.instance.image}" if serializer.instance.image else None
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    categories = Category.objects.all()
    all_categories_data = []

    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "image": f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{category.image}" if category.image else None,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }
        all_categories_data.append(category_data)

    return Response(all_categories_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, id_category):
    try:
        category = Category.objects.get(id=id_category)
        if category.image:
            image_path = category.image.lstrip('/')
            image_full_path = os.path.join(settings.MEDIA_ROOT, image_path.replace('media/', ''))

            if default_storage.exists(image_full_path):
                default_storage.delete(image_full_path)

        category.delete()
        return Response(True, status=status.HTTP_204_NO_CONTENT)

    except Category.DoesNotExist:
        error_response = {
            "message": "Category not found",
            "status": status.HTTP_404_NOT_FOUND
        }
        return Response(error_response, status=status.HTTP_404_NOT_FOUND)

