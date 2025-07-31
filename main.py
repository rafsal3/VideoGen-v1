from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, templates, projects
from database.connection import database
from datetime import datetime

app = FastAPI(
    title="Video Template Platform API",
    description="API for managing video templates, user authentication, and video projects",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://videogen01.netlify.app"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Video Template Platform API v2.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/debug/activate-templates")
async def activate_templates():
    """Debug endpoint to activate all templates"""
    from database.connection import template_collection
    
    result = await template_collection.update_many(
        {},  # Update all documents
        {"$set": {"is_active": True}}
    )
    
    return {
        "message": f"Activated {result.modified_count} templates",
        "modified_count": result.modified_count
    }

@app.get("/debug/template-status")
async def get_template_status():
    """Debug endpoint to check template status"""
    from database.connection import template_collection
    
    total_count = await template_collection.count_documents({})
    active_count = await template_collection.count_documents({"is_active": True})
    
    templates = []
    async for template in template_collection.find({}, {"template_id": 1, "name": 1, "is_active": 1}):
        templates.append({
            "template_id": template["template_id"],
            "name": template["name"],
            "is_active": template.get("is_active", False)
        })
    
    return {
        "total_templates": total_count,
        "active_templates": active_count,
        "templates": templates
    }

# Startup event to create sample data
@app.on_event("startup")
async def startup_event():
    # Create sample templates if none exist
    from database.connection import template_collection
    
    # Check if templates exist and are active
    active_count = await template_collection.count_documents({"is_active": True})
    total_count = await template_collection.count_documents({})
    
    print(f"Found {total_count} templates, {active_count} are active")
    
    if total_count == 0:
        sample_templates = [
            {
                "template_id": "tmpl-newspaper",
                "name": "Breaking News Template",
                "description": "Classic newspaper style breaking news template",
                "category": "News",
                "parameters_schema": {
                    "headline": {"type": "string", "required": True, "max_length": 100},
                    "subheadline": {"type": "string", "required": True, "max_length": 200},
                    "image_url": {"type": "url", "required": True},
                    "theme_color": {"type": "color", "required": True, "default": "#FF0000"},
                    "reporter_name": {"type": "string", "required": False, "default": "News Team"}
                },
                "preview_url": "https://example.com/preview-newspaper.mp4",
                "thumbnail_url": "https://example.com/thumb-newspaper.jpg",
                "duration_seconds": 30,
                "resolution": "1920x1080",
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "is_active": True,
                "render_engine": "news_engine",
                "tags": ["news", "breaking", "broadcast", "professional"]
            },
            {
                "template_id": "tmpl-social-story",
                "name": "Social Media Story",
                "description": "Trendy social media story template with animations",
                "category": "Social",
                "parameters_schema": {
                    "text": {"type": "string", "required": True, "max_length": 150},
                    "background_image": {"type": "url", "required": True},
                    "overlay_color": {"type": "color", "required": True, "default": "#000000"},
                    "opacity": {"type": "number", "required": True, "min": 0.0, "max": 1.0, "default": 0.5},
                    "font_style": {"type": "enum", "options": ["modern", "classic", "bold"], "default": "modern"}
                },
                "preview_url": "https://example.com/preview-social.mp4",
                "thumbnail_url": "https://example.com/thumb-social.jpg",
                "duration_seconds": 15,
                "resolution": "1080x1920",
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "is_active": True,
                "render_engine": "social_engine",
                "tags": ["social", "story", "instagram", "trendy", "vertical"]
            },
            {
                "template_id": "tmpl-corporate-intro",
                "name": "Corporate Introduction",
                "description": "Professional corporate introduction template with modern design",
                "category": "Business",
                "parameters_schema": {
                    "company_name": {"type": "string", "required": True, "max_length": 100},
                    "tagline": {"type": "string", "required": True, "max_length": 200},
                    "logo_url": {"type": "url", "required": True},
                    "primary_color": {"type": "color", "required": True, "default": "#0066CC"},
                    "secondary_color": {"type": "color", "required": True, "default": "#FFFFFF"},
                    "animation_style": {"type": "enum", "options": ["fade", "slide", "zoom"], "default": "fade"}
                },
                "preview_url": "https://example.com/preview-corporate.mp4",
                "thumbnail_url": "https://example.com/thumb-corporate.jpg",
                "duration_seconds": 20,
                "resolution": "1920x1080",
                "created_at": datetime.utcnow(),
                "is_premium": True,
                "is_active": True,
                "render_engine": "corporate_engine",
                "tags": ["corporate", "business", "professional", "introduction", "modern"]
            },
            {
                "template_id": "tmpl-wedding-announcement",
                "name": "Wedding Announcement",
                "description": "Elegant wedding announcement template with romantic styling",
                "category": "Events",
                "parameters_schema": {
                    "bride_name": {"type": "string", "required": True, "max_length": 50},
                    "groom_name": {"type": "string", "required": True, "max_length": 50},
                    "wedding_date": {"type": "date", "required": True},
                    "venue": {"type": "string", "required": True, "max_length": 100},
                    "theme_color": {"type": "color", "required": True, "default": "#FFD700"},
                    "background_image": {"type": "url", "required": True},
                    "music_style": {"type": "enum", "options": ["romantic", "classical", "modern"], "default": "romantic"}
                },
                "preview_url": "https://example.com/preview-wedding.mp4",
                "thumbnail_url": "https://example.com/thumb-wedding.jpg",
                "duration_seconds": 25,
                "resolution": "1920x1080",
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "is_active": True,
                "render_engine": "wedding_engine",
                "tags": ["wedding", "romantic", "elegant", "celebration", "love"]
            }
        ]
        
        # Insert sample templates
        await template_collection.insert_many(sample_templates)
        print(f"Created {len(sample_templates)} sample templates")
    elif active_count == 0:
        # If templates exist but none are active, activate them
        result = await template_collection.update_many(
            {},  # Update all documents
            {"$set": {"is_active": True}}
        )
        print(f"Activated {result.modified_count} existing templates")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)