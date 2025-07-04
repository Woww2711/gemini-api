# To-Do List: Gemini Summarization API Project

This document outlines the steps to build a FastAPI backend service that uses the Gemini API for summarization and provides the output in multiple downloadable formats.

## Phase 0: Project Setup & Foundation

This phase is about creating a solid, organized foundation for your project.

### 1. Initialize Project Directory
- [ ] Create a root folder for your project (e.g., `gemini_summarizer`).
- [ ] Inside the root, create a source folder (e.g., `app`).

### 2. Set Up Virtual Environment
- [ ] Navigate to your project folder in the terminal.
- [ ] Use Miniconda to create and activate your environment:
  ```bash
  conda create --name summerize python=3.11
  conda activate summerize
  ```

### 3. Install Dependencies
- [ ] Create a `requirements.txt` file in the project root.
- [ ] Add the necessary libraries to `requirements.txt`:
  ```
  # For the web framework
  fastapi
  uvicorn[standard]

  # For Gemini API
  google-generativeai
  python-dotenv

  # For handling URL content
  requests
  beautifulsoup4

  # For handling PDF uploads
  python-multipart

  # For creating PDF files
  fpdf2

  # For creating DOCX (Word) files
  python-docx
  ```
- [ ] Install the dependencies from the file:
  ```bash
  pip install -r requirements.txt
  ```

### 4. API Key & Configuration Management
- [ ] Create a `.env` file in the root directory to securely store your API key.
- [ ] Add your key to the `.env` file: `GEMINI_API_KEY="YOUR_API_KEY_HERE"`
- [ ] Create a `.gitignore` file and add the following lines to it. This is **critical** to avoid committing secrets.
  ```
  .env
  __pycache__/
  *.pyc
  ```

### 5. Create Initial File Structure
- [ ] Create the following directory and file structure for your application:
  ```
  SummerizeAPI/
  ├── .env
  ├── .gitignore
  ├── requirements.txt
  └── app/
      ├── __init__.py
      ├── main.py         # Main FastAPI app instance
      ├── schemas.py      # Pydantic models for request/response
      ├── router.py       # API endpoints/routes
      ├── services.py     # Core logic for Gemini interaction
      ├── formatters.py   # Logic for output file conversion
      └── config.py       # To load and manage settings/API keys
  ```

---

## Phase 1: Core Service Logic (The "Brains")

Focus on the business logic in `app/services.py` without worrying about the API endpoints yet.

- [ ] **1. Configure Gemini Client:**
    - In `app/config.py`, use `python-dotenv` to load the `GEMINI_API_KEY`.
    - In `app/services.py`, import the key and configure the `google.generativeai` client.

- [ ] **2. Implement Text/Clipboard Summarization:**
    - Create an `async` function `summarize_text(text: str)` in `services.py`.
    - This function will take a string, send it to the Gemini model, and return the summarized text string.

- [ ] **3. Implement Webpage URL Summarization:**
    - Create an `async` function `summarize_webpage_url(url: str)` in `services.py`.
    - Use `requests` or `httpx` to fetch the HTML content of the URL.
    - Use `BeautifulSoup4` to parse the HTML and extract clean, main text content.
    - Pass this cleaned text to your `summarize_text` function.

- [ ] **4. Implement PDF Summarization (from Upload):**
    - Create an `async` function `summarize_pdf(file_content: bytes, mime_type: str)` in `services.py`.
    - Use the Gemini File API (`genai.upload_file()`) to upload the `file_content`.
    - Send a prompt to the Gemini model that includes the reference to the uploaded file.
    - Process the response and return the summary text.

- [ ] **5. Implement PDF-from-URL Logic:**
    - Create an `async` helper function in `services.py` that takes a URL.
    - Use `requests` or `httpx` to download the content of the URL.
    - Verify the `Content-Type` header is `application/pdf`. If not, raise an error.
    - Pass the downloaded bytes to your `summarize_pdf` function.

---

## Phase 2: FastAPI Backend Implementation (The "Plumbing")

Connect your service logic to the outside world via API endpoints.

