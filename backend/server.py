from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import base64
import io
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone
from playwright.async_api import async_playwright
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="URL Screenshot API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    usage_count: int = 0

class APIKeyCreate(BaseModel):
    name: str

class ScreenshotOptions(BaseModel):
    width: Optional[int] = Field(default=1920, ge=100, le=4000)
    height: Optional[int] = Field(default=1080, ge=100, le=4000)
    fullPage: Optional[bool] = False
    delay: Optional[int] = Field(default=0, ge=0, le=30000)  # max 30 seconds
    format: Optional[Literal["png", "jpeg"]] = "png"
    quality: Optional[int] = Field(default=90, ge=1, le=100)  # Only for JPEG

class ScreenshotRequest(BaseModel):
    url: str
    options: Optional[ScreenshotOptions] = Field(default_factory=ScreenshotOptions)
    
    @validator('url')
    def validate_url(cls, v):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        return v

class ScreenshotResponse(BaseModel):
    status: str
    image: str
    format: str
    timestamp: datetime
    url: str

# Authentication dependency
async def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Check if API key exists and is active
    key_doc = await db.api_keys.find_one({"key": api_key, "is_active": True})
    if not key_doc:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    # Update usage count
    await db.api_keys.update_one(
        {"key": api_key},
        {"$inc": {"usage_count": 1}}
    )
    
    return APIKey(**key_doc)

# Screenshot service
class ScreenshotService:
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    async def initialize(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-web-security',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ]
            )
    
    async def take_screenshot(self, request: ScreenshotRequest) -> str:
        await self.initialize()
        
        # Create page with better settings for real websites
        page = await self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try:
            # Set viewport
            await page.set_viewport_size({
                "width": request.options.width,
                "height": request.options.height
            })
            
            # Add extra headers to appear more like a real browser
            await page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Upgrade-Insecure-Requests": "1",
            })
            
            # Navigate to URL with better error handling and longer timeout
            await page.goto(
                request.url, 
                wait_until="domcontentloaded",  # Less strict than networkidle
                timeout=60000  # Increased timeout to 60 seconds
            )
            
            # Apply delay if specified
            if request.options.delay > 0:
                await asyncio.sleep(request.options.delay / 1000)
            
            # Take screenshot
            screenshot_options = {
                "full_page": request.options.fullPage,
                "type": request.options.format
            }
            
            # Add quality for JPEG
            if request.options.format == "jpeg":
                screenshot_options["quality"] = request.options.quality
            
            screenshot_bytes = await page.screenshot(**screenshot_options)
            
            # Convert to base64
            base64_image = base64.b64encode(screenshot_bytes).decode()
            return f"data:image/{request.options.format};base64,{base64_image}"
            
        finally:
            await page.close()
    
    async def cleanup(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Initialize screenshot service
screenshot_service = ScreenshotService()

# API Routes
@api_router.post("/api-keys", response_model=APIKey)
async def create_api_key(request: APIKeyCreate):
    """Create a new API key"""
    api_key = APIKey(name=request.name)
    await db.api_keys.insert_one(api_key.dict())
    return api_key

@api_router.get("/api-keys", response_model=List[APIKey])
async def list_api_keys():
    """List all API keys (for demo purposes - normally you'd want authentication here too)"""
    keys = await db.api_keys.find().to_list(100)
    return [APIKey(**key) for key in keys]

@api_router.post("/v1/screenshot", response_model=ScreenshotResponse)
async def capture_screenshot(
    request: ScreenshotRequest,
    api_key: APIKey = Depends(verify_api_key)
):
    """Capture screenshot of a webpage"""
    try:
        # Take screenshot
        base64_image = await screenshot_service.take_screenshot(request)
        
        # Create response
        response = ScreenshotResponse(
            status="success",
            image=base64_image,
            format=request.options.format,
            timestamp=datetime.now(timezone.utc),
            url=request.url
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Screenshot error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Screenshot capture failed: {str(e)}")

@api_router.get("/")
async def root():
    return {"message": "URL Screenshot API v1.0", "status": "active"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize Playwright on startup"""
    await screenshot_service.initialize()
    logger.info("Screenshot service initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await screenshot_service.cleanup()
    client.close()
    logger.info("Services shut down")