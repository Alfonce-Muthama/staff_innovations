from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User,Department,Role
import json


@csrf_exempt
def create_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            department = Department.objects.get(id=data["department_id"])

            user = User.objects.create(
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                role=data.get("role"),
                department_id=department
            )

            return JsonResponse({
                "message": "User created successfully",
                "id": str(user.id)
            }, status=201)

        except Department.DoesNotExist:
            return JsonResponse({"error": "Department not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "POST method required"}, status=405)
