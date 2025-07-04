# File: app/schemas.py

from pydantic import BaseModel, HttpUrl, Field

# --- NEW: Nested model for usage data ---
class UsageMetadata(BaseModel):
    """
    A sub-model to hold the token count information from the API call.
    """
    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int

class TextRequest(BaseModel):
    text: str
    class Config:
        json_schema_extra = { "example": { "text": "..." } }

class UrlRequest(BaseModel):
    url: HttpUrl
    class Config:
        json_schema_extra = { "example": { "url": "https://en.wikipedia.org/wiki/Artificial_intelligence" } }

class EnhancedSummaryResponse(BaseModel):
    """
    The updated response schema that now includes API usage metadata.
    """
    title: str
    summary: str
    # Make the usage field optional in case of errors or non-applicable responses
    usage: UsageMetadata | None = Field(None, description="API usage statistics for the request.")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Essence of Artificial Intelligence",
                "summary": "Artificial intelligence (AI) refers to machine-demonstrated intelligence...",
                "usage": {
                    "prompt_token_count": 85,
                    "candidates_token_count": 120,
                    "total_token_count": 205
                }
            }
        }

