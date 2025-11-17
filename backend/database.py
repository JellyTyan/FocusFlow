from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Optional
from models.project import Project, ProjectCreate, ProjectUpdate, Topic

projects_db: Dict[str, dict] = {}
topics_db: Dict[str, dict] = {}

def calculate_priority(topic: dict, project_deadline: datetime) -> float:
    """Расчет приоритета темы"""
    days_to_deadline = (project_deadline - datetime.now()).days
    if days_to_deadline <= 0:
        days_to_deadline = 1

    confidence_factor = 6 - topic["confidence_level"]
    stuck_multiplier = 1 + (topic["stuck_count"] * 0.2)

    return (1 / days_to_deadline) * confidence_factor * stuck_multiplier

def create_project(project_data: ProjectCreate) -> Project:
    """Создать новый проект"""
    project_id = str(uuid4())
    now = datetime.now()

    project_dict = {
        "id": project_id,
        "name": project_data.name,
        "subject": project_data.subject,
        "deadline": project_data.deadline,
        "created_at": now,
        "topics": [],
        "progress": 0.0
    }

    for topic_name in project_data.topics:
        topic_id = str(uuid4())
        topic_dict = {
            "id": topic_id,
            "project_id": project_id,
            "name": topic_name,
            "confidence_level": 1,
            "priority_score": 0.0,
            "stuck_count": 0,
            "created_at": now
        }
        topics_db[topic_id] = topic_dict
        project_dict["topics"].append(topic_id)

    # Пересчитываем приоритеты
    update_priorities(project_id)

    projects_db[project_id] = project_dict
    return dict_to_project(project_dict)

def get_all_projects() -> List[Project]:
    """Получить все проекты"""
    return [dict_to_project(p) for p in projects_db.values()]

def get_project(project_id: str) -> Optional[Project]:
    """Получить проект по ID"""
    if project_id not in projects_db:
        return None
    return dict_to_project(projects_db[project_id])

def update_project(project_id: str, update_data: ProjectUpdate) -> Optional[Project]:
    """Обновить проект"""
    if project_id not in projects_db:
        return None

    project = projects_db[project_id]
    update_dict = update_data.dict(exclude_unset=True)

    for key, value in update_dict.items():
        project[key] = value

    update_priorities(project_id)
    return dict_to_project(project)

def delete_project(project_id: str) -> bool:
    """Удалить проект"""
    if project_id not in projects_db:
        return False

    topic_ids = projects_db[project_id]["topics"]
    for topic_id in topic_ids:
        topics_db.pop(topic_id, None)

    del projects_db[project_id]
    return True

def update_priorities(project_id: str):
    """Обновить приоритеты тем проекта"""
    if project_id not in projects_db:
        return

    project = projects_db[project_id]
    deadline = project["deadline"]

    for topic_id in project["topics"]:
        if topic_id in topics_db:
            topic = topics_db[topic_id]
            topic["priority_score"] = calculate_priority(topic, deadline)

def dict_to_project(project_dict: dict) -> Project:
    """Конвертировать словарь в объект Project"""
    topics = []
    for topic_id in project_dict["topics"]:
        if topic_id in topics_db:
            topic_dict = topics_db[topic_id]
            topics.append(Topic(**topic_dict))

    return Project(
        id=project_dict["id"],
        name=project_dict["name"],
        subject=project_dict["subject"],
        deadline=project_dict["deadline"],
        created_at=project_dict["created_at"],
        topics=topics,
        progress=project_dict["progress"]
    )
