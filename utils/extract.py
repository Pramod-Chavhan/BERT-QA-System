# utils/extract.py
import fitz  # PyMuPDF
import docx
import json

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file.file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_json(file):
    data = json.load(file.file)
    return json.dumps(data, indent=2)

def extract_text_from_txt(file):
    return file.file.read().decode("utf-8")
