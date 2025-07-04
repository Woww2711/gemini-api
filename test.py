from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import httpx
import io
import pathlib
import os
from dotenv import load_dotenv
import sys

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#------------------------------------------------------------------
# Read pdf from URL path

doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"
doc_data = httpx.get(doc_url).content

prompt = "Summarize this document"
response = client.models.generate_content(
  model="gemini-2.5-pro",
  contents=[
      types.Part.from_bytes(
        data=doc_data,
        mime_type='application/pdf',
      ),
      prompt])

#------------------------------------------------------------------
# Read pdf from local file

# filepath = pathlib.Path('pdf/_OceanofPDF.com_Educating_the_Reflective_Practitioner_-_Donald_Schon.pdf')
# doc_data = filepath.read_bytes()


# prompt = "Summarize this document"
# response = client.models.generate_content(
#   model="gemini-2.5-flash-lite-preview-06-17",
#   contents=[
#       types.Part.from_bytes(
#         data=doc_data,
#         mime_type='application/pdf',
#       ),
#       prompt])

#------------------------------------------------------------------
# Read text from URL path

# url_context_tool = Tool(
#     url_context = types.UrlContext
# )

# response = client.models.generate_content(
#     model="gemini-2.5-flash-lite-preview-06-17",
#     contents="Summarize this url: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10536191",
#     config=GenerateContentConfig(
#         tools=[url_context_tool],
#         response_modalities=["TEXT"],
#     )
# )

#------------------------------------------------------------------

print(response.text)
# print(sys.platform)