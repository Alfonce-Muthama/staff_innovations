from django.http import JsonResponse
from django.template.defaultfilters import title
from django.views.decorators.csrf import csrf_exempt
from users.decorators import jwt_required,role_required
from users.models import User
from .models import Idea
from .services import create_idea
from Transaction_Log_Base.services import AuditLogger
from Transaction_Log_Base.models import EventType
from django.core.paginator import Paginator
import json
from .services import (
    submit_idea as submit_idea_service,
    add_comment as add_comment_service,
    like_idea as like_idea_service,
    dislike_idea as dislike_idea_service,
    approve_idea as approve_idea_service,
    reject_idea as reject_idea_service,
)

@csrf_exempt
@jwt_required
@role_required(["Admin", "Product Manager"])
def create_new_idea(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description")

        if not title:
            return JsonResponse(
                {"error": "Title is required"},
                status=400
            )
        if not description:
            return JsonResponse(
                {"error": "Description is required"},
                status=400
            )
        user = User.objects.get(id=request.user_id)

        idea = create_idea(
            user=user,
            title=title,
            description=description
        )
        event_type = EventType.objects.get(name="IDEA_CREATED")

        AuditLogger.log(
            request=request,
            user=user,
            event_type=event_type,
            message=f"Idea '{idea.title}' created.",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Idea created successfully",
            "idea_id": str(idea.id),
            "status": idea.status
        }, status=201)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@jwt_required
def list_ideas(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "GET method required"},
            status=405
        )

    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 10)

    try:
        page_size = int(page_size)
    except ValueError:
        page_size = 10

    ideas = Idea.objects.select_related("creator").order_by("-created_at")

    paginator = Paginator(ideas, page_size)

    try:
        page_obj = paginator.page(page)
    except:
        return JsonResponse(
            {"error": "Invalid page number"},
            status=400
        )

    data = []

    for idea in page_obj:
        data.append({
            "id": str(idea.id),
            "title": idea.title,
            "description": idea.description,
            "status": idea.status,
            "priority": idea.priority,
            "likes": idea.likes,
            "dislikes": idea.dislikes,
            "creator": idea.creator.username,
        })

    return JsonResponse({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page_obj.number,
        "page_size": page_size,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "results": data,
    })

@jwt_required
def idea_detail(request, pk):
    if request.method != "GET":
        return JsonResponse(
            {"error": "GET method required"},
            status=405
        )
    try:

        idea = Idea.objects.select_related(
            "creator"
        ).get(id=pk)

        return JsonResponse({
            "id": str(idea.id),
            "title": idea.title,
            "description": idea.description,
            "status": idea.status,
            "priority": idea.priority,
            "due_date": idea.due_date,
            "review_comment": idea.review_comment,
            "likes": idea.likes,
            "dislikes": idea.dislikes,
            "creator": idea.creator.username

        })

    except Idea.DoesNotExist:

        return JsonResponse(
            {"error": "Idea not found"},
            status=404
        )

@csrf_exempt
@jwt_required
@role_required(["Admin"])
def update_idea(request, pk):

    if request.method != "PUT":
        return JsonResponse(
            {"error": "PUT method required"},
            status=405
        )

    try:

        idea = Idea.objects.get(id=pk)

        if str(idea.creator.id) != request.user_id:

            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )

        if idea.status != "Draft":

            return JsonResponse({
                "error":
                "Only Draft ideas can be edited."
            }, status=400)

        data = json.loads(request.body)
        idea.title = data.get(
            "title",
            idea.title
        )
        idea.description = data.get(
            "description",
            idea.description
        )
        idea.save()
        actor = User.objects.get(id=request.user_id)

        event_type = EventType.objects.get(name="IDEA_UPDATED")
        AuditLogger.log(
            request=request,
            user=actor,
            event_type=event_type,
            message=f"Idea '{idea.title}' was updated.",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )


        return JsonResponse({
            "message":
            "Idea updated successfully"
        })

    except Idea.DoesNotExist:

        return JsonResponse({
            "error":
            "Idea not found"
        }, status=404)

    except Exception as e:

        return JsonResponse({
            "error":
            str(e)
        }, status=400)

@csrf_exempt
@jwt_required
@role_required(["Admin"])
def delete_idea(request, pk):
    if request.method != "DELETE":
        return JsonResponse({
            "error":
            "DELETE method required"
        }, status=405)

    try:
        idea = Idea.objects.get(id=pk)

        current_user = User.objects.select_related("role").get(id=request.user_id)

        is_creator = idea.creator.id == request.user_id
        is_admin = current_user.role and current_user.role.name == "Admin"

        if not (is_creator or is_admin):
            return JsonResponse(
                {"error": "Permission denied"},
                status=403,
            )

        if idea.status != "Draft":
            return JsonResponse({
                "error":
                "Only Draft ideas can be deleted."

            }, status=400)

        event_type = EventType.objects.get(name="IDEA_DELETED")
        AuditLogger.log(
            request=request,
            user=User.objects.get(id=request.user_id),
            event_type=event_type,
            message=f"Idea '{idea.title}' was deleted",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )

        idea.delete()
        return JsonResponse({
            "message":
            "Idea deleted successfully"
        })

    except Idea.DoesNotExist:
        return JsonResponse({

            "error":
            "Idea not found"

        }, status=404)


