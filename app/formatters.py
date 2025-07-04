# Logic for output file conversion
from fpdf import FPDF
from docx import Document
import io

def to_pdf(text: str) -> bytes:
    """
    Converts a string of text into a PDF file in memory.

    Args:
        text: The summary text to be converted.

    Returns:
        The content of the PDF file as bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Set the font. 'DejaVu' is a good choice as it supports a wide range of Unicode characters.
    # You might need to add the font file if it's not standard. For simplicity, we'll try 'Arial'.
    pdf.set_font("Arial", size=12)
    
    # Add the text to the PDF. The multi_cell function handles line breaks automatically.
    # We need to encode the text into 'latin-1' or a similar format that FPDF supports.
    pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
    
    # Output the PDF to a byte string.
    return pdf.output(dest='S').encode('latin-1')


def to_docx(text: str) -> bytes:
    """
    Converts a string of text into a Microsoft Word (.docx) file in memory.

    Args:
        text: The summary text to be converted.

    Returns:
        The content of the .docx file as bytes.
    """
    document = Document()
    document.add_paragraph(text)
    
    # Use an in-memory byte stream to save the document without creating a physical file.
    file_stream = io.BytesIO()
    document.save(file_stream)
    
    # Reset the stream's position to the beginning before reading its content.
    file_stream.seek(0)
    
    return file_stream.read()