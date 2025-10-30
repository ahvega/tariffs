"""
Authentication API views for JWT-based authentication.

Provides endpoints for user registration, login, and profile retrieval.
These endpoints are consumed by the Next.js frontend via NextAuth.js.

Endpoints:
    - POST /api/auth/register/ - User registration
    - POST /api/auth/login/ - User login (returns JWT tokens)
    - GET /api/auth/me/ - Get current user info (requires JWT)
    - POST /api/auth/refresh/ - Refresh access token
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from MiCasillero.models import Cliente
from .serializers import RegisterSerializer, UserSerializer


@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={201: UserSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user and return JWT tokens.

    Creates a new user account and associated Cliente record.
    Returns user info and JWT tokens for immediate authentication.

    Request body:
        - username (str): Unique username
        - email (str): Email address
        - password (str): Password
        - password2 (str): Password confirmation
        - first_name (str): First name
        - last_name (str): Last name

    Returns:
        - 201: User created successfully with tokens
        - 400: Validation error
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Return user info and tokens
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Authentication"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }
    },
    responses={200: UserSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate user and return JWT tokens.

    Validates credentials and returns user info with JWT tokens.

    Request body:
        - username (str): Username or email
        - password (str): Password

    Returns:
        - 200: Authentication successful with tokens
        - 400: Missing credentials
        - 401: Invalid credentials
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Try to authenticate with username
    user = authenticate(username=username, password=password)

    # If authentication failed, try with email
    if not user:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if not user:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"error": "User account is disabled"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=["Authentication"],
    responses={200: UserSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get current authenticated user information including Cliente data.

    Requires JWT authentication via Authorization header.

    Returns:
        - 200: Current user information with cliente data
        - 401: Not authenticated or invalid token
    """
    user_data = UserSerializer(request.user).data

    # Try to get associated Cliente
    try:
        cliente = Cliente.objects.get(user=request.user)
        user_data['cliente'] = {
            'id': cliente.id,
            'codigo_cliente': cliente.codigo_cliente,
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}",
        }
    except Cliente.DoesNotExist:
        user_data['cliente'] = None

    return Response(user_data, status=status.HTTP_200_OK)