# PEER_REVIEW STAGE
@csrf_exempt
@jwt_required
def submit_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        idea = Idea.objects.get(id=pk)
        if str(idea.creator_id) != request.user_id:
            return JsonResponse({"error": "Permission denied"}, status=403)

        if idea.status != "Draft":
            return JsonResponse(
                {"error": "Only Draft ideas can be submitted"},
                status=400,
            )
        submit_idea_service(idea)

        event_type = EventType.objects.get(name="IDEA_SUBMITTED")
        AuditLogger.log(
            request=request,
            user=idea.creator,
            event_type=event_type,
            message=f"Idea '{idea.title}' was submitted.",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Idea submitted successfully",
            "status": idea.status,
        })
    except Idea.DoesNotExist:
        return JsonResponse({"error": "Idea not found"}, status=404)

@csrf_exempt
@jwt_required
def add_comment(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        data = json.loads(request.body)
        text = data.get("comment")

        if not text:
            return JsonResponse({"error": "Comment is required"}, status=400)
        idea = Idea.objects.get(id=pk)
        user = User.objects.get(id=request.user_id)
        comment = add_comment_service(user, idea, text)

        event_type = EventType.objects.get(name="IDEA_COMMENTED")
        AuditLogger.log(
            request=request,
            user=user,
            event_type=event_type,
            message=f"Comment added to idea '{idea.title}'.",
            entity_type="IdeaComment",
            entity_id=comment.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Comment added",
            "comment_id": str(comment.id),
        }, status=201)

    except (Idea.DoesNotExist, User.DoesNotExist):
        return JsonResponse({"error": "Resource not found"}, status=404)

@csrf_exempt
@jwt_required
def like_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        idea = Idea.objects.get(id=pk)
        user = User.objects.get(id=request.user_id)
        like_idea_service(user, idea)

        event_type = EventType.objects.get(name="LIKE_IDEA")
        AuditLogger.log(
            request=request,
            user=user,
            event_type=event_type,
            message=f"{user.username} liked '{idea.title}'",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Vote recorded",
            "likes": idea.likes,
            "status": idea.status,
        })

    except (Idea.DoesNotExist, User.DoesNotExist):
        return JsonResponse({"error": "Resource not found"}, status=404)


@csrf_exempt
@jwt_required
def dislike_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    try:
        idea = Idea.objects.get(id=pk)
        user = User.objects.get(id=request.user_id)
        dislike_idea_service(user, idea)

        event_type = EventType.objects.get(name="DISLIKE_IDEA")
        AuditLogger.log(
            request=request,
            user=user,
            event_type=event_type,
            message=f"{user.username} disliked '{idea.title}'",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Vote recorded",
            "dislikes": idea.dislikes,
        })

    except (Idea.DoesNotExist, User.DoesNotExist):
        return JsonResponse({"error": "Resource not found"}, status=404)



#PRODUCT MANAGER APPROVAL/REJECTION
@csrf_exempt
@jwt_required
@role_required(["Product Manager", "Admin"])
def approve_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        idea = Idea.objects.get(id=pk)
        data = json.loads(request.body)

        print("REQUEST DATA:", data)
        print("Priority:", data.get("priority"))
        print("Due date:", data.get("due_date"))
        print("Comment:", data.get("review_comment"))
        project = approve_idea_service(
            idea=idea,
            priority=data.get("priority"),
            due_date = data.get("due_date"),
            review_comment = data.get("review_comment"),
            product_manager=User.objects.get(id=request.user_id),
        )

        event_type = EventType.objects.get(name="PROJECT_CREATED")
        AuditLogger.log(
            request=request,
            user=User.objects.get(id=request.user_id),
            event_type=event_type,
            message=f"Approved idea '{idea.title}' and created project '{project.project_name}'",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )
        return JsonResponse({
            "message": "Idea approved and project created successfully.",
            "project_id": str(project.id),
        })

    except Idea.DoesNotExist:
        return JsonResponse({"error": "Idea not found"}, status=404)


@csrf_exempt
@jwt_required
@role_required(["Product Manager","Admin"])
def reject_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        idea = Idea.objects.get(id=pk)
        data = json.loads(request.body)

        reject_idea_service(
            idea,
            data.get("review_comment", "")
        )

        event_type = EventType.objects.get(name="IDEA_REJECTED")
        AuditLogger.log(
            request=request,
            user=User.objects.get(id=request.user_id),
            event_type=event_type,
            message=f"Idea '{idea.title}' was rejected.",
            entity_type="Idea",
            entity_id=idea.id,
            entity_name=idea.title,
        )

        return JsonResponse({
            "message": "Idea rejected successfully"
        })

    except Idea.DoesNotExist:
        return JsonResponse({"error": "Idea not found"}, status=404)



