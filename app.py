# File: gui.py

import gradio as gr
import requests
import json
import os
from datetime import datetime

# --- Configuration ---
API_URL = "http://127.0.0.1:8000"
os.makedirs("temp_downloads", exist_ok=True)

# --- NEW: Mapping Dictionaries for Vietnamese UI ---
# Maps Vietnamese UI text to the English values the API expects.

LENGTH_MAP_VI = {
    "Ngắn": "Short",
    "Trung bình": "Medium",
    "Chi tiết": "Detailed",
}

TONE_MAP_VI = {
    "Chuyên nghiệp": "Professional",
    "Thân mật": "Casual",
    "Đơn giản": "Simple, for a general audience",
    "Kỹ thuật": "Technical, for an expert audience",
}

# --- Helper to create a unique filename ---
def get_download_path(extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("temp_downloads", f"ketqua_{timestamp}.{extension}")

# --- API Client Functions (Updated to use mapping dictionaries) ---

def process_request(endpoint, params, payload=None, files=None):
    try:
        if files:
            files_to_upload = [('files', (os.path.basename(f.name), open(f.name, 'rb'), 'application/pdf')) for f in payload]
            response = requests.post(endpoint, params=params, files=files_to_upload, data={"custom_prompt": params.get("custom_prompt", "")})
            for _, (_, file_handle, _) in files_to_upload:
                file_handle.close()
        elif 'url' in payload or 'text' in payload:
             response = requests.post(endpoint, params=params, data=payload)
        else:
            response = requests.post(endpoint, params=params, json=payload)

        response.raise_for_status()
        output_format = params.get("output_format")

        json_visible, md_visible, file_visible = False, False, False
        title_val, summary_val, md_val, file_val, usage_val = "", "", "", None, ""

        if output_format == 'json':
            json_visible = True
            data = response.json()
            title_val, summary_val = data.get('title', 'Không có tiêu đề'), data.get('summary', 'Không có tóm tắt')
            usage_val = f"Thông tin sử dụng: {data.get('usage')}"
        
        else:
            # --- NEW: Logic to extract usage info from headers for all other formats ---
            file_visible = True
            prompt_tokens = response.headers.get("X-Prompt-Tokens", "N/A")
            candidates_tokens = response.headers.get("X-Candidates-Tokens", "N/A")
            total_tokens = response.headers.get("X-Total-Tokens", "N/A")
            usage_val = f"Thông tin sử dụng: {{'prompt_token_count': {prompt_tokens}, 'candidates_token_count': {candidates_tokens}, 'total_token_count': {total_tokens}}}"
            
            file_path = get_download_path(output_format)
            if output_format in ['markdown', 'text']:
                if output_format == 'markdown':
                    md_visible = True
                    title_val = "Xem trước Markdown & Tải về"
                    md_val = response.text
                else:
                    json_visible = True
                    title_val = "Xem trước Text & Tải về"
                    summary_val = response.text
                with open(file_path, 'w', encoding='utf-8') as f: f.write(response.text)
            else: # pdf or docx
                title_val = f"Tệp {output_format.upper()} đã sẵn sàng"
                with open(file_path, 'wb') as f: f.write(response.content)
            file_val = file_path

        return (
            gr.update(value=title_val), 
            gr.update(value=summary_val, visible=json_visible),
            gr.update(value=md_val, visible=md_visible), 
            gr.update(value=file_val, visible=file_visible),
            gr.update(value=usage_val)
        )
    except requests.exceptions.RequestException as e:
        try: detail = e.response.json().get('detail'); error_msg = f"Lỗi API: {detail}"
        except: error_msg = f"Không thể kết nối đến API: {e}"
        return gr.update(value="Lỗi"), gr.update(value=error_msg, visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="Lỗi")


def summarize_url_from_gui(url, length_ui, tone_ui, output_format, custom_prompt):
    if not url or not url.strip():
        return "Lỗi", gr.update(value="Vui lòng nhập một URL.", visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="Yêu cầu bị hủy")
    endpoint, api_length, api_tone = f"{API_URL}/summarize/url", LENGTH_MAP_VI.get(length_ui), TONE_MAP_VI.get(tone_ui)
    params = {"length": api_length, "tone": api_tone, "output_format": output_format}
    payload = {"url": url, "custom_prompt": custom_prompt or ""}
    return process_request(endpoint, params, payload=payload)

def summarize_paste_from_gui(text, length_ui, tone_ui, output_format, custom_prompt):
    if not text or not text.strip():
        return "Lỗi", gr.update(value="Vui lòng nhập hoặc dán văn bản vào ô.", visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="Yêu cầu bị hủy")
    endpoint, api_length, api_tone = f"{API_URL}/summarize/paste", LENGTH_MAP_VI.get(length_ui), TONE_MAP_VI.get(tone_ui)
    params = {"length": api_length, "tone": api_tone, "output_format": output_format}
    payload = {"text": text, "custom_prompt": custom_prompt or ""}
    return process_request(endpoint, params, payload=payload)

def summarize_files_from_gui(files, length_ui, tone_ui, output_format, custom_prompt):
    if not files:
        return "Lỗi", gr.update(value="Chưa có tệp nào được tải lên. Vui lòng chọn ít nhất một tệp PDF.", visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(value="Yêu cầu bị hủy")
    endpoint, api_length, api_tone = f"{API_URL}/summarize/pdf/upload", LENGTH_MAP_VI.get(length_ui), TONE_MAP_VI.get(tone_ui)
    params = {"length": api_length, "tone": api_tone, "output_format": output_format, "custom_prompt": custom_prompt or ""}
    return process_request(endpoint, params, payload=files, files=True)


# --- Gradio UI Definition (Translated to Vietnamese) ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Bộ Xử lý Nội dung Gemini")
    gr.Markdown("Giao diện đơn giản để kiểm tra và đánh giá API. Sử dụng trường 'Yêu cầu Tùy chỉnh' cho các tác vụ khác ngoài tóm tắt.")
    
    with gr.Tabs():
        with gr.TabItem("Xử lý từ URL"):
            url_input=gr.Textbox(label="URL", placeholder="Nhập URL của trang web hoặc tệp PDF...")
            custom_prompt_url=gr.Textbox(label="Yêu cầu Tùy chỉnh (Tùy chọn)", placeholder="Để trống nếu muốn tóm tắt, hoặc nhập yêu cầu của bạn...")
            with gr.Row():
                length_input_url=gr.Dropdown(list(LENGTH_MAP_VI.keys()), label="Độ dài", value="Ngắn")
                tone_input_url=gr.Dropdown(list(TONE_MAP_VI.keys()), label="Phong cách", value="Đơn giản")
            with gr.Row():
                format_input_url=gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Định dạng Đầu ra", value="json")
            url_button=gr.Button("Xử lý URL", variant="primary")
            
        with gr.TabItem("Xử lý từ Văn bản"):
            paste_input=gr.Textbox(label="Văn bản được dán", placeholder="Dán văn bản của bạn vào đây...", lines=10)
            custom_prompt_paste=gr.Textbox(label="Yêu cầu Tùy chỉnh (Tùy chọn)", placeholder="Để trống nếu muốn tóm tắt, hoặc nhập yêu cầu của bạn...")
            with gr.Row():
                length_input_paste=gr.Dropdown(list(LENGTH_MAP_VI.keys()), label="Độ dài", value="Ngắn")
                tone_input_paste=gr.Dropdown(list(TONE_MAP_VI.keys()), label="Phong cách", value="Đơn giản")
            with gr.Row():
                format_input_paste=gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Định dạng Đầu ra", value="json")
            paste_button=gr.Button("Xử lý Văn bản", variant="primary")

        with gr.TabItem("Xử lý từ Tệp"):
            file_input=gr.File(label="Tải lên tệp PDF", file_count="multiple", file_types=[".pdf"])
            custom_prompt_file=gr.Textbox(label="Yêu cầu Tùy chỉnh (Tùy chọn)", placeholder="Để trống nếu muốn tóm tắt, hoặc nhập yêu cầu của bạn...")
            with gr.Row():
                length_input_file=gr.Dropdown(list(LENGTH_MAP_VI.keys()), label="Độ dài", value="Ngắn")
                tone_input_file=gr.Dropdown(list(TONE_MAP_VI.keys()), label="Phong cách", value="Đơn giản")
            with gr.Row():
                format_input_file=gr.Dropdown(["json", "text", "markdown", "pdf", "docx"], label="Định dạng Đầu ra", value="json")
            file_button=gr.Button("Xử lý Tệp", variant="primary")
            
    gr.Markdown("---"); gr.Markdown("## 📝 Kết quả")
    title_output=gr.Textbox(label="Tiêu đề")
    json_summary_output=gr.Textbox(label="Tóm tắt / Kết quả", lines=15, visible=True)
    md_preview_output=gr.Markdown(label="Xem trước Markdown", visible=False)
    download_output=gr.File(label="Tải về Tệp", visible=False)
    usage_output=gr.Textbox(label="Thông tin Sử dụng")
    
    outputs_list=[title_output, json_summary_output, md_preview_output, download_output, usage_output]

    url_button.click(fn=summarize_url_from_gui, inputs=[url_input, length_input_url, tone_input_url, format_input_url, custom_prompt_url], outputs=outputs_list)
    paste_button.click(fn=summarize_paste_from_gui, inputs=[paste_input, length_input_paste, tone_input_paste, format_input_paste, custom_prompt_paste], outputs=outputs_list)
    file_button.click(fn=summarize_files_from_gui, inputs=[file_input, length_input_file, tone_input_file, format_input_file, custom_prompt_file], outputs=outputs_list)

if __name__ == "__main__":
    demo.launch()