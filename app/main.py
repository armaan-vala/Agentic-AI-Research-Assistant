from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.models import QueryRequest, ResearchResponse
from app.agent import run_research_agent

app = FastAPI(
    title="AI Research Agent",
    description="Agentic AI Research Assistant using LangGraph and Groq",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/research", response_model=ResearchResponse)
async def research(request: QueryRequest):
    try:
        result = await run_research_agent(request.query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent failed: {e}")
    return ResearchResponse(**result)
