# Main FastAPI app instance
from fastapi import FastAPI
from . import router as summarization_router
import uvicorn

# Create the main FastAPI application instance.
# The title and description will appear in the automatic OpenAPI docs (e.g., at /docs).
app = FastAPI(
    title="Gemini Summarization API",
    description="A fast, powerful API to summarize text, webpages, and PDF documents using Google's Gemini Flash Model.",
    version="1.0.0",
)

# A simple root endpoint to confirm the API is running.
# This is often used as a "health check" by deployment services.
@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"status": "ok", "message": "Welcome to the Gemini Summarization API!"}

# Include the router from app/router.py into the main application.
# All endpoints defined in that router will now be part of the main app,
# prefixed with '/summarize' as we defined.
app.include_router(summarization_router.router)

# This block allows you to run the server directly from the script
# for easy development and testing.
# To run: `python -m app.main` from the project's root directory.
# The uvicorn server will automatically reload when you save changes.
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)