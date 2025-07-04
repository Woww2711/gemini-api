# File: gui.py

import gradio as gr
import requests
import json
import os

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"
os.makedirs("temp_downloads", exist_ok=True)

# --- NEW: Mapping for UI-friendly names to API-required values ---
TONE_MAP = {
    "Professional": "Professional",
    "Casual": "Casual",
    "Simple": "Simple, for a general audience",
    "Technical": "Technical, for an expert audience",
}

# --- API Client Functions ---

def summarize_url_from_gui(url, length, tone_ui, output_format):
    endpoint = f"{API_URL}/summarize/url"
    # Use the map to get the correct API value for the selected tone
    api_tone = TONE_MAP.get(tone_ui)
    params = {"length": length, "tone": api_tone, "output_format": output_format}
    payload = {"url": url}
    try:
        response = requests.post(endpoint, params=params, json=payload)
        response.raise_for_status()
        if output_format == 'json':
            data = response.json()
            return data.get('title', 'No Title'), data.get('summary', 'No Summary'), None, f"Token Usage: {data.get('usage')}"
        else:
            temp_file_path = os.path.join("temp_downloads", f"summary.{output_format}")
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            return "File Ready", "Check the downloaded file below.", temp_file_path, "File generated."
    except requests.exceptions.RequestException as e:
        try:
            detail = e.response.json().get('detail')
            return "Error", f"API Error: {detail}", None, "Error"
        except (AttributeError, json.JSONDecodeError):
            return "Error", f"Failed to connect to API: {e}", None, "Error"


def summarize_paste_from_gui(text, length, tone_ui, output_format):
    endpoint = f"{API_URL}/summarize/paste"
    api_tone = TONE_MAP.get(tone_ui)
    params = {"length": length, "tone": api_tone, "output_format": output_format}
    payload = {"text": text}
    try:
        response = requests.post(endpoint, params=params, data=payload)
        response.raise_for_status()
        if output_format == 'json':
            data = response.json()
            return data.get('title', 'No Title'), data.get('summary', 'No Summary'), None, f"Token Usage: {data.get('usage')}"
        else:
            temp_file_path = os.path.join("temp_downloads", f"summary.{output_format}")
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            return "File Ready", "Check the downloaded file below.", temp_file_path, "File generated."
    except requests.exceptions.RequestException as e:
        try:
            detail = e.response.json().get('detail')
            return "Error", f"API Error: {detail}", None, "Error"
        except (AttributeError, json.JSONDecodeError):
            return "Error", f"Failed to connect to API: {e}", None, "Error"


def summarize_files_from_gui(files, length, tone_ui, output_format):
    endpoint = f"{API_URL}/summarize/pdf/upload"
    api_tone = TONE_MAP.get(tone_ui)
    params = {"length": length, "tone": api_tone, "output_format": output_format}
    
    if not files:
        return "Error", "No files uploaded. Please select at least one PDF.", None, "Error"
    try:
        files_to_upload = [('files', (os.path.basename(f.name), open(f.name, 'rb'), 'application/pdf')) for f in files]
        response = requests.post(endpoint, params=params, files=files_to_upload)
        response.raise_for_status()
        for _, (name, file_handle, _) in files_to_upload:
            file_handle.close()

        if output_format == 'json':
            data = response.json()
            return data.get('title', 'No Title'), data.get('summary', 'No Summary'), None, f"Token Usage: {data.get('usage')}"
        else:
            temp_file_path = os.path.join("temp_downloads", f"summary.{output_format}")
            with open(temp_file_path, 'wb') as f:
                f.write(response.content)
            return "File Ready", "Check the downloaded file below.", temp_file_path, "File generated."
    except requests.exceptions.RequestException as e:
        try:
            detail = e.response.json().get('detail')
            return "Error", f"API Error: {detail}", None, "Error"
        except (AttributeError, json.JSONDecodeError):
            return "Error", f"Failed to connect to API: {e}", None, "Error"
    except Exception as e:
        return "Error", f"An error occurred: {str(e)}", None, "Error"


# --- Gradio UI Definition (unchanged) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Gemini Summarization API Tester")
    gr.Markdown("A simple UI to test and evaluate the summarization API.")
    with gr.Tabs():
        with gr.TabItem("Summarize from URL"):
            url_input = gr.Textbox(label="URL", placeholder="Enter a URL to a webpage or PDF...")
            with gr.Row():
                length_input_url = gr.Dropdown(["short", "medium", "detailed"], label="Length", value="short")
                tone_input_url = gr.Dropdown(["Professional", "Casual", "Simple", "Technical"], label="Tone", value="Simple")
                format_input_url = gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Output Format", value="json")
            url_button = gr.Button("Summarize URL", variant="primary")
        with gr.TabItem("Summarize from Pasted Text"):
            paste_input = gr.Textbox(label="Pasted Text", placeholder="Paste your text here...", lines=10)
            with gr.Row():
                length_input_paste = gr.Dropdown(["short", "medium", "detailed"], label="Length", value="short")
                tone_input_paste = gr.Dropdown(["Professional", "Casual", "Simple", "Technical"], label="Tone", value="Simple")
                format_input_paste = gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Output Format", value="json")
            paste_button = gr.Button("Summarize Text", variant="primary")
        with gr.TabItem("Summarize from File(s)"):
            file_input = gr.File(label="Upload PDF(s)", file_count="multiple", file_types=[".pdf"])
            with gr.Row():
                length_input_file = gr.Dropdown(["short", "medium", "detailed"], label="Length", value="short")
                tone_input_file = gr.Dropdown(["Professional", "Casual", "Simple", "Technical"], label="Tone", value="Simple")
                format_input_file = gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Output Format", value="json")
            file_button = gr.Button("Summarize File(s)", variant="primary")
    gr.Markdown("---")
    gr.Markdown("## 📝 Output")
    title_output = gr.Textbox(label="Title")
    summary_output = gr.Textbox(label="Summary", lines=15)
    download_output = gr.File(label="Download File")
    usage_output = gr.Textbox(label="Usage Info")

    url_button.click(fn=summarize_url_from_gui, inputs=[url_input, length_input_url, tone_input_url, format_input_url], outputs=[title_output, summary_output, download_output, usage_output])
    paste_button.click(fn=summarize_paste_from_gui, inputs=[paste_input, length_input_paste, tone_input_paste, format_input_paste], outputs=[title_output, summary_output, download_output, usage_output])
    file_button.click(fn=summarize_files_from_gui, inputs=[file_input, length_input_file, tone_input_file, format_input_file], outputs=[title_output, summary_output, download_output, usage_output])

if __name__ == "__main__":
    demo.launch()