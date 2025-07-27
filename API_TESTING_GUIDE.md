# Video Template Platform API - Testing Guide

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require authentication. Use the Bearer token from the login endpoint.

## 1. Authentication Endpoints

### 1.1 Register User
**POST** `/auth/register`

**Request Body:**
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "testpassword123",
  "full_name": "Test User"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

### 1.2 Login User
**POST** `/auth/login`

**Request Body (form-data):**
```
username: testuser
password: testpassword123
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 1.3 Get Current User
**GET** `/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "saved_templates": [],
  "created_at": "2024-01-15T10:30:00"
}
```

## 2. Template Endpoints

### 2.1 Get All Templates
**GET** `/templates/`

**Headers (optional):**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "template_id": "tmpl-newspaper",
    "name": "Breaking News Template",
    "description": "Classic newspaper style breaking news template",
    "category": "News",
    "parameters_schema": {
      "headline": {"type": "string", "required": true, "max_length": 100},
      "subheadline": {"type": "string", "required": true, "max_length": 200},
      "image_url": {"type": "url", "required": true},
      "theme_color": {"type": "color", "required": true, "default": "#FF0000"},
      "reporter_name": {"type": "string", "required": false, "default": "News Team"}
    },
    "preview_url": "https://example.com/preview-newspaper.mp4",
    "thumbnail_url": "https://example.com/thumb-newspaper.jpg",
    "duration_seconds": 30,
    "resolution": "1920x1080",
    "created_at": "2024-01-15T10:30:00",
    "is_premium": false,
    "is_active": true,
    "render_engine": "news_engine",
    "tags": ["news", "breaking", "broadcast", "professional"],
    "is_saved": false,
    "total_saves": 5
  }
]
```

### 2.2 Get Template Categories
**GET** `/templates/categories`

**Response:**
```json
{
  "categories": ["News", "Social", "Business", "Events"]
}
```

### 2.3 Get Templates by Category
**GET** `/templates/category/{category}`

**Example:** `/templates/category/News`

**Headers (optional):**
```
Authorization: Bearer <access_token>
```

### 2.4 Get Template by ID
**GET** `/templates/{template_id}`

**Example:** `/templates/tmpl-newspaper`

**Headers (optional):**
```
Authorization: Bearer <access_token>
```

### 2.5 Save Template
**POST** `/templates/{template_id}/save`

**Example:** `/templates/tmpl-newspaper/save`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Template saved successfully"
}
```

### 2.6 Unsave Template
**DELETE** `/templates/{template_id}/unsave`

**Example:** `/templates/tmpl-newspaper/unsave`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Template unsaved successfully"
}
```

### 2.7 Get Saved Templates
**GET** `/templates/saved/my-templates`

**Headers:**
```
Authorization: Bearer <access_token>
```

### 2.8 Search Templates
**GET** `/templates/search/{query}`

**Example:** `/templates/search/news`

**Headers (optional):**
```
Authorization: Bearer <access_token>
```

## 3. Project Endpoints

### 3.1 Create Project
**POST** `/projects/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "template_id": "tmpl-newspaper",
  "name": "My Breaking News Video",
  "description": "A breaking news video about local events",
  "parameters": {
    "headline": "Breaking: Major Event in City",
    "subheadline": "Local authorities respond to emergency situation",
    "image_url": "https://example.com/news-image.jpg",
    "theme_color": "#FF0000",
    "reporter_name": "John Smith"
  },
  "render_quality": "1080p"
}
```

**Response:**
```json
{
  "message": "Project created successfully",
  "project_id": "proj_abc123def456",
  "_id": "507f1f77bcf86cd799439011"
}
```

### 3.2 Get User Projects
**GET** `/projects/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "project_id": "proj_abc123def456",
    "user_id": "testuser",
    "template_id": "tmpl-newspaper",
    "name": "My Breaking News Video",
    "description": "A breaking news video about local events",
    "parameters": {
      "headline": "Breaking: Major Event in City",
      "subheadline": "Local authorities respond to emergency situation",
      "image_url": "https://example.com/news-image.jpg",
      "theme_color": "#FF0000",
      "reporter_name": "John Smith"
    },
    "status": "draft",
    "render_quality": "1080p",
    "video_url": null,
    "thumbnail_url": null,
    "duration_seconds": null,
    "file_size_mb": null,
    "render_started_at": null,
    "render_completed_at": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "is_public": false,
    "template_info": {
      "name": "Breaking News Template",
      "category": "News",
      "thumbnail_url": "https://example.com/thumb-newspaper.jpg"
    }
  }
]
```

### 3.3 Get Project by ID
**GET** `/projects/{project_id}`

**Example:** `/projects/proj_abc123def456`

**Headers:**
```
Authorization: Bearer <access_token>
```

### 3.4 Update Project
**PUT** `/projects/{project_id}`

**Example:** `/projects/proj_abc123def456`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Updated Breaking News Video",
  "description": "Updated description",
  "parameters": {
    "headline": "Updated: Major Event in City",
    "subheadline": "Updated subheadline",
    "image_url": "https://example.com/updated-image.jpg",
    "theme_color": "#FF0000",
    "reporter_name": "John Smith"
  },
  "render_quality": "4k",
  "is_public": true
}
```

**Response:**
```json
{
  "message": "Project updated successfully"
}
```

### 3.5 Delete Project
**DELETE** `/projects/{project_id}`

**Example:** `/projects/proj_abc123def456`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

### 3.6 Render Project
**POST** `/projects/{project_id}/render`

**Example:** `/projects/proj_abc123def456/render`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Render job started",
  "project_id": "proj_abc123def456",
  "status": "processing"
}
```

