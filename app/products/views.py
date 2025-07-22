import os
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import Product
from .serializers import ProductSerializer


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create(request):
    serializer = ProductSerializer(data=request.data)

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

    upload_images = request.FILES.getlist('files')
    images_urls = []

    if upload_images:
        for _, image in enumerate(upload_images[:2]):
            file_path = f'uploads/products/{serializer.instance.id}/{image.name}'
            save_path = default_storage.save(file_path, ContentFile(image.read()))
            images_urls.append(default_storage.url(save_path))

        serializer.instance.image1 = images_urls[0] if len(images_urls) > 0 else None
        serializer.instance.image2 = images_urls[1] if len(images_urls) > 1 else None
        serializer.instance.save()

    product_data = ProductSerializer(serializer.instance).data
    return Response({
        **product_data,
        "image1" : f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{serializer.instance.image1}" if serializer.instance.image1 else None,
        "image2" : f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{serializer.instance.image2}" if serializer.instance.image2 else None
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_products_by_category(request, category_id):
    try:
        products = Product.objects.filter(id_category=category_id)
        if not products.exists():
            error_response = {
                "message": f'No products found for category ID {category_id}.',
                "status": status.HTTP_404_NOT_FOUND
            }
            return Response(error_response, status=status.HTTP_404_NOT_FOUND)

        serializer_products = []
        for product in products:
            serializer_data = ProductSerializer(product).data
            serializer_data['image1'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{product.image1}" if product.image1 else None
            serializer_data['image2'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{product.image2}" if product.image2 else None
            serializer_products.append(serializer_data)

        return Response(serializer_products, status=status.HTTP_200_OK)

    except Exception as e:
        error_response = {
            "message": f'An error occurred while fetching products: {str(e)}',
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete(request, id_product):
    try:
        product = Product.objects.get(id=id_product)
        if product.image1:
            image1_path = product.image1.lstrip('/').replace('media/', '')
            full_path1 = os.path.join(settings.MEDIA_ROOT, image1_path)
            if default_storage.exists(full_path1):
                default_storage.delete(product.image1)

        if product.image2:
            image2_path = product.image2.lstrip('/').replace('media/', '')
            full_path2 = os.path.join(settings.MEDIA_ROOT, image2_path)
            if default_storage.exists(full_path2):
                default_storage.delete(product.image2)

        product.delete()
        return Response(True, status=status.HTTP_204_NO_CONTENT)

    except Product.DoesNotExist:
        error_response = {
            "message": f'Product with ID {id_product} does not exist.',
            "status": status.HTTP_404_NOT_FOUND
        }
        return Response(error_response, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        error_response = {
            "message": f'An error occurred while deleting the product: {str(e)}',
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update(request, id_product):
    try:
        product = Product.objects.get(id=id_product)
        serializer = ProductSerializer(product, data=request.data, partial=True)

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

        if 'files' in request.FILES:
            files = request.FILES.getlist('files')

            if len(files) > 0:
                if product.image1:
                    image1_path = product.image1.lstrip('/').replace('media/', '')
                    full_path1 = os.path.join(settings.MEDIA_ROOT, image1_path)
                    if default_storage.exists(full_path1):
                        default_storage.delete(product.image1)

                file_path1 = f'uploads/products/{product.id}/{files[0].name}'
                save_path1 = default_storage.save(file_path1, ContentFile(files[0].read()))
                product.image1 = default_storage.url(save_path1)

            if len(files) > 1:
                if product.image2:
                    image2_path = product.image2.lstrip('/').replace('media/', '')
                    full_path2 = os.path.join(settings.MEDIA_ROOT, image2_path)
                    if default_storage.exists(full_path2):
                        default_storage.delete(product.image2)

                file_path2 = f'uploads/products/{product.id}/{files[1].name}'
                save_path2 = default_storage.save(file_path2, ContentFile(files[1].read()))
                product.image2 = default_storage.url(save_path2)

            product.save()

        serializer_data = ProductSerializer(product).data
        serializer_data['image1'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{product.image1}" if product.image1 else None
        serializer_data['image2'] = f"http://{settings.GLOBAL_IP}:{settings.GLOBAL_HOST}{product.image2}" if product.image2 else None
        return Response(serializer_data, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        error_response = {
            "message": f'Product with ID {id_product} does not exist.',
            "status": status.HTTP_404_NOT_FOUND
        }
        return Response(error_response, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        error_response = {
            "message": f'An error occurred while updating the product: {str(e)}',
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)