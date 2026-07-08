from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.decorators import jwt_required,role_required
from users.models import User
from .models import Idea
from .services import create_idea
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
    ideas = Idea.objects.select_related("creator")
    data = []
    for idea in ideas:
        data.append({"id": str(idea.id),
            "title": idea.title,
            "description": idea.description,
            "status": idea.status,
            "priority": idea.priority,
            "likes": idea.likes,
            "dislikes": idea.dislikes,
            "creator": idea.creator.username
        })
    return JsonResponse(data, safe=False)

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
def delete_idea(request, pk):
    if request.method != "DELETE":
        return JsonResponse({
            "error":
            "DELETE method required"
        }, status=405)

    try:
        idea = Idea.objects.get(id=pk)
        if str(idea.creator.id) != request.user_id:
            return JsonResponse({
                "error":
                "Permission denied"
            }, status=403)

        if idea.status != "Draft":
            return JsonResponse({
                "error":
                "Only Draft ideas can be deleted."

            }, status=400)

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
        return JsonResponse({
            "message": "Vote recorded",
            "dislikes": idea.dislikes,
        })

    except (Idea.DoesNotExist, User.DoesNotExist):
        return JsonResponse({"error": "Resource not found"}, status=404)



#PRODUCT MANAGER APPROVAL/REJECTION
@csrf_exempt
@jwt_required
@role_required(["Product Manager"])
def approve_idea(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        idea = Idea.objects.get(id=pk)
        data = json.loads(request.body)
        project = approve_idea_service(
            idea=idea,
            priority=data["priority"],
            due_date=data["due_date"],
            review_comment=data.get("review_comment", ""),
            product_manager=User.objects.get(id=request.user_id),
        )
        return JsonResponse({
            "message": "Idea approved successfully",
            "project_id": str(project.id),
        })

    except Idea.DoesNotExist:
        return JsonResponse({"error": "Idea not found"}, status=404)


@csrf_exempt
@jwt_required
@role_required(["Product Manager"])
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

        return JsonResponse({
            "message": "Idea rejected successfully"
        })

    except Idea.DoesNotExist:
        return JsonResponse({"error": "Idea not found"}, status=404)



