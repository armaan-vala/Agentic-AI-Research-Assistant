from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from tavily import TavilyClient
from app.config import settings


class AgentState(TypedDict):
    query: str
    search_queries: list[str]
    search_results: list[str]
    report: str


def create_llm():
    return ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
    )


def planner_node(state: AgentState) -> AgentState:
    llm = create_llm()
    prompt = (
        f"You are a research planner. Given this query: '{state['query']}'\n"
        "Generate 2-3 specific search queries to gather comprehensive information.\n"
        "Return ONLY the search queries, one per line. No numbering, no extra text."
    )
    response = llm.invoke(prompt)
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return {"search_queries": queries[:3]}


def search_node(state: AgentState) -> AgentState:
    client = TavilyClient(api_key=settings.tavily_api_key)
    all_results = []

    for query in state["search_queries"]:
        try:
            response = client.search(query=query, max_results=3)
            for result in response.get("results", []):
                all_results.append(
                    f"**{result['title']}**\n{result['content']}\nSource: {result['url']}"
                )
        except Exception:
            all_results.append(f"Search failed for: {query}")

    return {"search_results": all_results}


def summarizer_node(state: AgentState) -> AgentState:
    llm = create_llm()
    combined_results = "\n\n---\n\n".join(state["search_results"])
    prompt = (
        f"You are a research summarizer. Based on the following search results, "
        f"create a comprehensive report for the query: '{state['query']}'\n\n"
        f"Search Results:\n{combined_results}\n\n"
        "Create a well-structured report with:\n"
        "1. Brief introduction\n"
        "2. Key findings (use bullet points)\n"
        "3. Comparison table if applicable (use markdown table)\n"
        "4. Pros and cons if applicable\n"
        "5. Final recommendation\n\n"
        "Use markdown formatting."
    )
    response = llm.invoke(prompt)
    return {"report": response.content}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("searcher", search_node)
    graph.add_node("summarizer", summarizer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "searcher")
    graph.add_edge("searcher", "summarizer")
    graph.add_edge("summarizer", END)

    return graph.compile()


async def run_research_agent(query: str) -> dict:
    graph = build_graph()
    initial_state: AgentState = {
        "query": query,
        "search_queries": [],
        "search_results": [],
        "report": "",
    }
    result = await graph.ainvoke(initial_state)
    return {
        "query": result["query"],
        "search_results": result["search_results"],
        "report": result["report"],
    }
