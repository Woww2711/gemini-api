# File: app/services.py

from google import genai
from google.genai import types
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from . import config
from . import schemas

client = genai.Client(api_key=config.GEMINI_API_KEY)

# --- Base System Instruction (Unchanged) ---

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

MODEL_ID = 'gemini-2.5-flash-lite-preview-06-17'

# --- NEW: Helper function for dynamic prompt building ---
def build_dynamic_instruction(length: str | None, tone: str | None, is_json_mode: bool = True) -> str:
    """Builds a set of dynamic instructions for the model."""
    instructions = [
        "You are an expert summarizer. Your task is to produce a summary and a compelling title for the given content."
    ]
    if is_json_mode:
        instructions.append("Your final output MUST be a JSON object matching the provided schema.")
    
    if length:
        length_map = { "short": "in a single, concise paragraph (around 100 words)", "medium": "in about three paragraphs (around 300 words)", "detailed": "as a detailed summary (around 500 words)" }
        instructions.append(f"The summary's length should be {length_map.get(length, 'medium')}.")
    if tone:
        instructions.append(f"The tone of your writing must be {tone}.")
    return "\n".join(instructions)

# --- UPDATED: Core Service Functions ---

async def summarize_text(text: str, length: str | None, tone: str | None) -> types.GenerateContentResponse:
    processed_text = text.replace('\n', ' ')
    if not processed_text:
        raise ValueError("Input text cannot be empty.")
    try:
        system_instruction = build_dynamic_instruction(length, tone)
        generation_config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=schemas.EnhancedSummaryResponse,
        )
        return await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=f"Generate a summary and title for this text:\n\n{processed_text}",
            config=generation_config,
        )
    except Exception as e:
        print(f"An error occurred during text summarization: {e}")
        raise RuntimeError("Failed to get a summary from the API.") from e


async def summarize_pdf_files(
    file_contents: list[bytes],
    length: str | None,
    tone: str | None,
    mime_type: str = "application/pdf"
) -> types.GenerateContentResponse:
    """
    Summarizes PDF files using a robust two-step process.
    1. Generate a plain text summary from the raw PDF(s).
    2. Format that plain text into the final JSON object.
    """
    if not file_contents:
        raise ValueError("No file content was provided.")

    try:
        # --- STEP 1: Generate a plain text summary (no JSON mode) ---
        print("PDF Step 1: Generating plain text summary...")
        text_generation_instruction = build_dynamic_instruction(length, tone, is_json_mode=False)
        text_generation_config = types.GenerateContentConfig(
            system_instruction=text_generation_instruction,
            temperature=0.2,
        )

        if len(file_contents) == 1:
            prompt_instruction = "Please provide a detailed summary of this document."
        else:
            prompt_instruction = "Please provide a detailed summary that synthesizes the key information from all of the following documents."
        
        prompt_parts = [prompt_instruction]
        for content in file_contents:
            prompt_parts.append(types.Part.from_bytes(data=content, mime_type=mime_type))

        text_response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=prompt_parts,
            config=text_generation_config,
        )
        plain_text_summary = text_response.text
        print("PDF Step 1 Complete. Raw summary:", plain_text_summary[:100] + "...")

        # --- STEP 2: Format the plain text into JSON ---
        print("PDF Step 2: Formatting text into JSON object...")
        # We now call our reliable text summarizer to do the final formatting.
        json_response = await summarize_text(plain_text_summary, length=None, tone=None) # Use base settings for formatting
        return json_response

    except Exception as e:
        # Improved Error Logging: Print the original error from the Gemini library
        print(f"An error occurred during the two-step PDF summarization process: {e}")
        raise RuntimeError("Failed to process the PDF files with the API.") from e


async def summarize_url(url: str, length: str | None, tone: str | None) -> types.GenerateContentResponse:
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(url, timeout=30.0, follow_redirects=True, headers=HEADERS)
            response.raise_for_status()
        content_type = response.headers.get("Content-Type", "").lower()

        if "application/pdf" in content_type:
            return await summarize_pdf_files(response.content, length, tone)
        elif "text/html" in content_type:
            soup = BeautifulSoup(response.content, 'html.parser')
            embed_tag = soup.find("embed", attrs={"type": "application/pdf"})
            if embed_tag and embed_tag.get("src"):
                pdf_url = urljoin(url, embed_tag["src"])
                async with httpx.AsyncClient() as pdf_http_client:
                    pdf_response = await pdf_http_client.get(pdf_url, timeout=30.0, headers=HEADERS)
                return await summarize_pdf_files(pdf_response.content, length, tone)
            else:
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                    element.decompose()
                text = soup.get_text(separator=' ', strip=True)
                if not text:
                    raise ValueError("Could not extract meaningful text.")
                return await summarize_text(text, length, tone)
        else:
            raise ValueError(f"Unsupported content type '{content_type}'.")
    except httpx.RequestError as e:
        raise ValueError(f"Could not fetch or process the URL: {url}") from e
    
