# Create your views here.
from django.contrib.auth import authenticate, get_user_model
from django_ratelimit.decorators import ratelimit
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)
from .utils import (
    clear_reset_token,
    generate_reset_token,
    send_password_reset_email,
    store_reset_token,
    verify_reset_token,
)

User = get_user_model()


@swagger_auto_schema(
    method="post",
    request_body=UserRegistrationSerializer,
    responses={
        201: openapi.Response("User created successfully"),
        400: openapi.Response("Validation error"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    email = request.data.get("email")

    if User.objects.filter(email=email).exists():
        return Response(
            {"message": "User with this email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # send_welcome_email(user.email, user.full_name)

        return Response(
            {
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response("Login successful"),
        400: openapi.Response("Invalid credentials"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"message": "Email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"message": "User with this email does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response(
            {"message": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    return Response(
        {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(access_token),
            },
        },
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="post",
    request_body=PasswordResetRequestSerializer,
    responses={
        200: openapi.Response("Password reset token sent"),
        404: openapi.Response("User not found"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def forgot_password(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]

        try:
            _ = User.objects.get(email=email)

            token = generate_reset_token()
            store_reset_token(email, token, expires_in=600)
            if send_password_reset_email(email, token):
                return Response(
                    {"message": "Password reset token sent to your email"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Failed to send email"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except User.DoesNotExist:
            return Response(
                {"message": "Password reset token sent to your email"},
                status=status.HTTP_200_OK,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=PasswordResetConfirmSerializer,
    responses={
        200: openapi.Response("Password reset successful"),
        400: openapi.Response("Invalid token or validation error"),
    },
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        user = None
        for cached_user in User.objects.all():
            if verify_reset_token(cached_user.email, token):
                user = cached_user
                break

        if user:
            user.set_password(new_password)
            user.save()

            clear_reset_token(user.email)

            return Response(
                {"message": "Password reset successful"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get", responses={200: UserProfileSerializer})
@api_view(["GET"])
@permission_classes([])
def profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def ping(request):
    return "pong"
