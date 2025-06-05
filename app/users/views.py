import bcrypt
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer


@api_view(['POST'])
def create(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email= request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            response_data = {
                "user": UserSerializer(user).data,
                "token": "Bearer " + access_token
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid password."}, status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
