# File: app/services.py

from google import genai
from google.genai import types
import httpx
from bs4 import BeautifulSoup
from .dependencies import MAX_REQUEST_SIZE

from . import config, schemas

client = genai.Client(api_key=config.GEMINI_API_KEY)

HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36" }

MODEL_ID = "gemini-2.5-flash-lite-preview-06-17"

# --- Helper function to get the base text of a prompt ---
def get_base_prompt_text(custom_prompt: str | None) -> str:
    """Returns the user's custom prompt or the default summarization prompt."""
    # The .strip() is crucial to handle empty strings from form inputs
    if custom_prompt and custom_prompt.strip():
        return custom_prompt.strip()
    return "Generate a detailed summary and a compelling title for the following content."


# --- Core Service Functions ---

async def summarize_text(text: str, length: str | None, tone: str | None, custom_prompt: str | None) -> types.GenerateContentResponse:
    processed_text = text.replace('\n', ' ')
    if not processed_text:
        raise ValueError("Input text cannot be empty.")
        
    try:
        base_prompt = get_base_prompt_text(custom_prompt)
        
        # Determine if we should use JSON mode
        use_json_mode = not (custom_prompt and custom_prompt.strip())
        
        system_instruction = f"You are a helpful AI assistant. The user wants you to do the following: '{base_prompt}'."
        if tone:
            system_instruction += f" Your tone must be {tone}."
        if length and not custom_prompt: # Only apply length if it's a summary
            length_map = { "short": "short (1 paragraph)", "medium": "medium (3 paragraphs)", "detailed": "detailed" }
            system_instruction += f" The length should be {length_map.get(length, 'medium')}."

        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json" if use_json_mode else "text/plain",
            response_schema=schemas.EnhancedSummaryResponse if use_json_mode else None,
        )
        
        return await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=processed_text,
            config=generation_config,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to process text with the API: {e}") from e


async def summarize_pdf_files(file_contents: list[bytes], length: str | None, tone: str | None, custom_prompt: str | None) -> types.GenerateContentResponse:
    if not file_contents:
        raise ValueError("No file content was provided.")
    try:
        base_prompt = get_base_prompt_text(custom_prompt)
        
        use_json_mode = not (custom_prompt and custom_prompt.strip())
        
        system_instruction = f"You are a helpful AI assistant. The user wants you to do the following with the provided file(s): '{base_prompt}'."
        if tone:
            system_instruction += f" Your tone must be {tone}."
        if length and not custom_prompt:
             length_map = { "short": "short (1 paragraph)", "medium": "medium (3 paragraphs)", "detailed": "detailed" }
             system_instruction += f" The length should be {length_map.get(length, 'medium')}."
             
        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json" if use_json_mode else "text/plain",
            response_schema=schemas.EnhancedSummaryResponse if use_json_mode else None,
        )
        
        prompt_parts = [types.Part.from_bytes(data=c, mime_type="application/pdf") for c in file_contents]
        
        return await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt_parts,
            config=generation_config,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to process the PDF files with the API: {e}") from e


async def summarize_url(url: str, length: str | None, tone: str | None, custom_prompt: str | None) -> types.GenerateContentResponse:
    try:
        async with httpx.AsyncClient() as http_client:
            head_response = await http_client.head(url, timeout=10.0, follow_redirects=True)
            head_response.raise_for_status()
            
            content_length = head_response.headers.get("content-length")
            if content_length and int(content_length) > MAX_REQUEST_SIZE:
                raise ValueError(f"Remote file is too large. Limit is {MAX_REQUEST_SIZE / (1024*1024):.2f} MB.")

            response = await http_client.get(url, timeout=30.0, follow_redirects=True, headers=HEADERS)
            response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()

        if "application/pdf" in content_type:
            return await summarize_pdf_files([response.content], length, tone, custom_prompt)
        elif "text/html" in content_type:
            soup = BeautifulSoup(response.content, 'html.parser')
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                element.decompose()
            text = soup.get_text(separator=' ', strip=True)
            if not text:
                raise ValueError("Could not extract meaningful text.")
            return await summarize_text(text, length, tone, custom_prompt)
        else:
            raise ValueError(f"Unsupported content type '{content_type}'.")
    except httpx.RequestError as e:
        raise ValueError(f"Could not fetch or process the URL: {url}") from e