### 1. Define Schemas (`app/schemas.py`)
- [ ] Create Pydantic models for your API requests and default JSON response.
    ```python
    from pydantic import BaseModel

    class TextRequest(BaseModel):
        text: str

    class UrlRequest(BaseModel):
        url: str

    class SummaryResponse(BaseModel):
        summary: str
    ```

### 2. Create the Router (`app/router.py`)
- [ ] Initialize an `APIRouter`.
- [ ] **Endpoint 1: Text/Clipboard:** Create a `POST /summarize/text` endpoint.
- [ ] **Endpoint 2: Webpage URL:** Create a `POST /summarize/webpage` endpoint.
- [ ] **Endpoint 3: PDF Upload:** Create a `POST /summarize/pdf/upload` endpoint using `UploadFile`.
- [ ] **Endpoint 4: PDF from URL:** Create a `POST /summarize/pdf/url` endpoint.
- [ ] For now, have them call the appropriate service function but return a basic response. We will enhance them in Phase 4.

### 3. Assemble the App (`app/main.py`)
- [ ] Create the main FastAPI app instance: `app = FastAPI()`.
- [ ] Include the router from `app/router.py`.
- [ ] Add a root `GET /` health check endpoint.

---

## Phase 3: Refinement & Robustness

Make your application reliable and user-friendly.

- [ ] **1. Implement Comprehensive Error Handling:**
    - In your router endpoints, use `try...except` blocks.
    - Catch potential errors (Gemini API errors, invalid URLs, file errors).
    - Raise FastAPI's `HTTPException` with appropriate status codes (`400`, `503`, etc.).

- [ ] **2. Add API Documentation:**
    - In `app/main.py`, give your FastAPI app a `title` and `description`.
    - In `app/router.py`, add `summary` and `description` arguments to each endpoint decorator for clarity in the `/docs`.

- [ ] **3. Implement Logging:**
    - Set up Python's built-in `logging` module.
    - Log incoming requests, successful summaries, and especially any errors that occur.

---

## Phase 4: Output Formatting & Download Functionality

Implement the logic to return the summary in various downloadable formats.

### 1. Create the Format Conversion Service (`app/formatters.py`)
- [ ] **PDF Formatter:** Create `def to_pdf(text: str) -> bytes:` using `fpdf2`.
- [ ] **DOCX (Word) Formatter:** Create `def to_docx(text: str) -> bytes:` using `python-docx` and `io.BytesIO`.
- [ ] **Simple Formatters:** Text and Markdown can be handled directly in the router as they don't require complex conversion.

### 2. Update the API Router (`app/router.py`)
- [ ] **Define an Enum for valid formats** to get validation and a dropdown in the docs.
    ```python
    from enum import Enum
    class OutputFormat(str, Enum):
        json = "json"
        text = "text"
        markdown = "markdown"
        pdf = "pdf"
        docx = "docx"
    ```
- [ ] **Modify endpoint signatures** to accept an `OutputFormat` query parameter with a default of `"json"`.
- [ ] **Implement response logic:** Inside each endpoint, after getting the summary string, use a `match` or `if/elif` block based on the `format` parameter.
- [ ] **Return appropriate `Response` types:** Use `JSONResponse` for `json` and `fastapi.Response` for all file types, setting the correct `media_type` and `Content-Disposition` header for downloads.

### 3. Update API Documentation
- [ ] Use the `responses` parameter in the endpoint decorator in `app/router.py` to explicitly document the different possible `Content-Type`s that each endpoint can return.

### Summary Table for Output Formats

| Format | Library | MIME Type | FastAPI Response | `Content-Disposition` Header |
| :--- | :--- | :--- | :--- | :--- |
| **JSON** | (built-in) | `application/json` | `JSONResponse` | Not needed |
| **Text** | (built-in) | `text/plain` | `Response` | `attachment; filename="summary.txt"` |
| **Markdown**| (built-in) | `text/markdown` | `Response` | `attachment; filename="summary.md"` |
| **PDF** | `fpdf2` | `application/pdf` | `Response` | `attachment; filename="summary.pdf"` |
| **DOCX** | `python-docx`| `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `Response` | `attachment; filename="summary.docx"` |
