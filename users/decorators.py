from functools import wraps

import jwt
from django.conf import settings
from django.http import JsonResponse

from .models import User


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # First check cookie
        token = request.COOKIES.get("jwt")

        # If not found, check Authorization header
        if not token:
            auth_header = request.headers.get("Authorization")

            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return JsonResponse(
                {"error": "Authentication credentials not provided"},
                status=401
            )

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            # Retrieve the logged in user
            user = User.objects.select_related("role").get(
                id=payload["user_id"]
            )

            # Store useful information on the request
            request.user = user
            request.user_id = user.id
            request.username = user.username

            if user.role:
                request.role = user.role.role_name if user.role else None
            else:
                request.role = None

        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User no longer exists"},
                status=401
            )

        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Token has expired"},
                status=401
            )

        except jwt.InvalidTokenError:
            return JsonResponse(
                {"error": "Invalid token"},
                status=401
            )

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=500
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def role_required(allowed_roles):

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.role is None:
                return JsonResponse(
                    {"error": "User has no assigned role"},
                    status=403
                )

            if request.role not in allowed_roles:
                return JsonResponse(
                    {
                        "error": "Permission denied",
                        "required_roles": allowed_roles,
                        "your_role": request.role,
                    },
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator