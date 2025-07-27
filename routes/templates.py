from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models.template import Template, TemplateResponse, SavedTemplate
from models.user import User
from database.connection import template_collection, saved_templates_collection, user_collection
from routes.auth import get_current_user
from datetime import datetime

router = APIRouter()

async def get_template_with_user_data(template: dict, user_id: Optional[str] = None) -> TemplateResponse:
    """Add user-specific data to template"""
    template["_id"] = str(template["_id"])
    
    # Count total saves
    total_saves = await saved_templates_collection.count_documents({"template_id": template["template_id"]})
    template["total_saves"] = total_saves
    
    # Check if current user has saved this template
    if user_id:
        is_saved = await saved_templates_collection.find_one({
            "user_id": user_id,
            "template_id": template["template_id"]
        }) is not None
        template["is_saved"] = is_saved
    else:
        template["is_saved"] = False
    
    return TemplateResponse(**template)

@router.get("/", response_model=List[TemplateResponse])
async def get_all_templates(current_user: Optional[User] = Depends(get_current_user)):
    """Get all available templates with user-specific data"""
    templates = []
    user_id = current_user.username if current_user else None
    
    async for template in template_collection.find({"is_active": True}):
        template_with_data = await get_template_with_user_data(template, user_id)
        templates.append(template_with_data)
    
    return templates

@router.get("/categories")
async def get_template_categories():
    """Get all template categories"""
    categories = await template_collection.distinct("category", {"is_active": True})
    return {"categories": categories}

@router.get("/category/{category}", response_model=List[TemplateResponse])
async def get_templates_by_category(category: str, current_user: Optional[User] = Depends(get_current_user)):
    """Get templates by category"""
    templates = []
    user_id = current_user.username if current_user else None
    
    async for template in template_collection.find({"category": category, "is_active": True}):
        template_with_data = await get_template_with_user_data(template, user_id)
        templates.append(template_with_data)
    
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_by_id(template_id: str, current_user: Optional[User] = Depends(get_current_user)):
    """Get a specific template by ID"""
    template = await template_collection.find_one({"template_id": template_id, "is_active": True})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    user_id = current_user.username if current_user else None
    return await get_template_with_user_data(template, user_id)

@router.post("/{template_id}/save", response_model=dict)
async def save_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Save a template to user's collection"""
    # Check if template exists
    template = await template_collection.find_one({"template_id": template_id, "is_active": True})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if already saved
    existing = await saved_templates_collection.find_one({
        "user_id": current_user.username,
        "template_id": template_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template already saved"
        )
    
    # Save template
    saved_template = SavedTemplate(
        user_id=current_user.username,
        template_id=template_id
    )
    
    await saved_templates_collection.insert_one(saved_template.dict())
    
    # Update user's saved templates list
    await user_collection.update_one(
        {"username": current_user.username},
        {"$addToSet": {"saved_templates": template_id}}
    )
    
    return {"message": "Template saved successfully"}

@router.delete("/{template_id}/unsave", response_model=dict)
async def unsave_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Remove a template from user's saved collection"""
    result = await saved_templates_collection.delete_one({
        "user_id": current_user.username,
        "template_id": template_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found in saved collection"
        )
    
    # Update user's saved templates list
    await user_collection.update_one(
        {"username": current_user.username},
        {"$pull": {"saved_templates": template_id}}
    )
    
    return {"message": "Template unsaved successfully"}

@router.get("/saved/my-templates", response_model=List[TemplateResponse])
async def get_saved_templates(current_user: User = Depends(get_current_user)):
    """Get user's saved templates"""
    saved_templates = []
    
    # Get saved template IDs
    async for saved in saved_templates_collection.find({"user_id": current_user.username}):
        template = await template_collection.find_one({
            "template_id": saved["template_id"],
            "is_active": True
        })
        if template:
            template_with_data = await get_template_with_user_data(template, current_user.username)
            saved_templates.append(template_with_data)
    
    return saved_templates

@router.get("/search/{query}", response_model=List[TemplateResponse])
async def search_templates(query: str, current_user: Optional[User] = Depends(get_current_user)):
    """Search templates by name, description, or tags"""
    search_filter = {
        "is_active": True,
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"tags": {"$in": [query]}}
        ]
    }
    
    templates = []
    user_id = current_user.username if current_user else None
    
    async for template in template_collection.find(search_filter):
        template_with_data = await get_template_with_user_data(template, user_id)
        templates.append(template_with_data)
    
    return templates