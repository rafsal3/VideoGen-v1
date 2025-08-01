import aiohttp
import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RenderEngineClient:
    """Client to communicate with the separate render engine backend"""
    
    def __init__(self):
        # Configuration - adjust these based on your setup
        self.render_engine_base_url = config("RENDER_ENGINE_URL", default="http://localhost:8001")
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
        self.max_retries = 3
        self.retry_delay = 5  # seconds
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to render engine with retry logic"""
        url = f"{self.render_engine_base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    if method.upper() == "POST":
                        async with session.post(url, json=data) as response:
                            if response.status == 202:  # Accepted for rendering
                                return await response.json()
                            elif response.status >= 400:
                                error_text = await response.text()
                                raise Exception(f"Render engine error {response.status}: {error_text}")
                    
                    elif method.upper() == "GET":
                        async with session.get(url) as response:
                            if response.status == 200:
                                return await response.json()
                            elif response.status == 404:
                                return {"status": "not_found"}
                            elif response.status >= 400:
                                error_text = await response.text()
                                raise Exception(f"Render engine error {response.status}: {error_text}")

                    elif method.upper() == "HEAD":
                        async with session.head(url) as response:
                            if response.status == 200:
                                return {"status": "ready"}
                            elif response.status == 404:
                                return {"status": "not_found"}
                            else:
                                raise Exception(f"Render engine status check failed with status {response.status}")
                                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == self.max_retries - 1:
                    raise Exception("Render engine request timeout after all retries")
                await asyncio.sleep(self.retry_delay)
                
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1} for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
    
    async def start_render_job(self, template_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start a render job on the render engine"""
        try:
            logger.info(f"Starting render job for template: {template_name}")
            
            # Map template_id to template_name for render engine
            template_mapping = {
                "tmpl-newspaper": "text_reveal",
                "tmpl-social-story": "text_reveal",
                "tmpl-corporate-intro": "text_reveal",
                "tmpl-wedding-announcement": "text_reveal",
                # Add the new template to the mapping
                "text-reveal": "text_reveal"
            }
            
            render_template_name = template_mapping.get(template_name, "text_reveal")
            
            # Transform parameters to match render engine expectations
            render_parameters = self._transform_parameters(template_name, parameters)
            
            endpoint = f"/render/{render_template_name}"
            response = await self._make_request("POST", endpoint, render_parameters)
            
            logger.info(f"Render job started successfully: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to start render job: {str(e)}")
            raise Exception(f"Render engine communication failed: {str(e)}")
    
    def _transform_parameters(self, template_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Transform parameters from standard backend format to render engine format"""
        
        # --- ADD THIS NEW CONDITION ---
        if template_id == "text-reveal":
            return {
                "text": parameters.get("text", "Default Text"),
                "speed": parameters.get("speed", 0.1),
                "font_name": parameters.get("font", "Arial"),
                "font_size": parameters.get("font_size", 48),
                "font_color": parameters.get("font_color", "#FF0000"),
                "bg_color": parameters.get("background_color", "#FFFFFF"),
                "duration": parameters.get("duration", 5.0),
                "resolution": "1920x1080" # Assuming a default resolution
            }
        # -----------------------------

        elif template_id == "tmpl-newspaper":
            return {
                "text": parameters.get("headline", "Breaking News"),
                "speed": 0.1, "font_name": "Arial", "font_size": 24,
                "font_color": parameters.get("theme_color", "#FF0000"),
                "bg_color": "#FFFFFF", "duration": 30.0,
                "resolution": "1920x1080"
            }
        elif template_id == "tmpl-social-story":
            return {
                "text": parameters.get("text", "Social Story"),
                "speed": 0.15, "font_name": "Arial", "font_size": 20,
                "font_color": "#FFFFFF",
                "bg_color": parameters.get("overlay_color", "#000000"),
                "duration": 15.0,
                "resolution": "1080x1920"
            }
        elif template_id == "tmpl-corporate-intro":
            return {
                "text": parameters.get("company_name", "Company"),
                "speed": 0.08, "font_name": "Arial", "font_size": 28,
                "font_color": parameters.get("primary_color", "#0066CC"),
                "bg_color": parameters.get("secondary_color", "#FFFFFF"),
                "duration": 20.0,
                "resolution": "1920x1080"
            }
        elif template_id == "tmpl-wedding-announcement":
            bride = parameters.get("bride_name", "")
            groom = parameters.get("groom_name", "")
            text = f"{bride} & {groom}"
            return {
                "text": text, "speed": 0.12, "font_name": "Arial", "font_size": 26,
                "font_color": parameters.get("theme_color", "#FFD700"),
                "bg_color": "#FFFFFF", "duration": 25.0,
                "resolution": "1920x1080"
            }
        else:
            # This block should now only be a fallback
            return {
                "text": "Default Text", "speed": 0.1, "font_name": "Arial",
                "font_size": 24, "font_color": "#000000",
                "bg_color": "#FFFFFF", "duration": 30.0,
                "resolution": "1920x1080"
            }
    
    async def check_render_status(self, filename: str) -> Dict[str, Any]:
        """Check if a rendered video is ready using a HEAD request"""
        try:
            endpoint = f"/videos/{filename}"
            response = await self._make_request("HEAD", endpoint)
            return response
        except Exception as e:
            logger.error(f"Failed to check render status: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_available_templates(self) -> Dict[str, Any]:
        """Get list of available templates from render engine"""
        try:
            response = await self._make_request("GET", "/")
            return response
        except Exception as e:
            logger.error(f"Failed to get available templates: {str(e)}")
            return {"available_templates": []}

class RenderEngine:
    """Updated render engine service that communicates with actual render engine backend"""
    
    _client = None
    
    @classmethod
    def get_client(cls) -> RenderEngineClient:
        """Get or create the render engine client"""
        if cls._client is None:
            cls._client = RenderEngineClient()
        return cls._client
    
    @classmethod
    async def start_render_job(cls, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a render job using the actual render engine"""
        try:
            client = cls.get_client()
            
            template_id = project_data.get("template_id")
            parameters = project_data.get("parameters", {})
            project_id = project_data.get("project_id")
            
            logger.info(f"Starting render for project {project_id} with template {template_id}")
            
            render_response = await client.start_render_job(template_id, parameters)
            
            if render_response:
                return {
                    "success": True,
                    "render_job_id": render_response.get("filename", f"{project_id}.mp4"),
                    "download_url": render_response.get("download_url"),
                    "message": render_response.get("message", "Render started"),
                    "estimated_completion": "2-3 minutes"
                }
            else:
                return {"success": False, "error": "Failed to start render job"}
                
        except Exception as e:
            logger.error(f"Render job failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    async def check_render_completion(cls, render_job_id: str) -> Dict[str, Any]:
        """Check if render job is completed and get the video URL"""
        try:
            client = cls.get_client()
            
            status_response = await client.check_render_status(render_job_id)
            
            if status_response.get("status") == "ready":
                return {
                    "completed": True,
                    "success": True,
                    "video_url": f"{client.render_engine_base_url}/videos/{render_job_id}",
                    "thumbnail_url": f"{client.render_engine_base_url}/videos/{render_job_id.replace('.mp4', '.jpg')}",
                    "duration_seconds": 30,
                    "file_size_mb": 2.5
                }
            else:
                return {
                    "completed": False,
                    "status": "rendering"
                }
                
        except Exception as e:
            logger.error(f"Failed to check render completion: {str(e)}")
            return {"completed": True, "success": False, "error": str(e)}
    
    @classmethod
    async def mock_render_job(cls, project_id: str) -> Dict[str, Any]:
        """Keep the mock method for backward compatibility during testing"""
        return {
            "success": True,
            "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "duration_seconds": 30,
            "file_size_mb": 2.5
        }