from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User,Department, Role
from .decorators import jwt_required,role_required
from Transaction_Log_Base.services import AuditLogger
from Transaction_Log_Base.models import EventType, TransactionLogBase
import jwt
import datetime
from django.conf import settings
import json
from django.http import HttpRequest, HttpResponse

#CREATE USER
@csrf_exempt
@jwt_required
@role_required(["Admin"])
def create_user(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required"},
            status=405
        )

    try:
        data = json.loads(request.body)

        required_fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "department_id",
        ]

        for field in required_fields:
            if not data.get(field):
                return JsonResponse(
                    {"error": f"{field} is required"},
                    status=400
                )

        if User.objects.filter(username=data["username"]).exists():
            return JsonResponse(
                {"error": "Username already exists"},
                status=400
            )

        if User.objects.filter(email=data["email"]).exists():
            return JsonResponse(
                {"error": "Email already exists"},
                status=400
            )

        if len(data["password"]) < 8:
            return JsonResponse(
                {
                    "error": "Password must be at least 8 characters long."
                },
                status=400
            )

        try:
            department = Department.objects.get(
                id=data["department_id"]
            )

        except Department.DoesNotExist:
            return JsonResponse(
                {"error": "Department not found"},
                status=404
            )

        try:
            role = Role.objects.get(name=data["role"])
        except Role.DoesNotExist:
            return JsonResponse(
                {"error": "Role not found"},
                status=404
            )

        user = User.objects.create(
            username=data["username"],
            email=data["email"],
            password=make_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=role,
            department_id=department,
        )

        try:

            event_type = EventType.objects.get(
                name="USER_CREATED"
            )

            AuditLogger.log(
                request=request,

                # Logged-in Admin
                user=request.user,

                event_type=event_type,

                message=f"{request.user.username} created user '{user.username}'.",

                entity_type="User",

                entity_id=user.id,

                entity_name=user.username,
            )

        except EventType.DoesNotExist:
            pass

        return JsonResponse(
            {
                "message": "User created successfully.",
                "id": str(user.id),
            },
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {
                "error": f"User failed to create. {str(e)}"
            },
            status=500,
        )


# LOGIN USER
@csrf_exempt
def login_user(request: HttpRequest):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST method required"},
            status=405
        )

    try:
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")

        if not username:
            return JsonResponse(
                {"error": "Username is required"},
                status=400
            )

        if not password:
            return JsonResponse(
                {"error": "Password is required"},
                status=400
            )

        user = User.objects.select_related("role").get(
            username=username
        )

        if not check_password(password, user.password):
            return JsonResponse(
                {"error": "Invalid password"},
                status=401
            )

        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role.name if user.role else None,
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC)
                   + datetime.timedelta(minutes=30),

        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        response = JsonResponse(
            {
                "message": "Login successful",
                "token": token,
                "username": user.username,
                "role": user.role.name if user.role else None,
            }
        )

        response.set_cookie(
            key="jwt",
            value=token,
            httponly=True,
            secure=False,        # True in production
            samesite="Lax",
            max_age=30 * 60
        )

        try:
            event_type = EventType.objects.get(name="LOGIN")

            AuditLogger.log(
                request=request,
                user=user,
                event_type=event_type,
                message=f"{user.username} logged into the system.",
                entity_type="User",
                entity_id=user.id,
                entity_name=user.username,
            )

        except EventType.DoesNotExist:
            pass

        return response

    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=404
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )

# UPDATE
@csrf_exempt
@jwt_required
@role_required(["Admin"])
def update_user(request, pk):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON in request body"},
                status=400,
            )

        try:
            user = User.objects.get(pk=pk)
            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)
            if data.get("password"):
                user.password = make_password(data["password"])
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            if "role" in data:
                try:
                    role = Role.objects.get(name=data["role"])
                    user.role = role
                except Role.DoesNotExist:
                    return JsonResponse(
                        {"error": "Role not found"},
                        status=404
                    )
            if "department_id" in data:
                try:
                    user.department_id = Department.objects.get(
                        id=data["department_id"]
                    )
                except Department.DoesNotExist:
                    return JsonResponse(
                        {"error": "Department not found"},
                        status=404,
                    )
            user.save()
            user.save()

            event_type = EventType.objects.get(name="User Updated")
            AuditLogger.log(
                request=request,
                user=request.user,
                event_type=event_type,
                message=f"Updated user '{user.username}'",
                entity_type="User",
                entity_id=user.id,
                entity_name=user.username,
            )

            return JsonResponse({"message": "user updated successfully"})

        except User.DoesNotExist:
            return JsonResponse({"error": "user not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "PUT method required"}, status=405)


#DELETE
@csrf_exempt
@jwt_required
@role_required(["Admin"])
def delete_user(request, pk):
    if request.method == "DELETE":
        try:
            user = User.objects.get(pk=pk)

            event_type = EventType.objects.get(name="User Deleted")
            AuditLogger.log(
                request=request,
                user=request.user,  # or the authenticated user object
                event_type=event_type,
                message=f"Deleted user '{user.username}'",
                entity_type="User",
                entity_id=user.id,
                entity_name=user.username,
            )

            user.delete()
            return JsonResponse({
                "message": "user deleted successfully"
            })

        except User.DoesNotExist:
            return JsonResponse({"error": "user not found"}, status=404)

    return JsonResponse({"error": "DELETE method required"}, status=405)





