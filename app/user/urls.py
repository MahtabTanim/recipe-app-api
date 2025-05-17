from django.urls import path
from .views import (
    CreateUserView,
    CreateTokenView,
    ManageUserView,
    register_view,
    login_view,
    logout_view,
)


app_name = "user"
urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create"),
    path("token/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="me"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]
