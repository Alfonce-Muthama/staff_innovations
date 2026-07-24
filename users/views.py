from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .decorators import jwt_required,role_required
from Transaction_Log_Base.services import AuditLogger
from Transaction_Log_Base.models import EventType,TransactionLogBase, Notifications
import jwt
import datetime
from django.conf import settings
import json
from django.http import HttpRequest
from django.db.models import Count, Avg
from users.models import User, Role, Department
from ideas.models import Idea
from projects.models import Project,Task
from django.utils import timezone
from Gamification.models import Badge,UserBadge,PointRule,PointHistory
from Base.pagination import paginate_queryset




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
                   + datetime.timedelta(hours=2),

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
            secure=False,        
            samesite="Lax",
            max_age=2 * 60 * 60
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
            ##[ff,rtr43r,3r34t34,hj]

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

            event_type = EventType.objects.get(name="USER_UPDATED")
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

            event_type = EventType.objects.get(name="USER_DELETED")
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

#LIST
@jwt_required
@role_required(["Admin"])
def list_users(request):

    users = User.objects.select_related(
        "role",
        "department_id"
    ).order_by("username")

    def serialize(user):
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.name if user.role else None,
            "department": (
                user.department_id.department_name
                if user.department_id else None
            ),
            "points": user.points,
        }

    return paginate_queryset(
        request,
        users,
        serialize,
        per_page=10
    )



 #The dashboard
@jwt_required
@role_required(["Admin","Developer","Product Manager"])
def dashboard(request):

    dashboard = {}

# USERS
    dashboard["users"] = {
        "total_users": User.objects.count(),

        "active_users": User.objects.filter(
            state__name="Active"
        ).count(),

        "roles": list(
            Role.objects.annotate(
                total=Count("user")
            ).values(
                "name",
                "total"
            )
        ),

        "departments": list(
            Department.objects.annotate(
                total=Count("user")
            ).values(
                "department_name",
                "total"
            )
        )
    }

# IDEAS
    dashboard["ideas"] = {

        "total": Idea.objects.count(),

        "draft": Idea.objects.filter(
            status="Draft"
        ).count(),

        "Submitted": Idea.objects.filter(
            status="Submitted"
        ).count(),

        "peer_review": Idea.objects.filter(
            status="Peer Review"
        ).count(),

        "pm_review": Idea.objects.filter(
            status="Product Manager Review"
        ).count(),

        "approved": Idea.objects.filter(
            status="Approved"
        ).count(),

        "rejected": Idea.objects.filter(
            status="Rejected"
        ).count(),

        "implementation": Idea.objects.filter(
            status="Implementation"
        ).count(),

        "impact": Idea.objects.filter(
            status="Impact Evaluation"
        ).count(),

        "archived": Idea.objects.filter(
            status="Archived"
        ).count()
    }

# PROJECTS
    dashboard["projects"] = {

        "total": Project.objects.count(),

        "completed": Project.objects.filter(
            progress=100
        ).count(),

        "ongoing": Project.objects.filter(
            progress__lt=100
        ).count(),

        "overdue": Project.objects.filter(
            progress__lt=100,
            end_date__lt=timezone.localdate()
        ).count(),

        "average_progress":
            Project.objects.aggregate(
                Avg("progress")
            )["progress__avg"] or 0
    }

# TASKS
    dashboard["tasks"] = {

        "total": Task.objects.count(),

        "completed": Task.objects.filter(
            completed=True
        ).count(),

        "pending": Task.objects.filter(
            completed=False
        ).count(),

        "overdue": Task.objects.filter(
            completed=False,
            due_date__lt=timezone.localdate()
        ).count()
    }

# GAMIFICATION
    dashboard["gamification"] = {

        "top_contributors": list(

            User.objects.order_by(
                "-points"
            ).values(
                "username",
                "points"
            )[:10]

        ),

        "points_awarded":

            PointHistory.objects.aggregate(
                total=Count("id")
            )["total"]
    }

# AUDIT LOGS
    dashboard["audit_logs"] = {

        "total_logs":
            TransactionLogBase.objects.count(),

        "today":

            TransactionLogBase.objects.filter(
                created_at=timezone.localdate()
            ).count(),

        "recent":

            list(

                TransactionLogBase.objects.select_related(
                    "event_type",
                    "triggered_by"
                ).order_by(
                    "-created_at"
                ).values(

                    "created_at",
                    "event_message",
                    "event_type__name",
                    "triggered_by__username"

                )[:10]
            )
    }

# NOTIFICATIONS

    dashboard["notifications"] = {

        "total":

            Notifications.objects.count(),

        "unread":

            Notifications.objects.filter(
                read_at=None
            ).count(),

        "latest":

            list(

                Notifications.objects.select_related(
                    "recipient"
                ).order_by(
                    "-created_at"
                ).values(

                    "recipient__username",
                    "created_at"

                )[:10]
            )
    }
#RECENT IDEAS
    dashboard["recent_ideas"] = list(
        Idea.objects.filter(
            creator=request.user
        )
        .order_by("-created_at")
        .values(
            "id",
            "title",
            "status",
            "likes",
            "created_at"
        )[:5]
    )

# CHARTS
    dashboard["charts"] = {

        "idea_status_distribution": [

            {
                "label": x["status"],
                "value": x["total"]
            }

            for x in

            Idea.objects.values(
                "status"
            ).annotate(
                total=Count("id")
            )
        ],

        "role_distribution": [

            {
                "label": x["role__name"],
                "value": x["total"]
            }

            for x in

            User.objects.values(
                "role__name"
            ).annotate(
                total=Count("id")
            )
        ],

        "department_distribution": [

            {
                "label": x["department_id__department_name"],
                "value": x["total"]
            }

            for x in

            User.objects.values(
                "department_id__department_name"
            ).annotate(
                total=Count("id")
            )
        ],

        "leaderboard":

            list(

                User.objects.order_by(
                    "-points"
                ).values(

                    "username",
                    "points"

                )[:10]
            ),

        "project_progress":

            list(

                Project.objects.values(
                    "project_name",
                    "progress"
                )
            )
    }


    return JsonResponse(dashboard)


