from contextlib import asynccontextmanager

from fastapi import (
    Depends, FastAPI)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.templates import templates
from app.core.redis_config import (
    close_redis_connection, connect_to_redis)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan manager."""
#     # Startup
#     # await create_tables()
#     yield
#     # Shutdown
#     pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print("Application startup (via lifespan)...")
    # Call Redis connection on startup
    await connect_to_redis()
    yield
    # Call Redis disconnection on shutdown
    print("Application shutdown (via lifespan)...")
    await close_redis_connection()





# Create FastAPI app
app = FastAPI(
    title="DocHub API",
    description="A centralized, secure platform for collaborative document management and AI-powered content refinement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure this properly for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*", "Authorization", "Content-Type"],
#     expose_headers=["*"],
# )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://docu-prompt-hub.s3-website-us-east-1.amazonaws.com", "http://docu-hub.abacies.com.s3-website-us-east-1.amazonaws.com", "https://docu-hub.abacies.com"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization", "Content-Type"],
    expose_headers=["*"],
)



# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly for production
)


# @app.on_event("startup")
# async def startup_event():
#     """Run this code when the application starts."""
#     print("Application startup...")
#     await connect_to_redis()

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Run this code when the application shuts down."""
#     print("Application shutdown...")
#     await close_redis_connection()




# Include API routes
app.include_router(api_router, prefix="/api/v1")




@app.get("/health-check",
    summary="Health Check",
    description="Test endpoint to check if the application server is running and responding",
    status_code=200,
    responses={
        200: {"description": "Application is healthy"}
    },
    tags=['Health Check']
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Application is running successfully"
    }