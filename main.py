from fastapi import FastAPI
from core.logging import setup_logging
from api.v1.routers import email

# Configures application-wide logging before initializing the FastAPI app.
setup_logging()

# Initializes the main FastAPI application instance.
app = FastAPI(
    title="Wonderstreet API",
    description="API for managing agent workflows.",
    version="0.1.0",
)

# Registers the email router with all routes available under the /api/v1 prefix.
app.include_router(email.router, prefix="/api/v1")


# Health check endpoint for monitoring API availability.
@app.get("/", tags=["Health"])
async def read_root():
    """
    Root health check endpoint.
    """
    return {"status": "ok", "message": "API is running"}


# --- Future Enhancements ---
# @app.on_event("startup")
# async def startup_event():
#     # Creates shared resources (e.g., database pool, GmailClient) using app.state.
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Closes shared resources created during startup.
#     pass
