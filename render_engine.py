import subprocess
import os
import tempfile
import json
from datetime import datetime
from typing import Dict, Any
import requests
from PIL import Image, ImageDraw, ImageFont
import uuid

class RealVideoRenderer:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = "generated_videos"  # Configure your output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def render_breaking_news_template(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the Breaking News Template (tmpl-newspaper) with real video generation
        """
        try:
            # Extract parameters from project data
            params = project_data.get("parameters", {})
            project_id = project_data.get("project_id")
            
            headline = params.get("headline", "Breaking News")
            subheadline = params.get("subheadline", "This is a developing story")
            image_url = params.get("image_url", "")
            theme_color = params.get("theme_color", "#FF0000")
            reporter_name = params.get("reporter_name", "News Team")
            
            # Generate unique filename
            video_filename = f"{project_id}_{uuid.uuid4().hex[:8]}.mp4"
            video_path = os.path.join(self.output_dir, video_filename)
            
            # Create background image with news layout
            background_path = await self._create_news_background(
                headline, subheadline, image_url, theme_color, reporter_name
            )
            
            # Generate video using FFmpeg
            await self._generate_video_with_ffmpeg(background_path, video_path)
            
            # Get video info
            duration = 30  # Fixed duration for news template
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # Size in MB
            
            # Generate thumbnail
            thumbnail_path = await self._generate_thumbnail(video_path, project_id)
            
            return {
                "success": True,
                "video_url": f"/videos/{video_filename}",  # Adjust based on your static file serving
                "thumbnail_url": f"/thumbnails/{project_id}_thumb.jpg",
                "duration_seconds": duration,
                "file_size_mb": round(file_size, 2)
            }
            
        except Exception as e:
            print(f"Error rendering video: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_news_background(self, headline: str, subheadline: str, 
                                    image_url: str, theme_color: str, reporter_name: str) -> str:
        """Create a news-style background image"""
        
        # Create canvas (1920x1080)
        width, height = 1920, 1080
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        try:
            # Load fonts (you'll need to have these fonts or use default)
            title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 80)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 50)
            reporter_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 30)
        except:
            # Fallback to default font if custom fonts not available
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            reporter_font = ImageFont.load_default()
        
        # Draw red news banner
        banner_height = 200
        draw.rectangle([0, 0, width, banner_height], fill=theme_color)
        
        # Add "BREAKING NEWS" text
        breaking_text = "BREAKING NEWS"
        bbox = draw.textbbox((0, 0), breaking_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, 20), breaking_text, font=title_font, fill='white')
        
        # Add headline
        headline_y = banner_height + 50
        headline_lines = self._wrap_text(headline, title_font, width - 100)
        for i, line in enumerate(headline_lines[:2]):  # Max 2 lines
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, headline_y + i * 90), line, font=title_font, fill='white')
        
        # Add subheadline
        subheadline_y = headline_y + len(headline_lines) * 90 + 50
        subheadline_lines = self._wrap_text(subheadline, subtitle_font, width - 100)
        for i, line in enumerate(subheadline_lines[:3]):  # Max 3 lines
            bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, subheadline_y + i * 60), line, font=subtitle_font, fill='#cccccc')
        
        # Add reporter name at bottom
        reporter_text = f"Reported by: {reporter_name}"
        draw.text((50, height - 100), reporter_text, font=reporter_font, fill='#888888')
        
        # Download and add background image if provided
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                        tmp_file.write(response.content)
                        bg_image = Image.open(tmp_file.name)
                        
                        # Resize and blend background image
                        bg_image = bg_image.resize((width, height))
                        # Create semi-transparent overlay
                        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 128))
                        bg_image = Image.alpha_composite(bg_image.convert('RGBA'), overlay)
                        
                        # Paste on main image with low opacity
                        img = Image.alpha_composite(img.convert('RGBA'), bg_image).convert('RGB')
            except Exception as e:
                print(f"Could not load background image: {e}")
        
        # Save background image
        bg_path = os.path.join(self.temp_dir, f"bg_{uuid.uuid4().hex[:8]}.jpg")
        img.save(bg_path, 'JPEG', quality=95)
        
        return bg_path
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    async def _generate_video_with_ffmpeg(self, background_path: str, output_path: str):
        """Generate video using FFmpeg with animations"""
        
        # FFmpeg command to create animated video
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-loop', '1',  # Loop the input image
            '-i', background_path,  # Input background image
            '-c:v', 'libx264',  # Video codec
            '-t', '30',  # Duration in seconds
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-vf', 'scale=1920:1080,fade=in:0:30,fade=out:870:30',  # Add fade effects
            '-r', '30',  # Frame rate
            '-crf', '23',  # Quality (lower = better quality)
            output_path
        ]
        
        # Run FFmpeg command
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {process.stderr}")
    
    async def _generate_thumbnail(self, video_path: str, project_id: str) -> str:
        """Generate thumbnail from video"""
        thumbnail_filename = f"{project_id}_thumb.jpg"
        thumbnail_path = os.path.join("thumbnails", thumbnail_filename)
        os.makedirs("thumbnails", exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-ss', '5',  # Take frame at 5 seconds
            '-vframes', '1',  # Extract 1 frame
            '-vf', 'scale=320:180',  # Thumbnail size
            thumbnail_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        return thumbnail_path

# Updated render engine service
class RenderEngine:
    _renderer = None
    
    @classmethod
    def get_renderer(cls):
        """Get or create the renderer instance"""
        if cls._renderer is None:
            cls._renderer = RealVideoRenderer()
        return cls._renderer
    
    @staticmethod
    async def mock_render_job(project_id: str):
        """Keep existing mock for other templates"""
        return {
            "success": True,
            "video_url": f"https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "thumbnail_url": f"https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "duration_seconds": 30,
            "file_size_mb": 2.5
        }
    
    # Make sure this method is indented to be inside the RenderEngine class
    @staticmethod
    async def render_real_video(project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Render real video based on template"""
        template_id = project_data.get("template_id")
        
        if template_id == "tmpl-newspaper":
            renderer = RenderEngine.get_renderer()
            return await renderer.render_breaking_news_template(project_data)
        else:
            # Fall back to mock for other templates
            return await RenderEngine.mock_render_job(project_data.get("project_id"))