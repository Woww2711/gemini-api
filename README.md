# Gemini Content API

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)

A powerful and versatile backend service built with FastAPI that leverages the Google Gemini API to process and summarize content from various sources, including URLs, pasted text, and PDF documents. The API is designed to be flexible, allowing for custom processing tasks beyond simple summarization and providing outputs in multiple convenient formats.

This project also includes a user-friendly testing and evaluation GUI built with Gradio.

**Repository:** [https://github.com/Woww2711/gemini-api](https://github.com/Woww2711/gemini-api)

## Features

-   **Multi-Modal Input:** Process content from multiple sources:
    -   **Web URLs:** Automatically scrapes and processes content from any live webpage.
    -   **Direct PDF URLs:** Intelligently handles links that point directly to a PDF file.
    -   **Pasted Text:** A user-friendly endpoint for direct text input.
    -   **File Uploads:** Supports uploading one or more PDF documents for summarization or synthesis.
-   **Flexible Processing:**
    -   **Summarization:** Default mode provides a high-quality summary with an automatically generated title.
    -   **Custom Prompts:** Users can provide their own prompts to perform tasks other than summarization (e.g., translation, data extraction, reformatting).
-   **Customizable Output:**
    -   **Length & Tone:** Control the length (short, medium, detailed) and tone (e.g., Professional, Casual) of the generated summary.
    -   **Multiple Formats:** Receive the output as a JSON object or as a downloadable file in `.txt`, `.md`, `.pdf`, or `.docx` formats.
-   **Developer-Friendly:**
    -   **API Usage Tracking:** JSON responses include detailed token counts (`prompt_tokens`, `candidates_tokens`, `total_tokens`) for usage monitoring.
    -   **Robust Error Handling:** The API gracefully handles common issues like inaccessible URLs, invalid inputs, and oversized files.
    -   **File Size Limiting:** Protects the service by rejecting requests with payloads larger than 15MB.
-   **Interactive GUI:** Includes a `gui.py` file built with Gradio for easy testing, evaluation, and demonstration of all API features.

## Tech Stack

-   **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
-   **AI Model:** [Google Gemini API](https://ai.google.dev/) (`google-genai` SDK)
-   **Web Scraping:** [HTTPX](https://www.python-httpx.org/) & [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
-   **File Generation:** [python-docx](https://python-docx.readthedocs.io/), [fpdf2](https://pyfpdf.github.io/fpdf2/)
-   **Testing GUI:** [Gradio](https://www.gradio.app/)
-   **Environment Management:** [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## Project Structure

```
gemini-api/
├── app/
│   ├── __init__.py
│   ├── config.py           # Handles API key loading from .env
│   ├── dependencies.py     # Reusable dependencies (e.g., size limiter)
│   ├── exceptions.py       # Custom exception classes
│   ├── formatters.py       # Logic for creating PDF and DOCX files
│   ├── main.py             # Main FastAPI app instance and entry point
│   ├── router.py           # Defines all API endpoints (/summarize/*)
│   ├── schemas.py          # Pydantic models for request/response validation
│   └── services.py         # Core logic for interacting with Gemini API
│
├── temp_downloads/         # Directory for temporary downloaded files from GUI
├── .env.example            # Example environment file
├── .gitignore
├── gui.py                  # Standalone Gradio testing interface
├── README.md               # This documentation file
└── requirements.txt        # Python dependencies
```

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Woww2711/gemini-api.git
cd gemini-api
```

### 2. Create a Conda Environment
It is highly recommended to use a virtual environment. This project is configured for Python 3.10+.
```bash
conda create --name gemini-api python=3.11
conda activate gemini-api
```

### 3. Install Dependencies
Install all the required Python libraries from the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
The application loads the Gemini API key from an environment variable.

-   Make a copy of the example environment file:
    ```bash
    cp .env.example .env
    ```
-   Open the `.env` file in a text editor.
-   Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
-   Replace `YOUR_API_KEY_HERE` with your actual key:
    ```
    GOOGLE_API_KEY="AIzaSy...your...key...here"
    ```
The application will automatically load this key on startup. The `.env` file is included in `.gitignore` to prevent accidental commits of your secret key.

## Running the Application

This project has two main components: the FastAPI server and the Gradio GUI. You need to run them in two separate terminals.

### 1. Start the FastAPI Server
In your first terminal, make sure your conda environment is active (`conda activate gemini-api`) and run the following command from the project's root directory:

```bash
uvicorn app.main:app --reload
```
The server will start on `http://127.0.0.1:8000`. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### 2. Start the Gradio GUI
Open a second terminal, activate the same conda environment, and run:
```bash
python gui.py
```
The Gradio interface will launch, typically on `http://127.0.0.1:7860`. Open this URL in your browser to use the graphical interface for testing.

## API Endpoints

All endpoints are prefixed with `/summarize`.

| Method | Path             | Description                                                                                       |
| :----- | :--------------- | :------------------------------------------------------------------------------------------------ |
| `POST` | `/url`           | Processes content from a URL (webpage or PDF). Accepts form data.                                 |
| `POST` | `/paste`         | Processes text pasted directly into a form.                                                       |
| `POST` | `/pdf/upload`    | Processes one or more uploaded PDF files. If multiple, a synthesized summary is generated.      |

## Contact

This project is maintained by:

-   **Nguyen Minh Quan**
-   Email: [quannm@proxglobal.com](mailto:quannm@proxglobal.com)

Feel free to reach out with any questions or feedback.