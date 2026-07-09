from django.utils import timezone

def complete_task(task):
    task.completed_at = timezone.now().date()
    task.save()
    update_project_progress(task.project_phase_id.project_id)

def update_project_progress(project):
    total = project.projectphase_set.count()
    if total == 0:
        project.progress = "0%"
    else:
        completed = 0
        for phase in project.projectphase_set.all():
            if phase.task_set.exists() and all(
                t.completed_at for t in phase.task_set.all()
            ):
                completed += 1
        project.progress = f"{int(completed * 100 / total)}%"
    project.save()


