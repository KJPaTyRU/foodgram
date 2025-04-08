from rest_framework import viewsets, status, views, permissions, filters
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg

from reciepts.models import CustomUser, Tag, Ingredient, Reciept
from api.models import BlacklistedTokens
from api.pagination import PageLimitPagination
from api.serializers import (
    UserSerializer,
    SignUpSerializer,
    CustomTokenObtainSerializer,
    ChangePasswordSerializer,
    IngredientSerializer,
    RecieptCreateSerializer,
    AvatarSerializer,
    TagSerializer,
)


class CustomTokenObtainView(TokenObtainPairView):
    serializer_class = CustomTokenObtainSerializer


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Token "):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]

        try:
            AccessToken(token)
            BlacklistedTokens.objects.create(token=token)
            return Response(
                {"detail": "Токен успешно удален."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserAndSignUpViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head", "options", "trace"]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageLimitPagination

    def create(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(views.APIView):
    http_method_names = ["get", "head", "options", "trace"]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AvatarView(views.APIView):
    http_method_names = ["put", "delete", "head", "options", "trace"]
    permission_classes = (permissions.IsAuthenticated,)

    def put(self, request):
        user = request.user
        data = request.data.copy()
        serializer = AvatarSerializer(user, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        obj = CustomUser.objects.get(id=request.user.id)
        obj.avatar = None
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(views.APIView):
    http_method_names = ["post", "head", "options", "trace"]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        data = request.data.copy()
        serializer = ChangePasswordSerializer(
            user, data=data, context={"user": user}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "head", "options", "trace"]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "head", "options", "trace"]
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class RecieptViewSet(viewsets.ModelViewSet):
    queryset = Reciept.objects.all()
    serializer_class = RecieptCreateSerializer
    permission_classes = (permissions.AllowAny,)
