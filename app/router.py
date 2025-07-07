# File: app/router.py

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Response, Depends
from pydantic import HttpUrl
from . import schemas, services, formatters, dependencies, exceptions
from enum import Enum

# ... (Enums are unchanged) ...
class LengthOption(str, Enum): 
    short = "Short"
    medium = "Medium"
    detailed = "Detailed"

class ToneOption(str, Enum): 
    professional = "Professional"
    casual = "Casual"
    simple = "Simple, for a general audience"
    technical = "Technical, for an expert audience"

class OutputFormat(str, Enum): 
    json = "json"
    text = "text"
    markdown = "markdown"
    pdf = "pdf"
    docx = "docx"

router = APIRouter(
    prefix="/summarize", 
    tags=["Summarization"], 
    dependencies=[Depends(dependencies.limit_content_length)]
)

def build_response(summary_text: str, output_format: OutputFormat, gemini_response) -> Response:
    """
    Takes summary text and the full Gemini response, and returns a file
    response with token usage data embedded in the headers.
    """
    headers = {
        "Content-Disposition": f'attachment; filename="ketqua.{output_format}"',
        # Add token counts to the headers. Prefix with X- for custom headers.
        "X-Prompt-Tokens": str(gemini_response.usage_metadata.prompt_token_count),
        "X-Candidates-Tokens": str(gemini_response.usage_metadata.candidates_token_count),
        "X-Total-Tokens": str(gemini_response.usage_metadata.total_token_count)
    }

    if output_format == OutputFormat.text:
        return Response(content=summary_text, media_type="text/plain", headers=headers)
    if output_format == OutputFormat.markdown:
        return Response(content=summary_text, media_type="text/markdown", headers=headers)
    if output_format == OutputFormat.pdf:
        pdf_bytes = formatters.to_pdf(summary_text)
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    if output_format == OutputFormat.docx:
        docx_bytes = formatters.to_docx(summary_text)
        return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)
# --- UPDATED Endpoint Logic ---

@router.post("/url", response_model=schemas.EnhancedSummaryResponse)
async def summarize_url_endpoint(
    url: HttpUrl = Form(..., description="The URL to a webpage or PDF.", examples=["https://ai.google.dev/gemini-api/docs"]),
    custom_prompt: str | None = Form(None, description="Optional: Provide a specific prompt instead of summarizing.", examples=['']),
    length: LengthOption | None = Query(None), 
    tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    try:
        gemini_response = await services.summarize_url(str(url), length, tone, custom_prompt)
        
        # Check if we got a parsed JSON object or plain text
        if gemini_response.parsed is not None:
            summary_obj = gemini_response.parsed
            summary_text = summary_obj.summary
            title = summary_obj.title
        else:
            summary_text = gemini_response.text
            title = custom_prompt or "Custom Prompt Result"
        
        if output_format == OutputFormat.json:
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count
            )
            return schemas.EnhancedSummaryResponse(title=title, summary=summary_text, usage=usage_data)
        
        return build_response(summary_text, output_format, gemini_response)
    except exceptions.URLAccessError as e:
        # This catches our custom error and returns the *correct* status code and detail.
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except (ValueError, RuntimeError) as e:
        # This generic handler remains for other types of errors.
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/paste", 
             response_model=schemas.EnhancedSummaryResponse,
             dependencies=[Depends(dependencies.limit_content_length)])
async def summarize_from_paste_endpoint(
    text: str = Form(..., examples=[""]),
    custom_prompt: str | None = Form(None, description="Optional: Provide a specific prompt instead of summarizing.", examples=['']),
    length: LengthOption | None = Query(None), 
    tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    try:
        gemini_response = await services.summarize_text(text, length, tone, custom_prompt)
        
        if gemini_response.parsed is not None:
            summary_obj = gemini_response.parsed
            summary_text = summary_obj.summary
            title = summary_obj.title
        else:
            summary_text = gemini_response.text
            title = custom_prompt or "Custom Prompt Result"
            
        if output_format == OutputFormat.json:
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count,
            )
            return schemas.EnhancedSummaryResponse(title=title, summary=summary_text, usage=usage_data)
        
        return build_response(summary_text, output_format, gemini_response)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pdf/upload", 
             response_model=schemas.EnhancedSummaryResponse,
             dependencies=[Depends(dependencies.limit_content_length)])
async def summarize_pdf_upload_endpoint(
    files: list[UploadFile] = File(..., description="One or more PDF files to summarize or process."),
    custom_prompt: str | None = Form(None, description="Optional: Provide a specific prompt instead of summarizing.", examples=['']),
    length: LengthOption | None = Query(None), 
    tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    try:
        pdf_bytes_list = [await file.read() for file in files]
        gemini_response = await services.summarize_pdf_files(pdf_bytes_list, length, tone, custom_prompt)
        
        if gemini_response.parsed is not None:
            summary_obj = gemini_response.parsed
            summary_text = summary_obj.summary
            title = summary_obj.title
        else:
            summary_text = gemini_response.text
            title = custom_prompt or "Custom Prompt Result"
            
        if output_format == OutputFormat.json:
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count,
            )
            return schemas.EnhancedSummaryResponse(title=title, summary=summary_text, usage=usage_data)

        return build_response(summary_text, output_format, gemini_response)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        for file in files: await file.close()