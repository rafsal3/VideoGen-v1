from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import List, Optional
from models.project import Project, ProjectCreate, ProjectUpdate, ProjectStatus, RenderRequest
from models.user import User
from models.template import Template
from database.connection import project_collection, template_collection
from routes.auth import get_current_user
from services.render_engine import RenderEngine
from datetime import datetime
from bson import ObjectId
import uuid

router = APIRouter()

async def get_project_with_template(project_dict: dict) -> dict:
    """Enrich project data with template information"""
    template = await template_collection.find_one({"template_id": project_dict["template_id"]})
    if template:
        project_dict["template_info"] = {
            "name": template["name"],
            "category": template["category"],
            "thumbnail_url": template.get("thumbnail_url")
        }
    return project_dict

@router.post("/", response_model=dict)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    """Create a new project"""
    # Verify template exists
    template = await template_collection.find_one({
        "template_id": project_data.template_id,
        "is_active": True
    })
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Generate project ID
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    
    # Create project
    project = Project(
        project_id=project_id,
        user_id=current_user.username,
        **project_data.dict()
    )
    
    result = await project_collection.insert_one(project.dict())
    
    return {
        "message": "Project created successfully",
        "project_id": project_id,
        "_id": str(result.inserted_id)
    }

@router.get("/", response_model=List[dict])
async def get_user_projects(current_user: User = Depends(get_current_user)):
    """Get all projects for the current user"""
    projects = []
    
    async for project in project_collection.find({"user_id": current_user.username}).sort("created_at", -1):
        project["_id"] = str(project["_id"])
        project_with_template = await get_project_with_template(project)
        projects.append(project_with_template)
    
    return projects

@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific project"""
    project = await project_collection.find_one({
        "project_id": project_id,
        "user_id": current_user.username
    })
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project["_id"] = str(project["_id"])
    return await get_project_with_template(project)

@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a project"""
    # Check if project exists and belongs to user
    existing_project = await project_collection.find_one({
        "project_id": project_id,
        "user_id": current_user.username
    })
    
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Prepare update data
    update_data = {k: v for k, v in project_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Update project
    await project_collection.update_one(
        {"project_id": project_id, "user_id": current_user.username},
        {"$set": update_data}
    )
    
    return {"message": "Project updated successfully"}

@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Delete a project"""
    result = await project_collection.delete_one({
        "project_id": project_id,
        "user_id": current_user.username
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {"message": "Project deleted successfully"}

async def process_render_job(project_id: str, user_id: str):
    """Background task to process render job"""
    try:
        # Update status to processing
        await project_collection.update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "status": ProjectStatus.PROCESSING,
                    "render_started_at": datetime.utcnow()
                }
            }
        )
        
        # For development, use mock render
        render_result = await RenderEngine.mock_render_job(project_id)
        
        if render_result["success"]:
            # Update project with video URL and completion status
            await project_collection.update_one(
                {"project_id": project_id},
                {
                    "$set": {
                        "status": ProjectStatus.COMPLETED,
                        "video_url": render_result["video_url"],
                        "thumbnail_url": render_result["thumbnail_url"],
                        "duration_seconds": render_result["duration_seconds"],
                        "file_size_mb": render_result["file_size_mb"],
                        "render_completed_at": datetime.utcnow()
                    }
                }
            )
        else:
            # Mark as failed
            await project_collection.update_one(
                {"project_id": project_id},
                {
                    "$set": {
                        "status": ProjectStatus.FAILED,
                        "render_completed_at": datetime.utcnow()
                    }
                }
            )
    
    except Exception as e:
        # Mark as failed on exception
        await project_collection.update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "status": ProjectStatus.FAILED,
                    "render_completed_at": datetime.utcnow()
                }
            }
        )

@router.post("/{project_id}/render", response_model=dict)
async def render_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Start rendering a project"""
    # Get project
    project = await project_collection.find_one({
        "project_id": project_id,
        "user_id": current_user.username
    })
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project["status"] == ProjectStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is already being processed"
        )
    
    # Add render job to background tasks
    background_tasks.add_task(process_render_job, project_id, current_user.username)
    
    return {
        "message": "Render job started",
        "project_id": project_id,
        "status": "processing"
    }

@router.get("/{project_id}/status", response_model=dict)
async def get_render_status(project_id: str, current_user: User = Depends(get_current_user)):
    """Get the render status of a project"""
    project = await project_collection.find_one({
        "project_id": project_id,
        "user_id": current_user.username
    })
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return {
        "project_id": project_id,
        "status": project["status"],
        "video_url": project.get("video_url"),
        "render_started_at": project.get("render_started_at"),
        "render_completed_at": project.get("render_completed_at"),
        "duration_seconds": project.get("duration_seconds"),
        "file_size_mb": project.get("file_size_mb")
    }

@router.post("/render-callback/{project_id}")
async def render_callback(project_id: str, callback_data: dict):
    """Callback endpoint for render engine to report completion"""
    try:
        if callback_data.get("success"):
            await project_collection.update_one(
                {"project_id": project_id},
                {
                    "$set": {
                        "status": ProjectStatus.COMPLETED,
                        "video_url": callback_data.get("video_url"),
                        "thumbnail_url": callback_data.get("thumbnail_url"),
                        "duration_seconds": callback_data.get("duration_seconds"),
                        "file_size_mb": callback_data.get("file_size_mb"),
                        "render_completed_at": datetime.utcnow()
                    }
                }
            )
        else:
            await project_collection.update_one(
                {"project_id": project_id},
                {
                    "$set": {
                        "status": ProjectStatus.FAILED,
                        "render_completed_at": datetime.utcnow()
                    }
                }
            )
        
        return {"message": "Callback processed successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process callback: {str(e)}"
        )

@router.get("/public/showcase", response_model=List[dict])
async def get_public_projects():
    """Get public projects for showcase"""
    projects = []
    
    async for project in project_collection.find({
        "is_public": True,
        "status": ProjectStatus.COMPLETED
    }).sort("created_at", -1).limit(20):
        project["_id"] = str(project["_id"])
        # Remove sensitive user data
        project.pop("user_id", None)
        project_with_template = await get_project_with_template(project)
        projects.append(project_with_template)
    
    return projects