### 3.7 Get Render Status
**GET** `/projects/{project_id}/status`

**Example:** `/projects/proj_abc123def456/status`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "project_id": "proj_abc123def456",
  "status": "completed",
  "video_url": "https://example.com/videos/proj_abc123def456.mp4",
  "render_started_at": "2024-01-15T10:35:00",
  "render_completed_at": "2024-01-15T10:40:00",
  "duration_seconds": 30,
  "file_size_mb": 15.5
}
```

### 3.8 Get Public Projects (Showcase)
**GET** `/projects/public/showcase`

**Response:**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "project_id": "proj_abc123def456",
    "template_id": "tmpl-newspaper",
    "name": "Public Breaking News Video",
    "description": "A public breaking news video",
    "parameters": {
      "headline": "Breaking: Major Event in City",
      "subheadline": "Local authorities respond to emergency situation",
      "image_url": "https://example.com/news-image.jpg",
      "theme_color": "#FF0000",
      "reporter_name": "John Smith"
    },
    "status": "completed",
    "render_quality": "1080p",
    "video_url": "https://example.com/videos/proj_abc123def456.mp4",
    "thumbnail_url": "https://example.com/thumbnails/proj_abc123def456.jpg",
    "duration_seconds": 30,
    "file_size_mb": 15.5,
    "render_started_at": "2024-01-15T10:35:00",
    "render_completed_at": "2024-01-15T10:40:00",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "is_public": true,
    "template_info": {
      "name": "Breaking News Template",
      "category": "News",
      "thumbnail_url": "https://example.com/thumb-newspaper.jpg"
    }
  }
]
```

## 4. Debug Endpoints

### 4.1 Activate Templates
**POST** `/debug/activate-templates`

**Response:**
```json
{
  "message": "Activated 4 templates",
  "modified_count": 4
}
```

### 4.2 Get Template Status
**GET** `/debug/template-status`

**Response:**
```json
{
  "total_templates": 4,
  "active_templates": 4,
  "templates": [
    {
      "template_id": "tmpl-newspaper",
      "name": "Breaking News Template",
      "is_active": true
    },
    {
      "template_id": "tmpl-social-story",
      "name": "Social Media Story",
      "is_active": true
    },
    {
      "template_id": "tmpl-corporate-intro",
      "name": "Corporate Introduction",
      "is_active": true
    },
    {
      "template_id": "tmpl-wedding-announcement",
      "name": "Wedding Announcement",
      "is_active": true
    }
  ]
}
```

## 5. General Endpoints

### 5.1 Root Endpoint
**GET** `/`

**Response:**
```json
{
  "message": "Welcome to Video Template Platform API v2.0"
}
```

### 5.2 Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 6. Testing Workflow

### Step 1: Start the Server
```bash
cd backend
python main.py
```

### Step 2: Test Authentication
1. Register a new user
2. Login to get access token
3. Test getting current user

### Step 3: Test Templates
1. Get all templates
2. Get templates by category
3. Get specific template
4. Search templates
5. Save/unsave templates (requires authentication)

### Step 4: Test Projects
1. Create a new project
2. Get user projects
3. Update project
4. Start rendering
5. Check render status
6. Delete project

### Step 5: Test Debug Endpoints
1. Check template status
2. Activate templates if needed

## 7. Sample Test Data

### User Registration Data
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "testpassword123",
  "full_name": "Test User"
}
```

### Project Creation Data
```json
{
  "template_id": "tmpl-newspaper",
  "name": "Breaking News Video",
  "description": "A breaking news video about local events",
  "parameters": {
    "headline": "Breaking: Major Event in City",
    "subheadline": "Local authorities respond to emergency situation",
    "image_url": "https://example.com/news-image.jpg",
    "theme_color": "#FF0000",
    "reporter_name": "John Smith"
  },
  "render_quality": "1080p"
}
```

### Social Media Project Data
```json
{
  "template_id": "tmpl-social-story",
  "name": "Instagram Story Video",
  "description": "A trendy social media story",
  "parameters": {
    "text": "Amazing sunset at the beach!",
    "background_image": "https://example.com/sunset.jpg",
    "overlay_color": "#000000",
    "opacity": 0.5,
    "font_style": "modern"
  },
  "render_quality": "720p"
}
```

### Corporate Project Data
```json
{
  "template_id": "tmpl-corporate-intro",
  "name": "Company Introduction Video",
  "description": "Professional company introduction",
  "parameters": {
    "company_name": "TechCorp Solutions",
    "tagline": "Innovating for tomorrow",
    "logo_url": "https://example.com/logo.png",
    "primary_color": "#0066CC",
    "secondary_color": "#FFFFFF",
    "animation_style": "fade"
  },
  "render_quality": "4k"
}
```

## 8. Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Template not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Username or email already registered"
}
```

## 9. Tools for Testing

### Using curl
```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass","full_name":"Test User"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Get templates (with token)
curl -X GET "http://localhost:8000/templates/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman
1. Import the endpoints
2. Set up environment variables for base URL and tokens
3. Use the test data provided above

### Using Python requests
```python
import requests

base_url = "http://localhost:8000"

# Register
response = requests.post(f"{base_url}/auth/register", json={
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass",
    "full_name": "Test User"
})

# Login
response = requests.post(f"{base_url}/auth/login", data={
    "username": "testuser",
    "password": "testpass"
})
token = response.json()["access_token"]

# Get templates
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{base_url}/templates/", headers=headers)
``` 