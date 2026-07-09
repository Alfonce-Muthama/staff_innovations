from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
import json

from users.decorators import role_required
from .models import Project, ProjectPhase, Task
from users.models import User
from .services import complete_task

# Create your views here.
@csrf_exempt
def create_phase(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    project = Project.objects.get(pk=project_id)

    phase = ProjectPhase.objects.create(
        project_id=project,
        phase_name=data["phase_name"],
        description=data.get("description", "")
    )

    return JsonResponse({"id": str(phase.id)}, status=201)


@csrf_exempt
def create_task(request, phase_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    phase = ProjectPhase.objects.get(pk=phase_id)

    task = Task.objects.create(
        project_phase_id=phase,
        assigned_to=User.objects.get(pk=data["assigned_to"]),
        title=data["title"],
        description=data.get("description", ""),
        priority=data.get("priority"),
        due_date=parse_date(data["due_date"]) if data.get("due_date") else None,
    )

    return JsonResponse({"id": str(task.id)}, status=201)


@csrf_exempt
def mark_task_complete(request, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    task = Task.objects.get(pk=task_id)
    complete_task(task)

    return JsonResponse({"message": "Task completed successfully"})


@csrf_exempt
def list_projects(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET method required"}, status=405)

    data = [
        {
            "id": str(p.id),
            "name": p.project_name,
            "progress": p.progress,
        }
        for p in Project.objects.all()
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def project_detail(request, pk):
    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)

    return JsonResponse({
        "id": str(p.id),
        "name": p.project_name,
        "description": p.description,
        "progress": p.progress,
    })


@csrf_exempt
def update_project(request, pk):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT method required"}, status=405)

    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)

    data = json.loads(request.body)
    project.project_name = data.get("project_name", project.project_name)
    project.description = data.get("description", project.description)
    project.end_date = parse_date(data["end_date"]) if data.get("end_date") else project.end_date
    project.save()

    return JsonResponse({"message": "Project updated successfully"})


@csrf_exempt
def delete_project(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE method required"}, status=405)

    try:
        Project.objects.get(pk=pk).delete()
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)

    return JsonResponse({"message": "Project deleted successfully"})


