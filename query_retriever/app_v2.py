from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from query_retriever import main
from query_retriever.generate_embeddings import EmbeddingManager

embedding_manager = EmbeddingManager()

base_dir = Path(__file__).resolve().parent

app = FastAPI(title="Agentic InboxRag", version="2.0")
app.mount(
    "/static",
    StaticFiles(directory=base_dir / "static"),
    name="static"
)
templates = Jinja2Templates(directory=base_dir/"templates")

@app.get('/', response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "chatbot.html",
        {"request" : request, "title" : "InboxRAG"}
    )
    
@app.post("/get")
async def chat(request: Request):
    body = await request.json()
    getquery = body.get("message")

    data = main.respond_query(getquery, embedding_manager)

    async def generate():
        for chunk in data:
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")