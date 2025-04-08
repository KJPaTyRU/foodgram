from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from api.views import (
    UserAndSignUpViewSet,
    CurrentUserView,
    CustomTokenObtainView,
    ChangePasswordView,
    IngredientViewSet,
    TagViewSet,
    AvatarView,
    LogoutView,
    RecieptViewSet,
)

router = routers.DefaultRouter()
# router.register(r'posts', PostViewSet)
# router.register(
#     r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comment'
# )
router.register(r"users", UserAndSignUpViewSet, basename="users")
router.register(r"tags", TagViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecieptViewSet)

urlpatterns = [
    path(
        "auth/token/login/", CustomTokenObtainView.as_view(), name="get_token"
    ),
    path("auth/token/logout/", LogoutView.as_view(), name="delete_token"),
    path("users/me/avatar/", AvatarView.as_view(), name="current_user_avatar"),
    path("users/me/", CurrentUserView.as_view(), name="current_user"),
    path(
        "users/set_password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
    path("", include(router.urls)),
]
