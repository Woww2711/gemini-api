from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Response
from . import schemas, services, formatters
from enum import Enum

# --- NEW: Enums for user-friendly query parameters ---
class LengthOption(str, Enum):
    short = "short"
    medium = "medium"
    detailed = "detailed"

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

router = APIRouter(prefix="/summarize", tags=["Summarization"])

# --- Helper function to build the correct response ---
def build_response(summary_text: str, output_format: OutputFormat) -> Response:
    # This function remains the same, it only works with the summary text
    if output_format == OutputFormat.text:
        return Response(content=summary_text, media_type="text/plain", headers={"Content-Disposition": 'attachment; filename="summary.txt"'})
    if output_format == OutputFormat.markdown:
        return Response(content=summary_text, media_type="text/markdown", headers={"Content-Disposition": 'attachment; filename="summary.md"'})
    if output_format == OutputFormat.pdf:
        pdf_bytes = formatters.to_pdf(summary_text)
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="summary.pdf"'})
    if output_format == OutputFormat.docx:
        docx_bytes = formatters.to_docx(summary_text)
        return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                        headers={"Content-Disposition": 'attachment; filename="summary.docx"'})

# --- Updated Endpoints ---

@router.post("/url", response_model=schemas.EnhancedSummaryResponse)
async def summarize_url_endpoint(
    request: schemas.UrlRequest,
    length: LengthOption | None = Query(None), tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    try:
        # The service now returns the full response object from the Gemini API
        gemini_response = await services.summarize_url(str(request.url), length, tone)
        
        # Extract the parsed content (title and summary)
        summary_obj = gemini_response.parsed
        
        if output_format == OutputFormat.json:
            # For JSON responses, we construct our final object with usage data
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count,
            )
            return schemas.EnhancedSummaryResponse(
                title=summary_obj.title,
                summary=summary_obj.summary,
                usage=usage_data
            )
        
        # For file downloads, we only need the summary text
        return build_response(summary_obj.summary, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")

@router.post("/paste", response_model=schemas.EnhancedSummaryResponse)
async def summarize_from_paste_endpoint(
    text: str = Form(...), length: LengthOption | None = Query(None), tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    try:
        gemini_response = await services.summarize_text(text, length, tone)
        summary_obj = gemini_response.parsed
        
        if output_format == OutputFormat.json:
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count,
            )
            return schemas.EnhancedSummaryResponse(title=summary_obj.title, summary=summary_obj.summary, usage=usage_data)
        
        return build_response(summary_obj.summary, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")


@router.post("/pdf/upload", response_model=schemas.EnhancedSummaryResponse)
async def summarize_pdf_upload_endpoint(
    # The signature is already correct, but we update the description
    files: list[UploadFile] = File(..., description="One or more PDF files to summarize. If multiple files are uploaded, a synthesized summary will be generated."),
    length: LengthOption | None = Query(None),
    tone: ToneOption | None = Query(None),
    output_format: OutputFormat = Query(OutputFormat.json)
):
    pdf_bytes_list = []
    try:
        for file in files:
            if file.content_type != "application/pdf":
                raise HTTPException(status_code=400, detail=f"Invalid file type: '{file.filename}'. All uploaded files must be PDFs.")
            pdf_bytes_list.append(await file.read())

        gemini_response = await services.summarize_pdf_files(pdf_bytes_list, length, tone)
        summary_obj = gemini_response.parsed
        
        if output_format == OutputFormat.json:
            usage_data = schemas.UsageMetadata(
                prompt_token_count=gemini_response.usage_metadata.prompt_token_count,
                candidates_token_count=gemini_response.usage_metadata.candidates_token_count,
                total_token_count=gemini_response.usage_metadata.total_token_count,
            )
            return schemas.EnhancedSummaryResponse(title=summary_obj.title, summary=summary_obj.summary, usage=usage_data)
            
        return build_response(summary_obj.summary, output_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: {e}")
    finally:
        for file in files:
            await file.close()


