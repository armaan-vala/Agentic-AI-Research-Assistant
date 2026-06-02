from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    query: str
    search_results: list[str]
    report: str
