from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import User,Department
from .decorators import jwt_required,role_required
from Transaction_Log_Base.services import AuditLogger
import jwt
import datetime
from django.conf import settings
import json
from django.http import HttpRequest, HttpResponse

# CREATE USER
@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON in request body"},
                status=400
            )

        # Username
        if not data.get("username"):
            return JsonResponse({"error": "Username is required."}, status=400)
        # Email
        if not data.get("email"):
            return JsonResponse({"error": "Email is required."}, status=400)

        # Password
        if not data.get("password"):
            return JsonResponse({"error": "Password is required."}, status=400)

        # First Name
        if not data.get("first_name"):
            return JsonResponse({"error": "First name is required."}, status=400)

        # Last Name
        if not data.get("last_name"):
            return JsonResponse({"error": "Last name is required."}, status=400)

        # Role
        if not data.get("role"):
            return JsonResponse({"error": "Role is required."}, status=400)

        # Department
        if not data.get("department_id"):
            return JsonResponse({"error": "Department is required."}, status=400)

        # Check if username already exists
        if User.objects.filter(username=data["username"]).exists():
            return JsonResponse({"error": "Username already exists."}, status=400)

        # Check if email already exists
        if User.objects.filter(email=data["email"]).exists():
            return JsonResponse({"error": "Email already exists."}, status=400)

        # Check password length
        if len(data["password"]) < 8:
            return JsonResponse(
                {"error": "Password must be at least 8 characters long."},
                status=400
            )

        # Check department exists
        try:
            department = Department.objects.get(id=data["department_id"])
        except Department.DoesNotExist:
            return JsonResponse({"error": "Department not found."}, status=404)

        user = User.objects.create(
            username=data["username"],
            email=data["email"],
            password=make_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=data["role"],
            department_id=department
        )
        AuditLogger.log(
            request=request,
            user=request.user,
            event_type="USER_CREATED",
            message=f"User '{user.username}' was created.",
            entity_type="User",
            entity_id=user.id,
            entity_name=user.username,
        )

        return JsonResponse({
            "message": "User created successfully",
            "id": str(user.id)
        }, status=201)

    return JsonResponse({"error": "POST method required"}, status=405)

# LOGIN USER
@csrf_exempt
def login_user(request: HttpRequest):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400,
        )

    try:
        user = User.objects.get(username=data["username"])

        if not check_password(data["password"], user.password):
            return JsonResponse({"error": "Invalid password"}, status=401)

        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role,
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC)
                   + datetime.timedelta(minutes=30),
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        response = JsonResponse({
            "message": "Login successful",
            "token": token,
            "username": user.username,
            "role": user.role,
        })

        response.set_cookie(
            key="jwt",
            value=token,
            httponly=True,
            samesite="Lax",
            secure=False,
            max_age=30 * 60,
        )
        AuditLogger.log(
            request=request,
            user=user,
            event_type="LOGIN",
            message=f"{user.username} logged in successfully",
            entity_type=user,
            entity_id=user.id,
            entity_name=user.username,
        )

        return response

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid request body"}, status=400)

# UPDATE
@csrf_exempt
@jwt_required
@role_required(["User"])
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
            user.role = data.get("role", user.role)
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

            AuditLogger.log(
                request=request,
                user=request.user,
                event_type="UPDATE_USER",
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
@role_required(["User"])
def delete_user(request, pk):
    if request.method == "DELETE":
        try:
            user = User.objects.get(pk=pk)
            AuditLogger.log(
                request=request,
                user=request.user,  # or the authenticated user object
                event_type="DELETE_USER",
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





