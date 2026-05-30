import logging

from crewai.tools import BaseTool

from core.config import settings

logger = logging.getLogger(__name__)


class GoogleSearchTool(BaseTool):
    """Google Search grounding을 통해 최신 웹 정보를 검색하는 crewAI 도구."""

    name: str = "Google Web Search"
    description: str = (
        "Searches the web for current and up-to-date information about stocks, companies, "
        "financial news, earnings reports, and market data. "
        "Use this tool to retrieve the latest news and real-time financial information "
        "before writing your analysis."
    )

    def _run(self, query: str) -> str:
        from google import genai
        from google.genai import types

        logger.debug("GoogleSearchTool query: %.100s", query)
        try:
            client = genai.Client(api_key=settings.google_api_key)
            response = client.models.generate_content(
                model=settings.gemini_search_model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1,
                ),
            )
            result = response.text or ""
            logger.debug("GoogleSearchTool result length: %d chars", len(result))
            return result
        except Exception as e:
            logger.warning("GoogleSearchTool failed: %s", e)
            return f"검색 중 오류가 발생했습니다: {e}"
