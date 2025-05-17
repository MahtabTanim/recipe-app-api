from rest_framework import authentication, generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import get_user_model
from .serializers import TokenSerializer, UserSerializer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """create new auth token for user"""

    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """retrieve and manages authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = [
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    ]
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self):
        return self.request.user


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        print(form.data)
        if form.is_valid():
            first_name = form.data.get("first_name")
            last_name = form.data.get("last_name")
            username = form.data.get("username")
            email = form.data.get("email")
            password = form.data.get("password")
            user = get_user_model().objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            if get_user_model().objects.filter(id=user.id).exists():
                return redirect("user:login")
            else:
                print("something worng")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("api-ui")
            else:
                messages.error(request, "Please Fill in both fields")
                return redirect("user:register")
        else:
            messages.error(request, "Please Fill in both fields")
    if request.user.is_authenticated:
        return redirect("api-ui")
    return render(
        request,
        "login.html",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(
        {"detail": "Successfully logged out."},
        status=status.HTTP_200_OK,
    )
