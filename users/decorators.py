from functools import wraps
from django.http import JsonResponse
from django.conf import settings
import jwt

def role_required(allowed_roles):
    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # request.role is set by jwt_required
            if request.role not in allowed_roles:
                return JsonResponse(
                    {"error": "Permission denied"},
                    status=403
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get("jwt")

        if token is None:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if token is None:
            return JsonResponse(
                {"error": "Authentication credentials not provided"},
                status=401,
            )

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

            request.user_id = payload["user_id"]
            request.username = payload["username"]
            request.role = payload["role"]

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)

        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


