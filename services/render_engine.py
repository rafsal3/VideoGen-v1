import httpx
import asyncio
from typing import Dict, Any
from decouple import config
import uuid
from datetime import datetime

RENDER_ENGINE_URL = config("RENDER_ENGINE_URL", default="http://localhost:9000/render")
VIDEO_STORAGE_URL = config("VIDEO_STORAGE_URL", default="https://your-cdn.com/videos")

class RenderEngine:
    @staticmethod
    async def submit_render_job(project_id: str, template_id: str, parameters: Dict[str, Any], 
                              render_quality: str, user_id: str) -> Dict[str, Any]:
        """Submit a render job to the render engine"""
        
        render_payload = {
            "project_id": project_id,
            "template_id": template_id,
            "parameters": parameters,
            "quality": render_quality,
            "user_id": user_id,
            "callback_url": f"http://localhost:8000/projects/render-callback/{project_id}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(RENDER_ENGINE_URL, json=render_payload)
                response.raise_for_status()
                
                result = response.json()
                return {
                    "success": True,
                    "job_id": result.get("job_id"),
                    "estimated_duration": result.get("estimated_duration", 300),  # 5 minutes default
                    "message": "Render job submitted successfully"
                }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Render engine error: {str(e)}",
                "job_id": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "job_id": None
            }
    
    @staticmethod
    async def get_render_status(job_id: str) -> Dict[str, Any]:
        """Get the status of a render job"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{RENDER_ENGINE_URL}/status/{job_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    @staticmethod
    def generate_video_url(project_id: str, file_name: str) -> str:
        """Generate the final video URL"""
        return f"{VIDEO_STORAGE_URL}/{project_id}/{file_name}"
    
    @staticmethod
    async def mock_render_job(project_id: str) -> Dict[str, Any]:
        """Mock render job for development/testing"""
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Generate mock video URL
        video_filename = f"{project_id}_{uuid.uuid4().hex[:8]}.mp4"
        video_url = RenderEngine.generate_video_url(project_id, video_filename)
        
        return {
            "success": True,
            "video_url": video_url,
            "thumbnail_url": f"{video_url.replace('.mp4', '_thumb.jpg')}",
            "duration_seconds": 30,
            "file_size_mb": 15.5
        }