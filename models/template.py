from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class Template(BaseModel):
    template_id: str
    name: str
    description: Optional[str] = None
    category: str
    parameters_schema: Dict[str, Any]  # Schema defining required parameters
    preview_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    resolution: Optional[str] = "1920x1080"
    created_at: datetime = datetime.utcnow()
    is_premium: bool = False
    is_active: bool = True
    render_engine: str = "default"  # Which render engine to use
    tags: List[str] = []

class SavedTemplate(BaseModel):
    user_id: str
    template_id: str
    saved_at: datetime = datetime.utcnow()

class TemplateResponse(Template):
    is_saved: Optional[bool] = False  # Whether current user has saved this template
    total_saves: Optional[int] = 0    # Total number of saves