from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from core.config import settings

# Create FastAPI App
app = FastAPI(
    title="B2B Lead Generator API", 
    version="1.0.0",
    description="API for Generating and Managing B2B Leads Using Apollo.io API Integration"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routes
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "B2B Lead Generator API", "status": "Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )