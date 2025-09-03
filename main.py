from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from utils.extract import extract_text_from_pdf, extract_text_from_docx, extract_text_from_json, extract_text_from_txt
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BERT QA Web App")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Allow all CORS for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load QA model
qa_pipeline = pipeline("question-answering")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask/")
async def ask_question_ui(
    request: Request,
    file: UploadFile = File(...),
    question: str = Form(...)
):
    filetype = file.content_type
    context = ""

    if "pdf" in filetype:
        context = extract_text_from_pdf(file)
    elif "word" in filetype or "officedocument" in filetype:
        context = extract_text_from_docx(file)
    elif "json" in filetype:
        context = extract_text_from_json(file)
    elif "text" in filetype:
        context = extract_text_from_txt(file)
    else:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Unsupported file type."
        })

    if not context.strip():
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Empty content in file."
        })

    result = qa_pipeline(question=question, context=context)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": result["answer"],
        "confidence": round(result["score"] * 100, 2),
        "question": question
    })
