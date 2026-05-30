import json
import re
from typing import Callable

from crewai import LLM, Agent, Crew, Task

from core.config import settings

Emitter = Callable[[str, dict], None]


def _create_llm() -> LLM:
    return LLM(
        model="gemini/gemini-2.0-flash",
        api_key=settings.google_api_key,
        temperature=0.1,
    )


def _extract_json(text: str) -> dict:
    """LLM 출력에서 JSON 객체를 추출한다."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(text[start : end + 1])


def run_stock_analysis(question: str, emit: Emitter) -> None:
    """
    3단계 crewAI 파이프라인을 동기 실행한다.
    스레드풀에서 호출되므로 emit은 call_soon_threadsafe로 감싸진 콜백이어야 한다.
    """
    llm = _create_llm()

    try:
        # ── 1. Router Agent ────────────────────────────────────────
        emit("agent_status", {"agent": "RouterAgent", "status": "RUNNING"})

        router_agent = Agent(
            role="Question Classifier",
            goal="Determine whether a question is about stocks or financial markets.",
            backstory="You are a strict classifier. You only output one of two exact strings.",
            llm=llm,
            verbose=False,
        )
        router_task = Task(
            description=(
                f"Classify the following question.\n"
                f"Question: {question}\n\n"
                "Rules:\n"
                "- If the question is about stocks, companies, investments, or financial markets → output exactly: stock_related\n"
                "- Otherwise → output exactly: not_stock\n"
                "Output ONLY one of these two strings. No punctuation, no explanation."
            ),
            expected_output="stock_related or not_stock",
            agent=router_agent,
        )
        router_output = str(Crew(agents=[router_agent], tasks=[router_task], verbose=False).kickoff()).strip().lower()

        is_stock = "stock_related" in router_output
        result_value = "stock_related" if is_stock else "not_stock"

        emit("agent_status", {"agent": "RouterAgent", "status": "SUCCESS", "result": result_value})

        if not is_stock:
            return

        # ── 2. Research Agent ──────────────────────────────────────
        emit("agent_status", {"agent": "ResearchAgent", "status": "RUNNING"})

        research_agent = Agent(
            role="Stock Research Analyst",
            goal="Gather comprehensive information about a stock or company.",
            backstory=(
                "You are a senior equity analyst with deep knowledge of global financial markets. "
                "You research companies, analyze recent news, financial performance, and key business developments."
            ),
            llm=llm,
            verbose=False,
        )
        research_task = Task(
            description=(
                f"Research the following question thoroughly: {question}\n\n"
                "Cover these areas:\n"
                "1. Company/stock overview\n"
                "2. Recent news and developments\n"
                "3. Key financial metrics or performance\n"
                "4. Major risks or concerns\n"
                "Provide detailed, factual information."
            ),
            expected_output="Comprehensive research covering company overview, recent news, financials, and risks.",
            agent=research_agent,
        )
        research_result = str(
            Crew(agents=[research_agent], tasks=[research_task], verbose=False).kickoff()
        )

        emit("agent_status", {"agent": "ResearchAgent", "status": "SUCCESS"})

        # ── 3. Summary Agent ───────────────────────────────────────
        emit("agent_status", {"agent": "SummaryAgent", "status": "RUNNING"})

        summary_agent = Agent(
            role="Investment Summary Writer",
            goal="Produce a structured JSON investment analysis from research data.",
            backstory="You are a financial writer who creates clear, concise investment summaries in strict JSON format.",
            llm=llm,
            verbose=False,
        )
        summary_task = Task(
            description=(
                f"Based on the research below, write a structured analysis for: {question}\n\n"
                f"Research:\n{research_result}\n\n"
                "IMPORTANT: Return ONLY a raw JSON object. No markdown, no code blocks, no extra text.\n"
                'Format: {"summary": "...", "positives": ["...", "..."], "risks": ["...", "..."]}\n'
                "- summary: 2-3 sentence overview\n"
                "- positives: 2-4 key positive factors (array of strings)\n"
                "- risks: 2-4 key risk factors (array of strings)"
            ),
            expected_output='Raw JSON: {"summary": "...", "positives": [...], "risks": [...]}',
            agent=summary_agent,
        )
        summary_output = str(
            Crew(agents=[summary_agent], tasks=[summary_task], verbose=False).kickoff()
        )

        emit("agent_status", {"agent": "SummaryAgent", "status": "SUCCESS"})

        # ── 4. Parse & emit complete ───────────────────────────────
        try:
            answer = _extract_json(summary_output)
            # 필드 보정
            if "summary" not in answer:
                answer["summary"] = summary_output
            if "positives" not in answer:
                answer["positives"] = []
            if "risks" not in answer:
                answer["risks"] = []
        except Exception:
            answer = {"summary": summary_output, "positives": [], "risks": []}

        emit("complete", answer)

    except Exception as e:
        emit("error", {"message": str(e)})
