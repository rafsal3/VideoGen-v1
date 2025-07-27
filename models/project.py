from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class RenderQuality(str, Enum):
    LOW = "480p"
    MEDIUM = "720p"
    HIGH = "1080p"
    ULTRA = "4k"

class Project(BaseModel):
    project_id: Optional[str] = None
    user_id: str
    template_id: str
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    status: ProjectStatus = ProjectStatus.DRAFT
    render_quality: RenderQuality = RenderQuality.HIGH
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_mb: Optional[float] = None
    render_started_at: Optional[datetime] = None
    render_completed_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    is_public: bool = False

class ProjectCreate(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    render_quality: RenderQuality = RenderQuality.HIGH

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    render_quality: Optional[RenderQuality] = None
    is_public: Optional[bool] = None

class RenderRequest(BaseModel):
    project_id: str
    template_id: str
    parameters: Dict[str, Any]
    render_quality: RenderQuality
    user_id: str