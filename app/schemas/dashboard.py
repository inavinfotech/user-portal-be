from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ActivityItem(BaseModel):
    id: str
    type: str
    description: str
    timestamp: datetime

class DashboardSummary(BaseModel):
    total_users: int
    total_roles: int
    total_applications: int
    active_sessions: int
    recent_activity: List[ActivityItem]
