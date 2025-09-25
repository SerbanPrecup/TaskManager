from datetime import date

def calculate_task_progress(task):
    if task.deadline and task.created_at:
        total_days = (task.deadline.date() - task.created_at.date()).days
        if total_days <= 0:
            return 100
        elapsed_days = (date.today() - task.created_at.date()).days
        return min(100, max(0, int((elapsed_days / total_days) * 100)))
    return 0

STATUS_PROGRESS = {
    "Not Started": 0,
    "In Progress": 50,
    "On Hold": 15,
    "Needs Review": 90,
    "Completed": 100,
    "Cancelled": 0,
    "Delayed": 40,
}

def estimate_project_progress(status):
    return STATUS_PROGRESS.get(status, 0)