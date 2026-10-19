from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile, File, HTTPException
import fitz
from fastapi import Form
from retrieval import split_text, create_embeddings, search_chunks
import os
from dotenv import load_dotenv

load_dotenv()

from google import genai

api_key=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)

app = FastAPI(title="RAG Academic QA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "RAG Academic QA Backend is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    content = await file.read()

    try:
        doc = fitz.open(stream=content, filetype="pdf")

        text = ""

        for page in doc:
            text += page.get_text() + "\n"

        doc.close()

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        return {
            "filename": file.filename,
            "pages": len(fitz.open(stream=content, filetype="pdf")),
            "text": text
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e

        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please try another file."
        )

@app.post("/ask")
async def ask_question(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    if not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    content = await file.read()

    try:
        doc = fitz.open(stream=content, filetype="pdf")

        text = ""

        for page in doc:
            text += page.get_text() + "\n"

        doc.close()

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF."
            )

        chunks = split_text(text)

        embeddings = create_embeddings(chunks)

        results = search_chunks(
            chunks,
            embeddings,
            question,
            top_k=3
        )

        context="\n\n".join(results)

        prompt=f"""
        Answer the question using only the information provided in the context below.
        If the answer is not available in the context, say that the uploaded document does not contain enough information.

        Context:
        {context}

        Question:
        {question}
        """

        response=client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
   )

        answer=response.text

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": results
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF or retrieve relevant text."
        )

@app.get("/test-gemini")
def test_gemini():
    try:
        response=client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Explain the Document Object Model in two sentences."
        )

        return {"answer":response.text}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API error: {str(e)}"
        )